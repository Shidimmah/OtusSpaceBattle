# Space Battle

Многопользовательская космическая игра

## Развертывание

Проект настроен на автоматическое развертывание при помощи GitHub Actions. При push в ветку main происходит:

1. Обновление кода на сервере
2. Перезапуск Docker контейнеров
3. Проверка статуса сервисов

## Сервисы

- API Gateway
- Battle Mechanics
- Resource Management
- Analytics
- Ranking
- Prometheus (мониторинг) 