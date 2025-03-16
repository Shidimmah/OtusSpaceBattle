# common/Dockerfile
FROM python:3.10

WORKDIR /app

# Копируем common
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary