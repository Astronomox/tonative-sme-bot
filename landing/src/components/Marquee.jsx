import React from 'react'

const items = [
  'TEF Programme', 'Bank of Industry', 'YouWiN Connect',
  'NIRSAL Microfinance', 'SMEDAN Grants', 'CBN Facilities',
  'AfDB Youth Fund', 'LSETF Lagos', 'WOTCLEF Women',
]

export default function Marquee() {
  const doubled = [...items, ...items]

  return (
    <div style={{
      borderTop: '1px solid var(--border)',
      borderBottom: '1px solid var(--border)',
      padding: '1rem 0',
      overflow: 'hidden',
      background: 'var(--white)',
    }}>
      <div style={{
        display: 'flex',
        animation: 'marquee 28s linear infinite',
        whiteSpace: 'nowrap',
      }}>
        {doubled.map((item, i) => (
          <span key={i} style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.6rem',
            padding: '0 2.5rem',
            fontSize: '0.75rem', fontWeight: 600,
            letterSpacing: '0.08em', textTransform: 'uppercase',
            color: 'var(--ink-3)',
            flexShrink: 0,
          }}>
            <svg width="5" height="5" viewBox="0 0 5 5">
              <circle cx="2.5" cy="2.5" r="2.5" fill="var(--green-bright)" />
            </svg>
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}
