import { defineStore } from 'pinia'

let toastIdSeq = 1

export const useUiStore = defineStore('ui', {
  state: () => ({ toasts: [] }),
  actions: {
    toast(message, type = 'info', timeoutMs = 3000) {
      const id = toastIdSeq++
      this.toasts.push({ id, message, type })
      if (timeoutMs > 0) {
        setTimeout(() => {
          this.toasts = this.toasts.filter(t => t.id !== id)
        }, timeoutMs)
      }
    },
    remove(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },
  },
})


