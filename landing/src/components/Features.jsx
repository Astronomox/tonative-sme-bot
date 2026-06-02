import React, { useEffect, useRef } from 'react'

const features = [
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
      </svg>
    ),
    title: 'Finds Your Match',
    desc: 'Tell us about your business once. BizPadi searches every relevant grant, loan, and programme in real time and brings back only what fits you specifically.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
      </svg>
    ),
    title: 'Walks You Through',
    desc: 'Each opportunity comes with a step-by-step guide, the exact documents you need, and a direct link to apply. No guesswork, no wasted trips.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/>
      </svg>
    ),
    title: 'Keeps You on Track',
    desc: 'Applied for something? BizPadi logs it, watches the deadline, and sends you a reminder before it closes. Your pipeline, organised.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      </svg>
    ),
    title: 'Speaks Your Language',
    desc: 'English, Yoruba, Hausa, Pidgin, French. Text or voice note. BizPadi understands you exactly as you are, no translation needed.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
      </svg>
    ),
    title: 'Always Available',
    desc: '2am or 2pm. Ask anything about your business, funding eligibility, CAC registration, or market opportunities. It is always there.',
  },
  {
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    ),
    title: 'Lives on WhatsApp',
    desc: 'No app to download, no account to create, no website to navigate. You already have WhatsApp. That is all you need.',
  },
]

function FeatureCard({ icon, title, desc, index }) {
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1'
          entry.target.style.transform = 'translateY(0)'
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.1 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  return (
    <div
      ref={ref}
      style={{
        background: 'var(--white)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '2rem',
        opacity: 0,
        transform: 'translateY(20px)',
        transition: `opacity 0.6s ease ${index * 0.08}s, transform 0.6s ease ${index * 0.08}s, box-shadow 0.3s, border-color 0.3s`,
        cursor: 'default',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.boxShadow = 'var(--shadow)'
        e.currentTarget.style.borderColor = '#ccc'
        e.currentTarget.style.transform = 'translateY(-3px)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.boxShadow = 'none'
        e.currentTarget.style.borderColor = 'var(--border)'
        e.currentTarget.style.transform = 'translateY(0)'
      }}
    >
      <div style={{
        width: 44, height: 44,
        borderRadius: 12,
        background: 'var(--green-light)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: 'var(--green)',
        marginBottom: '1.25rem',
      }}>
        {icon}
      </div>
      <h3 style={{
        fontFamily: 'Fraunces, serif',
        fontSize: '1.05rem', fontWeight: 700,
        color: 'var(--ink)', marginBottom: '0.6rem',
      }}>
        {title}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--ink-2)', lineHeight: 1.75 }}>
        {desc}
      </p>
    </div>
  )
}

export default function Features() {
  return (
    <section id="features" style={{
      padding: '8rem 3rem',
      background: 'var(--bg)',
    }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{
          fontSize: '0.72rem', fontWeight: 700,
          letterSpacing: '0.12em', textTransform: 'uppercase',
          color: 'var(--green)', marginBottom: '1rem',
        }}>
          What BizPadi does
        </div>
        <h2 style={{
          fontSize: 'clamp(2rem, 4vw, 3rem)',
          fontWeight: 900, color: 'var(--ink)',
          marginBottom: '1rem', maxWidth: 600,
        }}>
          Built for the way Nigerian{' '}
          <em style={{ fontStyle: 'italic', color: 'var(--green)' }}>businesses actually run.</em>
        </h2>
        <p style={{
          fontSize: '0.95rem', color: 'var(--ink-2)',
          maxWidth: 480, lineHeight: 1.75,
          marginBottom: '4rem',
        }}>
          No apps, no forms, no appointments. Just WhatsApp, in your language, at any hour.
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1.25rem',
        }}>
          {features.map((f, i) => (
            <FeatureCard key={i} {...f} index={i} />
          ))}
        </div>
      </div>
    </section>
  )
}
