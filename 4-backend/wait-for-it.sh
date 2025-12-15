#!/bin/sh
set -e

host="$1"
port="$2"

shift 2
if [ "$1" = '--' ]; then
  shift
fi

echo "Esperando a PostgreSQL en $host:$port..."

until PGPASSWORD=$DB_PASSWORD psql -h "$host" -p "$port" -U "$DB_USER" -c '\q' >/dev/null 2>&1; do
  >&2 echo "Postgres no está listo — esperando…"
  sleep 1
done

>&2 echo "Postgres disponible — ejecutando comando"
exec "$@"