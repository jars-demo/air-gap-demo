# Updates, rollback and the VPC checklist

> A ferry that comes once a week makes every release count. Ship an update, roll it back in a second, and leave with the list of what an air-gapped VPC needs.

**Time:** 15 minutes

## Goal

Ship 1.1.0, switch between releases without sending anything again, and know the pieces a real air-gapped VPC needs around your app.

## Ship 1.1.0

Give Parrot a new mood. In `lab/parrot/phrases.json`, add:

```json
  "pirate": ["Arr! Release 1.1.0 made it across."]
```

Remember the comma after the `sleepy` list. Then set `__version__ = "1.1.0"` in `lab/parrot/__init__.py`, and ship:

```bash
uv run python -m ferry pack --wheels dock/wheels
uv run python -m ferry send
uv run python -m ferry land
uv run python -m ferry run --selftest --mood pirate
```

```text
island: running 1.1.0 with PARROT_OFFLINE=1, behind the gap guard
parrot 1.1.0 from .../air-gap-demo/lab/island/releases/1.1.0/parrot
ready in 0.0 s on http://127.0.0.1:8600  offline=True
selftest: parrot says 'Arr! Release 1.1.0 made it across.'
gap guard: nothing tried to leave
```

## Roll back in a second

```bash
uv run python -m ferry releases
uv run python -m ferry rollback
uv run python -m ferry run --selftest --mood pirate
```

```text
    1.0.0
    1.0.1
  * 1.1.0
current -> 1.0.1  (was 1.1.0)
island: running 1.0.1 with PARROT_OFFLINE=1, behind the gap guard
parrot 1.0.1 from .../air-gap-demo/lab/island/releases/1.0.1/parrot
ready in 0.0 s on http://127.0.0.1:8600  offline=True
  BLOCKED  errors.parrot.example:443  from parrot/crash.py:15
selftest: 500 parrot has no such mood
gap guard: 1 call tried to leave
```

Two lessons in one output. First, rollback took no transfer at all: every release stays on the island, and `island/current` is a pointer that names one of them. Second, rolling back brings old bugs back: 1.0.1 has no `pirate` mood, so it hits its error path, and its crash reporter tries to call home. If you did the chapter 02 exercise, you will not see the `BLOCKED` line: your fix crossed with 1.0.1.

Roll forward again with `uv run python -m ferry use 1.1.0`.

## Why it is built this way

- **Releases never change.** Landing 1.0.1 twice is refused. What ran yesterday can run again tomorrow, byte for byte.
- **Switching is one small write.** Changing a pointer is quick and hard to get half done, unlike copying files over a running app.
- **Rollback is local.** The next ferry may be a week away, so the island must be able to undo a release on its own.

## The air-gapped VPC checklist

Parrot is ready. Around it, an air-gapped VPC needs these, and a customer's security review will ask about most of them:

| The app needs         | Inside a VPC with no internet                                                 |
| --------------------- | ----------------------------------------------------------------------------- |
| packages              | a private mirror (devpi, Nexus, Artifactory, AWS CodeArtifact)                |
| container images      | a private registry (Harbor; ECR needs `ecr.api`, `ecr.dkr` and S3 endpoints)  |
| cloud APIs            | VPC endpoints for each service it calls (S3, STS, KMS, Secrets Manager, logs) |
| DNS                   | private zones and an internal resolver                                        |
| time                  | an internal NTP source (on AWS, Amazon Time Sync at `169.254.169.123`)        |
| TLS                   | an internal certificate authority, and its bundle shipped with the app        |
| licences              | an offline licence file, never a licence server                               |
| telemetry and updates | off by default, behind one switch you can show the customer                   |
| logs and metrics      | kept inside; anything that leaves goes out through the same checks            |
| updates               | a release schedule, signed crates, and rollback that needs no ferry           |

## Check it works

- `ferry releases` lists three releases, and `rollback` and `use` move the star.
- On 1.0.1, the `pirate` mood fails with a 500, because that release does not have it.

## Exercise

Islands run out of disk. Add `ferry prune --keep 2`, which deletes all but the newest two releases and never the current one. Make it print what it would delete, and delete only with `--yes`.

### More to try

- Write the one-page runbook for the island operator: how to check a crate's hash, land it, check it, and roll back. Could someone follow it at 3 a.m.?
- Pick one row of the checklist your product cannot meet yet, and write down the smallest change that would let it.
