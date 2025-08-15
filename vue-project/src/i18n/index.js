import { createI18n } from 'vue-i18n'

const ru = {
  brand: 'NexusShop',
  nav: {
    cart: 'Корзина',
  },
  categories: 'Категории',
  productsInCategory: 'Товары в категории',
  cart: {
    title: 'Корзина',
    empty: 'Корзина пуста',
    checkout: 'Оформить заказ',
    total: 'Итого',
    name: 'Ваше имя',
    phone: 'Телефон',
    address: 'Адрес доставки',
    phoneHint: 'Введите номер формата +7 ХХХ ХХХ-ХХ-ХХ',
  },
  success: {
    title: 'Заказ оформлен',
    number: 'Номер заказа',
    back: 'Вернуться в магазин',
  }
}

const en = {
  brand: 'NexusShop',
  nav: { cart: 'Cart' },
  categories: 'Categories',
  productsInCategory: 'Products',
  cart: {
    title: 'Cart', empty: 'Your cart is empty', checkout: 'Checkout', total: 'Total',
    name: 'Your name', phone: 'Phone', address: 'Delivery address', phoneHint: 'Enter phone as +7 XXX XXX-XX-XX'
  },
  success: { title: 'Order placed', number: 'Order #', back: 'Back to shop' }
}

export function setupI18n() {
  // detect language from Telegram or browser
  const tg = typeof window !== 'undefined' ? /** @type {any} */ (window).Telegram?.WebApp : null
  const lang = tg?.initDataUnsafe?.user?.language_code || navigator.language || 'ru'
  const locale = lang.startsWith('ru') ? 'ru' : 'en'
  return createI18n({ legacy: false, locale, fallbackLocale: 'en', messages: { ru, en } })
}


