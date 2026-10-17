# Pack the crate

> Whatever crosses the gap must be one file, complete, and checkable on the other side. Pack Parrot into a sealed crate that comes out byte-for-byte the same every time.

**Time:** 15 minutes

## Goal

Pack a release into a single file with a manifest of hashes and a seal, and see why reproducible packing matters when the only link to the island is a person reading out a hash.

## Pack it

```bash
uv run python -m ferry pack
```

```text
new seal key in dock/seal.key, and a copy handed to the island (once, in person)
packed dock/parrot-1.0.0.crate  12 files, 30,720 bytes
sha256 4fed1c4d54357115a1fd08311f6bd9eb19d7e7cbe8fac2d17b0eee2a96024cb3
```

The first pack makes a seal key and puts a copy on the island. In real life that happens once, in person, before any software crosses.

Now pack again, without changing anything:

```bash
uv run python -m ferry pack
```

The `sha256` line is the same. Your hash differs from the one above because your seal key is your own, but your two packs match each other.

## Look inside

A crate is a plain tar file, so `tar` can list it. It ships with macOS, Linux and Windows 10 or later:

```bash
tar -tvf dock/parrot-1.0.0.crate
```

```text
-rw-r--r-- 0/0            1208 1970-01-01 00:00 MANIFEST.json
-rw-r--r-- 0/0              65 1970-01-01 00:00 SEAL
-rw-r--r-- 0/0             122 1970-01-01 00:00 parrot/__init__.py
-rw-r--r-- 0/0            1680 1970-01-01 00:00 parrot/__main__.py
...
```

Three things to notice:

- **MANIFEST.json** lists the SHA-256 of every file. The island checks each one.
- **SEAL** is an HMAC of the manifest, made with the seal key. Change the manifest and the seal no longer fits.
- **Every file has owner 0 and the time 1970-01-01**, the zero timestamp (`tar` shows it in your time zone). That is what makes the crate reproducible.

## Why the same bytes every time

Normal archives record who packed them and when. Pack twice and you get two different hashes, so nobody can tell a rebuilt crate from a tampered one. `lab/ferry/crate.py` fixes every field that could vary:

```python
def write(out: Path, entries: dict[str, bytes]) -> None:
    """Write a tar with fixed times, owners and order, so it is byte-for-byte reproducible."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out, "w", format=tarfile.PAX_FORMAT) as tar:
        for name, data in entries.items():
            info = tarfile.TarInfo(name)
            info.size, info.mtime, info.mode = len(data), 0, 0o644
            tar.addfile(info, io.BytesIO(data))
```

The files go in sorted order too. Now the hash is a fingerprint of the content alone, and you can announce it over a separate channel: a phone call, a ticket, a printed change request. The island compares it before it trusts anything.

## About the seal

An HMAC uses one shared key: whoever can check a seal can also make one. That is fine for learning, and wrong for real releases. Real setups sign with a private key that never leaves the build system, and ship only the public key to the island, using tools like minisign, GPG or cosign. With cosign, verify offline against a key you ship. The public transparency log is on the internet, and the island cannot reach it.

## Check it works

- Two packs in a row print the same `sha256`.
- `tar -tvf` shows `MANIFEST.json`, `SEAL` and the twelve Parrot files.

## Exercise

Change one phrase in `lab/parrot/phrases.json` and pack. The hash changes. Undo your change, for example with `git checkout parrot/phrases.json`, and pack again. Do you get the first hash back? Explain why that matters to the person on the island.

### More to try

- Run `tar -xOf dock/parrot-1.0.0.crate MANIFEST.json` and find the hash of `parrot/phrases.json`. Hash the file yourself with `sha256sum` or `Get-FileHash` and compare.
- `gzip` stores a timestamp in its header, which breaks reproducible builds unless you pass `-n`. Find the same problem in a tool you use, and the fix (search for `SOURCE_DATE_EPOCH`).
