# Cross the gap

> Send the crate across, meet some pirates, and let the harbour master check everything before a single file touches the island.

**Time:** 15 minutes

## Goal

Send a crate to the island, watch tampered crates get rejected, land a clean one as a release, and run it.

## Pirates

Transfers go wrong: a corrupt USB stick, a proxy that rewrites files, or someone with bad intentions. `ferry send --pirates` changes one file on the way:

```bash
uv run python -m ferry send --pirates
uv run python -m ferry land
```

```text
pirates boarded the ferry and changed parrot/server.py
sent parrot-1.0.0.crate to island/inbox
sha256 dfcdf91fc62846ec1320d695e6be2b9e18f0966aa3cf77aa9c6551be42d958a6
harbour master checking parrot-1.0.0.crate
  sha256   dfcdf91fc62846ec1320d695e6be2b9e18f0966aa3cf77aa9c6551be42d958a6
  REJECTED parrot/server.py does not match the manifest
nothing was unpacked
```

The `sha256` no longer matches the one `ferry pack` printed in chapter 03, so a careful person would stop there. The harbour master also catches it alone: one file's hash does not match the manifest.

Clever pirates change the file **and** fix its hash in the manifest:

```bash
uv run python -m ferry send --clever-pirates
uv run python -m ferry land
```

```text
  REJECTED the seal does not match the manifest
nothing was unpacked
```

The pirates do not have the seal key, so they cannot make a seal that fits the new manifest. That is the whole job of the seal.

## An honest crossing

```bash
uv run python -m ferry send
uv run python -m ferry land
```

```text
harbour master checking parrot-1.0.0.crate
  sha256   4fed1c4d54357115a1fd08311f6bd9eb19d7e7cbe8fac2d17b0eee2a96024cb3
  seal     ok
  files    12 of 12 match the manifest
  landed   island/releases/1.0.0
current -> 1.0.0
```

## Check first, unpack second

`lab/ferry/crate.py` reads the whole crate into memory and checks it before anything is written to disk:

```python
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
```

The seal is checked first: if the manifest cannot be trusted, neither can the hashes in it. Then every file must be listed, and every listed file must be there and match. Before all that, `read()` refuses any path that tries to climb out of the release folder, such as `../../etc/cron.d/evil`. That trick is called "tar slip", and it is why you never call `extractall` on a crate you have not checked.

## Run it on the island

```bash
uv run python -m ferry run --selftest
```

`ferry run` starts the current release from `island/releases/`, with `PARROT_OFFLINE=1`, behind the gap guard. It also starts Python with `-S`, which hides the packages installed on your laptop, because the island has none of them:

```text
island: running 1.0.0 with PARROT_OFFLINE=1, behind the gap guard
Traceback (most recent call last):
  ...
  File ".../lab/island/releases/1.0.0/parrot/__main__.py", line 9, in <module>
    from rich.console import Console
ModuleNotFoundError: No module named 'rich'
```

The crate is sealed, checked and landed, and the app still does not start. Parrot needs a package from PyPI, and the island has no PyPI. Chapter 05 fixes that.

## Check it works

- Both pirate crates are rejected and nothing is unpacked.
- The honest crate lands in `island/releases/1.0.0`, and `run` fails on the missing `rich`.

## Exercise

Pirates could also make a crate enormous, to fill the island's disk. Add a check to `read()` in `lab/ferry/crate.py` that rejects a crate larger than 50 MB before reading it. Test it by lowering the limit to 10 KB for a moment.

### More to try

- Run `uv run python -m ferry land` again with the honest crate. Why does it refuse, and why is that a good rule?
- Who checks the crate's `sha256` against the one you announced? Make the harbour master do it: add an `--expect HASH` option to `land`.
