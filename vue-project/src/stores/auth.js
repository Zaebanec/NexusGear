import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({ token: '', userId: 0, isAdmin: false }),
  actions: {
    async bootstrapFromTwa() {
      const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp : null
      const initDataUnsafe = tg?.initDataUnsafe
      if (!initDataUnsafe) return
      const res = await fetch('/api/v1/auth/telegram/validate', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(initDataUnsafe)
      })
      const data = await res.json()
      if (data.status === 'ok') {
        this.token = data.token
        this.userId = data.user_id
        this.isAdmin = true
      }
    }
  }
})


