# Generated manually for Session 736 - recreate OddsSnapshot and GameLineHistory
# These tables were deleted in migration 0129 but the model files still exist

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0160_alter_agentmemory_embedding_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="OddsSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("game_id", models.CharField(db_index=True, help_text="The Odds API game ID", max_length=100)),
                ("sport_key", models.CharField(db_index=True, max_length=50)),
                ("home_team", models.CharField(max_length=100)),
                ("away_team", models.CharField(max_length=100)),
                ("commence_time", models.DateTimeField(help_text="Game start time")),
                ("bookmaker", models.CharField(db_index=True, max_length=50)),
                ("bookmaker_title", models.CharField(blank=True, max_length=100)),
                ("market", models.CharField(choices=[("h2h", "Moneyline"), ("spreads", "Spread"), ("totals", "Totals")], db_index=True, max_length=20)),
                ("outcome_name", models.CharField(help_text="Team name, Over, or Under", max_length=100)),
                ("price", models.IntegerField(help_text="American odds (e.g., -110, +150)")),
                ("point", models.DecimalField(blank=True, decimal_places=1, help_text="Spread or total line (e.g., -3.5, 45.5)", max_digits=5, null=True)),
                ("captured_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                "verbose_name": "Odds Snapshot",
                "verbose_name_plural": "Odds Snapshots",
                "ordering": ["-captured_at"],
            },
        ),
        migrations.CreateModel(
            name="GameLineHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("game_id", models.CharField(db_index=True, help_text="The Odds API game ID", max_length=100, unique=True)),
                ("sport_key", models.CharField(db_index=True, max_length=50)),
                ("home_team", models.CharField(max_length=100)),
                ("away_team", models.CharField(max_length=100)),
                ("commence_time", models.DateTimeField(db_index=True, help_text="Game start time")),
                ("opening_home_ml", models.IntegerField(blank=True, help_text="Opening home moneyline", null=True)),
                ("opening_away_ml", models.IntegerField(blank=True, help_text="Opening away moneyline", null=True)),
                ("opening_spread", models.DecimalField(blank=True, decimal_places=1, help_text="Opening spread line", max_digits=5, null=True)),
                ("opening_total", models.DecimalField(blank=True, decimal_places=1, help_text="Opening total line", max_digits=5, null=True)),
                ("current_home_ml", models.IntegerField(blank=True, help_text="Current home moneyline", null=True)),
                ("current_away_ml", models.IntegerField(blank=True, help_text="Current away moneyline", null=True)),
                ("current_spread", models.DecimalField(blank=True, decimal_places=1, help_text="Current spread line", max_digits=5, null=True)),
                ("current_total", models.DecimalField(blank=True, decimal_places=1, help_text="Current total line", max_digits=5, null=True)),
                ("ml_movement_direction", models.CharField(blank=True, choices=[("home", "Toward Home"), ("away", "Toward Away"), ("stable", "Stable")], max_length=10)),
                ("spread_movement", models.DecimalField(blank=True, decimal_places=1, help_text="Points moved from opening", max_digits=5, null=True)),
                ("total_movement", models.DecimalField(blank=True, decimal_places=1, help_text="Points moved from opening", max_digits=5, null=True)),
                ("snapshot_count", models.IntegerField(default=0, help_text="Number of snapshots captured")),
                ("first_captured_at", models.DateTimeField(blank=True, null=True)),
                ("last_captured_at", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Game Line History",
                "verbose_name_plural": "Game Line Histories",
                "ordering": ["-commence_time"],
            },
        ),
        migrations.AddIndex(
            model_name="oddssnapshot",
            index=models.Index(fields=["game_id", "bookmaker", "market", "outcome_name"], name="core_oddssn_game_id_5a7b8c_idx"),
        ),
        migrations.AddIndex(
            model_name="oddssnapshot",
            index=models.Index(fields=["sport_key", "captured_at"], name="core_oddssn_sport_k_6d7e8f_idx"),
        ),
        migrations.AddIndex(
            model_name="oddssnapshot",
            index=models.Index(fields=["game_id", "captured_at"], name="core_oddssn_game_id_9a0b1c_idx"),
        ),
        migrations.AddIndex(
            model_name="gamelinehistory",
            index=models.Index(fields=["sport_key", "commence_time"], name="core_gameli_sport_k_2c3d4e_idx"),
        ),
    ]
