#!/bin/bash
set -e

# Ожидаем запуска других сервисов
echo "Ожидаем запуска других сервисов..."
sleep 10

# Запускаем тесты с покрытием
echo "Запускаем тесты..."
python -m pytest --cov=. --cov-report=xml:/app/reports/coverage.xml --cov-report=term-missing --cov-report=html:/app/reports/html_coverage --cov-fail-under=95 \
  tests/unit/test_auth_service.py \
  tests/unit/test_battle_mechanics.py \
  tests/unit/test_resource_management.py \
  tests/unit/test_analytics.py \
  tests/unit/test_ranking.py \
  tests/unit/test_matchmaking.py \
  tests/integration/

# Сохраняем статус выполнения тестов
TEST_EXIT_CODE=$?

echo "Тесты завершены с кодом: $TEST_EXIT_CODE"
echo "Отчет о покрытии сохранен в /app/reports/coverage.xml"
echo "HTML отчет доступен в /app/reports/html_coverage"

# Если тесты не прошли, можно решить, нужно ли остановить контейнер или продолжить
if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "ВНИМАНИЕ: Некоторые тесты не прошли!"
    # Здесь можно добавить логику остановки контейнера, если нужно
    # exit $TEST_EXIT_CODE
fi

# Генерируем отчет для CI/CD
echo "Генерируем сводку для CI/CD..."
echo "TOTAL Coverage: " > /app/reports/coverage_summary.txt
cat /app/reports/coverage.xml | grep -o 'line-rate="[0-9.]*"' | head -1 | cut -d'"' -f2 | awk '{printf "%.1f%%\n", $1*100}' >> /app/reports/coverage_summary.txt

# Переходим в режим ожидания для возможности повторного запуска тестов
echo "Переходим в режим ожидания. Для повторного запуска тестов выполните:"
echo "docker exec -it test_service pytest --cov=. tests/"
echo "Для остановки нажмите Ctrl+C"

# Бесконечный цикл ожидания
tail -f /dev/null 