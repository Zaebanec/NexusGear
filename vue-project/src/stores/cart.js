import { defineStore } from 'pinia'
import { ref, computed, watch, onMounted } from 'vue'
import { setItem as cloudSet, getItem as cloudGet, isCloudAvailable } from '../lib/twaCloud.js'

/**
 * @typedef {Object} CartItem
 * @property {number} id
 * @property {string} [name]
 * @property {number} price
 * @property {number} quantity
 */

export const useCartStore = defineStore('cart', () => {
  const STORAGE_KEY = 'ngs_cart_items_v1'
  /** @type {import('vue').Ref<CartItem[]>} */
  const items = ref([])

  // Load persisted state (localStorage, затем CloudStorage)
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) items.value = parsed
    }
  } catch { /* ignore */ }

  onMounted(async () => {
    if (items.value.length > 0) return
    const cloud = await cloudGet(STORAGE_KEY)
    if (cloud) {
      try {
        const parsed = JSON.parse(cloud)
        if (Array.isArray(parsed)) items.value = parsed
      } catch { /* ignore */ }
    }
  })

  const totalItems = computed(() => items.value.reduce((total, item) => total + item.quantity, 0))

  const totalPrice = computed(() => items.value.reduce((total, item) => total + item.price * item.quantity, 0))

  function addProduct(product) {
    const existing = items.value.find(i => i.id === product.id)
    if (existing) existing.quantity++
    else items.value.push({ ...product, quantity: 1 })
  }

  function decrementProduct(productId) {
    const existing = items.value.find(i => i.id === productId)
    if (!existing) return
    existing.quantity = Math.max(0, existing.quantity - 1)
    if (existing.quantity === 0) {
      items.value = items.value.filter(i => i.id !== productId)
    }
  }

  function setQuantity(productId, quantity) {
    const existing = items.value.find(i => i.id === productId)
    if (!existing) return
    const next = Math.max(0, Number(quantity) || 0)
    if (next === 0) {
      items.value = items.value.filter(i => i.id !== productId)
    } else {
      existing.quantity = next
    }
  }

  function removeProduct(productId) {
    items.value = items.value.filter(i => i.id !== productId)
  }

  // ➕ экшен очистки
  function clear() {
    items.value = []
  }

  // Persist to localStorage
  watch(items, (val) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
    } catch {
      /* ignore */
    }
  }, { deep: true })

  // Persist to Telegram CloudStorage (best-effort)
  watch(items, async (val) => {
    try {
      if (!isCloudAvailable()) return
      await cloudSet(STORAGE_KEY, JSON.stringify(val))
    } catch { /* ignore */ }
  }, { deep: true })

  return { items, totalItems, totalPrice, addProduct, decrementProduct, setQuantity, removeProduct, clear }
})
