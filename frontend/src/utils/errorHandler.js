export const ErrorTypes = {
  NETWORK: 'network',
  VALIDATION: 'validation',
  AUTHENTICATION: 'auth',
  NOT_FOUND: 'not_found',
  SERVER: 'server',
  CALENDAR: 'calendar',
  UNKNOWN: 'unknown'
}

import { t } from '@/i18n'

export const getErrorMessage = (errorType) => {
  const messageKeys = {
    [ErrorTypes.NETWORK]: 'errors.networkError',
    [ErrorTypes.VALIDATION]: 'errors.validationError',
    [ErrorTypes.AUTHENTICATION]: 'errors.authenticationError',
    [ErrorTypes.NOT_FOUND]: 'errors.notFoundError',
    [ErrorTypes.SERVER]: 'errors.serverError',
    [ErrorTypes.CALENDAR]: 'errors.calendarError',
    [ErrorTypes.UNKNOWN]: 'errors.unknownError'
  }
  
  return t(messageKeys[errorType] || messageKeys[ErrorTypes.UNKNOWN])
}

export class AppError extends Error {
  constructor(message, type = ErrorTypes.UNKNOWN, originalError = null) {
    super(message)
    this.type = type
    this.originalError = originalError
    this.timestamp = Date.now()
  }
}

export function parseApiError(error) {
  if (!error.response) {
    return new AppError(getErrorMessage(ErrorTypes.NETWORK), ErrorTypes.NETWORK, error)
  }

  const status = error.response.status
  const data = error.response.data

  switch (status) {
    case 400:
      return new AppError(
        data?.message || getErrorMessage(ErrorTypes.VALIDATION),
        ErrorTypes.VALIDATION,
        error
      )
    case 401:
    case 403:
      return new AppError(
        data?.message || getErrorMessage(ErrorTypes.AUTHENTICATION),
        ErrorTypes.AUTHENTICATION,
        error
      )
    case 404:
      return new AppError(
        data?.message || getErrorMessage(ErrorTypes.NOT_FOUND),
        ErrorTypes.NOT_FOUND,
        error
      )
    case 422:
      return new AppError(
        data?.message || t('errors.invalidCalendarFormat'),
        ErrorTypes.CALENDAR,
        error
      )
    case 500:
    case 502:
    case 503:
      return new AppError(
        data?.message || getErrorMessage(ErrorTypes.SERVER),
        ErrorTypes.SERVER,
        error
      )
    default:
      return new AppError(
        data?.message || getErrorMessage(ErrorTypes.UNKNOWN),
        ErrorTypes.UNKNOWN,
        error
      )
  }
}

export function createRetryableAction(action, maxRetries = 3, delay = 1000) {
  return async function(...args) {
    let lastError
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await action(...args)
      } catch (error) {
        lastError = parseApiError(error)
        
        if (attempt === maxRetries || 
            lastError.type === ErrorTypes.AUTHENTICATION ||
            lastError.type === ErrorTypes.VALIDATION) {
          throw lastError
        }
        
        await new Promise(resolve => setTimeout(resolve, delay * attempt))
      }
    }
    
    throw lastError
  }
}