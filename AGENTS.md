# AGENTS.md

Guidance for AI coding agents and developers. Humans: start with [README.md](README.md).

## What this is

A short workshop, "Ship it to the island": deploy a small app into a network with no internet.
The lab in `lab/` and the chapters in `workshop/` are the product; `frontend/` is the site.

## Map

```text
lab/parrot/             the app to ship; telemetry, update check and crash reporter call home
lab/ferry/guard.py      audit hook that blocks non-loopback DNS lookups and connections
lab/ferry/scan.py       static scan for outbound URLs, split into code and browser
lab/ferry/crate.py      reproducible tar, MANIFEST.json, HMAC SEAL, inspect() before unpack
lab/ferry/island.py     land a crate as an immutable release, current pointer, rollback
lab/ferry/__main__.py   CLI: guard, scan, pack, send, land, run, use, releases, rollback, reset
workshop/NN-slug.md     chapters; code and output quoted from lab/ must match a real run
frontend/               Next.js site; reads ../workshop at build time
```

## Commands

```bash
cd lab && uv sync && uv run python -m ferry guard parrot --selftest
cd frontend && npm ci && npm run verify
```

## Rules

1. **ferry uses the standard library only.** Parrot has one dependency, `rich`, on purpose: it
   is what chapter 05 carries across.
2. **The phone-homes are the exercise.** Do not remove the telemetry, update check, crash
   reporter or CDN links from Parrot, and keep `crash.py` without the offline switch.
3. **Never contact a real host.** Parrot only uses `.example` names. Servers bind to 127.0.0.1.
4. **Chapters quote real code and real output.** Re-run the commands after changing `lab/`.
   A unit test checks the code quoted in chapters 03, 04 and 05 and every file path mentioned.
5. **Writing style.** Plain English, short sentences, no em dashes. Conventional Commits, no AI
   attribution trailers.
