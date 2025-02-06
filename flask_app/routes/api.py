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
        or not user_data.get("email") == current_app.config.get("TEST_ACCOUNT_EMAIL")
    ):
        return {
            "success": False,
            "errors": ["Not authorized to use this endpoint"],
            "error": True,
        }, 401

    command = "cd {} && $(which direnv) allow && $(which direnv) exec . $(which flask) process_email".format(
        current_app.config.get("HOME_DIR")
    )

    result = None
    try:
        result = subprocess.run(
            ["bash", "-c", command], check=True, capture_output=True
        )
    except subprocess.CalledProcessError as e:
        current_app.logger.debug(
            f"Command failed with error: {e.returncode} Stdout: {e.stdout} Stderr: {e.stderr}"
        )

    # if not result or not result.returncode == 0:
    #     current_app.logger.error(f"Error processing emails via API: {result}")
    #     return {
    #         "success": False,
    #         "errors": ["Error processing emails"],
    #         "error": True,
    #     }, 500

    current_app.logger.info("Emails processed via API {}".format(result))
    return {"success": True, "errors": [], "error": False}
