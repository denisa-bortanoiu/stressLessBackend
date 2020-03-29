#!/bin/sh
set -e

flask db upgrade
exec gunicorn app:app -w 1 --bind 0.0.0.0:5000 --timeout 60 --reload --log-file '-'
