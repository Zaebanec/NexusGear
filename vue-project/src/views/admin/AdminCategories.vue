<script setup>
import { ref, onMounted, computed } from 'vue'
import AdminNav from '../../components/admin/AdminNav.vue'
import { useAuthStore } from '../../stores/auth.js'
import { useUiStore } from '../../stores/ui.js'

const categories = ref([])
const isLoading = ref(false)
const error = ref('')

const newName = ref('')
const editId = ref(null)
const editName = ref('')

// Search & Pagination
const searchQuery = ref('')
const page = ref(1)
const perPageOptions = [10, 20, 50]
const perPage = ref(10)
const filtered = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return categories.value
  return categories.value.filter(c => String(c.name || c.title || '').toLowerCase().includes(q) || String(c.id).includes(q))
})
const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / perPage.value)))
const paginated = computed(() => {
  const start = (page.value - 1) * perPage.value
  return filtered.value.slice(start, start + perPage.value)
})

const auth = useAuthStore()
const ui = useUiStore()

onMounted(async () => {
  await auth.bootstrapFromTwa()
  try {
    isLoading.value = true
    const r = await fetch('/api/v1/admin/categories', { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
    if (!r.ok) throw new Error('failed to load categories')
    categories.value = await r.json()
    page.value = 1
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    isLoading.value = false
  }
})

async function createCategory() {
  const name = newName.value.trim()
  if (name.length < 2) { ui.toast('Name must be at least 2 chars', 'error', 2500); return }
  const r = await fetch('/api/v1/admin/categories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify({ name })
  })
  if (r.ok) {
    const created = await r.json()
    categories.value.push(created)
    page.value = 1
    newName.value = ''
    ui.toast('Category created', 'success', 1800)
  } else {
    ui.toast('Failed to create category', 'error', 2500)
  }
}

function startEdit(c) {
  editId.value = c.id
  editName.value = c.name || ''
}

async function saveEdit() {
  if (!editId.value) return
  const name = editName.value.trim()
  if (name.length < 2) { ui.toast('Name must be at least 2 chars', 'error', 2500); return }
  const r = await fetch(`/api/v1/admin/categories/${editId.value}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify({ name })
  })
  if (r.ok) {
    const updated = await r.json()
    const idx = categories.value.findIndex(x => x.id === updated.id)
    if (idx !== -1) categories.value[idx] = updated
    page.value = 1
    editId.value = null
    editName.value = ''
    ui.toast('Saved', 'success', 1500)
  } else {
    ui.toast('Failed to save', 'error', 2500)
  }
}

async function removeCategory(id) {
  const r = await fetch(`/api/v1/admin/categories/${id}`, { method: 'DELETE', headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (r.ok) {
    categories.value = categories.value.filter(x => x.id !== id)
    if (page.value > totalPages.value) page.value = totalPages.value
    ui.toast('Deleted', 'success', 1500)
  } else {
    ui.toast('Failed to delete', 'error', 2500)
  }
}
</script>

<template>
  <AdminNav />
  <section class="page-section">
    <h2 class="section-title">Categories</h2>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div class="panel panel-top">
        <input class="field" v-model="searchQuery" placeholder="Search by id or name" @input="(page = 1)" />
        <div class="spacer" />
        <label class="muted">Per page</label>
        <select class="field" v-model.number="perPage" @change="(page = 1)">
          <option v-for="o in perPageOptions" :key="o" :value="o">{{ o }}</option>
        </select>
      </div>
      <div class="panel">
        <input class="field" v-model="newName" placeholder="New category name" />
        <button class="btn" @click="createCategory">Create</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in paginated" :key="c.id">
            <td>{{ c.id }}</td>
            <td>
              <template v-if="editId === c.id">
                <input class="field" v-model="editName" />
              </template>
              <template v-else>
                {{ c.name || c.title }}
              </template>
            </td>
            <td class="actions">
              <template v-if="editId === c.id">
                <button class="btn" @click="saveEdit">Save</button>
                <button class="btn" @click="(editId = null, editName = '')">Cancel</button>
              </template>
              <template v-else>
                <button class="btn" @click="startEdit(c)">Edit</button>
                <button class="btn" @click="removeCategory(c.id)">Delete</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn" :disabled="page <= 1" @click="page = Math.max(1, page - 1)">Prev</button>
        <span class="muted">Page {{ page }} / {{ totalPages }}</span>
        <button class="btn" :disabled="page >= totalPages" @click="page = Math.min(totalPages, page + 1)">Next</button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.page-section { padding: 16px; }
.section-title { margin: 0 0 12px; font-weight: 800; font-size: 20px; }
.table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 10px; border-bottom: 1px solid #eee; text-align: left; }
.panel { display: flex; gap: 8px; margin: 8px 0 12px; align-items: center; }
.panel-top { margin-top: 0; }
.spacer { flex: 1; }
.field { padding: 8px 10px; border: 1px solid #eee; border-radius: 8px; }
.actions { display: flex; gap: 6px; }
.btn { appearance:none; border:0; border-radius:8px; padding:6px 10px; background:#f3f4f6; }
.pagination { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
.muted { color: #6b7280; font-size: 12px; }
</style>

