import React, { useEffect, useRef } from 'react'

const testimonials = [
  {
    initials: 'AO',
    color: '#DCFCE7',
    textColor: '#15803D',
    name: 'Adaeze Okonkwo',
    biz: 'Bakery, Abuja FCT',
    quote: 'I had no idea so many grants existed for my kind of business. BizPadi showed me five within minutes. I applied for three of them.',
  },
  {
    initials: 'KA',
    color: '#DBEAFE',
    textColor: '#1D4ED8',
    name: 'Kunle Adeyemi',
    biz: 'Fashion Label, Lagos',
    quote: 'I sent a voice note in Yoruba at midnight. It understood everything and came back with the TEF application steps. Very sharp.',
  },
  {
    initials: 'FI',
    color: '#FCE7F3',
    textColor: '#9D174D',
    name: 'Fatima Ibrahim',
    biz: 'Agribusiness, Kano',
    quote: 'The reminders alone are worth everything. BizPadi pinged me two days before the BOI deadline and I submitted just in time.',
  },
]

function Stars() {
  return (
    <div style={{ display: 'flex', gap: 3, marginBottom: '1rem' }}>
      {[1,2,3,4,5].map(i => (
        <svg key={i} width="13" height="13" viewBox="0 0 24 24" fill="#F59E0B">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
        </svg>
      ))}
    </div>
  )
}

export default function Testimonials() {
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          entry.target.querySelectorAll('[data-reveal]').forEach((el, i) => {
            setTimeout(() => {
              el.style.opacity = '1'
              el.style.transform = 'translateY(0)'
            }, i * 100)
          })
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.1 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  return (
    <section id="stories" style={{
      padding: '8rem 3rem',
      background: 'var(--bg)',
      borderTop: '1px solid var(--border)',
    }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }} ref={ref}>
        <div data-reveal style={{
          opacity: 0, transform: 'translateY(20px)',
          transition: 'all 0.6s ease',
        }}>
          <div style={{
            fontSize: '0.72rem', fontWeight: 700,
            letterSpacing: '0.12em', textTransform: 'uppercase',
            color: 'var(--green)', marginBottom: '1rem',
          }}>
            From SME owners
          </div>
          <h2 style={{
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: 900, color: 'var(--ink)',
            marginBottom: '4rem', maxWidth: 560,
          }}>
            The people building Nigeria{' '}
            <em style={{ color: 'var(--green)' }}>deserve better tools.</em>
          </h2>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1.25rem',
        }} className="testimonials-grid">
          {testimonials.map((t, i) => (
            <div
              key={i}
              data-reveal
              style={{
                opacity: 0, transform: 'translateY(20px)',
                transition: `all 0.6s ease`,
                background: 'var(--white)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius)',
                padding: '2rem',
                cursor: 'default',
              }}
              onMouseEnter={e => {
                e.currentTarget.style.boxShadow = 'var(--shadow)'
                e.currentTarget.style.transform = 'translateY(-3px)'
                e.currentTarget.style.borderColor = '#ccc'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.boxShadow = 'none'
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.borderColor = 'var(--border)'
              }}
            >
              <div style={{
                display: 'flex', alignItems: 'center', gap: '0.75rem',
                marginBottom: '1.25rem',
              }}>
                <div style={{
                  width: 42, height: 42, borderRadius: '50%',
                  background: t.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'Fraunces, serif',
                  fontSize: '0.85rem', fontWeight: 700,
                  color: t.textColor,
                  flexShrink: 0,
                }}>
                  {t.initials}
                </div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--ink)' }}>{t.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--ink-3)' }}>{t.biz}</div>
                </div>
              </div>
              <Stars />
              <p style={{
                fontSize: '0.9rem', color: 'var(--ink-2)',
                lineHeight: 1.75, fontStyle: 'italic',
              }}>
                "{t.quote}"
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
