import json
from flask import (
    request,
    session,
    current_app,
)
from flask_app.modules.extensions import DB
from flask_app.modules.user.user import get_user_id_by_email


def handle_webhook():
    webhook_secret = request.values.get("STRIPE_WEBHOOK_SECRET")
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get("stripe-signature")
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret
            )
            data = event["data"]
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event["type"]
    else:
        data = request_data["data"]
        event_type = request_data["type"]
    data_object = data["object"]

    data_json = json.dumps(data_object)

    # Handle the event
    if event_type == "checkout.session.completed":
        # current_app.logger.info(f"{event_type}: {data_json}")
        pass
    elif event_type == "customer.subscription.created":
        # current_app.logger.info(f"{event_type}: {data_json}")
        pass
    elif event_type == "customer.subscription.deleted":
        # current_app.logger.info(f"{event_type}: {data_json}")
        pass
    elif event_type == "customer.subscription.paused":
        # current_app.logger.info(f"{event_type}: {data_json}")
        pass
    elif event_type == "invoice.created":
        # current_app.logger.info(f"{event_type}: {data_json}")
        pass
    elif event_type == "invoice.paid":
        # current_app.logger.info(f"{event_type}: {data_json}")
        pass
    elif event_type == "invoice.payment_failed":
        # current_app.logger.info(f"{event_type}: {data_json}")pass
        pass
    elif event_type == "invoice.payment_succeeded":
        # current_app.logger.info(f"{event_type}: {data_json}")
        pass
        # invoice_paid(data_object)
    # ... handle other event types
    else:
        current_app.logger.error("Unhandled event type {}".format(event_type))

    return {"status": "success"}


def invoice_paid(data):
    # add or update user subscription
    user_id = get_user_id_by_email(data["customer_email"])

    ins = DB.insert_query(
        """
        INSERT INTO subscription (
          user_id,
          email,
          customer_name,
          stripe_customer,
          subscription_id,
          created,
          active
        )
        VALUES (
          %(user_id)s,
          %(email)s,
          %(customer_name)s,
          %(stripe_customer)s,
          %(subscription_id)s,
          FROM_UNIXTIME(%(created)s),
          1
        )
        ON DUPLICATE KEY UPDATE
          stripe_customer = %(stripe_customer)s,
          subscription_id = %(subscription_id)s,
          active = 1
      """,
        {
            "user_id": user_id,
            "email": data["customer_email"],
            "customer_name": data["customer_name"],
            "stripe_customer": data["customer"],
            "subscription_id": data["lines"]["data"][0]["subscription"],
            "created": data["created"],
        },
    )

    if not ins:
        current_app.logger.error("Failed to insert subscription")
        return {"status": "error"}, 500

    return {"status": "success"}
