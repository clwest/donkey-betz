# Session 1049: Sync ORM Meta.indexes with existing HNSW index in DB.
# Migration 0037 created the index via raw SQL as 'documentembedding_vector_hnsw_idx'.
# This migration tells Django's state about the ORM-defined index without touching the DB.

import pgvector.django.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0039_session_949_risk_aware_rag"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddIndex(
                    model_name="documentembedding",
                    index=pgvector.django.indexes.HnswIndex(
                        ef_construction=64,
                        fields=["embedding_vector"],
                        m=16,
                        name="docembed_vector_hnsw_idx",
                        opclasses=["vector_cosine_ops"],
                    ),
                ),
            ],
            database_operations=[
                # No-op: index already exists via 0037 raw SQL migration
            ],
        ),
    ]
