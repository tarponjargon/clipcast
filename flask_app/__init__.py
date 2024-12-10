""" Flask Application Module

Creates the Flask application using the app factory method
"""

from datetime import datetime
import os
import logging
from flask import Flask, current_app, g, request, session


def register_extensions(app):
    """Registers Flask extensions

    Args:
      app (app): The Flask application
    """
    from .modules.extensions import db, compress, cache, mail, sess

    compress.init_app(app)
    db.init_app(app)
    cache.init_app(app)
    sess.init_app(app)
    mail.init_app(app)


def create_app():
    """Creates the Flask application

    Returns:
      app: The Flask application
    """
    app = Flask(__name__, static_folder="assets")
    with app.app_context():
        app.config.from_object("config." + "config." + os.environ["ENV"])

        register_extensions(app)

        # standard application logging
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

        # post critical errors to notification service
        if app.config.get("PRODUCTION"):
            from .modules.http import CustomHTTPErrorHandler

            error_notify_handler = CustomHTTPErrorHandler()
            error_notify_handler.setLevel(logging.ERROR)
            app.logger.addHandler(error_notify_handler)

        # template routes
        from flask_app.routes.views import views

        app.register_blueprint(views)

        # api routes
        from flask_app.routes.api import api

        app.register_blueprint(api)

        # partial routes
        from flask_app.routes.partials import partials

        app.register_blueprint(partials)

        from .modules.http import (
            page_not_found,
            error_500,
            add_security_headers,
            session_safe_get,
        )

        app.register_error_handler(404, page_not_found)
        app.register_error_handler(500, error_500)

        from .modules.helpers import match_uuid, get_random_string, sanitize
        from .modules.user.user import User, login_user

        @app.before_request
        def do_before():
            """Procedures to do before normal Flask request processing.  The order is immportant"""

            # login the user
            user_id_cookie = request.cookies.get("user")
            if (
                user_id_cookie
                and match_uuid(user_id_cookie)
                and not session.get("user_id")
            ):
                user = User.from_id(user_id_cookie)
                if user:
                    app.logger.debug(f"logging in user from cookie: {user.get_id()}")
                    login_user(user)

            # process urls that are requested to be added but got diverted to login/signup
            if session.get("user_id") and session.get("addurl"):
                from .modules.user.add_podcast_content import add_podcast_url

                add_podcast_url(session.get("addurl"), session.get("user_id"))
                session.pop("addurl")

        @app.after_request
        def do_after(response):
            """Procedures to do after normal Flask request processing but before respose sent to user.  The order is immportant"""

            # set a cookie named user with a value of user.get_id() and set it to expire in a long time
            if session.get("user_id"):
                response.set_cookie(
                    "user",
                    session.get("user_id"),
                    max_age=63115200,
                    secure=True,
                    samesite="Lax",
                )
            return add_security_headers(response)

        @app.context_processor
        def template_utils():
            """Makes functions available inside templates"""
            return dict(
                datetime=datetime,
                session_safe_get=session_safe_get,
                get_random_string=get_random_string,
                sanitize=sanitize,
            )

        from .commands.test import test1
        from .commands.process_content import process_content
        from .commands.process_email import process_email

    return app
