FROM python:3.11-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем общие модули
COPY ../../common /app/common

# Копируем код приложения
COPY . /app/

# Открываем порт для FastAPI
EXPOSE 8004

# Запускаем приложение
CMD ["python", "-m", "src.app"] 