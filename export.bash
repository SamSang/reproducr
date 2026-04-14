#!/usr/bin/env bash
set -e

# Load .env
if [ ! -f .secret ]; then
  echo ".secret file not found"
  exit 1
fi

source .secret

# Dump database to a static file
pg_dump \
  --host="$PGHOST" \
  --port="${PGPORT:-5432}" \
  --username="$PGUSER" \
  --dbname="$DB_NAME" \
  --format=custom \
  --no-owner \
  --no-privileges \
  --exclude-schema=pg_catalog \
  --exclude-schema=information_schema \
  --exclude-schema=rdsadmin \
  --file="daan822_g4.dump"