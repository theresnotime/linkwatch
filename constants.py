import json
import os
import re
import typing

import dotenv

dotenv.load_dotenv()

# Version
VERSION = "1.1.0"

dir_path = os.path.dirname(os.path.realpath(__file__))

with open(dir_path + "/config/allowlist.json", encoding="utf-8") as allowfile:
    ALLOWLIST = json.load(allowfile)

# DB
DB_HOST = typing.cast(str, os.getenv("DB_HOST"))
DB_USER = typing.cast(str, os.getenv("DB_USER"))
DB_PASSWORD = typing.cast(str, os.getenv("DB_PASSWORD"))
DB_DATABASE = typing.cast(str, os.getenv("DB_DATABASE"))
DB_PORT = typing.cast(str, os.getenv("DB_PORT"))
DB_TABLE = typing.cast(str, os.getenv("DB_TABLE"))
DB_VIEW = typing.cast(str, os.getenv("DB_VIEW"))

# Regexes
RE_ARCHIVEORG = re.compile(
    r"http(s)?://web\.archive\.org\/web\/(\d+|\*)\/(?P<url>http(s)?:.*)$", re.IGNORECASE
)
