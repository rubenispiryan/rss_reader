"""
This module contains the RSSParser class which performs all main actions and parsing of the RSS.
"""

import logging
import os
import re
from typing import Optional

from bs4 import BeautifulSoup
from bs4.element import PageElement, ResultSet
import requests
from dateutil import parser
from dateutil.parser import ParserError

from .helpers import validate_method_args, validate_limit, validate_url
from .html_converter import html_feed
from .pdf_converter import pdf_feed
from .rss_cache import CacheReader
from .rss_classes import Item, Element, ElementType, ElementCollection, Feed
from .rss_exception import RSSException


class RSSParser:
    """
    This is a class which combines data and methods regarding the parsing of an RSS.
    """

    def __init__(self):
        self.is_offline = None
        self.url = None
        self.parsed_items: Optional[list[Item]] = None
        self.soup = None
        self._title = None
        self.rss_cache = CacheReader()
        logging.info('RSS parser is created')

    def request_soup(self, url: str) -> None:
        """
        This method requests `url` and creates a BeautifulSoup object with its content.
        :return: A bs4 soup object to parse xml.
        """
        if not url:
            logging.error('RSS URL must be provided!')
            raise RSSException('Argument url must be of type str.', is_logged=True)
        validate_url(url)
        self.url = url
        req = requests.get(url)
        logging.info('RSS is requested from given URL')
        self.soup = BeautifulSoup(req.content, features='xml')

    @property
    def feed_title(self) -> str:
        """
        :return: RSS Title
        """
        return self._title if self._title else self.soup.title.string

    @feed_title.setter
    def feed_title(self, value):
        self._title = value

    def items(self, limit: Optional[str] = None) -> ResultSet:
        """
        This method retrieves all items from an RSS.
        :return: An object containing all raw items.
        """
        if limit is None:
            logging.info('Getting all items from feed')
            return self.soup.findAll('item', limit=limit)
        limit = validate_limit(limit)

        return self.soup.findAll('item', limit=limit)

    def parse_items_by_date(self, date: str, url: Optional[str], limit: Optional[str]) -> None:
        """
        This method checks the cache for all feeds that match the given date and URL,
        if no URL is provided it will check all feeds. It will add matching items until the limit is reaching,
        if no limit is provided it will retrieve all items.
        :param date:str: Date in the format of yymmdd.
        :param url:Optional[str]: The url of the rss feed to be matched.
        :param limit:Optional[str]: Limit the number of items to be retrieved.
        """
        if len(date) != 8:
            logging.error('The length of parameter --date should be 8 characters long!')
            raise RSSException('Date provided was not 8 characters', is_logged=True)
        try:
            vis_date = parser.parse(date).strftime('%d/%m/%Y')
        except ParserError:
            logging.error('Faulty date was provided!')
            raise RSSException('Date was not matching following format "yymmdd".', is_logged=True)

        try:
            feed_list = self.rss_cache.fetch_by_filters(date, url)
        except FileNotFoundError:
            logging.error('There is no cache available!')
            raise RSSException('Cache was not yet created.', is_logged=True)

        feed_str = ''
        if url:
            validate_url(url)
            feed_str += f', and {url} URL'
        if limit:
            limit = validate_limit(limit)
            feed_str += f', and  limit of {limit}'
        else:
            limit = len(feed_list)
        if not feed_list:
            logging.error('No news were found for given filters!')
            raise RSSException('Found no news with given filters.', is_logged=True)
        self.feed_title = f'News fetched from cache by - {vis_date} Date{feed_str}.'
        self.parsed_items = feed_list[:limit]
        logging.info(f'Parsed items from cache with following filters Date: {vis_date}{feed_str}')
        self.is_offline = True

    @validate_method_args
    def _parse_item(self, item: PageElement) -> Item:
        """
        This method parses a PageElement with its title, date, link, media and description into an Item object.
        :param item: A PageElement to be parsed into an Item.
        :return: A parsed Item.
        """
        title = self._parse_title(item)
        date = self._parse_date(item)
        link = self._parse_link(item)
        images = self._parse_images(item)
        media = self._parse_media(item, images)
        description = self._parse_description(item)
        parsed_item = Item(title=title, date=date, link=link, description=description, media_links=media,
                           image_links=images)
        logging.info(f'Finished parsing item with title: {parsed_item.title}')

        return parsed_item

    @validate_method_args
    def parse_items(self, items: ResultSet) -> None:
        """
        This method parses all given items and assigns them to a class attribute.
        :param items: A ResultSet object with raw items from a rss.
        """
        self.parsed_items = [self._parse_item(item) for item in items]
        self.rss_cache.cache_results(self.feed)

    @staticmethod
    @validate_method_args
    def _parse_title(item: PageElement) -> Element:
        """
        This method parses the title of a page element and returns it as an Element object.
        :param item: An item from which to get the title.
        :return: An Element object with the value of the title.
        """
        title_elem = Element(ElementType.TITLE)
        title_elem.value = item.title.string.strip()
        logging.info(f'Got item\'s title: {title_elem.value}')
        if not title_elem.value:
            logging.info('Title was not found')
        return title_elem

    @staticmethod
    @validate_method_args
    def _parse_date(item: PageElement) -> Element:
        """
        This method parses the date of a page element and returns it as an Element object.
        :param item: An item from which to get the date.
        :return: An Element object with the value of the date.
        """
        date_elem = Element(ElementType.PUB_DATE)
        date_elem.value = item.pubDate.string
        date_elem.value = parser.parse(date_elem.value).strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f'Got item\'s publish date: {date_elem.value}')
        if not date_elem.value:
            logging.info('Publish date was not found')
        return date_elem

    @staticmethod
    @validate_method_args
    def _parse_link(item: PageElement) -> Element:
        """
        This method parses the link of a page element and returns it as an Element object.
        :param item: An item from which to get the link.
        :return: An Element object with the value of the link.
        """
        link_elem = Element(ElementType.LINK)
        link_elem.value = item.link.string
        logging.info(f'Got item\'s link: {link_elem.value}')
        if not link_elem.value:
            logging.info('Link was not found')
        return link_elem

    @staticmethod
    def _parse_media(item: PageElement, images: ElementCollection) -> ElementCollection:
        """
        This method takes a PageElement object and returns an ElementCollection of media URLs.
        :param item: An item from which to get the media links.
        :return: An ElementCollection object with the value of media links.
        """
        media_urls = re.findall(r'(https?://[^\s"<]+)', str(item))
        media_collection = None
        if media_urls:
            media_urls = set(map(lambda x: Element(ElementType.MEDIA, x), media_urls))
            image_urls = [image_url.value for image_url in images.elements]
            media_urls = [media_url for media_url in media_urls if media_url.value not in image_urls]
            media_collection = ElementCollection(ElementType.MEDIA, list(media_urls))
            logging.info(f'Got item\'s media urls, {len(media_collection)} found.')
        if not media_collection:
            logging.info('Media was not found')
        return media_collection

    @staticmethod
    @validate_method_args
    def _parse_images(item: PageElement) -> ElementCollection:
        """
        This method takes a PageElement object and returns an ElementCollection of media URLs.
        :param item: An item from which to get the media links.
        :return: An ElementCollection object with the value of media links.
        """
        images = [item.enclosure, item.content, item.thumbnail]
        images = [tag['url'] for tag in images if tag]
        if item.image:
            images.append(item.image.text)
        image_urls = set(map(lambda x: Element(ElementType.IMAGE, x), images))
        image_collection = ElementCollection(ElementType.IMAGE, list(image_urls))
        logging.info(f'Got item\'s media urls, {len(image_collection)} found.')
        if not image_collection:
            logging.info('Images were not found')
        return image_collection

    @staticmethod
    @validate_method_args
    def _parse_description(item: PageElement) -> Element:
        """
        This method parses the description of a page element and returns it as an Element object.
        :param item: An item from which to get the description.
        :return: An Element object with the value of the description.
        """
        desc_elem = Element(ElementType.DESCRIPTION)
        if getattr(item, 'description'):
            desc_elem.value = re.sub('<[^>]*>', '', item.description.text)
            logging.info(f'Got item\'s description: {desc_elem.value}')
        if not desc_elem.value:
            logging.info('Description was not found')
        return desc_elem

    def json_results(self) -> str:
        """
        This method returns a JSON string containing the results of
        the rss parser.
        :return: A string containing the json representation of the results
        """
        return self.feed.to_json()

    def save_pdf(self, path: str):
        """
        This method saves the current operating feed into a PDF file.
        """
        html = html_feed(self.feed, for_pdf=True, is_cache=self.is_offline)
        if os.path.exists(path):
            with open(f'{path}rss_feed.pdf', 'wb') as f:
                pdf_feed(html, f)
        else:
            logging.error('Given path was not found, saving to current location instead!')
            with open('rss_feed.pdf', 'wb') as f:
                pdf_feed(html, f)
        logging.info('Successfully saved the results into a PDF file.')

    def save_html(self, path: str) -> str:
        """
        This method saves the current operating feed into an HTML file.
        """
        html = html_feed(self.feed, is_cache=self.is_offline)
        if os.path.exists(path):
            with open(f'{path}rss_feed.html', 'w', encoding='utf-8') as f:
                f.write(html)
        else:
            logging.error('Given path was not found, saving to current location instead!')
            with open('rss_feed.html', 'w', encoding='utf-8') as f:
                f.write(html)
        return html

    @property
    def feed(self):
        return Feed(self.feed_title, self.url, self.parsed_items)
