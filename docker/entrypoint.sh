#!/bin/sh
set -e

echo "Очікування PostgreSQL…"
until python -c "
import os
import psycopg2
psycopg2.connect(
    dbname=os.environ.get('POSTGRES_DB', 'coursework_db'),
    user=os.environ.get('POSTGRES_USER', 'coursework'),
    password=os.environ.get('POSTGRES_PASSWORD', ''),
    host=os.environ.get('DB_HOST', 'db'),
    port=os.environ.get('DB_PORT', '5432'),
)
" 2>/dev/null; do
  sleep 1
done
echo "База доступна."

python manage.py migrate --noinput
python manage.py ensure_admin
python manage.py seed_auditories

exec "$@"
