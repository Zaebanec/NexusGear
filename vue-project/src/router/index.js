// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import CategoriesView from '../views/CategoriesView.vue'
import ProductsView from '../views/ProductsView.vue'
// --- ИЗМЕНЕНИЕ: Импортируем страницу корзины ---
import CartView from '../views/CartView.vue'
import SuccessView from '../views/SuccessView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: CategoriesView
    },
    {
      path: '/categories',
      name: 'categories',
      component: CategoriesView
    },
    {
      path: '/categories/:id', 
      name: 'products',
      component: ProductsView
    },
    // --- ИЗМЕНЕНИЕ: Добавляем маршрут для корзины ---
    {
      path: '/cart',
      name: 'cart',
      component: CartView
    },
    {
      path: '/success/:id',
      name: 'success',
      component: SuccessView,
      props: true,
    }
  ]
})

export default router