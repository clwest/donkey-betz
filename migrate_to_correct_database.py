#!/usr/bin/env python3
"""
Migrate code embeddings from unified_donkey_betz to ai_unified_platform 
(the database Django is configured to use)
"""

import psycopg2
from psycopg2.extras import execute_batch
from tqdm import tqdm

def migrate_to_correct_database():
    """Copy embeddings to the correct database"""
    
    print("\n" + "="*80)
    print("🔄 MIGRATING TO CORRECT DATABASE")
    print("="*80)
    print("Moving embeddings from unified_donkey_betz → ai_unified_platform")
    
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
        
        # Get all embeddings from source database
        print("\n📦 Fetching embeddings from source database...")
        with source_conn.cursor() as source_cur:
            source_cur.execute("""
                SELECT source_database, source_table, source_id, content_type,
                       content_text, embedding, embedding_model, 
                       CASE 
                           WHEN metadata IS NULL THEN '{}'::jsonb
                           WHEN metadata::text LIKE 'gAAAAA%' THEN '{}'::jsonb  -- Skip encrypted/binary data
                           ELSE metadata 
                       END as metadata,
                       importance_score, content_hash, created_at
                FROM unified_embeddings 
                ORDER BY id
            """)
            
            embeddings = source_cur.fetchall()
            print(f"   Found {len(embeddings):,} embeddings to migrate")
            
            if not embeddings:
                print("   ⚠️  No embeddings found!")
                return 0
        
        # Insert into target database
        print(f"\n💾 Inserting embeddings into target database...")
        
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
            
            # Process in batches
            batch_size = 1000
            for i in tqdm(range(0, len(embeddings), batch_size), desc="   Migrating batches"):
                batch = embeddings[i:i+batch_size]
                execute_batch(target_cur, insert_query, batch, page_size=100)
                target_conn.commit()
        
        # Verify migration
        print(f"\n🔍 Verifying migration...")
        with target_conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM unified_embeddings")
            total_count = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) FROM unified_embeddings 
                WHERE source_table = 'ai_partner_codeembedding'
            """)
            code_count = cur.fetchone()[0]
            
            print(f"   📊 Total embeddings: {total_count:,}")
            print(f"   💻 Code embeddings: {code_count}")
            
        print(f"\n" + "="*80)
        print("✅ MIGRATION COMPLETE!")
        print("="*80)
        print(f"""
Django will now find the embeddings at:
📍 Database: ai_unified_platform
📍 Table: unified_embeddings
💻 Code embeddings: {code_count}

Your RAG system should now work with the code intelligence! 🎉
""")
        
        return total_count
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        source_conn.close()
        target_conn.close()

def main():
    migrate_to_correct_database()

if __name__ == "__main__":
    main()