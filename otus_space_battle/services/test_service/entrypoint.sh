#!/bin/bash
set -e

# Ожидаем запуска других сервисов
echo "Ожидаем запуска других сервисов..."
sleep 10

# Запускаем тесты с покрытием
echo "Запускаем тесты..."
pytest --cov=. --cov-report=xml:/app/reports/coverage.xml --cov-report=term-missing --cov-fail-under=95 tests/

# Сохраняем статус выполнения тестов
TEST_EXIT_CODE=$?

echo "Тесты завершены с кодом: $TEST_EXIT_CODE"
echo "Отчет о покрытии сохранен в /app/reports/coverage.xml"

# Если тесты не прошли, можно решить, нужно ли остановить контейнер или продолжить
if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "ВНИМАНИЕ: Некоторые тесты не прошли!"
    # Здесь можно добавить логику остановки контейнера, если нужно
    # exit $TEST_EXIT_CODE
fi

# Переходим в режим ожидания для возможности повторного запуска тестов
echo "Переходим в режим ожидания. Для повторного запуска тестов выполните:"
echo "docker exec -it test_service pytest --cov=. tests/"
echo "Для остановки нажмите Ctrl+C"

# Бесконечный цикл ожидания
tail -f /dev/null 