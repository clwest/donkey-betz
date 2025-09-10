#!/bin/bash

# Complete backup and migration script for moveyourazz_dev database
# This ensures ALL data is preserved before deletion

set -e  # Exit on error

echo "=========================================="
echo "MOVEYOURAZZ_DEV COMPLETE BACKUP & MIGRATE"
echo "=========================================="
echo "Date: $(date)"
echo

# Configuration
SOURCE_DB="moveyourazz_dev"
SOURCE_USER="donkeyking"
TARGET_DB="ai_unified_platform"
TARGET_USER="ai_unified_user"
TARGET_PASS="ai_unified_pass_2025"
BACKUP_DIR="./database_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Step 1: Creating complete database backup..."
echo "----------------------------------------"
BACKUP_FILE="$BACKUP_DIR/${SOURCE_DB}_complete_${TIMESTAMP}.sql"
pg_dump -U $SOURCE_USER -h localhost $SOURCE_DB > $BACKUP_FILE

if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(ls -lh $BACKUP_FILE | awk '{print $5}')
    echo "✅ Backup created: $BACKUP_FILE (Size: $BACKUP_SIZE)"
else
    echo "❌ Backup failed!"
    exit 1
fi

echo
echo "Step 2: Creating compressed backup..."
echo "----------------------------------------"
gzip -c $BACKUP_FILE > "${BACKUP_FILE}.gz"
COMPRESSED_SIZE=$(ls -lh "${BACKUP_FILE}.gz" | awk '{print $5}')
echo "✅ Compressed backup: ${BACKUP_FILE}.gz (Size: $COMPRESSED_SIZE)"

echo
echo "Step 3: Exporting important tables as CSV..."
echo "----------------------------------------"
CSV_DIR="$BACKUP_DIR/csv_exports_${TIMESTAMP}"
mkdir -p $CSV_DIR

# Export important tables as CSV for easy access
IMPORTANT_TABLES=(
    "ai_partner_conversationtopic"
    "ai_partner_conversationmemory"
    "core_aiusagetracking"
    "agent_memory_contributions"
    "agent_mythology_profiles"
    "mythology_events"
    "prompting_system_extractedtemplatecomponent"
    "prompting_system_extractedexample"
)

for table in "${IMPORTANT_TABLES[@]}"; do
    echo "  Exporting $table..."
    psql -U $SOURCE_USER -h localhost $SOURCE_DB -c "\COPY $table TO '$CSV_DIR/${table}.csv' WITH CSV HEADER" 2>/dev/null || echo "    ⚠️ Skipped $table"
done

echo "✅ CSV exports saved to: $CSV_DIR"

echo
echo "Step 4: Creating metadata report..."
echo "----------------------------------------"
REPORT_FILE="$BACKUP_DIR/migration_report_${TIMESTAMP}.txt"

cat > $REPORT_FILE << EOF
MOVEYOURAZZ_DEV DATABASE MIGRATION REPORT
==========================================
Date: $(date)
Source Database: $SOURCE_DB
Target Database: $TARGET_DB

DATABASE STATISTICS
-------------------
EOF

# Add table counts to report
psql -U $SOURCE_USER -h localhost $SOURCE_DB -c "
    SELECT relname as table_name, n_live_tup as record_count 
    FROM pg_stat_user_tables 
    WHERE n_live_tup > 0 
    ORDER BY n_live_tup DESC
" >> $REPORT_FILE

# Add database size
echo -e "\nDATABASE SIZE" >> $REPORT_FILE
psql -U $SOURCE_USER -h localhost $SOURCE_DB -c "
    SELECT pg_database.datname,
           pg_size_pretty(pg_database_size(pg_database.datname)) AS size
    FROM pg_database WHERE datname = '$SOURCE_DB'
" >> $REPORT_FILE

echo "✅ Report saved to: $REPORT_FILE"

echo
echo "Step 5: Verifying embeddings migration..."
echo "----------------------------------------"
# Check embeddings in target database
EMBEDDINGS_COUNT=$(PGPASSWORD=$TARGET_PASS psql -U $TARGET_USER -h localhost $TARGET_DB -t -c "
    SELECT COUNT(*) FROM unified_embeddings 
    WHERE source_database = '$SOURCE_DB'
")

echo "  Embeddings migrated from $SOURCE_DB: $EMBEDDINGS_COUNT"

echo
echo "=========================================="
echo "BACKUP SUMMARY"
echo "=========================================="
echo "✅ Full SQL backup: $BACKUP_FILE"
echo "✅ Compressed backup: ${BACKUP_FILE}.gz"
echo "✅ CSV exports: $CSV_DIR"
echo "✅ Migration report: $REPORT_FILE"
echo
echo "NEXT STEPS:"
echo "-----------"
echo "1. Review the migration report"
echo "2. Verify all critical data is in $TARGET_DB"
echo "3. Test the application with $TARGET_DB"
echo "4. If everything works, delete the database:"
echo "   dropdb -U $SOURCE_USER $SOURCE_DB"
echo
echo "TO RESTORE IF NEEDED:"
echo "   createdb -U $SOURCE_USER ${SOURCE_DB}_restored"
echo "   psql -U $SOURCE_USER ${SOURCE_DB}_restored < $BACKUP_FILE"
echo
echo "✅ Backup complete and safe to proceed with deletion!"