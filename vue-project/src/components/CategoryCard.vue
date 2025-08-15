// src/components/CategoryCard.vue
<script setup>

defineProps({
  category: {
    type: Object,
    required: true
  }
})
</script>

<template>
  <router-link :to="{ name: 'products', params: { id: category.id } }" class="card">
    {{ category.name }}
  </router-link>
</template>

<style scoped>
.card {
  display: block;
  appearance: none;
  border: 0;
  border-radius: 14px;
  padding: 18px 16px;
  background: #f7f7f7;
  box-shadow: 0 1px 2px rgba(0,0,0,.05);
  font-weight: 700;
  font-size: 18px;
  width: 100%;
  text-align: center;
  color: inherit;
  text-decoration: none;
}
</style>