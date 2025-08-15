# ~/nexus-gear-store/Dockerfile - КАНОНИЧЕСКАЯ ВЕРСИЯ (с поддержкой сборки фронтенда)

# ---------- Стадия 1: сборка фронтенда ----------
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
# Копируем и устанавливаем зависимости отдельно для лучшего кеширования
COPY vue-project/package*.json ./
RUN npm ci --no-audit --no-fund
# Копируем исходники фронтенда и собираем
COPY vue-project/ ./
# Некоторые окружения создают .bin без исп. бита. Чиним и запускаем билдер напрямую через node
RUN chmod +x node_modules/.bin/* || true && \
    node node_modules/vite/bin/vite.js build

# ---------- Стадия 2: Python бекенд/бот ----------
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем только файлы зависимостей Poetry
COPY poetry.lock pyproject.toml ./

# Устанавливаем Poetry и зависимости проекта
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main

# Копируем весь остальной код приложения
COPY . .

# Копируем собранный фронтенд в статическую директорию, откуда его раздает aiohttp
COPY --from=frontend-builder /frontend/dist /app/src/presentation/web/static

# Команда запуска контейнера
CMD ["python", "-m", "src.presentation.bot"]