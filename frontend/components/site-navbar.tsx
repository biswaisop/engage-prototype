'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Menu, X } from 'lucide-react'
import { Logo } from '@/components/logo'
import { cn } from '@/lib/utils'

const links = [
  { label: 'Product', href: '#product' },
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
]

export function SiteNavbar() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="fixed inset-x-0 top-0 z-50"
    >
      <div
        aria-hidden
        className={cn(
          'pointer-events-none absolute inset-x-0 top-0 nav-fog transition-all duration-500 ease-out',
          scrolled ? 'h-28 opacity-100' : 'h-24 opacity-80',
        )}
      />
      <div
        className={cn(
          'relative mx-auto flex max-w-7xl items-center justify-between px-5 transition-all duration-500 ease-out sm:px-8',
          scrolled
            ? 'my-3 rounded-2xl glass shadow-[0_8px_40px_-12px_rgba(0,0,0,0.6)] py-3'
            : 'my-2 border border-transparent py-5',
        )}
      >
        <Logo />

        <nav className="hidden items-center gap-8 md:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="group relative text-sm text-muted-foreground transition-colors duration-300 hover:text-foreground"
            >
              {link.label}
              <span className="absolute -bottom-1 left-0 h-px w-0 bg-gold shadow-[0_0_8px_var(--gold)] transition-all duration-300 group-hover:w-full" />
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Link
            href="/login"
            className="rounded-full px-4 py-2 text-sm text-muted-foreground transition-colors duration-300 hover:text-foreground"
          >
            Login
          </Link>
          <Link
            href="/signup"
            className="rounded-full bg-gold px-5 py-2 text-sm font-medium text-gold-foreground transition-all duration-300 hover:scale-[1.03] hover:glow-gold"
          >
            Try Now
          </Link>
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-foreground md:hidden"
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mx-3 mt-1 rounded-2xl glass-strong p-4 md:hidden"
        >
          <nav className="flex flex-col gap-1">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="rounded-lg px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              >
                {link.label}
              </Link>
            ))}
            <div className="mt-2 flex flex-col gap-2 border-t border-border pt-3">
              <Link
                href="/login"
                onClick={() => setOpen(false)}
                className="rounded-full border border-border px-4 py-2.5 text-center text-sm text-foreground"
              >
                Login
              </Link>
              <Link
                href="/signup"
                onClick={() => setOpen(false)}
                className="rounded-full bg-gold px-4 py-2.5 text-center text-sm font-medium text-gold-foreground"
              >
                Try Now
              </Link>
            </div>
          </nav>
        </motion.div>
      )}
    </motion.header>
  )
}
