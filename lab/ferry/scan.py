"""Find every URL in a folder that points off this machine, including the ones only a browser
would follow."""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from ferry.guard import is_local

URL = re.compile(r"""\b(?:https?|wss?|ftp)://[^\s"'<>)\]}]+""")
CODE = {".py", ".toml", ".json", ".cfg", ".ini", ".yaml", ".yml", ".env", ".txt"}
BROWSER = {".html", ".htm", ".css", ".js", ".mjs", ".svg"}


@dataclass(frozen=True)
class Finding:
    where: str
    host: str
    seen_by: str  # "code" runs in Python, "browser" runs on the visitor's machine


def scan(root: Path) -> list[Finding]:
    findings = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in CODE | BROWSER:
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for number, line in enumerate(lines, 1):
            for match in URL.finditer(line):
                host = urlsplit(match.group()).hostname
                if host and not is_local(host):
                    seen_by = "browser" if path.suffix in BROWSER else "code"
                    where = f"{path.relative_to(root.parent).as_posix()}:{number}"
                    findings.append(Finding(where, host, seen_by))
    return findings
