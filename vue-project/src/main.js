// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/global.css'
import { applyTgTheme } from './lib/twaTheme.js'
import { setupI18n } from './i18n/index.js'
import { useAuthStore } from './stores/auth.js'

const tg = window?.Telegram?.WebApp
if (tg) {
  tg.expand?.()
  tg.setBackgroundColor?.('#ffffff')
  tg.setHeaderColor?.('#ffffff')
  tg.ready?.()
  applyTgTheme(tg)
  tg.onEvent?.('themeChanged', () => applyTgTheme(tg))
}

const app = createApp(App)
const pinia = createPinia()
const i18n = setupI18n()
app.use(pinia)
app.use(i18n)
app.use(router)
app.mount('#app')

// Bootstrap auth (TWA validation)
const auth = useAuthStore()
auth.bootstrapFromTwa()?.catch?.(() => {})
