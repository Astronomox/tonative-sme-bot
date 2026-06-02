import React, { useState, useEffect } from 'react'

const WA_LINK = 'https://wa.me/14155238886?text=Hello%2C%20I%20want%20to%20find%20funding%20for%20my%20business'

export default function Nav() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '1.1rem 3rem',
      background: scrolled ? 'rgba(247,246,242,0.95)' : 'transparent',
      backdropFilter: scrolled ? 'blur(20px)' : 'none',
      borderBottom: scrolled ? '1px solid var(--border)' : '1px solid transparent',
      transition: 'all 0.3s ease',
    }}>
      <a href="/" style={{
        fontFamily: 'Fraunces, serif',
        fontSize: '1.5rem', fontWeight: 900,
        color: 'var(--ink)', letterSpacing: '-0.03em',
      }}>
        Biz<span style={{ color: 'var(--green)' }}>Padi</span>
      </a>

      <div style={{ display: 'flex', alignItems: 'center', gap: '2.5rem' }}>
        {['Features', 'How it works', 'Stories'].map(link => (
          <a key={link}
            href={`#${link.toLowerCase().replace(/\s+/g, '-')}`}
            style={{
              fontFamily: 'Montserrat, sans-serif',
              fontSize: '0.82rem', fontWeight: 500,
              color: 'var(--ink-2)', letterSpacing: '0.01em',
              transition: 'color 0.2s',
            }}
            onMouseEnter={e => e.target.style.color = 'var(--ink)'}
            onMouseLeave={e => e.target.style.color = 'var(--ink-2)'}
          >
            {link}
          </a>
        ))}

        <a href={WA_LINK} target="_blank" rel="noreferrer" style={{
          display: 'flex', alignItems: 'center', gap: '0.5rem',
          background: 'var(--ink)', color: '#fff',
          fontFamily: 'Montserrat, sans-serif',
          fontWeight: 600, fontSize: '0.8rem',
          padding: '0.65rem 1.4rem', borderRadius: 'var(--radius-full)',
          letterSpacing: '0.02em',
          transition: 'all 0.2s',
        }}
          onMouseEnter={e => { e.currentTarget.style.background = 'var(--green)'; e.currentTarget.style.transform = 'translateY(-1px)' }}
          onMouseLeave={e => { e.currentTarget.style.background = 'var(--ink)'; e.currentTarget.style.transform = 'translateY(0)' }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
          </svg>
          Start free
        </a>
      </div>
    </nav>
  )
}
