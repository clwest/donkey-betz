# Session 736 - Fix GameLineHistory field names to match model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0161_session_736_recreate_odds_history"),
    ]

    operations = [
        # Drop the incorrectly created GameLineHistory table and recreate with correct fields
        migrations.DeleteModel(
            name="GameLineHistory",
        ),
        migrations.CreateModel(
            name="GameLineHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("game_id", models.CharField(db_index=True, max_length=100, unique=True)),
                ("sport_key", models.CharField(db_index=True, max_length=50)),
                ("home_team", models.CharField(max_length=100)),
                ("away_team", models.CharField(max_length=100)),
                ("commence_time", models.DateTimeField()),
                # Opening lines
                ("open_spread_home", models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ("open_spread_price", models.IntegerField(blank=True, null=True)),
                ("open_total", models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ("open_ml_home", models.IntegerField(blank=True, null=True)),
                ("open_ml_away", models.IntegerField(blank=True, null=True)),
                # Current lines
                ("current_spread_home", models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ("current_spread_price", models.IntegerField(blank=True, null=True)),
                ("current_total", models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True)),
                ("current_ml_home", models.IntegerField(blank=True, null=True)),
                ("current_ml_away", models.IntegerField(blank=True, null=True)),
                # Movement tracking
                ("spread_movement", models.DecimalField(decimal_places=1, default=0, help_text="Change in spread from open to current", max_digits=5)),
                ("total_movement", models.DecimalField(decimal_places=1, default=0, help_text="Change in total from open to current", max_digits=5)),
                # Snapshot counts
                ("snapshot_count", models.PositiveIntegerField(default=0)),
                ("first_snapshot_at", models.DateTimeField(blank=True, null=True)),
                ("last_snapshot_at", models.DateTimeField(blank=True, null=True)),
                # Timestamps
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Game Line History",
                "verbose_name_plural": "Game Line Histories",
                "ordering": ["-commence_time"],
            },
        ),
    ]
