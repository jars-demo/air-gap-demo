import Link from 'next/link'

import { BackToTop } from './BackToTop'

export const REPO_URL = 'https://github.com/jars-demo/air-gap-demo'

export function Mark({ size = 22 }: { size?: number }) {
  // The sun over the sea: the island is out there.
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <rect x="1" y="1" width="22" height="22" rx="6" fill="#0b6b9a" />
      <circle cx="16" cy="8.5" r="3" fill="#fcd34d" />
      <path
        d="M4 15.5c1.5 0 2.3-1.2 4-1.2s2.5 1.2 4 1.2 2.3-1.2 4-1.2 2.5 1.2 4 1.2"
        stroke="#ffffff"
        strokeWidth="1.8"
        fill="none"
        strokeLinecap="round"
      />
      <path
        d="M4 19.2c1.5 0 2.3-1.2 4-1.2s2.5 1.2 4 1.2 2.3-1.2 4-1.2 2.5 1.2 4 1.2"
        stroke="#ffffff"
        strokeOpacity="0.55"
        strokeWidth="1.8"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  )
}

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <header className="border-b border-line">
        <nav
          aria-label="Main"
          className="mx-auto flex h-14 max-w-5xl items-center justify-between gap-4 px-4"
        >
          <Link href="/" className="inline-flex items-center gap-2.5 text-[15px] font-semibold">
            <Mark />
            Ship it to the island
          </Link>
          <ul className="flex items-center gap-5 text-[14px] text-ink-2">
            <li>
              <Link href="/workshop" className="hover:text-ink">
                Workshop
              </Link>
            </li>
            <li>
              <a href={REPO_URL} className="hover:text-ink">
                GitHub
              </a>
            </li>
          </ul>
        </nav>
      </header>
      <main id="main" className="flex-1">
        {children}
      </main>
      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-5xl flex-col gap-2 px-4 py-6 text-[13px] text-muted sm:flex-row sm:justify-between">
          <span>Ship it to the island · MIT licensed</span>
          <a href={REPO_URL} className="hover:text-ink">
            GitHub
          </a>
        </div>
      </footer>
      <BackToTop />
    </>
  )
}
