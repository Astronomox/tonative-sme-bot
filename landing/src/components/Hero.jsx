import React from 'react'
import { WA_LINK, scrollToId } from '../lib/constants'
import { WhatsappIcon, ArrowRight } from '../lib/icons'
import ChatMockup from './ChatMockup'

const TRUST = ['AO', 'KA', 'FI', 'EM']

export default function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero-glow" />
      <div className="container">
        <div className="hero-grid">
          <div className="hero-copy">
            <span className="hero-badge">AI funding companion for Nigerian SMEs</span>

            <h1 className="hero-title">
              Your Business.<br />
              Real <span className="green">Funding.</span><br />
              <span className="gold">Right Now.</span>
            </h1>

            <p className="hero-lead">
              BizPadi finds grants, loans, and support programmes that actually match your
              business. Send one WhatsApp message and it handles the rest, in your language.
            </p>

            <div className="hero-ctas">
              <a href={WA_LINK} target="_blank" rel="noreferrer" className="btn btn-primary">
                <WhatsappIcon size={17} />
                Start free on WhatsApp
              </a>
              <button className="btn btn-ghost" onClick={() => scrollToId('how')}>
                See how it works
                <ArrowRight size={16} />
              </button>
            </div>

            <div className="hero-trust">
              <div className="avatar-stack">
                {TRUST.map((initials) => (
                  <span key={initials} className="avatar">{initials}</span>
                ))}
              </div>
              <span className="hero-trust-label">Built for SMEs across Nigeria</span>
            </div>
          </div>

          <div className="hero-visual">
            <ChatMockup variant="classic" />
          </div>
        </div>
      </div>
    </section>
  )
}
