"""Sends crashes home so the parrot team can fix them. Nobody added the offline switch here."""

import contextlib
import json
import urllib.request

from parrot import __version__

URL = "https://errors.parrot.example/v1/report"


def report(error: BaseException) -> None:
    body = json.dumps({"version": __version__, "error": repr(error)}).encode()
    with contextlib.suppress(OSError):
        urllib.request.urlopen(urllib.request.Request(URL, data=body), timeout=3)
