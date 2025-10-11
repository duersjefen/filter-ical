#!/bin/bash
# Setup backup cron job on EC2 via SSM
# Run: ./scripts/setup-backups.sh

set -e

# Load EC2 instance ID
if [ ! -f .env.ec2 ]; then
    echo "Error: .env.ec2 not found"
    exit 1
fi

source .env.ec2

echo "📦 Setting up database backups on EC2..."

# Copy backup script to EC2 and setup cron
aws ssm send-command \
    --instance-ids "$INSTANCE_ID" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "# Create backup directory",
        "sudo mkdir -p /var/backups/filter-ical",
        "sudo chown ubuntu:ubuntu /var/backups/filter-ical",
        "",
        "# Create backup script",
        "cat > /home/ubuntu/backup-database.sh <<\"BACKUP_SCRIPT\"",
        "#!/bin/bash",
        "set -e",
        "BACKUP_DIR=\"/var/backups/filter-ical\"",
        "DATE=\\$(date +%Y%m%d-%H%M%S)",
        "",
        "# Backup staging",
        "docker exec filter-ical-postgres-staging pg_dump -U platform_admin filterical_staging | gzip > \"\\$BACKUP_DIR/staging-\\$DATE.sql.gz\"",
        "",
        "# Backup production",
        "docker exec filter-ical-postgres-production pg_dump -U platform_admin filterical_production | gzip > \"\\$BACKUP_DIR/production-\\$DATE.sql.gz\"",
        "",
        "# Keep only last 7 days",
        "find \"\\$BACKUP_DIR\" -name \"*.sql.gz\" -mtime +7 -delete",
        "",
        "echo \"Backup completed: \\$DATE\"",
        "BACKUP_SCRIPT",
        "",
        "# Make executable",
        "chmod +x /home/ubuntu/backup-database.sh",
        "",
        "# Add to crontab if not already there",
        "(crontab -l 2>/dev/null | grep -v backup-database.sh; echo \"0 2 * * * /home/ubuntu/backup-database.sh >> /var/log/backup.log 2>&1\") | crontab -",
        "",
        "echo \"Backup cron job installed: daily at 2 AM UTC\""
    ]' \
    --region eu-north-1

echo "✅ Backup system configured!"
echo ""
echo "Backups will run daily at 2 AM UTC"
echo "View logs: tail -f /var/log/backup.log"
echo "List backups: ls -lh /var/backups/filter-ical/"
