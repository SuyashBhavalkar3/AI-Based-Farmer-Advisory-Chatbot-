#!/bin/bash
# Entrypoint script for production deployment

set -e

echo "Starting Farmer Advisory Chatbot API..."

# Wait for database to be ready
if [ "$DATABASE_URL" != "" ]; then
  echo "Waiting for database..."
  while ! python -c "from sqlalchemy import create_engine; create_engine('$DATABASE_URL').connect()" 2>/dev/null; do
    sleep 1
  done
  echo "Database is ready!"
fi

# Run migrations (if using Alembic)
# alembic upgrade head

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
