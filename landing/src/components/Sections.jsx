import { useEffect, useRef, useState } from 'react'

const WA = 'https://wa.me/14155238886?text=Hello%2C%20I%20want%20to%20find%20funding%20for%20my%20business'

function useReveal() {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) {
        el.querySelectorAll('.reveal').forEach((r, i) => {
          setTimeout(() => r.classList.add('in'), i * 90)
        })
        obs.unobserve(el)
      }
    }, { threshold: 0.1 })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])
  return ref
}

const features = [
  {
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>,
    title: 'Finds Your Match',
    desc: 'Tell us about your business once. BizPadi searches every relevant grant, loan, and programme in real time.',
  },
  {
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>,
    title: 'Walks You Through',
    desc: 'Each opportunity comes with a step-by-step guide, exact documents needed, and a direct link to apply.',
  },
  {
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/></svg>,
    title: 'Tracks Deadlines',
    desc: 'Applied for something? BizPadi logs it, watches the deadline, and reminds you before it closes.',
  },
  {
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>,
    title: 'Speaks Your Language',
    desc: 'English, Yoruba, Hausa, Pidgin, French. Text or voice note. BizPadi understands you exactly as you are.',
  },
  {
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>,
    title: 'Always Available',
    desc: '2am or 2pm, weekday or weekend. Ask anything about funding, CAC registration, or market opportunities.',
  },
  {
    icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>,
    title: 'Lives on WhatsApp',
    desc: 'No app to download, no account to create. You already have WhatsApp. That is all you need.',
  },
]

export function Features() {
  const ref = useReveal()
  return (
    <section className="section" id="features" ref={ref}>
      <div className="container">
        <div style={{ textAlign: 'center', marginBottom: 0 }}>
          <div className="section-eyebrow reveal"><span className="section-eyebrow-dot" />What BizPadi Does</div>
          <h2 className="section-title reveal">Built for Nigerian businesses.</h2>
          <p className="section-sub reveal">No apps, no forms, no appointments. Just WhatsApp, in your language, any hour.</p>
        </div>
        <div className="features-grid">
          {features.map((f, i) => (
            <div key={i} className="feature-card reveal">
              <div className="feature-icon">{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <p className="feature-desc">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

const steps = [
  { num: '01', title: 'Tell us about your hustle', desc: 'Send a WhatsApp message about your business. What you do, where you are, how long you have been running. Speak naturally.' },
  { num: '02', title: 'We find your matches', desc: 'BizPadi analyses your profile against every available opportunity in real time and surfaces only the ones you qualify for.' },
  { num: '03', title: 'Apply with confidence', desc: 'Get a clear step-by-step guide for each opportunity. BizPadi tracks your application and reminds you before deadlines close.' },
]

export function HowItWorks() {
  const ref = useReveal()
  return (
    <section className="section section--alt" id="how" ref={ref}>
      <div className="container">
        <div style={{ textAlign: 'center' }}>
          <div className="section-eyebrow reveal"><span className="section-eyebrow-dot" />How It Works</div>
          <h2 className="section-title reveal">Three messages. Real results.</h2>
          <p className="section-sub reveal">No onboarding, no waiting. Start a conversation and BizPadi handles everything.</p>
        </div>
        <div className="steps-row">
          <div className="steps-connector" />
          {steps.map((s, i) => (
            <div key={i} className="step reveal">
              <div className="step-num">{s.num}</div>
              <div>
                <div className="step-title">{s.title}</div>
                <p className="step-desc">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

const testimonials = [
  { initials: 'AO', bg: '#DCFCE7', color: '#15803D', name: 'Adaeze Okonkwo', biz: 'Bakery, Abuja FCT', quote: 'I had no idea so many grants existed for my kind of business. BizPadi showed me five within minutes. I applied for three.' },
  { initials: 'KA', bg: '#DBEAFE', color: '#1D4ED8', name: 'Kunle Adeyemi', biz: 'Fashion Label, Lagos', quote: 'I sent a voice note in Yoruba at midnight. It understood everything and gave me the TEF application steps. Very sharp.' },
  { initials: 'FI', bg: '#FCE7F3', color: '#9D174D', name: 'Fatima Ibrahim', biz: 'Agribusiness, Kano', quote: 'BizPadi reminded me two days before the BOI deadline. I submitted just in time. The reminders alone are worth everything.' },
]

export function Testimonials() {
  const ref = useReveal()
  return (
    <section className="section" id="stories" ref={ref}>
      <div className="container">
        <div style={{ textAlign: 'center' }}>
          <div className="section-eyebrow reveal"><span className="section-eyebrow-dot" />From SME Owners</div>
          <h2 className="section-title reveal">The people building Nigeria deserve better tools.</h2>
        </div>
        <div className="quotes-grid">
          {testimonials.map((t, i) => (
            <div key={i} className="quote-card reveal">
              <div className="quote-stars">
                {[1,2,3,4,5].map(j => (
                  <svg key={j} width="13" height="13" viewBox="0 0 24 24" fill="#F59E0B"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                ))}
              </div>
              <p className="quote-text">"{t.quote}"</p>
              <div className="quote-author">
                <div className="quote-avatar" style={{ background: t.bg, color: t.color }}>{t.initials}</div>
                <div>
                  <div className="quote-name">{t.name}</div>
                  <div className="quote-biz">{t.biz}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export function CTA() {
  return (
    <section className="cta-section">
      <div className="cta-glow" />
      <div className="section-eyebrow" style={{ color: 'var(--green-vivid)', justifyContent: 'center' }}>
        <span style={{ width: 5, height: 5, borderRadius: '50%', background: 'var(--green-vivid)', flexShrink: 0 }} />
        Ready to find your funding?
      </div>
      <h2 className="cta-title">Your next grant is<br />one message away.</h2>
      <p className="cta-sub">No forms, no appointments, no wahala. Open WhatsApp and start talking.</p>
      <a href={WA} target="_blank" rel="noreferrer" className="cta-btn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        Open WhatsApp, it's free
      </a>
    </section>
  )
}

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <a href="/" className="footer-logo">Biz<span>Padi</span></a>
        <p className="footer-copy">Built for Nigerian SMEs. Powered by AI.</p>
        <p className="footer-copy">2026 BizPadi</p>
      </div>
    </footer>
  )
}

export function WhatsAppWidget() {
  const [pos, setPos] = useState({ x: null, y: null })
  const [dragging, setDragging] = useState(false)
  const [moved, setMoved] = useState(false)
  const start = useRef({})

  useEffect(() => {
    setPos({ x: window.innerWidth - 80, y: window.innerHeight - 80 })
  }, [])

  useEffect(() => {
    const move = (e) => {
      if (!dragging) return
      const dx = e.clientX - start.current.mx
      const dy = e.clientY - start.current.my
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) setMoved(true)
      setPos({
        x: Math.max(0, Math.min(window.innerWidth - 54, start.current.px + dx)),
        y: Math.max(0, Math.min(window.innerHeight - 54, start.current.py + dy)),
      })
    }
    const up = () => setDragging(false)
    window.addEventListener('mousemove', move)
    window.addEventListener('mouseup', up)
    return () => { window.removeEventListener('mousemove', move); window.removeEventListener('mouseup', up) }
  }, [dragging])

  if (!pos.x) return null

  return (
    <div
      className="wa-widget"
      style={{ left: pos.x, top: pos.y, bottom: 'auto', right: 'auto' }}
      onMouseDown={(e) => {
        setDragging(true); setMoved(false)
        const r = e.currentTarget.getBoundingClientRect()
        start.current = { mx: e.clientX, my: e.clientY, px: r.left, py: r.top }
        e.preventDefault()
      }}
    >
      <a
        href={WA} target="_blank" rel="noreferrer"
        className="wa-btn"
        onClick={(e) => { if (moved) e.preventDefault() }}
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
        <div className="wa-notif">1</div>
      </a>
      <div className="wa-tooltip">Chat with BizPadi</div>
    </div>
  )
}
