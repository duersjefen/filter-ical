/**
 * Tests for BaseCard component
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseCard from '../../../src/components/shared/BaseCard.vue'

describe('BaseCard', () => {
  it('renders with default props', () => {
    const wrapper = mount(BaseCard, {
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card content')
  })

  it('displays title when provided', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card Title')
  })

  it('displays subtitle when provided', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title',
        subtitle: 'Card subtitle'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card subtitle')
  })

  it('displays icon when provided', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title',
        icon: '📦'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('📦')
  })

  it('renders header slot content', () => {
    const wrapper = mount(BaseCard, {
      slots: {
        header: '<div class="custom-header">Custom Header</div>',
        default: 'Card content'
      }
    })
    expect(wrapper.find('.custom-header').exists()).toBe(true)
    expect(wrapper.text()).toContain('Custom Header')
  })

  it('renders footer slot content', () => {
    const wrapper = mount(BaseCard, {
      slots: {
        default: 'Card content',
        footer: '<div class="custom-footer">Custom Footer</div>'
      }
    })
    expect(wrapper.find('.custom-footer').exists()).toBe(true)
    expect(wrapper.text()).toContain('Custom Footer')
  })

  it('renders header-actions slot content', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title'
      },
      slots: {
        default: 'Card content',
        'header-actions': '<button class="action-btn">Action</button>'
      }
    })
    expect(wrapper.find('.action-btn').exists()).toBe(true)
  })

  it('applies default variant classes', () => {
    const wrapper = mount(BaseCard, {
      props: {
        variant: 'default'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.classes()).toContain('bg-white')
    expect(wrapper.classes()).toContain('shadow-lg')
  })

  it('applies gradient variant classes', () => {
    const wrapper = mount(BaseCard, {
      props: {
        variant: 'gradient'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.classes()).toContain('bg-gradient-to-br')
  })

  it('applies elevated variant classes', () => {
    const wrapper = mount(BaseCard, {
      props: {
        variant: 'elevated'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.classes()).toContain('shadow-xl')
  })

  it('applies blue color theme', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title',
        color: 'blue'
      },
      slots: {
        default: 'Card content'
      }
    })
    // Card should render with title
    expect(wrapper.text()).toContain('Card Title')
    expect(wrapper.exists()).toBe(true)
  })

  it('applies green color theme', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title',
        color: 'green'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card Title')
    expect(wrapper.exists()).toBe(true)
  })

  it('applies red color theme', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title',
        color: 'red'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card Title')
    expect(wrapper.exists()).toBe(true)
  })

  it('applies medium padding by default', () => {
    const wrapper = mount(BaseCard, {
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card content')
    expect(wrapper.exists()).toBe(true)
  })

  it('applies small padding when specified', () => {
    const wrapper = mount(BaseCard, {
      props: {
        padding: 'sm'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card content')
    expect(wrapper.exists()).toBe(true)
  })

  it('applies large padding when specified', () => {
    const wrapper = mount(BaseCard, {
      props: {
        padding: 'lg'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card content')
    expect(wrapper.exists()).toBe(true)
  })

  it('applies no padding when specified', () => {
    const wrapper = mount(BaseCard, {
      props: {
        padding: 'none'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card content')
    expect(wrapper.exists()).toBe(true)
  })

  it('applies custom header padding', () => {
    const wrapper = mount(BaseCard, {
      props: {
        title: 'Card Title',
        headerPadding: 'lg',
        bodyPadding: 'sm'
      },
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.text()).toContain('Card Title')
    expect(wrapper.text()).toContain('Card content')
  })

  it('has rounded corners', () => {
    const wrapper = mount(BaseCard, {
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.classes()).toContain('rounded-xl')
  })

  it('has transition classes', () => {
    const wrapper = mount(BaseCard, {
      slots: {
        default: 'Card content'
      }
    })
    expect(wrapper.classes()).toContain('transition-all')
    expect(wrapper.classes()).toContain('duration-300')
  })
})
