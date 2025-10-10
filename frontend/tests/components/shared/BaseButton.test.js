/**
 * Tests for BaseButton component
 */
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseButton from '../../../src/components/shared/BaseButton.vue'

describe('BaseButton', () => {
  it('renders with default props', () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me'
      }
    })
    expect(wrapper.text()).toContain('Click me')
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(BaseButton, {
      slots: {
        default: 'Click me'
      }
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click').length).toBe(1)
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        disabled: true
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    await button.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('does not emit click when loading', async () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    await button.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('shows loading text when loading', () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true,
        loadingText: 'Loading...'
      },
      slots: {
        default: 'Click me'
      }
    })
    expect(wrapper.text()).toContain('Loading...')
    expect(wrapper.text()).not.toContain('Click me')
  })

  it('applies primary variant classes', () => {
    const wrapper = mount(BaseButton, {
      props: {
        variant: 'primary'
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('bg-blue-600')
  })

  it('applies secondary variant classes', () => {
    const wrapper = mount(BaseButton, {
      props: {
        variant: 'secondary'
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('bg-gray-200')
  })

  it('applies success variant classes', () => {
    const wrapper = mount(BaseButton, {
      props: {
        variant: 'success'
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('bg-green-600')
  })

  it('applies danger variant classes', () => {
    const wrapper = mount(BaseButton, {
      props: {
        variant: 'danger'
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('bg-red-600')
  })

  it('applies small size classes', () => {
    const wrapper = mount(BaseButton, {
      props: {
        size: 'sm'
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('px-3')
    expect(button.classes()).toContain('py-1.5')
  })

  it('applies large size classes', () => {
    const wrapper = mount(BaseButton, {
      props: {
        size: 'lg'
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('px-6')
    expect(button.classes()).toContain('py-3')
  })

  it('applies full width class', () => {
    const wrapper = mount(BaseButton, {
      props: {
        fullWidth: true
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('w-full')
  })

  it('has correct button type attribute', () => {
    const wrapper = mount(BaseButton, {
      props: {
        type: 'submit'
      },
      slots: {
        default: 'Submit'
      }
    })
    const button = wrapper.find('button')
    expect(button.attributes('type')).toBe('submit')
  })

  it('applies rounded classes', () => {
    const wrapper = mount(BaseButton, {
      props: {
        rounded: 'full'
      },
      slots: {
        default: 'Click me'
      }
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('rounded-full')
  })

  it('shows loading spinner when loading', () => {
    const wrapper = mount(BaseButton, {
      props: {
        loading: true
      },
      slots: {
        default: 'Click me'
      }
    })
    expect(wrapper.find('svg.animate-spin').exists()).toBe(true)
  })
})
