# Roadmap — Nexus Gear Store

## Фаза 0: Фундамент и Инфраструктура — Завершена
- [x] Git
- [x] Python 3.11, Poetry (package-mode = false)
- [x] Dockerfile, docker-compose
- [x] Конфигурация и DI (Dishka), единые префиксы в .env/config
- [x] БД и миграции (Alembic)
- [x] Первый запуск

## Фаза 1: Ядро Приложения — Завершена
- [x] Domain: `Category`, `Product`, `Order`, `OrderItem`, `User`
- [x] Контракты репозиториев (interfaces)
- [x] Реализация репозиториев на SQLAlchemy
- [x] Application‑сервисы (Каталог, Заказы, Пользователи, AI‑консультант)

## Фаза 1.5: Стабилизация/Пивот — Завершена
- [x] Переход на Webhook (бот): `on_startup`/`on_shutdown`, секрет в заголовке
- [x] Сетевые настройки и схема раздачи
- [x] Концепция "бот как пульт" утверждена

## Фаза 2: Web App "Магазин" — Завершена
- [x] Публичные API:
  - GET `/api/categories`
  - GET `/api/products?category_id=...`
- [x] Веб‑UI каталога (Vue 3, Pinia) и клиентская корзина
- [x] CORS (aiohttp-cors, allow_credentials, методы/заголовки)
- [x] Dev‑proxy (Vite) — при локальной разработке

## Фаза 3: Фичи Бота — Завершена
- [x] AI‑консультант
- [x] Кнопка "Открыть магазин" (TWA)

## Фаза 4: Оформление заказа (Checkout)
- [x] (Frontend) Страница заказа + валидации (имя/телефон/адрес), интеграция с TWA MainButton
- [x] (Backend) POST `/api/create_order` (pydantic‑схема `CreateOrderSchema`)
- [x] (Backend) Уведомление в Telegram через `INotifier` (`TelegramNotifier`)
- [ ] Сквозные E2E тесты сценария: `/start -> TWA -> Заказ -> Уведомление`

## Фаза 5: Администрирование
- [x] (Backend) Админ‑API:
  - Категории: GET/POST/PUT/DELETE `/api/v1/admin/categories`
  - Товары: GET/POST/PUT/DELETE `/api/v1/admin/products`
  - Заказы: GET/GET by id/PATCH status `/api/v1/admin/orders[...]`
  - HMAC‑аутентификация: `X-Admin-User` + `X-Admin-Token`
- [x] (Frontend) Админ‑SPA (Vue): `AdminDashboard`, `AdminCategories`, `AdminProducts`, `AdminOrders`, `AdminOrderDetails`
- [x] Валидация TWA в `/api/v1/auth/telegram/validate` → выдача токена/идентификатора
- [ ] Улучшения: пагинация/поиск/фильтры, уведомления об ошибках, подтверждения действий

## Фаза 6: Финализация и Демонстрация
- [ ] UI/UX полировка (адаптив, лоадеры, пустые состояния, i18n в админке)
- [ ] Безопасность: rate‑limit, защита от повторов, унификация ошибок API
- [ ] Документация: demo‑скрипт, README, диаграмма архитектуры
- [ ] Тесты: unit+api (>70% покрытие), E2E (Playwright/Cypress)
- [ ] CI/CD: линтеры (ruff/black/eslint), тесты, сборки, деплой
- [ ] Об observability: структурные логи, базовые метрики

## Ближайший бэклог
- [ ] E2E checkout тест (успех/ошибки)
- [ ] Админ‑UI: пагинация и поиск (категории/товары/заказы)
- [ ] Middleware rate‑limit для `/api/v1/admin/*`
- [ ] Единый формат ошибок API
- [ ] Обновление README с ссылкой на Roadmap

## Дальше (опционально): Платежи
- [ ] Интеграция платёжного провайдера + вебхуки
- [ ] Идемпотентность и статусы заказов (pending/paid/cancelled)
- [ ] Страницы/уведомления по оплате


