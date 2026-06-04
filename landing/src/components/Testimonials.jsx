import React from 'react'
import { useReveal } from '../lib/useReveal'

const QUOTES = [
  {
    initials: 'KA',
    tone: 'blue',
    name: 'Kunle Adeyemi',
    biz: 'Fashion label · Lagos',
    quote: 'I sent a voice note in Yoruba at midnight. It understood everything and came back with the full TEF application steps. Very sharp.',
  },
  {
    initials: 'FI',
    tone: 'pink',
    name: 'Fatima Ibrahim',
    biz: 'Agribusiness · Kano',
    quote: 'BizPadi pinged me two days before the BOI deadline and I submitted just in time. The reminders alone are worth everything.',
  },
  {
    initials: 'AO',
    tone: 'green',
    name: 'Adaeze Okonkwo',
    biz: 'Bakery · Abuja',
    quote: 'I had no idea so many grants existed for my kind of business. BizPadi showed me five within minutes. I applied for three.',
  },
]

function Stars() {
  return (
    <div className="stars" aria-label="5 out of 5 stars">
      {[0, 1, 2, 3, 4].map((i) => (
        <svg key={i} width="15" height="15" viewBox="0 0 24 24" fill="var(--gold-star)" aria-hidden="true">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      ))}
    </div>
  )
}

export default function Testimonials() {
  const ref = useReveal()
  return (
    <section className="section" id="stories" ref={ref}>
      <div className="container">
        <div className="section-head">
          <div className="eyebrow reveal"><span className="eyebrow-dot" />From SME owners</div>
          <h2 className="section-title reveal">The people building Nigeria <em>deserve better tools.</em></h2>
        </div>

        <div className="quotes">
          {QUOTES.map((t) => (
            <figure className="quote reveal" key={t.name}>
              <Stars />
              <blockquote className="quote-text">&ldquo;{t.quote}&rdquo;</blockquote>
              <figcaption className="quote-author">
                <span className={`quote-avatar quote-avatar--${t.tone}`}>{t.initials}</span>
                <span>
                  <span className="quote-name">{t.name}</span>
                  <span className="quote-biz">{t.biz}</span>
                </span>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  )
}
