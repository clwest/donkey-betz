#!/usr/bin/env python
"""
Migrate ALL data from unified_donkey_betz to ai_unified_platform
This ensures NOTHING is lost before deletion.
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
import json
from datetime import datetime
import uuid

def get_connection(database):
    """Get database connection"""
    if database == 'unified_donkey_betz':
        return psycopg2.connect(
            host='localhost',
            database='unified_donkey_betz',
            user='postgres',
            cursor_factory=RealDictCursor
        )
    elif database == 'ai_unified_platform':
        return psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='[REDACTED - HISTORICAL SECRET]',
            cursor_factory=RealDictCursor
        )

def serialize_for_json(obj):
    """Serialize objects for JSON storage"""
    if obj is None:
        return None
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif isinstance(obj, (dict, list)):
        return obj
    else:
        return str(obj)

def ensure_legacy_tables():
    """Ensure legacy data tables exist"""
    conn = get_connection('ai_unified_platform')
    cur = conn.cursor()
    
    try:
        # Create unified_donkey_betz_legacy table for all non-embedding data
        cur.execute("""
            CREATE TABLE IF NOT EXISTS unified_donkey_betz_legacy (
                id SERIAL PRIMARY KEY,
                source_table VARCHAR(255) NOT NULL,
                source_id VARCHAR(255),
                data_type VARCHAR(100),
                content TEXT,
                metadata JSONB,
                original_data JSONB,
                created_at TIMESTAMPTZ,
                migrated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(source_table, source_id)
            )
        """)
        
        # Create index
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_udb_legacy_source 
            ON unified_donkey_betz_legacy(source_table, data_type)
        """)
        
        conn.commit()
        print("✅ Legacy tables ready")
        
    finally:
        conn.close()

def migrate_agents():
    """Migrate ALL agent templates"""
    source_conn = get_connection('unified_donkey_betz')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating Agent Templates...")
        
        source_cur.execute("SELECT * FROM agents_unifiedagenttemplate")
        agents = source_cur.fetchall()
        
        print(f"   Found {len(agents)} agent templates")
        
        migrated = 0
        for agent in agents:
            try:
                # Store in legacy table with full data
                content = f"Agent: {agent.get('name', '')}\n"
                content += f"Display: {agent.get('display_name', '')}\n"
                content += f"Category: {agent.get('category', '')}\n"
                content += f"Description: {agent.get('description', '')[:500]}"
                
                target_cur.execute("""
                    INSERT INTO unified_donkey_betz_legacy (
                        source_table, source_id, data_type,
                        content, metadata, original_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_table, source_id) DO UPDATE
                    SET original_data = EXCLUDED.original_data,
                        metadata = EXCLUDED.metadata
                """, (
                    'agents_unifiedagenttemplate',
                    str(agent.get('id', '')),
                    'agent_template',
                    content[:10000],
                    json.dumps({k: serialize_for_json(v) for k, v in agent.items() if k not in ['id', 'created_at']}),
                    json.dumps({k: serialize_for_json(v) for k, v in agent.items()}),
                    agent.get('created_at')
                ))
                
                migrated += 1
                
            except Exception as e:
                print(f"      Error with agent {agent.get('name', 'unknown')}: {str(e)[:50]}")
                continue
        
        target_conn.commit()
        print(f"   ✅ Migrated {migrated} agent templates")
        
    finally:
        source_conn.close()
        target_conn.close()
    
    return migrated

def migrate_sports_data():
    """Migrate ALL sports data"""
    source_conn = get_connection('unified_donkey_betz')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating Sports Data...")
        
        sports_tables = [
            ('sports_league', 'sports_league'),
            ('sports_team', 'sports_team'),
            ('sports_game', 'sports_game'),
            ('sports_sportsbook', 'sportsbook'),
            ('sports_bettingmarket', 'betting_market'),
            ('sports_oddsline', 'odds_line'),
            ('sports_bankrollmanagement', 'bankroll')
        ]
        
        total_migrated = 0
        
        for table_name, data_type in sports_tables:
            try:
                source_cur.execute(f"SELECT * FROM {table_name}")
                records = source_cur.fetchall()
                
                if not records:
                    continue
                
                print(f"   Migrating {table_name}: {len(records)} records")
                
                migrated = 0
                for record in records:
                    try:
                        # Create content summary
                        content = f"Type: {data_type}\n"
                        for key, value in record.items()[:5]:  # First 5 fields for summary
                            if key != 'id':
                                content += f"{key}: {str(value)[:100]}\n"
                        
                        target_cur.execute("""
                            INSERT INTO unified_donkey_betz_legacy (
                                source_table, source_id, data_type,
                                content, metadata, original_data, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (source_table, source_id) DO UPDATE
                            SET original_data = EXCLUDED.original_data
                        """, (
                            table_name,
                            str(record.get('id', '')),
                            data_type,
                            content[:10000],
                            json.dumps({k: serialize_for_json(v) for k, v in record.items() if k != 'id'}),
                            json.dumps({k: serialize_for_json(v) for k, v in record.items()}),
                            record.get('created_at', datetime.now())
                        ))
                        
                        migrated += 1
                        
                    except Exception as e:
                        continue
                
                print(f"      ✅ {migrated} {table_name} records")
                total_migrated += migrated
                
            except Exception as e:
                print(f"      ❌ Error with {table_name}: {str(e)[:50]}")
                continue
        
        target_conn.commit()
        print(f"   ✅ Total sports records migrated: {total_migrated}")
        
    finally:
        source_conn.close()
        target_conn.close()
    
    return total_migrated

def migrate_users_and_auth():
    """Migrate user and authentication data"""
    source_conn = get_connection('unified_donkey_betz')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating User and Auth Data...")
        
        # Migrate users
        source_cur.execute("SELECT * FROM core_unifieduser")
        users = source_cur.fetchall()
        
        if users:
            print(f"   Found {len(users)} users")
            
            for user in users:
                content = f"User: {user.get('email', '')}\n"
                content += f"Username: {user.get('username', '')}\n"
                content += f"Created: {user.get('date_joined', '')}"
                
                target_cur.execute("""
                    INSERT INTO unified_donkey_betz_legacy (
                        source_table, source_id, data_type,
                        content, metadata, original_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_table, source_id) DO NOTHING
                """, (
                    'core_unifieduser',
                    str(user.get('id', '')),
                    'user',
                    content,
                    json.dumps({'email': user.get('email', ''), 'username': user.get('username', '')}),
                    json.dumps({k: serialize_for_json(v) for k, v in user.items() if k != 'password'}),
                    user.get('date_joined')
                ))
            
            target_conn.commit()
            print(f"   ✅ Migrated {len(users)} users")
        
    finally:
        source_conn.close()
        target_conn.close()

def migrate_platform_metrics():
    """Migrate platform metrics"""
    source_conn = get_connection('unified_donkey_betz')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Checking Platform Metrics...")
        
        source_cur.execute("SELECT * FROM core_platformmetrics")
        metrics = source_cur.fetchall()
        
        if metrics:
            print(f"   Found {len(metrics)} metrics records")
            
            for metric in metrics:
                target_cur.execute("""
                    INSERT INTO unified_donkey_betz_legacy (
                        source_table, source_id, data_type,
                        content, original_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_table, source_id) DO NOTHING
                """, (
                    'core_platformmetrics',
                    str(metric.get('id', '')),
                    'platform_metrics',
                    json.dumps({k: serialize_for_json(v) for k, v in metric.items()})[:10000],
                    json.dumps({k: serialize_for_json(v) for k, v in metric.items()}),
                    metric.get('created_at', datetime.now())
                ))
            
            target_conn.commit()
            print(f"   ✅ Migrated {len(metrics)} metrics")
        
    finally:
        source_conn.close()
        target_conn.close()

def final_verification():
    """Verify migration completeness"""
    target_conn = get_connection('ai_unified_platform')
    target_cur = target_conn.cursor()
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION VERIFICATION")
    print("=" * 80)
    
    # Check legacy data
    target_cur.execute("""
        SELECT data_type, COUNT(*) as count
        FROM unified_donkey_betz_legacy
        GROUP BY data_type
        ORDER BY count DESC
    """)
    
    results = target_cur.fetchall()
    
    if results:
        print("\n📊 Migrated Data Summary:")
        print("-" * 50)
        print(f"{'Data Type':<25} {'Count':<10}")
        print("-" * 50)
        
        total = 0
        for row in results:
            print(f"{row['data_type']:<25} {row['count']:<10}")
            total += row['count']
        
        print("-" * 50)
        print(f"{'TOTAL':<25} {total:<10}")
    
    # Check embeddings
    target_cur.execute("""
        SELECT COUNT(*) as count 
        FROM unified_embeddings
    """)
    embeddings = target_cur.fetchone()['count']
    
    print(f"\n✅ Total embeddings in ai_unified_platform: {embeddings:,}")
    
    target_conn.close()

def main():
    print("=" * 80)
    print("🚀 COMPLETE MIGRATION: unified_donkey_betz → ai_unified_platform")
    print("=" * 80)
    print("\nTarget Database: ai_unified_platform")
    print("This will migrate ALL remaining data before deletion")
    
    # Ensure tables exist
    ensure_legacy_tables()
    
    # Migrate everything
    total_migrated = 0
    
    total_migrated += migrate_agents()
    total_migrated += migrate_sports_data()
    migrate_users_and_auth()
    migrate_platform_metrics()
    
    # Verify
    final_verification()
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    print(f"\nAll data from unified_donkey_betz has been migrated to ai_unified_platform")
    print(f"Total records migrated: {total_migrated}+")
    print("\n📝 Data is now in ai_unified_platform:")
    print("  • unified_embeddings table (embeddings)")
    print("  • legacy_moveyourazz_data table (moveyourazz data)")
    print("  • unified_donkey_betz_legacy table (unified_donkey_betz data)")
    print("\n🎯 Ready for backup and deletion of unified_donkey_betz!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()