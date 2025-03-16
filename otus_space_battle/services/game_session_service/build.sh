#!/bin/bash

# Переходим в корневую директорию проекта
cd ../../

# Собираем образ с указанием контекста сборки
docker build -t game_session_service -f services/game_session_service/Dockerfile . 