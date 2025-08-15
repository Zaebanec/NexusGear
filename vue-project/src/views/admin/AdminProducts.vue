<script setup>
import { ref, onMounted, computed } from 'vue'
import AdminNav from '../../components/admin/AdminNav.vue'
import { useAuthStore } from '../../stores/auth.js'
import { useUiStore } from '../../stores/ui.js'

const products = ref([])
const categories = ref([])
const isLoading = ref(false)
const error = ref('')

// Search & Pagination
const searchQuery = ref('')
const page = ref(1)
const perPageOptions = [10, 20, 50]
const perPage = ref(10)
const total = ref(0)
const categoryById = computed(() => {
  /** @type {Record<string, string>} */
  const m = {}
  for (const c of categories.value) m[String(c.id)] = c.name || ''
  return m
})
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage.value)))

// Create form
const newName = ref('')
const newDescription = ref('')
const newPrice = ref('')
const newCategoryId = ref('')

// Edit form
const editId = ref(null)
const editName = ref('')
const editDescription = ref('')
const editPrice = ref('')
const editCategoryId = ref('')

const auth = useAuthStore()
const ui = useUiStore()

const isCreating = ref(false)
const isSaving = ref(false)
const deletingId = ref(0)

const selectedCategory = ref('')
async function loadProducts() {
  const params = new URLSearchParams()
  if (searchQuery.value.trim()) params.set('q', searchQuery.value.trim())
  if (selectedCategory.value) params.set('category_id', String(selectedCategory.value))
  params.set('limit', String(perPage.value))
  params.set('offset', String((page.value - 1) * perPage.value))
  const r = await fetch(`/api/v1/admin/products?${params.toString()}`, { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (!r.ok) { await ui.toastFromResponse(r); throw new Error('failed to load products') }
  products.value = await r.json()
  const tc = Number(r.headers.get('x-total-count') || '0')
  total.value = Number.isFinite(tc) ? tc : products.value.length
}

async function loadCategories() {
  const r = await fetch('/api/v1/admin/categories', { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (!r.ok) { await ui.toastFromResponse(r); throw new Error('failed to load categories') }
  categories.value = await r.json()
}

onMounted(async () => {
  await auth.bootstrapFromTwa()
  try {
    isLoading.value = true
    await Promise.all([loadProducts(), loadCategories()])
    page.value = 1
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    isLoading.value = false
  }
})

async function createProduct() {
  if (isCreating.value) return
  const name = newName.value.trim()
  const description = newDescription.value.trim()
  const priceNum = Number(newPrice.value)
  const categoryIdNum = Number(newCategoryId.value)
  if (name.length < 2) { ui.toast('Name must be at least 2 chars', 'error', 2500); return }
  if (description.length < 5) { ui.toast('Description must be at least 5 chars', 'error', 2500); return }
  if (!isFinite(priceNum) || priceNum <= 0) { ui.toast('Price must be > 0', 'error', 2500); return }
  if (!categoryIdNum) { ui.toast('Select category', 'error', 2500); return }
  const payload = {
    name,
    description,
    price: priceNum,
    category_id: categoryIdNum,
  }
  isCreating.value = true
  const r = await fetch('/api/v1/admin/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify(payload)
  })
  if (r.ok) {
    await r.json()
    // после создания перезагружаем первую страницу
    page.value = 1
    await loadProducts()
    newName.value = ''
    newDescription.value = ''
    newPrice.value = ''
    newCategoryId.value = ''
    ui.toast('Product created', 'success', 1800)
  } else {
    await ui.toastFromResponse(r)
  }
  isCreating.value = false
}

function startEdit(p) {
  editId.value = p.id
  editName.value = p.name
  editDescription.value = p.description || ''
  editPrice.value = String(p.price)
  editCategoryId.value = String(p.category_id)
}

async function saveEdit() {
  if (!editId.value) return
  if (isSaving.value) return
  isSaving.value = true
  const payload = {
    name: editName.value.trim(),
    description: editDescription.value.trim(),
    price: Number(editPrice.value),
    category_id: Number(editCategoryId.value),
  }
  if (payload.name.length < 2) { ui.toast('Name must be at least 2 chars', 'error', 2500); return }
  if (payload.description.length < 5) { ui.toast('Description must be at least 5 chars', 'error', 2500); return }
  if (!isFinite(payload.price) || payload.price <= 0) { ui.toast('Price must be > 0', 'error', 2500); return }
  if (!payload.category_id) { ui.toast('Select category', 'error', 2500); return }
  const r = await fetch(`/api/v1/admin/products/${editId.value}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify(payload)
  })
  if (r.ok) {
    await r.json()
    // обновляем текущую страницу
    await loadProducts()
    editId.value = null
    editName.value = ''
    editDescription.value = ''
    editPrice.value = ''
    editCategoryId.value = ''
    ui.toast('Saved', 'success', 1500)
  } else {
    await ui.toastFromResponse(r)
  }
  isSaving.value = false
}

async function removeProduct(id) {
  if (!confirm(`Delete product #${id}?`)) return
  deletingId.value = id
  const r = await fetch(`/api/v1/admin/products/${id}`, { method: 'DELETE', headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (r.ok) {
    // перезагружаем страницу; если опустела, откатимся на предыдущую
    await loadProducts()
    if (products.value.length === 0 && page.value > 1) {
      page.value = page.value - 1
      await loadProducts()
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
    <h2 class="section-title">Products</h2>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div class="panel panel-top">
        <input class="field" v-model="searchQuery" placeholder="Search by id, name, description or category" @input="(page = 1, loadProducts())" />
        <div class="spacer" />
        <select class="field" v-model="selectedCategory" @change="(page = 1, loadProducts())">
          <option value="">All categories</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <label class="muted">Per page</label>
        <select class="field" v-model.number="perPage" @change="(page = 1, loadProducts())">
          <option v-for="o in perPageOptions" :key="o" :value="o">{{ o }}</option>
        </select>
      </div>
      <div class="panel">
        <input class="field" v-model="newName" placeholder="Name" />
        <input class="field" v-model="newDescription" placeholder="Description" />
        <input class="field" v-model="newPrice" placeholder="Price" inputmode="decimal" />
        <select class="field" v-model="newCategoryId">
          <option value="" disabled>Category</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <button class="btn" :disabled="isCreating" @click="createProduct">{{ isCreating ? 'Creating…' : 'Create' }}</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Price</th>
            <th>Category</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id">
            <td>{{ p.id }}</td>
            <td>
              <template v-if="editId === p.id">
                <input class="field" v-model="editName" />
              </template>
              <template v-else>
                {{ p.name }}
              </template>
            </td>
            <td>
              <template v-if="editId === p.id">
                <input class="field" v-model="editDescription" />
              </template>
              <template v-else>
                {{ p.description }}
              </template>
            </td>
            <td>
              <template v-if="editId === p.id">
                <input class="field" v-model="editPrice" inputmode="decimal" />
              </template>
              <template v-else>
                {{ p.price }}
              </template>
            </td>
            <td>
              <template v-if="editId === p.id">
                <select class="field" v-model="editCategoryId">
                  <option v-for="c in categories" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
                </select>
              </template>
              <template v-else>
                {{ categoryById[String(p.category_id)] || p.category_id }}
              </template>
            </td>
            <td class="actions">
              <template v-if="editId === p.id">
                <button class="btn" :disabled="isSaving" @click="saveEdit">{{ isSaving ? 'Saving…' : 'Save' }}</button>
                <button class="btn" @click="(editId = null, editName = '', editDescription = '', editPrice = '', editCategoryId = '')">Cancel</button>
              </template>
              <template v-else>
                <button class="btn" @click="startEdit(p)">Edit</button>
                <button class="btn" :disabled="deletingId===p.id" @click="removeProduct(p.id)">{{ deletingId===p.id ? 'Deleting…' : 'Delete' }}</button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="pagination" v-if="totalPages > 1">
        <button class="btn" :disabled="page <= 1" @click="(page = Math.max(1, page - 1), loadProducts())">Prev</button>
        <span class="muted">Page {{ page }} / {{ totalPages }}</span>
        <button class="btn" :disabled="page >= totalPages" @click="(page = Math.min(totalPages, page + 1), loadProducts())">Next</button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.page-section { padding: 16px; }
.section-title { margin: 0 0 12px; font-weight: 800; font-size: 20px; }
.table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 10px; border-bottom: 1px solid #eee; text-align: left; }
.panel { display: grid; grid-template-columns: 1.5fr 2fr 1fr 1fr auto; gap: 8px; margin: 8px 0 12px; align-items: center; }
.panel-top { display: flex; gap: 8px; grid-template-columns: none; }
.spacer { flex: 1; }
.field { padding: 8px 10px; border: 1px solid #eee; border-radius: 8px; width: 100%; }
.actions { display: flex; gap: 6px; }
.btn { appearance:none; border:0; border-radius:8px; padding:6px 10px; background:#f3f4f6; }
.pagination { display: flex; align-items: center; gap: 10px; margin-top: 10px; }
.muted { color: #6b7280; font-size: 12px; }
</style>

