FROM nginx:latest

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y \
    nginx-extras \
    && rm -rf /var/lib/apt/lists/*

# Копируем конфигурацию
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf 