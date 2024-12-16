import os
from rq import Worker, Queue
from redis import Redis
from flask_app import create_app

# Initialize Flask app
app = create_app()

# Redis connection
redis_url = f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_RQ_DB')}"
redis_conn = Redis.from_url(redis_url)

if __name__ == "__main__":
    with app.app_context():
        worker = Worker([os.environ.get("RQ_TASK_QUEUE")], connection=redis_conn)
        worker.work()
