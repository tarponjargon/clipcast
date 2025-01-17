import base64
import hashlib
import secrets
from flask import request, current_app, session
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import match_uuid
from flask_app.modules.http import get_env_vars


def create_user(email, password):
    """Creates a new user account, returns the user_id if successful

    Args:
      email (str): The E-mail address that is the login for the account
      password (str): The password for the account

    Returns:
      int: The user_id if successful, else 0
    """
    if not email or not password:
        return None

    existing_user_id = get_user_id_by_email(email)
    if existing_user_id:
        return existing_user_id

    password_hash = hash_password(password)
    id = DB.insert_query(
        """
      INSERT INTO user (
        user_id,
        email,
        password_hash,
        accepted_terms,
        is_active,
        base_voice,
        premium_voice,
        created_at
      )
      VALUES (
        UUID(),
        %(email)s,
        %(password_hash)s,
        1,
        1,
        %(base_voice)s,
        %(premium_voice)s,
        NOW()
      )
    """,
        {
            "email": email,
            "password_hash": password_hash,
            "base_voice": current_app.config["DEFAULT_BASE_VOICE"],
            "premium_voice": current_app.config["DEFAULT_PREMIUM_VOICE"],
        },
    )

    return get_user_id_by_email(email)


def hash_password(password, salt=None, iterations=260000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(
        current_app.config.get("HASHING_ALGORITHM"), iterations, salt, b64_hash
    )


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == current_app.config.get("HASHING_ALGORITHM")
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)


def get_user_id_by_email(email):
    """Returns user_id if the customer record exists and has a password

    Args:
      email (str): The E-mail address that is the login for the account

    Returns:
      int: The user_id if found, else 0
    """
    id = 0
    q = DB.fetch_one(
        """
      SELECT user_id
      FROM user WHERE email = %(email)s
      AND (password_hash IS NOT NULL and password_hash != '')
    """,
        {"email": email},
    )

    return q.get("user_id") if q else None


def login_user(user):
    """Logs in a user to the session"""
    if not user or not isinstance(user, User):
        current_app.logger.error("login_user: user is not a User object")
        return

    # set user values to session
    session["user_id"] = user.get_id()
    for key, val in user.get_user().items():
        # current_app.logger.debug(f"login_user: setting {key} to session")
        session[key] = val

    # add feed url to the session so you don't have to piece it together
    session["feed_url"] = user.get_feed_url()

    # current_app.logger.debug("login_user: {}".format(user.get_id()))

    # record login
    envs = get_env_vars()
    DB.insert_query(
        """
      INSERT INTO login (
        user_id,
        email,
        user_agent,
        ip_address,
        device_code,
        path
      )
      VALUES (
        %(user_id)s,
        %(email)s,
        %(user_agent)s,
        %(ip_address)s,
        %(device_code)s,
        %(path)s
      )
    """,
        {
            "user_id": user.get_id(),
            "email": user.get_email(),
            "user_agent": envs.get("user_agent"),
            "ip_address": envs.get("ip_address"),
            "device_code": envs.get("device_code"),
            "path": request.path,
        },
    )

    return user.get_id()


def load_user(user_id):
    """Load user data from the DB

    Args:
      user_id (int): The user_id

    Returns:
      dict: The user data loaded from the db
    """

    sql = f"SELECT * FROM user WHERE user_id = %(user_id)s"
    params = {"user_id": user_id}
    return DB.fetch_one(sql, params)


class User(object):
    def __init__(self, user=None):
        if user is None:
            user = {}

        self.data = user

    def get_user(self):
        """Gets user

        Returns:
          User: The User
        """
        return self.data

    def get_id(self):
        """Gets user ID

        Returns:
          str: The user ID
        """
        return self.data.get("user_id")

    def get_email(self):
        """Gets user email

        Returns:
          str: The user email
        """
        return self.data.get("email")

    def get_plan(self):
        """Gets user plan

        Returns:
          str: the plan name
        """
        return self.data.get("plan", "base")

    def update_voice(self, plan, voice_code):
        """Updates the user's selected voice"""
        if plan not in ["base", "premium"]:
            return False

        if not voice_code:
            return False

        sql = f"""
            UPDATE user
            SET {plan}_voice = %(voice_code)s
            WHERE user_id = %(user_id)s
        """
        params = {"voice_code": voice_code, "user_id": self.get_id()}
        DB.update_query(sql, params)
        self.data[f"{plan}_voice"] = voice_code
        session[f"{plan}_voice"] = voice_code
        return True

    def update_plan(self, plan):
        """Updates the user's selected plan"""
        if plan not in ["base", "premium"]:
            return False
        sql = f"""
            UPDATE user
            SET plan = %(plan)s
            WHERE user_id = %(user_id)s
        """
        params = {"plan": plan, "user_id": self.get_id()}
        DB.update_query(sql, params)
        self.data["plan"] = plan
        session["plan"] = plan
        return True

    def get_feed_url(self):
        """Gets the uer's feed url

        Returns:
          str: The feed url
        """

        if self.get_id() is None:
            return None
        return (
            current_app.config.get("STORE_URL") + "/profile/rss-feed/" + self.get_id()
        )

    @classmethod
    def from_id(cls, user_id):
        """Constructor creates User object from user_id

        Args:
          user_id (int): The customer ID

        Returns:
          User: the instantiated User object
        """
        user_data = load_user(user_id)
        if not user_data or not user_data.get("user_id"):
            return None

        return cls(user_data)
