# Используем базовый образ Python
FROM python:3.10

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код сервиса
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем сервис
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
