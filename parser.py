"""
Parse raw data output
"""

from pathlib import Path

from lxml import etree


def parse_jmir_xml_file(xml_file_path: str | Path) -> tuple[str, list[str]]:
    """
    Extract data from xml file

    :param xml_file_path: Path to xml file with raw data
    :type xml_file_path: str | Path
    :return: list of strings describing data availability.
    :rtype: list[str]
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
