"""The notice board: one page, one API, all on 127.0.0.1."""

import json
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from parrot import crash

HERE = Path(__file__).parent
PHRASES = json.loads((HERE / "phrases.json").read_text(encoding="utf-8"))
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/static/parrot.css": ("parrot.css", "text/css"),
    "/static/parrot.js": ("parrot.js", "text/javascript"),
    "/static/confetti.js": ("confetti.js", "text/javascript"),
}


class Board(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        url = urlsplit(self.path)
        if url.path in STATIC:
            name, kind = STATIC[url.path]
            self.send(200, (HERE / "static" / name).read_bytes(), kind)
        elif url.path == "/health":
            self.send(200, b"ok\n", "text/plain")
        elif url.path == "/api/squawk":
            mood = parse_qs(url.query).get("mood", ["happy"])[0]
            try:
                phrase = random.choice(PHRASES[mood])
            except KeyError as error:
                crash.report(error)
                self.send(500, b'{"error": "parrot has no such mood"}', "application/json")
                return
            body = json.dumps({"mood": mood, "says": phrase}).encode()
            self.send(200, body, "application/json")
        else:
            self.send(404, b"not found\n", "text/plain")

    def send(self, status: int, body: bytes, kind: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass  # keep the terminal for what matters


def make(port: int) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Board)
