#!/bin/bash
# Database Backup Script
# Created: Nov 30, 2025 (Session 294 - After Data Loss Incident)
#
# Usage:
#   ./scripts/backup_database.sh           # Creates timestamped backup
#   ./scripts/backup_database.sh restore backup_file.sql  # Restore from backup
#
# Recommended: Add to crontab for daily backups:
#   0 2 * * * /path/to/unified-donkey-betz/scripts/backup_database.sh

set -e

# Configuration
DB_NAME="unified_donkey_betz"
BACKUP_DIR="$(dirname "$0")/../backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

if [ "$1" = "restore" ]; then
    # Restore mode
    if [ -z "$2" ]; then
        echo "Usage: $0 restore <backup_file.sql>"
        exit 1
    fi

    RESTORE_FILE="$2"
    if [ ! -f "$RESTORE_FILE" ]; then
        echo "Backup file not found: $RESTORE_FILE"
        exit 1
    fi

    echo "WARNING: This will overwrite the current database!"
    echo "Database: $DB_NAME"
    echo "Backup file: $RESTORE_FILE"
    read -p "Are you sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" = "yes" ]; then
        echo "Restoring database..."
        psql -d "$DB_NAME" < "$RESTORE_FILE"
        echo "Database restored from: $RESTORE_FILE"
    else
        echo "Restore cancelled."
    fi
else
    # Backup mode
    echo "Creating database backup..."
    echo "Database: $DB_NAME"
    echo "Backup file: $BACKUP_FILE"

    pg_dump "$DB_NAME" > "$BACKUP_FILE"

    # Compress the backup
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"

    # Get file size
    SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')

    echo "Backup created: $BACKUP_FILE ($SIZE)"

    # Keep only last 30 backups
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.sql.gz 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 30 ]; then
        echo "Cleaning old backups (keeping last 30)..."
        ls -1t "$BACKUP_DIR"/*.sql.gz | tail -n +31 | xargs rm -f
    fi

    echo "Done!"
fi
