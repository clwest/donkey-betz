# Generated manually - Session 730
# Migrates embedding fields from JSONField to pgvector VectorField
# Models: SpiderData, AgentMemory, MemoryCluster, BusinessResearchResult, LegalResearchResult, LegalMemory
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0158_conversationmemory_embedding'),
    ]

    operations = [
        # SpiderData.embedding - Drop and recreate as vector type
        migrations.RunSQL(
            sql="""
                -- Create temp column, copy data, drop old, rename new
                ALTER TABLE core_spiderdata ADD COLUMN embedding_new vector(1536);
                UPDATE core_spiderdata
                SET embedding_new = embedding::text::vector(1536)
                WHERE embedding IS NOT NULL
                  AND embedding::text != 'null'
                  AND embedding::text != '[]';
                ALTER TABLE core_spiderdata DROP COLUMN embedding;
                ALTER TABLE core_spiderdata RENAME COLUMN embedding_new TO embedding;
            """,
            reverse_sql="""
                ALTER TABLE core_spiderdata ADD COLUMN embedding_old jsonb;
                UPDATE core_spiderdata
                SET embedding_old = embedding::text::jsonb
                WHERE embedding IS NOT NULL;
                ALTER TABLE core_spiderdata DROP COLUMN embedding;
                ALTER TABLE core_spiderdata RENAME COLUMN embedding_old TO embedding;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS spiderdata_embedding_hnsw_idx
                ON core_spiderdata
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS spiderdata_embedding_hnsw_idx;",
        ),

        # AgentMemory.embedding
        migrations.RunSQL(
            sql="""
                ALTER TABLE core_agentmemory ADD COLUMN embedding_new vector(1536);
                UPDATE core_agentmemory
                SET embedding_new = embedding::text::vector(1536)
                WHERE embedding IS NOT NULL
                  AND embedding::text != 'null'
                  AND embedding::text != '[]';
                ALTER TABLE core_agentmemory DROP COLUMN embedding;
                ALTER TABLE core_agentmemory RENAME COLUMN embedding_new TO embedding;
            """,
            reverse_sql="""
                ALTER TABLE core_agentmemory ADD COLUMN embedding_old jsonb;
                UPDATE core_agentmemory
                SET embedding_old = embedding::text::jsonb
                WHERE embedding IS NOT NULL;
                ALTER TABLE core_agentmemory DROP COLUMN embedding;
                ALTER TABLE core_agentmemory RENAME COLUMN embedding_old TO embedding;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS agentmemory_embedding_hnsw_idx
                ON core_agentmemory
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS agentmemory_embedding_hnsw_idx;",
        ),

        # MemoryCluster.centroid_embedding
        migrations.RunSQL(
            sql="""
                ALTER TABLE core_memorycluster ADD COLUMN centroid_embedding_new vector(1536);
                UPDATE core_memorycluster
                SET centroid_embedding_new = centroid_embedding::text::vector(1536)
                WHERE centroid_embedding IS NOT NULL
                  AND centroid_embedding::text != 'null'
                  AND centroid_embedding::text != '[]';
                ALTER TABLE core_memorycluster DROP COLUMN centroid_embedding;
                ALTER TABLE core_memorycluster RENAME COLUMN centroid_embedding_new TO centroid_embedding;
            """,
            reverse_sql="""
                ALTER TABLE core_memorycluster ADD COLUMN centroid_embedding_old jsonb;
                UPDATE core_memorycluster
                SET centroid_embedding_old = centroid_embedding::text::jsonb
                WHERE centroid_embedding IS NOT NULL;
                ALTER TABLE core_memorycluster DROP COLUMN centroid_embedding;
                ALTER TABLE core_memorycluster RENAME COLUMN centroid_embedding_old TO centroid_embedding;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS memorycluster_centroid_hnsw_idx
                ON core_memorycluster
                USING hnsw (centroid_embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS memorycluster_centroid_hnsw_idx;",
        ),

        # BusinessResearchResult.embedding
        migrations.RunSQL(
            sql="""
                ALTER TABLE core_businessresearchresult ADD COLUMN embedding_new vector(1536);
                UPDATE core_businessresearchresult
                SET embedding_new = embedding::text::vector(1536)
                WHERE embedding IS NOT NULL
                  AND embedding::text != 'null'
                  AND embedding::text != '[]';
                ALTER TABLE core_businessresearchresult DROP COLUMN embedding;
                ALTER TABLE core_businessresearchresult RENAME COLUMN embedding_new TO embedding;
            """,
            reverse_sql="""
                ALTER TABLE core_businessresearchresult ADD COLUMN embedding_old jsonb;
                UPDATE core_businessresearchresult
                SET embedding_old = embedding::text::jsonb
                WHERE embedding IS NOT NULL;
                ALTER TABLE core_businessresearchresult DROP COLUMN embedding;
                ALTER TABLE core_businessresearchresult RENAME COLUMN embedding_old TO embedding;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS businessresearchresult_embedding_hnsw_idx
                ON core_businessresearchresult
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS businessresearchresult_embedding_hnsw_idx;",
        ),

        # LegalResearchResult.embedding
        migrations.RunSQL(
            sql="""
                ALTER TABLE core_legalresearchresult ADD COLUMN embedding_new vector(1536);
                UPDATE core_legalresearchresult
                SET embedding_new = embedding::text::vector(1536)
                WHERE embedding IS NOT NULL
                  AND embedding::text != 'null'
                  AND embedding::text != '[]';
                ALTER TABLE core_legalresearchresult DROP COLUMN embedding;
                ALTER TABLE core_legalresearchresult RENAME COLUMN embedding_new TO embedding;
            """,
            reverse_sql="""
                ALTER TABLE core_legalresearchresult ADD COLUMN embedding_old jsonb;
                UPDATE core_legalresearchresult
                SET embedding_old = embedding::text::jsonb
                WHERE embedding IS NOT NULL;
                ALTER TABLE core_legalresearchresult DROP COLUMN embedding;
                ALTER TABLE core_legalresearchresult RENAME COLUMN embedding_old TO embedding;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS legalresearchresult_embedding_hnsw_idx
                ON core_legalresearchresult
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS legalresearchresult_embedding_hnsw_idx;",
        ),

        # LegalMemory.embedding
        migrations.RunSQL(
            sql="""
                ALTER TABLE core_legalmemory ADD COLUMN embedding_new vector(1536);
                UPDATE core_legalmemory
                SET embedding_new = embedding::text::vector(1536)
                WHERE embedding IS NOT NULL
                  AND embedding::text != 'null'
                  AND embedding::text != '[]';
                ALTER TABLE core_legalmemory DROP COLUMN embedding;
                ALTER TABLE core_legalmemory RENAME COLUMN embedding_new TO embedding;
            """,
            reverse_sql="""
                ALTER TABLE core_legalmemory ADD COLUMN embedding_old jsonb;
                UPDATE core_legalmemory
                SET embedding_old = embedding::text::jsonb
                WHERE embedding IS NOT NULL;
                ALTER TABLE core_legalmemory DROP COLUMN embedding;
                ALTER TABLE core_legalmemory RENAME COLUMN embedding_old TO embedding;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS legalmemory_embedding_hnsw_idx
                ON core_legalmemory
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS legalmemory_embedding_hnsw_idx;",
        ),
    ]
