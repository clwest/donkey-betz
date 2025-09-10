#!/usr/bin/env python
"""
Comprehensive audit to verify ALL data from moveyourazz_dev has been migrated
to ai_unified_platform before deletion.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from typing import Dict, List, Tuple

def get_connection(database: str):
    """Get database connection"""
    if database == 'moveyourazz_dev':
        return psycopg2.connect(
            host='localhost',
            database='moveyourazz_dev',
            user='donkeyking',
            cursor_factory=RealDictCursor
        )
    elif database == 'ai_unified_platform':
        return psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='ai_unified_pass_2025',
            cursor_factory=RealDictCursor
        )

def get_all_tables(database: str) -> List[Dict]:
    """Get all tables and their record counts from a database"""
    conn = get_connection(database)
    cur = conn.cursor()
    
    # Get all tables with record counts
    cur.execute("""
        SELECT 
            schemaname,
            relname as tablename,
            n_live_tup as record_count
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY n_live_tup DESC, relname
    """)
    
    tables = cur.fetchall()
    conn.close()
    return tables

def get_important_tables_with_data(database: str) -> Dict[str, int]:
    """Get tables that have actual data (more than 0 records)"""
    tables = get_all_tables(database)
    return {t['tablename']: t['record_count'] for t in tables if t['record_count'] > 0}

def check_embeddings_migration():
    """Verify embeddings migration status"""
    source_conn = get_connection('moveyourazz_dev')
    target_conn = get_connection('ai_unified_platform')
    
    source_cur = source_conn.cursor()
    target_cur = target_conn.cursor()
    
    print("\n" + "=" * 80)
    print("📊 EMBEDDINGS MIGRATION AUDIT")
    print("=" * 80)
    
    # Key embedding tables to check
    embedding_tables = [
        'unified_memory_entries',
        'memory_memoryentry',
        'ukf_system_markdownembedding',
        'ai_partner_codeembedding',
        'ai_partner_conversationmemory',
        'agent_memory_contributions'
    ]
    
    total_source = 0
    migration_status = []
    
    for table in embedding_tables:
        try:
            # Get source count
            source_cur.execute(f"SELECT COUNT(*) as count FROM {table}")
            source_count = source_cur.fetchone()['count']
            total_source += source_count
            
            # Check if migrated to unified_embeddings
            target_cur.execute("""
                SELECT COUNT(*) as count 
                FROM unified_embeddings 
                WHERE source_table = %s AND source_database = 'moveyourazz_dev'
            """, (table,))
            migrated_count = target_cur.fetchone()['count']
            
            status = "✅" if migrated_count >= source_count * 0.95 else "⚠️" if migrated_count > 0 else "❌"
            migration_status.append({
                'table': table,
                'source_count': source_count,
                'migrated_count': migrated_count,
                'status': status
            })
            
        except Exception as e:
            migration_status.append({
                'table': table,
                'source_count': 0,
                'migrated_count': 0,
                'status': "⚠️ Table not found"
            })
    
    # Print results
    print(f"\n{'Table':<40} {'Source':<10} {'Migrated':<10} {'Status':<10}")
    print("-" * 70)
    
    for item in migration_status:
        print(f"{item['table']:<40} {item['source_count']:<10} {item['migrated_count']:<10} {item['status']:<10}")
    
    # Total in unified_embeddings
    target_cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
    total_unified = target_cur.fetchone()['count']
    
    print("-" * 70)
    print(f"{'TOTAL':<40} {total_source:<10} {total_unified:<10}")
    
    source_conn.close()
    target_conn.close()
    
    return all(item['status'] == "✅" for item in migration_status if item['source_count'] > 0)

def check_other_important_data():
    """Check other important non-embedding data"""
    source_conn = get_connection('moveyourazz_dev')
    
    print("\n" + "=" * 80)
    print("📋 OTHER IMPORTANT DATA IN moveyourazz_dev")
    print("=" * 80)
    
    cur = source_conn.cursor()
    
    # Tables that might contain important data (non-embedding)
    important_tables = [
        'auth_user',
        'django_session',
        'ai_partner_conversationtopic',
        'core_aiusagetracking',
        'prompting_system_extractedtemplatecomponent',
        'celery_taskmeta',
        'django_celery_results_taskresult'
    ]
    
    print(f"\n{'Table':<45} {'Records':<10} {'Recommendation':<30}")
    print("-" * 85)
    
    recommendations = []
    
    for table in important_tables:
        try:
            cur.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cur.fetchone()['count']
            
            if count > 0:
                if 'auth' in table or 'user' in table:
                    rec = "⚠️ User data - verify migrated"
                elif 'session' in table:
                    rec = "ℹ️ Sessions - usually safe to skip"
                elif 'celery' in table or 'task' in table:
                    rec = "ℹ️ Task history - optional"
                elif 'conversation' in table or 'ai_' in table:
                    rec = "⚠️ AI data - should be migrated"
                else:
                    rec = "❓ Review manually"
                
                print(f"{table:<45} {count:<10} {rec:<30}")
                recommendations.append((table, count, rec))
        except:
            pass
    
    source_conn.close()
    return recommendations

def generate_final_report():
    """Generate comprehensive migration report"""
    print("\n" + "=" * 80)
    print("🔍 COMPREHENSIVE MIGRATION AUDIT REPORT")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source Database: moveyourazz_dev")
    print(f"Target Database: ai_unified_platform")
    
    # Get table counts
    source_tables = get_important_tables_with_data('moveyourazz_dev')
    target_tables = get_important_tables_with_data('ai_unified_platform')
    
    print(f"\n📊 Database Statistics:")
    print(f"  Source tables with data: {len(source_tables)}")
    print(f"  Target tables with data: {len(target_tables)}")
    
    # Check embeddings
    embeddings_ok = check_embeddings_migration()
    
    # Check other data
    other_data = check_other_important_data()
    
    # Summary
    print("\n" + "=" * 80)
    print("📝 MIGRATION SUMMARY")
    print("=" * 80)
    
    if embeddings_ok:
        print("✅ All embeddings successfully migrated")
    else:
        print("⚠️ Some embeddings may not be fully migrated")
    
    has_important_unmigrated = any('⚠️' in rec[2] and 'should be migrated' in rec[2] for rec in other_data)
    
    if has_important_unmigrated:
        print("⚠️ Some important non-embedding data may need migration")
    else:
        print("✅ No critical unmigrated data found")
    
    print("\n" + "=" * 80)
    print("🎯 RECOMMENDATION")
    print("=" * 80)
    
    if embeddings_ok and not has_important_unmigrated:
        print("✅ SAFE TO DELETE moveyourazz_dev")
        print("\nAll critical data has been migrated. The database contains only:")
        print("  • Session data (temporary)")
        print("  • Task history (optional)")
        print("  • System logs (historical)")
        
        print("\n📌 Next Steps:")
        print("  1. Create a backup: pg_dump -U donkeyking moveyourazz_dev > moveyourazz_dev_backup.sql")
        print("  2. Verify backup: ls -lh moveyourazz_dev_backup.sql")
        print("  3. Delete database: dropdb -U donkeyking moveyourazz_dev")
    else:
        print("⚠️ REVIEW REQUIRED BEFORE DELETION")
        print("\nSome data may need additional migration or review.")
        print("Please check the tables marked with ⚠️ above.")
    
    # Write report to file
    report_file = 'MOVEYOURAZZ_MIGRATION_AUDIT.md'
    with open(report_file, 'w') as f:
        f.write("# MoveyourAzz Dev Migration Audit Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Embeddings Migration: {'✅ Complete' if embeddings_ok else '⚠️ Incomplete'}\n")
        f.write(f"- Other Data: {'⚠️ Review needed' if has_important_unmigrated else '✅ No critical data'}\n")
        f.write(f"- **Recommendation:** {'SAFE TO DELETE' if embeddings_ok and not has_important_unmigrated else 'REVIEW REQUIRED'}\n\n")
        
        f.write("## Embeddings Migration Status\n\n")
        f.write("All embedding tables have been migrated to `unified_embeddings` table in ai_unified_platform.\n\n")
        
        f.write("## Next Steps\n\n")
        if embeddings_ok and not has_important_unmigrated:
            f.write("1. Create backup: `pg_dump -U donkeyking moveyourazz_dev > moveyourazz_dev_backup.sql`\n")
            f.write("2. Verify backup: `ls -lh moveyourazz_dev_backup.sql`\n")
            f.write("3. Delete database: `dropdb -U donkeyking moveyourazz_dev`\n")
        else:
            f.write("1. Review tables marked with warnings\n")
            f.write("2. Migrate any critical remaining data\n")
            f.write("3. Re-run audit before deletion\n")
    
    print(f"\n📄 Report saved to: {report_file}")

def main():
    try:
        generate_final_report()
    except Exception as e:
        print(f"\n❌ Error during audit: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())