/* Single source of truth for the WhatsApp deep link + nav targets. */
export const WA_LINK = 'https://wa.me/14155238886?text=join%20industry-plain'

export const NAV_ITEMS = [
  { label: 'What it does', id: 'features' },
  { label: 'How it works', id: 'how' },
  { label: 'Stories', id: 'stories' },
]

/* JS smooth scroll — no hash URLs. */
export function scrollToId(id) {
  const el = document.getElementById(id)
  if (!el) return
  const top = el.getBoundingClientRect().top + window.scrollY - 72
  window.scrollTo({ top, behavior: 'smooth' })
}
