'use client'

import { Reveal } from '@/components/reveal'
import { cn } from '@/lib/utils'

type SectionHeadingProps = {
  index: string
  label: string
  title: React.ReactNode
  description?: React.ReactNode
  className?: string
}

/**
 * Editorial, "chaptered" section header:
 * a numbered index + label sit above a hairline rule, with the headline on the
 * left and an optional lede aligned to the baseline on the right.
 */
export function SectionHeading({
  index,
  label,
  title,
  description,
  className,
}: SectionHeadingProps) {
  return (
    <Reveal className={cn('w-full', className)}>
      <div className="flex items-center justify-between gap-4">
        <span className="flex items-center gap-3 font-mono text-xs uppercase tracking-[0.28em] text-gold">
          <span className="tabular-nums">{index}</span>
          <span className="h-3 w-px bg-gold/40" />
          <span className="text-muted-foreground">{label}</span>
        </span>
      </div>

      <div className="mt-5 h-px w-full bg-border" />

      <div className="mt-8 grid gap-6 md:grid-cols-12 md:items-end">
        <h2 className="col-span-12 text-balance font-serif text-3xl leading-[1.1] tracking-tight text-foreground md:col-span-8 md:text-[2.75rem] lg:text-5xl">
          {title}
        </h2>
        {description ? (
          <p className="col-span-12 text-pretty leading-relaxed text-muted-foreground md:col-span-4 md:text-right">
            {description}
          </p>
        ) : null}
      </div>
    </Reveal>
  )
}
