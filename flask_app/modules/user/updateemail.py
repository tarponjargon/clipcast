from flask import request, session, current_app, render_template, render_template_string
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email
from flask_app.modules.user.user import get_user_id_by_email


def handle_updateemail_request():
    """User login route, returns a new email container html or an error in a toast"""

    email = request.form.get("email")

    if not email or not validate_email(email):
        return (
            render_template_string(
                "Please enter an E-mail in the format you@yourdomain.com"
            ),
            400,
        )

    user_id = get_user_id_by_email(email)

    if user_id and session.get("user_id") != user_id:
        return render_template_string("This e-mail is taken by another user"), 400

    DB.update_query(
        """
        UPDATE user SET
        email = %(email)s
        WHERE user_id = %(user_id)s
      """,
        {"email": email, "user_id": session.get("user_id")},
    )

    session["email"] = email

    return render_template("partials/profile/profile_email.html.j2")
