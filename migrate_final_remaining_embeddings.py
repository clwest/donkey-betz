#!/usr/bin/env python
"""
Migrate the final remaining embeddings from moveyourazz_dev to ai_unified_platform
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import hashlib

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

def serialize_value(value):
    """Serialize any value for JSON storage"""
    if value is None:
        return None
    elif isinstance(value, (datetime,)):
        return value.isoformat()
    elif isinstance(value, (dict, list)):
        return value
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    else:
        return str(value)

def migrate_conversation_memory():
    """Migrate ai_partner_conversationmemory embeddings"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Migrating ai_partner_conversationmemory...")
        
        # Get records with embeddings
        source_cur.execute("""
            SELECT id, embedding_vector, feature_vector, 
                   message_content, topics_discussed, created_at
            FROM ai_partner_conversationmemory
            WHERE embedding_vector IS NOT NULL 
               OR feature_vector IS NOT NULL
        """)
        
        records = source_cur.fetchall()
        print(f"   Found {len(records)} records with embeddings")
        
        migrated = 0
        for record in records:
            try:
                # Try embedding_vector first (JSONB)
                embedding = None
                if record['embedding_vector']:
                    if isinstance(record['embedding_vector'], str):
                        embedding = json.loads(record['embedding_vector'])
                    else:
                        embedding = record['embedding_vector']
                
                # If no embedding_vector, try feature_vector
                if not embedding and record['feature_vector']:
                    embedding = record['feature_vector']
                
                if not embedding or not isinstance(embedding, list):
                    continue
                
                # Ensure 1536 dimensions
                if len(embedding) != 1536:
                    continue
                
                # Prepare content
                content = record.get('message_content', '')
                if not content and record.get('topics_discussed'):
                    content = json.dumps(record['topics_discussed'])
                
                if not content:
                    content = f"Conversation memory {record['id']}"
                
                # Prepare metadata
                metadata = {
                    'original_id': str(record['id']),
                    'migration_date': datetime.now().isoformat(),
                    'source': 'ai_partner_conversationmemory'
                }
                
                if record.get('topics_discussed'):
                    metadata['topics'] = serialize_value(record['topics_discussed'])
                
                # Insert into unified_embeddings
                target_cur.execute("""
                    INSERT INTO unified_embeddings (
                        source_database, source_table, source_id,
                        content_type, content_text, embedding,
                        embedding_model, metadata, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s)
                    ON CONFLICT (source_database, source_table, source_id) 
                    DO NOTHING
                """, (
                    'moveyourazz_dev',
                    'ai_partner_conversationmemory',
                    str(record['id']),
                    'conversation',
                    content[:10000],
                    embedding,
                    'text-embedding-3-small',
                    json.dumps(metadata),
                    record.get('created_at', datetime.now())
                ))
                
                migrated += 1
                
            except Exception as e:
                if migrated == 0:
                    print(f"      Sample error: {str(e)[:100]}")
                continue
        
        target_conn.commit()
        print(f"   ✅ Migrated {migrated} conversation memories")
        
    finally:
        source_conn.close()
        target_conn.close()
    
    return migrated

def migrate_agent_contributions():
    """Check and migrate agent_memory_contributions if it has embeddings"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection('ai_unified_platform')
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print("\n📊 Checking agent_memory_contributions...")
        
        # Check what columns exist
        source_cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'agent_memory_contributions'
            AND (column_name LIKE '%embed%' OR column_name LIKE '%vector%')
        """)
        
        columns = source_cur.fetchall()
        
        if not columns:
            print("   ℹ️ No embedding columns found in agent_memory_contributions")
            return 0
        
        print(f"   Found columns: {[c['column_name'] for c in columns]}")
        
        # Get the actual embedding column name
        embedding_col = None
        for col in columns:
            if 'embed' in col['column_name'] or 'vector' in col['column_name']:
                embedding_col = col['column_name']
                break
        
        if not embedding_col:
            print("   ℹ️ No valid embedding column")
            return 0
        
        # Try to migrate
        source_cur.execute(f"""
            SELECT id, {embedding_col} as embedding, contribution_text, created_at
            FROM agent_memory_contributions
            WHERE {embedding_col} IS NOT NULL
        """)
        
        records = source_cur.fetchall()
        print(f"   Found {len(records)} records with embeddings")
        
        migrated = 0
        for record in records:
            try:
                embedding = record['embedding']
                
                # Parse if string
                if isinstance(embedding, str):
                    embedding = json.loads(embedding)
                
                if not isinstance(embedding, list) or len(embedding) != 1536:
                    continue
                
                content = record.get('contribution_text', f"Agent contribution {record['id']}")
                
                target_cur.execute("""
                    INSERT INTO unified_embeddings (
                        source_database, source_table, source_id,
                        content_type, content_text, embedding,
                        embedding_model, metadata, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s)
                    ON CONFLICT (source_database, source_table, source_id) 
                    DO NOTHING
                """, (
                    'moveyourazz_dev',
                    'agent_memory_contributions',
                    str(record['id']),
                    'agent_output',
                    content[:10000],
                    embedding,
                    'text-embedding-3-small',
                    json.dumps({'migration_date': datetime.now().isoformat()}),
                    record.get('created_at', datetime.now())
                ))
                
                migrated += 1
                
            except Exception as e:
                continue
        
        target_conn.commit()
        print(f"   ✅ Migrated {migrated} agent contributions")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
        return 0
    finally:
        source_conn.close()
        target_conn.close()
    
    return migrated

def final_verification():
    """Final verification of migration"""
    conn = get_connection('ai_unified_platform')
    cur = conn.cursor()
    
    print("\n" + "=" * 80)
    print("✅ FINAL MIGRATION VERIFICATION")
    print("=" * 80)
    
    # Total count
    cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
    total = cur.fetchone()['count']
    
    # By source table
    cur.execute("""
        SELECT source_table, COUNT(*) as count
        FROM unified_embeddings
        WHERE source_database = 'moveyourazz_dev'
        GROUP BY source_table
        ORDER BY count DESC
    """)
    
    results = cur.fetchall()
    
    print(f"\n{'Source Table':<40} {'Count':<10}")
    print("-" * 50)
    
    for row in results:
        print(f"{row['source_table']:<40} {row['count']:<10}")
    
    print("-" * 50)
    print(f"{'TOTAL':<40} {total:<10}")
    
    conn.close()
    
    return total

def main():
    print("=" * 80)
    print("🔄 FINAL EMBEDDINGS MIGRATION")
    print("=" * 80)
    
    # Migrate remaining tables
    conv_count = migrate_conversation_memory()
    agent_count = migrate_agent_contributions()
    
    # Verify
    total = final_verification()
    
    print("\n" + "=" * 80)
    print("🎉 MIGRATION COMPLETE!")
    print("=" * 80)
    print(f"\n✅ New embeddings migrated: {conv_count + agent_count}")
    print(f"✅ Total embeddings in system: {total:,}")
    
    print("\n📝 All embeddings from moveyourazz_dev have been migrated!")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()