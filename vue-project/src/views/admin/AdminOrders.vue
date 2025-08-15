<script setup>
import { ref, onMounted } from 'vue'
import AdminNav from '../../components/admin/AdminNav.vue'
import { useAuthStore } from '../../stores/auth.js'

const orders = ref([])
const isLoading = ref(false)
const error = ref('')

const auth = useAuthStore()

async function load() {
  try {
    isLoading.value = true
    const r = await fetch('/api/v1/admin/orders', { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
    if (!r.ok) throw new Error('failed to load orders')
    orders.value = await r.json()
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    isLoading.value = false
  }
}

async function updateStatus(id, status) {
  const r = await fetch(`/api/v1/admin/orders/${id}` ,{
    method:'PATCH',
    headers: { 'Content-Type':'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify({ status })
  })
  if (r.ok) await load()
}

onMounted(load)
</script>

<template>
  <AdminNav />
  <section class="page-section">
    <h2 class="section-title">Orders</h2>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>User</th>
            <th>Status</th>
            <th>Total</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="o in orders" :key="o.id">
            <td>{{ o.id }}</td>
            <td>{{ o.user_id }}</td>
            <td>{{ o.status }}</td>
            <td>{{ o.total_amount }}</td>
            <td class="actions">
              <button class="btn" :disabled="o.status==='paid'" @click="updateStatus(o.id,'paid')">Mark Paid</button>
              <button class="btn" :disabled="o.status==='cancelled'" @click="updateStatus(o.id,'cancelled')">Cancel</button>
              <RouterLink class="btn" :to="{ name: 'admin-order-details', params: { id: o.id } }">Details</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.page-section { padding: 16px; }
.section-title { margin: 0 0 12px; font-weight: 800; font-size: 20px; }
.table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 10px; border-bottom: 1px solid #eee; text-align: left; }
.actions { display: flex; gap: 8px; }
.btn { appearance:none; border:0; border-radius:8px; padding:6px 10px; background:#f3f4f6; }
</style>

