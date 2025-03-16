# Используем Python 3.11-slim
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../common /app/common

# Запуск скрипта инициализации БД
CMD ["python", "init_db.py"]
