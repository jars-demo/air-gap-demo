import type { Metadata, Viewport } from 'next'
import { Bricolage_Grotesque, DM_Mono } from 'next/font/google'

import { Shell } from '@/components/Shell'

import './globals.css'

const sans = Bricolage_Grotesque({
  variable: '--font-face-sans',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
})
const mono = DM_Mono({
  variable: '--font-face-mono',
  subsets: ['latin'],
  weight: ['400', '500'],
})

export const metadata: Metadata = {
  title: { default: 'Ship it to the island', template: '%s · Ship it to the island' },
  description:
    'A playful, hands-on workshop on air-gapped deploys: catch the calls an app makes home, pack a sealed reproducible crate, beat the pirates, carry the dependencies, run in a container with no network, and roll back.',
}

export const viewport: Viewport = { themeColor: '#fffbf3' }

export default function RootLayout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <a
          href="#main"
          className="sr-only bg-ink px-4 py-2 text-canvas focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50"
        >
          Skip to content
        </a>
        <Shell>{children}</Shell>
      </body>
    </html>
  )
}
