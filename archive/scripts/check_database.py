#!/usr/bin/env python3
"""
Check database tables and connection
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from django.db import connection
from django.conf import settings

def check_database():
    """Check database connection and tables"""
    print("🔍 DATABASE CONNECTION CHECK")
    print("=" * 60)
    
    # Check connection settings
    print(f"Database Engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"Database Name: {settings.DATABASES['default']['NAME']}")
    print(f"Database Host: {settings.DATABASES['default'].get('HOST', 'localhost')}")
    print(f"Database Port: {settings.DATABASES['default'].get('PORT', '5432')}")
    print()
    
    # Test connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL Version: {version[0]}")
            
            # Get database size
            cursor.execute("""
                SELECT pg_database_size(current_database()) / 1024 / 1024 as size_mb
            """)
            size = cursor.fetchone()[0]
            print(f"✅ Database Size: {size:.2f} MB")
            
            # Count connections
            cursor.execute("""
                SELECT COUNT(*) FROM pg_stat_activity
            """)
            conn_count = cursor.fetchone()[0]
            print(f"✅ Active Connections: {conn_count}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return
    
    print("\n📊 TABLE STATUS")
    print("-" * 60)
    
    # Check for required tables
    tables_to_check = [
        'agents_unifiedagenttemplate',
        'agents_agentexecution',
        'core_aistrategy',
        'core_generatedproject',
        'unified_embeddings',
        'income_incomestream',
        'income_opportunityscan'
    ]
    
    for table_name in tables_to_check:
        try:
            with connection.cursor() as cursor:
                # Check if table exists
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = %s
                """, [table_name])
                
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    # Count rows
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"✅ {table_name}: {count} rows")
                else:
                    print(f"❌ {table_name}: TABLE NOT FOUND")
                    
        except Exception as e:
            print(f"⚠️  {table_name}: Error - {str(e)[:50]}")
    
    print("\n🧪 SAMPLE DATA CHECK")
    print("-" * 60)
    
    # Try to get sample agent data
    try:
        from agents.models import UnifiedAgentTemplate
        agents = UnifiedAgentTemplate.objects.all()[:3]
        if agents:
            print(f"Found {UnifiedAgentTemplate.objects.count()} agents:")
            for agent in agents:
                print(f"  - {agent.name}: {agent.specialization}")
        else:
            print("No agents found in database")
    except Exception as e:
        print(f"Error fetching agents: {e}")
    
    print("\n💡 NEXT STEPS:")
    print("-" * 60)
    if connection.vendor == 'postgresql':
        print("✅ PostgreSQL is properly configured")
        print("\nTo populate data, run:")
        print("  python manage.py migrate")
        print("  python populate_real_data_simple.py")
        print("  python manage.py loaddata initial_data.json  # if you have fixtures")
    else:
        print(f"⚠️  Using {connection.vendor} instead of PostgreSQL")
        print("Update your DATABASES setting in settings.py")

if __name__ == "__main__":
    check_database()
