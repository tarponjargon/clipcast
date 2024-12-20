import math
from flask import current_app, session
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import match_uuid


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

    # current_app.logger.debug(
    #     "total_results %s has_more_results %s", total_results, has_more_results
    # )
    return {
        "results": q.get("results", []),
        "next_page": next_page,
        "previous_page": previous_page,
        "total_episodes": total_results,
    }


def get_queue_item(content_id):
    """Gets a queue item
    å
        Returns:
          dict: The queue item
    """
    if not match_uuid(content_id):
        return {}

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
