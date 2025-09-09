#!/bin/bash

# Unified Donkey Betz Platform - Database Management Script
# Usage: ./manage_database.sh [command]

set -e

DB_NAME="unified_donkey_betz"
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PostgreSQL is running
check_postgres() {
    if ! brew services list | grep -q "postgresql@15.*started"; then
        print_error "PostgreSQL is not running. Start it with: brew services start postgresql@15"
        exit 1
    fi
    print_status "PostgreSQL is running"
}

# Backup database
backup_db() {
    print_status "Creating database backup..."
    local backup_file="backups/unified_donkey_betz_$(date +%Y%m%d_%H%M%S).sql"
    mkdir -p backups
    pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $backup_file
    print_status "Backup created: $backup_file"
}

# Restore database from backup
restore_db() {
    if [ -z "$1" ]; then
        print_error "Please specify backup file: ./manage_database.sh restore [backup_file]"
        exit 1
    fi
    
    print_warning "This will drop and recreate the database. Continue? (y/N)"
    read -r confirmation
    if [[ $confirmation != [yY] ]]; then
        print_status "Restore cancelled"
        exit 0
    fi
    
    print_status "Dropping existing database..."
    dropdb -h $DB_HOST -U $DB_USER --if-exists $DB_NAME
    
    print_status "Creating fresh database..."
    createdb -h $DB_HOST -U $DB_USER $DB_NAME
    
    print_status "Installing pgvector extension..."
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    print_status "Restoring from backup: $1"
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME < $1
    
    print_status "Database restored successfully"
}

# Reset database (fresh start)
reset_db() {
    print_warning "This will completely reset the database. All data will be lost. Continue? (y/N)"
    read -r confirmation
    if [[ $confirmation != [yY] ]]; then
        print_status "Reset cancelled"
        exit 0
    fi
    
    print_status "Creating backup before reset..."
    backup_db
    
    print_status "Dropping existing database..."
    dropdb -h $DB_HOST -U $DB_USER --if-exists $DB_NAME
    
    print_status "Creating fresh database..."
    createdb -h $DB_HOST -U $DB_USER $DB_NAME
    
    print_status "Installing pgvector extension..."
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    print_status "Running Django migrations..."
    python manage.py migrate
    
    print_status "Creating superuser..."
    echo "from core.models import UnifiedUser; UnifiedUser.objects.create_superuser('admin', 'admin@unified-donkey-betz.com', 'admin123')" | python manage.py shell
    
    print_status "Database reset complete"
}

# Check database health
health_check() {
    print_status "Checking database health..."
    
    # Check connection
    if psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1;" > /dev/null 2>&1; then
        print_status "✓ Database connection successful"
    else
        print_error "✗ Database connection failed"
        exit 1
    fi
    
    # Check pgvector
    if psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM pg_available_extensions WHERE name = 'vector';" | grep -q vector; then
        print_status "✓ pgvector extension available"
    else
        print_warning "✗ pgvector extension not available"
    fi
    
    # Check Django migrations
    python manage.py showmigrations --verbosity=0 | grep -q "\[ \]" && {
        print_warning "✗ Some migrations are not applied"
    } || {
        print_status "✓ All migrations are applied"
    }
    
    # Check table count
    local table_count=$(psql -h $DB_HOST -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
    print_status "✓ Tables in database: $table_count"
    
    # Check user count
    local user_count=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.count())" | tail -1)
    print_status "✓ Users in system: $user_count"
}

# Show database information
info() {
    print_status "Database Information:"
    echo "  Database Name: $DB_NAME"
    echo "  Host: $DB_HOST:$DB_PORT"
    echo "  User: $DB_USER"
    echo ""
    
    print_status "PostgreSQL Version:"
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT version();"
    echo ""
    
    print_status "Database Size:"
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));"
    echo ""
    
    print_status "Tables:"
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "\dt"
}

# Main command handling
case "$1" in
    backup)
        check_postgres
        backup_db
        ;;
    restore)
        check_postgres
        restore_db "$2"
        ;;
    reset)
        check_postgres
        reset_db
        ;;
    health)
        check_postgres
        health_check
        ;;
    info)
        check_postgres
        info
        ;;
    *)
        echo "Unified Donkey Betz Platform - Database Management"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  backup          Create a backup of the database"
        echo "  restore [file]  Restore database from backup file"
        echo "  reset           Reset database (fresh start with migrations)"
        echo "  health          Check database health and status"
        echo "  info            Show database information"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore backups/unified_donkey_betz_20250908_214500.sql"
        echo "  $0 reset"
        echo "  $0 health"
        echo "  $0 info"
        ;;
esac