// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/global.css'
import { applyTgTheme } from './lib/twaTheme.js'

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
app.use(pinia)
app.use(router)
app.mount('#app')
