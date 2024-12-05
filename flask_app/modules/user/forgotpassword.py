import hashlib
from flask import Blueprint, request, session, current_app, render_template
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email, get_random_string
from flask_app.modules.email import send_email
from flask_app.modules.user.user import get_user_id_by_email


def handle_forgotpassword_request():
    """Handles forgotpassword request, sends email if valid"""

    email = request.form.get("email")

    account_message = """<h1>Submitted</h1>If you have an account with us,
    you will receive an email with password reset instructions.
    If it does not arrive, please check your spam folder."""

    if not email or not validate_email(email):
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please enter an E-mail in the format you@yourdomain.com",
            ),
            400,
        )

    user_id = get_user_id_by_email(email)

    if not user_id:
        # for security reasons, we don't want to tell the user if the email is not found
        return render_template(
            "partials/notifications/success_card.html.j2", message=account_message
        )

    token = hashlib.md5(get_random_string().encode("utf8")).hexdigest()
    success = DB.insert_query(
        "INSERT INTO password_replace SET hash = %(token)s, user_id = %(user_id)s",
        {"token": token, "user_id": user_id},
    )

    if not success:
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="""Problem sending the password recovery link.
      Please <a href="/contact">contact us</a> and we can help you.""",
            ),
            400,
        )

    send_email(
        subject=f"Reset Your {current_app.config['STORE_NAME']} Password",
        sender=current_app.config["STORE_EMAIL"],
        recipients=[email],
        reply_to=current_app.config["DEFAULT_MAIL_SENDER"],
        text_body=render_template(
            "emails/forgotpassword.txt.j2", email=email, token=token
        ),
    )

    return render_template(
        "partials/notifications/success_card.html.j2", message=account_message
    )
