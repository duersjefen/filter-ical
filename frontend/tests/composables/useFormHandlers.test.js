import { describe, it, expect, vi } from 'vitest'
import { useFormHandlers } from '../../src/composables/useFormHandlers'

describe('useFormHandlers', () => {
  describe('handleSubmit', () => {
    it('submits successfully without validation', async () => {
      const { handleSubmit, isSubmitting, errors } = useFormHandlers()
      const submitFn = vi.fn().mockResolvedValue()

      await handleSubmit(submitFn)

      expect(submitFn).toHaveBeenCalled()
      expect(isSubmitting.value).toBe(false)
      expect(Object.keys(errors.value)).toHaveLength(0)
    })

    it('sets isSubmitting during submission', async () => {
      const { handleSubmit, isSubmitting } = useFormHandlers()
      let submittingDuringFn = false

      const submitFn = vi.fn(async () => {
        submittingDuringFn = isSubmitting.value
        await new Promise(resolve => setTimeout(resolve, 10))
      })

      await handleSubmit(submitFn)

      expect(submittingDuringFn).toBe(true)
      expect(isSubmitting.value).toBe(false)
    })

    it('prevents concurrent submissions', async () => {
      const { handleSubmit, isSubmitting } = useFormHandlers()
      const submitFn = vi.fn().mockResolvedValue()

      // Manually set submitting
      isSubmitting.value = true

      await handleSubmit(submitFn)

      expect(submitFn).not.toHaveBeenCalled()
    })

    it('runs validation and stops if errors exist', async () => {
      const { handleSubmit, errors } = useFormHandlers()
      const submitFn = vi.fn().mockResolvedValue()
      const validationFn = vi.fn(() => ({ email: 'Invalid email' }))

      await handleSubmit(submitFn, validationFn)

      expect(validationFn).toHaveBeenCalled()
      expect(submitFn).not.toHaveBeenCalled()
      expect(errors.value).toEqual({ email: 'Invalid email' })
    })

    it('continues if validation passes', async () => {
      const { handleSubmit, errors } = useFormHandlers()
      const submitFn = vi.fn().mockResolvedValue()
      const validationFn = vi.fn(() => ({}))

      await handleSubmit(submitFn, validationFn)

      expect(validationFn).toHaveBeenCalled()
      expect(submitFn).toHaveBeenCalled()
      expect(Object.keys(errors.value)).toHaveLength(0)
    })

    it('handles submission errors', async () => {
      const { handleSubmit, errors } = useFormHandlers()
      const error = new Error('Submission failed')
      const submitFn = vi.fn().mockRejectedValue(error)

      await expect(handleSubmit(submitFn)).rejects.toThrow('Submission failed')

      expect(errors.value).toEqual({ general: 'Submission failed' })
    })

    it('clears previous errors on new submission', async () => {
      const { handleSubmit, errors, setError } = useFormHandlers()
      const submitFn = vi.fn().mockResolvedValue()

      // Set an error
      setError('field', 'Previous error')
      expect(errors.value.field).toBe('Previous error')

      // Submit again
      await handleSubmit(submitFn)

      expect(Object.keys(errors.value)).toHaveLength(0)
    })
  })

  describe('handleCancel', () => {
    it('clears errors', () => {
      const { handleCancel, errors, setError } = useFormHandlers()

      setError('field', 'Error message')
      handleCancel()

      expect(Object.keys(errors.value)).toHaveLength(0)
    })

    it('calls reset function if provided', () => {
      const { handleCancel } = useFormHandlers()
      const resetFn = vi.fn()

      handleCancel(resetFn)

      expect(resetFn).toHaveBeenCalled()
    })

    it('works without reset function', () => {
      const { handleCancel, errors, setError } = useFormHandlers()

      setError('field', 'Error message')
      handleCancel()

      expect(Object.keys(errors.value)).toHaveLength(0)
    })
  })

  describe('clearErrors', () => {
    it('clears all errors', () => {
      const { clearErrors, errors, setError } = useFormHandlers()

      setError('field1', 'Error 1')
      setError('field2', 'Error 2')
      expect(Object.keys(errors.value)).toHaveLength(2)

      clearErrors()

      expect(Object.keys(errors.value)).toHaveLength(0)
    })
  })

  describe('setError', () => {
    it('sets error for specific field', () => {
      const { setError, errors } = useFormHandlers()

      setError('email', 'Invalid email')

      expect(errors.value.email).toBe('Invalid email')
    })

    it('sets general error', () => {
      const { setError, errors } = useFormHandlers()

      setError('general', 'Form submission failed')

      expect(errors.value.general).toBe('Form submission failed')
    })

    it('overwrites existing error for field', () => {
      const { setError, errors } = useFormHandlers()

      setError('email', 'First error')
      setError('email', 'Second error')

      expect(errors.value.email).toBe('Second error')
    })
  })

  describe('getError', () => {
    it('retrieves error for specific field', () => {
      const { setError, getError } = useFormHandlers()

      setError('email', 'Invalid email')

      expect(getError('email')).toBe('Invalid email')
    })

    it('returns undefined for non-existent field', () => {
      const { getError } = useFormHandlers()

      expect(getError('nonexistent')).toBeUndefined()
    })
  })

  describe('hasErrors', () => {
    it('returns true when errors exist', () => {
      const { setError, hasErrors } = useFormHandlers()

      setError('field', 'Error')

      expect(hasErrors()).toBe(true)
    })

    it('returns false when no errors exist', () => {
      const { hasErrors } = useFormHandlers()

      expect(hasErrors()).toBe(false)
    })

    it('returns false after clearing errors', () => {
      const { setError, clearErrors, hasErrors } = useFormHandlers()

      setError('field', 'Error')
      expect(hasErrors()).toBe(true)

      clearErrors()
      expect(hasErrors()).toBe(false)
    })
  })
})
