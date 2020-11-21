#!/usr/bin/env bash
#!/bin/sh

apt-get update && apt-get install -y netcat

echo "Waiting for postgres..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL started"

poetry run alembic upgrade head
poetry run gunicorn main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers=4 --log-level=info

exec "$@"
