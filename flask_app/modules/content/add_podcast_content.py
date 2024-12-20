import validators
import json
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from trafilatura import fetch_url, extract_metadata, extract
from flask_app.modules.helpers import (
    convert_to_ascii,
    create_uuid,
    get_first_n_words,
    strip_html,
)
from flask import (
    Blueprint,
    request,
    current_app,
    render_template_string,
    render_template,
)
from flask_app.modules.extensions import DB
from flask_app.modules.content.process_content import process_episode


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
    """Send the content to Task queue for processing"""
    command = 'python -m episode_job "{}"'.format(content_id)
    result = subprocess.run(
        ["tsp", "bash", "-c", command], check=True, capture_output=True
    )
    if not result.returncode == 0:
        current_app.logger.error(f"Error processing content: {result}")
        return None
    job_id = result.stdout.decode().strip()
    if not job_id:
        current_app.logger.error(f"No job ID returned: {result}")
        return None
    job_result = subprocess.run(["tsp", "-o", job_id], check=True, capture_output=True)
    if not job_result.returncode == 0:
        current_app.logger.error(f"Error fetching job result: {job_result}")
        return None
    job_output_file = job_result.stdout.decode().strip()
    return job_id, job_output_file


def process_episode_content(id):
    """Process the episode content in a task queue"""
    with current_app.app_context():
        # retrieve the content and process it
        episode = DB.fetch_one(
            """
            SELECT
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

        # send the content to the task queue
        job_id, job_output_file = send_to_task_to_queue(episode.get("content_id"))
        if not job_id or not job_output_file:
            return default_error

        upd = DB.update_query(
            """
            UPDATE podcast_content SET
            job_id = %s,
            job_output_file = %s
            WHERE id = %s
          """,
            (job_id, job_output_file, id),
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

    downloaded = None
    try:
        downloaded = fetch_url(url)
    except Exception as e:
        current_app.logger.error(f"Error extracting metadata: {url} " + str(e))
        return {
            "response_code": 400,
            "message": "There was an error downloading the URL",
        }

    if not downloaded:
        current_app.logger.error(f"No content could be found failed for: {url}")
        return {
            "response_code": 400,
            "message": "No content could be extracted from URL",
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
            "message": "No content could be extracted from URL",
        }

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

    description = metadata.get("description")
    if not description:
        description = get_first_n_words(content, 50)

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


def add_podcast_content(content, user_id):
    """Add a podcast Content to the user's account"""

    if not user_id:
        return {
            "response_code": 401,
            "message": "Authentication error",
        }

    # extract content
    content = strip_html(content)

    if not content:
        return {
            "response_code": 400,
            "message": "No content provided",
        }

    title = get_first_n_words(content, 9)
    author = "Not available"
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
