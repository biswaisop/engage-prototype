'use client'

import { useState, type FormEvent } from 'react'
import { motion } from 'framer-motion'
import { CalendarDays, Check, Loader2 } from 'lucide-react'
import { Reveal } from '@/components/reveal'

export function ScheduleCall() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'done'>('idle')

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setStatus('loading')
    const data = Object.fromEntries(new FormData(e.currentTarget))
    // TODO: connect to CRM / scheduling API
    await new Promise((r) => setTimeout(r, 1200))
    console.log('[v0] Schedule a call request:', data)
    setStatus('done')
  }

  return (
    <section id="schedule" className="relative px-5 py-24 sm:px-8 sm:py-32">
      <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-2">
        <Reveal>
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-gold">
            Let&apos;s talk
          </p>
          <h2 className="mt-4 text-balance font-serif text-3xl tracking-tight text-foreground sm:text-5xl">
            See Front Desk AI on your own property.
          </h2>
          <p className="mt-5 max-w-md text-pretty leading-relaxed text-muted-foreground">
            Book a 20-minute walkthrough. We&apos;ll load your property details,
            show the widget answering real guest questions, and map an
            onboarding plan for your team.
          </p>

          {/* calendar embed placeholder */}
          <div className="mt-8 flex items-center gap-4 rounded-2xl glass p-5">
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gold/10 ring-1 ring-gold/20">
              <CalendarDays className="h-5 w-5 text-gold" />
            </span>
            <div>
              <p className="text-sm font-medium text-foreground">
                Prefer to pick a time?
              </p>
              <p className="text-sm text-muted-foreground">
                Calendar embed goes here — or use the form and we&apos;ll reach
                out.
              </p>
            </div>
          </div>
        </Reveal>

        <Reveal delay={0.12}>
          <div className="rounded-3xl glass-strong p-6 sm:p-8">
            {status === 'done' ? (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center py-16 text-center"
              >
                <span className="flex h-14 w-14 items-center justify-center rounded-full bg-gold/15 ring-1 ring-gold/30">
                  <Check className="h-6 w-6 text-gold" />
                </span>
                <h3 className="mt-5 font-serif text-2xl text-foreground">
                  Thank you
                </h3>
                <p className="mt-2 max-w-xs text-sm text-muted-foreground">
                  We&apos;ve received your request and will be in touch within
                  one business day.
                </p>
              </motion.div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <Field label="Full name" name="name" placeholder="Jordan Vance" />
                <Field
                  label="Work email"
                  name="email"
                  type="email"
                  placeholder="you@hotel.com"
                />
                <Field
                  label="Property name"
                  name="property"
                  placeholder="The Marlowe"
                />
                <div>
                  <label
                    htmlFor="message"
                    className="mb-1.5 block text-sm text-muted-foreground"
                  >
                    Message
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    rows={3}
                    placeholder="Tell us about your properties…"
                    className="w-full resize-none rounded-xl border border-input bg-foreground/[0.03] px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 transition-colors duration-300 focus:border-gold/50 focus:outline-none focus:ring-2 focus:ring-ring/40"
                  />
                </div>
                <button
                  type="submit"
                  disabled={status === 'loading'}
                  className="inline-flex w-full items-center justify-center gap-2 rounded-full bg-gold px-6 py-3.5 text-sm font-medium text-gold-foreground transition-all duration-300 hover:glow-gold disabled:opacity-70"
                >
                  {status === 'loading' ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Sending…
                    </>
                  ) : (
                    'Request a walkthrough'
                  )}
                </button>
              </form>
            )}
          </div>
        </Reveal>
      </div>
    </section>
  )
}

function Field({
  label,
  name,
  type = 'text',
  placeholder,
}: {
  label: string
  name: string
  type?: string
  placeholder?: string
}) {
  return (
    <div>
      <label
        htmlFor={name}
        className="mb-1.5 block text-sm text-muted-foreground"
      >
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        required
        placeholder={placeholder}
        className="w-full rounded-xl border border-input bg-foreground/[0.03] px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 transition-colors duration-300 focus:border-gold/50 focus:outline-none focus:ring-2 focus:ring-ring/40"
      />
    </div>
  )
}
