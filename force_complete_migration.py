#!/usr/bin/env python3
"""
FORCE COMPLETE EMBEDDINGS MIGRATION
This script will FORCEFULLY migrate ALL embeddings, even if they already exist.
It will clear existing data and start fresh to ensure we get all 36,656 records.
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
        logging.FileHandler('force_migration.log'),
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

def serialize_for_json(obj):
    """Convert objects to JSON-serializable format"""
    if obj is None:
        return None
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return serialize_for_json(obj.__dict__)
    else:
        try:
            json.dumps(obj)  # Test if it's already JSON serializable
            return obj
        except (TypeError, ValueError):
            return str(obj)

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

def setup_fresh_target():
    """Set up fresh target table"""
    logger.info("🗑️ Setting up fresh target table...")
    
    conn = get_connection(TARGET_DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Drop and recreate table for fresh start
        cur.execute("DROP TABLE IF EXISTS unified_embeddings CASCADE")
        
        # Enable pgvector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        
        # Create fresh table
        cur.execute("""
            CREATE TABLE unified_embeddings (
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
            "CREATE INDEX idx_unified_embeddings_embedding ON unified_embeddings USING hnsw (embedding vector_cosine_ops)",
            "CREATE INDEX idx_unified_embeddings_content_type ON unified_embeddings (content_type)",
            "CREATE INDEX idx_unified_embeddings_source ON unified_embeddings (source_database, source_table)",
            "CREATE INDEX idx_unified_embeddings_hash ON unified_embeddings (content_hash)",
            "CREATE INDEX idx_unified_embeddings_importance ON unified_embeddings (importance_score DESC)"
        ]
        
        for index_sql in indexes:
            cur.execute(index_sql)
        
        conn.commit()
        logger.info("✅ Fresh target table created")
        
    except Exception as e:
        logger.error(f"❌ Error setting up target table: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def migrate_unified_memory_entries():
    """Migrate ALL unified_memory_entries - both with and without embeddings"""
    logger.info("🔄 Migrating ALL unified_memory_entries...")
    
    source_conn = get_connection(SOURCE_DB_CONFIG)
    target_conn = get_connection(TARGET_DB_CONFIG)
    
    try:
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        # Get total count
        source_cur.execute("SELECT COUNT(*) FROM unified_memory_entries")
        total = source_cur.fetchone()['count']
        logger.info(f"   📊 Total records to migrate: {total:,}")
        
        # Migrate ALL records in batches
        batch_size = 1000
        migrated = 0
        errors = 0
        
        with tqdm(total=total, desc="   Migrating unified_memory_entries", unit="records") as pbar:
            offset = 0
            while offset < total:
                source_cur.execute("""
                    SELECT id, content_text, embedding, created_at, context_data, 
                           importance_score, content_type, memory_category
                    FROM unified_memory_entries 
                    ORDER BY id
                    LIMIT %s OFFSET %s
                """, (batch_size, offset))
                
                records = source_cur.fetchall()
                if not records:
                    break
                
                batch_data = []
                
                for record in records:
                    try:
                        content = record.get('content_text', '')
                        if not content:
                            content = f"Record {record['id']} from unified_memory_entries"
                        
                        # Parse embedding
                        embedding = parse_embedding(record.get('embedding'))
                        
                        # Truncate content if needed
                        if len(str(content)) > 8000:
                            content = str(content)[:8000] + "..."
                        
                        # Build metadata
                        metadata = {
                            'original_table': 'unified_memory_entries',
                            'migration_date': datetime.now().isoformat(),
                            'has_embedding': embedding is not None,
                            'memory_category': record.get('memory_category'),
                            'original_created_at': serialize_for_json(record.get('created_at'))
                        }
                        
                        # Add context data if available
                        if record.get('context_data'):
                            try:
                                if isinstance(record['context_data'], str):
                                    metadata['context_data'] = json.loads(record['context_data'])
                                else:
                                    metadata['context_data'] = serialize_for_json(record['context_data'])
                            except:
                                metadata['context_data'] = str(record['context_data'])
                        
                        # Determine content type
                        content_type = record.get('content_type', 'unified_memory')
                        if not content_type:
                            content_type = 'unified_memory'
                        
                        # Calculate importance
                        importance = record.get('importance_score', 0.5)
                        if importance is None:
                            importance = 0.5
                        
                        # Content hash
                        content_hash = hashlib.sha256(str(content).encode('utf-8')).hexdigest()
                        
                        batch_data.append((
                            'moveyourazz_dev',
                            'unified_memory_entries',
                            str(record['id']),
                            content_type,
                            content,
                            embedding,  # Can be None
                            'text-embedding-3-small',
                            json.dumps(metadata),
                            float(importance),
                            content_hash
                        ))
                        
                    except Exception as e:
                        errors += 1
                        if errors <= 10:
                            logger.warning(f"      Error processing record {record.get('id')}: {e}")
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
                        """
                        
                        execute_batch(target_cur, insert_query, batch_data, page_size=500)
                        target_conn.commit()
                        
                        migrated += len(batch_data)
                        
                    except Exception as e:
                        target_conn.rollback()
                        logger.error(f"      Batch insert error: {e}")
                        
                        # Try individual inserts
                        for data in batch_data:
                            try:
                                target_cur.execute(insert_query, data)
                                target_conn.commit()
                                migrated += 1
                            except Exception:
                                target_conn.rollback()
                                errors += 1
                
                offset += len(records)
                pbar.update(len(records))
        
        logger.info(f"   ✅ Migrated {migrated:,} records from unified_memory_entries")
        logger.info(f"      Errors: {errors:,}")
        
        return migrated
        
    finally:
        source_conn.close()
        target_conn.close()

def migrate_other_tables():
    """Migrate other embedding tables"""
    logger.info("🔄 Migrating other embedding tables...")
    
    tables = [
        {
            'name': 'memory_memoryentry',
            'content_type': 'memory_entry',
            'query': """
                SELECT id, full_transcript, embedding, created_at, importance
                FROM memory_memoryentry 
                WHERE full_transcript IS NOT NULL
                ORDER BY id
            """
        },
        {
            'name': 'ukf_system_markdownembedding',
            'content_type': 'markdown_chunk',
            'query': """
                SELECT id, chunk_text, embedding, created_date, 
                       importance_score, topics, entities
                FROM ukf_system_markdownembedding 
                WHERE chunk_text IS NOT NULL
                ORDER BY id
            """
        },
        {
            'name': 'ai_partner_codeembedding',
            'content_type': 'code_chunk',
            'query': """
                SELECT id, code_snippet, embeddings, created_at,
                       file_path, section_name, language
                FROM ai_partner_codeembedding 
                WHERE code_snippet IS NOT NULL
                ORDER BY id
            """
        }
    ]
    
    total_migrated = 0
    
    for table_config in tables:
        table_name = table_config['name']
        logger.info(f"   📦 Processing {table_name}...")
        
        source_conn = get_connection(SOURCE_DB_CONFIG)
        target_conn = get_connection(TARGET_DB_CONFIG)
        
        try:
            source_cur = source_conn.cursor()
            target_cur = target_conn.cursor()
            
            source_cur.execute(table_config['query'])
            records = source_cur.fetchall()
            
            logger.info(f"      Found {len(records):,} records")
            
            if not records:
                continue
            
            batch_data = []
            migrated = 0
            
            for record in tqdm(records, desc=f"      Processing {table_name}", unit="records"):
                try:
                    # Extract content based on table
                    if table_name == 'memory_memoryentry':
                        content = record.get('full_transcript', '')
                        embedding_col = 'embedding'
                    elif table_name == 'ukf_system_markdownembedding':
                        content = record.get('chunk_text', '')
                        embedding_col = 'embedding'
                    elif table_name == 'ai_partner_codeembedding':
                        content = record.get('code_snippet', '')
                        embedding_col = 'embeddings'
                    
                    if not content:
                        continue
                    
                    # Parse embedding
                    embedding = parse_embedding(record.get(embedding_col))
                    
                    # Truncate content
                    if len(str(content)) > 8000:
                        content = str(content)[:8000] + "..."
                    
                    # Build metadata
                    metadata = {
                        'original_table': table_name,
                        'migration_date': datetime.now().isoformat(),
                        'has_embedding': embedding is not None
                    }
                    
                    # Add table-specific metadata
                    for key, value in record.items():
                        if key not in [embedding_col, 'full_transcript', 'chunk_text', 'code_snippet']:
                            metadata[key] = serialize_for_json(value)
                    
                    importance = record.get('importance_score', record.get('importance', 0.5))
                    if importance is None:
                        importance = 0.5
                    
                    content_hash = hashlib.sha256(str(content).encode('utf-8')).hexdigest()
                    
                    batch_data.append((
                        'moveyourazz_dev',
                        table_name,
                        str(record['id']),
                        table_config['content_type'],
                        content,
                        embedding,
                        'text-embedding-3-small',
                        json.dumps(metadata),
                        float(importance),
                        content_hash
                    ))
                    
                except Exception as e:
                    logger.warning(f"         Error processing {table_name} record {record.get('id')}: {e}")
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
                    """
                    
                    execute_batch(target_cur, insert_query, batch_data, page_size=500)
                    target_conn.commit()
                    
                    migrated = len(batch_data)
                    total_migrated += migrated
                    logger.info(f"      ✅ Migrated {migrated:,} records")
                    
                except Exception as e:
                    logger.error(f"      ❌ Error migrating {table_name}: {e}")
                    target_conn.rollback()
        
        finally:
            source_conn.close()
            target_conn.close()
    
    return total_migrated

def main():
    """Main migration function"""
    logger.info("=" * 80)
    logger.info("🚀 FORCE COMPLETE EMBEDDINGS MIGRATION")
    logger.info("    This will create a FRESH migration of ALL data")
    logger.info("=" * 80)
    
    # Fresh start
    setup_fresh_target()
    
    # Migrate unified_memory_entries (ALL 36,656 records)
    unified_migrated = migrate_unified_memory_entries()
    
    # Migrate other tables
    others_migrated = migrate_other_tables()
    
    # Final verification
    logger.info("=" * 80)
    logger.info("📊 MIGRATION COMPLETE")
    logger.info("=" * 80)
    
    target_conn = get_connection(TARGET_DB_CONFIG)
    target_cur = target_conn.cursor()
    
    # Total counts
    target_cur.execute("SELECT COUNT(*) as total FROM unified_embeddings")
    total_records = target_cur.fetchone()['total']
    
    target_cur.execute("SELECT COUNT(*) as with_embeddings FROM unified_embeddings WHERE embedding IS NOT NULL")
    with_embeddings = target_cur.fetchone()['with_embeddings']
    
    # By table breakdown
    target_cur.execute("""
        SELECT source_table, content_type,
               COUNT(*) as total_count,
               COUNT(embedding) as with_embeddings
        FROM unified_embeddings
        GROUP BY source_table, content_type
        ORDER BY total_count DESC
    """)
    
    logger.info(f"🎯 FINAL RESULTS:")
    logger.info(f"   Total records: {total_records:,}")
    logger.info(f"   With embeddings: {with_embeddings:,}")
    logger.info(f"   Without embeddings: {total_records - with_embeddings:,}")
    logger.info("")
    logger.info("📈 Breakdown by table:")
    
    for row in target_cur.fetchall():
        logger.info(f"   • {row['content_type']} ({row['source_table']}): {row['total_count']:,} total, {row['with_embeddings']:,} embeddings")
    
    # Check unified_memory_entries specifically
    target_cur.execute("""
        SELECT COUNT(*) as count 
        FROM unified_embeddings 
        WHERE source_table = 'unified_memory_entries'
    """)
    unified_count = target_cur.fetchone()['count']
    
    logger.info("")
    logger.info(f"🔍 Unified Memory Entries: {unified_count:,} / 36,656 expected")
    
    if unified_count == 36656:
        logger.info("✅ SUCCESS! All unified_memory_entries migrated!")
    else:
        logger.warning(f"⚠️ Missing {36656 - unified_count:,} unified_memory_entries records")
    
    logger.info("")
    logger.info("🎉 FORCE MIGRATION COMPLETE!")
    
    target_conn.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.error("\n⚠️ Migration interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)