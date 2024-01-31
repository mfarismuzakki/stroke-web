#!/bin/bash

set -e

# Django
gunicorn --config gunicorn-cfg.py core.wsgi &

# Celery Worker
python manage.py run_huey