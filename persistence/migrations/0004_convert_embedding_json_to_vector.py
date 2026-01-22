from django.db import migrations
from django.apps import apps

def backfill_json_to_vector(apps, schema_editor):
    UnifiedEmbedding = apps.get_model("persistence", "UnifiedEmbedding")
    # Only rows that actually have JSON arrays
    batch, BATCH = [], 1000
    for row in UnifiedEmbedding.objects.all().only("id", "embedding").iterator():
        vec = row.embedding
        if isinstance(vec, list) and vec:
            # temp field we'll add below
            row.embedding_vec = vec
            batch.append(row)
            if len(batch) >= BATCH:
                UnifiedEmbedding.objects.bulk_update(batch, ["embedding_vec"])
                batch.clear()
    if batch:
        UnifiedEmbedding.objects.bulk_update(batch, ["embedding_vec"])

class Migration(migrations.Migration):
    dependencies = [
        ("persistence", "0003_enable_pgvector"),  # ← step 1 filename
    ]

    operations = [
        # 1) Add a temporary vector field
        migrations.AddField(
            model_name="unifiedembedding",
            name="embedding_vec",
            field=__import__("pgvector.django", fromlist=["VectorField"]).VectorField(
                dimensions=1536, null=True
            ),
        ),
        # 2) Copy JSON → vector
        migrations.RunPython(backfill_json_to_vector, migrations.RunPython.noop),
        # 3) Drop old JSON field
        migrations.RemoveField(model_name="unifiedembedding", name="embedding"),
        # 4) Rename new vector field to 'embedding'
        migrations.RenameField(
            model_name="unifiedembedding", old_name="embedding_vec", new_name="embedding"
        ),
    ]