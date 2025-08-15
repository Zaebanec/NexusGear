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

// Search & Pagination (server-side)
const searchQuery = ref('')
const page = ref(1)
const perPageOptions = [10, 20, 50]
const perPage = ref(10)
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))

const auth = useAuthStore()
const ui = useUiStore()

const isCreating = ref(false)
const isSaving = ref(false)
const deletingId = ref(0)

async function loadCategories() {
  const params = new URLSearchParams()
  if (searchQuery.value.trim()) params.set('q', searchQuery.value.trim())
  params.set('limit', String(perPage.value))
  params.set('offset', String((page.value - 1) * perPage.value))
  const r = await fetch(`/api/v1/admin/categories?${params.toString()}`, { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (!r.ok) { await ui.toastFromResponse(r); throw new Error('failed to load categories') }
  categories.value = await r.json()
  const tc = Number(r.headers.get('x-total-count') || '0')
  total.value = Number.isFinite(tc) ? tc : categories.value.length
}

onMounted(async () => {
  await auth.bootstrapFromTwa()
  try {
    isLoading.value = true
    await loadCategories()
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    isLoading.value = false
  }
})

async function createCategory() {
  if (isCreating.value) return
  const name = newName.value.trim()
  if (name.length < 2) { ui.toast('Name must be at least 2 chars', 'error', 2500); return }
  isCreating.value = true
  const r = await fetch('/api/v1/admin/categories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify({ name })
  })
  if (r.ok) {
    await r.json()
    page.value = 1
    await loadCategories()
    newName.value = ''
    ui.toast('Category created', 'success', 1800)
  } else {
    await ui.toastFromResponse(r)
  }
  isCreating.value = false
}

function startEdit(c) {
  editId.value = c.id
  editName.value = c.name || ''
}

async function saveEdit() {
  if (!editId.value) return
  if (isSaving.value) return
  isSaving.value = true
  const name = editName.value.trim()
  if (name.length < 2) { ui.toast('Name must be at least 2 chars', 'error', 2500); return }
  const r = await fetch(`/api/v1/admin/categories/${editId.value}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify({ name })
  })
  if (r.ok) {
    await r.json()
    await loadCategories()
    editId.value = null
    editName.value = ''
    ui.toast('Saved', 'success', 1500)
  } else {
    await ui.toastFromResponse(r)
  }
  isSaving.value = false
}

async function removeCategory(id) {
  if (!confirm(`Delete category #${id}?`)) return
  deletingId.value = id
  const r = await fetch(`/api/v1/admin/categories/${id}`, { method: 'DELETE', headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (r.ok) {
    await loadCategories()
    if (categories.value.length === 0 && page.value > 1) {
      page.value = page.value - 1
      await loadCategories()
    }
    ui.toast('Deleted', 'success', 1500)
  } else {
    await ui.toastFromResponse(r)
  }
  if (deletingId.value === id) deletingId.value = 0
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
        <input class="field" v-model="searchQuery" placeholder="Search by id or name" @input="(page = 1, loadCategories())" />
        <div class="spacer" />
        <label class="muted">Per page</label>
        <select class="field" v-model.number="perPage" @change="(page = 1, loadCategories())">
          <option v-for="o in perPageOptions" :key="o" :value="o">{{ o }}</option>
        </select>
      </div>
      <div class="panel">
        <input class="field" v-model="newName" placeholder="New category name" />
        <button class="btn" :disabled="isCreating" @click="createCategory">{{ isCreating ? 'Creating…' : 'Create' }}</button>
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
          <tr v-for="c in categories" :key="c.id">
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
                <button class="btn" :disabled="isSaving" @click="saveEdit">{{ isSaving ? 'Saving…' : 'Save' }}</button>
                <button class="btn" @click="(editId = null, editName = '')">Cancel</button>
              </template>
              <template v-else>
                <button class="btn" @click="startEdit(c)">Edit</button>
                <button class="btn" :disabled="deletingId===c.id" @click="removeCategory(c.id)">{{ deletingId===c.id ? 'Deleting…' : 'Delete' }}</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn" :disabled="page <= 1" @click="(page = Math.max(1, page - 1), loadCategories())">Prev</button>
        <span class="muted">Page {{ page }} / {{ totalPages }}</span>
        <button class="btn" :disabled="page >= totalPages" @click="(page = Math.min(totalPages, page + 1), loadCategories())">Next</button>
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

