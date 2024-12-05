from flask import current_app, session, request, render_template, render_template_string
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email


def get_contact_id_by_email(email):
    """Returns user_id if the contact record exists

    Args:
      email (str): The E-mail address

    Returns:
      int: The id if found, else None
    """
    q = DB.fetch_one(
        """
      SELECT id
      FROM contact WHERE email = %(email)s
    """,
        {"email": email},
    )

    return q.get("id") if q else None


def subscribe_contact(email):
    """Subscribes a contact

    Args:
      email (str): The E-mail address
    """

    subscribed_message = "<h3>Thank You</h3>You are now subscribed to our list."

    if not email or not validate_email(email):
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please enter an E-mail in the format you@yourname.comm",
            ),
            400,
        )

    existing_contact_id = get_contact_id_by_email(email)

    if existing_contact_id:
        success = DB.update_query(
            """
        UPDATE contact
        SET subscribed = 1, subscribed_at = NOW(), unsubscribed_at = NULL
        WHERE id = %(id)s
      """,
            {"id": existing_contact_id},
        )
        if success:
            return render_template(
                "partials/notifications/success_card.html.j2",
                message=subscribed_message,
            )
        else:
            current_app.logger.error(
                f"Problem updating subscription to 'subscribed' for contact {email}"
            )
            return (
                render_template(
                    "partials/notifications/error_card.html.j2",
                    error="Problem updating subscription.  Please <a href='/contact'>contact us</a>.",
                ),
                400,
            )

    id = DB.insert_query(
        """
      INSERT INTO contact (email, subscribed, subscribed_at)
      VALUES (%(email)s, 1, NOW())
    """,
        {"email": email},
    )

    if not id:
        current_app.logger.error(
            f"Problem creating subscription 'subscribed' for contact {email}"
        )
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Problem adding subscription.  Please <a href='/contact'>contact us</a>.",
            ),
            400,
        )

    session["email"] = email

    return render_template(
        "partials/notifications/success_card.html.j2", message=subscribed_message
    )


def unsubscribe_contact():
    """Unsubscribes a contact

    Args:
      email (str): The E-mail address
    """
    email = request.form.get("email")

    if not email or not validate_email(email):
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Please enter an E-mail in the format you@yourname.com",
            ),
            400,
        )

    existing_contact_id = get_contact_id_by_email(email)
    if not existing_contact_id:
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="This e-mail is not currently subscribed to our list.",
            ),
            400,
        )

    success = DB.update_query(
        """
      UPDATE contact
      SET subscribed = 0, unsubscribed_at = NOW()
      WHERE id = %(id)s
    """,
        {"id": existing_contact_id},
    )
    if not success:
        current_app.logger.error(
            f"Problem updating subscription to 'unsubscribed' for contact {email}"
        )
        return (
            render_template(
                "partials/notifications/error_card.html.j2",
                error="Problem updating subscription.  Please <a href='/contact'>contact us</a>.",
            ),
            400,
        )

    return render_template(
        "partials/notifications/success_card.html.j2",
        message="You are now unsubscribed from our list.",
    )


def toggle_subscription():
    """Toggles a contact's subscription status"""

    email = session.get("email")
    is_subscribed = request.args.get("subscribed")

    if (
        not email
        or not validate_email(email)
        or not is_subscribed
        or not is_subscribed in ["0", "1"]
    ):
        return (
            render_template_string(
                "Problem updating subscription.  Please <a href='/contact'>contact us</a>."
            ),
            400,
        )

    # since this function toggles, reverse their current subscription status
    new_subscribe_status = 0 if is_subscribed == "1" else 1

    id = get_contact_id_by_email(email)

    if id:
        if new_subscribe_status == 1:
            q = DB.update_query(
                """
          UPDATE contact
          SET subscribed = %(subscribed)s,
          subscribed_at = NOW(),
          unsubscribed_at = NULL
          WHERE id = %(id)s
        """,
                {"subscribed": new_subscribe_status, "id": id},
            )
        else:
            q = DB.update_query(
                """
          UPDATE contact
          SET subscribed = %(subscribed)s,
          unsubscribed_at = NOW()
          WHERE id = %(id)s
        """,
                {"subscribed": new_subscribe_status, "id": id},
            )
    else:
        q = DB.insert_query(
            """
        INSERT INTO contact (email, subscribed, subscribed_at)
        VALUES (%(email)s, %(subscribed)s, NOW())
      """,
            {"email": email, "subscribed": new_subscribe_status},
        )

    if not q:
        current_app.logger.error(f"Problem updating subscription for contact {email}")
        return (
            render_template_string(
                "Problem updating subscription.  Please <a href='/contact'>contact us</a>."
            ),
            400,
        )

    return render_template(
        "partials/profile/profile_subscription.html.j2", subscribed=new_subscribe_status
    )
