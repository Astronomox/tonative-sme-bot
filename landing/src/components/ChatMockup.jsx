import React from 'react'

/* Inline SVGs kept tiny + local so the mockup is self-contained. */
function Chevron() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M15 18l-6-6 6-6" />
    </svg>
  )
}

function Whatsapp({ size = 19 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.9 9.9 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2Zm0 18.13h-.01a8.2 8.2 0 0 1-4.18-1.14l-.3-.18-3.11.82.83-3.04-.2-.31a8.18 8.18 0 0 1-1.26-4.36c0-4.54 3.7-8.23 8.24-8.23a8.2 8.2 0 0 1 8.22 8.24c0 4.54-3.69 8.2-8.22 8.2Zm4.52-6.16c-.25-.12-1.47-.72-1.69-.81-.23-.08-.39-.12-.56.13-.16.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.12-1.05-.39-1.99-1.23-.74-.66-1.23-1.47-1.38-1.72-.14-.25-.01-.38.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.41.08-.17.04-.31-.02-.43-.06-.12-.56-1.34-.76-1.84-.2-.48-.41-.42-.56-.43h-.48c-.17 0-.43.06-.66.31-.22.25-.86.85-.86 2.07 0 1.22.89 2.4 1.01 2.56.12.17 1.75 2.67 4.23 3.74.59.26 1.05.41 1.41.52.59.19 1.13.16 1.56.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.08.14-1.18-.06-.11-.22-.17-.47-.29Z" />
    </svg>
  )
}

function Dots() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <circle cx="12" cy="5" r="1.6" /><circle cx="12" cy="12" r="1.6" /><circle cx="12" cy="19" r="1.6" />
    </svg>
  )
}

function Video() {
  return (
    <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M23 7l-7 5 7 5V7z" /><rect x="1" y="5" width="15" height="14" rx="2" />
    </svg>
  )
}

function Star() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="var(--gold-star)">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
    </svg>
  )
}

function Send() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="#fff">
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  )
}

/* variant: 'classic' | 'brand' | 'light' */
export default function ChatMockup({ variant = 'classic' }) {
  return (
    <div className="phone">
      <div className="phone-frame">
        <div className={`phone-screen chat--${variant}`}>
          <div className="phone-notch" />

          <header className="chat-top">
            <span className="chat-back"><Chevron /></span>
            <span className="chat-pfp"><Whatsapp size={18} /></span>
            <div className="chat-id">
              <div className="chat-name">BizPadi</div>
              <div className="chat-presence">online</div>
            </div>
            <div className="chat-top-icons">
              <Video />
              <Dots />
            </div>
          </header>

          <div className="chat-body">
            <span className="chat-day">TODAY</span>

            <div className="msg-group in">
              <span className="msg-sender">BizPadi</span>
              <div className="bubble in tail">
                Hey, good to meet you. What kind of business do you run?
                <span className="bubble-time">9:41 AM</span>
              </div>
            </div>

            <div className="msg-group out">
              <div className="bubble out tail">
                I sell clothes in Aba. 2 years, about ₦400k monthly.
                <span className="bubble-time">9:42 AM</span>
              </div>
            </div>

            <div className="msg-group in">
              <span className="msg-sender">BizPadi</span>
              <div className="bubble in tail">
                Found 4 funding opportunities that match your fashion business.
                <span className="bubble-time">9:42 AM</span>
              </div>
              <div className="bubble in match-card">
                <div className="match-row match-row--primary">
                  <div className="match-name">Tony Elumelu Foundation</div>
                  <div className="match-meta">$5,000 seed capital</div>
                  <div className="match-score">95% match</div>
                </div>
                <div className="match-row match-row--secondary">
                  <div className="match-name">SMEDAN Grant Scheme</div>
                  <div className="match-meta">Up to ₦3M</div>
                  <div className="match-score">88% match</div>
                </div>
                <span className="bubble-time">9:42 AM</span>
              </div>
            </div>

            <div className="msg-group out">
              <div className="bubble out tail">
                This is exactly what I needed!
                <span className="bubble-time">9:43 AM</span>
              </div>
            </div>

            <div className="msg-group in">
              <span className="msg-sender">BizPadi</span>
              <div className="bubble in match-card">
                <div className="stars">
                  <Star /><Star /><Star /><Star /><Star />
                </div>
                <div className="card-strong">Applied for TEF successfully!</div>
                <div className="card-soft">Application tracked for you</div>
                <span className="bubble-time">9:44 AM</span>
              </div>
            </div>

            <div className="msg-group in">
              <div className="typing">
                <span /><span /><span />
              </div>
            </div>
          </div>

          <div className="chat-input">
            <div className="chat-input-pill">Message</div>
            <div className="chat-send"><Send /></div>
          </div>
        </div>
      </div>

      <div className="float-card float-card--matches">
        <div className="float-label">Matched today</div>
        <div className="float-num">4</div>
        <div className="float-note">opportunities found</div>
      </div>

      <div className="float-card float-card--tracked">
        <span className="float-check">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        </span>
        <div>
          <div className="float-strong">Application tracked</div>
          <div className="float-sub">TEF 2026 applied</div>
        </div>
      </div>
    </div>
  )
}
