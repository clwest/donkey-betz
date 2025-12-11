#!/bin/bash
# Daily database backup script
# Run via cron: 0 2 * * * /path/to/daily_backup.sh

BACKUP_DIR="/Users/donkeyking/development/unified-donkey-betz/backups/database"
DB_NAME="unified_donkey_betz"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.dump"

# Create backup
pg_dump -U postgres -Fc "$DB_NAME" > "$BACKUP_FILE"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.dump" -mtime +7 -delete

echo "Backup created: $BACKUP_FILE"
echo "Size: $(du -h "$BACKUP_FILE" | cut -f1)"
