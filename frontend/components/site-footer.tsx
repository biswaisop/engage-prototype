import Link from 'next/link'
import { Mail, Globe, Send, Rss } from 'lucide-react'
import { Logo } from '@/components/logo'

const columns = [
  {
    heading: 'Product',
    links: [
      { label: 'Product', href: '#product' },
      { label: 'How it works', href: '#how-it-works' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'FAQ', href: '#faq' },
    ],
  },
  {
    heading: 'Company',
    links: [
      { label: 'About', href: '#' },
      { label: 'Careers', href: '#' },
      { label: 'Blog', href: '#' },
      { label: 'Contact', href: '#schedule' },
    ],
  },
  {
    heading: 'Legal',
    links: [
      { label: 'Privacy', href: '#' },
      { label: 'Terms', href: '#' },
      { label: 'Security', href: '#' },
    ],
  },
]

export function SiteFooter() {
  return (
    <footer className="relative mt-8 border-t border-border/70 px-5 pb-10 pt-16 sm:px-8">
      {/* subtle top border glow */}
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-gold/50 to-transparent"
      />
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-10 lg:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div>
            <Logo />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">
              The AI receptionist that gives every property a five-star front
              desk — around the clock.
            </p>
            <a
              href="mailto:hello@frontdesk.ai"
              className="mt-5 inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-gold"
            >
              <Mail className="h-4 w-4" />
              hello@frontdesk.ai
            </a>
          </div>

          {columns.map((col) => (
            <div key={col.heading}>
              <h3 className="text-sm font-medium text-foreground">
                {col.heading}
              </h3>
              <ul className="mt-4 space-y-3">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors duration-300 hover:text-foreground"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-border/70 pt-6 sm:flex-row">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} Front Desk AI. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            {[
              { icon: Globe, label: 'Website' },
              { icon: Send, label: 'Newsletter' },
              { icon: Rss, label: 'Blog' },
            ].map(({ icon: Icon, label }) => (
              <a
                key={label}
                href="#"
                aria-label={label}
                className="flex h-9 w-9 items-center justify-center rounded-full glass text-muted-foreground transition-all duration-300 hover:border-gold/40 hover:text-gold"
              >
                <Icon className="h-4 w-4" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
