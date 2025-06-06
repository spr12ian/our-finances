import logging
import os
import time
from functools import wraps
from typing import Any

from finances.classes.date_time_helper import DateTimeHelper

# https://docs.python.org/3/library/logging.html?form=MG0AV3

DEBUG_FILE = "debug.log"
logging.basicConfig(filename=DEBUG_FILE, level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# Use this snippet:
# fromhelper_log import LogHelper
# l = LogHelper(__name__)
# l.clear_debug_log()

# To time functions wrap them like this:
# @LogHelper.debug_function_call


class LogHelper:
    # Define a dictionary to map logging levels to their string representations
    LOG_LEVELS = {
        logging.CRITICAL: "CRITICAL",  # 50
        logging.ERROR: "ERROR",  # 40
        logging.WARNING: "WARNING",  # 30
        logging.INFO: "INFO",  # 20
        logging.DEBUG: "DEBUG",  # 10
        logging.NOTSET: "NOTSET",  # 0
    }

    def __init__(self, name) -> None:
        # print(f"LogHelper name: {name}")
        name = os.path.basename(name)
        # print(f"LogHelper basename: {basename}")
        if name == "SQLAlchemyHelper":
            self.logger = logging.getLogger("sqlalchemy.engine")
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logging.getLogger(name)
        self.saved_level = self.get_level()

        self.dt = DateTimeHelper()

    def clear_debug_log(self):
        with open(DEBUG_FILE, "w") as file:
            pass

    def critical(self, msg):
        self.logger.critical(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def disable(self):
        self.saved_level = self.get_level()
        self.logger.setLevel(logging.CRITICAL)

    def enable(self):
        self.logger.setLevel(self.saved_level)

    def error(self, msg):
        self.logger.error(msg)

    def exception(self, msg):
        self.logger.exception(msg)

    def get_date_today(self):
        dt = self.dt
        return dt.get_date_today()

    def get_level(self):
        return self.logger.getEffectiveLevel()

    # Function to get the effective logging level as a string
    def get_level_as_string(self):
        level = self.get_level()
        level_name = LogHelper.LOG_LEVELS.get(level, "UNKNOWN")
        return level_name

    def info(self, msg):
        self.logger.info(msg)

    def is_debug_enabled(self):
        return self.get_level() == logging.DEBUG

    def log_date_today(self):
        self.info(f"{self.get_date_today()}")

    def log_debug_level(self):
        self.info(f"{self.get_level_as_string()}: {self.get_level()}")

    def log_time(self):
        dt = self.dt

        time_now = dt.get_time_now()

        self.info("Current Time:", time_now)

    def print(self, msg):
        self.info(msg)
        print(msg)

    def set_level(self, level: Any) -> None:
        if isinstance(level, int):
            self.set_level_int(level)
        elif isinstance(level, str):
            self.set_level_string(level)
        else:
            raise ValueError(f"Unexpected level type: {type(level)} for level: {level}")

    def set_level_debug(self):
        self.logger.setLevel(logging.DEBUG)

    def set_level_int(self, level):
        if level not in LogHelper.LOG_LEVELS:
            raise ValueError(
                f"Invalid log level: {level}. Expected one of {list(LogHelper.LOG_LEVELS.keys())}."
            )

        if level == logging.NOTSET:
            raise ValueError(
                f"Cannot set the log level to {logging.NOTSET}. Choose a valid log level."
            )

        with open("debug.log", "a") as file:
            print(f"Calling logger.setLevel({level})", file=file)

        # Set the logger level
        self.logger.setLevel(level)
        # Optional feedback for debugging/logging purposes
        self.logger.debug(f"Log level set to {level}.")
        self.logger.info(f"Log level set to {level}.")

        self.log_debug_level()

    def set_level_string(self, level):
        if level not in LogHelper.LOG_LEVELS.values():
            raise ValueError(
                f"Invalid log level: {level}. Expected one of {list(LogHelper.LOG_LEVELS.values())}."
            )

        if level == "NOTSET":
            raise ValueError(
                "Cannot set the log level to NOTSET. Choose a valid log level."
            )

        # Set the logger level
        self.logger.setLevel(level)
        # Optional feedback for debugging/logging purposes
        self.logger.debug(f"Log level set to {level}.")

        self.log_debug_level()

    def tdebug(self, msg):
        dt = self.dt

        time_now = dt.get_time_now()

        message = f"{time_now}: {msg}"
        self.debug(message)

    def tlog(self, msg):
        dt = self.dt

        time_now = dt.get_time_now()

        message = f"{time_now}: {msg}"
        self.info(message)

    def warning(self, msg):
        self.logger.warning(msg)


def debug_function_call(func):
    l = logging.getLogger(func.__name__)
    # l.setLevel(logging.DEBUG)
    l.debug(__file__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args):
            l.debug(f"args: {args}")

        if len(kwargs):
            l.debug(f"kwargs: {kwargs}")

        start_time = time.time()
        l.debug(f"Started at {time.ctime(start_time)}")

        result = func(*args, **kwargs)

        end_time = time.time()

        l.debug(f"Finished at {time.ctime(end_time)}")

        l.debug(f"Returned: {result}")

        execution_time = end_time - start_time
        l.debug(f"Executed in {execution_time:.2f} seconds")

        return result

    return wrapper
