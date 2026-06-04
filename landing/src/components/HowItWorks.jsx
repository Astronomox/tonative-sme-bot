import React from 'react'
import { useReveal } from '../lib/useReveal'

const STEPS = [
  {
    num: '01',
    title: 'Tell us about your hustle',
    desc: 'Send a WhatsApp message about your business — what you do, where you are, how long you have been running. Speak naturally.',
  },
  {
    num: '02',
    title: 'We find your matches',
    desc: 'BizPadi reads your profile against every available opportunity and surfaces only the ones you actually qualify for.',
  },
  {
    num: '03',
    title: 'Apply with confidence',
    desc: 'Get a clear step-by-step guide for each one. BizPadi tracks your application and reminds you before deadlines close.',
  },
]

export default function HowItWorks() {
  const ref = useReveal()
  return (
    <section className="section section--alt" id="how" ref={ref}>
      <div className="container">
        <div className="section-head section-head--center">
          <div className="eyebrow reveal"><span className="eyebrow-dot" />How it works</div>
          <h2 className="section-title reveal">Three messages. <em>Real results.</em></h2>
          <p className="section-lead reveal">No onboarding, no waiting. Start a conversation and BizPadi does the heavy lifting.</p>
        </div>

        <div className="steps">
          <div className="steps-line" aria-hidden="true" />
          {STEPS.map((s) => (
            <div className="step reveal" key={s.num}>
              <div className="step-num">{s.num}</div>
              <div>
                <h3 className="step-title">{s.title}</h3>
                <p className="step-desc">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
