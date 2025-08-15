<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()

const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp || null : null

function goHome() {
  router.replace({ name: 'home' })
}

onMounted(() => {
  tg?.HapticFeedback?.notificationOccurred?.('success')
  tg?.BackButton?.show?.()
  tg?.BackButton?.onClick?.(goHome)
  tg?.MainButton?.setParams?.({ text: 'В магазин', color: '#1d4ed8', text_color: '#ffffff' })
  tg?.MainButton?.show?.()
  tg?.MainButton?.onClick?.(goHome)
})

onUnmounted(() => {
  tg?.BackButton?.hide?.()
  tg?.MainButton?.hide?.()
})
</script>

<template>
  <section class="page-section">
    <h2 class="section-title">Заказ оформлен</h2>
    <p class="subtitle">Номер заказа: <strong>#{{ props.id }}</strong></p>
    <p>Мы уже начали обработку заказа. Спасибо!</p>
    <button class="btn-primary" @click="goHome">Вернуться в магазин</button>
  </section>
</template>

<style scoped>
.page-section { padding: 16px; }
.section-title { margin: 0 0 8px; font-weight: 800; font-size: 20px; }
.subtitle { margin: 0 0 16px; color: #111; }
.btn-primary { appearance: none; border: 0; border-radius: 12px; padding: 12px 16px; background: #1d4ed8; color: #fff; font-weight: 700; }
</style>

