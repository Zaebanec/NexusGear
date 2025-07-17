# Этап 1: Установка зависимостей
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev --no-root


# Этап 2: Финальный образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Явно указываем Python, где искать наши модули.
# Это самый надежный способ.
ENV PYTHONPATH /app

# Создаем пользователя
RUN adduser --disabled-password --gecos "" appuser

# Копируем зависимости и исходный код
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=appuser:appuser src/ /app/src

# Переключаемся на пользователя
USER appuser

# Запускаем модуль. Python будет искать /app/src/presentation/bot.py
CMD ["python", "-m", "src.presentation.bot"]