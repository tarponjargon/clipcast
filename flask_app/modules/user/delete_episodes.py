from flask import request, session, current_app, redirect
from flask_app.modules.extensions import DB


def delete_episodes():
    """Delete podcast episodes from the user's account"""

    user_id = session.get("user_id")
    # current_app.logger.debug("request values: " + str(request.values))
    episode_ids = request.values.getlist("episodes[]")

    # check if the episodes belong to the user
    q = DB.fetch_all(
        """
        SELECT content_id FROM podcast_content WHERE user_id = %s AND content_id IN %s
      """,
        (user_id, tuple(episode_ids)),
    )
    if not q or not len(q.get("results")):
        return redirect("/app")

    # delete episodes
    DB.delete_query(
        """
        DELETE FROM podcast_content WHERE user_id = %s AND content_id IN %s
      """,
        (user_id, tuple(episode_ids)),
    )

    return redirect("/app")
