import { defineStore } from 'pinia'

export const useCatalogStore = defineStore('catalog', {
  state: () => ({
    /** @type {{ id:number; name?:string; title?:string; slug?:string }[]} */
    categories: [],
    isLoaded: false,
    isLoading: false,
    error: null,
  }),
  actions: {
    async fetchOnce() {
      if (this.isLoaded || this.isLoading) return
      this.isLoading = true
      try {
        const response = await fetch('/api/categories')
        if (!response.ok) throw new Error('failed to load')
        this.categories = await response.json()
        this.isLoaded = true
      } catch (e) {
        /** @type {{ message?: string }} */
        // @ts-ignore
        const err = e || {}
        this.error = err?.message ?? 'failed to load'
      } finally {
        this.isLoading = false
      }
    },
  },
})


