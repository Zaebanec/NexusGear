<script setup>
</script>

<template>
  <nav class="admin-nav">
    <RouterLink to="/admin" class="link">Dashboard</RouterLink>
    <RouterLink to="/admin/categories" class="link">Categories</RouterLink>
    <RouterLink to="/admin/products" class="link">Products</RouterLink>
  </nav>
</template>

<style scoped>
.admin-nav { display: flex; gap: 12px; padding: 12px 16px; border-bottom: 1px solid #eee; background: #fff; position: sticky; top: 0; z-index: 5; }
.link { text-decoration: none; color: #111; font-weight: 700; }
.link.router-link-active { color: #1d4ed8; }
</style>

