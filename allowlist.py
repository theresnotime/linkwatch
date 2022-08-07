import re

import tldextract

import constants


def checkAllowList(domain: str) -> bool:
    ext = tldextract.extract(domain)

    if checkMalformedCommons(domain) is True:
        # print(f"commons is in the allowlist")
        return True

    if ext.domain != "":
        if ext.registered_domain in constants.ALLOWLIST:
            # print(f"{ext.registered_domain} is in the allowlist")
            return True
        else:
            # print(f"{ext.registered_domain} is not in the allowlist")
            return False


def checkMalformedCommons(domain: str) -> bool:
    regex = re.compile(r"^https:////commons\.wikimedia\.org.*")
    if regex.match(domain):
        return True
    else:
        return False
