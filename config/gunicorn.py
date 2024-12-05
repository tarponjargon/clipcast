""" gunicorn webserver configuration """

import os
from glob import glob

workers = os.environ.get("GUNICORN_WORKERS") or 1
threads = os.environ.get("GUNICORN_THREADS") or 3
loglevel = os.environ.get("GUNICORN_LOGLEVEL") or "warning"
bind = f"{os.environ.get('RUN_HOST') or 'localhost'}:" + os.environ.get("APP_PORT") or 4051
reload = True
reload_extra_files = glob("flask_app/templates/**/*", recursive=True)
errorlog = "-" if os.environ.get("ENV") == "development" else "logs/gunicorn-error.log"
accesslog = None if os.environ.get("ENV") == "development" else "logs/gunicorn-access.log"
pidfile = None if os.environ.get("ENV") == "development" else "tmp/gunicorn.pid"
