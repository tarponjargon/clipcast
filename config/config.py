from datetime import timedelta
import redis
import os


class Config(object):
    """config vars common to all Flask app environments"""

    STORE_EMAIL = os.environ.get("STORE_EMAIL")
    STORE_CS_EMAIL = os.environ.get("STORE_EMAIL")
    STORE_CODE = os.environ.get("STORE_CODE")
    STORE_NAME = os.environ.get("STORE_NAME")
    STORE_ADDRESS1 = ""
    STORE_CITY = ""
    STORE_STATE = ""
    STORE_ZIP = ""
    STORE_PHONE = ""
    STORE_PHONE_MOBILE = ""
    STORE_CUSTOMER_SERVICE = ""
    STORE_CUSTOMER_SERVICE_PHONE = ""
    STORE_CUSTOMER_SERVICE_HOURS = ""
    STORE_CS_HOUR_OPEN = 9
    STORE_CS_HOUR_CLOSE = 19
    STORE_TAGLINE = "Turn Web Content into Podcast Episodes"
    STORE_META_DESCRIPTION = "ClipCast clips out just the content from links you provide - excluding ads, menus, and comments. The content is then converted to audio using natural language AI Text-to-Speech, and made available in your podcast feed."
    STORE_LOGO = "/assets/images/logo.svg"
    STORE_FAVICON = "/favicon.ico"
    STORE_ACCESSIBILITY_CONTACT = os.environ.get("STORE_EMAIL")
    STORE_ADMIN = os.environ.get("STORE_EMAIL")
    ERROR_NOTIFY_URL = os.environ.get("ERROR_NOTIFY_URL")
    ERROR_NOTIFY_AUTH = os.environ.get("ERROR_NOTIFY_AUTH")
    TEST_ACCOUNT_EMAIL = os.environ.get("TEST_ACCOUNT_EMAIL")
    TEST_ACCOUNT_PASSWORD = os.environ.get("TEST_ACCOUNT_PASSWORD")
    MAX_CONTENT_LENGTH = 2097152  # 2MB
    MAX_CHARACTERS = {
        "base": 30000,
        "premium": 70000,
    }
    MAX_EPISODES = {
        "base": 10,
        "premium": 30,
    }
    PAGE_SIZE = 10
    TTS_SENTENCE_CHUNK_SIZE = 4  # how many sentences to chunk together for TTS
    TRANSITION_VOICE = "echo"  # voice to use for intros/outros
    TEST_EMAILS = [os.environ.get("TEST_EMAIL1"), os.environ.get("TEST_EMAIL2")]
    COMMENTS_SELECTORS = [
        ".comment",
        ".comments",
        ".comment-body",
        ".comment-content",
        ".comment-text",
        ".comment-text-content",
        ".comment-text",
        "#comments",
    ]
    EPISODE_RETENTION_DAYS = 90

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    DEFAULT_MAIL_SENDER = os.environ.get("STORE_EMAIL")

    HASHING_ALGORITHM = os.environ.get("HASHING_ALGORITHM")

    # store defaults
    DEFAULT_IMAGE = os.environ.get("DEFAULT_IMAGE")
    GTM_ID = ""
    SITE_CODE = "clipcast"
    PRODUCT_IMAGE_PATH = "/assets/images"
    # these fields cannot be set to the session by request params, only from the server side
    FORBIDDEN_FIELDS = ["user_id"]
    SESSION_DEFAULTS = {}
    DEFAULT_BASE_VOICE = "co.uk"
    DEFAULT_PREMIUM_VOICE = "alloy"

    # db conns
    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_AUTOCOMMIT = True
    MYSQL_LOG_QUERY = False

    # view/function cache (redis thru flask_caching) uses redis db3
    CACHE_TYPE = "null"
    CACHE_REDIS_HOST = os.environ.get("REDIS_HOST")
    CACHE_REDIS_PORT = os.environ.get("REDIS_PORT")
    CACHE_REDIS_DB = os.environ.get("REDIS_CACHE_DB")
    CACHE_DEFAULT_TIMEOUT = 86400  # 1 day

    # sessions (redis thru flask-session) uses redis db4
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_NAME = os.environ.get("STORE_CODE")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=1440)
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.from_url(
        f"redis://{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_SESSION_DB')}"
    )

    # 2-way encryption/decryption algorithm for obscuring IDs
    OBSCURE_SALT = os.environ.get("OBSCURE_SALT")

    RANDOM_STRING = os.environ.get("RANDOM_STRING")

    PRODUCTION = False
    FAILOVER = False

    # S3 config
    S3_URL = os.environ.get("S3_URL")
    S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
    S3_SECRET_ACCESS_KEY = os.environ.get("S3_SECRET_ACCESS_KEY")
    S3_BUCKET = os.environ.get("S3_BUCKET")
    S3_PUBLIC_URL = os.environ.get("S3_PUBLIC_URL")

    # Google sign-in app
    GOOGLE_LOGIN_APP_CLIENT_ID = os.environ.get("GOOGLE_LOGIN_APP_CLIENT_ID")
    GOOGLE_LOGIN_APP_CLIENT_SECRET = os.environ.get("GOOGLE_LOGIN_APP_CLIENT_SECRET")


class development(Config):
    STORE_EMAIL = os.environ.get("STORE_EMAIL")
    APP_ROOT = "/project/flask_app"
    TMP_DIR = "/project/tmp"
    HOME_DIR = "/project"
    PUBLIC_HTML = "/project/public_html"
    DEVELOPMENT = True
    DEBUG = True
    STORE_URL = os.environ.get("BASE_URL")
    INTERNAL_IP = os.environ.get("BASE_URL")
    GTM_ID = ""
    GA_MEASUREMENT_ID = ""
    GA_MEASUREMENT_PROTOCOL_SECRET = ""
    TMP_DIR = "/project/tmp"


class staging(Config):
    APP_ROOT = "/home/clipcast/flask_app"
    PUBLIC_HTML = "/home/clipcast/public_html"
    TMP_DIR = "/home/clipcast/tmp"
    HOME_DIR = "/home/clipcast"
    DEVELOPMENT = True
    DEBUG = True
    CACHE_TYPE = "RedisCache"
    STORE_URL = os.environ.get("STAGING_URL")
    GTM_ID = ""
    GA_MEASUREMENT_ID = ""
    GA_MEASUREMENT_PROTOCOL_SECRET = ""


class testing(Config):
    APP_ROOT = "/home/clipcast-testing/flask_app"
    PUBLIC_HTML = "/home/clipcast-testing/public_html"
    TMP_DIR = "/home/clipcast/tmp"
    HOME_DIR = "/home/clipcast"
    TESTING = True
    DEBUG = True
    CACHE_TYPE = "RedisCache"
    STORE_URL = os.environ.get("TESTING_URL")
    WTF_CSRF_ENABLED = False
    DEVELOPMENT = False
    GTM_ID = ""
    GA_MEASUREMENT_ID = ""
    GA_MEASUREMENT_PROTOCOL_SECRET = ""


class production(Config):
    APP_ROOT = "/home/clipcast/flask_app"
    PUBLIC_HTML = "/home/clipcast/public_html"
    TMP_DIR = "/home/clipcast/tmp"
    HOME_DIR = "/home/clipcast"
    DEVELOPMENT = False
    DEBUG = False
    CACHE_TYPE = "RedisCache"
    STORE_URL = os.environ.get("PRODUCTION_URL")
    MAIL_DEBUG = True
    GTM_ID = ""
    GA_MEASUREMENT_ID = ""
    GA_MEASUREMENT_PROTOCOL_SECRET = ""
    PRODUCTION = True
