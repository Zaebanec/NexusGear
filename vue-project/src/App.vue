<!-- src/App.vue -->
<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useCartStore } from './stores/cart.js'
import ToastHost from './components/ToastHost.vue'
const cart = useCartStore()
const totalItems = computed(() => cart.totalItems)
</script>

<template>
  <header class="twa-header">
    <RouterLink to="/" class="brand">NexusShop</RouterLink>
    <RouterLink to="/cart" class="cart-pill">🛒 {{ totalItems }}</RouterLink>
  </header>
  <main class="app-root">
    <RouterView />
  </main>
  <ToastHost />
  
</template>

<style scoped>
.app-root {
  min-height: 100%;
  display: block;
  padding: 0;
  background: #fff;
}
.twa-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.brand { color: #111; text-decoration: none; font-weight: 800; font-size: 18px; }
.cart-pill { text-decoration: none; font-weight: 700; color: #111; background: #f3f4f6; padding: 6px 10px; border-radius: 999px; }
</style>