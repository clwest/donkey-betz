#!/usr/bin/env python3
"""
Migrate ONLY the 56 code embeddings to the correct Django database
"""

import psycopg2
import json
from psycopg2.extras import execute_batch
from tqdm import tqdm

def migrate_code_embeddings_only():
    """Copy only code embeddings to Django database"""
    
    print("\n" + "="*80)
    print("💻 MIGRATING CODE EMBEDDINGS ONLY")
    print("="*80)
    print("Moving 56 code embeddings to ai_unified_platform")
    
    # Connect to both databases
    source_conn = psycopg2.connect('postgresql://postgres@localhost/unified_donkey_betz')
    target_conn = psycopg2.connect('postgresql://ai_unified_user@localhost/ai_unified_platform')
    
    try:
        # First, create the unified_embeddings table in target if it doesn't exist
        print("\n📋 Creating target table structure...")
        with target_conn.cursor() as cur:
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
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    migrated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    content_hash VARCHAR(64),
                    UNIQUE(source_database, source_table, source_id)
                );
            """)
            
            # Create indexes
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_unified_embeddings_content_type 
                ON unified_embeddings(content_type);
                
                CREATE INDEX IF NOT EXISTS idx_unified_embeddings_source 
                ON unified_embeddings(source_database, source_table);
                
                CREATE INDEX IF NOT EXISTS idx_unified_embeddings_embedding_vector
                ON unified_embeddings USING hnsw (embedding vector_cosine_ops)
                WHERE embedding IS NOT NULL;
            """)
            
            target_conn.commit()
            print("   ✅ Target table ready")
        
        # Get ONLY code embeddings from source database
        print("\n📦 Fetching CODE embeddings from source database...")
        with source_conn.cursor() as source_cur:
            source_cur.execute("""
                SELECT source_database, source_table, source_id, content_type,
                       content_text, embedding, embedding_model, metadata,
                       importance_score, content_hash, created_at
                FROM unified_embeddings 
                WHERE source_table = 'ai_partner_codeembedding'
                ORDER BY id
            """)
            
            embeddings = source_cur.fetchall()
            print(f"   Found {len(embeddings)} code embeddings to migrate")
            
            if not embeddings:
                print("   ⚠️  No code embeddings found!")
                return 0
        
        # Process embeddings to handle metadata issues
        print(f"\n🔧 Processing embeddings...")
        processed_embeddings = []
        
        for embedding in tqdm(embeddings, desc="   Processing"):
            source_db, source_table, source_id, content_type, content_text, \
            embedding_vector, embedding_model, metadata, importance_score, \
            content_hash, created_at = embedding
            
            # Handle metadata safely
            try:
                if metadata is None:
                    safe_metadata = {}
                elif isinstance(metadata, str):
                    # If it's a string that looks encrypted/binary, skip it
                    if metadata.startswith('gAAAAA'):
                        safe_metadata = {'original_metadata': 'encrypted_data_skipped'}
                    else:
                        # Try to parse as JSON
                        try:
                            safe_metadata = json.loads(metadata)
                        except:
                            safe_metadata = {'raw_metadata': metadata[:100]}  # Truncate if problematic
                elif isinstance(metadata, dict):
                    safe_metadata = metadata
                else:
                    safe_metadata = {'metadata_type': str(type(metadata))}
            except Exception as e:
                safe_metadata = {'metadata_error': str(e)[:100]}
            
            processed_embeddings.append((
                source_db, source_table, source_id, content_type,
                content_text, embedding_vector, embedding_model,
                json.dumps(safe_metadata),  # Ensure it's JSON string
                importance_score, content_hash, created_at
            ))
        
        # Insert into target database
        print(f"\n💾 Inserting {len(processed_embeddings)} code embeddings...")
        
        with target_conn.cursor() as target_cur:
            insert_query = """
                INSERT INTO unified_embeddings (
                    source_database, source_table, source_id, content_type,
                    content_text, embedding, embedding_model, metadata,
                    importance_score, content_hash, created_at, migrated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                ) ON CONFLICT (source_database, source_table, source_id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    importance_score = EXCLUDED.importance_score,
                    content_hash = EXCLUDED.content_hash,
                    migrated_at = NOW()
            """
            
            execute_batch(target_cur, insert_query, processed_embeddings, page_size=10)
            target_conn.commit()
        
        # Verify migration
        print(f"\n🔍 Verifying migration...")
        with target_conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM unified_embeddings 
                WHERE source_table = 'ai_partner_codeembedding'
            """)
            code_count = cur.fetchone()[0]
            
            cur.execute("""
                SELECT content_type, COUNT(*) 
                FROM unified_embeddings 
                WHERE source_table = 'ai_partner_codeembedding'
                GROUP BY content_type
            """)
            breakdown = cur.fetchall()
            
            print(f"   💻 Code embeddings migrated: {code_count}")
            print(f"   📋 Breakdown:")
            for content_type, count in breakdown:
                print(f"      • {content_type}: {count}")
            
        print(f"\n" + "="*80)
        print("✅ CODE MIGRATION COMPLETE!")
        print("="*80)
        print(f"""
Django will now find the code embeddings at:
📍 Database: ai_unified_platform
📍 Table: unified_embeddings
💻 Code embeddings: {code_count}

Test with: python test_code_embeddings.py
""")
        
        return code_count
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        source_conn.close()
        target_conn.close()

def main():
    migrate_code_embeddings_only()

if __name__ == "__main__":
    main()