from time import sleep
from flask import (
    Blueprint,
    render_template,
    render_template_string,
    current_app,
    session,
    request,
)
from flask_app.modules.extensions import DB
from flask_app.modules.http import is_authenticated
from flask_app.modules.user.notifications import get_notifications
from flask_app.modules.user.login import handle_login_request
from flask_app.modules.user.signup import handle_signup_request
from flask_app.modules.user.forgotpassword import handle_forgotpassword_request
from flask_app.modules.user.updatepassword import handle_updatepassword_request
from flask_app.modules.user.updateemail import handle_updateemail_request
from flask_app.modules.content.add_podcast_content import (
    handle_add_url_post_request,
    handle_add_content_request,
)
from flask_app.modules.user.queue import get_queue, get_queue_item
from flask_app.modules.user.user import User
from flask_app.modules.contact_form import handle_contactform_request
from flask_app.modules.contact import (
    unsubscribe_contact,
    subscribe_contact,
    toggle_subscription,
)

partials = Blueprint("partials", __name__, url_prefix="/partials")


@partials.route("/privacy")
def do_privacy_partial():
    return render_template("/partials/info/privacy.html.j2")


@partials.route("/termsofuse")
def do_termsofuse_partial():
    return render_template("/partials/info/termsofuse.html.j2")


@partials.route("/base-plan-info")
def do_base_plan_partial():
    return render_template("/partials/info/base_plan_info.html.j2")


@partials.route("/premium-plan-info")
def do_premium_plan_partial():
    return render_template("/partials/info/premium_plan_info.html.j2")


@partials.route("/contact-form", methods=["POST"])
def do_contactform_request():
    return handle_contactform_request()


@partials.route("/login", methods=["POST"])
def do_login_request():
    return handle_login_request()


@partials.route("/signup", methods=["POST"])
def do_signup_request():
    return handle_signup_request()


@partials.route("/subscribe", methods=["POST"])
def do_subscribe_request():
    return subscribe_contact(request.form.get("email"))


@partials.route("/unsubscribe", methods=["POST"])
def do_unsubscribe_request():
    return unsubscribe_contact()


@partials.route("/forgotpassword", methods=["POST"])
def do_forgotpassword_request():
    return handle_forgotpassword_request()


@partials.route("/updatepassword", methods=["POST", "PUT"])
@is_authenticated
def do_updatepassword_request():
    return handle_updatepassword_request()


@partials.route("/updateemail", methods=["POST"])
@is_authenticated
def do_updateemail_request():
    return handle_updateemail_request()


@partials.route("/profile-email")
@is_authenticated
def do_profileemail_request():
    return render_template("/partials/profile/profile_email.html.j2")


@partials.route("/update-email-form")
@is_authenticated
def do_emailform_request():
    return render_template("/partials/profile/update_email_form.html.j2")


@partials.route("/profile-password")
@is_authenticated
def do_profilepassword_request():
    return render_template("/partials/profile/profile_password.html.j2")


@partials.route("/update-password-form")
@is_authenticated
def do_passwordform_request():
    return render_template("/partials/profile/update_password_form.html.j2")


@partials.route("/profile-subscription")
@is_authenticated
def do_profilesubscription_request():
    q = DB.fetch_one(
        """
      SELECT subscribed
      FROM contact
      WHERE email = %(email)s
    """,
        {"email": session.get("email")},
    )
    return render_template(
        "/partials/profile/profile_subscription.html.j2",
        subscribed=q.get("subscribed", 0),
    )


@partials.route("/update-profile-subscription")
@is_authenticated
def do_updatesubscription_request():
    return toggle_subscription()


@partials.route("/app/update-plan")
@is_authenticated
def do_updateplan_request():
    user = User.from_id(session.get("user_id"))
    if user.update_plan(request.args.get("plan")):
        return render_template_string("Plan updated")
    else:
        return render_template_string("Error updating plan"), 400


@partials.route("/app/notifications")
def do_notifications_request():
    return render_template(
        "/partials/profile/notifications.html.j2", notifications=get_notifications()
    )


@partials.route("/app/add-podcast-url", methods=["POST"])
@is_authenticated
def do_addurl_request():
    return handle_add_url_post_request(session.get("user_id"))


@partials.route("/app/add-podcast-content", methods=["POST"])
@is_authenticated
def do_addcontent_request():
    return handle_add_content_request(session.get("user_id"))


@partials.route("/app/update-voice")
@is_authenticated
def do_updatevoice_request():
    user = User.from_id(session.get("user_id"))
    if user.update_voice(request.args.get("plan"), request.args.get("voice")):
        return render_template_string("Voice updated")
    else:
        return render_template_string("Error updating voice"), 400


@partials.route("/app/queue")
@is_authenticated
def do_queue_request():
    page = request.args.get("page", 1)
    data = get_queue(session.get("user_id"), page)
    return render_template(
        "partials/profile/queue.html.j2",
        queue=data.get("results"),
        previous_page=data.get("previous_page"),
        next_page=data.get("next_page"),
    )


@partials.route("/app/queue-list")
@is_authenticated
def do_queue_list_request():
    page = request.args.get("page", 1)
    data = get_queue(session.get("user_id"), page)
    return render_template(
        "partials/profile/queue_list.html.j2",
        queue=data.get("results"),
        previous_page=data.get("previous_page"),
        next_page=data.get("next_page"),
    )


@partials.route("/app/queue-item/<string:content_id>")
@is_authenticated
def do_queue_item_request(content_id):
    item = get_queue_item(content_id)
    return render_template("partials/profile/queue_item.html.j2", item=item)
