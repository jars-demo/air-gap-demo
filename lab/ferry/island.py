"""The island side: land a crate, keep every release, point `current` at one, roll back."""

import io
import zipfile
from pathlib import Path

from ferry.crate import Rejected, inspect


def versions(island: Path) -> list[str]:
    releases = island / "releases"
    found = [path.name for path in releases.iterdir()] if releases.exists() else []
    return sorted(found, key=lambda v: tuple(int(part) for part in v.split(".")))


def current(island: Path) -> str | None:
    pointer = island / "current"
    return pointer.read_text(encoding="utf-8").strip() if pointer.exists() else None


def point(island: Path, version: str) -> None:
    (island / "current").write_text(version + "\n", encoding="utf-8")


def land(crate: Path, island: Path, key: bytes) -> tuple[dict, Path]:
    manifest, entries = inspect(crate, key)
    release = island / "releases" / manifest["version"]
    if release.exists():
        raise Rejected(f"{manifest['version']} has already landed. Releases never change: bump it")
    wheels = {name: data for name, data in entries.items() if name.startswith("wheels/")}
    for name in wheels:
        if not name.endswith("-none-any.whl"):
            raise Rejected(f"{name} is built for one platform; ferry unpacks pure-Python wheels")

    for name, data in entries.items():
        if name not in wheels:
            target = release / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    for data in wheels.values():
        # A pure-Python wheel is a zip laid out like site-packages: unzipping is installing.
        zipfile.ZipFile(io.BytesIO(data)).extractall(release / "site")

    point(island, manifest["version"])
    return manifest, release


def rollback(island: Path) -> tuple[str, str]:
    now, landed = current(island), versions(island)
    if now not in landed or landed.index(now) == 0:
        raise Rejected("there is no older release to roll back to")
    previous = landed[landed.index(now) - 1]
    point(island, previous)
    return now, previous
