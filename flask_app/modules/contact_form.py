from flask import current_app, session, render_template, request
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email
from flask_app.modules.email import send_email
from flask_app.modules.contact import subscribe_contact

def handle_contactform_request():
  """Contact form handling"""

  email = request.form.get("email")
  message = request.form.get("message")
  marketing_subscribed = request.form.get("marketing_subscribed")

  if not email or not validate_email(email):
    return render_template(
      "partials/notifications/error_card.html.j2",
      error="Please enter an E-mail in the format you@yourname.com"
    ), 400

  if not message:
    return render_template(
      "partials/notifications/error_card.html.j2",
      error="Please enter a message"
    ), 400

  session['email'] = email

  if marketing_subscribed:
      subscribe_contact(email)

  id = DB.insert_query(
      """
      INSERT INTO contact_form (email, message)
      VALUES (%(email)s, %(message)s)
    """,
      {"email": email, "message": message},
  )

  if not id:
    current_app.logger.error(f"Problem inserting contact form for contact {email}")
    return render_template(
      "partials/notifications/error_card.html.j2",
      error="Problem sending form."
    ), 400

  # send email to customer service
  send_email(
      subject=f" {current_app.config['STORE_NAME']} Customer Inquiry",
      sender=email,
      recipients=[current_app.config["STORE_CS_EMAIL"]],
      reply_to=email,
      text_body=render_template("emails/contact.txt.j2", email=email, message=message),
  )

  return render_template(
    "partials/notifications/success_card.html.j2",
    message="<h1>Submitted!</h1>Thank you for contacting us.  We will get back to you shortly."
  )
