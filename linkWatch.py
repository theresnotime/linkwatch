from datetime import datetime

from pywikibot.comms.eventstreams import EventStreams

import allowlist
import constants
import logger


def streamEdits():
    """Stream edits"""
    stream = EventStreams(streams=["page-links-change"])

    print("Filtering events...")
    while stream:
        try:
            change = next(iter(stream))
            if change["page_namespace"] == 0:
                if "performer" in change:
                    if change["performer"]["user_is_bot"] is False:
                        if "user_text" in change["performer"]:
                            if "added_links" in change:
                                if change["added_links"][0]["external"] is True:
                                    link = change["added_links"][0]["link"]
                                    if allowlist.checkAllowList(link) is False:
                                        page_id = change["page_id"]
                                        page_title = change["page_title"]
                                        rev_id = change["rev_id"]
                                        user_name = change["performer"]["user_text"]
                                        datetime = change["meta"]["dt"]
                                        site = change["meta"]["domain"]
                                        logger.logToDatabase(
                                            site,
                                            page_id,
                                            page_title,
                                            rev_id,
                                            user_name,
                                            datetime,
                                            link,
                                        )
        except:
            print("Error")
            break


def main():
    """Set up and stream edits"""
    streamEdits()


if __name__ == "__main__":
    print("=== LinkWatch started ===")
    print(f"Started at: {datetime.now()}")
    print(f"Version: {constants.VERSION}")
    print(f"Running on db: {constants.DB_DATABASE}")
    print(f"Running on view: {constants.DB_VIEW}", end="\n\n")
    main()
