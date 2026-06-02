import React, { useEffect, useRef } from 'react'

const steps = [
  {
    num: '01',
    title: 'Tell us about your hustle',
    desc: 'Send a WhatsApp message about your business. What you do, where you are, how long you have been running. Speak naturally.',
  },
  {
    num: '02',
    title: 'We find your matches',
    desc: 'BizPadi analyses your profile against every available opportunity in real time and surfaces only the ones you qualify for.',
  },
  {
    num: '03',
    title: 'Apply with confidence',
    desc: 'Get a clear step-by-step guide for each opportunity. BizPadi tracks your application and reminds you before deadlines close.',
  },
]

export default function HowItWorks() {
  const ref = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          entry.target.querySelectorAll('[data-reveal]').forEach((el, i) => {
            setTimeout(() => {
              el.style.opacity = '1'
              el.style.transform = 'translateY(0)'
            }, i * 120)
          })
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.15 }
    )
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  return (
    <section id="how-it-works" style={{
      padding: '8rem 3rem',
      background: 'var(--white)',
      borderTop: '1px solid var(--border)',
    }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }} ref={ref}>
        {/* Header */}
        <div data-reveal style={{
          opacity: 0, transform: 'translateY(20px)',
          transition: 'all 0.6s ease',
          marginBottom: '5rem',
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '3rem',
          alignItems: 'end',
        }}>
          <div>
            <div style={{
              fontSize: '0.72rem', fontWeight: 700,
              letterSpacing: '0.12em', textTransform: 'uppercase',
              color: 'var(--green)', marginBottom: '1rem',
            }}>
              How it works
            </div>
            <h2 style={{
              fontSize: 'clamp(2rem, 4vw, 3rem)',
              fontWeight: 900, color: 'var(--ink)',
            }}>
              Three messages.{' '}
              <em style={{ color: 'var(--green)' }}>Real results.</em>
            </h2>
          </div>
          <p style={{
            fontSize: '1rem', color: 'var(--ink-2)', lineHeight: 1.75,
            alignSelf: 'end',
          }}>
            No onboarding, no waiting, no forms. Start a conversation and BizPadi does the heavy lifting.
          </p>
        </div>

        {/* Steps grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 0,
          position: 'relative',
        }}>
          {/* Connector line */}
          <div style={{
            position: 'absolute',
            top: 28, left: '16.5%', right: '16.5%',
            height: 1,
            background: 'linear-gradient(90deg, transparent, var(--green-mid), transparent)',
          }} />

          {steps.map((step, i) => (
            <div
              key={i}
              data-reveal
              style={{
                opacity: 0, transform: 'translateY(20px)',
                transition: `all 0.6s ease`,
                padding: i === 0 ? '0 2rem 0 0' : i === 2 ? '0 0 0 2rem' : '0 2rem',
                borderRight: i < 2 ? '1px solid var(--border)' : 'none',
              }}
            >
              {/* Number circle */}
              <div style={{
                width: 56, height: 56,
                borderRadius: '50%',
                background: 'var(--bg)',
                border: '1.5px solid var(--border)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: '1.75rem',
                position: 'relative', zIndex: 1,
              }}>
                <span style={{
                  fontFamily: 'Fraunces, serif',
                  fontSize: '1.1rem', fontWeight: 900,
                  color: 'var(--green)',
                }}>
                  {step.num}
                </span>
              </div>

              <h3 style={{
                fontFamily: 'Fraunces, serif',
                fontSize: '1.15rem', fontWeight: 700,
                color: 'var(--ink)', marginBottom: '0.75rem',
              }}>
                {step.title}
              </h3>
              <p style={{
                fontSize: '0.875rem', color: 'var(--ink-2)', lineHeight: 1.75,
              }}>
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
