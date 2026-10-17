# The real gap, in Docker

> So far the gap was a Python hook. Now make a real one: a container with no network at all. Then carry the container image itself across.

**Time:** 15 minutes

## Goal

Prove the release runs where there is truly no network, and move a container image across the gap with `docker save` and `docker load`.

## A container with no network

`docker run --network none` gives a container only the loopback interface. There is no route anywhere: a real air gap on your laptop. Use an exact image version:

```bash
docker run --rm --network none python:3.13.15-slim python -c "import urllib.request; urllib.request.urlopen('https://pypi.org', timeout=5)"
```

```text
urllib.error.URLError: <urlopen error [Errno -3] Temporary failure in name resolution>
```

Not even DNS works. Now try what everyone tries first:

```bash
docker run --rm --network none python:3.13.15-slim pip install --retries 0 --timeout 2 rich
```

```text
ERROR: Could not find a version that satisfies the requirement rich (from versions: none)
ERROR: No matching distribution found for rich
```

That is the island in two lines.

## Run the release inside it

Mount the island folder read-only and run the release you landed in chapter 05:

```bash
docker run --rm --network none -v "$PWD/island:/island:ro" -w /island/releases/1.0.1 -e PARROT_OFFLINE=1 -e PYTHONPATH=site python:3.13.15-slim python -m parrot --selftest
```

```text
parrot 1.0.1 from /island/releases/1.0.1/parrot
ready in 0.0 s on http://127.0.0.1:8600  offline=True
selftest: parrot says 'I only talk to localhost now.'
```

In PowerShell, write `${PWD}` instead of `$PWD`. In Git Bash on Windows, put `MSYS_NO_PATHCONV=1` in front of `docker` so the `/island` paths stay as they are.

No laptop packages, no guard, no network: the crate carried everything Parrot needs. The container also has a different operating system from your laptop, and the pure-Python wheels did not care.

## Carry the image across

The island cannot pull images either. Save the image to a file on the mainland:

```bash
docker save python:3.13.15-slim -o dock/python-3.13.15-slim.tar
```

The file is about 122 MB. Hash it, announce the hash as you did for the crate, and send it. On the island, load it:

```bash
docker load -i dock/python-3.13.15-slim.tar
```

```text
Loaded image: python:3.13.15-slim
```

One surprise: after `docker load`, the image no longer knows its registry digest, the `python@sha256:...` name you would pin to. Check the tar file's hash before loading, then push the image to the island's own registry and pin to the digest that registry gives it. For files without Docker, `skopeo copy docker-archive:... docker://registry.internal/...` does the same job.

## Check it works

- Inside `--network none`, `urlopen` and `pip install` both fail.
- Parrot 1.0.1 starts and squawks inside the same container.

## Exercise

Run the container again without `-e PARROT_OFFLINE=1`. Parrot still starts in 0.0 s. Why is it fast here, but slow behind `ferry guard --drop 3`? Write one sentence about what this means for testing island behaviour on a laptop.

### More to try

- Add `--read-only --cap-drop ALL --user 65534` to the `docker run` command. Does Parrot still work? Island security teams will ask for all three.
- Write the `Dockerfile` for a Parrot image that installs from `wheels/` with `pip install --no-index --find-links`, so it builds with no network.
