const WA = 'https://wa.me/14155238886?text=Hello%2C%20I%20want%20to%20find%20funding%20for%20my%20business'

function ChatPreview() {
  return (
    <div className="chat-preview" style={{ animation: 'float 6s ease-in-out infinite' }}>
      <div className="chat-header">
        <div className="chat-avatar">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/></svg>
        </div>
        <div>
          <div className="chat-info-name">BizPadi</div>
          <div className="chat-info-status">online</div>
        </div>
        <div style={{ marginLeft: 'auto' }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth="2"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
        </div>
      </div>

      <div className="chat-body">
        <div className="chat-date">Today</div>

        <div className="bubble bubble-in">
          <div className="bubble-sender">BizPadi</div>
          Hey, good to meet you. What kind of business do you run?
          <div className="bubble-time">9:41 AM</div>
        </div>

        <div className="bubble bubble-out">
          I sell clothes in Aba. 2 years, about 400k monthly.
          <div className="bubble-time">9:42 AM</div>
        </div>

        <div className="bubble-match-card">
          <div className="bubble-sender">BizPadi</div>
          Found 4 opportunities that match your business.
          <div style={{ height: 6 }} />
          <div className="match-item match-item--primary">
            <div className="match-name">Tony Elumelu Foundation</div>
            <div className="match-desc">$5,000 seed capital. No CAC needed.</div>
            <div className="match-score">95% match</div>
          </div>
          <div className="match-item match-item--secondary">
            <div className="match-name">SMEDAN Grant Scheme</div>
            <div className="match-desc">Up to 3M naira. Rolling applications.</div>
            <div className="match-score">88% match</div>
          </div>
          <div className="bubble-time">9:42 AM</div>
        </div>

        <div className="bubble bubble-out">
          Applied for TEF. Thank you!
          <div className="bubble-time">9:44 AM</div>
        </div>

        <div className="bubble bubble-in" style={{ background: '#fff' }}>
          <div className="bubble-sender">BizPadi</div>
          <div style={{ display: 'flex', gap: 2, marginBottom: 3 }}>
            {[1,2,3,4,5].map(i => (
              <svg key={i} width="10" height="10" viewBox="0 0 24 24" fill="#F59E0B"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            ))}
          </div>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--ink)' }}>Applied successfully!</div>
          <div style={{ fontSize: '0.62rem', color: 'var(--ink2)', marginTop: 1 }}>Application tracked for you.</div>
          <div className="bubble-time">9:44 AM</div>
        </div>
      </div>

      <div className="chat-footer">
        <div className="chat-input-mock">Message</div>
        <div className="chat-send">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="white"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </div>
      </div>
    </div>
  )
}

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-bg" />

      <div className="badge reveal in">
        <span className="section-eyebrow-dot" />
        AI-Powered for Nigerian SMEs
      </div>

      <h1 className="hero-title reveal in" style={{ animationDelay: '0.05s' }}>
        Your Business.<br />
        Real <span className="accent">Funding.</span><br />
        <span className="gold">Right Now.</span>
      </h1>

      <p className="hero-sub reveal in" style={{ animationDelay: '0.1s' }}>
        BizPadi finds grants, loans, and support programmes that actually match your business.
        Send one WhatsApp message and we handle everything.
      </p>

      <div className="hero-ctas reveal in" style={{ animationDelay: '0.15s' }}>
        <a href={WA} target="_blank" rel="noreferrer" className="btn btn-primary" style={{ fontSize: '0.95rem', padding: '0.9rem 2rem' }}>
          <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
          Start free on WhatsApp
        </a>
        <button className="btn btn-outline" onClick={() => document.getElementById('how')?.scrollIntoView({ behavior:'smooth' })}>See how it works</button>
      </div>

      <div className="hero-trust reveal in" style={{ animationDelay: '0.2s' }}>
        <div className="trust-avatars">
          {['AO','KA','FI','EM'].map((x,i) => <div key={i} className="trust-avatar">{x}</div>)}
        </div>
        <span className="trust-label">Trusted by SMEs across Nigeria</span>
      </div>

      <div className="reveal in" style={{ animationDelay: '0.25s', width: '100%', display: 'flex', justifyContent: 'center' }}>
        <ChatPreview />
      </div>
    </section>
  )
}
