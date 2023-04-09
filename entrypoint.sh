#!/bin/bash

# Prepare log files and start outputting logs to stdout
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log
tail -n 0 -f ./logs/gunicorn*.log &

export DJANGO_SETTINGS_MODULE=config.settings.deploy

exec gunicorn config.wsgi.deploy:application \
    --name convey \
    --bind 0.0.0.0:8080 \
    --workers 1 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/gunicorn-access.log \
"$@"