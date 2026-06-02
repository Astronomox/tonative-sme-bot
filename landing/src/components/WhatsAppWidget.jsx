import React, { useState, useRef, useEffect } from 'react'

const WA_LINK = 'https://wa.me/14155238886?text=Hello%2C%20I%20want%20to%20find%20funding%20for%20my%20business'

export default function WhatsAppWidget() {
  const [pos, setPos] = useState({ x: null, y: null })
  const [dragging, setDragging] = useState(false)
  const [hasDragged, setHasDragged] = useState(false)
  const [hovered, setHovered] = useState(false)
  const startRef = useRef({})
  const widgetRef = useRef(null)

  // Init position from bottom-right
  useEffect(() => {
    setPos({
      x: window.innerWidth - 88,
      y: window.innerHeight - 88,
    })
  }, [])

  const onMouseDown = (e) => {
    e.preventDefault()
    setDragging(true)
    setHasDragged(false)
    startRef.current = {
      mx: e.clientX, my: e.clientY,
      px: pos.x, py: pos.y,
    }
  }

  useEffect(() => {
    const onMove = (e) => {
      if (!dragging) return
      const dx = e.clientX - startRef.current.mx
      const dy = e.clientY - startRef.current.my
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) setHasDragged(true)
      const newX = Math.max(0, Math.min(window.innerWidth - 58, startRef.current.px + dx))
      const newY = Math.max(0, Math.min(window.innerHeight - 58, startRef.current.py + dy))
      setPos({ x: newX, y: newY })
    }
    const onUp = () => setDragging(false)
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    return () => {
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
  }, [dragging])

  const handleClick = (e) => {
    if (hasDragged) e.preventDefault()
  }

  if (pos.x === null) return null

  return (
    <div
      ref={widgetRef}
      onMouseDown={onMouseDown}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        position: 'fixed',
        left: pos.x, top: pos.y,
        zIndex: 9999,
        cursor: dragging ? 'grabbing' : 'grab',
        userSelect: 'none',
        touchAction: 'none',
      }}
    >
      {/* Tooltip */}
      {hovered && !dragging && (
        <div style={{
          position: 'absolute',
          right: 68, top: '50%',
          transform: 'translateY(-50%)',
          background: 'var(--ink)',
          color: '#fff',
          fontFamily: 'Montserrat, sans-serif',
          fontSize: '0.75rem', fontWeight: 600,
          padding: '0.4rem 0.9rem',
          borderRadius: 100,
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
          boxShadow: 'var(--shadow)',
        }}>
          Chat with BizPadi
        </div>
      )}

      <a
        href={WA_LINK}
        target="_blank"
        rel="noreferrer"
        onClick={handleClick}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          width: 56, height: 56,
          background: '#25D366',
          borderRadius: '50%',
          boxShadow: '0 4px 20px rgba(37,211,102,0.45)',
          animation: 'pulse-green 2.5s ease infinite',
          transition: 'transform 0.2s',
          transform: hovered && !dragging ? 'scale(1.1)' : 'scale(1)',
          position: 'relative',
        }}
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="white">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
        </svg>
        {/* Notification dot */}
        <div style={{
          position: 'absolute', top: -2, right: -2,
          width: 14, height: 14,
          background: '#EF4444', borderRadius: '50%',
          border: '2px solid var(--bg)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.5rem', color: '#fff', fontWeight: 700,
        }}>
          1
        </div>
      </a>
    </div>
  )
}
