""" DB Manager

Runs raw SQL queries using the PyMYSQL DBAPI
Contains convenience methods like fetch_one, fetch_all, update_query, insert_query, delete_query

"""

import traceback
import json
import re
from flask import current_app
from pymysql.converters import escape_string
from pymysql.err import IntegrityError, ProgrammingError, InternalError
from pymysql.cursors import DictCursor
from pymysql import Error


class DBManager(object):
    """Contains functions for running SQL queries"""

    def __init__(self, db):
        self.db = db

    def esc(self, text):
        """Escapes strings for use in SQL queries.
        (named params are preferred)

        Args:
          text (str): The text to be escaped

        Returns:
          str: The escaped text
        """

        if isinstance(text, str):
            return escape_string(text)
        elif text is None:
            return ""
        else:
            return text

    def fetch_one(self, query, params=None, logquery=False):
        """Helper method for running a SQL query that returns a single result

        Args:
          query (str): The query to run, use pymysql-style name parameters, ex: %(value)s OR make sure the SQL is already safe
          params (dict): a dictionary of the named parameters to swap into the query
          logquery: (bool): If True, query will be written to the log

        Returns:
          dict: The query result with the colums as keys and field values as values.  Dict is empty if none.

        Example:
          { 'skuid': 'HB0001' }

        Raises:
          TypeError
          pymysql.err.ProgrammingError
          pymysql.err.IntegrityError
          pymysql.err.InternalError
          pymysql.Error: Generic PyMysql error
        """
        result = {}
        try:
            with self.db.connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(query, params)

                # Fetch all the records from SQL query output.
                # results are an array of dictionaries, fieldnames are the keys in each dict
                r = cursor.fetchone()

                if r:
                    result = r

                # log the post-compiled query if the config calls for it
                if logquery or current_app.config["MYSQL_LOG_QUERY"]:
                    self.log_query(query, params, cursor)

        except TypeError as e:
            current_app.logger.error(f"TypeError: {e}")
            self.log_query_error(query, params)
        except ProgrammingError as e:
            current_app.logger.error(f"MySQL ProgrammingError: {e}")
            self.log_query_error(query, params)
        except IntegrityError as e:
            current_app.logger.error(f"MySQL IntegrityError: {e}")
            self.log_query_error(query, params)
        except InternalError as e:
            current_app.logger.error(f"MySQL InternalError: {e}")
            self.log_query_error(query, params)
        except Error as e:
            current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
            current_app.logger.error("Stack trace:\n%s", traceback.format_exc())
            self.log_query_error(query, params)

        return result

    def fetch_all(self, query, params=None, logquery=False):
        """Helper method for running a SQL query that returns many results

        If SQL_CALC_FOUND_ROWS is used in the select query, an extra attribute is added
        to the results that will give is the total # of hits as if there were no LIMIT clause

        Args:
          query (str): The query to run, use pymysql-style name parameters, ex: %(value)s OR make sure the SQL is already safe
          params (dict): a dictionary of the named parameters to swap into the query
          logquery: (bool): If True, query will be written to the log

        Returns:
          dict: A dictionary containing the number of rows and a list of the results.
          dict['calc_rows'] will be 0 and the list will be empty if no matches

        Example:
          {
            'results': [
              {'skuid': HB0001'},
              {'skuid': HB0002'},
              {'skuid': HB0002'}
            ],
            'calc_rows': 3
          }

        Raises:
          TypeError
          ValueError
          pymysql.err.ProgrammingError
          pymysql.err.IntegrityError
          pymysql.err.InternalError
          pymysql.Error: Generic PyMysql error
        """
        data = {"results": [], "calc_rows": 0}
        try:
            with self.db.connection.cursor(cursor=DictCursor) as cursor:
                cursor.execute(query, params)

                # Fetch all the records from SQL query output.
                # results are an array of dictionaries, fieldnames are the keys in each dict
                r = cursor.fetchall()

                for row in r:
                    data["results"].append(row)

                if "SQL_CALC_FOUND_ROWS" in query:
                    cursor.execute("SELECT FOUND_ROWS() as FOUND_ROWS")
                    res = cursor.fetchone()
                    data["calc_rows"] = res["FOUND_ROWS"] if res and "FOUND_ROWS" in res else 0

                # log the post-compiled query if the config calls for it
                if logquery or current_app.config["MYSQL_LOG_QUERY"]:
                    self.log_query(query, params, cursor)

        except TypeError as e:
            current_app.logger.error(f"TypeError: {e}")
            self.log_query_error(query, params)
        except ValueError as e:
            current_app.logger.error(f"ValueError: {e}")
            self.log_query_error(query, params)
        except ProgrammingError as e:
            current_app.logger.error(f"MySQL ProgrammingError: {e}")
            self.log_query_error(query, params)
        except IntegrityError as e:
            current_app.logger.error(f"MySQL IntegrityError: {e}")
            self.log_query_error(query, params)
        except InternalError as e:
            current_app.logger.error(f"MySQL InternalError: {e}")
            self.log_query_error(query, params)
        except Error as e:
            current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
            current_app.logger.error("Stack trace:\n%s", traceback.format_exc())
            self.log_query_error(query, params)

        return data

    def update_query(self, query, params=None, logquery=False):
        """Helper method for running an UPDATE query

        Args:
          query (str): The query to run, use pymysql-style name parameters, ex: %(value)s OR make sure the SQL is already safe
          params (dict): a dictionary of the named parameters to swap into the query
          logquery: (bool): If True, query will be written to the log

        Returns:
          int: The number of rows affected.  A 0 value indicates failure.

        Raises:
          TypeError
          ValueError
          pymysql.err.ProgrammingError
          pymysql.err.IntegrityError
          pymysql.err.InternalError
          pymysql.Error: Generic PyMysql error
        """
        rows = 0
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.rowcount

                # log the post-compiled query if the config calls for it
                if logquery or current_app.config["MYSQL_LOG_QUERY"]:
                    self.log_query(query, params, cursor)

        except TypeError as e:
            current_app.logger.error(f"TypeError: {e}")
            self.log_query_error(query, params)
        except ValueError as e:
            current_app.logger.error(f"ValueError: {e}")
            self.log_query_error(query, params)
        except ProgrammingError as e:
            current_app.logger.error(f"MySQL ProgrammingError: {e}")
            self.log_query_error(query, params)
        except IntegrityError as e:
            current_app.logger.error(f"MySQL IntegrityError: {e}")
            self.log_query_error(query, params)
        except InternalError as e:
            current_app.logger.error(f"MySQL InternalError: {e}")
            self.log_query_error(query, params)
        except Error as e:
            current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
            current_app.logger.error(f"query: {query}")
            current_app.logger.error("Stack trace:\n%s", traceback.format_exc())
            self.log_query_error(query, params)

        return rows

    def insert_query(self, query, params=None, logquery=False):
        """Helper method for running an INSERT query

        Args:
          query (str): The query to run, use pymysql-style name parameters, ex: %(value)s OR make sure the SQL is already safe
          params (dict): a dictionary of the named parameters to swap into the query
          logquery: (bool): If True, query will be written to the log

        Returns:
          int: The id of the inserted row.  A 0 value indicates failure.

        Raises:
          TypeError
          ValueError
          pymysql.err.ProgrammingError
          pymysql.err.IntegrityError
          pymysql.err.InternalError
          pymysql.Error: Generic PyMysql error
        """
        id = 0
        try:
            with self.db.connection.cursor() as cursor:
                cursor.execute(query, params)
                id = cursor.lastrowid

                # log the post-compiled query if the config calls for it
                if logquery or current_app.config["MYSQL_LOG_QUERY"]:
                    self.log_query(query, params, cursor)

        except TypeError as e:
            current_app.logger.error(f"TypeError: {e}")
            self.log_query_error(query, params)
        except ValueError as e:
            current_app.logger.error(f"ValueError: {e}")
            self.log_query_error(query, params)
        except ProgrammingError as e:
            current_app.logger.error(f"MySQL ProgrammingError: {e}")
            self.log_query_error(query, params)
        except IntegrityError as e:
            current_app.logger.error(f"MySQL IntegrityError: {e}")
            self.log_query_error(query, params)
        except InternalError as e:
            current_app.logger.error(f"MySQL InternalError: {e}")
            self.log_query_error(query, params)
        except Error as e:
            current_app.logger.error(f"PyMySQL Non-Specific Error: {e}")
            current_app.logger.error("Stack trace:\n%s", traceback.format_exc())
            self.log_query_error(query, params)

        return id

    def delete_query(self, query, params=None):
        """Delete and Update are the same at this level, this is just an alias"""
        return self.update_query(query, params)

    def log_query_error(self, query, params=None):
        """PyMySQL doesn't appear to have a method for printing a complete,
        parameterized query *IF* the SQL fails.  This function assembles a query by merging in the named
        parameters.  May not produce actual usable SQL.  It's just to show a rough idea of the SQL for debug pruposes

        Args:
          query (str): The query that was executed
          params (dict or list): A dictionary or list of the named parameters

        """
        if not query or not isinstance(query, str):
            return query
        current_app.logger.error("RAW QUERY: " + str(query))
        if params:
            current_app.logger.error("QUERY PARAMS:")
            current_app.logger.error(params)
            debug_q = query
            if isinstance(params, dict):
                for k, v in params.items():
                    repl_key = "%(" + k + ")s"
                    debug_q = debug_q.replace(repl_key, "'" + str(v) + "'")
                current_app.logger.error("APPROX COMPILED SQL: " + debug_q)
            if isinstance(params, list):
                debug_q = query % tuple(params)
                current_app.logger.error("APPROX COMPILED SQL: " + debug_q)

    def log_query(self, query, params=None, cursor=None):
        """Logs the query if loglevel is info (usually called only if config MYSQL_LOG_QUERY = True)"""
        if not query or not cursor:
            return None
        current_app.logger.info("QUERY LOG: " + str(cursor.mogrify(query, params)))
