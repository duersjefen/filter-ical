export const ErrorTypes = {
  NETWORK: 'network',
  VALIDATION: 'validation',
  AUTHENTICATION: 'auth',
  NOT_FOUND: 'not_found',
  SERVER: 'server',
  CALENDAR: 'calendar',
  UNKNOWN: 'unknown'
}

export const ErrorMessages = {
  [ErrorTypes.NETWORK]: 'Network connection failed. Please check your internet connection.',
  [ErrorTypes.VALIDATION]: 'Please check your input and try again.',
  [ErrorTypes.AUTHENTICATION]: 'Authentication failed. Please log in again.',
  [ErrorTypes.NOT_FOUND]: 'The requested resource was not found.',
  [ErrorTypes.SERVER]: 'Server error occurred. Please try again later.',
  [ErrorTypes.CALENDAR]: 'Failed to process calendar data. Please check the calendar URL.',
  [ErrorTypes.UNKNOWN]: 'An unexpected error occurred. Please try again.'
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
    return new AppError(ErrorMessages[ErrorTypes.NETWORK], ErrorTypes.NETWORK, error)
  }

  const status = error.response.status
  const data = error.response.data

  switch (status) {
    case 400:
      return new AppError(
        data?.message || ErrorMessages[ErrorTypes.VALIDATION],
        ErrorTypes.VALIDATION,
        error
      )
    case 401:
    case 403:
      return new AppError(
        data?.message || ErrorMessages[ErrorTypes.AUTHENTICATION],
        ErrorTypes.AUTHENTICATION,
        error
      )
    case 404:
      return new AppError(
        data?.message || ErrorMessages[ErrorTypes.NOT_FOUND],
        ErrorTypes.NOT_FOUND,
        error
      )
    case 422:
      return new AppError(
        data?.message || 'Invalid calendar format or URL',
        ErrorTypes.CALENDAR,
        error
      )
    case 500:
    case 502:
    case 503:
      return new AppError(
        data?.message || ErrorMessages[ErrorTypes.SERVER],
        ErrorTypes.SERVER,
        error
      )
    default:
      return new AppError(
        data?.message || ErrorMessages[ErrorTypes.UNKNOWN],
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