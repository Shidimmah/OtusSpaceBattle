FROM python:3.9-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы тестов и конфигурации
COPY . .

# Делаем entrypoint.sh исполняемым
RUN chmod +x entrypoint.sh

# Создаем директорию для отчетов
RUN mkdir -p /app/reports

# Точка входа - наш скрипт запуска тестов
ENTRYPOINT ["/app/entrypoint.sh"] 