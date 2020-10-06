#!/usr/bin/env bash
#!/bin/sh

apt-get update && apt-get install -y netcat

echo "Waiting for postgres..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL started"

poetry run aerich init -t core.settings.TORTOISE_CONFIG
poetry run aerich init-db
poetry run aerich upgrade
poetry run uvicorn --host 0.0.0.0 --port 8000 main:app --reload

exec "$@"