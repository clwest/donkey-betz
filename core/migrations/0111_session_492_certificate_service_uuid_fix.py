# Session 492: Fix ContentProvenance history ID fields to use UUID
# Cannot cast bigint to UUID, so we drop and recreate the columns
# This is safe because ContentProvenance table is empty (0 records)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0110_session_484_spider_execution_log"),
    ]

    operations = [
        # Drop existing bigint columns
        migrations.RemoveField(
            model_name="contentprovenance",
            name="audio_history_id",
        ),
        migrations.RemoveField(
            model_name="contentprovenance",
            name="image_history_id",
        ),
        migrations.RemoveField(
            model_name="contentprovenance",
            name="video_history_id",
        ),
        # Add them back as UUID fields
        migrations.AddField(
            model_name="contentprovenance",
            name="audio_history_id",
            field=models.UUIDField(
                blank=True,
                help_text="Link to AudioHistory if content_type is audio",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="contentprovenance",
            name="image_history_id",
            field=models.UUIDField(
                blank=True,
                help_text="Link to ImageHistory if content_type is image",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="contentprovenance",
            name="video_history_id",
            field=models.UUIDField(
                blank=True,
                help_text="Link to VideoHistory if content_type is video",
                null=True,
            ),
        ),
    ]
