import Link from 'next/link'

import { CopyButton } from '@/components/CopyButton'
import { REPO_URL } from '@/components/Shell'
import { CHAPTERS } from '@/lib/workshop'

// Real output from the lab, trimmed to the lines that tell the story.
const RUN = [
  { cmd: 'ferry guard parrot --selftest' },
  { out: 'BLOCKED  telemetry.parrot.example:443', tone: 'bad' },
  { out: 'BLOCKED  updates.parrot.example:443', tone: 'bad' },
  { cmd: 'ferry send --pirates && ferry land' },
  { out: 'REJECTED parrot/server.py does not match the manifest', tone: 'bad' },
  { cmd: 'ferry send && ferry land' },
  { out: 'seal ok, 16 of 16 files match, current -> 1.0.1', tone: 'good' },
  { cmd: 'ferry run --selftest' },
  { out: 'parrot says "Who\'s a pretty deploy?"', tone: 'good' },
  { out: 'gap guard: nothing tried to leave', tone: 'good' },
]

const PARTS = [
  ['The app', 'lab/parrot/', 'A notice board that calls home three ways.'],
  ['The guard', 'lab/ferry/guard.py', 'Blocks every call that would leave.'],
  ['The crate', 'lab/ferry/crate.py', 'Sealed, hashed, the same bytes every time.'],
  ['The island', 'lab/ferry/island.py', 'Releases that never change, and rollback.'],
]

const TOPICS = [
  'Air-gapped VPC',
  'Egress',
  'Reproducible builds',
  'Signing',
  'Hashed wheels',
  'docker save',
  'Rollback',
]

const QUICKSTART = `git clone https://github.com/jars-demo/air-gap-demo.git
cd air-gap-demo/lab
uv sync
uv run python -m ferry guard parrot --selftest`

export default function Home() {
  const minutes = CHAPTERS.reduce((sum, chapter) => sum + chapter.minutes, 0)

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-20 px-4 pt-16 pb-24 sm:pt-24">
      <section className="grid items-start gap-12 lg:grid-cols-[1.05fr_1fr]">
        <div className="flex min-w-0 flex-col gap-6">
          <p className="font-mono text-[12px] tracking-wider text-muted uppercase">
            Deploy workshop · {CHAPTERS.length} chapters · {minutes} minutes
          </p>
          <h1 className="text-[2.75rem] leading-[1.05] font-bold tracking-[-0.035em] text-balance sm:text-[3.5rem]">
            Ship it to the island.
          </h1>
          <p className="max-w-xl text-[18px] leading-relaxed text-ink-2">
            Your customer runs everything in a network with no internet. Get Parrot there: catch the
            calls it makes home, seal it in a crate, beat the pirates on the ferry, bring its
            dependencies, run it with no network at all, and roll it back.
          </p>
          <ul className="flex flex-wrap gap-2" aria-label="Topics">
            {TOPICS.map((topic) => (
              <li
                key={topic}
                className="rounded-full bg-accent-wash px-3 py-1 text-[13px] font-medium text-accent-strong"
              >
                {topic}
              </li>
            ))}
          </ul>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/workshop/01-welcome-to-the-island"
              className="inline-flex h-11 items-center rounded-xl bg-accent px-5 text-[15px] font-semibold text-white hover:bg-accent-strong"
            >
              Start the workshop
            </Link>
            <a
              href={REPO_URL}
              className="inline-flex h-11 items-center rounded-xl border border-line-strong px-5 text-[15px] font-medium hover:bg-surface"
            >
              View the code
            </a>
          </div>
        </div>

        <figure className="code min-w-0 overflow-hidden rounded-2xl">
          <figcaption className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-2.5 text-[12px] text-[#9db4c0]">
            <span>mainland to island</span>
            <span>real output, trimmed</span>
          </figcaption>
          <div className="overflow-x-auto px-4 py-4 text-[12.5px] leading-[1.75]">
            {RUN.map((line, index) =>
              line.cmd ? (
                <div key={index} className="mt-2 whitespace-pre first:mt-0">
                  <span className="text-[#fcd34d]">$ </span>
                  {line.cmd}
                </div>
              ) : (
                <div
                  key={index}
                  className={`whitespace-pre pl-4 ${line.tone === 'bad' ? 'text-[#fca5a5]' : 'text-[#7dd3fc]'}`}
                >
                  {line.out}
                </div>
              ),
            )}
          </div>
        </figure>
      </section>

      <section aria-labelledby="parts" className="flex flex-col gap-6">
        <h2 id="parts" className="text-[1.6rem] font-bold tracking-[-0.02em]">
          What you run and read
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {PARTS.map(([name, file, about]) => (
            <div
              key={name}
              className="flex flex-col gap-2 rounded-2xl border border-line border-t-4 border-t-accent p-5"
            >
              <span className="text-[15px] font-semibold">{name}</span>
              <code className="font-mono text-[12px] break-all text-accent">{file}</code>
              <span className="text-[14px] text-ink-2">{about}</span>
            </div>
          ))}
        </div>
      </section>

      <section aria-labelledby="chapters" className="grid gap-10 lg:grid-cols-[1fr_1.3fr]">
        <div className="flex flex-col gap-3">
          <h2 id="chapters" className="text-[1.6rem] font-bold tracking-[-0.02em]">
            {CHAPTERS.length} short chapters
          </h2>
          <p className="text-[15px] leading-relaxed text-ink-2">
            Each one is a few minutes of reading, one thing to run or break, and an exercise. By the
            end you know what an island customer will ask, and you have an answer for each.
          </p>
        </div>
        <ol className="overflow-hidden rounded-2xl border border-line">
          {CHAPTERS.map((chapter) => (
            <li key={chapter.slug} className="border-b border-line last:border-b-0">
              <Link
                href={`/workshop/${chapter.slug}`}
                className="flex items-baseline gap-4 px-4 py-3.5 hover:bg-surface"
              >
                <span className="w-7 shrink-0 font-mono text-[13px] text-accent">
                  {chapter.number}
                </span>
                <span className="min-w-0 flex-1 text-[15px] font-medium">{chapter.title}</span>
                <span className="shrink-0 font-mono text-[12px] text-muted">
                  {chapter.minutes} min
                </span>
              </Link>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="start" className="flex flex-col gap-4">
        <h2 id="start" className="text-[1.6rem] font-bold tracking-[-0.02em]">
          Run it in a minute
        </h2>
        <p className="text-[15px] text-ink-2">
          You need{' '}
          <a href="https://docs.astral.sh/uv/" className="text-accent underline underline-offset-4">
            uv
          </a>{' '}
          and git. You will see Parrot try to call home, and the guard stop it. Docker is only
          needed for chapter 06.
        </p>
        <div className="code relative max-w-2xl overflow-x-auto rounded-2xl px-4 pt-10 pb-4 text-[13px] leading-relaxed">
          <div className="absolute top-2 right-2">
            <CopyButton text={QUICKSTART} />
          </div>
          <pre>{QUICKSTART}</pre>
        </div>
      </section>
    </div>
  )
}
