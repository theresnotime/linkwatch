import logging
import re

import mysql.connector
import tldextract

import constants

db = mysql.connector.connect(
    host=constants.DB_HOST,
    user=constants.DB_USER,
    password=constants.DB_PASSWORD,
    database=constants.DB_DATABASE,
    port=constants.DB_PORT,
)
cursor = db.cursor()

def logToDatabase(
    site: str,
    page_id: int,
    page_title: str,
    rev_id: int,
    user_name: str,
    datetime: str,
    link: str,
) -> None:
    """Log to database"""
    datetime = re.sub(r"T", " ", datetime)
    datetime = re.sub(r"Z", "", datetime)
    ext = tldextract.extract(link)
    if ext.domain != "":
        base_domain = ext.registered_domain
    else:
        base_domain = None

    sql = f"INSERT INTO {constants.DB_TABLE} "
    sql += "(added_date, site, page_id, page_title, rev_id, user_name, url, base_domain) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = (
        datetime,
        site,
        page_id,
        page_title,
        rev_id,
        user_name,
        link,
        base_domain,
    )
    cursor.execute(sql, values)

    db.commit()

    logging.debug(
        f"Saved to database: {datetime} {site} {page_id} {page_title} {rev_id} {user_name} {link} {base_domain}"
    )
