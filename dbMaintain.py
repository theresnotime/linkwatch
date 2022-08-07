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


def tidyArchiveLinks(base_domain: str, regex: str) -> int:
    """"""
    tidyCount = 0
    cursor.execute(
        f"SELECT * FROM {constants.DB_TABLE} WHERE base_domain = '{base_domain}'"
    )
    result = cursor.fetchall()
    for row in result:
        url = row[7]
        match = re.match(regex, url)
        if match:
            new_url = match.group("url")
            print(f"{url} -> {new_url}")
            ext = tldextract.extract(new_url)
            if ext.domain != "":
                base_domain = ext.registered_domain
            else:
                base_domain = None
            cursor.execute(
                f"UPDATE {constants.DB_TABLE} SET url = '{new_url}', base_domain = '{base_domain}' WHERE record_id = {row[0]}"
            )
            db.commit()
            tidyCount += 1

    return tidyCount


def tidyLinks() -> None:
    """Tidy links"""
    print("Tidying archive.org links...")
    tidyCount = tidyArchiveLinks("archive.org", constants.RE_ARCHIVEORG)
    print(f"Finished tidying {tidyCount} archive.org links!")


def doMaintenance() -> None:
    """Do maintenance"""
    print("=== Data maintenance ===")
    print(f"Running on table: {constants.DB_TABLE}", end="\n\n")
    tidyLinks()
    print("Finished data maintenance!")


if __name__ == "__main__":
    doMaintenance()
