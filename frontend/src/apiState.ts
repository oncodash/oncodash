import { defineStore } from 'pinia'

/**
 * Manage the state of the api requests, mostly
 * to know when to properly display the loading screen.
 */
export const useApiState = defineStore('apiState', {
  state: () => {
    return {
      requestCount: 0
    }
  },
  getters: {
    isLoading: (state): boolean => {
      return state.requestCount > 0
    }
  },
  actions: {
    addRequest(): void {
      this.requestCount++
    },
    removeRequest(): void {
      if (this.requestCount === 0) return
      this.requestCount--
    }
  }
})
