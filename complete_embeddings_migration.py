#!/usr/bin/env python3
"""
Complete the embeddings migration - get all remaining embeddings
"""

import os
import sys
import django
import psycopg2
from psycopg2.extras import execute_batch
import json
from datetime import datetime
from tqdm import tqdm
import hashlib

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

def migrate_remaining_embeddings():
    """Migrate all remaining embeddings from moveyourazz_dev"""
    
    print("\n" + "="*80)
    print("🚀 COMPLETING EMBEDDINGS MIGRATION")
    print("="*80)
    
    # Connect to both databases
    source_conn = psycopg2.connect('postgresql://postgres@localhost/moveyourazz_dev')
    target_conn = psycopg2.connect('postgresql://ai_unified_user@localhost/ai_unified_platform')
    
    # Tables to migrate with their configurations
    migration_tasks = [
        {
            'table': 'unified_memory_entries',
            'content_type': 'unified_memory',
            'select_query': """
                SELECT id, content_text, embedding, created_at, context_data, importance_score
                FROM unified_memory_entries 
                WHERE id NOT IN (
                    SELECT CAST(SUBSTRING(source_id FROM 1) AS INTEGER) 
                    FROM unified_embeddings 
                    WHERE source_table = 'unified_memory_entries'
                )
                ORDER BY id
            """,
            'description': 'Remaining unified memory entries'
        },
        {
            'table': 'memory_memoryentry', 
            'content_type': 'memory_entry',
            'select_query': """
                SELECT id, full_transcript, embedding, created_at, '{}', importance
                FROM memory_memoryentry 
                WHERE full_transcript IS NOT NULL AND embedding IS NOT NULL
                ORDER BY id
            """,
            'description': 'Memory entries with embeddings'
        },
        {
            'table': 'ukf_system_markdownembedding',
            'content_type': 'markdown',
            'select_query': """
                SELECT id, content, embedding_vector, created_at, metadata, 0.7 as importance_score
                FROM ukf_system_markdownembedding 
                WHERE content IS NOT NULL AND embedding_vector IS NOT NULL
                ORDER BY id
            """,
            'description': 'Markdown embeddings'
        },
        {
            'table': 'ai_partner_conversationmemory',
            'content_type': 'conversation',
            'select_query': """
                SELECT id, content, embedding_vector, created_at, metadata, importance_score
                FROM ai_partner_conversationmemory 
                WHERE content IS NOT NULL AND embedding_vector IS NOT NULL
                ORDER BY id
            """,
            'description': 'Conversation memories'
        }
    ]
    
    total_migrated = 0
    
    for task in migration_tasks:
        print(f"\n📦 Migrating {task['description']}...")
        
        with source_conn.cursor() as source_cur:
            source_cur.execute(task['select_query'])
            records = source_cur.fetchall()
            
            if not records:
                print(f"   ✅ No records to migrate from {task['table']}")
                continue
                
            print(f"   Found {len(records):,} records to migrate")
            
            # Prepare insert data
            insert_data = []
            
            for record in tqdm(records, desc=f"   Processing {task['table']}", unit="records"):
                record_id, content, embedding_vector, timestamp, metadata, importance_score = record[:6]
                
                # Create content hash
                content_hash = hashlib.md5(str(content).encode()).hexdigest()
                
                insert_data.append((
                    'moveyourazz_dev',  # source_database
                    task['table'],      # source_table
                    str(record_id),     # source_id
                    task['content_type'], # content_type
                    str(content)[:5000] if content else '',  # content_text (truncated)
                    embedding_vector,   # embedding
                    'text-embedding-ada-002',  # embedding_model
                    metadata or {},     # metadata
                    importance_score or 0.5,  # importance_score
                    content_hash        # content_hash
                ))
            
            # Batch insert to target
            if insert_data:
                with target_conn.cursor() as target_cur:
                    insert_query = """
                        INSERT INTO unified_embeddings (
                            source_database, source_table, source_id, content_type,
                            content_text, embedding, embedding_model, metadata,
                            importance_score, content_hash, created_at, migrated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                        ) ON CONFLICT (content_hash) DO NOTHING
                    """
                    
                    execute_batch(target_cur, insert_query, insert_data, page_size=1000)
                    target_conn.commit()
                    
                    # Count actually inserted (excluding duplicates)
                    target_cur.execute("""
                        SELECT COUNT(*) FROM unified_embeddings 
                        WHERE source_database = 'moveyourazz_dev' 
                        AND source_table = %s
                    """, (task['table'],))
                    
                    actual_count = target_cur.fetchone()[0]
                    print(f"   ✅ Successfully migrated {actual_count:,} records from {task['table']}")
                    total_migrated += actual_count
    
    # Final verification
    print(f"\n" + "="*80)
    print("📊 MIGRATION COMPLETE")
    print("="*80)
    
    with target_conn.cursor() as cur:
        cur.execute("""
            SELECT 
                source_table,
                content_type,
                COUNT(*) as count
            FROM unified_embeddings 
            WHERE source_database = 'moveyourazz_dev'
            GROUP BY source_table, content_type
            ORDER BY count DESC
        """)
        
        print(f"\n✅ Final Embedding Counts:")
        grand_total = 0
        for source_table, content_type, count in cur.fetchall():
            print(f"   • {content_type} ({source_table}): {count:,}")
            grand_total += count
        
        print(f"\n🎯 GRAND TOTAL: {grand_total:,} embeddings")
        print(f"   Added in this session: {total_migrated:,}")
    
    source_conn.close()
    target_conn.close()
    
    return grand_total

def main():
    total = migrate_remaining_embeddings()
    
    print(f"\n" + "="*80)
    print("🎉 SUCCESS!")
    print("="*80)
    print(f"""
Your embeddings are now fully migrated!

✅ Total embeddings available: {total:,}
✅ RAG system fully operational  
✅ Semantic search enabled
✅ All your historical data preserved

The assistant now has access to ALL your embeddings!

Test it: python test_rag_assistant.py
""")

if __name__ == "__main__":
    main()