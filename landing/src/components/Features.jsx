import React from 'react'
import { useReveal } from '../lib/useReveal'

const FEATURES = [
  {
    title: 'Finds Your Match',
    desc: 'Tell us about your business once. BizPadi searches every relevant grant, loan, and programme in real time and brings back only what fits you.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="7" /><path d="M21 21l-4.3-4.3" />
      </svg>
    ),
  },
  {
    title: 'Walks You Through',
    desc: 'Every opportunity comes with a step-by-step guide, the exact documents you need, and a direct link to apply. No guesswork.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2" /><rect x="9" y="3" width="6" height="4" rx="1" /><path d="M9 14l2 2 4-4" />
      </svg>
    ),
  },
  {
    title: 'Tracks Deadlines',
    desc: 'Applied for something? BizPadi logs it, watches the deadline, and reminds you before it closes so nothing slips.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.7 21a2 2 0 01-3.4 0" />
      </svg>
    ),
  },
  {
    title: 'Speaks Your Language',
    desc: 'English, Yoruba, Hausa, Pidgin, French. Text or voice note. BizPadi understands you exactly as you are.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" />
      </svg>
    ),
  },
  {
    title: 'Always Available',
    desc: '2am or 2pm, weekday or weekend. Ask anything about funding, CAC registration, or growing your business.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" />
      </svg>
    ),
  },
  {
    title: 'Lives on WhatsApp',
    desc: 'No app to download, no account to create. You already have WhatsApp. That is all you need to get started.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 21s7-4.4 7-10V5l-7-3-7 3v6c0 5.6 7 10 7 10z" />
      </svg>
    ),
  },
]

export default function Features() {
  const ref = useReveal()
  return (
    <section className="section" id="features" ref={ref}>
      <div className="container">
        <div className="section-head">
          <div className="eyebrow reveal"><span className="eyebrow-dot" />What BizPadi does</div>
          <h2 className="section-title reveal">Built for the way Nigerian <em>businesses actually run.</em></h2>
          <p className="section-lead reveal">No apps, no forms, no appointments. Just WhatsApp, in your language, at any hour.</p>
        </div>

        <div className="features-grid">
          {FEATURES.map((f) => (
            <article className="feature reveal" key={f.title}>
              <div className="feature-icon">{f.icon}</div>
              <h3 className="feature-title">{f.title}</h3>
              <p className="feature-desc">{f.desc}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
