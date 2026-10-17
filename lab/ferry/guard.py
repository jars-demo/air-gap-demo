"""The gap guard: blocks every network call that would leave this machine.

It is a Python audit hook, so it sees the calls your Python code makes. It cannot see what a
browser loads from your HTML; that is what `ferry scan` is for.
"""

import atexit
import ipaddress
import sys
import time
import traceback
from pathlib import Path


class Blocked(ConnectionRefusedError):
    """Raised instead of connecting. It is an OSError, so code that copes with a dead network
    copes with this too."""


def is_local(host: object) -> bool:
    if isinstance(host, bytes):
        host = host.decode()
    if host in (None, "", "localhost"):
        return True
    try:
        return ipaddress.ip_address(str(host).split("%")[0]).is_loopback
    except ValueError:
        return False


def install(app_dir: Path, drop: float = 0.0) -> list[str]:
    """Block non-local connections. `drop` waits that many seconds first, like a firewall that
    silently drops packets instead of refusing them."""
    root = str(app_dir)
    blocked: list[str] = []

    def caller() -> str:
        for frame in reversed(traceback.extract_stack()):
            if frame.filename.startswith(root):
                where = Path(frame.filename).relative_to(app_dir.parent).as_posix()
                return f"{where}:{frame.lineno}"
        return "outside the app"

    def hook(event: str, args: tuple) -> None:
        if event == "socket.getaddrinfo":
            host, port = args[0], args[1]
        elif event == "socket.connect" and isinstance(args[1], tuple):
            host, port = args[1][0], args[1][1]
        else:
            return
        if is_local(host):
            return
        if isinstance(host, bytes):
            host = host.decode()
        blocked.append(f"{host}:{port}")
        print(f"  BLOCKED  {host}:{port}  from {caller()}", file=sys.stderr, flush=True)
        if drop:
            time.sleep(drop)
        raise Blocked(f"the gap guard blocked {host}:{port}")

    def summary() -> None:
        if blocked:
            calls = "call" if len(blocked) == 1 else "calls"
            print(f"gap guard: {len(blocked)} {calls} tried to leave", file=sys.stderr)
        else:
            print("gap guard: nothing tried to leave", file=sys.stderr)

    sys.addaudithook(hook)
    atexit.register(summary)
    return blocked
