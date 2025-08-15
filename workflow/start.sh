#!/bin/sh
# Wait for Postgres
echo "Waiting for database..."
until nc -z db 5432; do
  sleep 1
done
echo "Database is up!"

echo "Waiting for MCP DB Server..."
until nc -z mcp-db 4000; do
  sleep 1
done
echo "MCP Server is up!"

echo "Waiting for MCP Gemini Server..."
until nc -z mcp-gemini 4001; do
  sleep 1
done
echo "MCP Server is up!"

# Start FastAPI
exec uvicorn workflow.api.main:app --host 0.0.0.0 --port 8080
