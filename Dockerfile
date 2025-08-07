# ~/nexus-gear-store/Dockerfile - КАНОНИЧЕСКАЯ ВЕРСИЯ

# Шаг 1: Используем официальный образ Python
FROM python:3.11-slim

# Шаг 2: Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Шаг 3: Копируем только файлы зависимостей
# Это оптимизирует кеширование Docker. Этот слой не будет пересобираться,
# если вы меняете только код, а не зависимости.
COPY poetry.lock pyproject.toml ./

# Шаг 4: Устанавливаем Poetry и зависимости проекта
# --no-root говорит poetry не создавать venv, а ставить в системный python
# --only main говорит ставить только основные зависимости, без dev (black, pytest)
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main

# Шаг 5: Копируем весь остальной код нашего приложения
COPY . .

# Шаг 6: Указываем команду, которая будет запускаться при старте контейнера
# Это чистый запуск, без всяких оболочек sh -c
CMD ["python", "-m", "src.presentation.bot"]