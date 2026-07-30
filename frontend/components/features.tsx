'use client'

import {
  Zap,
  Languages,
  ShieldCheck,
  MessagesSquare,
  Building2,
  LineChart,
} from 'lucide-react'
import { Reveal } from '@/components/reveal'

const features = [
  {
    icon: Zap,
    title: 'Instant responses',
    body: 'Guests get accurate answers in seconds, day or night — no hold music, no waiting.',
  },
  {
    icon: Languages,
    title: 'Multilingual',
    body: 'Reply fluently in your guests’ language, automatically detected in every conversation.',
  },
  {
    icon: ShieldCheck,
    title: 'Hallucination guardrails',
    body: 'Confidence thresholds and safe escalation mean it never invents policies or prices.',
  },
  {
    icon: MessagesSquare,
    title: 'Everywhere guests are',
    body: 'Website widget, WhatsApp, and Telegram — one brain across every channel.',
  },
  {
    icon: Building2,
    title: 'Multi-property',
    body: 'Manage one boutique or a hundred properties, each with its own knowledge base.',
  },
  {
    icon: LineChart,
    title: 'Analytics dashboard',
    body: 'See resolution rates, top questions, and escalation trends across your portfolio.',
  },
]

export function Features() {
  return (
    <section className="relative px-5 py-24 sm:px-8 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-gold">
            Capabilities
          </p>
          <h2 className="mt-4 text-balance font-serif text-3xl tracking-tight text-foreground sm:text-5xl">
            Everything a five-star front desk should be.
          </h2>
        </Reveal>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => {
            const Icon = feature.icon
            return (
              <Reveal key={feature.title} delay={(i % 3) * 0.1}>
                <div className="group h-full rounded-2xl glass p-7 transition-all duration-500 ease-out hover:-translate-y-1.5 hover:border-gold/30 hover:bg-foreground/[0.06]">
                  <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-gold/10 ring-1 ring-gold/20 transition-colors duration-500 group-hover:bg-gold/15">
                    <Icon className="h-5 w-5 text-gold" />
                  </span>
                  <h3 className="mt-5 font-serif text-xl text-foreground">
                    {feature.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {feature.body}
                  </p>
                </div>
              </Reveal>
            )
          })}
        </div>
      </div>
    </section>
  )
}
