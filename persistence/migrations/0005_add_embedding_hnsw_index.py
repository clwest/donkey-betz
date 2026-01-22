from django.db import migrations

class Migration(migrations.Migration):
    # keep the same dependency you already have
    dependencies = [
        ("persistence", "0004_convert_embedding_json_to_vector"),
    ]

    # This migration referenced an embedding model/index that no longer matches the codebase.
    # We intentionally make it a no-op to keep the migration graph consistent.
    operations = []