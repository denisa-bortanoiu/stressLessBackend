#!/bin/sh
set -e

#sleep 20
flask db upgrade
exec gunicorn app:app -w 1 --bind 0.0.0.0:5000 --timeout 600 --reload --log-file '-'
