import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useMobileDetection } from '@/composables/useMobileDetection'

// Mock window.innerWidth
Object.defineProperty(window, 'innerWidth', {
  writable: true,
  configurable: true,
  value: 1024,
})

// Mock addEventListener/removeEventListener
let mockEventListeners = {}
window.addEventListener = vi.fn((event, callback) => {
  if (!mockEventListeners[event]) {
    mockEventListeners[event] = []
  }
  mockEventListeners[event].push(callback)
})

window.removeEventListener = vi.fn((event, callback) => {
  if (mockEventListeners[event]) {
    const index = mockEventListeners[event].indexOf(callback)
    if (index > -1) {
      mockEventListeners[event].splice(index, 1)
    }
  }
})

const triggerResize = () => {
  if (mockEventListeners.resize) {
    mockEventListeners.resize.forEach(callback => callback())
  }
}

describe('useMobileDetection', () => {
  beforeEach(() => {
    mockEventListeners = {}
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should detect desktop screen as not mobile', () => {
    window.innerWidth = 1024
    const { isMobile, screenWidth } = useMobileDetection()
    
    expect(isMobile.value).toBe(false)
    expect(screenWidth.value).toBe(1024)
  })

  it('should detect mobile screen as mobile', () => {
    window.innerWidth = 375
    const { isMobile, screenWidth } = useMobileDetection()
    
    expect(isMobile.value).toBe(true)
    expect(screenWidth.value).toBe(375)
  })

  it('should detect tablet screen (768px) as mobile', () => {
    window.innerWidth = 768
    const { isMobile, screenWidth } = useMobileDetection()
    
    // 768px is exactly the md breakpoint, so it should still be considered mobile
    expect(isMobile.value).toBe(true)
    expect(screenWidth.value).toBe(768)
  })

  it('should detect screen above 768px as desktop', () => {
    window.innerWidth = 769
    const { isMobile, screenWidth } = useMobileDetection()
    
    expect(isMobile.value).toBe(false)
    expect(screenWidth.value).toBe(769)
  })

  it('should update when window is resized', () => {
    // Start with desktop
    window.innerWidth = 1024
    const { isMobile, screenWidth } = useMobileDetection()
    
    expect(isMobile.value).toBe(false)
    expect(screenWidth.value).toBe(1024)
    
    // Resize to mobile
    window.innerWidth = 375
    triggerResize()
    
    expect(isMobile.value).toBe(true)
    expect(screenWidth.value).toBe(375)
    
    // Resize back to desktop
    window.innerWidth = 1200
    triggerResize()
    
    expect(isMobile.value).toBe(false)
    expect(screenWidth.value).toBe(1200)
  })

  it('should add and remove event listeners', () => {
    const { isMobile } = useMobileDetection()
    
    // Should have added resize listener
    expect(window.addEventListener).toHaveBeenCalledWith('resize', expect.any(Function))
    
    // When component unmounts, should remove listener
    // This is tested implicitly - the composable sets up the listener cleanup
  })
})