export const LoadingStates = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error'
}

export const LoadingOperations = {
  FETCH_CALENDARS: 'fetchCalendars',
  ADD_CALENDAR: 'addCalendar',
  DELETE_CALENDAR: 'deleteCalendar',
  FETCH_EVENTS: 'fetchEvents',
  SAVE_FILTER: 'saveFilter',
  DELETE_FILTER: 'deleteFilter',
  GENERATE_ICAL: 'generateIcal',
  LOGIN: 'login'
}

export class LoadingManager {
  constructor() {
    this.operations = new Map()
    this.globalState = LoadingStates.IDLE
  }

  startOperation(operation) {
    this.operations.set(operation, LoadingStates.LOADING)
    this.updateGlobalState()
  }

  finishOperation(operation, success = true) {
    this.operations.set(
      operation, 
      success ? LoadingStates.SUCCESS : LoadingStates.ERROR
    )
    this.updateGlobalState()
    
    setTimeout(() => {
      if (this.operations.get(operation) !== LoadingStates.LOADING) {
        this.operations.delete(operation)
        this.updateGlobalState()
      }
    }, 2000)
  }

  isOperationLoading(operation) {
    return this.operations.get(operation) === LoadingStates.LOADING
  }

  getOperationState(operation) {
    return this.operations.get(operation) || LoadingStates.IDLE
  }

  isAnyLoading() {
    return Array.from(this.operations.values()).some(
      state => state === LoadingStates.LOADING
    )
  }

  getLoadingOperations() {
    return Array.from(this.operations.entries())
      .filter(([_, state]) => state === LoadingStates.LOADING)
      .map(([operation]) => operation)
  }

  updateGlobalState() {
    if (this.isAnyLoading()) {
      this.globalState = LoadingStates.LOADING
    } else if (Array.from(this.operations.values()).some(state => state === LoadingStates.ERROR)) {
      this.globalState = LoadingStates.ERROR
    } else if (Array.from(this.operations.values()).some(state => state === LoadingStates.SUCCESS)) {
      this.globalState = LoadingStates.SUCCESS
    } else {
      this.globalState = LoadingStates.IDLE
    }
  }

  clear() {
    this.operations.clear()
    this.globalState = LoadingStates.IDLE
  }
}

export function createLoadingWrapper(operation, loadingManager) {
  return async function(action, ...args) {
    loadingManager.startOperation(operation)
    
    try {
      const result = await action(...args)
      loadingManager.finishOperation(operation, true)
      return result
    } catch (error) {
      loadingManager.finishOperation(operation, false)
      throw error
    }
  }
}