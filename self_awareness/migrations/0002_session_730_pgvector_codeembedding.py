# Generated manually - Session 730
# Migrates CodeEmbedding.embedding_vector from JSONField to pgvector VectorField
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('self_awareness', '0001_initial'),
    ]

    operations = [
        # CodeEmbedding.embedding_vector - Drop and recreate as vector type
        # Note: Table may be empty, but we still convert for future use
        migrations.RunSQL(
            sql="""
                -- Create temp column, copy data, drop old, rename new
                ALTER TABLE self_awareness_codeembedding ADD COLUMN embedding_vector_new vector(1536);
                UPDATE self_awareness_codeembedding
                SET embedding_vector_new = embedding_vector::text::vector(1536)
                WHERE embedding_vector IS NOT NULL
                  AND embedding_vector::text != 'null'
                  AND embedding_vector::text != '[]';
                ALTER TABLE self_awareness_codeembedding DROP COLUMN embedding_vector;
                ALTER TABLE self_awareness_codeembedding RENAME COLUMN embedding_vector_new TO embedding_vector;
            """,
            reverse_sql="""
                ALTER TABLE self_awareness_codeembedding ADD COLUMN embedding_vector_old jsonb;
                UPDATE self_awareness_codeembedding
                SET embedding_vector_old = embedding_vector::text::jsonb
                WHERE embedding_vector IS NOT NULL;
                ALTER TABLE self_awareness_codeembedding DROP COLUMN embedding_vector;
                ALTER TABLE self_awareness_codeembedding RENAME COLUMN embedding_vector_old TO embedding_vector;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS codeembedding_vector_hnsw_idx
                ON self_awareness_codeembedding
                USING hnsw (embedding_vector vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS codeembedding_vector_hnsw_idx;",
        ),
    ]
