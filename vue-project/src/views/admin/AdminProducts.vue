<script setup>
import { ref, onMounted } from 'vue'
import AdminNav from '../../components/admin/AdminNav.vue'
import { useAuthStore } from '../../stores/auth.js'
import { useUiStore } from '../../stores/ui.js'

const products = ref([])
const categories = ref([])
const isLoading = ref(false)
const error = ref('')

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

async function loadProducts() {
  const r = await fetch('/api/v1/admin/products', { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (!r.ok) throw new Error('failed to load products')
  products.value = await r.json()
}

async function loadCategories() {
  const r = await fetch('/api/v1/admin/categories', { headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (!r.ok) throw new Error('failed to load categories')
  categories.value = await r.json()
}

onMounted(async () => {
  await auth.bootstrapFromTwa()
  try {
    isLoading.value = true
    await Promise.all([loadProducts(), loadCategories()])
  } catch (e) {
    error.value = e?.message || 'error'
  } finally {
    isLoading.value = false
  }
})

async function createProduct() {
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
  const r = await fetch('/api/v1/admin/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') },
    body: JSON.stringify(payload)
  })
  if (r.ok) {
    const created = await r.json()
    products.value.push(created)
    newName.value = ''
    newDescription.value = ''
    newPrice.value = ''
    newCategoryId.value = ''
    ui.toast('Product created', 'success', 1800)
  } else {
    ui.toast('Failed to create product', 'error', 2500)
  }
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
    const updated = await r.json()
    const idx = products.value.findIndex(x => x.id === updated.id)
    if (idx !== -1) products.value[idx] = updated
    editId.value = null
    editName.value = ''
    editDescription.value = ''
    editPrice.value = ''
    editCategoryId.value = ''
    ui.toast('Saved', 'success', 1500)
  } else {
    ui.toast('Failed to save', 'error', 2500)
  }
}

async function removeProduct(id) {
  const r = await fetch(`/api/v1/admin/products/${id}`, { method: 'DELETE', headers: { 'X-Admin-Token': auth.token || '', 'X-Admin-User': String(auth.userId || '') } })
  if (r.ok) {
    products.value = products.value.filter(x => x.id !== id)
    ui.toast('Deleted', 'success', 1500)
  } else {
    ui.toast('Failed to delete', 'error', 2500)
  }
}
</script>

<template>
  <AdminNav />
  <section class="page-section">
    <h2 class="section-title">Products</h2>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <div class="panel">
        <input class="field" v-model="newName" placeholder="Name" />
        <input class="field" v-model="newDescription" placeholder="Description" />
        <input class="field" v-model="newPrice" placeholder="Price" inputmode="decimal" />
        <select class="field" v-model="newCategoryId">
          <option value="" disabled>Category</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <button class="btn" @click="createProduct">Create</button>
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
                {{ p.category_id }}
              </template>
            </td>
            <td class="actions">
              <template v-if="editId === p.id">
                <button class="btn" @click="saveEdit">Save</button>
                <button class="btn" @click="(editId = null, editName = '', editDescription = '', editPrice = '', editCategoryId = '')">Cancel</button>
              </template>
              <template v-else>
                <button class="btn" @click="startEdit(p)">Edit</button>
                <button class="btn" @click="removeProduct(p.id)">Delete</button>
              </template>
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
.panel { display: grid; grid-template-columns: 1.5fr 2fr 1fr 1fr auto; gap: 8px; margin: 8px 0 12px; }
.field { padding: 8px 10px; border: 1px solid #eee; border-radius: 8px; width: 100%; }
.actions { display: flex; gap: 6px; }
.btn { appearance:none; border:0; border-radius:8px; padding:6px 10px; background:#f3f4f6; }
</style>

