#!/bin/bash

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 не установлен. Пожалуйста, установите Python 3"
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "pip3 не установлен. Пожалуйста, установите pip3"
    exit 1
fi

# Создаем и активируем виртуальное окружение
echo "Создаем виртуальное окружение..."
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
echo "Устанавливаем зависимости..."
pip install -e .

# Проверяем переменные окружения
if [ ! -f .env ]; then
    echo "Создаем файл .env..."
    echo "DATABASE_URL=postgresql://user:password@localhost:5432/main_db" > .env
fi

# Применяем миграции
echo "Применяем миграции..."
python services/database_service/init_db.py

echo "Установка завершена успешно!" 