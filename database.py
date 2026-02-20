"""
Build persistent storage for the extracted data

In and AWS postgres instance
"""

import json
from pathlib import Path

import psycopg

def get_config() -> tuple[str, str, str, str]:
    """
    Read values needed for database authentication
    """
    with open(Path(Path(__file__).parent, "config.json"), "r") as f:
        postgres = json.load(f).get("postgres", {})

    user = postgres["user"]
    pw = postgres["pw"]
    host = postgres["host"]
    db_name = postgres["db_name"]

    return user, pw, host, db_name


USER, PW, HOST, DB_NAME = get_config()


def write_efetch(data: list[tuple]) -> None:
    """
    Write data to the eftech table
    Rely on positions in the tuple: jmid, doi, data_availability
    """
    with psycopg.connect(host=HOST, dbname=DB_NAME, user=USER, password=PW) as conn:
        with conn.cursor() as cur:
            with cur.copy(
                "COPY efetch (jmid, doi, data_availability) FROM STDIN"
            ) as copy:
                copy.write(data)


def write_esummary(data: list[dict]) -> None:
    """
    Write data to the eftech table
    Iterate through the dictionary and insert one row at a time
    using a shared cursor and transaction
    """
    with psycopg.connect(host=HOST, dbname=DB_NAME, user=USER, password=PW) as conn:
        with conn.cursor() as cur:
            for row in data:
                query = f"INSERT INTO esummary ({', '.join(row.keys())}) VALUES ({','.join([f"%({col})s" for col in row])})"
                cur.execute(query, row)


def init(name="postgres") -> None:
    """
    Create tables if they do not exist
    """
    base_path = Path(Path(__file__).parent, name)
    sql_paths = base_path.glob("*sql")

    with psycopg.connect(host=HOST, dbname=DB_NAME, user=USER, password=PW) as conn:
        with conn.cursor() as cur:
            for sql_path in sql_paths:
                with open(sql_path, "r") as f:
                    print(f.read)
                    cur.execute(f.read())


def write_data(data: list[dict]) -> None:
    """
    Insert data to the database
    """
    # TODO write data to the database
    print(data)
    # print(len(data))
    pass
