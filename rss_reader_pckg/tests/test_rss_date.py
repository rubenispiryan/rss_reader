import logging
import unittest

from rss_reader_pckg.rss.rss_exception import RSSException
from rss_reader_pckg.rss.rss_parser import RSSParser


class TestRSSDateParser(unittest.TestCase):
    def setUp(self):
        self.rss_parser = RSSParser()
        logging.disable(logging.ERROR)

    def test_invalid_date(self):
        with self.assertRaises(RSSException) as e:
            self.rss_parser.parse_items_by_date('1baddat3', None, None)
        self.assertEqual(e.exception.args[0], 'Date was not matching following format "yymmdd".')
        with self.assertRaises(RSSException) as e:
            self.rss_parser.parse_items_by_date('20220100', None, None)
        self.assertEqual(e.exception.args[0], 'Date was not matching following format "yymmdd".')

    def test_wrong_date_length(self):
        with self.assertRaises(RSSException) as e:
            self.rss_parser.parse_items_by_date('202206', None, None)
        self.assertEqual(e.exception.args[0], 'Date provided was not 8 characters')


if __name__ == '__main__':
    unittest.main()
