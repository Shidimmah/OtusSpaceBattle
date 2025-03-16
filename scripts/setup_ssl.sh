#!/bin/bash

# Установка certbot
apt-get install -y certbot

# Остановка Nginx контейнера для освобождения 80 порта
docker-compose stop nginx

# Получение SSL сертификата
certbot certonly --standalone \
    --non-interactive \
    --agree-tos \
    --email ilya.hibiraim@gmail.com \
    -d vds2729307.my-ihor.ru \
    -d grafana.vds2729307.my-ihor.ru \
    -d kibana.vds2729307.my-ihor.ru

# Обновление конфигурации Nginx для использования SSL
cat > nginx/conf.d/default.conf << EOL
server {
    listen 80;
    server_name vds2729307.my-ihor.ru grafana.vds2729307.my-ihor.ru kibana.vds2729307.my-ihor.ru;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name vds2729307.my-ihor.ru;

    ssl_certificate /etc/letsencrypt/live/vds2729307.my-ihor.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vds2729307.my-ihor.ru/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://api_gateway:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /grafana/ {
        proxy_pass http://grafana:3000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /kibana/ {
        proxy_pass http://kibana:5601/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 443 ssl;
    server_name grafana.vds2729307.my-ihor.ru;

    ssl_certificate /etc/letsencrypt/live/vds2729307.my-ihor.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vds2729307.my-ihor.ru/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://grafana:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 443 ssl;
    server_name kibana.vds2729307.my-ihor.ru;

    ssl_certificate /etc/letsencrypt/live/vds2729307.my-ihor.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/vds2729307.my-ihor.ru/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://kibana:5601;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Настройка автоматического обновления сертификатов
echo "0 0,12 * * * root python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew -q && docker-compose restart nginx" | sudo tee -a /etc/crontab > /dev/null

# Запуск Nginx
docker-compose up -d nginx

echo "SSL setup completed!" 