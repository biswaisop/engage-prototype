import Link from 'next/link'
import { cn } from '@/lib/utils'

export function Logo({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      className={cn('group inline-flex items-center gap-2.5', className)}
      aria-label="Front Desk AI home"
    >
      <span className="relative flex h-8 w-8 items-center justify-center rounded-md border border-gold/40 bg-gold/10">
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          className="text-gold"
          aria-hidden="true"
        >
          <path
            d="M4 20V9l8-5 8 5v11"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M9 20v-5h6v5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
      <span className="font-serif text-lg tracking-tight text-foreground">
        Front Desk<span className="text-gold"> AI</span>
      </span>
    </Link>
  )
}
