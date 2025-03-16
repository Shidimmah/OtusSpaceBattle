#!/bin/bash

# Ждем, пока Elasticsearch запустится
until curl -s http://elasticsearch:9200 > /dev/null; do
    echo 'Waiting for Elasticsearch...'
    sleep 3
done

# Создаем политику жизненного цикла для логов
curl -X PUT "http://elasticsearch:9200/_ilm/policy/logs_policy" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "7d",
            "max_size": "7gb"
          }
        }
      },
      "delete": {
        "min_age": "7d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}'

# Создаем шаблон для индексов логов
curl -X PUT "http://elasticsearch:9200/_template/logs_template" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["logstash-*"],
  "settings": {
    "index.lifecycle.name": "logs_policy",
    "index.lifecycle.rollover_alias": "logs"
  }
}'

echo "Elasticsearch ILM policy and template configured successfully" 