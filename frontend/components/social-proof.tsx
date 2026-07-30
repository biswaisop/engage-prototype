'use client'

import { Reveal } from '@/components/reveal'

const logos = [
  'The Marlowe',
  'Aurora Bay',
  'Maison Vela',
  'Cedar & Stone',
  'Halcyon House',
]

export function SocialProof() {
  return (
    <section className="relative px-5 py-24 sm:px-8 sm:py-28">
      <div className="mx-auto max-w-4xl">
        <Reveal>
          <figure className="rounded-3xl glass-strong px-6 py-12 text-center sm:px-14 sm:py-16">
            <div className="mb-6 flex justify-center gap-1 text-gold" aria-hidden="true">
              {Array.from({ length: 5 }).map((_, i) => (
                <span key={i} className="text-lg">
                  ★
                </span>
              ))}
            </div>
            <blockquote className="text-balance font-serif text-2xl leading-snug text-foreground sm:text-3xl">
              “During our pilot, Front Desk AI handled the overwhelming majority
              of after-hours guest questions on its own — and knew exactly when
              to wake someone up. It feels like adding a night manager who never
              sleeps.”
            </blockquote>
            <figcaption className="mt-8 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">
                General Manager
              </span>{' '}
              · Pilot boutique property
            </figcaption>
          </figure>
        </Reveal>

        <Reveal delay={0.1}>
          <p className="mt-14 text-center text-xs uppercase tracking-[0.25em] text-muted-foreground/70">
            Piloting with independent hotels &amp; groups
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-x-10 gap-y-4">
            {logos.map((name) => (
              <span
                key={name}
                className="font-serif text-lg text-muted-foreground/50 transition-colors duration-300 hover:text-muted-foreground"
              >
                {name}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  )
}
