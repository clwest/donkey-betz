#!/usr/bin/env python
"""
FINAL MIGRATION: Migrate remaining embeddings to ai_unified_platform

FINDINGS:
- memory_memoryentry: 29,856 records, 2,906 have embeddings (stored as LISTS, not JSONB)
- agent_memory_contributions: 661 records, NO embeddings (just metadata)
- unified_memory_searches: 208 records, NO embeddings (just timing data)

FOCUS: Only memory_memoryentry has actual embeddings to migrate
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import hashlib

# Target database configuration
TARGET_DATABASE = 'ai_unified_platform'
TARGET_USER = 'ai_unified_user'
TARGET_PASSWORD = '[REDACTED - HISTORICAL SECRET]'

def get_connection(database):
    """Get database connection"""
    if database == 'moveyourazz_dev':
        return psycopg2.connect(
            host='localhost',
            database='moveyourazz_dev',
            user='donkeyking',
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

def ensure_unified_embeddings_table():
    """Ensure the unified embeddings table exists in ai_unified_platform"""
    conn = get_connection(TARGET_DATABASE)
    cur = conn.cursor()
    
    try:
        # Check if pgvector extension exists
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        
        # Create the unified_embeddings table if it doesn't exist
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
        
        # Create indexes if they don't exist
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
        print(f"❌ Error creating table: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def generate_content_hash(content):
    """Generate hash for content deduplication"""
    if content:
        return hashlib.sha256(content.encode()).hexdigest()
    return None

def migrate_memory_memoryentry():
    """Migrate embeddings from memory_memoryentry table"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection(TARGET_DATABASE)
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        print(f"\n{'='*60}")
        print(f"MIGRATING: memory_memoryentry")
        print(f"{'='*60}")
        
        # Get total count and embedding count
        source_cur.execute("SELECT COUNT(*) as count FROM memory_memoryentry")
        total_records = source_cur.fetchone()['count']
        
        source_cur.execute("""
            SELECT COUNT(*) as count 
            FROM memory_memoryentry 
            WHERE embedding IS NOT NULL
        """)
        embedding_records = source_cur.fetchone()['count']
        
        print(f"📊 Total records: {total_records:,}")
        print(f"🎯 Records with embeddings: {embedding_records:,}")
        
        if embedding_records == 0:
            print("❌ No embeddings to migrate")
            return 0
        
        # Check if already migrated
        target_cur.execute("""
            SELECT COUNT(*) as count 
            FROM unified_embeddings 
            WHERE source_database = 'moveyourazz_dev' 
            AND source_table = 'memory_memoryentry'
        """)
        already_migrated = target_cur.fetchone()['count']
        
        if already_migrated > 0:
            print(f"⚠️  Found {already_migrated:,} already migrated records")
            print("   Will skip duplicates using ON CONFLICT")
        
        # Migrate in batches
        batch_size = 100
        offset = 0
        migrated = 0
        skipped = 0
        errors = 0
        
        while offset < total_records:
            # Get batch of records with embeddings
            source_cur.execute("""
                SELECT id, event, title, type, memory_type, importance, 
                       timestamp, embedding, user_id, summary,
                       source_type, confidence_score
                FROM memory_memoryentry 
                WHERE embedding IS NOT NULL
                ORDER BY timestamp
                LIMIT %s OFFSET %s
            """, (batch_size, offset))
            
            records = source_cur.fetchall()
            
            if not records:
                break
            
            for record in records:
                try:
                    embedding = record['embedding']
                    
                    # Validate embedding format
                    if not isinstance(embedding, list):
                        errors += 1
                        continue
                    
                    if len(embedding) != 1536:
                        print(f"      ⚠️  Invalid embedding size: {len(embedding)} (expected 1536)")
                        errors += 1
                        continue
                    
                    # Prepare content text
                    content_parts = []
                    if record['title']:
                        content_parts.append(f"Title: {record['title']}")
                    if record['event']:
                        content_parts.append(f"Event: {record['event']}")
                    if record['summary']:
                        content_parts.append(f"Summary: {record['summary']}")
                    
                    content_text = " | ".join(content_parts)
                    if len(content_text) > 10000:
                        content_text = content_text[:10000]
                    
                    # Prepare metadata
                    metadata = {
                        'memory_type': record['memory_type'],
                        'source_type': record['source_type'],
                        'user_id': record['user_id'],
                        'confidence_score': float(record['confidence_score']) if record['confidence_score'] else 0.5,
                        'original_timestamp': record['timestamp'].isoformat() if record['timestamp'] else None,
                        'migration_date': datetime.now().isoformat(),
                        'migration_batch': 'final_memory_migration'
                    }
                    
                    # Insert into unified_embeddings
                    target_cur.execute("""
                        INSERT INTO unified_embeddings (
                            source_database, source_table, source_id,
                            content_type, content_text, embedding,
                            embedding_model, metadata, importance_score,
                            content_hash
                        ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s)
                        ON CONFLICT (source_database, source_table, source_id) 
                        DO NOTHING
                    """, (
                        'moveyourazz_dev',
                        'memory_memoryentry',
                        str(record['id']),
                        record['type'] or 'memory',
                        content_text,
                        embedding,
                        'text-embedding-3-small',
                        json.dumps(metadata),
                        float(record['importance']) / 10.0 if record['importance'] else 0.5,
                        generate_content_hash(content_text)
                    ))
                    
                    # Check if record was actually inserted
                    if target_cur.rowcount > 0:
                        migrated += 1
                    else:
                        skipped += 1
                    
                except Exception as e:
                    errors += 1
                    if errors <= 3:  # Show first few errors
                        print(f"      ❌ Error processing record {record['id']}: {str(e)[:100]}")
                    continue
            
            # Commit batch
            target_conn.commit()
            
            # Progress update
            progress = ((offset + len(records)) / total_records) * 100
            print(f"      Progress: {progress:.1f}% | Migrated: {migrated:,} | Skipped: {skipped:,} | Errors: {errors:,}", end='\r')
            
            offset += batch_size
        
        print(f"\n\n✅ MIGRATION COMPLETE:")
        print(f"   📈 Migrated: {migrated:,} new records")
        print(f"   ⏭️  Skipped: {skipped:,} duplicates")
        print(f"   ❌ Errors: {errors:,}")
        
        return migrated
        
    except Exception as e:
        print(f"\n❌ Migration error: {str(e)}")
        target_conn.rollback()
        raise
    finally:
        source_conn.close()
        target_conn.close()

def verify_migration():
    """Verify the migration results"""
    conn = get_connection(TARGET_DATABASE)
    cur = conn.cursor()
    
    try:
        print(f"\n{'='*60}")
        print(f"MIGRATION VERIFICATION")
        print(f"{'='*60}")
        
        # Total embeddings count
        cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
        total_count = cur.fetchone()['count']
        print(f"\n📊 Total embeddings in {TARGET_DATABASE}: {total_count:,}")
        
        # Count by source database
        cur.execute("""
            SELECT source_database, COUNT(*) as count 
            FROM unified_embeddings 
            GROUP BY source_database 
            ORDER BY count DESC
        """)
        print(f"\n📚 By source database:")
        for row in cur.fetchall():
            print(f"   {row['source_database']:25} {row['count']:8,}")
        
        # Count by content type
        cur.execute("""
            SELECT content_type, COUNT(*) as count 
            FROM unified_embeddings 
            GROUP BY content_type 
            ORDER BY count DESC
        """)
        print(f"\n📋 By content type:")
        for row in cur.fetchall():
            print(f"   {row['content_type']:20} {row['count']:8,}")
        
        # Specific count for memory_memoryentry
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM unified_embeddings 
            WHERE source_database = 'moveyourazz_dev' 
            AND source_table = 'memory_memoryentry'
        """)
        memory_count = cur.fetchone()['count']
        print(f"\n🎯 memory_memoryentry embeddings: {memory_count:,}")
        
        # Sample recent migration
        cur.execute("""
            SELECT source_table, content_type, content_text, 
                   LEFT(content_text, 100) as preview
            FROM unified_embeddings 
            WHERE source_database = 'moveyourazz_dev' 
            AND source_table = 'memory_memoryentry'
            ORDER BY migrated_at DESC 
            LIMIT 3
        """)
        
        print(f"\n📝 Sample migrated records:")
        for i, row in enumerate(cur.fetchall(), 1):
            print(f"   {i}. [{row['content_type']}] {row['preview']}...")
        
        return total_count
        
    finally:
        conn.close()

def main():
    print("=" * 80)
    print("🔥 FINAL EMBEDDINGS MIGRATION TO AI_UNIFIED_PLATFORM")
    print("=" * 80)
    print(f"\n🎯 Target Database: {TARGET_DATABASE}")
    print(f"📅 Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📋 MIGRATION PLAN:")
    print(f"   ✅ memory_memoryentry: ~2,906 embeddings (LIST format)")
    print(f"   ❌ agent_memory_contributions: No embeddings (just metadata)")
    print(f"   ❌ unified_memory_searches: No embeddings (just timing data)")
    
    # Ensure target table exists
    ensure_unified_embeddings_table()
    
    # Current status
    conn = get_connection(TARGET_DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
    current_count = cur.fetchone()['count']
    print(f"\n📊 Current embeddings in {TARGET_DATABASE}: {current_count:,}")
    conn.close()
    
    # Execute migration
    print(f"\n🚀 STARTING MIGRATION...")
    
    try:
        migrated_count = migrate_memory_memoryentry()
        
        # Final verification
        final_count = verify_migration()
        
        print(f"\n{'='*80}")
        print(f"🎉 MIGRATION SUCCESSFUL!")
        print(f"{'='*80}")
        print(f"\n✅ New embeddings migrated: {migrated_count:,}")
        print(f"✅ Total embeddings available: {final_count:,}")
        print(f"✅ Database: {TARGET_DATABASE}")
        print(f"\n🎯 All embeddings are now consolidated and ready for use!")
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)