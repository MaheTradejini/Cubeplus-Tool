#!/bin/bash
echo "Starting CubePlus Trading App..."
echo "PORT: $PORT"
echo "DATABASE_URL: ${DATABASE_URL:0:30}..."

# Start the application
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --access-logfile - --error-logfile - wsgi:application