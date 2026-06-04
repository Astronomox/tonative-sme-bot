import React from 'react'
import { WA_LINK } from '../lib/constants'
import { WhatsappIcon } from '../lib/icons'

export default function CTA() {
  return (
    <section className="cta" id="cta">
      <div className="cta-glow" />
      <div className="container cta-inner">
        <div className="eyebrow"><span className="eyebrow-dot" />Ready to find your funding?</div>
        <h2 className="cta-title">Your next grant is<br />one message away.</h2>
        <p className="cta-lead">No forms, no appointments, no wahala. Open WhatsApp and start the conversation.</p>
        <a href={WA_LINK} target="_blank" rel="noreferrer" className="btn cta-btn">
          <WhatsappIcon size={20} />
          Start free on WhatsApp
        </a>
      </div>
    </section>
  )
}
