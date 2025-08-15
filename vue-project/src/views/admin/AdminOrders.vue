<script setup>
import { ref, onMounted, computed } from 'vue'
import AdminNav from '../../components/admin/AdminNav.vue'
import { useAuthStore } from '../../stores/auth.js'
import { useUiStore } from '../../stores/ui.js'

const orders = ref([])
const isLoading = ref(false)
const error = ref('')

const auth = useAuthStore()
const ui = useUiStore()

// Search & Pagination
const searchQuery = ref('')
const statusFilter = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const page = ref(1)
const perPageOptions = [10, 20, 50]
const perPage = ref(10)
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))

async function load() {
  try {
    isLoading.value = true
    const params = new URLSearchParams()
    if (searchQuery.value.trim()) params.set('q', searchQuery.value.trim())
    if (statusFilter.value) params.set('status', statusFilter.value)
    if (dateFrom.value) params.set('created_from', dateFrom.value)
    if (dateTo.value) params.set('created_to', dateTo.value)
    params.set('limit', String(perPage.value))
    params.set('offset', String((page.value - 1) * perPage.value))
    const r = await fetch(`/api/v1/admin/orders?${params.toString()}`, { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
    if (!r.ok) { await ui.toastFromResponse(r); throw new Error('failed to load orders') }
    orders.value = await r.json()
    const tc = Number(r.headers.get('x-total-count') || '0')
    total.value = Number.isFinite(tc) ? tc : orders.value.length
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    isLoading.value = false
  }
}

const updatingId = ref(0)
async function updateStatus(id, status) {
  if (!confirm(`Set order #${id} status to ${status}?`)) return
  updatingId.value = id
  const r = await fetch(`/api/v1/admin/orders/${id}` ,{
    method:'PATCH',
    headers: { 'Content-Type':'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify({ status })
  })
  if (r.ok) await load(); else await ui.toastFromResponse(r)
  if (updatingId.value === id) updatingId.value = 0
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
      <div class="panel panel-top">
        <input class="field" v-model="searchQuery" placeholder="Search by order id or user id" @input="(page = 1, load())" />
        <div class="spacer" />
        <select class="field" v-model="statusFilter" @change="(page = 1, load())">
          <option value="">All statuses</option>
          <option value="pending">pending</option>
          <option value="paid">paid</option>
          <option value="cancelled">cancelled</option>
        </select>
        <input class="field" type="datetime-local" v-model="dateFrom" @change="(page = 1, load())" />
        <input class="field" type="datetime-local" v-model="dateTo" @change="(page = 1, load())" />
        <label class="muted">Per page</label>
        <select class="field" v-model.number="perPage" @change="(page = 1, load())">
          <option v-for="o in perPageOptions" :key="o" :value="o">{{ o }}</option>
        </select>
      </div>
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
              <button class="btn" :disabled="o.status==='paid' || updatingId===o.id" @click="updateStatus(o.id,'paid')">{{ updatingId===o.id ? 'Updating…' : 'Mark Paid' }}</button>
              <button class="btn" :disabled="o.status==='cancelled' || updatingId===o.id" @click="updateStatus(o.id,'cancelled')">{{ updatingId===o.id ? 'Updating…' : 'Cancel' }}</button>
              <RouterLink class="btn" :to="{ name: 'admin-order-details', params: { id: o.id } }">Details</RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn" :disabled="page <= 1" @click="(page = Math.max(1, page - 1), load())">Prev</button>
        <span class="muted">Page {{ page }} / {{ totalPages }}</span>
        <button class="btn" :disabled="page >= totalPages" @click="(page = Math.min(totalPages, page + 1), load())">Next</button>
      </div>
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
.panel-top { display: flex; align-items: center; gap: 8px; margin: 8px 0 12px; }
.field { padding: 8px 10px; border: 1px solid #eee; border-radius: 8px; }
.spacer { flex: 1; }
.pagination { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
.muted { color: #6b7280; font-size: 12px; }
</style>

