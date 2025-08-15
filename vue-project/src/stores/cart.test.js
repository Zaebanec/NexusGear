import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCartStore } from './cart.js'

describe('cart store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    // reset localStorage side-effects
    try { localStorage.clear() } catch { /* ignore */ }
  })

  it('adds and counts items', () => {
    const cart = useCartStore()
    cart.addProduct({ id: 1, name: 'A', price: 100 })
    cart.addProduct({ id: 1, name: 'A', price: 100 })
    cart.addProduct({ id: 2, name: 'B', price: 50 })
    expect(cart.totalItems).toBe(3)
    expect(cart.totalPrice).toBe(250)
  })

  it('decrements and removes when qty=0', () => {
    const cart = useCartStore()
    cart.addProduct({ id: 1, price: 10 })
    expect(cart.items.length).toBe(1)
    cart.decrementProduct(1)
    expect(cart.items.length).toBe(0)
  })
})


