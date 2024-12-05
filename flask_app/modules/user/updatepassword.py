import re
from flask import (
    Blueprint,
    request,
    session,
    current_app,
    render_template,
    render_template_string,
)
from flask_app.modules.extensions import DB
from flask_app.modules.user.user import hash_password


def handle_updatepassword_request():
    """Updates the user's password, returns a success or fail card html"""

    password = request.form.get("password")
    password_comfirm = request.form.get("password_confirm")

    if not password or not password_comfirm:
        # the regex makes sure the string has both letter(s) and number(s) with a lookahead
        if (
            not password
            or len(password) < 8
            or len(password) > 32
            or not re.match("^(?=.*?[0-9])(?=.*?[A-Za-z]).+", password)
        ):
            error = "Please enter a password 8-32 chars, letters and numbers, and confirm the password"
            if request.method == "PUT":
                return render_template_string(error), 400
            else:
                return (
                    render_template(
                        "partials/notifications/error_card.html.j2", error=error
                    ),
                    400,
                )

    if password != password_comfirm:
        error = "Confirmation password does not match"
        if request.method == "PUT":
            return render_template_string(error), 400
        else:
            return (
                render_template(
                    "partials/notifications/error_card.html.j2", error=error
                ),
                400,
            )

    password_hash = hash_password(password)
    success = DB.update_query(
        """
        UPDATE user SET
        password_hash = %(password_hash)s
        WHERE user_id = %(user_id)s
      """,
        {"password_hash": password_hash, "user_id": session.get("user_id")},
    )
    if not success:
        if request.method == "PUT":
            error = (
                "Problem updating password.  Please <a href='/contact'>contact us</a>."
            )
            return render_template_string(error), 400
        return (
            render_template("partials/notifications/error_card.html.j2", error=error),
            400,
        )

    # remove all password reset request records for this user
    DB.delete_query(
        """
    DELETE FROM password_replace
    WHERE user_id  = %(user_id)s
    """,
        {"user_id": session.get("user_id")},
    )

    # routine cleanup of the table unrelated to this request
    DB.delete_query(
        """
    DELETE FROM password_replace
    WHERE timestamp < DATE_SUB(NOW(),INTERVAL 12 HOUR)"""
    )

    if request.method == "PUT":
        return render_template("partials/profile/profile_password.html.j2")
    else:
        return render_template(
            "partials/notifications/success_card.html.j2",
            message="""Your password is updated.  Redirecting to app...
        <script>setTimeout(function(){window.location.href = '/app';}, 2000);</script>""",
        )
