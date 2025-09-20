#!/usr/bin/env python3
"""
Simple migration of remaining unified_memory_entries
"""

import psycopg2
from psycopg2.extras import execute_batch
import hashlib

def migrate_remaining():
    print("🚀 Migrating remaining unified_memory_entries...")
    
    # Connect to databases
    source_conn = psycopg2.connect('postgresql://postgres@localhost/moveyourazz_dev')
    target_conn = psycopg2.connect('postgresql://ai_unified_user@localhost/ai_unified_platform')
    
    # First check what's already migrated
    with target_conn.cursor() as target_cur:
        target_cur.execute("""
            SELECT CAST(source_id AS INTEGER) 
            FROM unified_embeddings 
            WHERE source_table = 'unified_memory_entries'
              AND source_id ~ '^[0-9]+$'
        """)
        migrated_ids = set(row[0] for row in target_cur.fetchall())
        print(f"Already migrated {len(migrated_ids)} records")
    
    # Get records not yet migrated
    with source_conn.cursor() as source_cur:
        if migrated_ids:
            placeholders = ','.join(['%s'] * len(migrated_ids))
            source_cur.execute(f"""
                SELECT id, content_text, embedding, created_at, importance_score, title, summary
                FROM unified_memory_entries 
                WHERE content_text IS NOT NULL 
                  AND embedding IS NOT NULL
                  AND id NOT IN ({placeholders})
                ORDER BY id
                LIMIT 25000
            """, list(migrated_ids))
        else:
            source_cur.execute("""
                SELECT id, content_text, embedding, created_at, importance_score, title, summary
                FROM unified_memory_entries 
                WHERE content_text IS NOT NULL 
                  AND embedding IS NOT NULL
                ORDER BY id
                LIMIT 25000
            """)
        
        records = source_cur.fetchall()
        print(f"Found {len(records)} records to migrate")
        
        if not records:
            print("✅ No new records to migrate")
            return
        
        # Prepare data
        insert_data = []
        for record in records:
            record_id, content_text, embedding, created_at, importance_score, title, summary = record
            
            content_hash = hashlib.md5(str(content_text).encode()).hexdigest()
            
            import json
            insert_data.append((
                'moveyourazz_dev',
                'unified_memory_entries', 
                str(record_id),
                'unified_memory',
                str(content_text)[:2000] if content_text else '',
                embedding,
                'text-embedding-ada-002',
                json.dumps({'title': title, 'summary': summary}),
                importance_score or 0.5,
                content_hash
            ))
        
        # Insert to target
        with target_conn.cursor() as target_cur:
            insert_query = """
                INSERT INTO unified_embeddings (
                    source_database, source_table, source_id, content_type,
                    content_text, embedding, embedding_model, metadata,
                    importance_score, content_hash, created_at, migrated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """
            
            execute_batch(target_cur, insert_query, insert_data, page_size=1000)
            target_conn.commit()
            
            # Check final count
            target_cur.execute("SELECT COUNT(*) FROM unified_embeddings")
            total = target_cur.fetchone()[0]
            print(f"✅ Total embeddings now: {total:,}")
    
    source_conn.close()
    target_conn.close()

if __name__ == "__main__":
    migrate_remaining()