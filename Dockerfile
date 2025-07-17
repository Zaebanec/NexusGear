# --- Этап 1: Builder ---
# Используем образ Python для сборки зависимостей
FROM python:3.11-slim as builder

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем только production-зависимости в виртуальное окружение
# --no-root: не устанавливать сам проект
# --no-dev: не устанавливать dev-зависимости
# Это создает .venv/ внутри /app
RUN poetry install --no-root --no-dev


# --- Этап 2: Production ---
# Используем тот же базовый образ для консистентности
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем виртуальное окружение, созданное на этапе builder
COPY --from=builder /app/.venv ./.venv

# Копируем исходный код нашего приложения
COPY src/ ./src

# Добавляем venv в PATH, чтобы можно было запускать команды напрямую
ENV PATH="/app/.venv/bin:$PATH"

# Команда для запуска приложения (пока что плейсхолдер)
# Мы создадим src/main.py на следующих шаках
CMD ["python", "-m", "src.main"]