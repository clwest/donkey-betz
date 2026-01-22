# Generated manually for Session 561 - Line Movement Charts

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0125_session_558_bankroll_tracker'),
    ]

    operations = [
        migrations.CreateModel(
            name='OddsSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, help_text='The Odds API game ID', max_length=100)),
                ('sport_key', models.CharField(db_index=True, max_length=50)),
                ('home_team', models.CharField(max_length=100)),
                ('away_team', models.CharField(max_length=100)),
                ('commence_time', models.DateTimeField(help_text='Game start time')),
                ('bookmaker', models.CharField(db_index=True, max_length=50)),
                ('bookmaker_title', models.CharField(blank=True, max_length=100)),
                ('market', models.CharField(choices=[('h2h', 'Moneyline'), ('spreads', 'Spread'), ('totals', 'Totals')], db_index=True, max_length=20)),
                ('outcome_name', models.CharField(help_text='Team name, Over, or Under', max_length=100)),
                ('price', models.IntegerField(help_text='American odds (e.g., -110, +150)')),
                ('point', models.DecimalField(blank=True, decimal_places=1, help_text='Spread or total line (e.g., -3.5, 45.5)', max_digits=5, null=True)),
                ('captured_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Odds Snapshot',
                'verbose_name_plural': 'Odds Snapshots',
                'ordering': ['-captured_at'],
            },
        ),
        migrations.CreateModel(
            name='GameLineHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_id', models.CharField(db_index=True, max_length=100, unique=True)),
                ('sport_key', models.CharField(db_index=True, max_length=50)),
                ('home_team', models.CharField(max_length=100)),
                ('away_team', models.CharField(max_length=100)),
                ('commence_time', models.DateTimeField()),
                ('open_spread_home', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('open_spread_price', models.IntegerField(blank=True, null=True)),
                ('open_total', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('open_ml_home', models.IntegerField(blank=True, null=True)),
                ('open_ml_away', models.IntegerField(blank=True, null=True)),
                ('current_spread_home', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('current_spread_price', models.IntegerField(blank=True, null=True)),
                ('current_total', models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ('current_ml_home', models.IntegerField(blank=True, null=True)),
                ('current_ml_away', models.IntegerField(blank=True, null=True)),
                ('spread_movement', models.DecimalField(decimal_places=1, default=0, help_text='Change in spread from open to current', max_digits=5)),
                ('total_movement', models.DecimalField(decimal_places=1, default=0, help_text='Change in total from open to current', max_digits=5)),
                ('snapshot_count', models.PositiveIntegerField(default=0)),
                ('first_snapshot_at', models.DateTimeField(blank=True, null=True)),
                ('last_snapshot_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Game Line History',
                'verbose_name_plural': 'Game Line Histories',
                'ordering': ['-commence_time'],
            },
        ),
        migrations.AddIndex(
            model_name='oddssnapshot',
            index=models.Index(fields=['game_id', 'bookmaker', 'market', 'outcome_name'], name='core_oddssnap_game_id_7e89e0_idx'),
        ),
        migrations.AddIndex(
            model_name='oddssnapshot',
            index=models.Index(fields=['sport_key', 'captured_at'], name='core_oddssnap_sport_k_f8e18c_idx'),
        ),
        migrations.AddIndex(
            model_name='oddssnapshot',
            index=models.Index(fields=['game_id', 'captured_at'], name='core_oddssnap_game_id_a12b5e_idx'),
        ),
    ]
