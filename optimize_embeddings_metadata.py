#!/usr/bin/env python3
"""
Optimize and enrich metadata for migrated embeddings
"""

import os
import sys
import django
import psycopg2
from psycopg2.extras import execute_batch
import json
from collections import defaultdict
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()


class EmbeddingMetadataOptimizer:
    """Optimize and enrich metadata for embeddings post-migration"""
    
    def __init__(self):
        self.conn = psycopg2.connect('postgresql://postgres@localhost/unified_donkey_betz')
        self.stats = defaultdict(int)
        
    def analyze_current_metadata(self):
        """Analyze current state of metadata"""
        print("\n📊 ANALYZING CURRENT METADATA...")
        
        with self.conn.cursor() as cur:
            # Get content type distribution
            cur.execute("""
                SELECT content_type, COUNT(*) 
                FROM unified_embeddings 
                GROUP BY content_type 
                ORDER BY COUNT(*) DESC
            """)
            
            print("\n📈 Content Type Distribution:")
            for content_type, count in cur.fetchall():
                print(f"   • {content_type}: {count:,}")
            
            # Check for missing metadata
            cur.execute("""
                SELECT COUNT(*) 
                FROM unified_embeddings 
                WHERE metadata IS NULL OR metadata = '{}'::jsonb
            """)
            empty_metadata = cur.fetchone()[0]
            print(f"\n⚠️  Embeddings with empty metadata: {empty_metadata:,}")
            
            # Sample metadata structures
            cur.execute("""
                SELECT DISTINCT jsonb_object_keys(metadata) as key
                FROM unified_embeddings
                WHERE metadata IS NOT NULL AND metadata != '{}'::jsonb
                LIMIT 20
            """)
            
            keys = [row[0] for row in cur.fetchall()]
            if keys:
                print(f"\n🔑 Common metadata keys: {', '.join(keys)}")
                
    def enrich_code_embeddings(self):
        """Add additional metadata to code embeddings"""
        print("\n💻 ENRICHING CODE EMBEDDINGS...")
        
        with self.conn.cursor() as cur:
            # Update code embeddings with language detection
            cur.execute("""
                UPDATE unified_embeddings
                SET metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{language}',
                    CASE 
                        WHEN content_text LIKE '%import %' OR content_text LIKE '%def %' THEN '"python"'
                        WHEN content_text LIKE '%function %' OR content_text LIKE '%const %' THEN '"javascript"'
                        WHEN content_text LIKE '%class %' AND content_text LIKE '%public %' THEN '"java"'
                        ELSE '"unknown"'
                    END::jsonb
                )
                WHERE content_type = 'code'
                AND (metadata->>'language' IS NULL OR metadata->>'language' = '')
            """)
            
            affected = cur.rowcount
            print(f"   ✅ Added language metadata to {affected:,} code embeddings")
            
            # Add complexity score based on content length and structure
            cur.execute("""
                UPDATE unified_embeddings
                SET metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{complexity_score}',
                    to_jsonb(
                        LEAST(1.0, 
                            (LENGTH(content_text) / 1000.0) * 0.3 + 
                            (LENGTH(content_text) - LENGTH(REPLACE(content_text, E'\\n', ''))) * 0.01
                        )
                    )
                )
                WHERE content_type = 'code'
                AND metadata->>'complexity_score' IS NULL
            """)
            
            affected = cur.rowcount
            print(f"   ✅ Added complexity scores to {affected:,} code embeddings")
            
            self.conn.commit()
            
    def categorize_content(self):
        """Categorize content into more specific types with agent domains"""
        print("\n🏷️  CATEGORIZING CONTENT WITH AGENT TYPES...")
        
        # Define agent types/domains with associated keywords and patterns
        agent_domains = {
            'code': {
                'keywords': ['def ', 'class ', 'import ', 'function ', 'const ', 'let ', 'var ', 
                            'public ', 'private ', 'return ', 'if __name__', '#!/usr/bin/env'],
                'categories': {
                    'python': ['def ', 'import ', '__init__', 'self.', 'from ', '__name__'],
                    'javascript': ['const ', 'let ', 'var ', 'function ', '=>', 'require('],
                    'typescript': ['interface ', 'type ', ': string', ': number', 'export '],
                    'database': ['CREATE TABLE', 'ALTER TABLE', 'SELECT ', 'INSERT INTO'],
                    'api': ['endpoint', '@api_view', '@router', 'request.', 'response.'],
                }
            },
            'legal': {
                'keywords': ['pursuant', 'hereby', 'whereas', 'agreement', 'contract', 'liability',
                            'jurisdiction', 'plaintiff', 'defendant', 'motion', 'court', 'filing'],
                'categories': {
                    'contracts': ['agreement', 'party', 'terms', 'conditions', 'obligations'],
                    'litigation': ['motion', 'complaint', 'filing', 'discovery', 'deposition'],
                    'compliance': ['regulation', 'compliance', 'audit', 'policy', 'procedure']
                }
            },
            'sports': {
                'keywords': ['betting', 'odds', 'spread', 'moneyline', 'parlay', 'kelly criterion',
                            'sportsbook', 'wager', 'ncaaf', 'nfl', 'nba', 'mlb'],
                'categories': {
                    'betting_analytics': ['odds', 'kelly', 'ev', 'arbitrage', 'value bet'],
                    'game_data': ['score', 'team', 'player', 'stats', 'matchup'],
                    'market_analysis': ['line movement', 'public betting', 'sharp money']
                }
            },
            'content': {
                'keywords': ['article', 'blog', 'post', 'content', 'write', 'draft', 'publish',
                            'seo', 'headline', 'paragraph', 'section'],
                'categories': {
                    'blog_posts': ['blog', 'article', 'post', 'published', 'author'],
                    'marketing': ['seo', 'keywords', 'campaign', 'audience', 'engagement'],
                    'documentation': ['readme', 'docs', 'guide', 'tutorial', 'example']
                }
            },
            'conversation': {
                'keywords': ['user:', 'assistant:', 'human:', 'ai:', 'question', 'answer',
                            'response', 'chat', 'message', 'said'],
                'categories': {
                    'user_interactions': ['user:', 'human:', 'question', 'asked'],
                    'assistant_responses': ['assistant:', 'ai:', 'response', 'answered'],
                    'dialog_context': ['conversation', 'context', 'history', 'thread']
                }
            },
            'agent': {
                'keywords': ['agent', 'tool', 'function', 'execute', 'orchestrate', 'workflow',
                            'pipeline', 'task', 'automation'],
                'categories': {
                    'agent_definitions': ['agent:', 'tools:', 'capabilities:', 'description:'],
                    'workflows': ['workflow', 'pipeline', 'sequence', 'orchestration'],
                    'automation': ['automate', 'scheduled', 'trigger', 'event', 'handler']
                }
            },
            'financial': {
                'keywords': ['transaction', 'payment', 'invoice', 'expense', 'revenue', 'budget',
                            'accounting', 'tax', 'profit', 'loss', 'balance'],
                'categories': {
                    'transactions': ['payment', 'transaction', 'transfer', 'debit', 'credit'],
                    'reporting': ['report', 'statement', 'summary', 'analysis', 'metrics'],
                    'budgeting': ['budget', 'forecast', 'projection', 'variance']
                }
            },
            'medical': {
                'keywords': ['patient', 'diagnosis', 'treatment', 'medication', 'symptoms',
                            'prescription', 'health', 'medical', 'clinical'],
                'categories': {
                    'clinical': ['diagnosis', 'treatment', 'procedure', 'examination'],
                    'pharmacy': ['medication', 'prescription', 'dosage', 'drug'],
                    'records': ['patient', 'history', 'chart', 'notes', 'records']
                }
            }
        }
        
        categories = {
            'api_documentation': ['endpoint', 'request', 'response', 'api', 'rest'],
            'database_schema': ['table', 'column', 'index', 'foreign key', 'constraint'],
            'configuration': ['config', 'settings', 'environment', 'env', 'setup'],
            'testing': ['test', 'assert', 'expect', 'mock', 'fixture'],
            'frontend': ['react', 'component', 'render', 'state', 'props'],
            'backend': ['django', 'model', 'view', 'serializer', 'queryset'],
            'deployment': ['docker', 'kubernetes', 'deploy', 'ci/cd', 'pipeline'],
            'documentation': ['readme', 'docs', 'guide', 'tutorial', 'example']
        }
        
        with self.conn.cursor() as cur:
            # First, classify by agent domain/type
            print("\n   🤖 Classifying agent domains...")
            for domain, config in agent_domains.items():
                # Build keyword conditions for domain detection
                domain_conditions = []
                for keyword in config['keywords']:
                    domain_conditions.append(f"LOWER(content_text) LIKE '%{keyword.lower()}%'")
                
                if domain_conditions:
                    condition_str = ' OR '.join(domain_conditions)
                    
                    cur.execute(f"""
                        UPDATE unified_embeddings
                        SET metadata = jsonb_set(
                            jsonb_set(
                                COALESCE(metadata, '{{}}'::jsonb),
                                '{{agent_type}}',
                                '"{domain}"'::jsonb
                            ),
                            '{{agent_domain}}',
                            '"{domain}"'::jsonb
                        )
                        WHERE ({condition_str})
                        AND (metadata->>'agent_type' IS NULL OR metadata->>'agent_type' = '')
                    """)
                    
                    affected = cur.rowcount
                    if affected > 0:
                        print(f"      ✅ Classified {affected:,} embeddings as domain '{domain}'")
                        self.stats[f'domain_{domain}'] = affected
                
                # Now classify sub-categories within each domain
                for subcategory, subkeywords in config.get('categories', {}).items():
                    sub_conditions = []
                    for keyword in subkeywords:
                        sub_conditions.append(f"LOWER(content_text) LIKE '%{keyword.lower()}%'")
                    
                    if sub_conditions:
                        sub_condition_str = ' OR '.join(sub_conditions)
                        
                        cur.execute(f"""
                            UPDATE unified_embeddings
                            SET metadata = jsonb_set(
                                COALESCE(metadata, '{{}}'::jsonb),
                                '{{subcategory}}',
                                '"{subcategory}"'::jsonb
                            )
                            WHERE metadata->>'agent_domain' = '{domain}'
                            AND ({sub_condition_str})
                            AND (metadata->>'subcategory' IS NULL OR metadata->>'subcategory' = '')
                        """)
                        
                        sub_affected = cur.rowcount
                        if sub_affected > 0:
                            print(f"         • {subcategory}: {sub_affected:,} items")
            
            # Then apply general categories for backwards compatibility
            print("\n   📂 Applying general categories...")
            for category, keywords in categories.items():
                keyword_conditions = ' OR '.join([f"LOWER(content_text) LIKE '%{kw}%'" for kw in keywords])
                
                cur.execute(f"""
                    UPDATE unified_embeddings
                    SET metadata = jsonb_set(
                        COALESCE(metadata, '{{}}'::jsonb),
                        '{{category}}',
                        '"{category}"'::jsonb
                    )
                    WHERE content_type IN ('code', 'unknown', 'markdown_knowledge')
                    AND ({keyword_conditions})
                    AND (metadata->>'category' IS NULL OR metadata->>'category' = '')
                """)
                
                affected = cur.rowcount
                if affected > 0:
                    print(f"      ✅ Categorized {affected:,} embeddings as '{category}'")
                    self.stats[category] = affected
                    
            self.conn.commit()
            
    def add_importance_scores(self):
        """Calculate and add importance scores based on content patterns"""
        print("\n⭐ CALCULATING IMPORTANCE SCORES...")
        
        with self.conn.cursor() as cur:
            # Higher importance for certain patterns
            importance_patterns = [
                ("content_text LIKE '%class %' AND content_text LIKE '%__init__%'", 0.9, "main classes"),
                ("content_text LIKE '%def main%' OR content_text LIKE '%if __name__%'", 0.85, "entry points"),
                ("content_text LIKE '%CREATE TABLE%' OR content_text LIKE '%ALTER TABLE%'", 0.8, "database schemas"),
                ("content_text LIKE '%API%' AND content_text LIKE '%endpoint%'", 0.75, "API definitions"),
                ("LENGTH(content_text) > 5000", 0.7, "comprehensive documents")
            ]
            
            for pattern, score, description in importance_patterns:
                cur.execute(f"""
                    UPDATE unified_embeddings
                    SET importance_score = {score}
                    WHERE {pattern}
                    AND importance_score < {score}
                """)
                
                affected = cur.rowcount
                if affected > 0:
                    print(f"   ✅ Set importance {score} for {affected:,} {description}")
                    
            self.conn.commit()
            
    def create_specialized_indexes(self):
        """Create specialized indexes for better query performance"""
        print("\n🔍 CREATING SPECIALIZED INDEXES...")
        
        indexes = [
            ("idx_code_embeddings", "content_type = 'code'"),
            ("idx_high_importance", "importance_score > 0.7"),
            ("idx_categorized", "metadata->>'category' IS NOT NULL"),
            ("idx_recent_migration", "migrated_at > NOW() - INTERVAL '1 day'")
        ]
        
        with self.conn.cursor() as cur:
            for index_name, condition in indexes:
                try:
                    cur.execute(f"""
                        CREATE INDEX IF NOT EXISTS {index_name}
                        ON unified_embeddings({condition})
                    """)
                    print(f"   ✅ Created index: {index_name}")
                except Exception as e:
                    print(f"   ⚠️  Index {index_name} might already exist: {str(e)[:50]}")
                    
            self.conn.commit()
            
    def create_useful_views(self):
        """Create database views for common queries"""
        print("\n📋 CREATING USEFUL VIEWS...")
        
        views = [
            ("code_embeddings_view", """
                CREATE OR REPLACE VIEW code_embeddings_view AS
                SELECT id, content_text, embedding, metadata, importance_score
                FROM unified_embeddings
                WHERE content_type = 'code'
                ORDER BY importance_score DESC
            """),
            ("high_value_embeddings", """
                CREATE OR REPLACE VIEW high_value_embeddings AS
                SELECT id, content_type, content_text, metadata, importance_score
                FROM unified_embeddings
                WHERE importance_score > 0.7
                OR metadata->>'category' IN ('api_documentation', 'database_schema')
                ORDER BY importance_score DESC
            """),
            ("recent_conversations", """
                CREATE OR REPLACE VIEW recent_conversations AS
                SELECT id, content_text, metadata, created_at
                FROM unified_embeddings
                WHERE content_type IN ('conversation', 'assistant_conversation')
                AND created_at > NOW() - INTERVAL '30 days'
                ORDER BY created_at DESC
            """)
        ]
        
        with self.conn.cursor() as cur:
            for view_name, view_sql in views:
                try:
                    cur.execute(view_sql)
                    print(f"   ✅ Created view: {view_name}")
                except Exception as e:
                    print(f"   ⚠️  Error creating {view_name}: {str(e)[:50]}")
                    
            self.conn.commit()
            
    def generate_statistics_report(self):
        """Generate final statistics report"""
        print("\n" + "="*80)
        print("📊 METADATA OPTIMIZATION COMPLETE")
        print("="*80)
        
        with self.conn.cursor() as cur:
            # Total embeddings
            cur.execute("SELECT COUNT(*) FROM unified_embeddings")
            total = cur.fetchone()[0]
            
            # By content type
            cur.execute("""
                SELECT content_type, COUNT(*), AVG(importance_score)
                FROM unified_embeddings
                GROUP BY content_type
                ORDER BY COUNT(*) DESC
            """)
            
            print(f"\n📈 Embedding Statistics:")
            print(f"   Total Embeddings: {total:,}")
            print(f"\n   By Content Type:")
            for content_type, count, avg_importance in cur.fetchall():
                print(f"      • {content_type}: {count:,} (avg importance: {avg_importance:.2f})")
            
            # Categories
            cur.execute("""
                SELECT metadata->>'category' as category, COUNT(*)
                FROM unified_embeddings
                WHERE metadata->>'category' IS NOT NULL
                GROUP BY metadata->>'category'
                ORDER BY COUNT(*) DESC
            """)
            
            categories = cur.fetchall()
            if categories:
                print(f"\n   By Category:")
                for category, count in categories:
                    print(f"      • {category}: {count:,}")
            
            # High importance items
            cur.execute("SELECT COUNT(*) FROM unified_embeddings WHERE importance_score > 0.7")
            high_importance = cur.fetchone()[0]
            print(f"\n   High Importance Embeddings: {high_importance:,}")
            
            print("\n✅ Metadata optimization complete!")
            print("   Your embeddings are now enriched with:")
            print("   • Content categorization")
            print("   • Importance scoring")
            print("   • Language detection (for code)")
            print("   • Optimized indexes for fast queries")
            print("   • Useful database views")
            
    def run_optimization(self):
        """Run all optimization steps"""
        try:
            self.analyze_current_metadata()
            self.enrich_code_embeddings()
            self.categorize_content()
            self.add_importance_scores()
            self.create_specialized_indexes()
            self.create_useful_views()
            self.generate_statistics_report()
        finally:
            self.conn.close()


if __name__ == "__main__":
    print("\n🚀 Starting Embedding Metadata Optimization...")
    optimizer = EmbeddingMetadataOptimizer()
    optimizer.run_optimization()