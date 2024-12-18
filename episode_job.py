import argparse
from flask_app import create_app
from flask_app.modules.content.process_content import process_episode

""" this is a command-line wrapper around the process_episode function.  it should be
called from a task runner (I'm using tsp on linux at the time of writing).  Needs to
run the the flask app context to access the database and other app resources. """

# Initialize Flask app
app = create_app()


def main(content_id):
    with app.app_context():
        print("Running long-running task...")
        process_episode(content_id)  # Execute the task
        print("Task completed successfully.")


if __name__ == "__main__":
    with app.app_context():
        parser = argparse.ArgumentParser(description="Process an episode")
        parser.add_argument(
            "content_id", help="The content ID of the episode to process"
        )
        args = parser.parse_args()
        main(args.content_id)
