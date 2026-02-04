"""
Parse raw data output
"""

from pathlib import Path

# remember to install "bibtexparser<2" because it's more forgiving
import bibtexparser
from lxml import etree


def parse_jmir_xml_file(xml_file_path: str | Path) -> tuple[str, list[str]]:
    """
    Extract data from xml file

    :param xml_file_path: Path to xml file with raw data
    :type xml_file_path: str | Path
    :return: tuple of the doi and a list of strings describing data availability.
    :rtype: tuple[ str, list[str]]
    """
    tree = etree.parse(xml_file_path)

    # Require the doi for this article
    try:
        doi = tree.xpath("//article-id[@pub-id-type='doi']/text()")[0]
    except:
        # if doi is missing, then pass an empty tuple
        return (None, [])

    data_results = []

    # Finds the 'p' tag that follows a 'title' containing 'Data Availability'
    data_availability = tree.xpath(
        "//title[text()='Data Availability']/following-sibling::p"
    )
    for result in data_availability:
        data_results.append(result.text)

    return doi, data_results


def parse_bibtex_file(bibtex_file_path: str | Path) -> list[tuple[str, list[str]]]:
    """
    Extract data from bibtex file

    :param bibtex_file_path: Path to bibtex file with raw data
    :type bibtex_file_path: str | Path
    :return: List of all the articles and their keywords found in the citation
    :rtype: list[tuple[str, list[str]]]
    """
    entries = []
    with open(bibtex_file_path, "r") as f:
        db = bibtexparser.load(f)

    for entry in db.entries:
        keywords = []
        if "keywords" in entry:
            keywords = entry["keywords"]
        entries.append((entry["doi"], keywords.split("; ")))

    return entries
