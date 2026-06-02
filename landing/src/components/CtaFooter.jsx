import React from 'react'

const WA_LINK = 'https://wa.me/14155238886?text=Hello%2C%20I%20want%20to%20find%20funding%20for%20my%20business'

export function CTA() {
  return (
    <section style={{
      padding: '9rem 3rem',
      background: 'var(--ink)',
      textAlign: 'center',
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: '50%', left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 600, height: 400,
        background: 'radial-gradient(ellipse, rgba(26,122,60,0.2) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      <div style={{ position: 'relative', zIndex: 1 }}>
        <div style={{
          fontSize: '0.72rem', fontWeight: 700,
          letterSpacing: '0.12em', textTransform: 'uppercase',
          color: 'var(--green-bright)', marginBottom: '1.25rem',
        }}>
          Ready to find your funding?
        </div>
        <h2 style={{
          fontFamily: 'Fraunces, serif',
          fontSize: 'clamp(2.5rem, 5vw, 4.2rem)',
          fontWeight: 900,
          color: '#fff',
          marginBottom: '1.25rem',
          letterSpacing: '-0.03em',
        }}>
          Your next grant is<br />
          one message away.
        </h2>
        <p style={{
          fontSize: '1rem', color: 'rgba(255,255,255,0.5)',
          maxWidth: 440, margin: '0 auto 3rem',
          fontFamily: 'Montserrat, sans-serif',
          fontWeight: 400, lineHeight: 1.75,
        }}>
          No forms, no appointments, no wahala. Open WhatsApp and start talking.
        </p>
        <a
          href={WA_LINK}
          target="_blank"
          rel="noreferrer"
          style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.7rem',
            background: 'var(--green-bright)', color: 'var(--ink)',
            fontFamily: 'Montserrat, sans-serif',
            fontWeight: 700, fontSize: '1rem',
            padding: '1.05rem 2.5rem', borderRadius: 'var(--radius-full)',
            boxShadow: '0 4px 32px rgba(34,197,94,0.4)',
            transition: 'all 0.2s',
          }}
          onMouseEnter={e => {
            e.currentTarget.style.transform = 'translateY(-3px)'
            e.currentTarget.style.boxShadow = '0 8px 40px rgba(34,197,94,0.5)'
          }}
          onMouseLeave={e => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.boxShadow = '0 4px 32px rgba(34,197,94,0.4)'
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
          </svg>
          Open WhatsApp, it's free
        </a>
      </div>
    </section>
  )
}

export function Footer() {
  return (
    <footer style={{
      padding: '2.25rem 3rem',
      borderTop: '1px solid var(--border)',
      background: 'var(--white)',
      display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem',
    }}>
      <a href="/" style={{
        fontFamily: 'Fraunces, serif',
        fontSize: '1.2rem', fontWeight: 900,
        color: 'var(--ink)', letterSpacing: '-0.02em',
      }}>
        Biz<span style={{ color: 'var(--green)' }}>Padi</span>
      </a>
      <p style={{ fontSize: '0.8rem', color: 'var(--ink-3)' }}>
        Built for Nigerian SMEs. Powered by AI.
      </p>
      <p style={{ fontSize: '0.78rem', color: 'var(--border)' }}>
        2026 BizPadi
      </p>
    </footer>
  )
}
