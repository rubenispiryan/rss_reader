"""
This module contains functions to convert an RSS Feed object to PDF.
"""

import time
from typing import BinaryIO

from xhtml2pdf import pisa


def pdf_feed(html: str, file: BinaryIO) -> bool:
    """
    This function creates a PDF from HTML string.
    :param html: The HTML template.
    :param file: The file object to which to write.
    :return: Success or failure of conversion.
    """
    pisa_status = pisa.CreatePDF(
        html,
        dest=file)

    return pisa_status.err