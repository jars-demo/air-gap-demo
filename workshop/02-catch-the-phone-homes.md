# Catch the phone-homes

> Apps call home in quiet ways. Find every one, at run time and by reading the code, and give the island an offline switch.

**Time:** 15 minutes

## Goal

Measure what a hidden call costs on the island, turn the calls off with one switch, and find the calls the guard cannot see.

## Silent calls cost seconds

Parrot's telemetry and update check swallow their errors, so they never break anything. On the mainland they fail fast. On an island they often do not: many firewalls drop packets instead of refusing them, so every call waits for its timeout.

`--drop 3` makes the guard wait three seconds before failing, like a firewall that drops:

```bash
uv run python -m ferry guard --drop 3 parrot --selftest
```

```text
  BLOCKED  telemetry.parrot.example:443  from parrot/telemetry.py:18
  BLOCKED  updates.parrot.example:443  from parrot/updates.py:15
parrot 1.0.0 from .../air-gap-demo/lab/parrot
ready in 6.0 s on http://127.0.0.1:8600  offline=False
```

Six seconds to start, from two calls nobody remembers writing. With longer timeouts, retries, or a health check that gives up after five seconds, this is how "it works everywhere except at the customer" begins.

## One switch for the island

Parrot reads `PARROT_OFFLINE` in `lab/parrot/config.py`, and telemetry and the update check skip their work when it is `1`:

```bash
PARROT_OFFLINE=1 uv run python -m ferry guard parrot --selftest
```

In PowerShell, set it first with `$env:PARROT_OFFLINE = "1"`, and clear it afterwards with `Remove-Item Env:PARROT_OFFLINE`.

```text
parrot 1.0.0 from .../air-gap-demo/lab/parrot
ready in 0.0 s on http://127.0.0.1:8600  offline=True
selftest: parrot says 'I only talk to localhost now.'
gap guard: nothing tried to leave
```

Clean. Or is it? The guard only sees code that runs. Ask for a mood Parrot does not have, so the error path runs:

```bash
PARROT_OFFLINE=1 uv run python -m ferry guard parrot --selftest --mood seasick
```

```text
parrot 1.0.0 from .../air-gap-demo/lab/parrot
ready in 0.0 s on http://127.0.0.1:8600  offline=True
  BLOCKED  errors.parrot.example:443  from parrot/crash.py:15
selftest: 500 parrot has no such mood
gap guard: 1 call tried to leave
```

The crash reporter has no offline switch. It only calls home when something goes wrong, which is exactly when nobody is watching.

## Read the code as well

`ferry scan` lists every URL in a folder that points off the machine:

```bash
uv run python -m ferry scan
```

```text
  code     errors.parrot.example        parrot/crash.py:9
  browser  fonts.parrot-cdn.example     parrot/static/index.html:7
  browser  cdn.parrot-cdn.example       parrot/static/index.html:9
  code     telemetry.parrot.example     parrot/telemetry.py:9
  code     updates.parrot.example       parrot/updates.py:8
5 outbound URLs. 2 load in the browser, where the guard can't see.
```

The two `browser` rows are the answer to chapter 01's exercise. A font and a script load from a CDN in the visitor's browser. On the island, the page loads without them, or hangs waiting for them.

The two tools work together. The guard proves what runs. The scan finds what could run. Neither is enough alone.

## Check it works

- `--drop 3` makes Parrot take about 6 seconds to start; `PARROT_OFFLINE=1` brings it back to 0.
- You found all five outbound URLs and know which two the guard cannot see.

## Exercise

Make Parrot fully island-safe:

1. In `lab/parrot/crash.py`, skip the report when `config.OFFLINE` is set. Run the `seasick` command again: the guard should say nothing tried to leave.
2. In `lab/parrot/static/index.html`, load the confetti from `/static/confetti.js`, which already ships with Parrot, and remove the font link. Run `ferry scan` again: only the three switched-off calls in Python should remain.

### More to try

- Flip the switch around: offline by default, online only when `PARROT_ONLINE=1`. Which default would your island customer prefer?
- Run `uv run python -m ferry scan path/to/your/project`. How many findings are real?
