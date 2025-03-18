# Используем базовый образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса
COPY main.py .
COPY common /app/common

# Открываем порт
EXPOSE 8000

# Запускаем FastAPI с Uvicorn
CMD ["python", "main.py"]
