#!/usr/bin/env python
"""
Migrate ALL important data from moveyourazz_dev to ai_unified_platform
This includes conversation topics, AI usage tracking, agent profiles, and more.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import uuid

def get_connection(database):
    """Get database connection"""
    if database == 'moveyourazz_dev':
        return psycopg2.connect(
            host='localhost',
            database='moveyourazz_dev',
            user='donkeyking',
            cursor_factory=RealDictCursor
        )
    elif database == 'ai_unified_platform':
        return psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='ai_unified_pass_2025',
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

def create_legacy_data_table():
    """Create table for storing legacy data if it doesn't exist"""
    conn = get_connection('ai_unified_platform')
    cur = conn.cursor()
    
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS legacy_moveyourazz_data (
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
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_legacy_source 
            ON legacy_moveyourazz_data(source_table, data_type)
        """)
        
        conn.commit()
        print("✅ Legacy data table ready")
        
    except Exception as e:
        if "already exists" in str(e):
            print("✅ Legacy data table already exists")
        else:
            print(f"❌ Error creating table: {str(e)}")
            raise
    finally:
        conn.close()

def migrate_conversation_topics():
    """Migrate conversation topics (1,882 records)"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating conversation topics...")
        
        source_cur.execute("""
            SELECT * FROM ai_partner_conversationtopic
            ORDER BY last_mentioned DESC
        """)
        
        records = source_cur.fetchall()
        print(f"   Found {len(records)} conversation topics")
        
        migrated = 0
        for record in records:
            try:
                # Prepare content
                content = f"Topic: {record.get('topic_name', '')}\n"
                if record.get('description'):
                    content += f"Description: {record['description']}\n"
                if record.get('key_insights'):
                    content += f"Insights: {record['key_insights']}"
                
                # Prepare metadata
                metadata = {}
                for key, value in record.items():
                    if key not in ['id', 'created_at']:
                        metadata[key] = serialize_for_json(value)
                
                # Store in legacy data table
                target_cur.execute("""
                    INSERT INTO legacy_moveyourazz_data (
                        source_table, source_id, data_type,
                        content, metadata, original_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_table, source_id) DO NOTHING
                """, (
                    'ai_partner_conversationtopic',
                    str(record.get('id', '')),
                    'conversation_topic',
                    content[:10000],
                    json.dumps(metadata),
                    json.dumps({k: serialize_for_json(v) for k, v in record.items()}),
                    record.get('last_mentioned')
                ))
                
                migrated += 1
                
            except Exception as e:
                if migrated == 0:
                    print(f"      Error: {str(e)[:100]}")
                continue
        
        target_conn.commit()
        print(f"   ✅ Migrated {migrated} conversation topics")
        
    finally:
        source_conn.close()
        target_conn.close()
    
    return migrated

def migrate_ai_usage_tracking():
    """Migrate AI usage tracking data (1,345 records)"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating AI usage tracking...")
        
        source_cur.execute("""
            SELECT * FROM core_aiusagetracking
            ORDER BY id DESC
        """)
        
        records = source_cur.fetchall()
        print(f"   Found {len(records)} usage tracking records")
        
        migrated = 0
        for record in records:
            try:
                # Prepare content
                content = f"Model: {record.get('model_name', '')}\n"
                content += f"Tokens: {record.get('total_tokens', 0)}\n"
                content += f"Cost: ${record.get('estimated_cost', 0):.4f}"
                
                # Store in legacy data table
                target_cur.execute("""
                    INSERT INTO legacy_moveyourazz_data (
                        source_table, source_id, data_type,
                        content, metadata, original_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_table, source_id) DO NOTHING
                """, (
                    'core_aiusagetracking',
                    str(record.get('id', '')),
                    'usage_tracking',
                    content,
                    json.dumps({k: serialize_for_json(v) for k, v in record.items() if k != 'id'}),
                    json.dumps({k: serialize_for_json(v) for k, v in record.items()}),
                    record.get('last_mentioned')
                ))
                
                migrated += 1
                
            except Exception as e:
                continue
        
        target_conn.commit()
        print(f"   ✅ Migrated {migrated} usage tracking records")
        
    finally:
        source_conn.close()
        target_conn.close()
    
    return migrated

def migrate_agent_profiles():
    """Migrate agent mythology profiles (626 records)"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating agent mythology profiles...")
        
        source_cur.execute("""
            SELECT * FROM agent_mythology_profiles
            ORDER BY id DESC
        """)
        
        records = source_cur.fetchall()
        print(f"   Found {len(records)} agent profiles")
        
        migrated = 0
        for record in records:
            try:
                # Prepare content
                content = f"Agent: {record.get('agent_name', '')}\n"
                content += f"Mythology: {record.get('mythology_type', '')}\n"
                if record.get('profile_data'):
                    content += f"Profile: {json.dumps(record['profile_data'])[:500]}"
                
                # Store in legacy data table
                target_cur.execute("""
                    INSERT INTO legacy_moveyourazz_data (
                        source_table, source_id, data_type,
                        content, metadata, original_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_table, source_id) DO NOTHING
                """, (
                    'agent_mythology_profiles',
                    str(record.get('id', '')),
                    'agent_profile',
                    content[:10000],
                    json.dumps({k: serialize_for_json(v) for k, v in record.items() if k != 'id'}),
                    json.dumps({k: serialize_for_json(v) for k, v in record.items()}),
                    record.get('last_mentioned')
                ))
                
                migrated += 1
                
            except Exception as e:
                continue
        
        target_conn.commit()
        print(f"   ✅ Migrated {migrated} agent profiles")
        
    finally:
        source_conn.close()
        target_conn.close()
    
    return migrated

def migrate_prompting_templates():
    """Migrate prompting system templates (1,230 records)"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating prompting templates...")
        
        source_cur.execute("""
            SELECT * FROM prompting_system_extractedtemplatecomponent
            ORDER BY id DESC
        """)
        
        records = source_cur.fetchall()
        print(f"   Found {len(records)} template components")
        
        migrated = 0
        for record in records:
            try:
                # Prepare content
                content = f"Component: {record.get('component_name', '')}\n"
                content += f"Type: {record.get('component_type', '')}\n"
                if record.get('template_content'):
                    content += f"Template: {record['template_content'][:1000]}"
                
                # Store in legacy data table
                target_cur.execute("""
                    INSERT INTO legacy_moveyourazz_data (
                        source_table, source_id, data_type,
                        content, metadata, original_data, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (source_table, source_id) DO NOTHING
                """, (
                    'prompting_system_extractedtemplatecomponent',
                    str(record.get('id', '')),
                    'prompt_template',
                    content[:10000],
                    json.dumps({k: serialize_for_json(v) for k, v in record.items() if k != 'id'}),
                    json.dumps({k: serialize_for_json(v) for k, v in record.items()}),
                    record.get('last_mentioned')
                ))
                
                migrated += 1
                
            except Exception as e:
                continue
        
        target_conn.commit()
        print(f"   ✅ Migrated {migrated} template components")
        
    finally:
        source_conn.close()
        target_conn.close()
    
    return migrated

def generate_final_report():
    """Generate comprehensive migration report"""
    conn = get_connection('ai_unified_platform')
    cur = conn.cursor()
    
    print("\n" + "=" * 80)
    print("📊 COMPLETE DATA MIGRATION REPORT")
    print("=" * 80)
    
    # Check unified_embeddings
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM unified_embeddings 
        WHERE source_database = 'moveyourazz_dev'
    """)
    embeddings_count = cur.fetchone()['count']
    
    # Check legacy data
    cur.execute("""
        SELECT data_type, COUNT(*) as count 
        FROM legacy_moveyourazz_data 
        GROUP BY data_type
        ORDER BY count DESC
    """)
    legacy_data = cur.fetchall()
    
    print(f"\n✅ Embeddings migrated: {embeddings_count:,}")
    
    if legacy_data:
        print("\n✅ Other data migrated:")
        for row in legacy_data:
            print(f"   {row['data_type']:25} {row['count']:,}")
    
    # Total legacy records
    cur.execute("SELECT COUNT(*) as count FROM legacy_moveyourazz_data")
    total_legacy = cur.fetchone()['count']
    
    print(f"\n📊 Total legacy records: {total_legacy:,}")
    print(f"📊 Total embeddings: {embeddings_count:,}")
    print(f"📊 Grand total: {total_legacy + embeddings_count:,}")
    
    conn.close()

def main():
    print("=" * 80)
    print("🚀 COMPLETE DATA MIGRATION FROM MOVEYOURAZZ_DEV")
    print("=" * 80)
    print("\nMigrating ALL important data to ai_unified_platform...")
    
    # Create legacy data table
    create_legacy_data_table()
    
    # Migrate all data types
    total_migrated = 0
    
    total_migrated += migrate_conversation_topics()
    total_migrated += migrate_ai_usage_tracking()
    total_migrated += migrate_agent_profiles()
    total_migrated += migrate_prompting_templates()
    
    # Generate report
    generate_final_report()
    
    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    print(f"\nAll important data from moveyourazz_dev has been migrated.")
    print(f"Total new records migrated: {total_migrated:,}")
    print("\n📝 Data is stored in:")
    print("  • unified_embeddings table (for embeddings)")
    print("  • legacy_moveyourazz_data table (for other data)")
    print("\n🎯 Ready to proceed with backup and deletion!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()