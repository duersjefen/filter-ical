#!/bin/bash
# Simple local database backup script
# Run daily via cron on EC2 instance

set -e

BACKUP_DIR="/var/backups/filter-ical"
DATE=$(date +%Y%m%d-%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup staging database
docker exec filter-ical-postgres-staging pg_dump -U platform_admin filterical_staging | gzip > "$BACKUP_DIR/staging-$DATE.sql.gz"

# Backup production database
docker exec filter-ical-postgres-production pg_dump -U platform_admin filterical_production | gzip > "$BACKUP_DIR/production-$DATE.sql.gz"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
