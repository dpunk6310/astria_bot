#!/bin/sh
python manage.py makemigrations
python manage.py migrate

gunicorn config.wsgi -b 0.0.0.0:8080 -w 10 --threads 4
