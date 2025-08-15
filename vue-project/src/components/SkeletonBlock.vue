<script setup>
defineProps({ height: { type: String, default: '16px' }, radius: { type: String, default: '12px' } })
</script>

<template>
  <div class="sk" :style="{ height, borderRadius: radius }" />
</template>

<style scoped>
.sk { width: 100%; background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 37%, #f3f4f6 63%); background-size: 400% 100%; animation: shimmer 1.2s infinite; }
@keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
</style>

