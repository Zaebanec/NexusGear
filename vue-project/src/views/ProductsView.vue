// src/views/ProductsView.vue
<script setup>
import { ref, onMounted } from 'vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import { useRoute } from 'vue-router'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const categoryId = route.params.id

const products = ref([])
const isLoading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    // Используем новый эндпоинт с query-параметром
    const response = await fetch(`/api/products?category_id=${categoryId}`)
    if (!response.ok) {
      throw new Error('Ошибка сети или сервера при загрузке товаров')
    }
    products.value = await response.json()
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="products-view">
    <h1>Товары в категории</h1>
    <div v-if="isLoading" class="skeletons">
      <SkeletonBlock height="220px" />
      <SkeletonBlock height="220px" />
      <SkeletonBlock height="220px" />
    </div>
    <div v-else-if="error" class="error">Ошибка: {{ error }}</div>
    <div v-else-if="products.length" class="products-grid">
      <ProductCard 
        v-for="product in products" 
        :key="product.id" 
        :product="product" 
      />
    </div>
    <div v-else>В этой категории пока нет товаров.</div>
  </div>
</template>

<style scoped>
.products-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.error {
  color: red;
}
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}
</style>