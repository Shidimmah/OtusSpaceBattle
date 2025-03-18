#!/bin/bash

# Функция для проверки доступности сервиса
check_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$port/health" > /dev/null; then
            echo "$service is ready!"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts: $service is not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "Error: $service failed to start"
    return 1
}

# Проверяем каждый сервис
services=(
    "api_gateway:8000"
    "auth_service:8001"
    "resource_management:8002"
    "battle_mechanics:8003"
    "analytics:8004"
    "game_session:8005"
    "matchmaking:8006"
    "fleet_management:8007"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if ! check_service "$name" "$port"; then
        echo "Failed to start services"
        exit 1
    fi
done

echo "All services are ready!" 