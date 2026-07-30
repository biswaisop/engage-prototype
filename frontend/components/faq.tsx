'use client'

import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Plus } from 'lucide-react'
import { Reveal } from '@/components/reveal'

const faqs = [
  {
    q: 'How does the AI avoid giving wrong answers?',
    a: 'Front Desk AI only answers from your approved knowledge base and uses confidence thresholds. When it isn’t certain, it escalates to your staff instead of guessing — no invented policies or prices.',
  },
  {
    q: 'What happens when a guest needs a human?',
    a: 'The conversation is flagged and routed to your team via your preferred channel, with full context attached so staff can pick up instantly without asking the guest to repeat themselves.',
  },
  {
    q: 'Can it manage multiple properties?',
    a: 'Yes. Each property has its own knowledge base and settings, and you switch between them — or view them together — from a single dashboard.',
  },
  {
    q: 'Which channels are supported?',
    a: 'A website chat widget out of the box, plus WhatsApp and Telegram on Growth and above. All channels share the same underlying knowledge and escalation rules.',
  },
  {
    q: 'How long does setup take?',
    a: 'Most properties are live within a day. You embed one snippet or connect a channel, import your property details, and the AI is ready to answer.',
  },
]

export function Faq() {
  const [open, setOpen] = useState<number | null>(0)

  return (
    <section id="faq" className="relative px-5 py-24 sm:px-8 sm:py-32">
      <div className="mx-auto max-w-3xl">
        <Reveal className="text-center">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-gold">
            FAQ
          </p>
          <h2 className="mt-4 text-balance font-serif text-3xl tracking-tight text-foreground sm:text-5xl">
            Questions, answered.
          </h2>
        </Reveal>

        <Reveal delay={0.1} className="mt-12">
          <div className="overflow-hidden rounded-3xl glass">
            {faqs.map((faq, i) => {
              const isOpen = open === i
              return (
                <div
                  key={faq.q}
                  className="border-b border-border last:border-b-0"
                >
                  <button
                    type="button"
                    onClick={() => setOpen(isOpen ? null : i)}
                    className="flex w-full items-center justify-between gap-4 px-6 py-5 text-left transition-colors duration-300 hover:bg-foreground/[0.03]"
                    aria-expanded={isOpen}
                  >
                    <span className="font-serif text-lg text-foreground">
                      {faq.q}
                    </span>
                    <motion.span
                      animate={{ rotate: isOpen ? 45 : 0 }}
                      transition={{ duration: 0.3 }}
                      className="shrink-0 text-gold"
                    >
                      <Plus className="h-5 w-5" />
                    </motion.span>
                  </button>
                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                        className="overflow-hidden"
                      >
                        <p className="px-6 pb-6 text-sm leading-relaxed text-muted-foreground">
                          {faq.a}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )
            })}
          </div>
        </Reveal>
      </div>
    </section>
  )
}
