import React from 'react'
import ChatMockup from './ChatMockup'

const WA_LINK = 'https://wa.me/14155238886?text=Hello%2C%20I%20want%20to%20find%20funding%20for%20my%20business'

function FloatingCard({ style, children }) {
  return (
    <div style={{
      position: 'absolute',
      background: '#fff',
      borderRadius: 16,
      padding: '0.9rem 1.1rem',
      boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
      ...style,
    }}>
      {children}
    </div>
  )
}

export default function Hero() {
  return (
    <section className="hero-section" style={{
      minHeight: '100vh',
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      alignItems: 'center',
      padding: '0 3rem',
      paddingTop: '5.5rem',
      paddingBottom: '3rem',
      background: 'var(--bg)',
      position: 'relative',
      overflow: 'hidden',
      gap: '4rem',
    }}>
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: 'radial-gradient(circle at 70% 50%, rgba(26,122,60,0.04) 0%, transparent 60%)',
        pointerEvents: 'none',
      }} />

      {/* Left */}
      <div className="hero-left-col" style={{ position: 'relative', zIndex: 2, maxWidth: 560 }}>
        <div className="fade-up" style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
          background: 'var(--green-light)',
          border: '1px solid var(--green-mid)',
          color: 'var(--green)',
          fontSize: '0.72rem', fontWeight: 700,
          padding: '0.4rem 1rem', borderRadius: 'var(--radius-full)',
          marginBottom: '1.75rem',
          letterSpacing: '0.06em', textTransform: 'uppercase',
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: 'var(--green-bright)',
            animation: 'blink 2s ease infinite',
            flexShrink: 0,
          }} />
          AI-Powered for Nigerian SMEs
        </div>

        <h1 className="fade-up delay-1" style={{
          fontSize: 'clamp(2.8rem, 5.5vw, 4.8rem)',
          fontWeight: 900,
          color: 'var(--ink)',
          marginBottom: '1.5rem',
          lineHeight: 1.02,
        }}>
          Your Business.<br />
          Real{' '}
          <em style={{ fontStyle: 'normal', color: 'var(--green)' }}>Funding.</em>
          <br />
          <span style={{ color: 'var(--gold)' }}>Right Now.</span>
        </h1>

        <p className="fade-up delay-2" style={{
          fontSize: '1.05rem',
          color: 'var(--ink-2)',
          fontWeight: 400,
          lineHeight: 1.75,
          maxWidth: 460,
          marginBottom: '2.5rem',
        }}>
          BizPadi finds grants, loans, and support programmes
          that actually match your business. Send one WhatsApp
          message and we handle the rest.
        </p>

        <div className="fade-up delay-3" style={{
          display: 'flex', alignItems: 'center', gap: '1rem',
          flexWrap: 'wrap', marginBottom: '2.25rem',
        }}>
          <a href={WA_LINK} target="_blank" rel="noreferrer" style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.6rem',
            background: 'var(--green)', color: '#fff',
            fontFamily: 'Montserrat, sans-serif',
            fontWeight: 700, fontSize: '0.9rem',
            padding: '0.9rem 2rem', borderRadius: 'var(--radius-full)',
            boxShadow: '0 4px 20px rgba(26,122,60,0.35)',
            transition: 'all 0.2s',
          }}
            onMouseEnter={e => { e.currentTarget.style.background = '#156832'; e.currentTarget.style.transform = 'translateY(-2px)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'var(--green)'; e.currentTarget.style.transform = 'translateY(0)' }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
            Start free on WhatsApp
          </a>
          <a href="#how-it-works" style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
            color: 'var(--ink-2)', fontFamily: 'Montserrat, sans-serif',
            fontWeight: 500, fontSize: '0.875rem',
            padding: '0.9rem 1.5rem',
            border: '1.5px solid var(--border)',
            borderRadius: 'var(--radius-full)', transition: 'all 0.2s',
          }}
            onMouseEnter={e => { e.currentTarget.style.color = 'var(--ink)'; e.currentTarget.style.borderColor = '#aaa' }}
            onMouseLeave={e => { e.currentTarget.style.color = 'var(--ink-2)'; e.currentTarget.style.borderColor = 'var(--border)' }}
          >
            See how it works
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </a>
        </div>

        <div className="fade-up delay-4" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ display: 'flex' }}>
            {['AO', 'KA', 'FI', 'EM'].map((init, i) => (
              <div key={i} style={{
                width: 30, height: 30, borderRadius: '50%',
                background: 'var(--green-light)',
                border: '2.5px solid var(--bg)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.6rem', fontWeight: 700, color: 'var(--green)',
                marginLeft: i === 0 ? 0 : -8,
              }}>{init}</div>
            ))}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--ink-3)', fontWeight: 500 }}>
            Trusted by SMEs across Nigeria
          </span>
        </div>
      </div>

      {/* Right — hidden on mobile via CSS class */}
      <div className="hero-right-col" style={{
        position: 'relative', zIndex: 2,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        paddingRight: '2rem',
      }}>
        <div style={{ position: 'relative', animation: 'float 6s ease-in-out infinite' }}>
          <ChatMockup />
          <FloatingCard style={{ right: -50, top: 60, width: 158, animation: 'float 5s ease-in-out infinite', animationDelay: '0.5s' }}>
            <div style={{ fontSize: '0.62rem', color: 'var(--ink-3)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Matched today</div>
            <div style={{ fontFamily: 'Fraunces, serif', fontSize: '2rem', fontWeight: 900, color: 'var(--ink)', lineHeight: 1.1, margin: '2px 0' }}>4</div>
            <div style={{ fontSize: '0.68rem', color: 'var(--green)', fontWeight: 600 }}>opportunities found</div>
          </FloatingCard>
          <FloatingCard style={{ left: -55, bottom: 100, width: 165, animation: 'float 7s ease-in-out infinite', animationDelay: '1s' }}>
            <div style={{ width: 32, height: 32, borderRadius: 10, background: 'var(--green-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 6 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--green)" strokeWidth="2.5"><path d="M20 6L9 17l-5-5" /></svg>
            </div>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--ink)', lineHeight: 1.3 }}>Application tracked</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--ink-3)', marginTop: 2 }}>TEF 2026 applied</div>
          </FloatingCard>
        </div>
      </div>
    </section>
  )
}
