FROM python:3.12-slim

WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса
COPY src/ .

# Копируем общие модули
COPY ../../common /app/common

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["python", "app.py"]
