from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0298_vip_invite_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='llmcalllog',
            name='trace_id',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text='PA request trace ID for joining LLM calls to Celery tasks',
                max_length=64,
            ),
        ),
    ]
