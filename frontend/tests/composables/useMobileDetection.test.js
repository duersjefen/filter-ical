import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { useMobileDetection } from '@/composables/useMobileDetection'

// Mock window.innerWidth
Object.defineProperty(window, 'innerWidth', {
  writable: true,
  configurable: true,
  value: 1024,
})

describe('useMobileDetection', () => {
  let addEventListenerSpy
  let removeEventListenerSpy

  beforeEach(() => {
    // Spy on actual window methods
    addEventListenerSpy = vi.spyOn(window, 'addEventListener')
    removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  // Helper to create a test component that uses the composable
  const createTestComponent = () => {
    return defineComponent({
      setup() {
        const detection = useMobileDetection()
        return { ...detection }
      },
      render() {
        return h('div')
      }
    })
  }

  it('should detect desktop screen as not mobile', () => {
    window.innerWidth = 1024
    const wrapper = mount(createTestComponent())

    expect(wrapper.vm.isMobile).toBe(false)
    expect(wrapper.vm.screenWidth).toBe(1024)

    wrapper.unmount()
  })

  it('should detect mobile screen as mobile', () => {
    window.innerWidth = 375
    const wrapper = mount(createTestComponent())

    expect(wrapper.vm.isMobile).toBe(true)
    expect(wrapper.vm.screenWidth).toBe(375)

    wrapper.unmount()
  })

  it('should detect tablet screen (768px) as desktop (boundary)', () => {
    window.innerWidth = 768
    const wrapper = mount(createTestComponent())

    // 768px is exactly the md breakpoint - code checks < 768, so 768 is desktop
    expect(wrapper.vm.isMobile).toBe(false)
    expect(wrapper.vm.screenWidth).toBe(768)

    wrapper.unmount()
  })

  it('should detect screen above 768px as desktop', () => {
    window.innerWidth = 769
    const wrapper = mount(createTestComponent())

    expect(wrapper.vm.isMobile).toBe(false)
    expect(wrapper.vm.screenWidth).toBe(769)

    wrapper.unmount()
  })

  it('should update when window is resized', async () => {
    // Start with desktop
    window.innerWidth = 1024
    const wrapper = mount(createTestComponent())

    expect(wrapper.vm.isMobile).toBe(false)
    expect(wrapper.vm.screenWidth).toBe(1024)

    // Resize to mobile
    window.innerWidth = 375
    window.dispatchEvent(new Event('resize'))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isMobile).toBe(true)
    expect(wrapper.vm.screenWidth).toBe(375)

    // Resize back to desktop
    window.innerWidth = 1200
    window.dispatchEvent(new Event('resize'))
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.isMobile).toBe(false)
    expect(wrapper.vm.screenWidth).toBe(1200)

    wrapper.unmount()
  })

  it('should add and remove event listeners', () => {
    const wrapper = mount(createTestComponent())

    // Should have added resize listener
    expect(addEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))

    // Unmount and check cleanup
    wrapper.unmount()
    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))
  })
})