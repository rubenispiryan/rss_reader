"""
This module contains RSS related Exception objects
"""


class RSSException(Exception):
    """
    A general RSS exception class,
    """
    def __init__(self, message, is_logged):
        super().__init__(message)
        self.is_logged = is_logged
