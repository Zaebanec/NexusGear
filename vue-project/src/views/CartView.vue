<script setup>
import { computed, onMounted, watch, ref } from 'vue'
import { useUiStore } from '../stores/ui.js'
import { useCartStore } from '../stores/cart.js'
import { useRouter } from 'vue-router'
import { maskRuPhone, isValidRuPhone, normalizeRuPhone } from '../lib/phone.js'

const cart = useCartStore()
const ui = useUiStore()
const router = useRouter()
const tg = typeof window !== 'undefined' ? window.Telegram?.WebApp || null : null

const total = computed(() => cart.totalPrice)
const itemsCount = computed(() => cart.totalItems)

const fullName = ref('')
const phone = ref('')
const address = ref('')
const isNameValid = computed(() => fullName.value.trim().length >= 2)
const isPhoneValid = computed(() => isValidRuPhone(phone.value))
const isAddressValid = computed(() => address.value.trim().length >= 5)
const isValidForm = computed(() => itemsCount.value > 0 && isNameValid.value && isPhoneValid.value && isAddressValid.value)
const phoneMasked = computed({
  get: () => maskRuPhone(phone.value),
  set: (v) => { phone.value = v },
})

async function submitOrder() {
  if (!itemsCount.value) return
  const payload = {
    items: cart.items.map(i => ({ product_id: i.id, quantity: i.quantity })),
    user: {
      id: tg?.initDataUnsafe?.user?.id || 0,
      first_name: tg?.initDataUnsafe?.user?.first_name || null,
      last_name: tg?.initDataUnsafe?.user?.last_name || null,
      username: tg?.initDataUnsafe?.user?.username || null,
    },
    full_name: fullName.value,
    phone: normalizeRuPhone(phone.value),
    address: address.value,
  }
  const res = await fetch('/api/create_order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const data = await res.json()
  if (data?.status === 'ok') {
    cart.clear()
    ui.toast(`Заказ №${data.order_id} создан`, 'success')
    router.replace({ name: 'success', params: { id: data.order_id } })
  } else {
    ui.toast(data?.message || 'Ошибка оформления', 'error', 4000)
    tg?.HapticFeedback?.notificationOccurred?.('error')
  }
}

onMounted(() => {
  if (!tg) return
  tg.ready?.()
  tg.MainButton?.setParams({ text: 'Оформить заказ', color: '#1d4ed8', text_color: '#ffffff' })
  const clickHandler = async () => {
    if (!isValidForm.value) { ui.toast('Проверьте форму заказа', 'error', 3000); tg.HapticFeedback?.notificationOccurred?.('error'); return }
    try { tg.MainButton?.showProgress?.(); await submitOrder() } finally { tg.MainButton?.hideProgress?.() }
  }
  tg.MainButton?.onClick(clickHandler)
  const syncButton = () => {
    if (isValidForm.value) { tg.MainButton?.show?.(); tg.MainButton?.enable?.() } else { tg.MainButton?.show?.(); tg.MainButton?.disable?.() }
  }
  watch([itemsCount, fullName, phone, address], syncButton, { immediate: true })
})
</script>

<template>
  <section class="page-section">
    <h2 class="section-title">Корзина</h2>
    <div v-if="itemsCount" class="cart-list">
      <div v-for="p in cart.items" :key="p.id" class="cart-row">
        <div class="title">{{ p.name }}</div>
        <div class="qty">
          <button class="btn" @click="(tg?.HapticFeedback?.impactOccurred?.('light'), cart.decrementProduct(p.id))">−</button>
          <span class="q">{{ p.quantity }}</span>
          <button class="btn" @click="(tg?.HapticFeedback?.impactOccurred?.('light'), cart.addProduct(p))">+</button>
        </div>
        <div class="sum">{{ new Intl.NumberFormat('ru-RU',{ style: 'currency', currency: 'RUB', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(p.price * p.quantity) }}</div>
        <button class="remove" @click="cart.removeProduct(p.id)">×</button>
      </div>
      <div class="summary">Итого: {{ new Intl.NumberFormat('ru-RU',{ style: 'currency', currency: 'RUB', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(total) }}</div>

      <div class="form">
        <input class="field" :class="{ invalid: !isNameValid && fullName }" v-model="fullName" placeholder="Ваше имя" />
        <input class="field" :class="{ invalid: !isPhoneValid && phone }" v-model="phoneMasked" placeholder="Телефон" inputmode="tel" />
        <input class="field" :class="{ invalid: !isAddressValid && address }" v-model="address" placeholder="Адрес доставки" />
        <p class="hint" v-if="phone && !isPhoneValid">Введите номер формата +7 ХХХ ХХХ-ХХ-ХХ</p>
      </div>
    </div>
    <div v-else class="empty">Корзина пуста</div>
  </section>
</template>

<style scoped>
.page-section { padding: 16px; }
.section-title { margin: 0 0 12px; font-weight: 700; font-size: 18px; }
.cart-list { display: flex; flex-direction: column; gap: 12px; }
.cart-row { display: grid; grid-template-columns: 1fr auto auto auto; gap: 8px; align-items: center; padding: 12px; border: 1px solid #e5e7eb; border-radius: 12px; }
.qty { display: grid; grid-template-columns: 36px auto 36px; gap: 6px; align-items: center; }
.btn { appearance: none; border: 0; border-radius: 8px; padding: 8px; background: #f3f4f6; font-weight: 700; }
.q { min-width: 24px; text-align: center; font-weight: 700; }
.sum { font-weight: 800; }
.remove { appearance: none; border: 0; background: transparent; font-size: 18px; }
.form { display: grid; gap: 8px; margin-top: 8px; }
.field { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #e5e7eb; }
.field.invalid { border-color: #ef4444; }
.hint { margin: 4px 0 0; color: #ef4444; font-size: 12px; }
</style>
