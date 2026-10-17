"""Tells the mainland that parrot started. Harmless at home, a hang on the island."""

import contextlib
import json
import urllib.request

from parrot import __version__, config

URL = "https://telemetry.parrot.example/v1/ping"


def ping() -> None:
    if config.OFFLINE:
        return
    body = json.dumps({"event": "start", "version": __version__}).encode()
    # Never let this break the app, which is also why nobody notices it.
    with contextlib.suppress(OSError):
        urllib.request.urlopen(urllib.request.Request(URL, data=body), timeout=3)
