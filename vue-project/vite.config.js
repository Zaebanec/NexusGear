import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  // alias не используем по манифесту — секцию можно опустить
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8081', // ← локальный бек (как в curl)
        changeOrigin: true,
        // не переписываем путь — на бэке тоже /api/...
      },
    },
  },
  build: {
    sourcemap: true,   // ← включаем карты исходников
  },
})
