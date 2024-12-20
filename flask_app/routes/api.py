""" API routes """

from flask import Blueprint, request, session, current_app
from flask_app.modules.http import is_authenticated
from flask_app.modules.extensions import DB

api = Blueprint("account_api", __name__, url_prefix="/api")


@api.route("/test", methods=["GET"])
def do_rest_route():
    return {"message": "Hello, World!"}


@api.route("/notifications-viewed", methods=["POST"])
@is_authenticated
def do_notifications_viwewed():
    user_id = session.get("user_id")
    upd = DB.update_query(
        """
      UPDATE notification
      SET viewed_at = NOW()
      WHERE user_id = %(user_id)s
    """,
        {"user_id": user_id},
    )
    return {"success": True, "message": str(upd) + "notifications viewed"}


@api.route("/total-episodes")
@is_authenticated
def do_get_total_episodes():
    user_id = session.get("user_id")
    q = DB.fetch_one(
        """
          SELECT COUNT(*) as total_episodes
          FROM podcast_content
          WHERE user_id = %(user_id)s
        """,
        {"user_id": user_id},
    )
    return {"totalEpisodes": q.get("total_episodes")}
