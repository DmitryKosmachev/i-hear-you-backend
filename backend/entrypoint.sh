#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput

cp -r /app/collected_static/. /backend_static/

python manage.py runbot &

exec gunicorn --bind 0.0.0.0:8000 backend.wsgi
