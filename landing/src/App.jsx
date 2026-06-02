import Nav from './components/Nav'
import Hero from './components/Hero'
import Marquee from './components/Marquee'
import { Features, HowItWorks, Testimonials, CTA, Footer, WhatsAppWidget } from './components/Sections'

export default function App() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <Marquee />
        <Features />
        <HowItWorks />
        <Testimonials />
        <CTA />
      </main>
      <Footer />
      <WhatsAppWidget />
    </>
  )
}
