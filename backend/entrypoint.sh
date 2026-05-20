#!/bin/sh
set -e

export FLASK_APP=wsgi.py

if [ ! -d migrations/versions ]; then
  flask db init 2>/dev/null || true
  flask db migrate -m "initial" 2>/dev/null || true
fi
flask db upgrade
python seed.py

exec "$@"
