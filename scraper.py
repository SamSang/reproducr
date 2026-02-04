"""
Collection of webpage scrapers
"""

import requests
from bs4 import BeautifulSoup

from robots import (
    resolve_and_check,
    HEADERS,
)


def jmir_article(url: str):
    """
    Scrape relevant information from a jmir page

    :param url: url of the article
    :type url: str
    """
    final_url, allowed = resolve_and_check(url=url)
    if not allowed:
        return
    page = requests.get(final_url, headers=HEADERS)
    soup = BeautifulSoup(page.content, "html.parser")

    xml_links = soup.find_all("a", attrs={"aria-label": "Download XML"})
    for xml_link in xml_links:
        xml_url, xml_allowed = resolve_and_check(url=xml_link.get("href"))
        print(xml_url, xml_allowed)

    bibtex_links = soup.find_all("a", attrs={"aria-label": "Export metadata in BibTeX"})
    for bibtex_link in bibtex_links:
        bibtex_url, bibtex_allowed = resolve_and_check(url=bibtex_link.get("href"))
        print(bibtex_url, bibtex_allowed)
