# Otus Space Battle

## Установка и настройка

### Предварительные требования
- Python 3.8 или выше
- Docker и Docker Compose
- pip (Python package installer)

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd otus_space_battle
```

2. Запустите PostgreSQL через Docker:
```bash
docker-compose up -d
```

3. Запустите скрипт установки:
```bash
chmod +x setup.sh
./setup.sh
```

Скрипт выполнит следующие действия:
- Создаст виртуальное окружение
- Установит все зависимости
- Создаст файл .env с настройками
- Применит миграции базы данных

### Запуск сервисов

Каждый сервис можно запустить отдельно:

```bash
# Активируйте виртуальное окружение, если оно не активировано
source venv/bin/activate

# Запуск сервисов (каждый в отдельном терминале)
uvicorn services.battle_mechanics_service.app:app --reload --port 8001
uvicorn services.resource_management_service.app:app --reload --port 8002
uvicorn services.ranking_service.app:app --reload --port 8003
uvicorn services.analytics_service.app:app --reload --port 8004
```

## Структура проекта

- `services/` - микросервисы проекта
  - `battle_mechanics_service/` - сервис игровой механики
  - `resource_management_service/` - сервис управления ресурсами
  - `ranking_service/` - сервис рейтинга игроков
  - `analytics_service/` - сервис аналитики
  - `database_service/` - сервис управления базой данных
- `common/` - общие компоненты
- `migrations/` - файлы миграций базы данных