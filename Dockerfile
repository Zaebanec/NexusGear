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
WORKDIR /app
RUN adduser --disabled-password --gecos "" appuser
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# --- НАЧАЛО ИСПРАВЛЕНИЯ ---
# Явно добавляем путь, куда poetry/pip скорее всего кладет исполняемые файлы
# для непривилегированного пользователя.
ENV PATH="/root/.local/bin:${PATH}"
# --- КОНЕЦ ИСПРАВЛЕНИЯ ---

COPY --chown=appuser:appuser src/ /app/src
USER appuser
CMD ["python", "-m", "src.presentation.bot"]