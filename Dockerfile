# ============ STAGE 1: Dependencies ============
FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS builder

# Установка системных зависимостей для сборки
RUN apt-get update && apt-get install -y \
    gcc g++ git build-essential \
    libxml2-dev libxslt1-dev zlib1g-dev \
    libjpeg-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование файлов конфигурации
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen --no-dev --no-editable

# ============ STAGE 2: Runtime ============
FROM python:3.13-slim-bookworm

# Runtime зависимости
RUN apt-get update && apt-get install -y \
    git \
    libxml2 libxslt1.1 \
    libjpeg62-turbo libpng16-16 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копирование Python окружения
COPY --from=builder /app/.venv /app/.venv

# Настройка PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app
USER app

# Рабочая директория
WORKDIR /home/app

# Копирование исходного кода
COPY --chown=app:app src/ ./src/
COPY --chown=app:app main.py pyproject.toml ./
COPY --chown=app:app data/ ./data/

# Создание необходимых директорий
RUN mkdir -p data/articles data/templates

EXPOSE 8000
CMD ["python", "main.py"]