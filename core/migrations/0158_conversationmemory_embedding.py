# Generated manually - Session 729
# Adds pgvector embedding field to ConversationMemory for semantic search
from django.db import migrations
import pgvector.django


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0157_intelligent_prompting_metrics'),
    ]

    operations = [
        # First drop the JSONField column if it exists (from earlier attempt)
        migrations.RunSQL(
            sql="ALTER TABLE core_conversation_memory DROP COLUMN IF EXISTS embedding;",
            reverse_sql="SELECT 1;",  # No-op for reverse
        ),
        # Add pgvector VectorField
        migrations.AddField(
            model_name='conversationmemory',
            name='embedding',
            field=pgvector.django.VectorField(
                dimensions=1536,
                blank=True,
                help_text='Vector embedding for semantic search (pgvector)',
                null=True
            ),
        ),
        # Add HNSW index for fast approximate nearest neighbor search
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS conversation_memory_embedding_hnsw_idx
                ON core_conversation_memory
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """,
            reverse_sql="DROP INDEX IF EXISTS conversation_memory_embedding_hnsw_idx;",
        ),
    ]
