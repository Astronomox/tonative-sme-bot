import React from 'react'

const PROGRAMMES = [
  'TEF Programme',
  'Bank of Industry',
  'YouWiN Connect',
  'NIRSAL Microfinance',
  'SMEDAN Grants',
  'CBN Facilities',
  'AfDB Youth Fund',
  'LSETF Lagos',
]

function Dot() {
  return (
    <svg className="marquee-dot" width="6" height="6" viewBox="0 0 6 6" aria-hidden="true">
      <circle cx="3" cy="3" r="3" fill="currentColor" />
    </svg>
  )
}

export default function Marquee() {
  /* Duplicated once so the -50% loop is seamless. */
  const loop = [...PROGRAMMES, ...PROGRAMMES]
  return (
    <div className="marquee" aria-label="Funding programmes BizPadi tracks">
      <div className="marquee-track">
        {loop.map((name, i) => (
          <span className="marquee-item" key={i} aria-hidden={i >= PROGRAMMES.length}>
            <Dot />
            {name}
          </span>
        ))}
      </div>
    </div>
  )
}
