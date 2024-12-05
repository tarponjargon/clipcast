import pymysql
from flask import g, current_app


class MySQL(object):
    """This is an updated and simplified version of
    https://github.com/rcbensley/flask-pymysql/blob/master/flask_pymysql/__init__.py"""

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if hasattr(app, "teardown_appcontext"):
            app.teardown_appcontext(self.teardown)

    @property
    def connect(self):
        kwargs = {
            "user": current_app.config["MYSQL_USER"],
            "password": current_app.config["MYSQL_PASSWORD"],
            "host": current_app.config["MYSQL_HOST"],
            "database": current_app.config["MYSQL_DATABASE"],
            "autocommit": current_app.config["MYSQL_AUTOCOMMIT"],
        }

        return pymysql.connect(**kwargs)

    @property
    def connection(self):
        if "mysql_db" not in g:
            g.mysql_db = self.connect
        return g.mysql_db

    def teardown(self, exception):
        db = g.pop("mysql_db", None)
        if db is not None:
            db.close()
