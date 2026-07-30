'use client'

import { useState } from 'react'
import Image from 'next/image'
import { AnimatePresence, motion } from 'framer-motion'
import { Reveal } from '@/components/reveal'
import { SectionHeading } from '@/components/section-heading'
import { cn } from '@/lib/utils'

const tabs = [
  {
    id: 'widget',
    label: 'Guest Chat Widget',
    image: '/mockup-chat.png',
    alt: 'AI chat widget answering a guest question on a hotel website',
    caption:
      'A refined chat widget that lives on your site, answering guests instantly in their own language.',
  },
  {
    id: 'dashboard',
    label: 'Operations Dashboard',
    image: '/mockup-dashboard.png',
    alt: 'Front Desk AI dashboard showing conversation logs, escalation flags and a multi-property switcher',
    caption:
      'Conversation logs, escalation flags, and a multi-property switcher — the full picture at a glance.',
  },
] as const

export function ProductShowcase() {
  const [active, setActive] = useState<(typeof tabs)[number]['id']>('widget')
  const current = tabs.find((t) => t.id === active) ?? tabs[0]

  return (
    <section id="product" className="relative px-5 py-24 sm:px-8 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          index="01"
          label="The Product"
          title="Beautiful on the front. Powerful behind the desk."
          description="Two surfaces, one intelligence — a guest-facing widget and the console your team runs it from."
        />

        <div className="mt-14 grid gap-10 lg:grid-cols-12 lg:gap-12">
          {/* selector list */}
          <div className="lg:col-span-4">
            <Reveal className="flex flex-col">
              {tabs.map((tab, i) => {
                const isActive = tab.id === active
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActive(tab.id)}
                    className={cn(
                      'group relative border-t border-border py-6 text-left transition-colors duration-300 last:border-b',
                      isActive ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
                    )}
                  >
                    {isActive && (
                      <motion.span
                        layoutId="showcase-marker"
                        className="absolute left-0 top-0 h-full w-px bg-gold shadow-[0_0_8px_var(--gold)]"
                        transition={{ type: 'spring', stiffness: 400, damping: 34 }}
                      />
                    )}
                    <span className="flex items-center gap-3 pl-4">
                      <span className="font-mono text-xs tabular-nums text-gold">
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      <span className="font-serif text-xl">{tab.label}</span>
                    </span>
                    <AnimatePresence initial={false}>
                      {isActive && (
                        <motion.p
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                          className="overflow-hidden pl-11 pr-4 text-sm leading-relaxed"
                        >
                          <span className="block pt-3">{tab.caption}</span>
                        </motion.p>
                      )}
                    </AnimatePresence>
                  </button>
                )
              })}
            </Reveal>
          </div>

          {/* device */}
          <Reveal delay={0.1} className="lg:col-span-8">
            <div className="relative rounded-2xl glass-strong p-2 shadow-[0_30px_120px_-40px_rgba(0,0,0,0.9)] sm:p-3">
              <div className="flex items-center gap-1.5 px-3 py-2.5">
                <span className="h-2.5 w-2.5 rounded-full bg-foreground/20" />
                <span className="h-2.5 w-2.5 rounded-full bg-foreground/20" />
                <span className="h-2.5 w-2.5 rounded-full bg-foreground/20" />
              </div>
              <div className="relative aspect-[16/10] w-full overflow-hidden rounded-xl border border-border">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={current.id}
                    initial={{ opacity: 0, scale: 1.02 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.99 }}
                    transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                    className="absolute inset-0"
                  >
                    <Image
                      src={current.image || '/placeholder.svg'}
                      alt={current.alt}
                      fill
                      sizes="(max-width: 1024px) 100vw, 768px"
                      className="object-cover"
                      priority
                    />
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  )
}
