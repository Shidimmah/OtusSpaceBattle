FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY battle_mechanics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса и общие модули
COPY battle_mechanics/main.py .
COPY common /app/common

# Открываем порт
EXPOSE 8000

# Запускаем FastAPI с Uvicorn
CMD ["python", "main.py"] 