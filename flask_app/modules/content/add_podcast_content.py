import validators
import json
import re
import requests
import time
import fitz  # PyMuPDF
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from trafilatura import fetch_url, extract_metadata, extract
from playwright.sync_api import sync_playwright, Error
from flask_app.modules.helpers import (
    convert_to_ascii,
    create_uuid,
    get_first_n_words,
    strip_html,
    match_uuid,
    create_uuid,
    parse_urls_from_text,
)
from flask import (
    Blueprint,
    request,
    current_app,
    render_template_string,
    render_template,
)
from flask_app.modules.extensions import DB
from flask_app.modules.user.user import load_user
from flask_app.modules.user.queue import get_plan_episode_count
from flask_app.modules.content.process_content import process_episode
from flask_app.modules.subprocess import (
    safe_subprocess,
    get_direnv_path,
    get_python_path,
    get_tsp_path,
)


def handle_add_url_post_request(user_id):
    """Handle the request to add a podcast URL.  POST requests are handled with AJAX"""

    url = request.form.get("url")
    if not url or not validators.url(url):
        return (
            render_template_string("Please enter a valid URL"),
            400,
        )

    resp = add_podcast_url(request.form.get("url"), user_id)
    if not resp.get("response_code") == 200:
        return render_template_string(resp.get("message")), resp.get("response_code")

    return render_template_string(resp.get("message"))


def handle_bulk_add_request(user_id):
    """Handle the request to bulk add URLs.  POST requests are handled with AJAX"""

    # return_messages = []
    text = request.form.get("bulk_urls")
    urls = parse_urls_from_text(text)
    if not urls:
        return (
            render_template_string("Please enter a valid URL"),
            400,
        )
    urls = list(set(urls))
    urls = [url for url in urls if validators.url(url)]

    max_bulk_urls = current_app.config.get("MAX_BULK_URLS")
    if len(urls) > max_bulk_urls:
        urls = urls[:max_bulk_urls]

    responses = []
    for url in urls:
        resp = add_podcast_url(url, user_id)
        responses.append(resp)

    # current_app.logger.debug(f"responses: {responses}")
    count_not_200 = len(
        [r.get("response_code") for r in responses if r.get("response_code") != 200]
    )
    # current_app.logger.debug(
    #     f"Count of non-200 status codes: {count_not_200} number of ulrs {len(urls)}"
    # )

    return_message, return_status = "The content has been added to your queue", 200
    if count_not_200 > 0:
        processed = len(urls) - count_not_200
        if processed > 0:
            return_message = f"Content added, but {count_not_200} URL(s) \
              could not be processed.  <a class='text-white' \
                href='/help#why-some-content'>Why some content doesn't work</a>"
        else:
            return_message, return_status = (
                "There was an error adding the URLs.  \
                  <a class='text-white' href='/help#why-some-content'>Why \
                  some content doesn't work</a>",
                400,
            )

    return render_template_string(return_message), return_status


def handle_add_content_request(user_id):
    """Handle the request to add content directly into the podcast queue"""

    content = request.form.get("content")
    if not content:
        return render_template_string("Please enter some content"), 400

    resp = add_podcast_content(content, user_id)
    if not resp.get("response_code") == 200:
        return render_template_string(resp.get("message")), resp.get("response_code")

    return render_template_string(resp.get("message"))


def extract_content_from_html(html):
    """Extract the content from an HTML page, removing comments"""

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Remove any elements that are obviously comments
    for selector in current_app.config.get("COMMENTS_SELECTORS"):
        for element in soup.select(selector):
            element.decompose()

    # now extract content with trafilatura
    raw_content = extract(str(soup))
    content = convert_to_ascii(raw_content)

    return content


def send_to_task_to_queue(content_id):
    """Send the content to task queue for processing"""

    if not content_id or not match_uuid(content_id):
        current_app.logger.error(f"Invalid content ID: {content_id}")
        return None

    tsp_path = get_tsp_path()
    direnv_path = get_direnv_path()
    python_path = get_python_path()
    command = (
        f"{tsp_path} {direnv_path} exec . {python_path} -m episode_job {content_id}"
    )
    job_id = safe_subprocess(command)
    current_app.logger.debug(f"Job ID returned from safe_subprocess: {job_id}")
    if not job_id:
        current_app.logger.error(f"No job ID returned: {result}")
        return None

    return job_id


def process_episode_content(id):
    """Process the episode content in a task queue"""
    with current_app.app_context():
        # retrieve the content and process it
        episode = DB.fetch_one(
            """
            SELECT
              user_id,
              content_id
            FROM `podcast_content`
            WHERE id = %s
          """,
            (id),
        )
        default_error = {
            "response_code": 500,
            "message": "There was an error processing the content",
        }
        if not episode:
            current_app.logger.error(f"Error fetching content from db: {ins}")
            return default_error

        print(f"Processing content: {episode.get('content_id')}")

        # send the content to the task queue
        job_id = send_to_task_to_queue(episode.get("content_id"))
        if not job_id:
            return default_error

        upd = DB.update_query(
            """
            UPDATE podcast_content SET
            job_id = %s
            WHERE id = %s
          """,
            (job_id, id),
        )

        if upd:
            # update plan_episodes to keep track of how many episodes the user has created
            # and to keep track of the user's plan
            user = load_user(episode.get("user_id"))
            ins = DB.insert_query(
                """
              INSERT INTO plan_episodes
              (user_id, content_id, job_id, plan)
              VALUES (%s, %s, %s, %s)
          """,
                (
                    episode.get("user_id"),
                    episode.get("content_id"),
                    job_id,
                    user.get("plan"),
                ),
            )

        return {
            "response_code": 200,
            "message": "The content has been added to your queue",
        }


def add_podcast_url(url, user_id):
    """Add a podcast URL to the user's account"""

    if not user_id:
        return {
            "response_code": 401,
            "message": "Authentication error",
        }

    user = load_user(user_id)
    if not user_id or not user.get("user_id"):
        return {
            "response_code": 401,
            "message": "Authentication error",
        }

    plan_count = get_plan_episode_count(user_id)
    plan = user.get("plan")
    if (
        plan_count >= current_app.config.get("MAX_EPISODES").get(plan)
        and user.get("email") not in current_app.config["TEST_EMAILS"]
    ):
        return {
            "response_code": 401,
            "message": "You have reached the limit of episodes for your plan",
        }

    # check if the url is already in the database for this user
    q = DB.fetch_one(
        """
          SELECT id FROM podcast_content WHERE user_id = %s AND url = %s
        """,
        (user_id, url),
    )
    if q and q.get("id"):
        return {
            "response_code": 401,
            "message": "The URL is already in your queue",
        }

    # check if this is a pdf
    if url.lower().endswith(".pdf"):
        return add_podcast_pdf(url, user_id)

    # fetch content with playwright to get computed source
    # and if we're lucky, get past any low bot checker hurdles
    downloaded = None
    retry_delay = current_app.config.get("FETCH_RETRY_DELAY")
    fetch_attempts = current_app.config.get("FETCH_ATTEMPTS")
    fetch_timeout = current_app.config.get("FETCH_TIMEOUT")
    for attempt in range(fetch_attempts):
        try:
            custom_headers = {
                "User-Agent": current_app.config.get("FETCH_USER_AGENT"),
                "Accept-Language": "en-US,en;q=0.9",
            }
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(extra_http_headers=custom_headers)
                page = context.new_page()
                page.goto(url, timeout=fetch_timeout)
                page.wait_for_load_state("networkidle", timeout=fetch_timeout)
                html_source = page.content()
                # current_app.logger.debug(html_source)
                downloaded = html_source
                browser.close()

        except Error as e:
            current_app.logger.error(
                f"Playwright error, attempt {attempt + 1}: {url} {e}"
            )
            # if this was the last attempt, return an error
            if (attempt + 1) == fetch_attempts:
                return {
                    "response_code": 400,
                    "message": "There was an error downloading the URL",
                }
            else:
                time.sleep(retry_delay)

        except Exception as e:
            current_app.logger.error(f"Playwright exception: {url} " + str(e))
            return {
                "response_code": 400,
                "message": "There was an error downloading the URL",
            }
            break

    if not downloaded:
        current_app.logger.error(f"No content could be found failed for: {url}")
        return {
            "response_code": 400,
            "message": "No content could be extracted from URL. \
               <a class='text-white' href='/help#why-some-content'>Why some content doesn't work</a>",
        }

    # parse metadata
    metadata = {}
    try:
        metadata = extract_metadata(downloaded).as_dict()
    except Exception as e:
        current_app.logger.error(f"Error extracting metadata: {url} " + str(e))
        metadata = {}

    # save metadata as JSON
    metadata_json = None
    try:
        metadata_json = json.dumps(metadata)
    except Exception as e:
        current_app.logger.error(f"Error serializing metadata: {url} " + str(e))

    # extract content
    content = extract_content_from_html(downloaded)

    if not content:
        return {
            "response_code": 400,
            "message": "No content could be extracted from URL.  <a class='text-white' href='/help#why-some-content'>Why some content doesn't work</a>",
        }

    # check content length
    maxlength_obj = current_app.config.get("MAX_CHARACTERS")
    maxlength = maxlength_obj.get(plan)
    if len(content) > maxlength:
        content = content[:maxlength]
        content += "...The content of this article has been truncated to fit your plan's character limit."

    title = metadata.get("title")
    author = metadata.get("author")
    hostname = metadata.get("hostname")
    if not hostname:
        try:
            hostname = urlparse(url).hostname.replace("www.", "")
        except Exception as e:
            current_app.logger.error(f"Error extracting hostname: {url} " + str(e))
            hostname = ""

    article_date = metadata.get("file_date")
    if not article_date:
        article_date = datetime.now().strftime("%Y-%m-%d")

    description = f"Original article: {url} - "
    if metadata.get("description"):
        description += "Description: " + metadata.get("description")
    else:
        description += "Description: " + get_first_n_words(content, 50)

    if author:
        description += f" by {author}."

    image = metadata.get("image")
    if not image:
        image = current_app.config.get("DEFAULT_IMAGE")

    char_count = len(content)

    # save to the database
    ins_id = DB.insert_query(
        """
        INSERT INTO podcast_content
        (user_id, content_id, url, title, author, description, image, hostname, article_date, metadata, content, content_character_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            user_id,
            create_uuid(),
            url,
            title,
            author,
            description,
            image,
            hostname,
            article_date,
            metadata_json,
            content,
            char_count,
        ),
    )
    if not ins_id:
        current_app.logger.error(f"Error saving url content to db: {url}")
        return {
            "response_code": 500,
            "message": "There was an error saving the content",
        }

    return process_episode_content(ins_id)


def add_podcast_pdf(url, user_id):

    response = None
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error downloading PDF: {url} " + str(e))
        return {
            "response_code": 500,
            "message": "Error downloading PDF",
        }

    # get the filename out of the url
    parsed_url = urlparse(url)
    path = parsed_url.path
    file_name = path.split("/")[-1]

    # save pdf
    file_path = current_app.config.get("TMP_DIR") + "/" + file_name
    with open(file_path, "wb") as file:
        file.write(response.content)

    # open an parse the pdf
    clean_text = ""
    try:
        all_text = ""
        pdf = fitz.open(file_path)
        for page_number in range(pdf.page_count):
            page = pdf.load_page(page_number)
            text = page.get_text("text")
            all_text += text
        clean_text = re.sub(r"\s+", " ", all_text).strip()
        pdf.close()
    except Exception as e:
        current_app.logger.error(f"Error extracting text from PDF: {url} " + str(e))
        return {
            "response_code": 500,
            "message": "Error extracting text from PDF",
        }

    if clean_text:
        return add_podcast_content(clean_text, user_id)
    else:
        return {
            "response_code": 500,
            "message": "No content extracted from PDF",
        }


def add_podcast_content(content, user_id):
    """Add a podcast Content to the user's account"""

    if not user_id:
        return {
            "response_code": 401,
            "message": "Authentication error",
        }

    user = load_user(user_id)
    if not user_id or not user.get("user_id"):
        return {
            "response_code": 401,
            "message": "Authentication error",
        }

    plan_count = get_plan_episode_count(user_id)
    plan = user.get("plan")
    if (
        plan_count >= current_app.config.get("MAX_EPISODES").get(plan)
        and user.get("email") not in current_app.config["TEST_EMAILS"]
    ):
        return {
            "response_code": 401,
            "message": "You have reached the limit of episodes for your plan",
        }

    # extract content
    content = strip_html(content)

    if not content:
        return {
            "response_code": 400,
            "message": "No content provided",
        }

    title = get_first_n_words(content, 9)
    author = ""
    hostname = current_app.config.get("STORE_NAME")
    article_date = datetime.now().strftime("%Y-%m-%d")
    description = get_first_n_words(content, 50)
    image = current_app.config.get("DEFAULT_IMAGE")
    metadata_json = "{}"
    char_count = len(content)

    # save to the database
    ins_id = DB.insert_query(
        """
        INSERT INTO podcast_content
        (user_id, content_id, title, author, description, image, hostname, article_date, metadata, content, content_character_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        (
            user_id,
            create_uuid(),
            title,
            author,
            description,
            image,
            hostname,
            article_date,
            metadata_json,
            content,
            char_count,
        ),
    )
    if not ins_id:
        current_app.logger.error(f"Error saving text content to db: {title}")
        return {
            "response_code": 500,
            "message": "There was an error saving the content",
        }

    return process_episode_content(ins_id)
