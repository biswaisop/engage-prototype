import { FogBackground } from '@/components/fog-background'
import { SiteNavbar } from '@/components/site-navbar'
import { Hero } from '@/components/hero'
import { ProductShowcase } from '@/components/product-showcase'
import { HowItWorks } from '@/components/how-it-works'
import { Features } from '@/components/features'
import { SocialProof } from '@/components/social-proof'
import { ScheduleCall } from '@/components/schedule-call'
import { Pricing } from '@/components/pricing'
import { Faq } from '@/components/faq'
import { SiteFooter } from '@/components/site-footer'

export default function Page() {
  return (
    <>
      <FogBackground />
      <SiteNavbar />
      <main>
        <Hero />
        <ProductShowcase />
        <HowItWorks />
        <Features />
        <SocialProof />
        <ScheduleCall />
        <Pricing />
        <Faq />
      </main>
      <SiteFooter />
    </>
  )
}
