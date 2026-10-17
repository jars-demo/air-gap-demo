# Welcome to the island

> Your customer runs everything in a network with no internet. Meet the app you have to get there, and the guard that makes your laptop behave like the island.

**Time:** 10 minutes

## Goal

Know what "air-gapped" means in a cloud VPC, run Parrot on the mainland, then run it again with every outbound call blocked and see what it was quietly doing.

## The island

Banks, hospitals, factories, ships and government teams often run software in an **air-gapped** network. In a cloud VPC that usually means private subnets with no internet gateway, no NAT gateway and no route out. Nothing inside can reach the internet, and nothing from the internet can reach in. New software arrives one way only: through an approved, checked transfer.

Your job today is to ship **Parrot**, a tiny notice board, to an island like that, and keep it running. The lab uses a few playful names. Here is what each one stands for:

| In this lab                       | In real life                                                               |
| --------------------------------- | -------------------------------------------------------------------------- |
| `lab/dock/`                       | your build machines and CI, which have internet                            |
| `ferry send`                      | the one approved way in: a transfer appliance, a data diode, a USB process |
| the seal                          | a signature on the release                                                 |
| `ferry land` (the harbour master) | the import check at the boundary                                           |
| `lab/island/`                     | the air-gapped VPC                                                         |
| the gap guard                     | an egress firewall, or security groups with no outbound rule               |

## Set up

You need [uv](https://docs.astral.sh/uv/) and git. Docker is needed only for chapter 06.

```bash
git clone https://github.com/jars-demo/air-gap-demo.git
cd air-gap-demo/lab
uv sync
```

Every command in this workshop runs from `lab/`.

## Run Parrot on the mainland

```bash
uv run python -m parrot
```

Open http://127.0.0.1:8600 and click the moods. Parrot works. Stop it with Ctrl+C.

## Run it behind the gap guard

`ferry guard` runs a Python module with every connection that would leave your machine blocked. Calls to `127.0.0.1` still work.

```bash
uv run python -m ferry guard parrot --selftest
```

```text
  BLOCKED  telemetry.parrot.example:443  from parrot/telemetry.py:18
  BLOCKED  updates.parrot.example:443  from parrot/updates.py:15
parrot 1.0.0 from .../air-gap-demo/lab/parrot
ready in 0.0 s on http://127.0.0.1:8600  offline=False
selftest: parrot says 'I only talk to localhost now.'
gap guard: 2 calls tried to leave
```

Parrot started and served, so nobody would notice anything on the mainland. But it tried to call home twice before it was even ready. `--selftest` asks for one squawk and stops, so you do not need Ctrl+C.

The guard is a Python audit hook, about 60 lines in `lab/ferry/guard.py`. Python raises an audit event before every DNS lookup and every connection, and the hook refuses the ones that leave the machine. The `.example` hosts in Parrot are reserved names that never resolve, so this lab never sends anything to a real server.

## Check it works

- Parrot runs on http://127.0.0.1:8600 without the guard.
- With the guard, you see two `BLOCKED` lines and Parrot still starts.

## Exercise

Run Parrot without the guard, open the page, and open your browser's developer tools on the Network tab. Reload. Which requests fail, and which file asked for them? Keep the answer: the guard cannot see these, and chapter 02 explains why.

### More to try

- Think of an app you ship. List everything it might contact at startup: telemetry, update checks, licence servers, feature flags, fonts, CDNs.
- Read `lab/ferry/guard.py`. Which two audit events does it listen for, and why both?
