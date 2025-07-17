# --- Этап 1: Builder ---
# Используем образ Python для сборки зависимостей
FROM python:3.11-slim as builder

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# --- ИСПРАВЛЕНИЕ ---
# Приказываем Poetry создавать .venv в директории проекта
RUN poetry config virtualenvs.in-project true

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем только production-зависимости в виртуальное окружение
# Теперь .venv будет создан здесь, в /app/.venv
RUN poetry install --no-root --without dev


# --- Этап 2: Production ---
# Используем тот же базовый образ для консистентности
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем виртуальное окружение, созданное на этапе builder
# Теперь эта команда сработает, так как /app/.venv существует
COPY --from=builder /app/.venv ./.venv

# Копируем исходный код нашего приложения
COPY src/ ./src

# Добавляем venv в PATH, чтобы можно было запускать команды напрямую
ENV PATH="/app/.venv/bin:$PATH"

# Команда для запуска приложения
CMD ["python", "-m", "src.bot"]