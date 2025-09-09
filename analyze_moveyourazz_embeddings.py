#!/usr/bin/env python3
"""
Comprehensive analysis of embeddings in moveyourazz_dev database
"""

import psycopg2
import json

def main():
    print("\n" + "="*80)
    print("🔍 MOVEYOURAZZ_DEV EMBEDDING ANALYSIS")
    print("="*80)
    
    conn = psycopg2.connect('postgresql://postgres@localhost/moveyourazz_dev')
    cur = conn.cursor()
    
    # Get all tables with vector columns
    cur.execute("""
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema='public' AND udt_name='vector'
        ORDER BY table_name;
    """)
    
    vector_tables = cur.fetchall()
    
    print(f"\n📊 Found {len(vector_tables)} vector columns across tables")
    print("-" * 80)
    
    total_embeddings = 0
    table_summary = {}
    
    for table_name, column_name in vector_tables:
        try:
            # Count total rows and rows with embeddings
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
                
                print(f"\n✅ {table_name}.{column_name}")
                print(f"   Total rows: {total:,}")
                print(f"   With embeddings: {with_embeddings:,}")
                print(f"   Dimension: {dimension}")
                
                # Get sample content for context
                cur.execute(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    AND column_name NOT LIKE '%embedding%'
                    AND column_name NOT LIKE '%vector%'
                    AND data_type IN ('text', 'character varying')
                    LIMIT 3;
                """)
                text_columns = [col[0] for col in cur.fetchall()]
                
                if text_columns:
                    cur.execute(f"""
                        SELECT {', '.join(text_columns)} 
                        FROM {table_name} 
                        WHERE {column_name} IS NOT NULL 
                        LIMIT 1;
                    """)
                    sample = cur.fetchone()
                    if sample:
                        print(f"   Sample content:")
                        for i, col in enumerate(text_columns):
                            if sample[i]:
                                content = str(sample[i])[:100]
                                if len(str(sample[i])) > 100:
                                    content += "..."
                                print(f"     {col}: {content}")
                
                total_embeddings += with_embeddings
                
                if table_name not in table_summary:
                    table_summary[table_name] = 0
                table_summary[table_name] += with_embeddings
                
            elif total > 0:
                print(f"\n⚠️  {table_name}.{column_name}")
                print(f"   Total rows: {total:,} (but no embeddings)")
                
        except Exception as e:
            print(f"\n❌ Error with {table_name}.{column_name}: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    
    print(f"\n🎯 TOTAL EMBEDDINGS: {total_embeddings:,}")
    
    if table_summary:
        print("\n📈 Top tables by embedding count:")
        sorted_tables = sorted(table_summary.items(), key=lambda x: x[1], reverse=True)
        for table, count in sorted_tables[:10]:
            percentage = (count / total_embeddings) * 100
            print(f"   • {table}: {count:,} ({percentage:.1f}%)")
    
    # Check for code-specific content
    print("\n💻 Code-Related Tables:")
    code_tables = [t for t, _ in vector_tables if 'code' in t.lower()]
    if code_tables:
        for table in code_tables:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"   • {table}: {count:,} rows")
    else:
        print("   No code embedding tables found with data")
    
    # Check if there are other ways code might be stored
    print("\n🔍 Checking for code in other tables...")
    
    # Check unified_memory_entries for code content
    cur.execute("""
        SELECT COUNT(*) 
        FROM unified_memory_entries 
        WHERE embedding IS NOT NULL 
        AND (content LIKE '%def %' OR content LIKE '%class %' OR content LIKE '%import %');
    """)
    code_memories = cur.fetchone()[0]
    if code_memories > 0:
        print(f"   • unified_memory_entries with code patterns: {code_memories:,}")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    
    if total_embeddings >= 600000:
        print(f"\n🎉 Found {total_embeddings:,} embeddings - this matches the 600k+ claim!")
    else:
        print(f"\n📝 Found {total_embeddings:,} embeddings total")
        print(f"   Still substantial but not quite 600k")
    
    print("""
    The embeddings are primarily in:
    - ai_partner_conversationembedding: Conversation history
    - unified_memory_entries: Unified memory system
    
    To import into unified_donkey_betz, you'll need to migrate these tables.
    """)


if __name__ == "__main__":
    main()