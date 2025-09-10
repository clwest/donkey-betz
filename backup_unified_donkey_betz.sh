#!/bin/bash

# Backup script for unified_donkey_betz database
set -e

echo "=========================================="
echo "UNIFIED_DONKEY_BETZ BACKUP"
echo "=========================================="
echo "Date: $(date)"
echo

BACKUP_DIR="./database_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "Creating backup..."
BACKUP_FILE="$BACKUP_DIR/unified_donkey_betz_${TIMESTAMP}.sql"
pg_dump -U postgres -h localhost unified_donkey_betz > $BACKUP_FILE

echo "Compressing..."
gzip -c $BACKUP_FILE > "${BACKUP_FILE}.gz"

echo
echo "✅ Backup complete!"
echo "   SQL: $BACKUP_FILE"
echo "   GZ:  ${BACKUP_FILE}.gz"
echo
echo "To restore:"
echo "   createdb -U postgres unified_donkey_betz_restored"
echo "   psql -U postgres unified_donkey_betz_restored < $BACKUP_FILE"
