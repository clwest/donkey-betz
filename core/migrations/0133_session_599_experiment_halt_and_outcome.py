# Generated for Session 599 - Adds halt conditions and outcome classification to Experiment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0132_session_597_experiment_learning'),
    ]

    operations = [
        # Session 599: Automatic Fail Fast - Halt Conditions
        migrations.AddField(
            model_name='experiment',
            name='halt_conditions',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Thresholds for automatic experiment halt'
            ),
        ),
        migrations.AddField(
            model_name='experiment',
            name='is_halted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='experiment',
            name='halted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='experiment',
            name='halted_by',
            field=models.CharField(
                blank=True,
                help_text="'auto' for system halt, or user name for manual halt",
                max_length=100
            ),
        ),
        migrations.AddField(
            model_name='experiment',
            name='halt_reason',
            field=models.TextField(
                blank=True,
                help_text='Reason for halt (which condition triggered)'
            ),
        ),

        # Session 599: Outcome Classification (PASS/LEARN/FAIL)
        migrations.AddField(
            model_name='experiment',
            name='outcome_classification',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('pass', 'PASS'),
                    ('learn', 'LEARN'),
                    ('fail', 'FAIL'),
                ],
                default='pending',
                help_text='Final outcome: PASS (proceed), LEARN (insights only), FAIL (rollback)',
                max_length=20
            ),
        ),
    ]
