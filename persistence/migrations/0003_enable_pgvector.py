from django.db import migrations
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    dependencies = [
        ("persistence", "0002_alter_unifiedembedding_creator_agent" ),
    ]
    operations = [
        VectorExtension(),  # CREATE EXTENSION IF NOT EXISTS vector
    ]