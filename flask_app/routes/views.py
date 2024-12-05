from flask import Blueprint, render_template, redirect, session, make_response
from flask_app.modules.extensions import DB
from flask_app.modules.http import login_required, check_if_logged_in_already
from flask_app.modules.user.resetpassword import handle_resetpassword_view
from flask_app.modules.user.notifications import get_notifications
from flask_app.modules.user.delete_episodes import delete_episodes
from flask_app.modules.user.voices import get_base_voices, get_premium_voices
from flask_app.modules.user.rss import serve_rss_feed
from flask_app.modules.user.queue import get_queue

views = Blueprint("views", __name__)


@views.route("/")
def do_home():
    return render_template("home.html.j2")


@views.route("/app")
@login_required
def do_app():
    data = get_queue(session.get("user_id"))
    notifications = get_notifications()
    return render_template(
        "app.html.j2",
        queue=data.get("results"),
        next_page=data.get("next_page"),
        notifications=notifications,
    )


@views.route("/signup")
@check_if_logged_in_already
def do_signup():
    return render_template("signup.html.j2")


@views.route("/login")
@check_if_logged_in_already
def do_login():
    return render_template("login.html.j2")


@views.route("/logout")
def do_logout():
    response = make_response(redirect("/login"))
    session["user_id"] = None
    response.set_cookie("user", "", expires=0)
    return response


@views.route("/unsubscribe")
def do_unsubscribe():
    return render_template("unsubscribe.html.j2")


@views.route("/contact")
def do_contact():
    return render_template("contact.html.j2")


@views.route("/forgotpassword")
def do_forgotpassword():
    return render_template("forgotpassword.html.j2")


@views.route("/privacy")
def do_privacy():
    return render_template("/partials/info/privacy.html.j2")


@views.route("/termsofuse")
def do_termsofuse():
    return render_template("/partials/info/termsofuse.html.j2")


@views.route("/rss-feed-info")
def do_rss_feed_info():
    return render_template("/includes/podcast_feed_url.html.j2")


@views.route("/resetpassword")
def do_resetpassword_view():
    return handle_resetpassword_view()


@views.route("/app/profile")
@login_required
def do_app_profile():
    return render_template("profile.html.j2")


@views.route("/app/voices")
@login_required
def do_app_voices():
    return render_template(
        "voices.html.j2",
        base_voices=get_base_voices(),
        premium_voices=get_premium_voices(),
    )


@views.route("/app/content")
@login_required
def do_app_content():
    return render_template("add_content.html.j2")


@views.route("/app/delete-episodes", methods=["POST", "GET"])
@login_required
def do_delete_episodes():
    return delete_episodes()


@views.route(f"/profile/rss-feed/<string:userid>")
def do_serve_rss(userid):
    return serve_rss_feed(userid)
