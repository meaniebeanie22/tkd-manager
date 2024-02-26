#!/bin/sh

echo "Collecting static files.."
python manage.py collectstatic --noinput

if [ "$RUN_MIGRATIONS" = "True" ]; then
    echo "Running migrations..."
    until python manage.py migrate
    do
        echo "Waiting for db to be ready..."
        sleep 2
    done
fi

echo "Starting app server..."
python -m gunicorn tkdmanager.wsgi \
    --log-level info

    