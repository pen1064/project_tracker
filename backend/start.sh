#!/bin/sh
# Wait for Postgres
echo "Waiting for database..."
until nc -z db 5432; do
  sleep 1
done
echo "Database is up!"

# Start FastAPI
exec uvicorn backend.database_api.main:app --host 0.0.0.0 --port 8000
