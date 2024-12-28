from datetime import datetime
import re
import logging
import requests
from functools import wraps
from urllib.parse import parse_qs, urlencode
from flask import render_template, request, session, request, current_app, redirect
from flask_app.modules.helpers import sanitize, convert_to_ascii


def page_not_found(e):
    """404 error template as text/html and a 404 response code
    Args:
      code_or_exception (Union[Type[flask.typing.GenericException], int])
    Returns:
       str: 404 error template as text/html
       int: 404 response code
    """
    return render_template("404.html.j2"), 404


def error_500(e):
    """500 error template as text/html and a 500 response code
    Args:
      code_or_exception (Union[Type[flask.typing.GenericException], int])
    Returns:
       str: 500 error template as text/html
       int: 500 response code
    """
    report_error_http(str(e))
    return render_template("500.html.j2"), 404


def api_route_error(message="Not found", status_code=404):
    """Error response for API route

    Args:
      message (str): Custom message or "Not found"
      status_code (int): The HTTP status code, default 404

    Returns:
       dict: body
       int: response code
    """
    return {"error": True, "message": message, "success": False}, status_code


def add_security_headers(response):
    """Adds common security headers to Flask's response object

    Args:
      response (response): Flask's response object

    Returns:
      response: Flask's response object with additional security headers
    """

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


def session_get(key, default=""):
    """Helper for retrieving session variables in (somewhat) case-insensitive fashion

    Args:
      key (str): The key of the session variable
      default (any): The default value to return if the key is not found

    Returns:
      str: The value of the session variable, "" if none
    """

    value = default
    if not key:
        return value

    if session.get(key):
        value = session.get(key)
    elif session.get(key.lower()):
        value = session.get(key.lower())
    elif session.get(key.upper()):
        value = session.get(key.upper())

    if value and isinstance(value, str):
        value = value.strip()
        value = convert_to_ascii(value)

    # print("SESSION VAR", key, value)
    return value


def session_safe_get(key, default=""):
    """Wrapper for session_get for use in templates, runs the value thru
    a sanitizer

    Args:
      key (str): The key of the session variable
      default (any): The default value to return if the key is not found

    Returns:
      str: The value of the session variable, "" if none
    """

    stored = session_get(key, default)
    if stored:
        return sanitize(stored)
    else:
        return default


def login_required(f):
    """Decorator to check if user is logged in

    Args:
      f (function): The function to decorate

    Returns:
      function: The decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            redirect_url = "/login"
            return redirect(redirect_url)
        return f(*args, **kwargs)

    return decorated_function


def check_if_logged_in_already(f):
    """Decorator to check if user is logged in

    Args:
      f (function): The function to decorate

    Returns:
      function: The decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            return redirect("/app")
        return f(*args, **kwargs)

    return decorated_function


def is_authenticated(f):
    """Decorator to checks if user is authenticated and if not returns 403

    Args:
      f (function): The function to decorate

    Returns:
      function: The decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return {
                "success": False,
                "error": True,
                "errors": ["Not authenticated"],
            }, 403
        return f(*args, **kwargs)

    return decorated_function


def report_error_http(error):
    """POST given error to notification service

    Args:
      error (str): The error message to send
    """
    url = current_app.config.get("ERROR_NOTIFY_URL")
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "X-Auth": current_app.config.get("ERROR_NOTIFY_AUTH"),
    }
    store_code = current_app.config.get("STORE_CODE")
    data = {"error": error, "site": store_code}
    response = None
    response_data = {}
    try:
        response = requests.post(url, headers=headers, data=urlencode(data), timeout=2)
        response.raise_for_status()
    except Exception as err:
        current_app.logger.info("HTTP error sending log info occurred {}".format(err))
        pass
    if response and response.status_code != 200:
        current_app.logger.info(
            "HTTP error sending log info occurred {}".format(response.content)
        )
        pass


def get_device_code():
    """A quite legacy method for determining device type.

    Returns:
      str: "P" = Phone, "T" = Tablet, "D" = Desktop
    """

    ua = request.headers.get("User-Agent")

    if not ua or not isinstance(ua, str):
        return "D"

    phone1 = re.compile(
        r"android.+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge\ |maemo|meego.+mobile|midp|mmp|netfront|opera\ m(ob|in)i|palm(\ os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows\ (ce|phone)|xda|xiino",
        re.IGNORECASE,
    )
    if phone1.search(ua):
        return "P"

    phone2 = re.compile(
        r"^(1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a\ wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r\ |s\ )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1\ u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp(\ i|ip)|hs\-c|ht(c(\-|\ |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac(\ |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt(\ |\/)|klon|kpt\ |kwc\-|kyo(c|k)|le(no|xi)|lg(\ g|\/(k|l|u)|50|54|\-[a-w])|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-|\ |o|v)|zz)|mt(50|p1|v\ )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v\ )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-|\ )|webc|whit|wi(g\ |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-)",
        re.IGNORECASE,
    )
    if phone2.search(ua):
        return "P"

    tablet = re.compile(r"(tablet|ipad|playbook|silk|android)", re.IGNORECASE)
    if tablet.search(ua):
        return "T"

    phone3 = re.compile(r"(silk|android)", re.IGNORECASE)
    phone4 = re.compile(r"(mobi|opera mini)", re.IGNORECASE)
    if phone3.search(ua) and phone4.search(ua):
        return "P"

    return "D"


def get_env_vars():
    """Gets user environment variables

    Returns:
      dict: Dictionary containing environment variables
    """
    true_client_ip = request.headers.get("True-Client-IP")
    if not true_client_ip:
        true_client_ip = request.remote_addr
    device_code = get_device_code()
    return {
        "user_agent": request.headers.get("User-Agent", ""),
        "ip_address": true_client_ip if true_client_ip else request.remote_addr,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
        "device_code": device_code,
    }


class CustomHTTPErrorHandler(logging.Handler):
    """Custom logging handler to send critical errors to notification service"""

    def emit(self, record):
        log_entry = self.format(record)
        report_error_http(log_entry)
