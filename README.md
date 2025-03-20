# Space Battle

Проект игры для курса OTUS

## Развертывание

Проект настроен на автоматическое развертывание при помощи GitHub Actions. При push в ветку main происходит:

1. Обновление кода на сервере
2. Перезапуск Docker контейнеров
3. Проверка статуса сервисов

## Сервисы

- API Gateway
- Auth Service (авторизация и аутентификация)
- Battle Mechanics (механики боя)
- Resource Management (управление ресурсами)
- Analytics (аналитика)
- Ranking (рейтинги)
- Game Session Service (управление игровыми сессиями)
- Matchmaking Service (подбор соперников)
- Fleet Management Service (управление флотами)
- Database Service (управление базой данных)
- Prometheus (мониторинг)
- Grafana (визуализация метрик)
- ELK  (логирование)
