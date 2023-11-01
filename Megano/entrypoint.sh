#!/bin/sh

python manage.py migrate
python manage.py loaddata catalog_dump
gunicorn Megano.wsgi:application --bind 0.0.0.0:8000

exec "$@"
