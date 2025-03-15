# Используем Python 3.10
FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary

# Запуск скрипта инициализации БД
CMD ["python", "init_db.py"]
