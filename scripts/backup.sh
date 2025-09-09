#!/bin/bash
# =============================================================================
# UNIFIED DONKEY BETZ PLATFORM - AUTOMATED BACKUP SCRIPT
# Comprehensive backup solution for production deployment
# =============================================================================

set -e

# Configuration
BACKUP_DIR=${BACKUP_DIR:-"/backups"}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
POSTGRES_HOST=${POSTGRES_HOST:-"postgres"}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-"ai_unified_platform"}
POSTGRES_USER=${POSTGRES_USER:-"unified_user"}
REDIS_HOST=${REDIS_HOST:-"redis"}
REDIS_PORT=${REDIS_PORT:-6379}

# S3 Configuration (optional)
AWS_S3_BUCKET=${AWS_S3_BUCKET:-""}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-""}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-""}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

log "Starting Unified Donkey Betz Platform backup - $TIMESTAMP"

# PostgreSQL Backup
log "Backing up PostgreSQL database..."
if pg_dump -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
   --no-password --verbose --clean --if-exists --create \
   > "$BACKUP_DIR/$TIMESTAMP/postgres_backup.sql"; then
    success "PostgreSQL backup completed"
    
    # Compress the backup
    gzip "$BACKUP_DIR/$TIMESTAMP/postgres_backup.sql"
    success "PostgreSQL backup compressed"
else
    error "PostgreSQL backup failed"
    exit 1
fi

# Redis Backup
log "Backing up Redis data..."
if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" --rdb "$BACKUP_DIR/$TIMESTAMP/redis_backup.rdb"; then
    success "Redis backup completed"
else
    warning "Redis backup failed or skipped"
fi

# Django Data Backup (if manage.py is available)
if [ -f "/app/manage.py" ]; then
    log "Backing up Django application data..."
    cd /app
    if python manage.py dumpdata --natural-foreign --natural-primary \
       > "$BACKUP_DIR/$TIMESTAMP/django_backup.json"; then
        success "Django data backup completed"
        gzip "$BACKUP_DIR/$TIMESTAMP/django_backup.json"
    else
        warning "Django data backup failed"
    fi
fi

# Media Files Backup
if [ -d "/app/media" ]; then
    log "Backing up media files..."
    if tar -czf "$BACKUP_DIR/$TIMESTAMP/media_backup.tar.gz" -C /app media/; then
        success "Media files backup completed"
    else
        warning "Media files backup failed"
    fi
fi

# Static Files Backup
if [ -d "/app/staticfiles" ]; then
    log "Backing up static files..."
    if tar -czf "$BACKUP_DIR/$TIMESTAMP/static_backup.tar.gz" -C /app staticfiles/; then
        success "Static files backup completed"
    else
        warning "Static files backup failed"
    fi
fi

# Configuration Backup
log "Backing up configuration files..."
CONFIG_FILES=("/app/.env" "/app/config" "/etc/nginx" "/etc/ssl")
for config_path in "${CONFIG_FILES[@]}"; do
    if [ -e "$config_path" ]; then
        cp -r "$config_path" "$BACKUP_DIR/$TIMESTAMP/" 2>/dev/null || true
    fi
done

# Create backup manifest
cat > "$BACKUP_DIR/$TIMESTAMP/backup_manifest.txt" << EOF
Unified Donkey Betz Platform Backup
==================================
Timestamp: $TIMESTAMP
Date: $(date)
Host: $(hostname)
Platform Version: $(cat /app/VERSION 2>/dev/null || echo "Unknown")

Backup Contents:
- PostgreSQL Database: $([ -f "$BACKUP_DIR/$TIMESTAMP/postgres_backup.sql.gz" ] && echo "✓" || echo "✗")
- Redis Data: $([ -f "$BACKUP_DIR/$TIMESTAMP/redis_backup.rdb" ] && echo "✓" || echo "✗")
- Django Data: $([ -f "$BACKUP_DIR/$TIMESTAMP/django_backup.json.gz" ] && echo "✓" || echo "✗")
- Media Files: $([ -f "$BACKUP_DIR/$TIMESTAMP/media_backup.tar.gz" ] && echo "✓" || echo "✗")
- Static Files: $([ -f "$BACKUP_DIR/$TIMESTAMP/static_backup.tar.gz" ] && echo "✓" || echo "✗")

Backup Size: $(du -sh "$BACKUP_DIR/$TIMESTAMP" | cut -f1)
EOF

success "Backup manifest created"

# Upload to S3 (if configured)
if [ -n "$AWS_S3_BUCKET" ] && [ -n "$AWS_ACCESS_KEY_ID" ]; then
    log "Uploading backup to S3..."
    if command -v aws &> /dev/null; then
        if aws s3 sync "$BACKUP_DIR/$TIMESTAMP" "s3://$AWS_S3_BUCKET/backups/$TIMESTAMP/" --delete; then
            success "Backup uploaded to S3"
        else
            error "Failed to upload backup to S3"
        fi
    else
        warning "AWS CLI not available, skipping S3 upload"
    fi
fi

# Cleanup old backups
log "Cleaning up old backups (retention: $BACKUP_RETENTION_DAYS days)..."
find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" -mtime +$BACKUP_RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true

# Cleanup old S3 backups (if configured)
if [ -n "$AWS_S3_BUCKET" ] && [ -n "$AWS_ACCESS_KEY_ID" ] && command -v aws &> /dev/null; then
    log "Cleaning up old S3 backups..."
    aws s3 ls "s3://$AWS_S3_BUCKET/backups/" --recursive | \
    while read -r line; do
        backup_date=$(echo "$line" | awk '{print $1}')
        backup_path=$(echo "$line" | awk '{print $4}')
        if [ -n "$backup_date" ]; then
            backup_age=$(( ($(date +%s) - $(date -d "$backup_date" +%s)) / 86400 ))
            if [ $backup_age -gt $BACKUP_RETENTION_DAYS ]; then
                aws s3 rm "s3://$AWS_S3_BUCKET/$backup_path"
            fi
        fi
    done 2>/dev/null || true
fi

# Final backup verification
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$TIMESTAMP" | cut -f1)
success "Backup completed successfully!"
log "Backup location: $BACKUP_DIR/$TIMESTAMP"
log "Backup size: $BACKUP_SIZE"

# Send notification (if configured)
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
    curl -X POST -H 'Content-type: application/json' \
         --data "{\"text\":\"✅ Unified Donkey Betz Platform backup completed successfully.\nTimestamp: $TIMESTAMP\nSize: $BACKUP_SIZE\"}" \
         "$SLACK_WEBHOOK_URL" 2>/dev/null || true
fi

exit 0