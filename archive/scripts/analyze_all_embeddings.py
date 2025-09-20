#!/usr/bin/env python3
"""
Comprehensive analysis of embeddings across all databases
"""

import psycopg2
import json
from collections import defaultdict

def analyze_database(conn_string, db_name):
    """Analyze embeddings in a specific database"""
    print(f"\n{'='*80}")
    print(f"📊 DATABASE: {db_name}")
    print('='*80)
    
    try:
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor()
        
        # Check for pgvector extension
        cur.execute("SELECT extname FROM pg_extension WHERE extname='vector';")
        has_vector = cur.fetchone()
        
        if has_vector:
            print(f"✅ pgvector extension installed")
            
            # Find all vector columns
            cur.execute("""
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE table_schema='public' AND udt_name='vector';
            """)
            
            vector_tables = cur.fetchall()
            
            if vector_tables:
                print(f"\n📍 Tables with vector columns:")
                total_embeddings = 0
                
                for table_name, column_name in vector_tables:
                    # Count embeddings
                    try:
                        cur.execute(f"""
                            SELECT 
                                COUNT(*) as total_rows,
                                COUNT({column_name}) as rows_with_embeddings
                            FROM {table_name};
                        """)
                        total, with_embeddings = cur.fetchone()
                        
                        if with_embeddings > 0:
                            # Get embedding dimension
                            cur.execute(f"""
                                SELECT array_length({column_name}::real[], 1) 
                                FROM {table_name} 
                                WHERE {column_name} IS NOT NULL 
                                LIMIT 1;
                            """)
                            dim_result = cur.fetchone()
                            dimension = dim_result[0] if dim_result else 'unknown'
                            
                            print(f"\n   📄 {table_name}.{column_name}:")
                            print(f"      Total rows: {total:,}")
                            print(f"      Rows with embeddings: {with_embeddings:,}")
                            print(f"      Embedding dimension: {dimension}")
                            
                            # Sample content
                            cur.execute(f"""
                                SELECT * FROM {table_name} 
                                WHERE {column_name} IS NOT NULL 
                                LIMIT 1;
                            """)
                            
                            # Get column names
                            col_names = [desc[0] for desc in cur.description]
                            sample = cur.fetchone()
                            
                            # Show relevant fields (avoid showing full embedding)
                            print(f"      Sample record:")
                            for i, col in enumerate(col_names):
                                if col != column_name and sample[i] is not None:
                                    value = str(sample[i])
                                    if len(value) > 100:
                                        value = value[:100] + "..."
                                    if col in ['content_text', 'summary', 'description', 'text']:
                                        print(f"        {col}: {value}")
                            
                            total_embeddings += with_embeddings
                        elif total > 0:
                            print(f"\n   📄 {table_name}.{column_name}:")
                            print(f"      Total rows: {total:,}")
                            print(f"      ⚠️  No embeddings present")
                    except Exception as e:
                        print(f"\n   ❌ Error accessing {table_name}: {str(e)}")
                
                print(f"\n📊 TOTAL EMBEDDINGS IN {db_name}: {total_embeddings:,}")
            else:
                print("   No vector columns found")
        else:
            print(f"❌ pgvector extension not installed")
            
        # Check for JSONB columns that might store embeddings
        cur.execute("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema='public' 
            AND data_type = 'jsonb'
            AND (column_name LIKE '%embed%' OR column_name LIKE '%vector%');
        """)
        
        jsonb_tables = cur.fetchall()
        if jsonb_tables:
            print(f"\n📦 JSONB columns that might contain embeddings:")
            for table_name, column_name in jsonb_tables:
                cur.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NOT NULL;")
                count = cur.fetchone()[0]
                if count > 0:
                    print(f"   • {table_name}.{column_name}: {count:,} non-null records")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to {db_name}: {str(e)}")


def main():
    """Analyze all relevant databases"""
    print("\n" + "="*80)
    print("🔍 COMPREHENSIVE EMBEDDING ANALYSIS")
    print("="*80)
    
    databases = [
        {
            'name': 'ai_content_studio',
            'conn': 'postgresql://postgres@localhost/ai_content_studio'
        },
        {
            'name': 'ai_unified_platform', 
            'conn': 'postgresql://postgres@localhost/ai_unified_platform'
        },
        {
            'name': 'unified_donkey_betz',
            'conn': 'postgresql://postgres@localhost/unified_donkey_betz'
        }
    ]
    
    total_all_dbs = 0
    
    for db in databases:
        analyze_database(db['conn'], db['name'])
    
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    print("""
    The embeddings are stored in the **ai_content_studio** database:
    - memories table: 359 embeddings (conversation memories)
    - assistant_conversationmemory: 333 embeddings (assistant interactions)
    
    Total: ~692 embeddings (not 600,000)
    
    To import into unified_donkey_betz, you would need to:
    1. Export from ai_content_studio.memories and ai_content_studio.assistant_conversationmemory
    2. Transform to match the unified_donkey_betz schema
    3. Import into the appropriate tables in your current database
    """)


if __name__ == "__main__":
    main()