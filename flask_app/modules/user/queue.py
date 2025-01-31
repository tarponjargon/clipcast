import math
import os
import subprocess
from flask import current_app, session
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import match_uuid
from flask_app.modules.user.user import load_user


def get_plan_episode_count(user_id):
    """Gets the number of episodes in a user's queue

    Returns:
      int: The number of episodes
    """
    if not user_id:
        return 0

    # load user data
    user_data = load_user(user_id)
    if not user_data or user_data.get("email") in current_app.config["TEST_EMAILS"]:
        return 0

    q = DB.fetch_one(
        """
          SELECT COUNT(*) AS episode_count
          FROM plan_episodes
          WHERE user_id = %s
          AND `timestamp` >= DATE_FORMAT(NOW(), '%%Y-%%m-01 00:00:00');
        """,
        (user_id),
    )

    return q.get("episode_count", 0)


def get_queue(user_id, page=1):
    """Gets a user's queue

    Returns:
      list: The user's queue
    """
    if not user_id:
        return []

    page = int(page)
    offset = (page - 1) * current_app.config["PAGE_SIZE"]

    q = DB.fetch_all(
        """
        SELECT SQL_CALC_FOUND_ROWS
          id,
          user_id,
          content_id,
          url,
          title,
          author,
          description,
          image,
          hostname,
          article_date,
          metadata,
          content_character_count,
          mp3_url,
          mp3_file_size,
          mp3_duration,
          voice_code,
          processing_start_time,
          processing_end_time,
          processing_time_seconds,
          estimated_cost_cents,
          current_status,
          error_message,
          timestamp
        FROM podcast_content
        WHERE user_id = %s
        ORDER BY id DESC, timestamp DESC
        LIMIT %s OFFSET %s
        """,
        (user_id, current_app.config["PAGE_SIZE"], offset),
    )

    total_results = q.get("calc_rows")
    has_more_results = total_results > (page * current_app.config["PAGE_SIZE"])
    next_page = page + 1 if has_more_results else None
    previous_page = page - 1 if page > 1 else None
    plan_count = get_plan_episode_count(user_id)
    plan = session.get("plan", "free")

    # current_app.logger.debug(
    #     "total_results %s has_more_results %s plan_count %s",
    #     total_results,
    #     has_more_results,
    #     plan_count,
    # )
    over_limit = False
    user_data = load_user(user_id)
    if (
        plan_count >= current_app.config.get("MAX_EPISODES").get(plan)
        and user_data.get("email") not in current_app.config["TEST_EMAILS"]
    ):
        over_limit = True

    return {
        "results": q.get("results", []),
        "next_page": next_page,
        "previous_page": previous_page,
        "total_episodes": total_results,
        "plan_count": plan_count,
        "over_limit": over_limit,
    }


def check_job_status(content_id):
    """Check the status of a job and updates the record if it's errored or nonexistent

    Returns:
      str: The status of the job
    """
    if not match_uuid(content_id):
        return "Invalid content ID"

    q = DB.fetch_one(
        """
        SELECT job_id
        FROM podcast_content
        WHERE content_id = %s
      """,
        (content_id,),
    )

    tsp_path = subprocess.run(
        ["which", "tsp"], capture_output=True, text=True
    ).stdout.strip()
    job_id = q.get("job_id")
    res = None
    job_result = None
    try:
        res = subprocess.run(
            [tsp_path, "-s", str(job_id)], capture_output=True, check=True, text=True
        )
        job_result = res.stdout.strip().lower()
    except subprocess.CalledProcessError as e:
        job_result = "error checking job status"

    # if the job is not found, update the record
    if "cannot be stated" in job_result or "error" in job_result:
        DB.update_query(
            """
          UPDATE podcast_content SET
          current_status = 'error',
          error_message = %s,
          processing_end_time = NOW()
          WHERE content_id = %s
        """,
            (job_result, content_id),
        )
        return job_result

    # need to check for instances of when the tsp job is showing finished (tho episode is still showing processing)
    # and an error level that is not 0
    if "finished" in job_result:
        e_level = 0
        result = subprocess.run(
            [tsp_path, "-l"],
            text=True,  # Return output as a string
            capture_output=True,  # Capture stdout and stderr
        )

        # Process output with Python
        if result.stdout:
            for line in result.stdout.splitlines():
                columns = line.split()
                if columns and columns[0] == str(job_id):  # Match Job ID
                    # E-Level is in the 4th column (index 3)
                    e_level = columns[3].strip()
                    print(f"E-Level for job {str(job_id)}: {e_level}")
                    break

        if e_level != 0:
            job_result = f"Job {str(job_id)} completed with error level {e_level} content_id: {content_id}"
            DB.update_query(
                """
              UPDATE podcast_content SET
              current_status = 'error',
              error_message = %s,
              processing_end_time = NOW()
              WHERE content_id = %s
            """,
                (job_result, content_id),
            )
            return job_result
    return None


def get_queue_item(content_id):
    """Gets a queue item
    Returns:
      dict: The queue item
    """
    if not match_uuid(content_id):
        return {}

    status = check_job_status(content_id)
    if status:
        current_app.logger.error("Episode %s errored: %s", content_id, status)

    item = DB.fetch_one(
        """
          SELECT *
          FROM podcast_content
          WHERE content_id = %s
          ORDER BY timestamp DESC
        """,
        (content_id,),
    )

    item["progress"] = None
    if item.get("current_status") == "processing":
        item["progress"] = estimate_progress(content_id)

    return item


def estimate_progress(row_id):
    """estimate progress for progress indicator"""

    q = DB.fetch_one(
        """
          SELECT
          processed_chunks,
          total_chunks
          FROM `podcast_content` WHERE content_id = %s
        """,
        (row_id),
    )
    chunks_processed = q.get("processed_chunks", 1)
    total_chunks = q.get("total_chunks", 1)
    percent_done = 0

    try:
        percent_done = math.ceil((chunks_processed / total_chunks) * 100)
    except ZeroDivisionError:
        percent_done = 0

    if percent_done < 1:
        percent_done = 1
    if percent_done > 100:
        percent_done = 99

    current_app.logger.debug("")
    current_app.logger.debug("%s total_chunks: %s", row_id, total_chunks)
    current_app.logger.debug("%s chunks_processed: %s", row_id, chunks_processed)
    current_app.logger.debug("%s percent_done: %s", row_id, percent_done)
    current_app.logger.debug("")

    return percent_done
