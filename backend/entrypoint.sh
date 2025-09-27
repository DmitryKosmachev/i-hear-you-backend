#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput

cp -r /app/collected_static/. /backend_static/

exec gunicorn --bind 0.0.0.0:8000 backend.wsgi