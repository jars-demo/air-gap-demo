# Bring your dependencies

> The island has no PyPI. Everything your app imports must cross the gap with it, down to the dependencies of your dependencies, pinned and hashed.

**Time:** 15 minutes

## Goal

Turn the lockfile into a list of exact, hashed packages, download them as wheels on the mainland, carry them in the crate, and see Parrot start on the island.

## You asked for one, you ship four

Parrot asks for one package, `rich`, in `lab/pyproject.toml`. uv's lockfile knows the rest. Export it as a pip requirements file with hashes:

```bash
uv export --format requirements-txt --no-header --no-dev --output-file dock/requirements.txt
```

```text
markdown-it-py==4.2.0 \
    --hash=sha256:04a21681d6fbb623de53f6f364d352309d4094dd4194040a10fd51833e418d49 \
    --hash=sha256:9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a
    # via rich
mdurl==0.1.2 \
...
```

Four packages, each with an exact version and the hashes of its files. `rich` needs `markdown-it-py` and `pygments`, and `markdown-it-py` needs `mdurl`. Forget one and the island finds out at startup.

## Download the wheels on the mainland

```bash
uvx pip@25.2 download --require-hashes --only-binary=:all: --no-deps -r dock/requirements.txt -d dock/wheels
```

```text
Saved .../lab/dock/wheels/markdown_it_py-4.2.0-py3-none-any.whl
Saved .../lab/dock/wheels/mdurl-0.1.2-py3-none-any.whl
Saved .../lab/dock/wheels/pygments-2.21.0-py3-none-any.whl
Saved .../lab/dock/wheels/rich-14.1.0-py3-none-any.whl
Successfully downloaded markdown-it-py mdurl pygments rich
```

What each flag is for:

| Flag                  | Why                                                                     |
| --------------------- | ----------------------------------------------------------------------- |
| `--require-hashes`    | refuse any file whose hash is not in the list                           |
| `--only-binary=:all:` | wheels only: no source builds, which would need compilers on the island |
| `--no-deps`           | the list is already complete; do not resolve again                      |
| `pip@25.2`            | an exact pip version, so this step is repeatable too                    |

## Mind the platform

All four wheels end in `py3-none-any`: pure Python, any machine. Packages with compiled code, like `pydantic-core` or `numpy`, have one wheel per platform, such as `cp313-cp313-manylinux_2_28_x86_64`. If your laptop is a Mac and the island runs Linux, download for the island, not for yourself:

```bash
uvx pip@25.2 download --only-binary=:all: --platform manylinux_2_28_x86_64 --python-version 3.13 -d dock/wheels-linux numpy==2.3.3
```

`ferry land` only unpacks pure-Python wheels, and refuses the others. For real projects, install on the island with a real installer, pointed at the wheels and never at the internet:

```bash
uv pip install --offline --no-index --find-links wheels -r requirements.txt
```

## Ship 1.0.1

Release 1.0.0 has already landed, and releases never change. Bump the version in `lab/parrot/__init__.py`:

```python
__version__ = "1.0.1"
```

Then pack with the wheels, send, land and run:

```bash
uv run python -m ferry pack --wheels dock/wheels
uv run python -m ferry send
uv run python -m ferry land
uv run python -m ferry run --selftest
```

```text
packed dock/parrot-1.0.1.crate  16 files, 1,628,160 bytes
...
  files    16 of 16 match the manifest
  landed   island/releases/1.0.1
current -> 1.0.1
island: running 1.0.1 with PARROT_OFFLINE=1, behind the gap guard
parrot 1.0.1 from .../air-gap-demo/lab/island/releases/1.0.1/parrot
ready in 0.0 s on http://127.0.0.1:8600  offline=True
selftest: parrot says "Who's a pretty deploy?"
gap guard: nothing tried to leave
```

Parrot runs on the island, with its own copy of `rich` from `island/releases/1.0.1/site`. The crate grew from 30 KB to 1.6 MB. Real apps carry hundreds of megabytes, which is why teams with islands care about lean dependencies.

## A wheel is a zip

How does `ferry land` install the wheels? From `lab/ferry/island.py`:

```python
    for data in wheels.values():
        # A pure-Python wheel is a zip laid out like site-packages: unzipping is installing.
        zipfile.ZipFile(io.BytesIO(data)).extractall(release / "site")
```

`ferry run` then puts `site` on the path. Installers do more (scripts, compiled bytecode, records), but this is the heart of it.

## Check it works

- `dock/wheels` holds four wheels, and every one of them is in `dock/requirements.txt` with a hash.
- `ferry run --selftest` prints a squawk and "nothing tried to leave".

## Exercise

Delete `dock/wheels/mdurl-0.1.2-py3-none-any.whl`, bump the version to 1.0.2, then pack, send, land and run. The crate is sealed and valid, and the app still breaks. Add a check to `ferry pack` that refuses to pack unless every package in `dock/requirements.txt` has a wheel. Download the wheel again when you are done.

### More to try

- Open `dock/requirements.txt` and follow the `# via` comments. Draw the tree.
- Which packages in your own project have no pure-Python wheel? `uv tree` is a good start.
