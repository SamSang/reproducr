"""
Fetch, store and analyze the robots.txt file for relevant sites
"""

from datetime import datetime
from pathlib import Path
import requests
from sqlite_utils import Database
import sqlite3
import urllib.robotparser as robotparser
from urllib.parse import urlparse

db_file_path = Path(Path(__file__).parent, "robots.db")
date_format_string = "%Y%m%d"


def get_robots(base_url: str) -> str:
    """
    Connect to the site and return the robots.txt file

    :param base_url: base url for the address
    :type base_url: str
    :return: robots.txt for that base url
    :rtype: str
    """

    robots = requests.get(f"{base_url}/robots.txt", timeout=10)
    robots.raise_for_status()

    return robots.text


def init_robots_db(db_file: str | Path = db_file_path) -> None:
    """
    Docstring for init_robots_db

    :param db_file: path to
    :type db_file: str
    """

    db = Database(db_file)
    db["robots"].create(
        {
            "base_url": str,
            "robots_txt": str,
            "updated": str,  # coerce to date later
        }
    )


def save_robots(base_url: str, db_file: str | Path = db_file_path) -> None:
    """
    Save content of robots.txt to a sqllite database

    :param base_url: base url for the address
    :type base_url: str
    :param db_file: path to sqllite database file
    :type db_file: str
    """

    with sqlite3.connect(db_file) as conn:
        conn.execute(f"DELETE FROM robots WHERE base_url = '{base_url}'")
        conn.execute(
            f"INSERT INTO robots VALUES ('{base_url}', '{get_robots(base_url)}', '{datetime.strftime(datetime.now(), date_format_string)}')"
        )
        conn.commit()


def update_robots(base_url: str, db_file: str | Path = db_file_path) -> None:
    """
    Check if today's base_url exists in the db

    :param base_url: url to check
    :type base_url: str
    :param db_file: file for database
    :type db_file: str | Path
    :return: if exists in the db, then True
    :rtype: bool
    """

    with sqlite3.connect(db_file) as conn:
        updated = conn.execute(
            f"SELECT updated FROM robots WHERE base_url = '{base_url}' ORDER BY updated desc"
        ).fetchall()
        if updated:
            last_updated = updated[0]
            if last_updated != datetime.strftime(datetime.now(), date_format_string):
                save_robots(base_url, db_file=db_file)


def is_allowed(
    user_agent: str, target_url: str, db_file: str | Path = db_file_path
) -> bool:
    """
    Docstring for is_allowed

    :param base_url: base url
    :type base_url: str
    :param user_agent: Description
    :type user_agent: str
    :param target_url: Description
    :type target_url: str
    :param db_file: Description
    :type db_file: str | Path
    :return: Description
    :rtype: bool
    """
    base_url = urlparse(target_url).netloc

    with sqlite3.connect(db_file) as conn:
        robots_txt = conn.execute(
            f"SELECT robots_txt FROM robots WHERE base_url = '{base_url}' limit 1"
        ).fetchall()
    rp = robotparser.RobotFileParser()
    rp.parse(robots_txt)

    return rp.can_fetch(user_agent, target_url)
