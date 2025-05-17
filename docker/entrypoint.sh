#!/bin/bash

# Exécuter les migrations
echo "Running migrations..."
alembic upgrade head

# Lancer l'application avec Gunicorn
echo "Starting application with Gunicorn..."
exec gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4 main:app
