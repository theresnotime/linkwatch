import re
import sys

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


def tidyArchiveLinks(base_domain: str, regex: str, dryrun: bool = False) -> int:
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
            if not dryrun:
                db.commit()
            tidyCount += 1

    return tidyCount


def markMaintenceNeeded(dryrun: bool = False) -> int:
    """"""
    markCount = 0
    cursor.execute(
        f"SELECT * FROM {constants.DB_TABLE} WHERE needs_maintenance = 0 AND base_domain = ''"
    )
    result = cursor.fetchall()
    for row in result:
        cursor.execute(
            f"UPDATE {constants.DB_TABLE} SET needs_maintenance = 1 WHERE record_id = {row[0]}"
        )
        if not dryrun:
            db.commit()
        markCount += 1

    return markCount


def tidyLinks(dryrun: bool = False) -> None:
    """Tidy links"""
    print("Tidying archive.org links...")
    tidyCount = tidyArchiveLinks("archive.org", constants.RE_ARCHIVEORG, dryrun)
    print(f"Finished tidying {tidyCount} archive.org links!")


def doMaintenance(dryrun: bool = False) -> None:
    """Do maintenance"""
    print("=== Data maintenance ===")
    if dryrun:
        print("Dry run, no changes will be made")
    print(f"Running on db: {constants.DB_DATABASE}")
    print(f"Running on table: {constants.DB_TABLE}", end="\n\n")
    tidyLinks(dryrun)
    markCount = markMaintenceNeeded(dryrun)
    if markCount > 0:
        print(f"[WARN] Marked {markCount} records as still needing maintenance")
    print("Finished data maintenance!")


def getEmpty() -> int:
    """"""
    cursor.execute(
        f"SELECT COUNT(record_id) as `count` FROM {constants.DB_VIEW} WHERE base_domain = ''"
    )
    result = cursor.fetchone()
    return result[0]


def getCount() -> int:
    """"""
    cursor.execute(f"SELECT COUNT(record_id) as `count` FROM {constants.DB_VIEW}")
    result = cursor.fetchone()
    return result[0]


def doStats() -> None:
    """Do stats"""
    print("=== Stats ===")
    print(f"Running on db: {constants.DB_DATABASE}")
    print(f"Running on view: {constants.DB_VIEW}", end="\n\n")
    print(f"Total rows: {getCount()}")
    print(f"Empty base domains: {getEmpty()}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--dryrun" in args:
        dryrun = True
    else:
        dryrun = False

    if len(args) == 0:
        doStats()
        print("\n")
        doMaintenance(dryrun)
    else:
        if args[0] == "run":
            doMaintenance(dryrun)
        elif args[0] == "stats":
            doStats()
        else:
            print("Invalid argument, exiting...")
            exit(1)
