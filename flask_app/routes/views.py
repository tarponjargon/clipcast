import validators
import stripe
import json
from urllib.parse import unquote
from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    session,
    make_response,
    current_app,
)
from flask_app.modules.extensions import DB, oauth
from flask_app.modules.http import login_required, check_if_logged_in_already
from flask_app.modules.user.resetpassword import handle_resetpassword_view
from flask_app.modules.user.notifications import get_notifications
from flask_app.modules.user.delete_episodes import delete_episodes
from flask_app.modules.user.voices import get_base_voices, get_premium_voices
from flask_app.modules.user.rss import serve_rss_feed
from flask_app.modules.user.queue import get_queue
from flask_app.modules.user.login import handle_google_login_callback
from flask_app.modules.user.user import User
from flask_app.modules.content.add_podcast_content import add_podcast_url
from flask_app.modules.payment.webhooks import handle_webhook

views = Blueprint("views", __name__)

google = oauth.register(
    name="google",
    client_id=current_app.config.get("GOOGLE_LOGIN_APP_CLIENT_ID"),
    client_secret=current_app.config.get("GOOGLE_LOGIN_APP_CLIENT_SECRET"),
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "email profile"},
)

stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY")


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
        total_episodes=data.get("total_episodes"),
        plan_count=data.get("plan_count"),
        over_limit=data.get("over_limit"),
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
    return render_template("privacy.html.j2")


@views.route("/termsofuse")
def do_termsofuse():
    return render_template("termsofuse.html.j2")


@views.route("/digital-accessibility")
def do_digital_accessibility():
    return render_template("digital_accessibility.html.j2")


@views.route("/rss-feed-info")
def do_rss_feed_info():
    return render_template("/includes/podcast_feed_url.html.j2")


@views.route("/test-article")
def do_test_article():
    return render_template("test_article.html.j2")


@views.route("/help")
def do_help():
    return render_template("help.html.j2")


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


@views.route("/app/quickstart")
@login_required
def do_app_quickstart():
    return render_template("quick_start.html.j2")


@views.route("/app/delete-episodes", methods=["POST", "GET"])
@login_required
def do_delete_episodes():
    return delete_episodes()


@views.route(f"/profile/rss-feed/<string:userid>")
def do_serve_rss(userid):
    return serve_rss_feed(userid)


@views.route("/google/start-login")
def do_google_login():
    redirect_uri = current_app.config.get("STORE_URL") + "/google/callback"
    return google.authorize_redirect(redirect_uri)


@views.route("/google/callback")
def do_google_login_callback():
    return handle_google_login_callback(google)


@views.route("/app/add-url")
def do_app_add_url():

    # check that a valid URL is provided
    encoded_url = request.values.get("url")
    current_app.logger.debug(f"Adding URL: {encoded_url}")
    if not encoded_url:
        return render_template("error.html.j2", error="No URL was passed"), 400
    url = unquote(encoded_url)
    if not validators.url(url):
        return render_template("error.html.j2", error="Please enter a valid URL"), 400

    # check that the user is logged in
    if not session.get("user_id"):
        # this might end up being a landmine, but I'm going to set the url to the session to be processed after login/signup
        session["addurl"] = url
        return redirect("/login")

    # add the URL to the database
    resp = add_podcast_url(url, session.get("user_id"))

    if not resp.get("response_code") == 200:
        return render_template("error.html.j2", error=resp.get("message")), resp.get(
            "response_code"
        )

    # redirect to the app page
    response = make_response(redirect("/app"))
    return response


@views.route("/app/payment-success")
@login_required
def do_payment_success():
    session = stripe.checkout.Session.retrieve(request.args.get("session_id"))
    customer = stripe.Customer.retrieve(session.customer)
    return render_template("payment_success.html.j2", customer=customer)


@views.route("/app/payment-cancel")
@login_required
def do_payment_cancel():
    return render_template("payment_cancel.html.j2")


@views.route("/app/payment-portal", methods=["POST"])
@login_required
def do_payment_portal():
    # Get the customer's ID
    user = User.from_id(session.get("user_id"))

    stripe_customer = user.get_stripe_customer()
    if not stripe_customer:
        return render_template("error.html.j2", error="No customer ID found"), 400

    # Create a portal session
    stripe_session = stripe.billing_portal.Session.create(
        customer=stripe_customer,
        return_url=current_app.config.get("STORE_URL") + "/app",
    )

    # Redirect to the URL returned on the session
    return redirect(stripe_session.url, code=303)


@views.route("/app/stripe-checkout", methods=["POST"])
@login_required
def do_stripe_checkout():
    price_id = request.form.get("price_id")
    base_url = current_app.config.get("STORE_URL")
    stripe_session = stripe.checkout.Session.create(
        client_reference_id=session.get("user_id"),
        success_url=base_url + "/app/payment-success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=base_url + "/app/payment-cancel",
        mode="subscription",
        payment_method_types=["card"],
        line_items=[
            {
                "price": current_app.config.get("STRIPE_PRICE_ID"),
                "quantity": 1,
            }
        ],
    )

    # Redirect to the URL returned on the session
    return redirect(stripe_session.url, code=303)


@views.route("/app/subscription-webhook", methods=["POST"])
def webhook_received():
    return handle_webhook()
