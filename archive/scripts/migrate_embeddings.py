#!/usr/bin/env python3
"""
Safe and secure migration of all embeddings to unified_donkey_betz database
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

from django.db import connection, transaction
from django.utils import timezone
from content.models import Document, DocumentEmbedding
from self_awareness.models import CodeEmbedding


class EmbeddingMigrator:
    """Safely migrate embeddings from multiple source databases"""
    
    def __init__(self):
        self.sources = {
            'moveyourazz_dev': 'postgresql://postgres@localhost/moveyourazz_dev',
            'ai_content_studio': 'postgresql://postgres@localhost/ai_content_studio',
            'ai_unified_platform': 'postgresql://postgres@localhost/ai_unified_platform'
        }
        self.target = 'postgresql://postgres@localhost/unified_donkey_betz'
        self.batch_size = 1000
        self.migration_stats = {
            'total_migrated': 0,
            'code_embeddings': 0,
            'conversation_embeddings': 0,
            'memory_embeddings': 0,
            'errors': []
        }
        
    def create_target_tables(self):
        """Create necessary tables in target database"""
        print("\n📋 Creating/verifying target tables...")
        
        with psycopg2.connect(self.target) as conn:
            with conn.cursor() as cur:
                # Create unified embeddings table
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
                
                # Create code embeddings table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS migrated_code_embeddings (
                        id SERIAL PRIMARY KEY,
                        file_path TEXT,
                        file_type VARCHAR(50),
                        module_path TEXT,
                        class_name VARCHAR(255),
                        function_name VARCHAR(255),
                        code_snippet TEXT,
                        embedding vector(1536),
                        embedding_model VARCHAR(100),
                        metadata JSONB,
                        source_database VARCHAR(100),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        migrated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                
                # Create indexes for efficient searching
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_unified_embeddings_content_type 
                    ON unified_embeddings(content_type);
                    
                    CREATE INDEX IF NOT EXISTS idx_unified_embeddings_source 
                    ON unified_embeddings(source_database, source_table);
                    
                    CREATE INDEX IF NOT EXISTS idx_unified_embeddings_embedding_vector
                    ON unified_embeddings USING hnsw (embedding vector_cosine_ops);
                    
                    CREATE INDEX IF NOT EXISTS idx_code_embeddings_embedding_vector
                    ON migrated_code_embeddings USING hnsw (embedding vector_cosine_ops);
                """)
                
                conn.commit()
                print("   ✅ Target tables ready")
                
    def migrate_moveyourazz_embeddings(self):
        """Migrate embeddings from moveyourazz_dev database"""
        print("\n🔄 Migrating from moveyourazz_dev...")
        
        source_conn = psycopg2.connect(self.sources['moveyourazz_dev'])
        target_conn = psycopg2.connect(self.target)
        
        try:
            # Migrate unified_memory_entries
            print("\n   📦 Migrating unified_memory_entries...")
            self._migrate_table(
                source_conn, target_conn,
                source_query="""
                    SELECT id, user_id, content_text, embedding, embedding_model,
                           importance_score, created_at, context_data, content_type
                    FROM unified_memory_entries
                    WHERE embedding IS NOT NULL
                    ORDER BY id
                """,
                target_table='unified_embeddings',
                source_db='moveyourazz_dev',
                source_table='unified_memory_entries',
                content_type_field='content_type'
            )
            
            # Migrate conversation embeddings
            print("\n   💬 Migrating conversation embeddings...")
            self._migrate_table(
                source_conn, target_conn,
                source_query="""
                    SELECT id, chunk_text, embedding, speaker, conversation_type,
                           conversation_timestamp, topics, entities
                    FROM ai_partner_conversationembedding
                    WHERE embedding IS NOT NULL
                    ORDER BY id
                """,
                target_table='unified_embeddings',
                source_db='moveyourazz_dev',
                source_table='ai_partner_conversationembedding',
                content_type_field='conversation_type'
            )
            
        finally:
            source_conn.close()
            target_conn.close()
            
    def migrate_ai_content_studio_embeddings(self):
        """Migrate embeddings from ai_content_studio database"""
        print("\n🔄 Migrating from ai_content_studio...")
        
        source_conn = psycopg2.connect(self.sources['ai_content_studio'])
        target_conn = psycopg2.connect(self.target)
        
        try:
            # Migrate memories
            print("\n   🧠 Migrating memories...")
            self._migrate_table(
                source_conn, target_conn,
                source_query="""
                    SELECT id, content_text, embedding, metadata, importance_score,
                           created_at, user_id, embedding_version
                    FROM memories
                    WHERE embedding IS NOT NULL
                    ORDER BY id
                """,
                target_table='unified_embeddings',
                source_db='ai_content_studio',
                source_table='memories',
                content_type_field=None
            )
            
            # Migrate assistant conversation memories
            print("\n   🤖 Migrating assistant conversation memories...")
            self._migrate_table(
                source_conn, target_conn,
                source_query="""
                    SELECT id, summary, embedding, context, importance,
                           created_at, session_id
                    FROM assistant_conversationmemory
                    WHERE embedding IS NOT NULL
                    ORDER BY id
                """,
                target_table='unified_embeddings',
                source_db='ai_content_studio',
                source_table='assistant_conversationmemory',
                content_type_field=None
            )
            
        finally:
            source_conn.close()
            target_conn.close()
            
    def _migrate_table(self, source_conn, target_conn, source_query, target_table,
                      source_db, source_table, content_type_field):
        """Generic table migration with batching and error handling"""
        
        with source_conn.cursor() as source_cur:
            with target_conn.cursor() as target_cur:
                # Count total records
                count_query = source_query.replace("SELECT", "SELECT COUNT(*) as cnt FROM (SELECT", 1) + ") as subq"
                source_cur.execute(count_query)
                total_count = source_cur.fetchone()[0]
                print(f"      Found {total_count:,} embeddings to migrate")
                
                if total_count == 0:
                    return
                
                # Migrate in batches
                offset = 0
                migrated = 0
                
                with tqdm(total=total_count, desc=f"      Migrating {source_table}") as pbar:
                    while offset < total_count:
                        batch_query = f"{source_query} LIMIT {self.batch_size} OFFSET {offset}"
                        source_cur.execute(batch_query)
                        batch = source_cur.fetchall()
                        
                        if not batch:
                            break
                        
                        # Prepare batch for insertion
                        insert_data = []
                        for row in batch:
                            try:
                                # Extract data based on source table
                                if source_table == 'unified_memory_entries':
                                    content_text = row[2]  # content_text
                                    embedding = row[3]     # embedding
                                    content_type = row[8] if len(row) > 8 else 'unknown'  # content_type
                                    metadata = row[7] if len(row) > 7 and row[7] else {}  # context_data
                                    
                                elif source_table == 'ai_partner_conversationembedding':
                                    content_text = row[1]  # chunk_text
                                    embedding = row[2]     # embedding
                                    content_type = row[4] if row[4] else 'conversation'  # conversation_type
                                    metadata = {
                                        'speaker': row[3] if row[3] else 'unknown',
                                        'topics': row[6] if len(row) > 6 and row[6] else [],
                                        'entities': row[7] if len(row) > 7 and row[7] else []
                                    }
                                    
                                elif source_table == 'memories':
                                    content_text = row[1]  # content_text
                                    embedding = row[2]     # embedding
                                    content_type = 'memory'
                                    metadata = row[3] if row[3] else {}  # metadata
                                    
                                elif source_table == 'assistant_conversationmemory':
                                    content_text = row[1]  # summary
                                    embedding = row[2]     # embedding
                                    content_type = 'assistant_conversation'
                                    metadata = {'context': row[3]} if len(row) > 3 and row[3] else {}
                                    
                                else:
                                    content_text = str(row[1]) if len(row) > 1 else ''
                                    embedding = row[2] if len(row) > 2 else None
                                    content_type = 'unknown'
                                    metadata = {}
                                
                                # Generate content hash for deduplication
                                content_hash = hashlib.sha256(content_text.encode()).hexdigest()
                                
                                # Check if it's code
                                if any(pattern in content_text for pattern in ['def ', 'class ', 'import ', 'function']):
                                    self.migration_stats['code_embeddings'] += 1
                                    content_type = 'code'
                                
                                insert_data.append((
                                    source_db,
                                    source_table,
                                    str(row[0]),  # source_id
                                    content_type,
                                    content_text[:10000],  # Truncate very long texts
                                    embedding,
                                    'text-embedding-3-small',  # Default model
                                    json.dumps(metadata),
                                    0.5,  # importance_score
                                    timezone.now(),
                                    content_hash
                                ))
                                
                            except Exception as e:
                                self.migration_stats['errors'].append(f"Row error: {str(e)[:100]}")
                                continue
                        
                        # Insert batch into target
                        if insert_data:
                            insert_query = """
                                INSERT INTO unified_embeddings (
                                    source_database, source_table, source_id, content_type,
                                    content_text, embedding, embedding_model, metadata,
                                    importance_score, migrated_at, content_hash
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (source_database, source_table, source_id) 
                                DO UPDATE SET 
                                    embedding = EXCLUDED.embedding,
                                    content_text = EXCLUDED.content_text,
                                    migrated_at = EXCLUDED.migrated_at
                            """
                            
                            execute_batch(target_cur, insert_query, insert_data, page_size=100)
                            target_conn.commit()
                            
                            migrated += len(insert_data)
                            self.migration_stats['total_migrated'] += len(insert_data)
                        
                        pbar.update(len(batch))
                        offset += self.batch_size
                
                print(f"      ✅ Migrated {migrated:,} embeddings from {source_table}")
                
    def verify_migration(self):
        """Verify the migration was successful"""
        print("\n🔍 Verifying migration...")
        
        with psycopg2.connect(self.target) as conn:
            with conn.cursor() as cur:
                # Count total migrated
                cur.execute("SELECT COUNT(*) FROM unified_embeddings")
                total = cur.fetchone()[0]
                
                # Count by source
                cur.execute("""
                    SELECT source_database, source_table, COUNT(*) 
                    FROM unified_embeddings 
                    GROUP BY source_database, source_table
                    ORDER BY source_database, source_table
                """)
                
                print(f"\n   📊 Migration Summary:")
                print(f"      Total embeddings migrated: {total:,}")
                print(f"\n      By source:")
                
                for source_db, source_table, count in cur.fetchall():
                    print(f"        • {source_db}.{source_table}: {count:,}")
                
                # Count by content type
                cur.execute("""
                    SELECT content_type, COUNT(*) 
                    FROM unified_embeddings 
                    GROUP BY content_type
                    ORDER BY COUNT(*) DESC
                """)
                
                print(f"\n      By content type:")
                for content_type, count in cur.fetchall():
                    print(f"        • {content_type}: {count:,}")
                
                # Verify vector dimensions
                cur.execute("""
                    SELECT array_length(embedding::real[], 1) as dim, COUNT(*)
                    FROM unified_embeddings
                    WHERE embedding IS NOT NULL
                    GROUP BY dim
                """)
                
                print(f"\n      Embedding dimensions:")
                for dim, count in cur.fetchall():
                    print(f"        • {dim}D: {count:,} embeddings")
                
                return total
                
    def run_migration(self):
        """Run the complete migration process"""
        print("\n" + "="*80)
        print("🚀 STARTING EMBEDDING MIGRATION")
        print("="*80)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Create target tables
            self.create_target_tables()
            
            # Step 2: Migrate from each source
            self.migrate_moveyourazz_embeddings()
            self.migrate_ai_content_studio_embeddings()
            
            # Note: ai_unified_platform appears to have duplicates of ai_content_studio
            # so we'll skip it to avoid duplicates
            
            # Step 3: Verify migration
            total = self.verify_migration()
            
            # Print final stats
            duration = (datetime.now() - start_time).total_seconds()
            print("\n" + "="*80)
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*80)
            print(f"\n📊 Final Statistics:")
            print(f"   Total embeddings migrated: {self.migration_stats['total_migrated']:,}")
            print(f"   Code embeddings identified: {self.migration_stats['code_embeddings']:,}")
            print(f"   Errors encountered: {len(self.migration_stats['errors'])}")
            print(f"   Time taken: {duration:.2f} seconds")
            
            if self.migration_stats['errors']:
                print(f"\n⚠️  Errors (first 5):")
                for error in self.migration_stats['errors'][:5]:
                    print(f"      • {error}")
            
            print(f"\n💡 Next steps:")
            print(f"   1. Test semantic search on the migrated embeddings")
            print(f"   2. Update your application to use unified_embeddings table")
            print(f"   3. Consider creating specialized views for different content types")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    migrator = EmbeddingMigrator()
    migrator.run_migration()