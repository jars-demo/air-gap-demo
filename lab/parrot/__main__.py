import argparse
import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from rich.console import Console

from parrot import __version__, config, server, telemetry, updates


def main() -> None:
    parser = argparse.ArgumentParser(prog="parrot")
    parser.add_argument("--selftest", action="store_true", help="ask for one squawk, then stop")
    parser.add_argument("--mood", default="happy", help="the mood to ask for in the selftest")
    args = parser.parse_args()
    console = Console(highlight=False, soft_wrap=True)

    started = time.perf_counter()
    telemetry.ping()
    newer = updates.check()
    httpd = server.make(config.PORT)
    took = time.perf_counter() - started

    console.print(f"[bold]parrot {__version__}[/] from {Path(__file__).parent}")
    console.print(
        f"ready in {took:.1f} s on http://127.0.0.1:{config.PORT}  offline={config.OFFLINE}"
    )
    if newer:
        console.print(f"parrot {newer} is out")

    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        if args.selftest:
            url = f"http://127.0.0.1:{config.PORT}/api/squawk?mood={args.mood}"
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    console.print(f"selftest: parrot says {json.load(response)['says']!r}")
            except urllib.error.HTTPError as error:
                console.print(f"selftest: {error.code} {json.load(error)['error']}")
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()
