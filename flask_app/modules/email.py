""" E-mail module

Functions related to sending e-mail
"""

from threading import Thread
from flask import current_app
from flask_app.modules.extensions import mail
from flask_mail import Message


def send_async_email(app, msg):
    """Helper funtion for sending e-mail async.  Sends an email with flask-mail

    Args:
      app (app): The current flask app
      msg (Message): The flask-mail message to be sent
    """
    with app.app_context():
        mail.send(msg)


def send_email(
    subject,
    sender,
    recipients,
    cc=None,
    reply_to=None,
    text_body=None,
    html_body=None,
    bcc=None,
):
    """Send an e-mail asynchronously so it does not block the request

    Args:
      subject (str): The subject for the mail
      sender (str): The email for the "from" field
      recipients (list): A list of the email recipients
      cc (list): A list of the cc emails
      reply_to: The email for the "reply to" field
      text_body (str): The text part of the email
      html_body (str): The html part of the email

    Returns:
      Thread: The thread started for e-mail sending
    """
    current_app.logger.info(f"emailing {recipients}")

    msg = Message(
        subject=subject,
        sender=sender,
        cc=cc,
        reply_to=reply_to,
        recipients=recipients,
        bcc=bcc,
    )
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=(current_app._get_current_object(), msg))
    thr.start()
    return thr
