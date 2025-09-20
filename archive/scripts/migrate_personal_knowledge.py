#!/usr/bin/env python3
import psycopg2
from psycopg2.extras import execute_batch
import json
import hashlib
from datetime import datetime

def migrate_personal_knowledge():
    source_conn = psycopg2.connect(
        dbname="ai_content_studio",
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
                # Get user ID for chris
                tgt_cur.execute("SELECT id FROM auth_user WHERE username = 'chris'")
                chris_user_id = tgt_cur.fetchone()[0]
                print(f"Using user 'chris' with ID: {chris_user_id}")
                
                # Count total source records
                src_cur.execute("SELECT COUNT(*) FROM content_personalknowledge")
                total_source = src_cur.fetchone()[0]
                print(f"Total personal knowledge records to migrate: {total_source}")
                
                # Check already migrated
                tgt_cur.execute("""
                    SELECT COUNT(*) FROM shared.shared_embeddings 
                    WHERE source_platform = 'studio' 
                    AND source_table = 'content_personalknowledge'
                """)
                already_migrated = tgt_cur.fetchone()[0]
                print(f"Already migrated: {already_migrated}")
                
                # Get personal knowledge data
                src_cur.execute("""
                    SELECT 
                        id, 
                        title,
                        description,
                        content,
                        content_type,
                        file_type,
                        category,
                        tags,
                        original_filename,
                        file_url,
                        metadata,
                        created_at,
                        updated_at,
                        user_id,
                        embedding_generated
                    FROM content_personalknowledge
                    ORDER BY id
                """)
                
                records = src_cur.fetchall()
                print(f"Fetched {len(records)} records from source")
                
                migrated_count = 0
                insert_data = []
                
                for row in records:
                    # Generate content hash from title + description + content
                    content_text = f"{row[1] or ''}\n{row[2] or ''}\n{row[3] or ''}"
                    content_hash = hashlib.sha256(content_text.encode()).hexdigest()
                    
                    # Build metadata
                    metadata = {
                        'title': row[1],
                        'description': row[2],
                        'content_type': row[4],
                        'file_type': row[5],
                        'category': row[6],
                        'tags': row[7],
                        'original_filename': row[8],
                        'file_url': row[9],
                        'original_metadata': row[10],
                        'original_user_id': row[13],
                        'embedding_generated': row[14],
                        'updated_at': row[12].isoformat() if row[12] else None
                    }
                    
                    # Create a zero vector for now (will need to generate real embeddings later)
                    zero_embedding = '[' + ','.join(['0'] * 1536) + ']'
                    
                    insert_data.append((
                        content_hash,                        # content_hash
                        content_text,                        # content_text
                        zero_embedding,                      # embedding vector (zero for now)
                        'personal_knowledge',                # content_type
                        'studio',                            # source_platform
                        'content_personalknowledge',         # source_table
                        str(row[0]),                         # source_id (convert UUID to string)
                        row[11],                             # created_at
                        json.dumps(metadata),                # metadata as JSON
                        chris_user_id                        # user_id (chris)
                    ))
                
                # Insert all records with user_id
                if insert_data:
                    insert_query = """
                        INSERT INTO shared.shared_embeddings 
                        (content_hash, content_text, embedding, content_type, 
                         source_platform, source_table, source_id, created_at, metadata, user_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                        ON CONFLICT (content_hash) DO UPDATE SET
                            user_id = EXCLUDED.user_id,
                            metadata = EXCLUDED.metadata,
                            updated_at = CURRENT_TIMESTAMP
                    """
                    
                    # Process in batches
                    batch_size = 50
                    for i in range(0, len(insert_data), batch_size):
                        batch = insert_data[i:i+batch_size]
                        execute_batch(tgt_cur, insert_query, batch, page_size=10)
                        target_conn.commit()
                        migrated_count += len(batch)
                        print(f"Migrated {migrated_count}/{len(records)} records...")
                
                print(f"\nMigration complete! Total migrated: {migrated_count}")
                
                # Verify migration
                tgt_cur.execute("""
                    SELECT COUNT(*) FROM shared.shared_embeddings 
                    WHERE source_platform = 'studio' 
                    AND source_table = 'content_personalknowledge'
                    AND user_id = %s
                """, (chris_user_id,))
                final_count = tgt_cur.fetchone()[0]
                print(f"Verified: {final_count} records now associated with user 'chris'")
                
    except Exception as e:
        print(f"Error: {e}")
        source_conn.rollback()
        target_conn.rollback()
        raise
    finally:
        source_conn.close()
        target_conn.close()

if __name__ == "__main__":
    migrate_personal_knowledge()