#!/bin/sh

set -e

db="$1"
db_new="$2"

timestamp=$(date +%F_%T)

# Export a fixture for users.
python manage.py dumpdata auth --indent 4 > auth_${timestamp}.json
python manage.py dumpdata core --indent 4 > core_${timestamp}.json

# Backup.
mv "$db" "${db}.bak_${timestamp}"

# Swap.
cp "$db_new" "$db"

# Load user data.
python manage.py loaddata auth_${timestamp}.json
python manage.py loaddata core_${timestamp}.json

# Anonymize.
./anonymize_sqlite.py "$db" --targets cohort_code sample_id samples sample --log-level WARNING

