"""
This module contains classes to represent the caching of the RSS Feeds.
"""

import logging
import os
import pickle
import shutil
import sys
from dataclasses import dataclass

import requests
from dateutil import parser

from rss_reader_pckg.rss.helpers import validate_method_args

from rss_reader_pckg.rss.rss_classes import Feed, Item


@dataclass
class RSSCache:
    """
    A class to represent the RSS feed for caching and its methods.
    """
    rss_feeds: list[Feed]

    def append(self, new_feed: Feed):
        """
        This method appends a new parsed feed to an existing RSSCache object.
        :param new_feed: A new parsed Feed object
        """
        is_existing_title = False
        for feed in self.rss_feeds:
            if new_feed.title == feed.title:
                unique_items = self._get_titles_set(feed.items)
                diff_titles = self._get_titles_set(new_feed.items).difference(unique_items)
                feed.items += [current_item for current_item in new_feed.items
                               if current_item.title in diff_titles]
                is_existing_title = True
        if not is_existing_title:
            self.rss_feeds.append(new_feed)

    @staticmethod
    def _get_titles_set(items: list[Item]) -> set[str]:
        """
        This method returns a set object containing the titles of rss items.
        :param items: RSS Items list
        :return: The set of titles.
        """
        return set(map(lambda item: item.title.value, items))


class CacheReader:
    """
    This class represents the methods for caching rss data and retrieving already cached data.
    """

    def __init__(self, cache_path: str = 'rss_cache.bin'):
        self.image_paths = None
        self._cache_path = f'cache/{cache_path}'

        if not os.path.exists('cache'):
            os.mkdir('cache')

    @property
    def cache(self) -> RSSCache:
        """
        This cache property retrieves the RSS feed data from a pickle file.
        :return: An instance of the RSSCache class.
        """
        logging.info('Reading cached results.')
        if os.path.exists(self._cache_path):
            with open(self._cache_path, 'rb') as c:
                logging.info('Loading cached data.')
                return pickle.load(c)
        else:
            raise FileNotFoundError

    @cache.setter
    def cache(self, obj: RSSCache):
        """
        This cache setter is used to store the RSS feed data in a pickle file.
        :param obj:RSSCache: RSSCache object to be stored in the cache file.
        """
        with open(self._cache_path, 'wb') as c:
            sys.setrecursionlimit(10000)
            pickle.dump(obj, c)
            logging.info('Finished caching data.')

    @validate_method_args
    def cache_results(self, current_items: Feed):
        """
        This method will serialize passed results into a BIN file along with the existing cache.
        :param current_items: Current feed items to add to cache.
        """
        for item in current_items.items:
            self.download_images(item)
        existing_cache = None
        if os.path.exists(self._cache_path) and os.path.getsize(self._cache_path):
            existing_cache = self.cache
            existing_cache.append(current_items)
        else:
            current_items = RSSCache([current_items])
        self.cache = existing_cache if existing_cache else current_items
        logging.info(f'Parsing results were successfully cached to: {self._cache_path}')

    def download_images(self, item: Item):
        """
        This method downloads all available images into the cache folder.
        :param item: An RSS Item object.
        """
        self.image_paths = [image_path.value.split('/')[-1] for image_path in item.image_links.elements]
        for image_path, image_link in zip(self.image_paths, item.image_links.elements):
            res = requests.get(image_link.value, stream=True)
            if res.status_code == 200:
                with open(f'cache/{image_path}', 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
        logging.info('Downloaded all images to the cache.')

    def fetch_by_filters(self, date: str, url: str) -> list[Item]:
        """
        This method fetches news from cache by date and url.
        :param date: A date string.
        :param url: An RSS url.
        :return: A list of Item objects.
        """
        feed_list = []
        for feed in self.cache.rss_feeds:
            if url and url != feed.url:
                continue
            for item in feed.items:
                item_date = parser.parse(item.date.value).strftime('%Y%m%d')
                if item_date == date:
                    feed_list.append(item)
        return feed_list
