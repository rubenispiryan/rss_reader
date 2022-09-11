import os
import unittest
import logging

from bs4 import BeautifulSoup

from rss_reader_pckg.rss.rss_exception import RSSException
from rss_reader_pckg.rss.rss_parser import RSSParser

logging.disable(logging.ERROR)


class TestRSSParser(unittest.TestCase):
    def setUp(self):
        self.rss_parser = RSSParser()
        with open(f'{os.path.dirname(os.path.abspath(__file__))}/test_rss.xml', 'r', encoding="utf8") as f:
            self.rss_parser.soup = BeautifulSoup(f.read(), features='xml')
        logging.disable(logging.ERROR)

    def test_correct_no_limit(self):
        results = self.rss_parser.items()
        self.assertEqual(len(results), 5)

    def test_correct_with_limit(self):
        results = self.rss_parser.items(2)
        self.assertEqual(len(results), 2)

    def test_limit_wrong_number_type(self):
        with self.assertRaises(RSSException) as e:
            self.rss_parser.items(-1)

        with self.assertRaises(RSSException) as e:
            self.rss_parser.items(0)
        self.assertEqual(e.exception.args[0], 'Non-positive limit was passed.')
        with self.assertRaises(RSSException) as e:
            self.rss_parser.items(1.1)
        self.assertEqual(e.exception.args[0], 'Non-integer limit was passed.')

    def test_limit_non_number(self):
        with self.assertRaises(RSSException) as e:
            self.rss_parser.items('hello')
        self.assertEqual(e.exception.args[0], 'Non-number limit was passed.')

    def test_item_title(self):
        item = self.rss_parser.items(1)
        self.assertEqual(self.rss_parser._parse_title(item[0]).value,
                         'Ночью под Борисовом лось вышел на дорогу, погиб водитель')


if __name__ == '__main__':
    unittest.main()
