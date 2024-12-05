from flask import current_app, session
from flask_app.modules.extensions import DB


def get_notifications():
    """Gets notifications for a user"""

    user_id = session.get("user_id")
    if not user_id:
        return None

    q = DB.fetch_all(
        """
      SELECT
        content_id,
        message,
        viewed_at,
        DATE_FORMAT(timestamp, '%%b %%c, %%l:%%i %%p') AS timestamp
      FROM notification
      WHERE user_id = %(user_id)s
      ORDER BY timestamp DESC
      LIMIT 5
    """,
        {"user_id": user_id},
    )

    return q.get("results", [])
