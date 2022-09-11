"""
This module has a function to parse arguments passed to the cli.
"""

import argparse
import logging


def get_args():
    """
    This function parser received arguments into a Namespace object
    :return: Namespace containing parsed arguments
    """
    logging.info('Parsing all given arguments to the program.')

    parser = argparse.ArgumentParser()

    parser.add_argument('source', default=None, nargs='?', help='RSS feed URL')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show all program logs to the user.')
    parser.add_argument('-j', '--json', action='store_true', help='Print the result of the program in JSON format.')
    parser.add_argument('-d', '--date', help='Get cached news by this date.')
    parser.add_argument('-V', '--version', action='store_true',
                        help='Will output current version of the program and exit.')
    parser.add_argument('-l', '--limit', help='Specify the amount of articles shown.')
    parser.add_argument('--to-pdf', help='Convert the results to PDF and save to given path.')
    parser.add_argument('--to-html', help='Convert the results to HTML and save to given path.')

    return parser.parse_args()
