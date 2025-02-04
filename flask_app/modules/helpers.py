""" Helpers

Helpers module
"""

import os
import json
from datetime import datetime
from obscure import Obscure
from urllib.parse import unquote
import uuid
from flask import request, current_app, g
from flask_app.modules.extensions import DB, cache
from boltons.iterutils import remap
import babel.numbers
import re
import math
import random
import string
import hashlib
from unidecode import unidecode
from html import unescape


def get_first_n_words(text, n):
    words = text.split()  # Split the text into a list of words
    return " ".join(words[:n])  # Return the first 'n' words, or fewer if not available


def md5_encode(message):
    """Simply return a md5-encoded version of given string

    Args:
      message (str): the string to encrypt

    Returns:
      str: MD5-encrypted version of message
    """

    if not message or not isinstance(message, str):
        return message

    return hashlib.md5(message.lower().encode("utf-8")).hexdigest()


def get_random_string(length=10):
    """Create a random string using letters and numbers

    Args:
      length (num): The length of the string to return

    Returns:
      str: The random string
    """
    chars = string.ascii_letters + string.digits
    return "".join((random.choice(chars)) for x in range(length))


def encode_id(id):
    """Encode a given ID with 2-way encryption package 'obscure'

    Args:
      id (str): The id you want obscured

    Returns:
      str: The obscured id
    """
    if not id:
        return None
    obscure = Obscure(current_app.config["OBSCURE_SALT"])

    return obscure.encode_hex(id)


def decode_id(encoded_id):
    """Decode a given ID with 2-way encryption package 'obscure'

    Args:
      encoded_id (str): The id to un-obscure

    Returns:
      str: The decoded (un-obscured) id
    """
    if not id:
        return None
    obscure = Obscure(current_app.config["OBSCURE_SALT"])

    return obscure.decode_hex(encoded_id)


def double_encode(mystring):
    """Replace % character in given string with %25

    Args:
      mystring (str): The string to double encode

    Returns:
      str: the double-encoded string
    """
    if not isinstance(mystring, str):
        return mystring

    mystring = mystring.replace("%", "%25")

    return mystring


def replace_double_quote(mystring):
    """replace any instances of double quotes with the html entity

    Args:
      mystring (str): The string to replace quotes in

    Returns:
      str: the new string with the html entity for quotes
    """
    if not isinstance(mystring, str):
        return mystring
    return mystring.replace('"', "&quot;")


def sanitize(mystring):
    """unencode, escape unsafe chars to avoid SQL, XSS

    Args:
      mystring (str): The string to sanitize

    Returns:
      str: the sanitized string
    """

    if isinstance(mystring, str):
        mystring = unquote(mystring)
        mystring = mystring.strip()
        mystring = re.sub(r"\s+", " ", mystring)
        mystring = mystring.replace("<", "&lt;")
        mystring = mystring.replace(">", "&gt;")
        mystring = mystring.replace("'", "&apos;")
        mystring = mystring.replace('"', "&quot;")
        mystring = mystring.replace("&", "&amp;")

        # handles the inevitable instances of chars encoded multiple times
        mystring = re.sub(
            re.compile("&amp;(amp;)+quot;", re.IGNORECASE), "&quot;", mystring
        )
        mystring = re.sub(re.compile("&amp;quot;", re.IGNORECASE), "&quot;", mystring)
        mystring = re.sub(
            re.compile("&amp;(amp;)+apos;", re.IGNORECASE), "&apos;", mystring
        )
        mystring = re.sub(re.compile("&amp;apos;", re.IGNORECASE), "&apos;", mystring)
        mystring = re.sub(re.compile("&amp;(amp;)+", re.IGNORECASE), "&amp;", mystring)
        mystring = re.sub(re.compile("&amp;amp;", re.IGNORECASE), "&amp;", mystring)
        mystring = re.sub(
            re.compile("&amp;(amp;)+gt;", re.IGNORECASE), "&gt;", mystring
        )
        mystring = re.sub(re.compile("&amp;gt;", re.IGNORECASE), "&gt;", mystring)
        mystring = re.sub(
            re.compile("&amp;(amp;)+lt;", re.IGNORECASE), "&lt;", mystring
        )
        mystring = re.sub(re.compile("&amp;lt;", re.IGNORECASE), "&lt;", mystring)

    return mystring


def create_uuid():
    """create a UUID

    Returns:
      str: The UUID
    """
    return str(uuid.uuid4())


def match_uuid(string):
    """checks if string matches a UUID pattern

    Args:
      string (str): UUID as string

    Returns:
      bool: True or False
    """

    uuid_pattern = re.compile(
        "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    )
    if uuid_pattern.match(string):
        return True
    else:
        return False


def validate_email(email):
    """E-Mail validation function

    Args:
      email (str): The e-mail address

    Returns:
      bool: True for successful match, False otherwise.
    """

    if not email or not isinstance(email, str):
        return False
    email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    if email_pattern.match(email):
        return True
    else:
        return False


def format_currency(number):
    """Formats currency, includes $ sign

    Args:
      number: The number to format

    Returns:
      str: The formatted currency, prefixed by a $
    """
    if not is_number(number):
        return number

    return babel.numbers.format_currency(number, "USD", locale="en_US")


def quote_list(lst=None):
    """Takes a list and transforms to a SQL-safe string of quoted values

    Args:
      lst (list): THe list to be joined and quoted

    Returns:
      string: A string of quoted values suitable for use in a SQL IN() clause (for example)
    """

    if not lst or not isinstance(lst, list):
        return None

    return ",".join(map(lambda x: "'%s'" % DB.esc(x), lst))


def split_to_list(value):
    """Takes a semicolon delimited string and splits to list

    Args:
      value (str): the value to be split

    Returns:
      list: a list of strings
    """
    string_list = []
    if isinstance(value, str):
        string_list = value.split(";")
        string_list = list(filter(None, string_list))  # remove empty list items
        string_list = [x.strip() for x in string_list]  # trim whitespace in list items
        string_list = list(filter(None, string_list))
        return string_list
    else:
        return value


def split_and_quote(value):
    """Wrapper around split_to_list and quote_list.  Takes a semicolon-demin list and converts to an SQL-safe quoted list.

    Args:
      value (str): THe string to be split to a list, then joined and quoted

    Returns:
      string: A string of quoted values suitable for use in a SQL IN() clause (for example) OR an empty quoted string
    """
    if not value:
        return "''"
    return quote_list(split_to_list(value))


def is_number(s):
    """Determines if given value is a number or not

    Args:
      s (any): The value to evaluate

    Returns:
      bool: True - is a number, False, is not a number
    """
    try:
        if isinstance(s, bool):  # bools are coerced to floats, have to be excepted
            return False
    except Exception as e:
        return False

    try:
        float(s)
        return True
    except Exception as e:
        return False


def is_float(s):
    """checks if given string can be coerced to a float

    Args:
      s (str): The string to evaluate as a float

    Returns:
      bool: True if it can be coerced to a float, false if not
    """
    if not s or not isinstance(s, str):
        return False

    if re.match(r"^-?\d+(?:\.\d+)$", s) is None:
        return False

    return True


def is_int(s):
    """checks if given string can be coerced to an int

    Args:
      s (str): The string to evaluate as an int

    Returns:
      bool: True if it can be coerced as an int, false if not
    """
    if not s or not isinstance(s, str) or s.startswith("0"):
        return False

    try:
        int(s)
    except ValueError:
        return False

    # False if > MAX_SAFE_INTEGER
    if int(s) > 9007199254740991:
        return False

    return True


def strip_non_numeric(s):
    """Strip all non-numeric characters from a given string

    Args:
      s (str): The string to strip

    Returns:
      str: The string with all non-numeric characters removed
    """
    if not s or not isinstance(s, str):
        return s

    return re.sub(r"[^0-9\.]", "", s)


def dedupe(lst):
    """Removes duplicates in a given list

    Args:
      lst (list): The list to dedupe

    Returns:
      list: The deduped ist
    """
    if not lst or not isinstance(lst, list):
        return lst
    output = []
    seen = set()
    for value in lst:
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def strip_html(string):
    """Merely strip the html from given string

    Args:
      string (str): The string to strip the html from

    Returns:
      str: The string, with html tag stripped out
    """
    if not string or not isinstance(string, str):
        return string

    return re.sub("<[^<]+?>", "", string)


def unescape_html(string):
    """Unescape any escaped html (or entities in given string)

    Args:
      string (str): The string to unescape html

    Returns:
      str: The string, with html unescaped
    """
    if not string or not isinstance(string, str):
        return string
    return unescape(string)


def convert_unicode(string):
    """Convert any unicode characters to nearest ASCII equivalent

    Args:
      string (str): The string to examine for unicode

    Returns:
      str: The string, with any unicode chars converted
    """
    if not string or not isinstance(string, str):
        return string
    string = unidecode(string)
    return string


def convert_to_ascii(string):
    """Convert given string to ascii characters

    Args:
      string (str): The string to convert to ascii

    Returns:
      str: The string, converted to ascii
    """
    if not string or not isinstance(string, str):
        return ""

    string = strip_html(unescape_html(convert_unicode(string)))
    if string:
        string = re.sub(r"\s+", " ", string)
    return string or ""


def dump_json_as_ascii(d):
    """Convert given dict to json string, converting all chars to ascii
    The reason I'm using this in Jinja templates over the built-in 'tojson'
    FOR ld_json data ONLY
    is because the built-in seems to convert apostrophes to unicode

    Args:
      d (dict): The dict to convert to json

    Returns:
      str: The json string, converted to ascii
    """
    if not d:
        return json.dumps({})

    return json.dumps(d, ensure_ascii=True)


def camelize(string):
    """Convert given string to Camel-case

    Args:
      string (str): The string to convert to camel-case

    Returns:
      str: The camel-cased string
    """
    camelized = string
    if isinstance(string, str):
        components = string.split("_")
        camelized = components[0] + "".join(x.title() for x in components[1:])
    return camelized


def decamelize(string):
    """Convert camel-case to snake-case

    Args:
      string (str): The camel-cased string to convert to snake-case

    Returns:
      str: The snake-cased string
    """
    decamelized = string
    if isinstance(decamelized, str):
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", decamelized)
        decamelized = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return decamelized


def serialize(obj=None):
    """Prepare data for consumption by Javascript

    uses boltons.iterutils to recurse into nested data structures.
    add nocasechange=1 to leave keys as snake-case

    Args:
      obj (any): String, list or dict

    Returns:
      object: The inputted object with all keys and values transformed (if necessary)
    """

    if request.args.get("nocasechange"):
        return obj
    if obj is None:
        obj = {}

    newobj = {}
    try:
        newobj = remap(obj, visit=convert_keys)
    except Exception as e:
        current_app.logger.error(f"ERROR problem in serialize {e}")

    return newobj


def convert_keys(path, key, value):
    """Helper function for serialize().  Do not use independently.

    Tells iterutils what to do with each passed key and value

    Args:
      path (str): do not explicitly specify
      key (str): do not explicitly specify
      value (any): do not explicitly specify

    Returns:
      object: for itertools only
    """

    return camelize(key), value


@cache.memoize()
def image_size(path):
    """Wraps pymage_size to performantly get the dimensions of the image
    passed in the path argument

    Args:
      path (str): The full path to the image FROM /public_html (i.e. do not include /public_html), including filename and extension

    Returns:
      tuple: A tuple with width in the first pos, height in the second
    """

    if not path:
        return "", ""
    path = current_app.config["PUBLIC_HTML"] + path
    image_object = None

    try:
        image_object = get_image_size(path)
    except FileNotFoundError as fnf:
        pass
        # current_app.logger.warning("image_size() file not found, " + path)
    except Exception as e:
        pass
        # current_app.logger.error("image_size() error, " + path + " " + str(e))

    if not image_object:
        return "", ""

    return image_object.get_dimensions()


def days_seconds(days):
    """Convert the given number of days into seconds

    Args:
      days: The days to convert to seconds

    Returns:
      int: Days converted to seconds
    """
    if not is_number(days):
        return 0

    return 60 * 60 * 24 * days


def reformat_datestring(datestr):
    """Convert the shorthand date  format like 9/13 (MM/DD) to a full date string

    Assumes year is current year UNLESS given month is less than the current month, and if so 1 year is added

    Args:
      datestr (str): A shorthand date in the format MM/DD, M/DD or M/D

    Returns:
      str: A date in the format YYYYMMDD.  If datestr format is not matched, datestr is returned unformatted
    """
    if not isinstance(datestr, str):
        return datestr

    res = re.search(r"^([0-9]{1,2})/([0-9]{1,2})$", datestr)
    if not res or not len(res.groups()) == 2:
        return datestr

    month = int(res.group(1))
    day = int(res.group(2))
    year = int(datetime.now().strftime("%Y"))
    curmonth = int(datetime.now().strftime("%m"))

    if month < curmonth:
        year = year + 1

    return str(year) + str(month).zfill(2) + str(day).zfill(2)


def days_between(d1, d2):
    """Calculate the number of days between two given date strings

    Args:
      d1 (str): The first date, format YYYYMMDD
      d2 (str): The second date, format YYYYMMDD

    Returns:
      int: The days between the two dates
    """
    if not re.match(r"[0-9]{8}", d1) or not re.match(r"[0-9]{8}", d2):
        return 0

    try:
        d1 = datetime.strptime(d1, "%Y%m%d")
        d2 = datetime.strptime(d2, "%Y%m%d")
    except ValueError:
        return 0
    return abs((d2 - d1).days)


def do_cache_clear():
    """clears the cached/memoized objects in redis db"""
    cache.clear()

    resp = {"success": True}
    return resp


def write_pid_file(pid_file, pid):
    """write the current process id to a file

    Args:
      pid_file (str): The full path to the file to write the pid to
      pid (int): The process id to write to the file
    """
    if not pid_file or not pid:
        return ""
    with open(pid_file, "w") as f:
        f.write(str(pid))
    return f"PID {pid} written to {pid_file}"


def remove_pid_file(pid_file):
    """remove the pid file if it exists

    Args:
      pid_file (str): The full path to the pid file to remove
    """
    if os.path.exists(pid_file):
        os.remove(pid_file)
        print(f"Removed PID file: {pid_file}")


def convert_unix_to_date(unix_timestamp):
    """Convert a Unix timestamp to a formatted date string

    Args:
      unix_timestamp (int): The Unix timestamp to convert

    Returns:
      str: The formatted date string
    """

    if not isinstance(unix_timestamp, (int, float)):
        raise ValueError("Unix timestamp must be a number.")

    try:
        dt = datetime.utcfromtimestamp(unix_timestamp)
    except Exception as e:
        raise ValueError(f"Invalid Unix timestamp: {e}")

    formatted_date = dt.strftime("%b %d, %Y")
    return formatted_date
