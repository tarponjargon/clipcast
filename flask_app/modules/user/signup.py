import re
from flask import Blueprint, request, session, current_app, render_template
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email, create_uuid
from flask_app.modules.contact import subscribe_contact
from flask_app.modules.user.user import (
    User,
    get_user_id_by_email,
    verify_password,
    load_user,
    login_user,
    create_user,
    add_welcome_podcast,
)


def handle_signup_request():
    """User signup route, returns success or fail html"""

    email = request.form.get("email")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")
    accepted_terms = request.form.get("accepted_terms")
    marketing_subscribed = request.form.get("marketing_subscribed")

    # current_app.logger.info(f"email: {email}, password: {password}, password_confirm: {password_confirm}, accepted_terms: {accepted_terms}")

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

    # the regex makes sure the string has both letter(s) and number(s) with a lookahead
    if (
        not password
        or len(password) < 8
        or len(password) > 32
        or not re.match("^(?=.*?[0-9])(?=.*?[A-Za-z]).+", password)
    ):
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please enter a password 8-32 chars, containing letters and numbers",
            ),
            400,
        )

    if password != password_confirm:
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Confirmation password does not match password",
            ),
            400,
        )

    if get_user_id_by_email(email):
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="An account already exists with that email.  \
        Try <a href='/forgotpassword'>replacing your password</a>",
            ),
            400,
        )

    if not accepted_terms:
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="You must agree to our terms and conditions to create an account",
            ),
            400,
        )

    user_id = create_user(email, password)
    if not user_id:
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Problem creating account.  Please <a href='/contact'>contact us</a>.",
            ),
            400,
        )

    user = User.from_id(user_id)

    login_user(user)

    if marketing_subscribed:
        subscribe_contact(email)

    add_welcome_podcast(user_id)

    return render_template(
        "partials/notifications/success_card.html.j2",
        message="""You are now logged in.  Redirecting the the app...
    <script>window.location.href = '/app/quickstart';</script>""",
    )
