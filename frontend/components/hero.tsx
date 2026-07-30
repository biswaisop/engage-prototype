'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Phone } from 'lucide-react'

const container = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.1, delayChildren: 0.1 },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] as const },
  },
}

const stats = [
  { value: '24/7', label: 'Always answering' },
  { value: '<1 day', label: 'Time to go live' },
  { value: '30+', label: 'Languages spoken' },
]

export function Hero() {
  return (
    <section className="relative flex min-h-screen items-center px-5 pt-32 pb-16 sm:px-8">
      <div className="mx-auto w-full max-w-6xl">
        <motion.div variants={container} initial="hidden" animate="show">
          <motion.span
            variants={item}
            className="inline-flex items-center gap-2 font-mono text-xs uppercase tracking-[0.28em] text-gold"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-gold shadow-[0_0_8px_var(--gold)]" />
            The AI receptionist for modern hospitality
          </motion.span>

          <div className="mt-8 grid gap-10 lg:grid-cols-12 lg:items-end">
            <motion.h1
              variants={item}
              className="col-span-12 text-balance font-serif text-4xl leading-[1.04] tracking-tight text-foreground sm:text-6xl lg:col-span-8 lg:text-[4.5rem]"
            >
              An AI front desk that never{' '}
              <span className="text-gradient-gold">clocks out</span>.
            </motion.h1>

            <motion.p
              variants={item}
              className="col-span-12 max-w-md text-pretty leading-relaxed text-muted-foreground lg:col-span-4"
            >
              Front Desk AI answers guest questions, handles requests, and
              quietly escalates to your team only when it matters — across every
              property you run.
            </motion.p>
          </div>

          <motion.div
            variants={item}
            className="mt-10 flex flex-col gap-3 sm:flex-row"
          >
            <Link
              href="/signup"
              className="group inline-flex items-center justify-center gap-2 rounded-full bg-gold px-7 py-3.5 text-sm font-medium text-gold-foreground transition-all duration-300 hover:scale-[1.03] hover:glow-gold"
            >
              Try Now
              <ArrowRight className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
            </Link>
            <Link
              href="#schedule"
              className="inline-flex items-center justify-center gap-2 rounded-full glass px-7 py-3.5 text-sm font-medium text-foreground transition-all duration-300 hover:border-gold/40 hover:bg-foreground/[0.07]"
            >
              <Phone className="h-4 w-4 text-gold" />
              Schedule a Call
            </Link>
          </motion.div>

          {/* editorial metric strip */}
          <motion.dl
            variants={item}
            className="mt-16 grid grid-cols-1 gap-px overflow-hidden border-y border-border sm:grid-cols-3"
          >
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="flex items-baseline gap-3 py-6 sm:flex-col sm:gap-1 sm:px-6 sm:first:pl-0"
              >
                <dt className="order-2 text-xs uppercase tracking-[0.18em] text-muted-foreground sm:order-1">
                  {stat.label}
                </dt>
                <dd className="order-1 font-serif text-3xl text-foreground sm:order-2 sm:text-4xl">
                  {stat.value}
                </dd>
              </div>
            ))}
          </motion.dl>
        </motion.div>
      </div>
    </section>
  )
}
