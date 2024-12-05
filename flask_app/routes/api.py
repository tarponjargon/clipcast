""" API routes """

from flask import Blueprint, request, session, current_app
from flask_app.modules.http import login_required
from flask_app.modules.extensions import DB

api = Blueprint("account_api", __name__, url_prefix="/api")


@api.route("/test", methods=["GET"])
def do_rest_route():
    return {"message": "Hello, World!"}


@api.route("/notifications-viewed", methods=["POST"])
@login_required
def do_notifications_viwewed():
    user_id = session.get("user_id")
    if not user_id:
        return {"message": "User not logged in"}, 401

    upd = DB.update_query(
        """
      UPDATE notification
      SET viewed_at = NOW()
      WHERE user_id = %(user_id)s
    """,
        {"user_id": user_id},
    )
    return {"success": True, "message": str(upd) + "notifications viewed"}
