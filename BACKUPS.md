# Database Backups (KISS)

## How It Works
- Backups run daily at 2 AM (UTC) via cron
- Stored locally on EC2 in `/var/backups/filter-ical/`
- Keep last 7 days, auto-delete older backups
- No cloud costs, simple and reliable

## Setup on EC2
```bash
# Copy backup script to EC2 (via SSM)
scp scripts/backup-database.sh ec2:/home/ubuntu/

# Make executable
chmod +x /home/ubuntu/backup-database.sh

# Add to cron
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup-database.sh >> /var/log/backup.log 2>&1
```

## Restore from Backup
```bash
# List available backups
ls -lh /var/backups/filter-ical/

# Restore production database
./scripts/restore-database.sh /var/backups/filter-ical/production-20251011-020000.sql.gz production

# Restore staging database
./scripts/restore-database.sh /var/backups/filter-ical/staging-20251011-020000.sql.gz staging
```

## Why Local Backups?
For small projects:
- ✅ Simple - no AWS S3 complexity
- ✅ Free - no cloud storage costs
- ✅ Fast - restore in seconds
- ✅ Good enough - 7-day retention protects against mistakes
