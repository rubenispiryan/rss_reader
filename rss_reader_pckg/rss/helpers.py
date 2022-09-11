"""
This module contains functions which help the RSS classes to operate
"""

import logging
import re

from rss_reader_pckg.rss.rss_exception import RSSException


def is_number(s: str) -> bool:
    """
    This function checks whether a string is a number.
    :param s: String to be checked.
    :return Boolean result of the check.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def validate_method_args(func):
    """
    The validate_method_args function is a decorator that validates the types of arguments passed to a method.
    It is intended to be used as a decorator on methods whose arguments are annotated with type information.
    :param func: The original function
    :return: A wrapper function that calls the original and checks types of arguments.
    """

    def wrapper(self, *args):
        for arg, (arg_name, arg_type) in zip(args, func.__annotations__.items()):
            if not isinstance(arg, arg_type):
                raise TypeError(f'The argument: "{arg_name}", must be of type "{arg_type.__name__}",'
                                f' but received: "{type(arg).__name__}"')
        return func(self, *args)

    return wrapper


def validate_limit(limit: str) -> int:
    """
    The validate_limit function takes a string and checks if it is an integer. If the input is not an integer,
    it raises an exception. If the input is not positive, it also raises an exception.
    :param limit:str: Limit to be checked.
    :return: An integer representation of limit
    """
    if not is_number(limit):
        logging.error('RSS parser limit was non-number!')
        raise RSSException('Non-number limit was passed.', is_logged=True)
    if float(limit) % 1:
        logging.error('RSS parser limit passed was not an integer!')
        raise RSSException('Non-integer limit was passed.', is_logged=True)
    limit = int(limit)
    if limit <= 0:
        logging.error('RSS parser limit passed was not a positive integer!')
        raise RSSException('Non-positive limit was passed.', is_logged=True)
    logging.info(f'Getting all items from feed until limit of {limit} item(s) is reached')
    return limit


def validate_url(url: str):
    """
    This function checks if passed url matches a web page url format.
    :param url: The url to check.
    """
    if not re.match(r'(https?://[^\s"<]+)', url):
        logging.error('Invalid RSS URL was provided!')
        raise RSSException('Argument provided was not a valid web url.', is_logged=True)
