# Ship it to the island

A hands-on workshop on air-gapped deploys. Ship **Parrot**, a tiny web app, into a network with no internet: catch the calls it makes home, pack it into a sealed crate that builds the same every time, ferry it across, beat the pirates, bring its dependencies, run it in a container with no network, and roll it back.

**Workshop site:** [airgap.jishanahmed.in](https://airgap.jishanahmed.in)

## Quick start

You need [uv](https://docs.astral.sh/uv/) and git. uv installs Python for you. Docker is needed only for chapter 06.

```bash
git clone https://github.com/jars-demo/air-gap-demo.git
cd air-gap-demo/lab
uv sync
uv run python -m ferry guard parrot --selftest
```

You will see Parrot try to call home twice, and the gap guard block it.

## The cast

| In this lab   | What it is                                                   | In real life                                |
| ------------- | ------------------------------------------------------------ | ------------------------------------------- |
| `lab/parrot/` | the app you ship: one page, one API, one dependency (`rich`) | your product                                |
| `lab/ferry/`  | the deploy tool, standard library only                       | your release pipeline                       |
| `lab/dock/`   | the mainland: crates, wheels and the seal key                | CI and build machines, with internet        |
| `lab/island/` | the other side: inbox, releases, and a `current` pointer     | the air-gapped VPC                          |
| the gap guard | an audit hook that blocks every outbound connection          | an egress firewall with nothing allowed out |
| pirates       | `ferry send --pirates` changes a file on the way             | corruption, tampering                       |

## Commands

| Command                                   | What it does                                                         |
| ----------------------------------------- | -------------------------------------------------------------------- |
| `uv run python -m ferry guard parrot`     | run Parrot with every outbound call blocked (`--drop 3` waits first) |
| `uv run python -m ferry scan`             | list every URL in Parrot that points off the machine                 |
| `uv run python -m ferry pack [--wheels]`  | seal Parrot, and its wheels, into a reproducible crate               |
| `uv run python -m ferry send [--pirates]` | ferry the newest crate to the island                                 |
| `uv run python -m ferry land`             | check the seal and every hash, then unpack as a release              |
| `uv run python -m ferry run`              | run the current release offline, guarded, with no laptop packages    |
| `uv run python -m ferry rollback`         | point the island at the previous release (`use VERSION` for any)     |
| `uv run python -m ferry reset`            | empty the dock and the island, to start again                        |

## The workshop

| #   | Chapter                                                                        | You learn                                               |
| --- | ------------------------------------------------------------------------------ | ------------------------------------------------------- |
| 01  | [Welcome to the island](workshop/01-welcome-to-the-island.md)                  | what air-gapped means in a VPC; the gap guard           |
| 02  | [Catch the phone-homes](workshop/02-catch-the-phone-homes.md)                  | silent calls, dropped packets, an offline switch, scans |
| 03  | [Pack the crate](workshop/03-pack-the-crate.md)                                | manifests, seals, reproducible archives                 |
| 04  | [Cross the gap](workshop/04-cross-the-gap.md)                                  | tamper checks, tar slip, check before you unpack        |
| 05  | [Bring your dependencies](workshop/05-bring-your-dependencies.md)              | lockfiles, hashed wheels, platform tags                 |
| 06  | [The real gap, in Docker](workshop/06-the-real-gap.md)                         | `--network none`, `docker save` and `docker load`       |
| 07  | [Updates, rollback and the VPC checklist](workshop/07-updates-and-rollback.md) | immutable releases, rollback, what a VPC needs          |

## Layout

```text
lab/parrot/       the app to ship, with three ways of calling home
lab/ferry/        guard, scan, crate (pack and inspect), island (land, rollback), CLI
workshop/         the chapters, in Markdown
frontend/         the workshop site (Next.js), which renders workshop/
```

Parrot only ever calls `.example` hosts, which are reserved names that never resolve, so the lab sends nothing to a real server. The seal is an HMAC with a shared key, which is right for learning and wrong for production: sign real releases with a private key and verify with a public one (minisign, GPG or cosign).

## Run the site locally

```bash
cd frontend
npm ci
npm run dev
```

## License

[MIT](LICENSE)
