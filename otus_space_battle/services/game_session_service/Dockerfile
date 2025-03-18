FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY game_session_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса и общие модули
COPY game_session_service/src/ .
COPY common /app/common

# Открываем порт
EXPOSE 8000

# Запускаем FastAPI с Uvicorn
CMD ["python", "app.py"] 