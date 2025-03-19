FROM python:3.11-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы тестов и конфигурации
COPY common /app/common
COPY tests /app/tests
COPY entrypoint.sh /app/entrypoint.sh

# Делаем entrypoint.sh исполняемым
RUN chmod +x entrypoint.sh

# Создаем директорию для отчетов
RUN mkdir -p /app/reports

# Точка входа - наш скрипт запуска тестов
ENTRYPOINT ["/app/entrypoint.sh"] 