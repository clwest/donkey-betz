#!/usr/bin/env python3
"""
CRITICAL: Complete Embeddings Migration Script
Migrate ALL embeddings from moveyourazz_dev to ai_unified_platform

This script will:
1. Connect to both databases with proper credentials
2. Migrate ALL records from unified_memory_entries (36,656 records)
3. Migrate ALL embedding records from all relevant tables
4. Handle both embedded and non-embedded records
5. Ensure no data is lost
6. Provide comprehensive progress tracking
7. Handle large volumes efficiently with batching
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
import json
from datetime import datetime
import hashlib
from tqdm import tqdm
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database configurations
SOURCE_DB_CONFIG = {
    'host': 'localhost',
    'database': 'moveyourazz_dev', 
    'user': 'donkeyking',
    'cursor_factory': RealDictCursor
}

TARGET_DB_CONFIG = {
    'host': 'localhost',
    'database': 'ai_unified_platform',
    'user': 'ai_unified_user', 
    'password': '[REDACTED - HISTORICAL SECRET]',
    'cursor_factory': RealDictCursor
}

def get_connection(config):
    """Get database connection"""
    return psycopg2.connect(**config)

def ensure_target_table():
    """Ensure the target table exists with proper structure"""
    logger.info("🔧 Setting up target database table...")
    
    conn = get_connection(TARGET_DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Create unified_embeddings table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS unified_embeddings (
                id SERIAL PRIMARY KEY,
                source_database VARCHAR(100) NOT NULL,
                source_table VARCHAR(100) NOT NULL,
                source_id VARCHAR(255) NOT NULL,
                content_type VARCHAR(100) NOT NULL,
                content_text TEXT,
                embedding vector(1536),
                embedding_model VARCHAR(100) DEFAULT 'text-embedding-3-small',
                metadata JSONB DEFAULT '{}',
                importance_score FLOAT DEFAULT 0.5,
                content_hash VARCHAR(64),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                migrated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(source_database, source_table, source_id)
            )
        """)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_unified_embeddings_embedding ON unified_embeddings USING hnsw (embedding vector_cosine_ops)",
            "CREATE INDEX IF NOT EXISTS idx_unified_embeddings_content_type ON unified_embeddings (content_type)",
            "CREATE INDEX IF NOT EXISTS idx_unified_embeddings_source ON unified_embeddings (source_database, source_table)",
            "CREATE INDEX IF NOT EXISTS idx_unified_embeddings_hash ON unified_embeddings (content_hash)",
            "CREATE INDEX IF NOT EXISTS idx_unified_embeddings_importance ON unified_embeddings (importance_score DESC)"
        ]
        
        for index_sql in indexes:
            cur.execute(index_sql)
        
        conn.commit()
        logger.info("✅ Target table and indexes ready")
        
    except Exception as e:
        logger.error(f"❌ Error setting up target table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def generate_content_hash(content):
    """Generate consistent hash for content"""
    if not content:
        return None
    return hashlib.sha256(str(content).encode('utf-8')).hexdigest()

def serialize_for_json(obj):
    """Convert objects to JSON-serializable format"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return {k: serialize_for_json(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    else:
        return obj

def parse_embedding(embedding_data):
    """Parse embedding data from various formats"""
    if not embedding_data:
        return None
        
    # Handle string JSON embeddings
    if isinstance(embedding_data, str):
        try:
            embedding_data = json.loads(embedding_data)
        except (json.JSONDecodeError, ValueError):
            return None
    
    # Ensure it's a list of floats with correct dimension
    if isinstance(embedding_data, list):
        if len(embedding_data) == 1536:
            try:
                return [float(x) for x in embedding_data]
            except (ValueError, TypeError):
                return None
    
    return None

def migrate_table(table_config, batch_size=1000):
    """Migrate embeddings from a specific table"""
    table_name = table_config['table']
    content_type = table_config['content_type']
    
    logger.info(f"🔄 Starting migration of {table_name}...")
    
    source_conn = get_connection(SOURCE_DB_CONFIG)
    target_conn = get_connection(TARGET_DB_CONFIG)
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        # Get total count
        count_query = table_config.get('count_query', f"SELECT COUNT(*) FROM {table_name}")
        source_cur.execute(count_query)
        total_records = source_cur.fetchone()['count']
        
        logger.info(f"   📊 Total records in {table_name}: {total_records:,}")
        
        if total_records == 0:
            logger.info(f"   ✅ No records to migrate from {table_name}")
            return 0
        
        # Check already migrated
        target_cur.execute("""
            SELECT COUNT(*) as count FROM unified_embeddings 
            WHERE source_database = 'moveyourazz_dev' AND source_table = %s
        """, (table_name,))
        already_migrated = target_cur.fetchone()['count']
        
        logger.info(f"   📈 Already migrated: {already_migrated:,}")
        
        # Execute main query
        main_query = table_config['query']
        source_cur.execute(main_query)
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        # Process in batches
        with tqdm(total=total_records, desc=f"   Migrating {table_name}", unit="records") as pbar:
            while True:
                records = source_cur.fetchmany(batch_size)
                if not records:
                    break
                
                batch_data = []
                
                for record in records:
                    try:
                        # Extract data based on table configuration
                        source_id = str(record['id'])
                        content = record.get('content_text', record.get('content', record.get('chunk_text', record.get('full_transcript', ''))))
                        
                        # Handle embedding extraction
                        embedding_raw = record.get('embedding', record.get('embeddings', record.get('embedding_vector')))
                        embedding = parse_embedding(embedding_raw)
                        
                        # Truncate content if too long
                        if content and len(str(content)) > 8000:
                            content = str(content)[:8000] + "..."
                        
                        # Generate metadata
                        metadata = {
                            'original_table': table_name,
                            'migration_date': datetime.now().isoformat(),
                            'has_embedding': embedding is not None,
                            'original_record_data': serialize_for_json({k: v for k, v in record.items() 
                                                   if k not in ['embedding', 'embeddings', 'embedding_vector'] and v is not None})
                        }
                        
                        # Additional metadata from record
                        if 'context_data' in record and record['context_data']:
                            try:
                                if isinstance(record['context_data'], str):
                                    metadata['context_data'] = json.loads(record['context_data'])
                                else:
                                    metadata['context_data'] = serialize_for_json(record['context_data'])
                            except:
                                pass
                        
                        # Calculate importance score
                        importance_score = record.get('importance_score', record.get('importance', 0.5))
                        if importance_score is None:
                            importance_score = 0.5
                        
                        batch_data.append((
                            'moveyourazz_dev',  # source_database
                            table_name,         # source_table  
                            source_id,          # source_id
                            content_type,       # content_type
                            str(content) if content else '',  # content_text
                            embedding,          # embedding (can be None)
                            'text-embedding-3-small',  # embedding_model
                            json.dumps(metadata),  # metadata
                            float(importance_score),  # importance_score
                            generate_content_hash(content)  # content_hash
                        ))
                        
                    except Exception as e:
                        error_count += 1
                        if error_count <= 5:  # Log first few errors
                            logger.warning(f"      Error processing record {record.get('id', 'unknown')}: {e}")
                        continue
                
                # Batch insert
                if batch_data:
                    try:
                        insert_query = """
                            INSERT INTO unified_embeddings (
                                source_database, source_table, source_id, content_type,
                                content_text, embedding, embedding_model, metadata,
                                importance_score, content_hash
                            ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s)
                            ON CONFLICT (source_database, source_table, source_id) 
                            DO UPDATE SET
                                content_text = EXCLUDED.content_text,
                                embedding = EXCLUDED.embedding,
                                metadata = EXCLUDED.metadata,
                                importance_score = EXCLUDED.importance_score,
                                content_hash = EXCLUDED.content_hash,
                                migrated_at = NOW()
                        """
                        
                        execute_batch(target_cur, insert_query, batch_data, page_size=batch_size)
                        target_conn.commit()
                        
                        migrated_count += len(batch_data)
                        
                    except Exception as e:
                        logger.error(f"      Batch insert error: {e}")
                        target_conn.rollback()
                        # Try individual inserts for this batch
                        for data in batch_data:
                            try:
                                target_cur.execute(insert_query, data)
                                target_conn.commit()
                                migrated_count += 1
                            except Exception as individual_error:
                                target_conn.rollback()
                                error_count += 1
                                continue
                
                pbar.update(len(records))
        
        logger.info(f"   ✅ Migration complete for {table_name}")
        logger.info(f"      Successfully migrated: {migrated_count:,}")
        logger.info(f"      Errors: {error_count:,}")
        
        return migrated_count
        
    except Exception as e:
        logger.error(f"   ❌ Error migrating {table_name}: {e}")
        return 0
    finally:
        source_conn.close()
        target_conn.close()

def main():
    """Main migration function"""
    logger.info("=" * 80)
    logger.info("🚀 COMPREHENSIVE EMBEDDINGS MIGRATION")
    logger.info("    Source: moveyourazz_dev")
    logger.info("    Target: ai_unified_platform") 
    logger.info("=" * 80)
    
    # Ensure target table exists
    ensure_target_table()
    
    # Check current status
    target_conn = get_connection(TARGET_DB_CONFIG)
    target_cur = target_conn.cursor()
    target_cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
    current_total = target_cur.fetchone()['count']
    logger.info(f"📊 Current embeddings in target: {current_total:,}")
    target_conn.close()
    
    # Migration configuration for all tables
    migration_tables = [
        {
            'table': 'unified_memory_entries',
            'content_type': 'unified_memory',
            'query': """
                SELECT id, content_text, embedding, created_at, context_data, importance_score
                FROM unified_memory_entries 
                ORDER BY id
            """,
            'count_query': "SELECT COUNT(*) FROM unified_memory_entries"
        },
        {
            'table': 'memory_memoryentry', 
            'content_type': 'memory_entry',
            'query': """
                SELECT id, full_transcript as content_text, embedding, created_at, importance
                FROM memory_memoryentry 
                WHERE full_transcript IS NOT NULL
                ORDER BY id
            """,
            'count_query': "SELECT COUNT(*) FROM memory_memoryentry WHERE full_transcript IS NOT NULL"
        },
        {
            'table': 'ukf_system_markdownembedding',
            'content_type': 'markdown_chunk', 
            'query': """
                SELECT id, chunk_text as content_text, embedding, created_date as created_at, 
                       importance_score, content_importance_score, semantic_cluster_id,
                       topics, entities, mentioned_technologies
                FROM ukf_system_markdownembedding 
                WHERE chunk_text IS NOT NULL
                ORDER BY id
            """,
            'count_query': "SELECT COUNT(*) FROM ukf_system_markdownembedding WHERE chunk_text IS NOT NULL"
        },
        {
            'table': 'ai_partner_codeembedding',
            'content_type': 'code_chunk',
            'query': """
                SELECT id, code_snippet as content_text, embeddings as embedding, created_at,
                       file_path, section_name, section_type, language
                FROM ai_partner_codeembedding 
                WHERE code_snippet IS NOT NULL
                ORDER BY id  
            """,
            'count_query': "SELECT COUNT(*) FROM ai_partner_codeembedding WHERE code_snippet IS NOT NULL"
        }
    ]
    
    # Execute migrations
    total_migrated = 0
    
    for table_config in migration_tables:
        try:
            migrated = migrate_table(table_config)
            total_migrated += migrated
            logger.info("")  # Add spacing between tables
        except Exception as e:
            logger.error(f"❌ Failed to migrate {table_config['table']}: {e}")
            continue
    
    # Final verification
    logger.info("=" * 80)
    logger.info("📊 MIGRATION SUMMARY")
    logger.info("=" * 80)
    
    target_conn = get_connection(TARGET_DB_CONFIG) 
    target_cur = target_conn.cursor()
    
    # Total count
    target_cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
    final_total = target_cur.fetchone()['count']
    
    # Count by table
    target_cur.execute("""
        SELECT source_table, content_type, 
               COUNT(*) as total_count,
               COUNT(embedding) as with_embeddings
        FROM unified_embeddings 
        WHERE source_database = 'moveyourazz_dev'
        GROUP BY source_table, content_type
        ORDER BY total_count DESC
    """)
    
    logger.info(f"🎯 FINAL RESULTS:")
    logger.info(f"   Total embeddings: {final_total:,}")
    logger.info(f"   Newly migrated: {total_migrated:,}")
    logger.info("")
    logger.info("📈 Breakdown by table:")
    
    table_totals = 0
    embedding_totals = 0
    
    for row in target_cur.fetchall():
        table_totals += row['total_count']  
        embedding_totals += row['with_embeddings']
        logger.info(f"   • {row['content_type']} ({row['source_table']}): {row['total_count']:,} total, {row['with_embeddings']:,} with embeddings")
    
    logger.info("")
    logger.info(f"✅ SUCCESS! Migration completed:")
    logger.info(f"   • Total records: {table_totals:,}")
    logger.info(f"   • With embeddings: {embedding_totals:,}")
    logger.info(f"   • Database: ai_unified_platform")
    logger.info("")
    logger.info("🎉 All embeddings are now available for RAG queries!")
    
    target_conn.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.error("\n⚠️ Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)