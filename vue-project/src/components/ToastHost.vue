<script setup>
import { useUiStore } from '../stores/ui.js'
const ui = useUiStore()
</script>

<template>
  <div class="toast-host">
    <transition-group name="toast" tag="div">
      <div v-for="t in ui.toasts" :key="t.id" class="toast" :data-type="t.type" @click="ui.remove(t.id)">
        {{ t.message }}
      </div>
    </transition-group>
  </div>
  
  </template>

<style scoped>
.toast-host { position: fixed; left: 0; right: 0; bottom: 16px; display: grid; gap: 8px; padding: 0 16px; pointer-events: none; }
.toast { pointer-events: auto; background: #111; color: #fff; padding: 12px 14px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.2); }
.toast[data-type="success"] { background: #0ea5e9; }
.toast[data-type="error"] { background: #ef4444; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(6px); }
.toast-enter-active, .toast-leave-active { transition: all .2s ease; }
</style>

