<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AdminNav from '../../components/admin/AdminNav.vue'
import { useAuthStore } from '../../stores/auth.js'

const route = useRoute()
const auth = useAuthStore()

const order = ref(null)
const items = ref([])
const isLoading = ref(false)
const error = ref('')

async function load() {
  try {
    isLoading.value = true
    await auth.bootstrapFromTwa()
    const id = route.params.id
    const r = await fetch(`/api/v1/admin/orders/${id}`, {
      headers: {
        'X-Admin-Token': auth.token || '',
        'X-Admin-User': String(auth.userId || '')
      }
    })
    if (!r.ok) throw new Error('failed to load order')
    const data = await r.json()
    order.value = data
    items.value = data.items || []
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    isLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <AdminNav />
  <section class="page-section">
    <h2 class="section-title">Order #{{ order?.id ?? route.params.id }}</h2>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="order" class="grid">
      <div class="card">
        <div><b>User:</b> {{ order.user_id }}</div>
        <div><b>Status:</b> {{ order.status }}</div>
        <div><b>Total:</b> {{ order.total_amount }}</div>
        <div><b>Created:</b> {{ order.created_at }}</div>
      </div>
      <div class="card">
        <h3 class="h3">Items</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Qty</th>
              <th>Price</th>
              <th>Sum</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="it in items" :key="`${it.product_id}-${it.price}`">
              <td>{{ it.product_id }}</td>
              <td>{{ it.quantity }}</td>
              <td>{{ it.price }}</td>
              <td>{{ (Number(it.price) * Number(it.quantity)).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.page-section { padding: 16px; }
.section-title { margin: 0 0 12px; font-weight: 800; font-size: 20px; }
.grid { display: grid; gap: 16px; }
.card { padding: 12px; border: 1px solid #eee; border-radius: 12px; background: #fff; }
.h3 { margin: 0 0 8px; font-size: 16px; }
.table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 10px; border-bottom: 1px solid #eee; text-align: left; }
</style>

