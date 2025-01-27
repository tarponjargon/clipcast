from flask import request, session, current_app, render_template
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email, get_random_string
from flask_app.modules.user.user import (
    User,
    get_user_id_by_email,
    create_user,
    verify_password,
    load_user,
    login_user,
    add_welcome_podcast,
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


def handle_google_login_callback(google):
    """Handle the callback from Google login"""

    token = None
    user_info = {}
    try:
        token = google.authorize_access_token()
        user_info = google.get("userinfo").json()
    except Exception as e:
        current_app.logger.error(
            "Problem getting user info from google login.  Error: {}".format(e)
        )

    if not user_info.get("email"):
        current_app.logger.error(
            "Google did not return an E-mail address. User info {}".format(user_info)
        )
        return render_template(
            "error.html.j2",
            error="Google did not return an E-mail address",
        )

    # # Check if user exists
    user_id = get_user_id_by_email(user_info.get("email"))
    if not user_id:
        # # Create user
        user_id = create_user(user_info.get("email"), get_random_string(32))

    user = User.from_id(user_id)
    if not user:
        current_app.logger.error(
            "Problem loading user from google login.  user_id: {}".format(user_id)
        )
        return render_template(
            "error.html.j2",
            error="Problem loading user",
        )
    login_user(user)

    add_welcome_podcast(user_id)

    return render_template(
        "partials/notifications/success_card.html.j2",
        message="""You are now logged in.  Redirecting the the app...
    <script>window.location.href = '/app/quiuckstart';</script>""",
    )
