FROM nginx:latest

# Копируем конфигурацию
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

# Создаем директорию для модулей если её нет
RUN mkdir -p /etc/nginx/modules-enabled/

# Включаем модуль sub_filter (он уже включен в базовом образе nginx)
RUN echo "load_module modules/ngx_http_sub_module.so;" > /etc/nginx/modules-enabled/50-mod-http-sub-filter.conf 