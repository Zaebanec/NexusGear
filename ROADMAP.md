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
- [x] Сквозные E2E тесты сценария: `/start -> TWA -> Заказ -> Уведомление` (15.08.2025 — добавлен тест `tests/e2e/test_full_twa_flow.py`; эмулируется /start через webhook, затем заказ через REST, проверяется регистрация пользователя и вызов уведомления)

## Фаза 5: Администрирование
- [x] (Backend) Админ‑API:
  - Категории: GET/POST/PUT/DELETE `/api/v1/admin/categories`
  - Товары: GET/POST/PUT/DELETE `/api/v1/admin/products`
  - Заказы: GET/GET by id/PATCH status `/api/v1/admin/orders[...]`
  - HMAC‑аутентификация: `X-Admin-User` + `X-Admin-Token`
- [x] (Frontend) Админ‑SPA (Vue): `AdminDashboard`, `AdminCategories`, `AdminProducts`, `AdminOrders`, `AdminOrderDetails`
- [x] Валидация TWA в `/api/v1/auth/telegram/validate` → выдача токена/идентификатора
- [x] Улучшения: серверная пагинация/поиск в админ‑GET, унификация ошибок API, уведомления об ошибках на фронте, индикаторы занятости и подтверждения действий
- [ ] Улучшения: подтверждения опасных действий, фильтры по категориям/датам

## Фаза 6: Финализация и Демонстрация
- [ ] UI/UX полировка (адаптив, лоадеры, пустые состояния, i18n в админке)
- [x] Безопасность: rate‑limit для `/api/v1/admin/*`
- [x] Унификация ошибок API (единый JSON формат)
- [ ] Защита от повторов
- [ ] Документация: demo‑скрипт, README, диаграмма архитектуры
- [ ] Тесты: unit+api (>70% покрытие), E2E (Playwright/Cypress)
- [x] CI/CD: GitHub Actions — backend pytest, frontend lint+build
- [ ] Об observability: структурные логи, базовые метрики

## Ближайший бэклог
- [x] E2E нотификация заказа
- [x] E2E checkout тест (ошибочные кейсы)
- [ ] Админ‑UI: подтверждения/улучшенный UX, индикаторы прогресса
- [x] Обновление README (пагинация, формат ошибок, админ‑заголовки, примеры curl)
- [x] Фильтры: товары по категории; заказы по статусу и дате (серверные параметры)

## Дальше (опционально): Платежи
- [ ] Интеграция платёжного провайдера + вебхуки
- [ ] Идемпотентность и статусы заказов (pending/paid/cancelled)
- [ ] Страницы/уведомления по оплате


