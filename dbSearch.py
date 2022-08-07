import sys

import mysql.connector

import constants

db = mysql.connector.connect(
    host=constants.DB_HOST,
    user=constants.DB_USER,
    password=constants.DB_PASSWORD,
    database=constants.DB_DATABASE,
    port=constants.DB_PORT,
)
cursor = db.cursor()
args = sys.argv[1:]


def searchBase() -> None:
    """"""
    base = args[1]

    # Shush.
    if len(args) > 1:
        count = True
    else:
        count = False

    print("=== Base domain search ===")
    print(f"Query: {base}")
    print(f"Searching on db: {constants.DB_DATABASE}")
    print(f"Searching on table: {constants.DB_TABLE}", end="\n\n")

    if count is False:
        cursor.execute(
            f"SELECT added_date, user_name, page_title, site, rev_id, url FROM {constants.DB_VIEW} WHERE base_domain = '{base}'"
        )
        result = cursor.fetchall()
        print(f"{len(result)} results found")
        print(
            "|       Date        |        User        |        Diff        |        Page        |        URL        |"
        )
        for row in result:
            print(
                f"| {row[0]} | https://{row[3]}/wiki/User:{row[1]} | https://{row[3]}/wiki/Special:Diff/{row[4]} | https://{row[3]}/wiki/{row[2]} | {row[5]} |"
            )
    else:
        cursor.execute(
            f"SELECT COUNT(record_id) as `count` FROM {constants.DB_VIEW} WHERE base_domain = '{base}'"
        )
        result = cursor.fetchone()
        print(f"{result[0]} results found")


if __name__ == "__main__":
    if len(args) < 2:
        print("Usage: dbSearch.py <type> <query>")
        sys.exit(1)
    else:
        if args[0] == "url":
            # searchURL
            pass
        elif args[0] == "base":
            searchBase()
            pass
        elif args[0] == "user":
            # searchUser
            pass
        else:
            print("Invalid argument, exiting...")
            exit(1)
