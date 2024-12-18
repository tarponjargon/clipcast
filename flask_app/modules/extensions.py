""" Extensions

For loading flask extensions.  In a separate module from create_app to avoid circular imports.
"""

from flask import current_app
import redis
from flask_compress import Compress
from flask_caching import Cache
from flask_session import Session
from flask_mail import Mail
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_app.modules.database.flask_pymysql import MySQL

from .database.db_manager import DBManager

sess = Session()
compress = Compress()
db = MySQL()
cache = Cache()
mail = Mail()
login_manager = LoginManager()
DB = DBManager(db)
oauth = OAuth()
