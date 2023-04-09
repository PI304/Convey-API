#!/bin/bash

# Prepare log files and start outputting logs to stdout
mkdir -p logs
cd logs
touch gunicorn.log
touch gunicorn-access.log
tail -n 0 -f gunicorn*.log &

export DJANGO_SETTINGS_MODULE=config.settings.deploy

python3 manage.py migrate || exit 1
exec gunicorn config.wsgi.deploy:application \
    --name convey \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/gunicorn-access.log \
"$@"