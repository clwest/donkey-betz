# Generated manually - Session 730
# Migrates DocumentEmbedding.embedding_vector from JSONField to pgvector VectorField
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0036_session_451_user_upload_support'),
    ]

    operations = [
        # DocumentEmbedding.embedding_vector - Drop and recreate as vector type
        migrations.RunSQL(
            sql="""
                -- Create temp column, copy data, drop old, rename new
                ALTER TABLE content_documentembedding ADD COLUMN embedding_vector_new vector(1536);
                UPDATE content_documentembedding
                SET embedding_vector_new = embedding_vector::text::vector(1536)
                WHERE embedding_vector IS NOT NULL
                  AND embedding_vector::text != 'null'
                  AND embedding_vector::text != '[]';
                ALTER TABLE content_documentembedding DROP COLUMN embedding_vector;
                ALTER TABLE content_documentembedding RENAME COLUMN embedding_vector_new TO embedding_vector;
            """,
            reverse_sql="""
                ALTER TABLE content_documentembedding ADD COLUMN embedding_vector_old jsonb;
                UPDATE content_documentembedding
                SET embedding_vector_old = embedding_vector::text::jsonb
                WHERE embedding_vector IS NOT NULL;
                ALTER TABLE content_documentembedding DROP COLUMN embedding_vector;
                ALTER TABLE content_documentembedding RENAME COLUMN embedding_vector_old TO embedding_vector;
            """,
        ),
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS documentembedding_vector_hnsw_idx
                ON content_documentembedding
                USING hnsw (embedding_vector vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS documentembedding_vector_hnsw_idx;",
        ),
    ]
