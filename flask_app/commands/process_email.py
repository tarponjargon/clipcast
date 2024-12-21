import re
import imaplib
import email
from email.header import decode_header
from flask import current_app
from flask_app.modules.user.user import User
from flask_app.modules.content.add_podcast_content import (
    add_podcast_content,
    add_podcast_url,
)


# Account credentials
EMAIL = current_app.config["MAIL_USERNAME"]
PASSWORD = current_app.config["MAIL_PASSWORD"]


def clean(text):
    """Clean text for creating safe filenames."""
    return "".join(c if c.isalnum() else "_" for c in text)


def safe_decode_header(header_value):
    """Safely decode email header values."""
    try:
        decoded, encoding = decode_header(header_value)[0]
        if isinstance(decoded, bytes):
            # If it's bytes, decode to a string
            return decoded.decode(encoding if encoding else "utf-8")
        return decoded
    except Exception as e:
        print(f"Error decoding header: {e}")
        return "Unknown"


def dump_headers(msg):
    """Dump all email headers as text."""
    print("Email Headers:")
    for key, value in msg.items():
        try:
            decoded_value = decode_header(value)
            header_parts = []
            for part, encoding in decoded_value:
                if isinstance(part, bytes):
                    # Decode bytes to string
                    header_parts.append(
                        part.decode(encoding if encoding else "utf-8", errors="replace")
                    )
                else:
                    header_parts.append(part)
            print(f"{key}: {' '.join(header_parts)}")
        except Exception as e:
            print(f"{key}: [Error decoding header: {e}]")
    print("=" * 50)


def get_msg_body(msg):
    # If the email has a body

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            # If part is text/plain or text/html
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                break
    else:
        # Extract content type of email
        if msg.get_content_type() == "text/plain":
            body = msg.get_payload(decode=True)
    return body


def get_body_urls(body):
    urls = []

    # Regex pattern for URLs
    url_pattern = r"https?://[^\s]+"

    # Find all URLs
    urls = re.findall(url_pattern, body)

    return urls


def handle_email(response, email_id):
    # Parse a byte email into a message object
    msg = email.message_from_bytes(response[1])

    # print the "To" email address
    to = msg.get("To")
    print(f"To: {to}")

    # Regular expression to match and capture the UUID
    regex = r"^clipcast\.submit\+([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})@gmail\.com$"

    # Validate and capture the UUID
    match = re.match(regex, to)

    uuid = None
    if match:
        uuid = match.group(1)
    else:
        return

    print(f"user id extracted from email: {uuid}")

    user = User.from_id(uuid)

    if not user or not user.get_id():
        print("No user found for {}".format(uuid))
        return

    # get body
    body_bytes = get_msg_body(msg)
    body = body_bytes.decode("utf-8")

    subject = msg.get("Subject", "")
    print(f"Subject: {subject}")

    if not body or not isinstance(body, str) or not len(body) > 0:
        print("No body found in email")
        return

    # Extract URLs from the email body
    urls = get_body_urls(body)

    if urls and len(urls) > 0:
        # Output the extracted URLs
        for url in urls:
            print(f"adding url {url}")
            resp = add_podcast_url(url, uuid)
            print(f"result: {resp}")

    else:
        # if no urls are in the body, then
        # input the content directly into the database
        print(f"{body}")
        resp = add_podcast_content(body, uuid)
        print(f"result: {resp}")


def check_inbox():
    # Connect to the Gmail IMAP server
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    # Login to your account
    mail.login(EMAIL, PASSWORD)

    # Select the mailbox you want to use
    mail.select("inbox")

    # Search for all emails
    status, messages = mail.search(None, "ALL")

    # Convert messages to a list of email IDs
    email_ids = messages[0].split()

    print(f"Total Emails: {len(email_ids)}")

    for email_id in email_ids:
        # Fetch the email by ID
        res, msg = mail.fetch(email_id, "(RFC822)")

        for response in msg:
            if isinstance(response, tuple):
                handle_email(response, email_id)
                try:
                    # Mark the email for deletion
                    mail.store(email_id, "+FLAGS", "\\Deleted")
                    print(f"Marked email {email_id.decode()} for deletion")
                except Exception as e:
                    print(f"Error deleting email {email_id.decode()}: {e}")

    # Permanently delete the marked emails
    mail.expunge()
    print("Deleted all marked emails.")

    # Close the connection and logout
    mail.close()
    mail.logout()


@current_app.cli.command("process_email")
def process_email():
    check_inbox()
