import React from 'react'
import { WA_LINK, NAV_ITEMS, scrollToId } from '../lib/constants'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <button className="brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
              Biz<span>Padi</span>
            </button>
            <p className="footer-tagline">
              The WhatsApp companion helping Nigerian SMEs find grants, loans, and funding that fit.
            </p>
          </div>

          <div>
            <div className="footer-col-title">Explore</div>
            <nav className="footer-links">
              {NAV_ITEMS.map((item) => (
                <button key={item.id} onClick={() => scrollToId(item.id)}>{item.label}</button>
              ))}
            </nav>
          </div>

          <div>
            <div className="footer-col-title">Get started</div>
            <nav className="footer-links">
              <a href={WA_LINK} target="_blank" rel="noreferrer">Chat on WhatsApp</a>
              <button onClick={() => scrollToId('stories')}>Read stories</button>
            </nav>
          </div>
        </div>

        <div className="footer-bottom">
          <span>© 2026 BizPadi</span>
          <span>Made in Nigeria, for Nigerian business.</span>
        </div>
      </div>
    </footer>
  )
}
