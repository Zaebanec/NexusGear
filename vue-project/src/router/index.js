// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
const CategoriesView = () => import('../views/CategoriesView.vue')
const ProductsView = () => import('../views/ProductsView.vue')
const CartView = () => import('../views/CartView.vue')
const SuccessView = () => import('../views/SuccessView.vue')
const AdminDashboard = () => import('../views/admin/AdminDashboard.vue')
const AdminCategories = () => import('../views/admin/AdminCategories.vue')
const AdminProducts = () => import('../views/admin/AdminProducts.vue')
const AdminOrders = () => import('../views/admin/AdminOrders.vue')
const AdminOrderDetails = () => import('../views/admin/AdminOrderDetails.vue')

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
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboard,
    },
    {
      path: '/admin/categories',
      name: 'admin-categories',
      component: AdminCategories,
    },
    {
      path: '/admin/products',
      name: 'admin-products',
      component: AdminProducts,
    },
    {
      path: '/admin/orders',
      name: 'admin-orders',
      component: AdminOrders,
    },
    {
      path: '/admin/orders/:id',
      name: 'admin-order-details',
      component: AdminOrderDetails,
      props: true,
    }
  ]
})

export default router