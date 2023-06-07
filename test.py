import allowlists
import time
import tldextract
from eventstreams import EventStreams
from termcolor import cprint


def get_project_family(project_domain):
    """Get the project family from the project domain"""
    # Odd one out
    if project_domain == "commons.wikimedia.org":
        return "commons"
    return tldextract.extract(project_domain).domain


def get_registered_domain(url):
    """Get the registered domain from a URL"""
    return tldextract.extract(url).registered_domain


def check_url_allowlists(url):
    """Check if a URL is in the allowlists"""
    registered_domain = get_registered_domain(url)
    if registered_domain in allowlists.combined_domains:
        return True
    return False


def check_ug_allowlists(performer):
    """Check if a user group is in the allowlists"""
    if (
        "user_groups" in performer
        and performer["user_groups"] in allowlists.user_groups
    ):
        return True
    return False


if __name__ == "__main__":
    stream = EventStreams(streams=["page-links-change"], timeout=1)
    # stream.register_filter(external = True)

    print(
        "[added_date] [project_domain] [project_family] [page_id] [rev_id] [user_text] [link_url] [base_domain]"
    )
    while stream:
        try:
            change = next(iter(stream))
            database = change["database"]
            project_domain = change["meta"]["domain"]
            performer = change["performer"]
            added_date = change["meta"]["dt"]
            project_family = get_project_family(project_domain)

            # Skip bot edits
            if "user_is_bot" in performer and performer["user_is_bot"]:
                cprint(
                    f"Bot edit by {performer['user_text']} to {database}, skipping",
                    "blue",
                )
                continue

            # Skip edits which don't add links
            if "added_links" in change:
                page_id = change["page_id"]
                page_title = change["page_title"]
                rev_id = change["rev_id"]
                if "user_id" in performer:
                    user_id = performer["user_id"]
                else:
                    user_id = None
                    user_is_ip = True
                user_text = performer["user_text"]

                added_links = change["added_links"]
                for link in added_links:
                    # Skip external links
                    if link["external"]:
                        link_url = link["link"]
                        if check_url_allowlists(link_url):
                            cprint("URL in allowlist, skipping", "green")
                        elif check_ug_allowlists(performer):
                            cprint("User group in allowlist, skipping", "green")
                        else:
                            base_domain = get_registered_domain(link_url)
                            # Print columns for database imput
                            print(
                                f"[{added_date}] [{project_domain}] [{project_family}] [{page_id}] [{rev_id}] [{user_text}] [{link_url}] [{base_domain}]"
                            )
            time.sleep(1)
        except KeyError:
            cprint("Caught KeyError exception, skipping", "red")
            continue
