#!/bin/sh

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

cp -r /app/collected_static/. /backend_static/

gunicorn --bind 0.0.0.0:8000 backend.wsgi

GUNICORN_PID=$!

# Запуск бота в фоновом режиме
python manage.py runbot &
# Сохранение PID процесса бота
BOT_PID=$!

# Функция для корректного завершения процессов при получении сигнала
terminate_processes() {
    kill -TERM $GUNICORN_PID
    kill -TERM $BOT_PID
}

# Установка обработчика сигналов для завершения работы
trap terminate_processes SIGTERM SIGINT

# Ожидание завершения любого из процессов
wait -n