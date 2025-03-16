#!/bin/bash

# Обновляем код из репозитория
git pull

# Перезапускаем сервисы
docker-compose down
docker-compose up -d

# Проверяем статус
docker-compose ps 