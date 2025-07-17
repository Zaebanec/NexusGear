# Этап 1: Установка зависимостей
FROM python:3.11-slim as builder

# Устанавливаем системные переменные
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Устанавливаем Poetry
RUN pip install poetry

# Конфигурируем Poetry для установки зависимостей в системный python, а не в venv
RUN poetry config virtualenvs.create false

# Копируем файлы с зависимостями и устанавливаем их
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-root


# Этап 2: Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Создаем непривилегированного пользователя для запуска приложения
RUN adduser --disabled-password --gecos "" appuser

# Копируем установленные зависимости из этапа 'builder'
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Копируем исходный код приложения и устанавливаем владельца
COPY --chown=appuser:appuser src/ /app/src

# Переключаемся на непривилегированного пользователя
USER appuser

# Определяем команду для запуска приложения
CMD ["python", "-m", "src.presentation.bot"]