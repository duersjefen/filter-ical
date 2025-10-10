/**
 * Tests for FormInput component
 */
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FormInput from '../../../src/components/shared/FormInput.vue'

describe('FormInput', () => {
  it('renders with required props', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input'
      }
    })
    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('input').attributes('id')).toBe('test-input')
  })

  it('displays label when provided', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        label: 'Test Label'
      }
    })
    expect(wrapper.find('label').exists()).toBe(true)
    expect(wrapper.find('label').text()).toContain('Test Label')
  })

  it('shows required asterisk when required', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        required: true
      }
    })
    expect(wrapper.find('.text-red-500').exists()).toBe(true)
  })

  it('shows optional text when provided', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        label: 'Test Label',
        optional: 'Optional'
      }
    })
    expect(wrapper.text()).toContain('Optional')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        modelValue: ''
      }
    })
    const input = wrapper.find('input')
    await input.setValue('test value')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['test value'])
  })

  it('displays error message when provided', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        error: 'This field is required'
      }
    })
    expect(wrapper.text()).toContain('This field is required')
    expect(wrapper.find('.text-red-600').exists()).toBe(true)
  })

  it('displays helper text when provided', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        helperText: 'Enter your email address'
      }
    })
    expect(wrapper.text()).toContain('Enter your email address')
  })

  it('applies error styling when error is present', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        error: 'Error message'
      }
    })
    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-red-500')
  })

  it('applies normal styling when no error', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input'
      }
    })
    const input = wrapper.find('input')
    expect(input.classes()).toContain('border-gray-300')
  })

  it('sets input type correctly', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        type: 'email'
      }
    })
    expect(wrapper.find('input').attributes('type')).toBe('email')
  })

  it('shows password toggle button for password type with value', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        type: 'password',
        modelValue: 'secret'
      }
    })
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('does not show password toggle button when no value', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        type: 'password',
        modelValue: ''
      }
    })
    expect(wrapper.find('button').exists()).toBe(false)
  })

  it('toggles password visibility when toggle button clicked', async () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        type: 'password',
        modelValue: 'secret'
      }
    })
    const input = wrapper.find('input')
    expect(input.attributes('type')).toBe('password')

    await wrapper.find('button').trigger('click')
    expect(input.attributes('type')).toBe('text')

    await wrapper.find('button').trigger('click')
    expect(input.attributes('type')).toBe('password')
  })

  it('disables input when disabled prop is true', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        disabled: true
      }
    })
    const input = wrapper.find('input')
    expect(input.attributes('disabled')).toBeDefined()
  })

  it('sets placeholder attribute', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        placeholder: 'Enter text here'
      }
    })
    expect(wrapper.find('input').attributes('placeholder')).toBe('Enter text here')
  })

  it('sets minlength attribute', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        minlength: 4
      }
    })
    expect(wrapper.find('input').attributes('minlength')).toBe('4')
  })

  it('sets maxlength attribute', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        maxlength: 100
      }
    })
    expect(wrapper.find('input').attributes('maxlength')).toBe('100')
  })

  it('sets pattern attribute', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'test-input',
        pattern: '[a-z0-9-]+'
      }
    })
    expect(wrapper.find('input').attributes('pattern')).toBe('[a-z0-9-]+')
  })
})
