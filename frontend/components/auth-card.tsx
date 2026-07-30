'use client'

import { useEffect, useState, type FormEvent } from 'react'
import Link from 'next/link'
import { AnimatePresence, motion } from 'framer-motion'
import { Loader2, Check } from 'lucide-react'
import { Logo } from '@/components/logo'

type Mode = 'login' | 'signup'
type Errors = Record<string, string>

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function AuthCard({ initialMode }: { initialMode: Mode }) {
  const [mode, setMode] = useState<Mode>(initialMode)
  const [status, setStatus] = useState<'idle' | 'loading' | 'done'>('idle')
  const [errors, setErrors] = useState<Errors>({})

  // keep the URL in sync when toggling modes client-side
  useEffect(() => {
    const path = mode === 'login' ? '/login' : '/signup'
    if (window.location.pathname !== path) {
      window.history.replaceState(null, '', path)
    }
  }, [mode])

  function validate(data: Record<string, string>): Errors {
    const next: Errors = {}
    if (mode === 'signup' && !data.name?.trim()) next.name = 'Please enter your name.'
    if (mode === 'signup' && !data.property?.trim())
      next.property = 'Please enter your property name.'
    if (!emailRe.test(data.email ?? '')) next.email = 'Enter a valid email address.'
    if (!data.password || data.password.length < 8)
      next.password = 'Password must be at least 8 characters.'
    return next
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const data = Object.fromEntries(
      new FormData(e.currentTarget),
    ) as Record<string, string>
    const nextErrors = validate(data)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    setStatus('loading')
    // TODO: connect to auth API
    await mockAuth(mode, data)
    setStatus('done')
  }

  function switchMode(next: Mode) {
    setErrors({})
    setStatus('idle')
    setMode(next)
  }

  return (
    <div className="w-full max-w-md">
      <div className="mb-8 flex justify-center">
        <Logo />
      </div>

      <div className="rounded-3xl glass-strong p-7 shadow-[0_30px_120px_-40px_rgba(0,0,0,0.9)] sm:p-9">
        <AnimatePresence mode="wait">
          <motion.div
            key={mode + status}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          >
            {status === 'done' ? (
              <div className="flex flex-col items-center py-10 text-center">
                <span className="flex h-14 w-14 items-center justify-center rounded-full bg-gold/15 ring-1 ring-gold/30">
                  <Check className="h-6 w-6 text-gold" />
                </span>
                <h1 className="mt-5 font-serif text-2xl text-foreground">
                  {mode === 'login' ? 'Welcome back' : 'Account created'}
                </h1>
                <p className="mt-2 max-w-xs text-sm text-muted-foreground">
                  This is a demo — authentication isn&apos;t wired up yet. Check
                  the console to see the submitted values.
                </p>
                <button
                  type="button"
                  onClick={() => setStatus('idle')}
                  className="mt-6 text-sm text-gold transition-colors hover:text-gold-soft"
                >
                  Back to form
                </button>
              </div>
            ) : (
              <>
                <div className="text-center">
                  <h1 className="font-serif text-2xl text-foreground sm:text-3xl">
                    {mode === 'login'
                      ? 'Sign in to your front desk'
                      : 'Create your account'}
                  </h1>
                  <p className="mt-2 text-sm text-muted-foreground">
                    {mode === 'login'
                      ? 'Welcome back. Enter your details to continue.'
                      : 'Give every property a five-star front desk.'}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => console.log('[v0] Continue with Google (mock)')}
                  className="mt-7 flex w-full items-center justify-center gap-3 rounded-full border border-input bg-foreground/[0.03] px-6 py-3 text-sm font-medium text-foreground transition-all duration-300 hover:border-gold/40 hover:bg-foreground/[0.06]"
                >
                  <GoogleIcon />
                  Continue with Google
                </button>

                <div className="my-6 flex items-center gap-4">
                  <span className="h-px flex-1 bg-border" />
                  <span className="text-xs uppercase tracking-widest text-muted-foreground/70">
                    or
                  </span>
                  <span className="h-px flex-1 bg-border" />
                </div>

                <form onSubmit={handleSubmit} noValidate className="space-y-4">
                  {mode === 'signup' && (
                    <AuthField
                      label="Full name"
                      name="name"
                      placeholder="Jordan Vance"
                      error={errors.name}
                    />
                  )}
                  <AuthField
                    label="Email"
                    name="email"
                    type="email"
                    placeholder="you@hotel.com"
                    error={errors.email}
                  />
                  <AuthField
                    label="Password"
                    name="password"
                    type="password"
                    placeholder="••••••••"
                    error={errors.password}
                  />
                  {mode === 'signup' && (
                    <AuthField
                      label="Hotel / property name"
                      name="property"
                      placeholder="The Marlowe"
                      error={errors.property}
                    />
                  )}

                  <button
                    type="submit"
                    disabled={status === 'loading'}
                    className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-full bg-gold px-6 py-3.5 text-sm font-medium text-gold-foreground transition-all duration-300 hover:glow-gold disabled:opacity-70"
                  >
                    {status === 'loading' ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {mode === 'login' ? 'Signing in…' : 'Creating account…'}
                      </>
                    ) : mode === 'login' ? (
                      'Sign in'
                    ) : (
                      'Create account'
                    )}
                  </button>
                </form>

                <p className="mt-6 text-center text-sm text-muted-foreground">
                  {mode === 'login' ? (
                    <>
                      New to Front Desk AI?{' '}
                      <button
                        type="button"
                        onClick={() => switchMode('signup')}
                        className="text-gold transition-colors hover:text-gold-soft"
                      >
                        Create an account
                      </button>
                    </>
                  ) : (
                    <>
                      Already have an account?{' '}
                      <button
                        type="button"
                        onClick={() => switchMode('login')}
                        className="text-gold transition-colors hover:text-gold-soft"
                      >
                        Sign in
                      </button>
                    </>
                  )}
                </p>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      <p className="mt-6 text-center text-sm">
        <Link
          href="/"
          className="text-muted-foreground transition-colors hover:text-foreground"
        >
          ← Back to home
        </Link>
      </p>
    </div>
  )
}

// TODO: connect to auth API — mock only
async function mockAuth(mode: Mode, data: Record<string, string>) {
  await new Promise((r) => setTimeout(r, 1200))
  console.log(`[v0] Mock ${mode} submitted:`, data)
}

function AuthField({
  label,
  name,
  type = 'text',
  placeholder,
  error,
}: {
  label: string
  name: string
  type?: string
  placeholder?: string
  error?: string
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
        placeholder={placeholder}
        aria-invalid={!!error}
        className={`w-full rounded-xl border bg-foreground/[0.03] px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground/60 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-ring/40 ${
          error
            ? 'border-destructive/70'
            : 'border-input focus:border-gold/50'
        }`}
      />
      {error && <p className="mt-1.5 text-xs text-destructive">{error}</p>}
    </div>
  )
}

function GoogleIcon() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#EA4335"
        d="M12 10.2v3.9h5.5c-.24 1.4-1.7 4.1-5.5 4.1-3.3 0-6-2.7-6-6.1s2.7-6.1 6-6.1c1.9 0 3.1.8 3.8 1.5l2.6-2.5C16.9 2.9 14.7 2 12 2 6.9 2 2.8 6.1 2.8 11.2S6.9 20.4 12 20.4c5.9 0 9.8-4.1 9.8-9.9 0-.7-.1-1.2-.2-1.7H12z"
      />
    </svg>
  )
}
