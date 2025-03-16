# Используем базовый образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем код сервиса
COPY . .

# Открываем порт
EXPOSE 80

# Запускаем FastAPI с Uvicorn
CMD ["python", "otus_space_battle/services/api_gateway/main.py"]
