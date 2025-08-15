// src/views/CategoriesView.vue
<script setup>
import { onMounted } from 'vue'
import SkeletonBlock from '../components/SkeletonBlock.vue'
import CategoryCard from '../components/CategoryCard.vue'
import { useCatalogStore } from '../stores/catalog.js'

const catalog = useCatalogStore()

onMounted(() => {
  catalog.fetchOnce()
})
</script>

<template>
  <section class="page-section">
    <h2 class="section-title">Категории</h2>
    <div v-if="catalog.isLoading" class="skeletons">
      <SkeletonBlock height="56px" />
      <SkeletonBlock height="56px" />
      <SkeletonBlock height="56px" />
    </div>
    <div v-else-if="catalog.error" class="error">Ошибка: {{ catalog.error }}</div>
    <div v-else class="cards">
      <CategoryCard
        v-for="category in catalog.categories"
        :key="category.id"
        :category="category"
      />
    </div>
  </section>
  
</template>

<style scoped>
.page-section { padding: 16px; }
.section-title { margin: 0 0 12px; font-weight: 700; font-size: 18px; }
.error { color: #e11d48; }
.cards { display: flex; flex-direction: column; gap: 12px; }
</style>