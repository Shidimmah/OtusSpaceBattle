#!/bin/bash
set -e

# Запуск PostgreSQL в фоне
docker-entrypoint.sh postgres &

# Ждём, пока БД поднимется
until pg_isready -U user -d main_db; do
  echo "Waiting for database to start..."
  sleep 2
done

# Выполняем init.sql, если таблиц ещё нет
if [ "$(psql -U user -d main_db -tAc "SELECT count(*) FROM pg_tables WHERE schemaname = 'public';")" -eq 0 ]; then
  echo "Executing init.sql..."
  psql -U user -d main_db -f /docker-entrypoint-initdb.d/init.sql
fi

# Ожидаем завершения процесса PostgreSQL
wait
