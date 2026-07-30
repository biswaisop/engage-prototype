'use client'

import { Reveal } from '@/components/reveal'
import { SectionHeading } from '@/components/section-heading'

const steps = [
  {
    title: 'Embed the widget',
    body: 'Drop one line of code onto your website — or connect WhatsApp and Telegram. Setup takes minutes, not weeks.',
  },
  {
    title: 'AI learns your property',
    body: 'It answers from your knowledge base: amenities, policies, rates, and local recommendations, all in your voice.',
  },
  {
    title: 'Escalates when unsure',
    body: 'If confidence drops, it hands off to your staff seamlessly — with full context, so no guest is left guessing.',
  },
  {
    title: 'Monitor everything',
    body: 'Review conversations, flags, and trends across all of your properties from a single operations dashboard.',
  },
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="relative px-5 py-24 sm:px-8 sm:py-32">
      <div className="mx-auto max-w-6xl">
        <SectionHeading
          index="02"
          label="How it works"
          title="From embed to effortless, in four steps."
          description="No integrations project, no IT ticket. You could be live before your next check-in."
        />

        <div className="mt-8">
          {steps.map((step, i) => (
            <Reveal key={step.title} delay={i * 0.08}>
              <div className="group grid grid-cols-12 items-baseline gap-4 border-t border-border py-8 transition-colors duration-500 last:border-b hover:bg-foreground/[0.02] sm:gap-6 sm:py-10">
                <span className="col-span-2 font-serif text-3xl text-muted-foreground/40 transition-colors duration-500 group-hover:text-gold sm:col-span-1 sm:text-4xl">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h3 className="col-span-10 font-serif text-xl text-foreground sm:col-span-4 sm:text-2xl">
                  {step.title}
                </h3>
                <p className="col-span-12 max-w-xl leading-relaxed text-muted-foreground sm:col-span-7">
                  {step.body}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
