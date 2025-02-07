""" API routes """

import subprocess
from flask import Blueprint, request, session, current_app
from flask_app.modules.http import is_authenticated
from flask_app.modules.extensions import DB
from flask_app.modules.user.user import load_user

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
    return {"success": True, "message": "notifications viewed"}


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


@api.route("/process-email")
@is_authenticated
def do_process_email():
    """this endpoint is for the testrunner to hit to trigger the email processing
    I've configured it to only work for the testrunner's account"""

    user_id = session.get("user_id")
    user_data = load_user(user_id)
    if (
        not user_data
        or not user_data.get("email")
        or not user_data.get("email") in current_app.config.get("TEST_EMAILS")
    ):
        return {
            "success": False,
            "errors": ["Not authorized to use this endpoint"],
            "error": True,
        }, 401

    direnv_path = get_dirnev_path()
    flask_path = get_flask_path()
    command = f"{direnv_path} exec . {flask_path} process_email"
    result = safe_subprocess(command)

    current_app.logger.info("Emails processed via API {}".format(result))
    return {"success": True, "errors": [], "error": False}
