#!/bin/bash

# Обновление системы
apt-get update
apt-get upgrade -y

# Установка необходимых пакетов
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    ufw

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Настройка UFW (файрвол)
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 3000  # Grafana
ufw allow 5601  # Kibana
echo "y" | ufw enable

# Создание директории проекта
mkdir -p /opt/space-battle
cd /opt/space-battle

# Создание docker-compose override для продакшен настроек
cat > docker-compose.override.yml << EOL
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d
      - ./nginx/ssl:/etc/nginx/ssl
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - api_gateway
      - grafana
      - kibana

  prometheus:
    restart: always
    volumes:
      - /opt/space-battle/monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus

  grafana:
    restart: always
    environment:
      - GF_SERVER_ROOT_URL=https://grafana.vds2729307.my-ihor.ru
      - GF_SECURITY_ADMIN_PASSWORD=Admin1010

  elasticsearch:
    restart: always
    environment:
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    restart: always

  db:
    restart: always
    environment:
      - POSTGRES_PASSWORD=Admin1010
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  prometheus_data:
    driver: local
  elasticsearch_data:
    driver: local
  postgres_data:
    driver: local
EOL

# Создание .env файла
cat > .env << EOL
GRAFANA_ADMIN_PASSWORD=Admin1010
DB_PASSWORD=Admin1010
EOL

# Создание директорий для Nginx
mkdir -p nginx/conf.d nginx/ssl

# Настройка Nginx
cat > nginx/conf.d/default.conf << EOL
server {
    listen 80;
    server_name vds2729307.my-ihor.ru;

    location / {
        proxy_pass http://api_gateway:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /grafana/ {
        proxy_pass http://grafana:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /kibana/ {
        proxy_pass http://kibana:5601/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}

# Grafana subdomain
server {
    listen 80;
    server_name grafana.vds2729307.my-ihor.ru;

    location / {
        proxy_pass http://grafana:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}

# Kibana subdomain
server {
    listen 80;
    server_name kibana.vds2729307.my-ihor.ru;

    location / {
        proxy_pass http://kibana:5601;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOL

echo "VPS setup completed! Please run setup_ssl.sh next." 