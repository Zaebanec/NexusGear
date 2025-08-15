import { defineStore } from 'pinia'

let toastIdSeq = 1

/**
 * @typedef {{ id: number; message: string; type: 'info'|'success'|'error' }} Toast
 */
export const useUiStore = defineStore('ui', {
  state: () => ({ /** @type {Toast[]} */ toasts: [] }),
  actions: {
    /** @param {string} message @param {'info'|'success'|'error'} [type] @param {number} [timeoutMs] */
    toast(message, type = 'info', timeoutMs = 3000) {
      const id = toastIdSeq++
      this.toasts.push({ id, message, type })
      if (timeoutMs > 0) {
        setTimeout(() => {
          this.toasts = this.toasts.filter(t => t.id !== id)
        }, timeoutMs)
      }
    },
    /** @param {number} id */
    remove(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },
  },
})


