# Generated manually - Session 59: Fix UUID field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_workflowhistory_workflowfavorite_and_more'),
    ]

    operations = [
        # Remove the old IntegerField
        migrations.RemoveField(
            model_name='workflowhistory',
            name='input_image_id',
        ),
        # Add the new UUIDField
        migrations.AddField(
            model_name='workflowhistory',
            name='input_image_id',
            field=models.UUIDField(blank=True, help_text='ImageHistory UUID if workflow used an input image', null=True),
        ),
    ]
