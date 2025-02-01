import os
import stripe
from flask import current_app

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


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


def get_subscription_status(stripe_customer_id):
    """
    Get the status of a customer's subscription

    Args:
        stripe_customer_id (str): The customer's Stripe ID

    Returns:
        str: The subscription status if found, else None

    """
    subscriptions = stripe.Subscription.list(customer=stripe_customer_id).data
    if subscriptions:
        return subscriptions[0].status
    return None


def get_subscription_status_by_email(email):
    """
    Get the status of a customer's subscription by email

    Args:
        email (str): The customer's email address

    Returns:
        str: The subscription status if found, else None

    """
    customer = get_stripe_customer_by_email(email)
    if customer:
        return get_subscription_status(customer.id)
    return None
