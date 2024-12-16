import time
from flask import current_app
from flask_app.modules.helpers import is_number

""" example task to get rq working - you can throw this away"""


def example(seconds):
    with current_app.app_context():
        print("Starting task")
        for i in range(seconds):
            print(i)
            if is_number(i):
                print("This is a number {}".format(i))
            else:
                print("This is not a number".format(i))

            time.sleep(1)
        print("Task completed")
