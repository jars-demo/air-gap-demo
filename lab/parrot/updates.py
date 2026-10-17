"""Asks the mainland whether a newer parrot exists."""

import json
import urllib.request

from parrot import __version__, config

URL = "https://updates.parrot.example/latest.json"


def check() -> str | None:
    if config.OFFLINE:
        return None
    try:
        with urllib.request.urlopen(URL, timeout=3) as response:
            latest = json.load(response)["version"]
    except (OSError, ValueError, KeyError):
        return None
    return latest if latest != __version__ else None
