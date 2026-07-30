'use client'

import Link from 'next/link'
import { Check } from 'lucide-react'
import { Reveal } from '@/components/reveal'
import { cn } from '@/lib/utils'

const tiers = [
  {
    name: 'Starter',
    price: '$149',
    cadence: '/mo',
    description: 'For a single boutique property finding its feet.',
    features: [
      '1 property',
      'Website chat widget',
      'Up to 1,000 conversations / mo',
      'Email escalation',
      'Basic analytics',
    ],
    cta: 'Try Now',
    href: '/signup',
    highlighted: false,
  },
  {
    name: 'Growth',
    price: '$399',
    cadence: '/mo',
    description: 'For growing groups that need reach and control.',
    features: [
      'Up to 5 properties',
      'Website, WhatsApp & Telegram',
      'Up to 10,000 conversations / mo',
      'Smart staff escalation',
      'Full analytics dashboard',
      'Multilingual replies',
    ],
    cta: 'Start free trial',
    href: '/signup',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    cadence: '',
    description: 'For portfolios with bespoke needs and SLAs.',
    features: [
      'Unlimited properties',
      'All channels + custom integrations',
      'Unlimited conversations',
      'Dedicated success manager',
      'SSO, audit logs & SLA',
    ],
    cta: 'Schedule a Call',
    href: '#schedule',
    highlighted: false,
  },
]

export function Pricing() {
  return (
    <section id="pricing" className="relative px-5 py-24 sm:px-8 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <Reveal className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-gold">
            Pricing
          </p>
          <h2 className="mt-4 text-balance font-serif text-3xl tracking-tight text-foreground sm:text-5xl">
            Simple plans that scale with your properties.
          </h2>
        </Reveal>

        <div className="mt-14 grid gap-6 lg:grid-cols-3">
          {tiers.map((tier, i) => (
            <Reveal key={tier.name} delay={i * 0.1} className="h-full">
              <div
                className={cn(
                  'relative flex h-full flex-col rounded-3xl p-8 transition-all duration-500',
                  tier.highlighted
                    ? 'glass-strong border-gold/40 glow-gold'
                    : 'glass hover:-translate-y-1 hover:border-gold/20',
                )}
              >
                {tier.highlighted && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gold px-3 py-1 text-xs font-medium text-gold-foreground">
                    Most popular
                  </span>
                )}
                <h3 className="font-serif text-2xl text-foreground">
                  {tier.name}
                </h3>
                <p className="mt-2 min-h-10 text-sm leading-relaxed text-muted-foreground">
                  {tier.description}
                </p>
                <div className="mt-6 flex items-end gap-1">
                  <span className="font-serif text-4xl text-foreground">
                    {tier.price}
                  </span>
                  <span className="mb-1 text-sm text-muted-foreground">
                    {tier.cadence}
                  </span>
                </div>

                <ul className="mt-8 flex-1 space-y-3">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-gold" />
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={tier.href}
                  className={cn(
                    'mt-8 inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-medium transition-all duration-300',
                    tier.highlighted
                      ? 'bg-gold text-gold-foreground hover:scale-[1.03] hover:glow-gold'
                      : 'glass text-foreground hover:border-gold/40 hover:bg-foreground/[0.07]',
                  )}
                >
                  {tier.cta}
                </Link>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
