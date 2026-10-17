"""ferry: carry an app across the air gap.

guard MODULE      run a Python module with every outbound call blocked
scan [DIR]        list every URL that points off this machine
pack              seal parrot (and its wheels) into a crate on the dock
send [CRATE]      ferry a crate to the island's inbox (watch out for pirates)
land [CRATE]      check a crate on the island and unpack it as a release
run               start the current release on the island, offline and guarded
releases          list the releases on the island
rollback          point the island back at the previous release
use VERSION       point the island at any release that has landed
reset             empty the dock and the island
"""

import argparse
import contextlib
import importlib.util
import json
import os
import runpy
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

from ferry import crate, guard, island, scan

LAB = Path(__file__).resolve().parent.parent
APP = LAB / "parrot"
DOCK = LAB / "dock"  # the mainland: crates you packed, wheels you downloaded, the seal key
ISLAND = LAB / "island"  # the other side of the gap


def digest(path: Path) -> str:
    return crate.sha256(path.read_bytes())


def newest(folder: Path) -> Path:
    crates = sorted(folder.glob("*.crate"), key=lambda p: p.stat().st_mtime)
    if not crates:
        sys.exit(f"no crates in {folder.relative_to(LAB)}")
    return crates[-1]


def seal_key() -> bytes:
    key = DOCK / "seal.key"
    if not key.exists():
        DOCK.mkdir(parents=True, exist_ok=True)
        ISLAND.mkdir(parents=True, exist_ok=True)
        key.write_text(secrets.token_hex(32) + "\n", encoding="utf-8")
        shutil.copy(key, ISLAND / "seal.key")
        print("new seal key in dock/seal.key, and a copy handed to the island (once, in person)")
    return key.read_text(encoding="utf-8").strip().encode()


def cmd_guard(args: argparse.Namespace) -> None:
    spec = importlib.util.find_spec(args.module)
    if spec is None or spec.origin is None:
        sys.exit(f"no module named {args.module}")
    guard.install(Path(spec.origin).parent, drop=args.drop)
    sys.argv = [args.module, *args.rest]
    runpy.run_module(args.module, run_name="__main__", alter_sys=True)


def cmd_scan(args: argparse.Namespace) -> None:
    root = Path(args.dir).resolve()
    findings = scan.scan(root)
    for finding in findings:
        print(f"  {finding.seen_by:<8} {finding.host:<28} {finding.where}")
    browser = sum(finding.seen_by == "browser" for finding in findings)
    print(
        f"{len(findings)} outbound URLs. {browser} load in the browser, where the guard can't see."
    )


def cmd_pack(args: argparse.Namespace) -> None:
    wheels = Path(args.wheels) if args.wheels else None
    out = crate.pack(APP, DOCK, seal_key(), wheels)
    files = json.loads(crate.read(out)["MANIFEST.json"])["files"]
    print(
        f"packed {out.relative_to(LAB).as_posix()}  {len(files)} files, {out.stat().st_size:,} bytes"
    )
    print(f"sha256 {digest(out)}")


def cmd_send(args: argparse.Namespace) -> None:
    source = Path(args.crate) if args.crate else newest(DOCK)
    target = ISLAND / "inbox" / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if args.pirates or args.clever_pirates:
        entries = crate.read(source)
        victim = f"{APP.name}/server.py"
        entries[victim] += b"\n# arr, the pirates were here\n"
        if args.clever_pirates:
            manifest = json.loads(entries["MANIFEST.json"])
            manifest["files"][victim] = crate.sha256(entries[victim])
            entries["MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
        crate.write(target, entries)
        print(f"pirates boarded the ferry and changed {victim}")
    else:
        shutil.copy(source, target)
    print(f"sent {source.name} to island/inbox")
    print(f"sha256 {digest(target)}")


def cmd_land(args: argparse.Namespace) -> None:
    source = Path(args.crate) if args.crate else newest(ISLAND / "inbox")
    key = ISLAND / "seal.key"
    if not key.exists():
        sys.exit("the island has no seal key yet: run `ferry pack` on the dock first")
    print(f"harbour master checking {source.name}")
    print(f"  sha256   {digest(source)}")
    try:
        manifest, release = island.land(
            source, ISLAND, key.read_text(encoding="utf-8").strip().encode()
        )
    except crate.Rejected as reason:
        print(f"  REJECTED {reason}")
        print("nothing was unpacked")
        sys.exit(1)
    print("  seal     ok")
    print(f"  files    {len(manifest['files'])} of {len(manifest['files'])} match the manifest")
    print(f"  landed   {release.relative_to(LAB).as_posix()}")
    print(f"current -> {manifest['version']}")


def cmd_run(args: argparse.Namespace) -> None:
    version = island.current(ISLAND)
    if version is None:
        sys.exit("nothing has landed on the island yet")
    release = ISLAND / "releases" / version
    env = {**os.environ, "PARROT_OFFLINE": "1"}
    env["PYTHONPATH"] = os.pathsep.join([str(release / "site"), str(LAB)])
    print(f"island: running {version} with PARROT_OFFLINE=1, behind the gap guard", flush=True)
    # -S skips this laptop's site-packages: the release must bring everything it needs.
    command = [sys.executable, "-S", "-m", "ferry", "guard", APP.name, *args.rest]
    with contextlib.suppress(KeyboardInterrupt):
        sys.exit(subprocess.call(command, cwd=release, env=env))


def cmd_releases(args: argparse.Namespace) -> None:
    now = island.current(ISLAND)
    for version in island.versions(ISLAND):
        print(f"  {'*' if version == now else ' '} {version}")
    if now is None:
        print("nothing has landed yet")


def cmd_rollback(args: argparse.Namespace) -> None:
    try:
        before, after = island.rollback(ISLAND)
    except crate.Rejected as reason:
        sys.exit(str(reason))
    print(f"current -> {after}  (was {before})")


def cmd_use(args: argparse.Namespace) -> None:
    if args.version not in island.versions(ISLAND):
        sys.exit(f"{args.version} has not landed on the island")
    before = island.current(ISLAND)
    island.point(ISLAND, args.version)
    print(f"current -> {args.version}  (was {before})")


def cmd_reset(args: argparse.Namespace) -> None:
    for folder in (DOCK, ISLAND):
        shutil.rmtree(folder, ignore_errors=True)
    print("the dock and the island are empty again")


def main() -> None:
    parser = argparse.ArgumentParser(prog="ferry", description="Carry an app across the air gap.")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("guard", help="run a module with every outbound call blocked")
    p.add_argument("module")
    p.add_argument(
        "--drop",
        type=float,
        default=0.0,
        metavar="SECONDS",
        help="wait before failing, like a firewall that drops packets",
    )
    p.add_argument("rest", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_guard)

    p = sub.add_parser("scan", help="list every URL that points off this machine")
    p.add_argument("dir", nargs="?", default=str(APP))
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("pack", help="seal parrot into a crate on the dock")
    p.add_argument("--wheels", metavar="DIR", help="also carry the wheels in this folder")
    p.set_defaults(func=cmd_pack)

    p = sub.add_parser("send", help="ferry a crate to the island")
    p.add_argument("crate", nargs="?")
    p.add_argument("--pirates", action="store_true", help="change a file on the way")
    p.add_argument("--clever-pirates", action="store_true", help="change a file and the manifest")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("land", help="check a crate and unpack it as a release")
    p.add_argument("crate", nargs="?")
    p.set_defaults(func=cmd_land)

    p = sub.add_parser("run", help="start the current release, offline and guarded")
    p.add_argument("rest", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("use", help="point the island at a release that has landed")
    p.add_argument("version")
    p.set_defaults(func=cmd_use)

    for name, func, text in [
        ("releases", cmd_releases, "list the releases on the island"),
        ("rollback", cmd_rollback, "point the island at the previous release"),
        ("reset", cmd_reset, "empty the dock and the island"),
    ]:
        sub.add_parser(name, help=text).set_defaults(func=func)

    args, extra = parser.parse_known_args()
    if extra and args.func not in (cmd_guard, cmd_run):
        parser.error(f"unrecognized arguments: {' '.join(extra)}")
    args.rest = [*extra, *getattr(args, "rest", [])]
    args.func(args)


if __name__ == "__main__":
    main()
