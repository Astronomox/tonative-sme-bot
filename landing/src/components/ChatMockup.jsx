import React from 'react'

const WA_GREEN = '#075E54'
const WA_LIGHT = '#ECE5DD'
const WA_BUBBLE = '#FFFFFF'
const WA_SENT = '#D9FDD3'

function Bubble({ sent, name, children, time }) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: sent ? 'flex-end' : 'flex-start',
    }}>
      <div style={{
        maxWidth: '82%',
        background: sent ? WA_SENT : WA_BUBBLE,
        borderRadius: sent ? '12px 12px 3px 12px' : '12px 12px 12px 3px',
        padding: '0.55rem 0.8rem',
        boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
        position: 'relative',
      }}>
        {!sent && name && (
          <div style={{ fontSize: '0.6rem', fontWeight: 700, color: '#1A7A3C', marginBottom: 3 }}>
            {name}
          </div>
        )}
        <div style={{ fontSize: '0.72rem', lineHeight: 1.5, color: '#111' }}>{children}</div>
        <div style={{ fontSize: '0.58rem', color: '#999', textAlign: 'right', marginTop: 2 }}>{time}</div>
      </div>
    </div>
  )
}

function DateDivider({ label }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <span style={{
        background: 'rgba(255,255,255,0.7)',
        fontSize: '0.6rem', color: '#888',
        padding: '0.2rem 0.8rem',
        borderRadius: 100,
        display: 'inline-block',
      }}>{label}</span>
    </div>
  )
}

export default function ChatMockup() {
  return (
    <div style={{
      width: 300,
      borderRadius: 32,
      overflow: 'hidden',
      boxShadow: '0 0 0 8px #E8E8E8, 0 0 0 10px #DCDCDC, 0 32px 80px rgba(0,0,0,0.15)',
      background: '#fff',
      position: 'relative',
    }}>
      {/* Status bar */}
      <div style={{
        background: WA_GREEN,
        padding: '0.85rem 1rem',
        display: 'flex', alignItems: 'center', gap: '0.6rem',
      }}>
        <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.8)', display: 'flex' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M19 12H5M12 5l-7 7 7 7" />
          </svg>
        </button>
        <div style={{
          width: 34, height: 34, borderRadius: '50%',
          background: '#25D366',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z" />
          </svg>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ color: '#fff', fontSize: '0.82rem', fontWeight: 600, lineHeight: 1.2 }}>BizPadi</div>
          <div style={{ color: 'rgba(255,255,255,0.65)', fontSize: '0.62rem' }}>online</div>
        </div>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="2">
          <circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /><circle cx="5" cy="12" r="1" />
        </svg>
      </div>

      {/* Chat body */}
      <div style={{
        background: WA_LIGHT,
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23b8a898' fill-opacity='0.12' fill-rule='evenodd'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/svg%3E")`,
        padding: '0.9rem',
        display: 'flex', flexDirection: 'column', gap: '0.5rem',
        minHeight: 460,
      }}>
        <DateDivider label="Today" />

        <Bubble name="BizPadi" time="9:41 AM">
          Hey, good to meet you. What kind of business do you run?
        </Bubble>

        <Bubble sent time="9:42 AM">
          I sell clothes in Aba. Been running 2 years, about 400k monthly.
        </Bubble>

        <Bubble name="BizPadi" time="9:42 AM">
          Got it. Found 4 funding opportunities that match your fashion business in Aba.
        </Bubble>

        {/* Match card */}
        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
          <div style={{
            background: WA_BUBBLE,
            borderRadius: '12px 12px 12px 3px',
            padding: '0.7rem 0.8rem',
            boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
            maxWidth: '88%',
          }}>
            <div style={{ fontSize: '0.6rem', fontWeight: 700, color: '#1A7A3C', marginBottom: 6 }}>BizPadi</div>
            <div style={{
              background: '#EDFAF2', borderRadius: 8,
              padding: '0.55rem 0.65rem', marginBottom: 5,
              borderLeft: '3px solid #22C55E',
            }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, color: '#0C1A0E' }}>1. Tony Elumelu Foundation</div>
              <div style={{ fontSize: '0.62rem', color: '#6B7280', marginTop: 2 }}>$5,000 seed capital. No CAC needed.</div>
              <div style={{ fontSize: '0.58rem', color: '#16A34A', fontWeight: 700, marginTop: 3 }}>95% match</div>
            </div>
            <div style={{
              background: '#F9F9F9', borderRadius: 8,
              padding: '0.55rem 0.65rem',
            }}>
              <div style={{ fontSize: '0.68rem', fontWeight: 700, color: '#0C1A0E' }}>2. SMEDAN Grant Scheme</div>
              <div style={{ fontSize: '0.62rem', color: '#6B7280', marginTop: 2 }}>Up to 3M naira. Rolling applications.</div>
              <div style={{ fontSize: '0.58rem', color: '#16A34A', fontWeight: 700, marginTop: 3 }}>88% match</div>
            </div>
            <div style={{ fontSize: '0.58rem', color: '#999', textAlign: 'right', marginTop: 4 }}>9:42 AM</div>
          </div>
        </div>

        <Bubble sent time="9:43 AM">
          This is exactly what I needed. Can you help me apply for TEF?
        </Bubble>

        {/* Satisfaction card */}
        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
          <div style={{
            background: WA_BUBBLE,
            borderRadius: '12px 12px 12px 3px',
            padding: '0.75rem 0.85rem',
            boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
            maxWidth: '88%',
          }}>
            <div style={{ fontSize: '0.6rem', fontWeight: 700, color: '#1A7A3C', marginBottom: 6 }}>BizPadi</div>
            <div style={{ display: 'flex', gap: 2, marginBottom: 4 }}>
              {[1,2,3,4,5].map(i => (
                <svg key={i} width="11" height="11" viewBox="0 0 24 24" fill="#F59E0B">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
              ))}
            </div>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#0C1A0E' }}>Applied for TEF successfully!</div>
            <div style={{ fontSize: '0.62rem', color: '#6B7280', marginTop: 2 }}>Chisom got step-by-step guidance</div>
            <div style={{ fontSize: '0.58rem', color: '#999', textAlign: 'right', marginTop: 4 }}>9:44 AM</div>
          </div>
        </div>
      </div>

      {/* Input bar */}
      <div style={{
        background: '#F0F0F0',
        padding: '0.6rem 0.75rem',
        display: 'flex', alignItems: 'center', gap: '0.5rem',
        borderTop: '1px solid rgba(0,0,0,0.06)',
      }}>
        <div style={{
          flex: 1, background: '#fff',
          borderRadius: 100, padding: '0.38rem 0.75rem',
          fontSize: '0.7rem', color: '#999',
          fontFamily: 'Montserrat, sans-serif',
        }}>
          Message
        </div>
        <div style={{
          width: 32, height: 32,
          background: '#25D366', borderRadius: '50%',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </div>
      </div>
    </div>
  )
}
