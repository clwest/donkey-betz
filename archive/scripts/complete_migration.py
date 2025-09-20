#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import execute_batch
import json
import hashlib

def migrate_conversation_embeddings():
    source_conn = psycopg2.connect(
        dbname="moveyourazz_dev",
        user="donkeyking",
        host="localhost",
        port=5432
    )
    
    target_conn = psycopg2.connect(
        dbname="ai_unified_platform",
        user="donkeyking",
        host="localhost",
        port=5432
    )
    
    try:
        source_conn.autocommit = False
        target_conn.autocommit = False
        
        with source_conn.cursor() as src_cur:
            with target_conn.cursor() as tgt_cur:
                # Count total source records
                src_cur.execute("SELECT COUNT(*) FROM ai_partner_conversationembedding")
                total_source = src_cur.fetchone()[0]
                print(f"Total source records: {total_source}")
                
                # Count migrated records
                tgt_cur.execute("""
                    SELECT COUNT(*) FROM shared.shared_embeddings 
                    WHERE source_platform = 'studio' 
                    AND source_table = 'ai_partner_conversationembedding'
                """)
                migrated = tgt_cur.fetchone()[0]
                print(f"Already migrated: {migrated}")
                
                if migrated >= total_source:
                    print("Migration already complete!")
                    return
                
                # Get last migrated ID
                tgt_cur.execute("""
                    SELECT MAX(source_id) 
                    FROM shared.shared_embeddings 
                    WHERE source_platform = 'studio'
                    AND source_table = 'ai_partner_conversationembedding'
                """)
                last_id = tgt_cur.fetchone()[0] or 0
                print(f"Continuing from ID: {last_id}")
                
                # Migrate in small batches
                batch_size = 50  # Even smaller batches to avoid disk issues
                migrated_count = 0
                
                while True:
                    src_cur.execute("""
                        SELECT 
                            id, chunk_text, chunk_index, embedding,
                            topics, entities, sentiment, importance_score,
                            conversation_timestamp, created_at, conversation_id,
                            speaker, conversation_type, conversation_phase,
                            mentioned_agents, mentioned_features, mentioned_people
                        FROM ai_partner_conversationembedding
                        WHERE id > %s
                        ORDER BY id
                        LIMIT %s
                    """, (last_id, batch_size))
                    
                    batch = src_cur.fetchall()
                    if not batch:
                        break
                    
                    insert_data = []
                    for row in batch:
                        # Generate content hash
                        content_hash = hashlib.sha256(row[1].encode()).hexdigest()
                        
                        # Build metadata
                        metadata = {
                            'chunk_index': row[2],
                            'topics': row[4],
                            'entities': row[5],
                            'sentiment': row[6],
                            'importance_score': row[7],
                            'conversation_timestamp': row[8].isoformat() if row[8] else None,
                            'conversation_id': str(row[10]) if row[10] else None,
                            'speaker': row[11],
                            'conversation_type': row[12],
                            'conversation_phase': row[13],
                            'mentioned_agents': row[14],
                            'mentioned_features': row[15],
                            'mentioned_people': row[16]
                        }
                        
                        insert_data.append((
                            content_hash,                        # content_hash
                            row[1],                              # content_text (chunk_text)
                            row[3],                              # embedding vector
                            'conversation',                      # content_type
                            'studio',                            # source_platform
                            'ai_partner_conversationembedding', # source_table
                            row[0],                              # source_id
                            row[9],                              # created_at
                            json.dumps(metadata)                # metadata as JSON
                        ))
                        last_id = row[0]
                    
                    # Insert batch
                    insert_query = """
                        INSERT INTO shared.shared_embeddings 
                        (content_hash, content_text, embedding, content_type, 
                         source_platform, source_table, source_id, created_at, metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                        ON CONFLICT (content_hash) DO NOTHING
                    """
                    
                    execute_batch(tgt_cur, insert_query, insert_data, page_size=10)
                    target_conn.commit()
                    
                    migrated_count += len(batch)
                    if migrated_count % 1000 == 0:
                        print(f"Migrated {migrated_count} records...")
                
                print(f"Migration complete! Total migrated: {migrated_count}")
                
    except Exception as e:
        print(f"Error: {e}")
        source_conn.rollback()
        target_conn.rollback()
        raise
    finally:
        source_conn.close()
        target_conn.close()

if __name__ == "__main__":
    migrate_conversation_embeddings()
