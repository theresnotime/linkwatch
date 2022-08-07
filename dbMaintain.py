import logging
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

logging.basicConfig(
    handlers=[
        logging.FileHandler("linkwatch.maintenance.log"),
        logging.StreamHandler(),
    ],
    encoding="utf-8",
    level=logging.DEBUG,
    format="[%(asctime)s]: %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def copyTable(fromDB: str, toDB: str, dryrun: bool = False) -> None:
    """Copy table"""
    print("=== Copy table ===")
    if dryrun:
        print("Dry run, no changes will be made")
    print(f"Copying from: {fromDB}")
    print(f"Copying to: {toDB}")
    print(f"Running on table: {constants.DB_TABLE}", end="\n\n")
    # Harcoded safety check
    if fromDB == toDB:
        logging.error("Can't copy table to same database")
        sys.exit(1)
    if toDB == "linkwatch":
        logging.error("You are trying to copy TO the production database")
        sys.exit(1)
    if not dryrun:
        logging.info(f"DROP TABLE IF EXISTS {toDB}.{constants.DB_TABLE}")
        cursor.execute(f"DROP TABLE IF EXISTS {toDB}.{constants.DB_TABLE}")
        logging.info(
            f"CREATE TABLE {toDB}.{constants.DB_TABLE} LIKE {fromDB}.{constants.DB_TABLE}"
        )
        cursor.execute(
            f"CREATE TABLE {toDB}.{constants.DB_TABLE} LIKE {fromDB}.{constants.DB_TABLE}"
        )
        logging.info(
            f"INSERT {toDB}.{constants.DB_TABLE} SELECT * FROM {fromDB}.{constants.DB_TABLE}"
        )
        cursor.execute(
            f"INSERT {toDB}.{constants.DB_TABLE} SELECT * FROM {fromDB}.{constants.DB_TABLE}"
        )
        db.commit()
    else:
        print("Dry run, no changes will be made, but would have run:")
        print(f"DROP TABLE IF EXISTS {toDB}.{constants.DB_TABLE}")
        print(
            f"CREATE TABLE {toDB}.{constants.DB_TABLE} LIKE {fromDB}.{constants.DB_TABLE}"
        )
        print(
            f"INSERT {toDB}.{constants.DB_TABLE} SELECT * FROM {fromDB}.{constants.DB_TABLE}"
        )
    logging.info("Finished copying table")


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
    logging.info("Finished data maintenance")


def getLikelyArchives() -> int:
    """"""
    cursor.execute(
        f"SELECT COUNT(record_id) as `count` FROM {constants.DB_VIEW} WHERE base_domain LIKE '%archive%'"
    )
    result = cursor.fetchone()
    return result[0]


def getMarked() -> int:
    """"""
    cursor.execute(
        f"SELECT COUNT(record_id) as `count` FROM {constants.DB_VIEW} WHERE needs_maintenance = 1"
    )
    result = cursor.fetchone()
    return result[0]


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
    print(f"Rows marked as needing maintenance: {getMarked()}")
    print(f"Rows with empty base domains: {getEmpty()}")
    print(f"Rows with likely archive base domains: {getLikelyArchives()}")


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
        elif args[0] == "archiveorg":
            tidyCount = tidyArchiveLinks("archive.org", constants.RE_ARCHIVEORG, dryrun)
            logging.info(f"Tidied {tidyCount} archive.org links")
        elif args[0] == "sync":
            copyTable("linkwatch", "linkwatchdev", dryrun)
        else:
            print("Invalid argument, exiting...")
            exit(1)
