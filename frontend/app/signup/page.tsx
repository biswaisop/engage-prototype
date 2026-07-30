import { FogBackground } from '@/components/fog-background'
import { AuthCard } from '@/components/auth-card'

export default function SignupPage() {
  return (
    <>
      <FogBackground />
      <main className="flex min-h-screen items-center justify-center px-5 py-16">
        <AuthCard initialMode="signup" />
      </main>
    </>
  )
}
