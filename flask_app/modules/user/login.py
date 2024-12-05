from flask import request, session, current_app, render_template
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email
from flask_app.modules.user.user import (
    User,
    get_user_id_by_email,
    verify_password,
    load_user,
    login_user,
)


def handle_login_request():
    """User login route, returns success or fail message html"""

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please fill out all fields",
            ),
            400,
        )

    if not validate_email(email):
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please enter an E-mail in the format you@yourdomain.com",
            ),
            400,
        )

    session["email"] = email

    user_id = get_user_id_by_email(email)

    if not user_id:
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please <a href='/signup'>sign up</a> for an account",
            ),
            400,
        )

    my_user = load_user(user_id)

    if not verify_password(password, my_user.get("password_hash")):
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please check your password or <a href='/forgotpassword'>replace your password</a>",
            ),
            400,
        )

    user = User.from_id(user_id)
    login_user(user)

    return render_template(
        "partials/notifications/success_card.html.j2",
        message="""You are now logged in.  Redirecting the the app...
      <script>window.location.href = '/app';</script>""",
    )
