import re
from flask import render_template, request, current_app
from flask_app.modules.user.user import User, login_user
from flask_app.modules.extensions import DB


def handle_resetpassword_view():
    """Reset password form view"""

    default_error = 'The key passed on your e-mail is either incorrect or expired. \
          Please try your password recovery \
          again or <a href="/contact">contact us</a> for assistance.'

    token = request.values.get("key")
    if not token or not re.match(r"^[A-Za-z0-9]{32}$", token):
        return render_template("error.html.j2", error=default_error), 400

    res = DB.fetch_one(
        """
        SELECT user_id
        FROM password_replace
        WHERE hash = %(token)s
        AND timestamp > DATE_SUB(NOW(),INTERVAL 12 HOUR)
      """,
        {"token": token},
    )
    current_app.logger.debug(f"Reset password: {res}")
    if not res or not res.get("user_id"):
        return render_template("error.html.j2", error=default_error), 400

    user = User.from_id(res.get("user_id"))
    if not user:
        return (
            render_template("error.html.j2", error="No account found for this key."),
            400,
        )

    login_user(user)

    return render_template("resetpassword.html.j2", errors=[])
