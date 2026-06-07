import { useEffect, useRef } from 'react'

/* Reveals `.reveal` children when the section scrolls into view.
   Uses scroll + an initial check + a safety timer so content can never
   get stuck hidden (works even if IntersectionObserver misbehaves). */
export function useReveal(stagger = 90) {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    let done = false

    const fire = () => {
      if (done) return
      done = true
      el.querySelectorAll('.reveal').forEach((node, i) => {
        setTimeout(() => node.classList.add('is-in'), i * stagger)
      })
      window.removeEventListener('scroll', onScroll)
    }

    const onScroll = () => {
      const rect = el.getBoundingClientRect()
      if (rect.top < window.innerHeight * 0.88 && rect.bottom > 0) fire()
    }

    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    const safety = setTimeout(fire, 1600)

    return () => {
      window.removeEventListener('scroll', onScroll)
      clearTimeout(safety)
    }
  }, [stagger])
  return ref
}
