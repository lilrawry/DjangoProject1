#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if needed..."
python create_superuser.py

echo "Initializing database with sample rooms if needed..."
python initialize_db.py

echo "Updating room images if needed..."
python update_room_images.py

echo "Starting Gunicorn server..."
exec gunicorn DjangoProject1.wsgi:application --bind 0.0.0.0:$PORT
