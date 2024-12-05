from datetime import datetime
import re
import logging
import requests
from functools import wraps
from urllib.parse import parse_qs, urlencode
from flask import render_template, session, request, current_app, redirect
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

    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
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
  """ Decorator to check if user is logged in

  Args:
    f (function): The function to decorate

  Returns:
    function: The decorated function
  """

  @wraps(f)
  def decorated_function(*args, **kwargs):
      if not session.get('user_id'):
          return redirect('/login')
      return f(*args, **kwargs)
  return decorated_function

def check_if_logged_in_already(f):
  """ Decorator to check if user is logged in

  Args:
    f (function): The function to decorate

  Returns:
    function: The decorated function
  """

  @wraps(f)
  def decorated_function(*args, **kwargs):
      if session.get('user_id'):
          return redirect('/app')
      return f(*args, **kwargs)
  return decorated_function

def is_authenticated(f):
  """ Decorator to checks if user is authenticated and if not returns 403

  Args:
    f (function): The function to decorate

  Returns:
    function: The decorated function
  """

  @wraps(f)
  def decorated_function(*args, **kwargs):
      if not session.get('user_id'):
        return {"success": False, "error": True, "errors": ["Not authenticated"]}, 403
      return f(*args, **kwargs)
  return decorated_function

def report_error_http(error):
  """ POST given error to notification service

  Args:
    error (str): The error message to send
  """
  url = current_app.config.get('ERROR_NOTIFY_URL')
  headers = {
    "Content-type": "application/x-www-form-urlencoded",
    'X-Auth': current_app.config.get('ERROR_NOTIFY_AUTH')
  }
  store_code = current_app.config.get('STORE_CODE')
  data = {
    'error': error,
    'site': store_code
  }
  response=None
  response_data={}
  try:
      response = requests.post(url, headers=headers, data=urlencode(data), timeout=2)
      response.raise_for_status()
  except Exception as err:
      current_app.logger.info("HTTP error sending log info occurred {}".format(err))
      pass
  if response and response.status_code != 200:
      current_app.logger.info("HTTP error sending log info occurred {}".format(response.content))
      pass

class CustomHTTPErrorHandler(logging.Handler):
  """ Custom logging handler to send critical errors to notification service """
  def emit(self, record):
    log_entry = self.format(record)
    report_error_http(log_entry)