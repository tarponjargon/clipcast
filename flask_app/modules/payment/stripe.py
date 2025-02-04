import os
import stripe
from flask import current_app, session, render_template

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def handle_payment_status_request():
    stripe_sub = get_stripe_subscription_by_email(session.get("email"))
    stripe_status = stripe_sub.get("status") if stripe_sub else None
    current_app.logger.debug(f"stripe_status: {stripe_status}")
    return render_template(
        "partials/profile/payment_status.html.j2", status=stripe_status
    )


def get_stripe_customer_by_email(email):
    """
    Get a Stripe customer by email address

    Args:
        email (str): The customer's email address

    Returns:
        stripe.Customer: The customer object if found, else None
    """
    customers = stripe.Customer.list(email=email).data
    return customers[0] if customers else None  # Return first match or None


def get_stripe_subscription_by_id(stripe_customer_id):
    """
    Get the status of a customer's subscription

    Args:
        stripe_customer_id (str): The customer's Stripe ID

    Returns:
        str: The subscription status if found, else None

    """
    if not stripe_customer_id:
        return None
    subscriptions = stripe.Subscription.list(customer=stripe_customer_id).data
    if subscriptions:
        # current_app.logger.debug(f"subscriptions: {subscriptions[0]}")
        return subscriptions[0]
    return None


def get_stripe_subscription_by_email(email):
    """
    Get the status of a customer's subscription by email

    Args:
        email (str): The customer's email address

    Returns:
        str: The subscription status if found, else None

    """
    customer = get_stripe_customer_by_email(email)
    if customer:
        return get_stripe_subscription_by_id(customer.id)
    return None
