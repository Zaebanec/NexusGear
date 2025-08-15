// src/components/ProductCard.vue
<script setup>
import { computed } from 'vue'
import { useCartStore } from '../stores/cart.js'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const cart = useCartStore()

const formattedPrice = computed(() => {
  if (!props.product || typeof props.product.price !== 'number') return ''
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(props.product.price)
})
</script>

<template>
  <article v-if="product" class="product-card">
    <div class="product-image-placeholder"></div>
    <h4 class="title">{{ product.name }}</h4>
    <p class="price">{{ formattedPrice }}</p>
    <div class="row">
      <button class="btn" @click="cart.decrementProduct(product.id)">−</button>
      <button class="btn primary" @click="cart.addProduct(product)">В корзину</button>
      <button class="btn" @click="cart.addProduct(product)">+</button>
    </div>
  </article>
</template>

<style scoped>
.product-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
}
.product-image-placeholder {
  width: 100%; height: 150px; background: #f3f4f6; border-radius: 8px; margin-bottom: 12px;
}
.title { margin: 0 0 8px; font-size: 18px; font-weight: 800; }
.price { font-size: 18px; font-weight: 800; color: #111; margin: 0 0 16px; }
.row { display: grid; grid-template-columns: 40px 1fr 40px; gap: 8px; align-items: center; }
.btn { appearance: none; border: 0; border-radius: 10px; padding: 10px; background: #f3f4f6; font-weight: 700; }
.btn.primary { background: #1d4ed8; color: #fff; }
</style>