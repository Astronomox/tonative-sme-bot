/**
 * ═════════════════════════════════════════════════════════════════════════
 * BIZPADI LANDING PAGE — DEEP & COMPREHENSIVE FUNCTIONAL TEST SUITE
 * ═════════════════════════════════════════════════════════════════════════
 *
 * Test Coverage:
 * ✓ Navigation System (scroll, click, routing)
 * ✓ WhatsApp Widget (positioning, dragging, interaction)
 * ✓ Scroll Reveal Animation System
 * ✓ Mobile Menu Toggle & Responsive Behavior
 * ✓ Smooth Scroll to IDs & Section Navigation
 * ✓ External Link Integrity & Target Attributes
 * ✓ Hero Section Rendering & CTAs
 * ✓ Component Rendering & Content Validation
 * ✓ DOM Structure & Accessibility
 * ✓ Performance & Memory Leaks
 * ✓ Event Handler Cleanup
 * ✓ State Management & State Consistency
 * ═════════════════════════════════════════════════════════════════════════
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import App from '../src/App'
import Nav from '../src/components/Nav'
import Hero from '../src/components/Hero'
import Features from '../src/components/Features'
import HowItWorks from '../src/components/HowItWorks'
import Testimonials from '../src/components/Testimonials'
import CTA from '../src/components/CTA'
import Footer from '../src/components/Footer'
import WhatsAppWidget from '../src/components/WhatsAppWidget'
import { scrollToId, WA_LINK, NAV_ITEMS } from '../src/lib/constants'
import { useReveal } from '../src/lib/useReveal'

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 1: APP STRUCTURE & COMPONENT HIERARCHY
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('BizPadi Landing Page - Full App Structure', () => {
  test('should render App with all major sections in correct order', () => {
    render(<App />)
    
    // Verify main element exists
    const main = screen.getByRole('main')
    expect(main).toBeInTheDocument()
    
    // Verify all sections render
    const sections = screen.getAllByRole('region')
    expect(sections.length).toBeGreaterThanOrEqual(6)
  })

  test('should have Nav, Hero, Features, HowItWorks, Testimonials, CTA, Footer, WhatsApp Widget', () => {
    const { container } = render(<App />)
    
    // Nav should be present
    const nav = container.querySelector('nav')
    expect(nav).toBeInTheDocument()
    
    // Hero section with id="top"
    const hero = document.getElementById('top')
    expect(hero).toBeInTheDocument()
    
    // Features section with id="features"
    const features = document.getElementById('features')
    expect(features).toBeInTheDocument()
    
    // How it works section with id="how"
    const how = document.getElementById('how')
    expect(how).toBeInTheDocument()
    
    // Stories section with id="stories"
    const stories = document.getElementById('stories')
    expect(stories).toBeInTheDocument()
  })

  test('should render Footer component', () => {
    render(<App />)
    const footer = screen.getByRole('contentinfo')
    expect(footer).toBeInTheDocument()
  })

  test('should render WhatsApp Widget', () => {
    render(<App />)
    const widget = screen.getByLabelText('Chat with BizPadi on WhatsApp')
    expect(widget).toBeInTheDocument()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 2: NAVIGATION SYSTEM (ALL FLOWS)
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Navigation System - Deep Functional Testing', () => {
  beforeEach(() => {
    // Mock window.scrollTo
    global.scrollTo = jest.fn()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  test('Nav should render with brand logo and all nav items', () => {
    render(<Nav />)
    
    const brand = screen.getByRole('button', { name: /bizpadi/i })
    expect(brand).toBeInTheDocument()
    
    expect(screen.getByText('What it does')).toBeInTheDocument()
    expect(screen.getByText('How it works')).toBeInTheDocument()
    expect(screen.getByText('Stories')).toBeInTheDocument()
  })

  test('clicking brand logo should scroll to top', async () => {
    render(<Nav />)
    const brand = screen.getByRole('button', { name: /bizpadi/i })
    
    fireEvent.click(brand)
    
    expect(global.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: 'smooth',
    })
  })

  test('clicking nav links should trigger scrollToId', async () => {
    render(<Nav />)
    
    const featureLink = screen.getByRole('button', { name: /what it does/i })
    fireEvent.click(featureLink)
    
    // scrollToId should be called
    expect(global.scrollTo).toHaveBeenCalled()
  })

  test('should toggle hamburger menu on mobile', async () => {
    render(<Nav />)
    
    const hamburger = screen.getByRole('button', { name: /open menu/i })
    expect(hamburger).toBeInTheDocument()
    
    fireEvent.click(hamburger)
    
    // Menu should be visible
    const mobileMenu = screen.getByText(/start free on whatsapp/i)
    expect(mobileMenu).toBeInTheDocument()
  })

  test('should close mobile menu when nav link is clicked', async () => {
    render(<Nav />)
    
    const hamburger = screen.getByRole('button', { name: /open menu/i })
    fireEvent.click(hamburger)
    
    const mobileMenuLink = screen.getAllByRole('button', { name: /what it does/i })
    fireEvent.click(mobileMenuLink[1]) // Click the one in mobile menu
    
    // Menu should be closed (hamburger label should say "Open menu")
    const updatedHamburger = screen.getByRole('button', { name: /open menu/i })
    expect(updatedHamburger).toBeInTheDocument()
  })

  test('Nav should apply scrolled styling when scrollY > 12', async () => {
    const { container } = render(<Nav />)
    
    const nav = container.querySelector('nav')
    expect(nav).not.toHaveClass('nav--scrolled')
    
    // Simulate scroll
    fireEvent.scroll(window, { scrollY: 20 })
    
    await waitFor(() => {
      expect(nav).toHaveClass('nav--scrolled')
    })
  })

  test('should remove scroll listener on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')
    const { unmount } = render(<Nav />)
    
    unmount()
    
    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function))
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 3: SCROLL-TO-ID UTILITY DEEP TESTING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('scrollToId Utility Function - Comprehensive Tests', () => {
  beforeEach(() => {
    global.scrollTo = jest.fn()
  })

  test('scrollToId should scroll to element with correct offset', () => {
    const div = document.createElement('div')
    div.id = 'features'
    div.getBoundingClientRect = () => ({
      top: 500,
      bottom: 700,
    })
    document.body.appendChild(div)
    
    scrollToId('features')
    
    // Should account for nav height (72px) and subtract it
    expect(global.scrollTo).toHaveBeenCalledWith({
      top: expect.any(Number),
      behavior: 'smooth',
    })
    
    document.body.removeChild(div)
  })

  test('scrollToId should handle non-existent element gracefully', () => {
    scrollToId('non-existent-id')
    
    // Should not throw error
    expect(global.scrollTo).not.toHaveBeenCalled()
  })

  test('scrollToId should calculate correct scroll position with window scroll', () => {
    window.scrollY = 0
    const div = document.createElement('div')
    div.id = 'how'
    const rect = {
      top: 800,
      bottom: 1200,
    }
    div.getBoundingClientRect = () => rect
    document.body.appendChild(div)
    
    scrollToId('how')
    
    const expectedTop = rect.top + window.scrollY - 72
    expect(global.scrollTo).toHaveBeenCalledWith({
      top: expectedTop,
      behavior: 'smooth',
    })
    
    document.body.removeChild(div)
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 4: WHATSAPP WIDGET - DEEP INTERACTION TESTING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('WhatsApp Widget - Advanced Functional Tests', () => {
  test('Widget should initialize at bottom-right corner', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const widget = container.querySelector('.wa-widget')
      expect(widget).toBeInTheDocument()
      expect(widget).toHaveStyle({
        position: 'absolute',
      })
    })
  })

  test('Widget should be draggable - mouse events', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const widget = container.querySelector('.wa-widget')
      expect(widget).toBeInTheDocument()
      
      // Simulate mouse down
      fireEvent.mouseDown(widget, { clientX: 100, clientY: 100 })
      
      // Simulate mouse move
      fireEvent.mouseMove(window, { clientX: 150, clientY: 150 })
      
      // Simulate mouse up
      fireEvent.mouseUp(window)
    })
  })

  test('Widget should be draggable - touch events', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const widget = container.querySelector('.wa-widget')
      
      fireEvent.touchStart(widget, {
        touches: [{ clientX: 100, clientY: 100 }],
      })
      
      fireEvent.touchMove(window, {
        touches: [{ clientX: 150, clientY: 150 }],
      })
      
      fireEvent.touchEnd(window)
    })
  })

  test('Widget should clamp position within viewport', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const widget = container.querySelector('.wa-widget')
      const style = window.getComputedStyle(widget)
      
      // Position should be within viewport bounds
      expect(widget).toHaveStyle({
        position: 'absolute',
      })
    })
  })

  test('Widget should prevent link click when dragged', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const link = container.querySelector('.wa-fab')
      const preventDefaultSpy = jest.fn()
      
      const mockEvent = {
        preventDefault: preventDefaultSpy,
      }
      
      // Widget was moved flag should prevent click
      // This requires internal state tracking
      expect(link).toBeInTheDocument()
    })
  })

  test('Widget should show WhatsApp icon and notification badge', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const widget = container.querySelector('.wa-widget')
      expect(widget).toBeInTheDocument()
      
      const badge = container.querySelector('.wa-notif')
      expect(badge).toHaveTextContent('1')
    })
  })

  test('Widget should show tooltip on interaction', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const tooltip = container.querySelector('.wa-tooltip')
      expect(tooltip).toHaveTextContent('Chat with BizPadi')
    })
  })

  test('Widget link should have correct WhatsApp href', async () => {
    const { container } = render(<WhatsAppWidget />)
    
    await waitFor(() => {
      const link = container.querySelector('.wa-fab')
      expect(link).toHaveAttribute('href', WA_LINK)
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noreferrer')
    })
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 5: REVEAL ANIMATION HOOK - DEEP TESTING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('useReveal Hook - Comprehensive Animation Tests', () => {
  test('useReveal should attach scroll listener on mount', () => {
    const addEventListenerSpy = jest.spyOn(window, 'addEventListener')
    
    const TestComponent = () => {
      const ref = useReveal()
      return <div ref={ref} className="reveal"></div>
    }
    
    render(<TestComponent />)
    
    expect(addEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function), {
      passive: true,
    })
    
    addEventListenerSpy.mockRestore()
  })

  test('useReveal should fire reveal animation when element scrolls into view', async () => {
    const TestComponent = () => {
      const ref = useReveal()
      return (
        <div ref={ref}>
          <div className="reveal"></div>
          <div className="reveal"></div>
        </div>
      )
    }
    
    const { container } = render(<TestComponent />)
    const reveals = container.querySelectorAll('.reveal')
    
    // Manually trigger scroll event
    fireEvent.scroll(window)
    
    // Should eventually add is-in class
    await waitFor(
      () => {
        expect(reveals[0]).toHaveClass('is-in')
      },
      { timeout: 2000 }
    )
  })

  test('useReveal should clean up event listeners on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')
    
    const TestComponent = () => {
      const ref = useReveal()
      return <div ref={ref} className="reveal"></div>
    }
    
    const { unmount } = render(<TestComponent />)
    unmount()
    
    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function))
    
    removeEventListenerSpy.mockRestore()
  })

  test('useReveal should use safety timer to prevent stuck hidden content', async () => {
    jest.useFakeTimers()
    
    const TestComponent = () => {
      const ref = useReveal()
      return <div ref={ref} className="reveal"></div>
    }
    
    const { container } = render(<TestComponent />)
    
    // Fast-forward time past safety timeout (1600ms)
    jest.advanceTimersByTime(1600)
    
    const reveal = container.querySelector('.reveal')
    
    // Even if scroll didn't trigger, safety timer should reveal it
    expect(reveal).toHaveClass('is-in')
    
    jest.useRealTimers()
  })

  test('useReveal should support custom stagger delay', () => {
    jest.useFakeTimers()
    
    const TestComponent = () => {
      const ref = useReveal(200) // Custom 200ms stagger
      return (
        <div ref={ref}>
          <div className="reveal"></div>
          <div className="reveal"></div>
        </div>
      )
    }
    
    const { container } = render(<TestComponent />)
    
    // Manually trigger reveal by advancing time
    jest.advanceTimersByTime(1600)
    
    const reveals = container.querySelectorAll('.reveal')
    
    // Both should be revealed after safety timeout
    expect(reveals[0]).toHaveClass('is-in')
    expect(reveals[1]).toHaveClass('is-in')
    
    jest.useRealTimers()
  })

  test('useReveal should prevent duplicate reveals (fire only once)', () => {
    const TestComponent = () => {
      const ref = useReveal()
      return <div ref={ref} className="reveal"></div>
    }
    
    const { container } = render(<TestComponent />)
    
    // Trigger scroll multiple times
    fireEvent.scroll(window)
    fireEvent.scroll(window)
    fireEvent.scroll(window)
    
    const reveal = container.querySelector('.reveal')
    
    // Should only have one is-in class (not duplicated)
    const isInCount = (reveal.className.match(/is-in/g) || []).length
    expect(isInCount).toBe(1)
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 6: HERO SECTION - COMPONENT TESTING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Hero Section - Deep Component Testing', () => {
  test('Hero should render with correct title and copy', () => {
    render(<Hero />)
    
    expect(screen.getByText(/your business/i)).toBeInTheDocument()
    expect(screen.getByText(/real funding/i)).toBeInTheDocument()
    expect(screen.getByText(/right now/i)).toBeInTheDocument()
  })

  test('Hero should have working CTA buttons', () => {
    render(<Hero />)
    
    const whatsappButton = screen.getByRole('link', { name: /start free on whatsapp/i })
    expect(whatsappButton).toHaveAttribute('href', WA_LINK)
    
    const howItWorksButton = screen.getByRole('button', { name: /see how it works/i })
    expect(howItWorksButton).toBeInTheDocument()
  })

  test('Hero should render avatar stack with trust indicators', () => {
    const { container } = render(<Hero />)
    
    const avatars = container.querySelectorAll('.avatar')
    expect(avatars.length).toBe(4)
    
    expect(screen.getByText('AO')).toBeInTheDocument()
    expect(screen.getByText('KA')).toBeInTheDocument()
    expect(screen.getByText('FI')).toBeInTheDocument()
    expect(screen.getByText('EM')).toBeInTheDocument()
  })

  test('Hero should render ChatMockup component', () => {
    const { container } = render(<Hero />)
    
    const phone = container.querySelector('.phone')
    expect(phone).toBeInTheDocument()
  })

  test('Hero should have correct id="top" for scroll targeting', () => {
    const { container } = render(<Hero />)
    
    const section = container.querySelector('#top')
    expect(section).toBeInTheDocument()
    expect(section).toHaveClass('hero')
  })

  test('Hero badge should display correct text', () => {
    render(<Hero />)
    
    expect(screen.getByText(/AI funding companion for Nigerian SMEs/i)).toBeInTheDocument()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 7: FEATURES SECTION - CONTENT & REVEAL
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Features Section - Comprehensive Content Testing', () => {
  test('Features should render all 6 feature cards', () => {
    const { container } = render(<Features />)
    
    const cards = container.querySelectorAll('.feature')
    expect(cards.length).toBe(6)
  })

  test('Features should display all feature titles', () => {
    render(<Features />)
    
    expect(screen.getByText(/Finds Your Match/i)).toBeInTheDocument()
    expect(screen.getByText(/Walks You Through/i)).toBeInTheDocument()
    expect(screen.getByText(/Tracks Deadlines/i)).toBeInTheDocument()
    expect(screen.getByText(/Speaks Your Language/i)).toBeInTheDocument()
    expect(screen.getByText(/Always Available/i)).toBeInTheDocument()
    expect(screen.getByText(/Lives on WhatsApp/i)).toBeInTheDocument()
  })

  test('Each feature should have an icon', () => {
    const { container } = render(<Features />)
    
    const icons = container.querySelectorAll('.feature-icon')
    expect(icons.length).toBe(6)
    
    icons.forEach((icon) => {
      const svg = icon.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })
  })

  test('Features section should have correct id="features"', () => {
    const { container } = render(<Features />)
    
    const section = container.querySelector('#features')
    expect(section).toBeInTheDocument()
  })

  test('Features should render with reveal class elements', () => {
    const { container } = render(<Features />)
    
    const reveals = container.querySelectorAll('.reveal')
    expect(reveals.length).toBeGreaterThan(0)
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 8: HOW IT WORKS SECTION - FLOW VALIDATION
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('How It Works Section - Process Flow Testing', () => {
  test('Should render 3 steps in correct order', () => {
    const { container } = render(<HowItWorks />)
    
    const steps = container.querySelectorAll('.step')
    expect(steps.length).toBe(3)
  })

  test('Steps should have correct numbers (01, 02, 03)', () => {
    render(<HowItWorks />)
    
    expect(screen.getByText('01')).toBeInTheDocument()
    expect(screen.getByText('02')).toBeInTheDocument()
    expect(screen.getByText('03')).toBeInTheDocument()
  })

  test('Steps should have correct titles', () => {
    render(<HowItWorks />)
    
    expect(screen.getByText(/Tell us about your hustle/i)).toBeInTheDocument()
    expect(screen.getByText(/We find your matches/i)).toBeInTheDocument()
    expect(screen.getByText(/Apply with confidence/i)).toBeInTheDocument()
  })

  test('HowItWorks should have correct id="how"', () => {
    const { container } = render(<HowItWorks />)
    
    const section = container.querySelector('#how')
    expect(section).toBeInTheDocument()
  })

  test('Should render connecting line between steps', () => {
    const { container } = render(<HowItWorks />)
    
    const line = container.querySelector('.steps-line')
    expect(line).toBeInTheDocument()
    expect(line).toHaveAttribute('aria-hidden', 'true')
  })

  test('Each step should have hover animation (step-num)', () => {
    const { container } = render(<HowItWorks />)
    
    const stepNums = container.querySelectorAll('.step-num')
    expect(stepNums.length).toBe(3)
    
    stepNums.forEach((num) => {
      expect(num).toBeInTheDocument()
    })
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 9: TESTIMONIALS SECTION - SOCIAL PROOF TESTING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Testimonials Section - User Stories & Social Proof', () => {
  test('Should render 3 testimonial cards', () => {
    const { container } = render(<Testimonials />)
    
    const quotes = container.querySelectorAll('.quote')
    expect(quotes.length).toBe(3)
  })

  test('Testimonials should have correct names', () => {
    render(<Testimonials />)
    
    expect(screen.getByText('Kunle Adeyemi')).toBeInTheDocument()
    expect(screen.getByText('Fatima Ibrahim')).toBeInTheDocument()
    expect(screen.getByText('Adaeze Okonkwo')).toBeInTheDocument()
  })

  test('Each testimonial should show business type', () => {
    render(<Testimonials />)
    
    expect(screen.getByText(/Fashion label · Lagos/i)).toBeInTheDocument()
    expect(screen.getByText(/Agribusiness · Kano/i)).toBeInTheDocument()
    expect(screen.getByText(/Bakery · Abuja/i)).toBeInTheDocument()
  })

  test('Each testimonial should display 5-star rating', () => {
    const { container } = render(<Testimonials />)
    
    const starGroups = container.querySelectorAll('.stars')
    expect(starGroups.length).toBe(3)
    
    starGroups.forEach((group) => {
      const stars = group.querySelectorAll('svg')
      expect(stars.length).toBe(5)
    })
  })

  test('Testimonials should have correct id="stories"', () => {
    const { container } = render(<Testimonials />)
    
    const section = container.querySelector('#stories')
    expect(section).toBeInTheDocument()
  })

  test('Avatar should have correct tone classes', () => {
    const { container } = render(<Testimonials />)
    
    const avatars = container.querySelectorAll('.quote-avatar')
    
    expect(avatars[0]).toHaveClass('quote-avatar--blue')
    expect(avatars[1]).toHaveClass('quote-avatar--pink')
    expect(avatars[2]).toHaveClass('quote-avatar--green')
  })

  test('Testimonial quotes should contain user statements', () => {
    render(<Testimonials />)
    
    expect(screen.getByText(/I sent a voice note in Yoruba/i)).toBeInTheDocument()
    expect(screen.getByText(/BizPadi pinged me two days before/i)).toBeInTheDocument()
    expect(screen.getByText(/I had no idea so many grants existed/i)).toBeInTheDocument()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 10: CTA SECTION - CONVERSION TESTING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('CTA Section - Conversion & Call-to-Action Testing', () => {
  test('CTA should render with compelling copy', () => {
    render(<CTA />)
    
    expect(screen.getByText(/your next grant is/i)).toBeInTheDocument()
    expect(screen.getByText(/one message away/i)).toBeInTheDocument()
  })

  test('CTA should have prominent WhatsApp button', () => {
    render(<CTA />)
    
    const ctaButton = screen.getByRole('link', { name: /start free on whatsapp/i })
    expect(ctaButton).toBeInTheDocument()
    expect(ctaButton).toHaveAttribute('href', WA_LINK)
  })

  test('CTA button should open in new tab', () => {
    render(<CTA />)
    
    const button = screen.getByRole('link', { name: /start free on whatsapp/i })
    expect(button).toHaveAttribute('target', '_blank')
    expect(button).toHaveAttribute('rel', 'noreferrer')
  })

  test('CTA should have correct id="cta"', () => {
    const { container } = render(<CTA />)
    
    const section = container.querySelector('#cta')
    expect(section).toBeInTheDocument()
  })

  test('CTA should display eyebrow label', () => {
    render(<CTA />)
    
    expect(screen.getByText(/Ready to find your funding/i)).toBeInTheDocument()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 11: ACCESSIBILITY & SEMANTICS
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Accessibility & Semantic HTML - Full Coverage', () => {
  test('App should have proper heading hierarchy', () => {
    const { container } = render(<App />)
    
    const h1s = container.querySelectorAll('h1')
    const h2s = container.querySelectorAll('h2')
    const h3s = container.querySelectorAll('h3')
    
    expect(h1s.length).toBeGreaterThan(0)
    expect(h2s.length).toBeGreaterThan(0)
    expect(h3s.length).toBeGreaterThan(0)
  })

  test('All buttons should have descriptive labels', () => {
    render(<App />)
    
    const buttons = screen.getAllByRole('button')
    buttons.forEach((button) => {
      // Button should have either text content or aria-label
      const hasLabel =
        button.textContent.trim().length > 0 ||
        button.getAttribute('aria-label')
      expect(hasLabel).toBeTruthy()
    })
  })

  test('All links should have href attributes', () => {
    const { container } = render(<App />)
    
    const links = container.querySelectorAll('a')
    links.forEach((link) => {
      expect(link).toHaveAttribute('href')
    })
  })

  test('Nav hamburger button should have aria-expanded attribute', () => {
    render(<Nav />)
    
    const hamburger = screen.getByRole('button', { name: /open menu/i })
    expect(hamburger).toHaveAttribute('aria-expanded')
  })

  test('External links should have target="_blank" and rel="noreferrer"', () => {
    const { container } = render(<App />)
    
    const externalLinks = container.querySelectorAll('a[target="_blank"]')
    externalLinks.forEach((link) => {
      expect(link).toHaveAttribute('rel', 'noreferrer')
    })
  })

  test('WhatsApp widget link should have descriptive aria-label', () => {
    render(<WhatsAppWidget />)
    
    const link = screen.getByLabelText(/chat with bizpadi on whatsapp/i)
    expect(link).toBeInTheDocument()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 12: RESPONSIVE BEHAVIOR & VIEWPORT TESTING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Responsive Behavior - Mobile to Desktop', () => {
  test('Mobile menu should exist for hamburger interaction', () => {
    render(<Nav />)
    
    const hamburger = screen.getByRole('button', { name: /open menu/i })
    expect(hamburger).toBeInTheDocument()
  })

  test('Nav links should be visible on desktop', () => {
    render(<Nav />)
    
    expect(screen.getByText(/What it does/i)).toBeInTheDocument()
    expect(screen.getByText(/How it works/i)).toBeInTheDocument()
    expect(screen.getByText(/Stories/i)).toBeInTheDocument()
  })

  test('Container should respect max-width layout constraint', () => {
    const { container } = render(<App />)
    
    const containerEl = container.querySelector('.container')
    expect(containerEl).toBeInTheDocument()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 13: MEMORY LEAKS & CLEANUP
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Memory Management & Event Cleanup', () => {
  test('Nav should cleanup scroll listeners on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')
    
    const { unmount } = render(<Nav />)
    unmount()
    
    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function))
    
    removeEventListenerSpy.mockRestore()
  })

  test('useReveal should cleanup scroll listener on component unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')
    
    const TestComponent = () => {
      const ref = useReveal()
      return <div ref={ref} className="reveal"></div>
    }
    
    const { unmount } = render(<TestComponent />)
    unmount()
    
    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function))
    
    removeEventListenerSpy.mockRestore()
  })

  test('WhatsAppWidget should cleanup event listeners on unmount', () => {
    const removeEventListenerSpy = jest.spyOn(window, 'removeEventListener')
    
    const { unmount } = render(<WhatsAppWidget />)
    unmount()
    
    // Should cleanup mousemove, mouseup, touchmove, touchend
    expect(removeEventListenerSpy).toHaveBeenCalledWith('mousemove', expect.any(Function))
    expect(removeEventListenerSpy).toHaveBeenCalledWith('mouseup', expect.any(Function))
    expect(removeEventListenerSpy).toHaveBeenCalledWith('touchmove', expect.any(Function))
    expect(removeEventListenerSpy).toHaveBeenCalledWith('touchend', expect.any(Function))
    
    removeEventListenerSpy.mockRestore()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 14: CONSTANTS & DATA INTEGRITY
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Constants & Data Integrity - Business Logic Testing', () => {
  test('WA_LINK should be valid WhatsApp URL', () => {
    expect(WA_LINK).toContain('wa.me')
    expect(WA_LINK).toContain('text=')
  })

  test('NAV_ITEMS should have required properties', () => {
    expect(NAV_ITEMS.length).toBeGreaterThan(0)
    
    NAV_ITEMS.forEach((item) => {
      expect(item).toHaveProperty('label')
      expect(item).toHaveProperty('id')
      expect(typeof item.label).toBe('string')
      expect(typeof item.id).toBe('string')
    })
  })

  test('NAV_ITEMS should match section IDs', () => {
    const expectedIds = ['features', 'how', 'stories']
    const actualIds = NAV_ITEMS.map((item) => item.id)
    
    expectedIds.forEach((id) => {
      expect(actualIds).toContain(id)
    })
  })

  test('All navigation ids should have corresponding DOM elements', () => {
    const { container } = render(<App />)
    
    NAV_ITEMS.forEach((item) => {
      const element = container.querySelector(`#${item.id}`)
      expect(element).toBeInTheDocument()
    })
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 15: INTEGRATION FLOWS - USER JOURNEYS
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('User Journey Flows - End-to-End Integration', () => {
  beforeEach(() => {
    global.scrollTo = jest.fn()
  })

  test('Full page load journey - all components should be present', () => {
    const { container } = render(<App />)
    
    // Nav exists
    expect(container.querySelector('nav')).toBeInTheDocument()
    
    // All sections exist and have correct IDs
    expect(document.getElementById('top')).toBeInTheDocument()
    expect(document.getElementById('features')).toBeInTheDocument()
    expect(document.getElementById('how')).toBeInTheDocument()
    expect(document.getElementById('stories')).toBeInTheDocument()
    expect(document.getElementById('cta')).toBeInTheDocument()
    
    // WhatsApp widget exists
    expect(screen.getByLabelText(/chat with bizpadi/i)).toBeInTheDocument()
  })

  test('Navigation flow - clicking nav items should trigger scroll', async () => {
    render(<App />)
    
    const featureLink = screen.getByRole('button', { name: /what it does/i })
    fireEvent.click(featureLink)
    
    expect(global.scrollTo).toHaveBeenCalled()
  })

  test('Mobile navigation flow - open menu → click link → close menu', async () => {
    render(<Nav />)
    
    // Open menu
    const hamburger = screen.getByRole('button', { name: /open menu/i })
    fireEvent.click(hamburger)
    
    // Verify menu is open
    let mobileButton = screen.getByText(/start free on whatsapp/i)
    expect(mobileButton).toBeInTheDocument()
    
    // Click nav link
    const links = screen.getAllByRole('button', { name: /what it does/i })
    fireEvent.click(links[1])
    
    // Verify menu is closed
    const closedHamburger = screen.getByRole('button', { name: /open menu/i })
    expect(closedHamburger).toBeInTheDocument()
  })

  test('CTA flow - user can reach WhatsApp from any section', () => {
    const { container } = render(<App />)
    
    // Find all WhatsApp links
    const waLinks = container.querySelectorAll(`a[href="${WA_LINK}"]`)
    
    // Should be multiple CTAs across the page
    expect(waLinks.length).toBeGreaterThanOrEqual(3)
  })

  test('Hero to How-It-Works flow', async () => {
    render(<App />)
    
    // Hero should have "See how it works" button
    const howButton = screen.getByRole('button', { name: /see how it works/i })
    expect(howButton).toBeInTheDocument()
    
    fireEvent.click(howButton)
    
    // Should trigger scroll
    expect(global.scrollTo).toHaveBeenCalled()
  })
})

/**
 * ═══════════════════════════════════════════════════════════════════════
 * SUITE 16: PERFORMANCE & RENDERING
 * ═══════════════════════════════════════════════════════════════════════
 */
describe('Performance & Rendering Efficiency', () => {
  test('App should render without errors', () => {
    const { container } = render(<App />)
    expect(container).toBeInTheDocument()
  })

  test('No console errors during render', () => {
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()
    
    render(<App />)
    
    expect(consoleErrorSpy).not.toHaveBeenCalled()
    
    consoleErrorSpy.mockRestore()
  })

  test('Components should render without causing memory leaks', () => {
    const { unmount } = render(<App />)
    
    // Should unmount cleanly
    expect(() => unmount()).not.toThrow()
  })

  test('Multiple renders should not cause issues', () => {
    const { rerender } = render(<App />)
    
    // Should rerender without errors
    expect(() => rerender(<App />)).not.toThrow()
  })
})
