# Stage 1: Тестирование
FROM python:3.11-slim as testing

WORKDIR /app

# Устанавливаем зависимости для сборки и тестирования
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt requirements-dev.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements-dev.txt

# Копируем исходный код и тесты
COPY otus_space_battle/ ./otus_space_battle/
COPY tests/ ./tests/

# Запускаем тесты
RUN pytest tests/ -v --cov=otus_space_battle

# Stage 2: Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем только необходимые зависимости для продакшена
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем только исходный код без тестов
COPY otus_space_battle/ ./otus_space_battle/

# Настраиваем переменные окружения
ENV PYTHONPATH=/app
ENV PROMETHEUS_MULTIPROC_DIR=/tmp

# Создаем пользователя без прав root
RUN useradd -m appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app && \
    mkdir -p /tmp && \
    chown -R appuser:appuser /tmp

USER appuser

# Команда запуска приложения
CMD ["python", "-m", "otus_space_battle"] 