import React, { useState, useRef, useEffect, useCallback } from 'react'
import { WA_LINK } from '../lib/constants'
import { WhatsappIcon } from '../lib/icons'

const SIZE = 58
const EDGE = 24

export default function WhatsAppWidget() {
  const [pos, setPos] = useState(null)
  const dragging = useRef(false)
  const moved = useRef(false)
  const origin = useRef({ mx: 0, my: 0, px: 0, py: 0 })

  /* Anchor to bottom-right on mount. */
  useEffect(() => {
    setPos({
      x: window.innerWidth - SIZE - EDGE,
      y: window.innerHeight - SIZE - EDGE,
    })
  }, [])

  const clamp = (x, y) => ({
    x: Math.max(EDGE / 2, Math.min(window.innerWidth - SIZE - EDGE / 2, x)),
    y: Math.max(EDGE / 2, Math.min(window.innerHeight - SIZE - EDGE / 2, y)),
  })

  const onDown = (clientX, clientY) => {
    dragging.current = true
    moved.current = false
    origin.current = { mx: clientX, my: clientY, px: pos.x, py: pos.y }
  }

  const onMove = useCallback((clientX, clientY) => {
    if (!dragging.current) return
    const dx = clientX - origin.current.mx
    const dy = clientY - origin.current.my
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) moved.current = true
    setPos(clamp(origin.current.px + dx, origin.current.py + dy))
  }, [])

  useEffect(() => {
    const mm = (e) => onMove(e.clientX, e.clientY)
    const tm = (e) => {
      if (!dragging.current) return
      onMove(e.touches[0].clientX, e.touches[0].clientY)
      e.preventDefault()
    }
    const end = () => { dragging.current = false }
    window.addEventListener('mousemove', mm)
    window.addEventListener('mouseup', end)
    window.addEventListener('touchmove', tm, { passive: false })
    window.addEventListener('touchend', end)
    return () => {
      window.removeEventListener('mousemove', mm)
      window.removeEventListener('mouseup', end)
      window.removeEventListener('touchmove', tm)
      window.removeEventListener('touchend', end)
    }
  }, [onMove])

  if (!pos) return null

  return (
    <div
      className="wa-widget"
      style={{ left: pos.x, top: pos.y }}
      onMouseDown={(e) => { e.preventDefault(); onDown(e.clientX, e.clientY) }}
      onTouchStart={(e) => onDown(e.touches[0].clientX, e.touches[0].clientY)}
    >
      <a
        href={WA_LINK}
        target="_blank"
        rel="noreferrer"
        className="wa-fab"
        aria-label="Chat with BizPadi on WhatsApp"
        onClick={(e) => { if (moved.current) e.preventDefault() }}
      >
        <WhatsappIcon size={28} />
        <span className="wa-notif">1</span>
      </a>
      <span className="wa-tooltip">Chat with BizPadi</span>
    </div>
  )
}
