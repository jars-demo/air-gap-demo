"""A crate is one tar file that carries a release across the gap.

Inside: MANIFEST.json (the SHA-256 of every file), SEAL (an HMAC of the manifest) and the files.
The same source always packs to the same bytes, so the digest you announce can be checked.
"""

import hashlib
import hmac
import io
import json
import re
import tarfile
from pathlib import Path, PurePosixPath


class Rejected(Exception):
    """The crate failed a check. Nothing from it may be unpacked."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def seal(key: bytes, manifest: bytes) -> str:
    return hmac.new(key, manifest, "sha256").hexdigest()


def version_of(app_dir: Path) -> str:
    text = (app_dir / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__ = "([^"]+)"', text).group(1)


def collect(app_dir: Path, wheels: Path | None = None) -> dict[str, bytes]:
    files = {}
    for path in sorted(app_dir.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            files[f"{app_dir.name}/{path.relative_to(app_dir).as_posix()}"] = path.read_bytes()
    if wheels:
        for wheel in sorted(wheels.glob("*.whl")):
            files[f"wheels/{wheel.name}"] = wheel.read_bytes()
    return files


def manifest_for(name: str, version: str, files: dict[str, bytes]) -> bytes:
    manifest = {
        "name": name,
        "version": version,
        "files": {path: sha256(data) for path, data in sorted(files.items())},
    }
    return (json.dumps(manifest, indent=2) + "\n").encode()


def write(out: Path, entries: dict[str, bytes]) -> None:
    """Write a tar with fixed times, owners and order, so it is byte-for-byte reproducible."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out, "w", format=tarfile.PAX_FORMAT) as tar:
        for name, data in entries.items():
            info = tarfile.TarInfo(name)
            info.size, info.mtime, info.mode = len(data), 0, 0o644
            tar.addfile(info, io.BytesIO(data))


def pack(app_dir: Path, out_dir: Path, key: bytes, wheels: Path | None = None) -> Path:
    version = version_of(app_dir)
    files = collect(app_dir, wheels)
    manifest = manifest_for(app_dir.name, version, files)
    entries = {"MANIFEST.json": manifest, "SEAL": (seal(key, manifest) + "\n").encode(), **files}
    out = out_dir / f"{app_dir.name}-{version}.crate"
    write(out, entries)
    return out


def read(crate: Path) -> dict[str, bytes]:
    entries = {}
    with tarfile.open(crate) as tar:
        for member in tar.getmembers():
            path = PurePosixPath(member.name)
            if not member.isfile():
                raise Rejected(f"{member.name} is not a plain file")
            if path.is_absolute() or ".." in path.parts:
                raise Rejected(f"{member.name} tries to climb out of the release folder")
            entries[member.name] = tar.extractfile(member).read()
    return entries


def inspect(crate: Path, key: bytes) -> tuple[dict, dict[str, bytes]]:
    """Check the seal, then every file, before anything touches the disk."""
    entries = read(crate)
    manifest_bytes = entries.pop("MANIFEST.json", b"")
    expected = seal(key, manifest_bytes)
    if not hmac.compare_digest(expected, entries.pop("SEAL", b"").decode().strip()):
        raise Rejected("the seal does not match the manifest")
    manifest = json.loads(manifest_bytes)
    for name in entries:
        if name not in manifest["files"]:
            raise Rejected(f"{name} is not in the manifest")
    for name, digest in manifest["files"].items():
        if name not in entries:
            raise Rejected(f"{name} is missing")
        if sha256(entries[name]) != digest:
            raise Rejected(f"{name} does not match the manifest")
    return manifest, entries
