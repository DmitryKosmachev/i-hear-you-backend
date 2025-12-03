#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput

python manage.py runstatbot &
python manage.py runbot &

exec gunicorn --bind 0.0.0.0:8000 backend.wsgi --access-logfile="-" --error-logfile="-"
