#!/bin/bash
# Restore database from backup

if [ -z "$1" ]; then
    echo "Usage: ./restore-database.sh <backup-file>"
    echo "Example: ./restore-database.sh /var/backups/filter-ical/production-20251011-020000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"
ENVIRONMENT="${2:-production}"  # Default to production

echo "⚠️  WARNING: This will OVERWRITE the $ENVIRONMENT database!"
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

# Drop and recreate database
docker exec filter-ical-postgres-$ENVIRONMENT psql -U platform_admin -c "DROP DATABASE IF EXISTS filterical_$ENVIRONMENT;"
docker exec filter-ical-postgres-$ENVIRONMENT psql -U platform_admin -c "CREATE DATABASE filterical_$ENVIRONMENT;"

# Restore from backup
gunzip -c "$BACKUP_FILE" | docker exec -i filter-ical-postgres-$ENVIRONMENT psql -U platform_admin filterical_$ENVIRONMENT

echo "✅ Restore completed from $BACKUP_FILE"
