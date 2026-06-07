import React, { useState, useEffect } from 'react'
import { WA_LINK, NAV_ITEMS, scrollToId } from '../lib/constants'
import { WhatsappIcon } from '../lib/icons'

export default function Nav() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const go = (id) => {
    setOpen(false)
    scrollToId(id)
  }

  return (
    <>
      <nav className={`nav${scrolled ? ' nav--scrolled' : ''}`}>
        <button className="brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          Biz<span>Padi</span>
        </button>

        <div className="nav-links">
          {NAV_ITEMS.map((item) => (
            <button key={item.id} className="nav-link" onClick={() => go(item.id)}>
              {item.label}
            </button>
          ))}
        </div>

        <div className="nav-actions">
          <a href={WA_LINK} target="_blank" rel="noreferrer" className="btn btn-primary btn-sm">
            <WhatsappIcon size={14} />
            Start free
          </a>
          <button
            className="hamburger"
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            ) : (
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M3 6h18M3 12h18M3 18h18" />
              </svg>
            )}
          </button>
        </div>
      </nav>

      {open && (
        <div className="mobile-menu">
          {NAV_ITEMS.map((item) => (
            <button key={item.id} className="nav-link" onClick={() => go(item.id)}>
              {item.label}
            </button>
          ))}
          <a
            href={WA_LINK}
            target="_blank"
            rel="noreferrer"
            className="btn btn-primary"
            onClick={() => setOpen(false)}
          >
            <WhatsappIcon size={15} />
            Start free on WhatsApp
          </a>
        </div>
      )}
    </>
  )
}
