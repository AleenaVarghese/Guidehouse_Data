""" Logging helper functions
DO NOT name this file logging.py
"""
import logging
# AttributeError: module 'logging' has no attribute 'handlers'
# https://stackoverflow.com/questions/3781522
# This has to be imported
import logging.handlers

def setup_logger(name, log_file, format_string, level=logging.INFO):
    """ Setup and return a logger
    """
    # Setting up the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        # max size of each file
        # 2 MB
        # https://en.wikipedia.org/wiki/Kilobyte
        # SI is followed
        maxBytes=1000*1000*2,
        # max no of backup files created
        backupCount=10,
        delay=True
    )
    logger.addHandler(handler)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    return logger


def get_rotating_handler(logger):
    """ Get the rotating ifle handler for a logger
    Will be used to do rollover later.

    There can be multiple handlers for a logger. Here the assumption
    is that the there is only one rotating file handler.
    """
    rotating_handler = None
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            rotating_handler = handler
            break
    return rotating_handler
