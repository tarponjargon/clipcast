import sys
import click
from flask import current_app
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import match_uuid


@current_app.cli.command("process_content")
def process_content():
    """Process content from the database"""

    errors = []
    q = DB.fetch_all(
        "SELECT content_id FROM podcast_content WHERE current_status = 'queued'"
    )

    for row in q.get("results", []):
        errors = process_episode(row.get("content_id"))
    if errors:
        print(f"Errors occurred: {errors}")
        sys.exit(1)


@current_app.cli.command("process_podcast_episode")
@click.argument("content_id")
def process_podcast_episode(content_id):
    """Process a specific episode from the database"""

    errors = []

    if not content_id or not match_uuid(content_id):
        print("No content ID provided")
        sys.exit(1)

    q = DB.fetch_one(
        "SELECT content_id FROM podcast_content WHERE current_status = 'queued' AND content_id = %s",
        (content_id),
    )

    if not q or not q.get("content_id"):
        print("Episode not found or already processed")
        sys.exit(1)

    errors = process_episode(content_id)
    if errors:
        print(f"Errors occurred processing {content_id}: {errors}")
        sys.exit(1)
