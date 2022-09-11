"""
This module contains functions to convert an RSS Feed object to HTML.
"""
import logging

from airium import Airium

from rss_reader_pckg.rss.rss_classes import Feed, Item


def html_media(a: Airium, item: Item):
    """
    This function creates the HTML for media urls.
    :param a: The Airium object to create HTML.
    :param item: Item from which to get the urls.
    """
    a.h4(_t='Media Links:')
    for link in item.media_links.elements:
        if link.value == item.link.value:
            continue
        a.a(_t=link, href=link)
        a.br()


def html_images(a: Airium, item: Item, is_cache: bool = False):
    """
    This function creates the HTML for images from cache or from url.
    :param a: The Airium object to create HTML.
    :param item: Item from which to get the images.
    :param is_cache: Whether to take images from cache or from web.
    """
    a.h4(_t='Images:')
    for image_link in item.image_links.elements:
        link = 'cache/' + image_link.value.split('/')[-1] if is_cache else image_link.value
        a.img(src=link, style='height: 128px; width 128px;')
        a.br()


def html_feed(feed: Feed, for_pdf: bool = False, is_cache: bool = False) -> str:
    """
    This function creates the HTML template from Feed object.
    :param feed: The Feed object to create HTML from.
    :param for_pdf: Depending on this the styles will change to match pdf.
    :param is_cache: Whether to take images from cache or from web.
    :return A string containing the HTML template.
    """
    bg_color = '#DAA520' if not for_pdf else 'white'
    a = Airium()
    center_style = 'display: flex; justify-content: center; align-items: center;'
    column_div_style = ('box-sizing: border-box; height: 100%; padding-left:15%; padding-right:15%;'
                        ' display: flex; flex-direction: column;')
    item_div_style = (f'box-shadow: 0 0 5px 2px rgba(0,0,0,.35); border-radius: 8px; padding:'
                      f' 8px; background-color: {bg_color}; margin-bottom: 10px;')
    source_link_style = ('background-color: #f44336; color: white; padding: 5px 10px;'
                         ' text-align: center; text-decoration: none; display: inline-block;')
    a('<!DOCTYPE html>')
    with a.html(lang='en'):
        with a.head():
            a.meta(charset='utf-8')
            a.title(_t='RSS Feed Report')
        with a.body(style='background-color: #FF8C00;').div():
            a.h1(_t=feed.title, style=center_style)
            with a.div(style=column_div_style):
                for item in feed.items:
                    with a.div(style=item_div_style):
                        a.h3(_t=item.title)
                        a.h4(_t=item.date)
                        a.p(_t=f'Description - {item.description}')
                        if len(item.image_links) > 0:
                            html_images(a, item, is_cache)
                        if len(item.media_links) > 1:
                            html_media(a, item)

                        a.br()
                        a.a(_t='Source Link', href=item.link, style=source_link_style)

    if not for_pdf:
        logging.info('Successfully created the results into a HTML file.')
    return str(a)
