import argparse
from flask import current_app
from flask_app import create_app
from flask_app.modules.content.process_content import process_episode
from flask_app.modules.http import report_error_http
from flask_app.modules.extensions import DB

""" this is a command-line wrapper around the process_episode function.  it should be
called from a task runner (I'm using tsp on linux at the time of writing).  Needs to
run the the flask app context to access the database and other app resources. """

# Initialize Flask app
app = create_app()


def main(content_id):
    with app.app_context():
        print("Processing episode {}".format(content_id))
        try:
            process_episode(content_id)
        except Exception as e:
            print(f"Task failed: {e}")
            report_error_http(f"Processing episode {content_id} failed: {e}")
            upd = DB.update_query(
                """
              UPDATE podcast_content SET
              current_status = 'error',
              error_message = %s,
              processing_end_time = NOW()
              WHERE content_id = %s
            """,
                (e, content_id),
            )
            return
        print("Task completed successfully.")


if __name__ == "__main__":
    with app.app_context():
        parser = argparse.ArgumentParser(description="Process an episode")
        parser.add_argument(
            "content_id", help="The content ID of the episode to process"
        )
        args = parser.parse_args()
        main(args.content_id)
