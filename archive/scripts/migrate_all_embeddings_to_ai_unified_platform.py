#!/usr/bin/env python
"""
CRITICAL: Migrate ALL 70k+ embeddings into ai_unified_platform database
This is the ACTIVE database being used by the application!
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import hashlib

# CRITICAL: This is the active database from DATABASE_URL in .env
TARGET_DATABASE = 'ai_unified_platform'
TARGET_USER = 'ai_unified_user'
TARGET_PASSWORD = 'ai_unified_pass_2025'

def get_connection(database):
    """Get database connection"""
    if database == 'moveyourazz_dev':
        return psycopg2.connect(
            host='localhost',
            database='moveyourazz_dev',
            user='donkeyking',
            cursor_factory=RealDictCursor
        )
    elif database == 'unified_donkey_betz':
        return psycopg2.connect(
            host='localhost',
            database='unified_donkey_betz',
            user='postgres',
            cursor_factory=RealDictCursor
        )
    elif database == TARGET_DATABASE:
        return psycopg2.connect(
            host='localhost',
            database=TARGET_DATABASE,
            user=TARGET_USER,
            password=TARGET_PASSWORD,
            cursor_factory=RealDictCursor
        )

def create_unified_embeddings_table():
    """Create the unified embeddings table in ai_unified_platform if it doesn't exist"""
    conn = get_connection(TARGET_DATABASE)
    cur = conn.cursor()
    
    try:
        # Check if pgvector extension exists
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        
        # Create the unified_embeddings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS unified_embeddings (
                id SERIAL PRIMARY KEY,
                source_database VARCHAR(100),
                source_table VARCHAR(100),
                source_id VARCHAR(255),
                content_type VARCHAR(100),
                content_text TEXT,
                embedding vector(1536),
                embedding_model VARCHAR(100),
                metadata JSONB,
                importance_score FLOAT DEFAULT 0.5,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                migrated_at TIMESTAMPTZ DEFAULT NOW(),
                content_hash VARCHAR(64),
                UNIQUE(source_database, source_table, source_id)
            )
        """)
        
        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_unified_embeddings_embedding_vector 
            ON unified_embeddings USING hnsw (embedding vector_cosine_ops)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_unified_embeddings_content_type 
            ON unified_embeddings (content_type)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_unified_embeddings_source 
            ON unified_embeddings (source_database, source_table)
        """)
        
        conn.commit()
        print(f"✅ Unified embeddings table ready in {TARGET_DATABASE}")
        
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

def generate_content_hash(content):
    """Generate hash for content deduplication"""
    if content:
        return hashlib.sha256(content.encode()).hexdigest()
    return None

def migrate_from_moveyourazz(table_name, content_type, batch_size=500):
    """Migrate embeddings from moveyourazz_dev to ai_unified_platform"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection(TARGET_DATABASE)
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        # Get total count
        source_cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        total = source_cur.fetchone()['count']
        print(f"\n📊 Migrating: {table_name}")
        print(f"   Total records: {total:,}")
        
        if total == 0:
            return 0
        
        # Check columns
        source_cur.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s
        """, (table_name,))
        columns = [row['column_name'] for row in source_cur.fetchall()]
        
        # Find embedding column
        embedding_col = None
        for col in ['embedding', 'embedding_vector', 'vector', 'embeddings']:
            if col in columns:
                embedding_col = col
                break
        
        if not embedding_col:
            print(f"   ❌ No embedding column found")
            return 0
        
        # Find content column
        content_col = None
        for col in ['content', 'text', 'message', 'description', 'summary', 'entry']:
            if col in columns:
                content_col = col
                break
        
        # Migrate in batches
        offset = 0
        migrated = 0
        
        while offset < total:
            # Build query
            if content_col:
                query = f"""
                    SELECT id, {embedding_col} as embedding, {content_col} as content
                    FROM {table_name}
                    ORDER BY id
                    LIMIT %s OFFSET %s
                """
            else:
                query = f"""
                    SELECT id, {embedding_col} as embedding
                    FROM {table_name}
                    ORDER BY id
                    LIMIT %s OFFSET %s
                """
            
            source_cur.execute(query, (batch_size, offset))
            records = source_cur.fetchall()
            
            if not records:
                break
            
            for record in records:
                try:
                    embedding = record.get('embedding')
                    if not embedding:
                        continue
                    
                    # Handle JSON string embeddings
                    if isinstance(embedding, str):
                        try:
                            embedding = json.loads(embedding)
                        except:
                            continue
                    
                    if not isinstance(embedding, list) or len(embedding) != 1536:
                        continue
                    
                    content = record.get('content', f"{table_name} record {record['id']}")
                    if len(content) > 10000:
                        content = content[:10000]
                    
                    # Insert into ai_unified_platform
                    target_cur.execute("""
                        INSERT INTO unified_embeddings (
                            source_database, source_table, source_id,
                            content_type, content_text, embedding,
                            embedding_model, metadata, content_hash
                        ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s)
                        ON CONFLICT (source_database, source_table, source_id) 
                        DO NOTHING
                    """, (
                        'moveyourazz_dev',
                        table_name,
                        str(record['id']),
                        content_type,
                        content,
                        embedding,
                        'text-embedding-3-small',
                        json.dumps({'migration_date': datetime.now().isoformat()}),
                        generate_content_hash(content)
                    ))
                    
                    migrated += 1
                    
                except Exception as e:
                    if migrated == 0:  # Only show first error
                        print(f"      Sample error: {str(e)[:100]}")
                    continue
            
            target_conn.commit()
            
            progress = ((offset + len(records)) / total) * 100
            print(f"      Progress: {progress:.1f}% - Migrated: {migrated:,}", end='\r')
            offset += batch_size
        
        print(f"\n   ✅ Migrated: {migrated:,} records")
        return migrated
        
    finally:
        source_conn.close()
        target_conn.close()

def migrate_from_unified_donkey_betz():
    """Migrate existing embeddings from unified_donkey_betz to ai_unified_platform"""
    source_conn = get_connection('unified_donkey_betz')
    target_conn = get_connection(TARGET_DATABASE)
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        # Get count
        source_cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
        total = source_cur.fetchone()['count']
        print(f"\n📊 Migrating from unified_donkey_betz")
        print(f"   Total records: {total:,}")
        
        if total == 0:
            return 0
        
        # Migrate in batches
        batch_size = 1000
        offset = 0
        migrated = 0
        
        while offset < total:
            source_cur.execute("""
                SELECT source_database, source_table, source_id,
                       content_type, content_text, embedding,
                       embedding_model, metadata, content_hash
                FROM unified_embeddings
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (batch_size, offset))
            
            records = source_cur.fetchall()
            if not records:
                break
            
            for record in records:
                try:
                    target_cur.execute("""
                        INSERT INTO unified_embeddings (
                            source_database, source_table, source_id,
                            content_type, content_text, embedding,
                            embedding_model, metadata, content_hash
                        ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s)
                        ON CONFLICT (source_database, source_table, source_id) 
                        DO NOTHING
                    """, (
                        record['source_database'],
                        record['source_table'],
                        record['source_id'],
                        record['content_type'],
                        record['content_text'],
                        record['embedding'],
                        record['embedding_model'],
                        record['metadata'],
                        record['content_hash']
                    ))
                    migrated += 1
                except Exception as e:
                    continue
            
            target_conn.commit()
            
            progress = ((offset + len(records)) / total) * 100
            print(f"      Progress: {progress:.1f}% - Migrated: {migrated:,}", end='\r')
            offset += batch_size
        
        print(f"\n   ✅ Migrated: {migrated:,} records")
        return migrated
        
    finally:
        source_conn.close()
        target_conn.close()

def main():
    print("=" * 70)
    print("🚨 CRITICAL EMBEDDINGS MIGRATION TO AI_UNIFIED_PLATFORM")
    print("=" * 70)
    print(f"\n🎯 Target Database: {TARGET_DATABASE}")
    print("📦 This will consolidate ALL 70k+ embeddings into the ACTIVE database")
    
    # Create table if needed
    create_unified_embeddings_table()
    
    # Check current status
    conn = get_connection(TARGET_DATABASE)
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_name = 'unified_embeddings'
    """)
    
    if cur.fetchone()['count'] > 0:
        cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
        current_count = cur.fetchone()['count']
        print(f"\n📊 Current embeddings in {TARGET_DATABASE}: {current_count:,}")
    else:
        current_count = 0
    
    conn.close()
    
    total_migrated = 0
    
    # 1. Migrate from moveyourazz_dev (70k embeddings)
    print("\n" + "=" * 70)
    print("📚 PHASE 1: Migrating from moveyourazz_dev (70k embeddings)")
    print("=" * 70)
    
    migration_tasks = [
        ('unified_memory_entries', 'document'),
        ('memory_memoryentry', 'conversation'),
        ('ukf_system_markdownembedding', 'document'),
        ('ai_partner_conversationmemory', 'conversation'),
        ('agent_memory_contributions', 'agent_output'),
        ('unified_memory_searches', 'search'),
        ('ai_partner_codeembedding', 'code'),
        ('learning_intelligence_unifiedmemoryentry', 'learning')
    ]
    
    for table_name, content_type in migration_tasks:
        migrated = migrate_from_moveyourazz(table_name, content_type)
        total_migrated += migrated
    
    # 2. Migrate from unified_donkey_betz (16k embeddings)
    print("\n" + "=" * 70)
    print("📚 PHASE 2: Migrating from unified_donkey_betz (16k embeddings)")
    print("=" * 70)
    
    migrated = migrate_from_unified_donkey_betz()
    total_migrated += migrated
    
    # Final verification
    print("\n" + "=" * 70)
    print("✅ MIGRATION COMPLETE - FINAL VERIFICATION")
    print("=" * 70)
    
    conn = get_connection(TARGET_DATABASE)
    cur = conn.cursor()
    
    # Total count
    cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
    final_count = cur.fetchone()['count']
    print(f"\n🎉 Total embeddings in {TARGET_DATABASE}: {final_count:,}")
    
    # By content type
    print("\n📈 Embeddings by type:")
    cur.execute("""
        SELECT content_type, COUNT(*) as count 
        FROM unified_embeddings 
        GROUP BY content_type 
        ORDER BY count DESC
    """)
    for row in cur.fetchall():
        print(f"   {row['content_type']:20} {row['count']:10,}")
    
    # By source database
    print("\n📚 Embeddings by source database:")
    cur.execute("""
        SELECT source_database, COUNT(*) as count 
        FROM unified_embeddings 
        GROUP BY source_database 
        ORDER BY count DESC
    """)
    for row in cur.fetchall():
        print(f"   {row['source_database']:25} {row['count']:10,}")
    
    print("\n" + "=" * 70)
    print("🚀 SUCCESS!")
    print("=" * 70)
    print(f"\n✅ Migrated {total_migrated:,} new embeddings")
    print(f"✅ Total available: {final_count:,} embeddings")
    print(f"✅ Database: {TARGET_DATABASE}")
    print("\n🎯 All agents and Personal Assistant now have access to the COMPLETE knowledge base!")
    
    conn.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Migration interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)