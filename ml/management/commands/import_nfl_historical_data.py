"""
Import historical NFL data from Kaggle dataset
Dataset: https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data

To use:
1. Download dataset from Kaggle and extract to /tmp/nfl_data/
2. Run: python manage.py import_nfl_historical_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from sports.models import Game, Team, League
from datetime import datetime
import csv
import os


class Command(BaseCommand):
    help = 'Import historical NFL data from Kaggle dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='/tmp/nfl_data/spreadspoke_scores.csv',
            help='Path to the CSV file'
        )
        parser.add_argument(
            '--start-season',
            type=int,
            default=2018,
            help='Starting season year (default: 2018 for recent data)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of games to import (for testing)'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        start_season = options['start_season']
        limit = options['limit']

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(
                f"File not found: {csv_file}\n"
                f"\n"
                f"To download:\n"
                f"1. Go to: https://www.kaggle.com/datasets/tobycrabtree/nfl-scores-and-betting-data\n"
                f"2. Click 'Download' (requires Kaggle account)\n"
                f"3. Extract spreadspoke_scores.csv to {csv_file}\n"
            ))
            return

        # Get NFL league
        try:
            nfl_league = League.objects.get(sport_type='nfl')
        except League.DoesNotExist:
            self.stdout.write(self.style.ERROR("NFL league not found. Run sync_sports_data first."))
            return

        # Track stats
        imported_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(f"Reading {csv_file}...")

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Common column names from this dataset
            # schedule_date, schedule_season, team_home, team_away,
            # score_home, score_away, spread_favorite, over_under_line

            for i, row in enumerate(reader):
                if limit and imported_count >= limit:
                    break

                try:
                    # Extract season year
                    season = int(row.get('schedule_season', 0))

                    # Skip old seasons
                    if season < start_season:
                        skipped_count += 1
                        continue

                    # Parse date
                    date_str = row.get('schedule_date', '')
                    try:
                        game_date = datetime.strptime(date_str, '%m/%d/%Y')
                        game_date = timezone.make_aware(game_date)
                    except ValueError:
                        try:
                            game_date = datetime.strptime(date_str, '%Y-%m-%d')
                            game_date = timezone.make_aware(game_date)
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f"Invalid date: {date_str}"))
                            error_count += 1
                            continue

                    # Get team names
                    home_team_name = row.get('team_home', '').strip()
                    away_team_name = row.get('team_away', '').strip()

                    if not home_team_name or not away_team_name:
                        error_count += 1
                        continue

                    # Find teams (try matching by name)
                    home_team = self._find_team(home_team_name)
                    away_team = self._find_team(away_team_name)

                    if not home_team or not away_team:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Teams not found: {home_team_name} vs {away_team_name}"
                            )
                        )
                        error_count += 1
                        continue

                    # Get scores
                    home_score = self._parse_score(row.get('score_home'))
                    away_score = self._parse_score(row.get('score_away'))

                    # Skip if no scores (game hasn't been played)
                    if home_score is None or away_score is None:
                        skipped_count += 1
                        continue

                    # Check if game already exists
                    existing = Game.objects.filter(
                        home_team=home_team,
                        away_team=away_team,
                        scheduled_start__date=game_date.date()
                    ).first()

                    if existing:
                        # Update existing game
                        existing.home_score = home_score
                        existing.away_score = away_score
                        existing.status = 'final'
                        existing.save()
                        skipped_count += 1
                    else:
                        # Create new game
                        Game.objects.create(
                            league=nfl_league,
                            home_team=home_team,
                            away_team=away_team,
                            scheduled_start=game_date,
                            home_score=home_score,
                            away_score=away_score,
                            status='final',
                            season=season,
                            week=self._parse_week(row.get('schedule_week', ''))
                        )
                        imported_count += 1

                    if imported_count % 100 == 0:
                        self.stdout.write(f"Imported {imported_count} games...")

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Error processing row {i}: {e}")
                    )
                    error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Import complete!\n"
                f"  Imported: {imported_count} games\n"
                f"  Skipped: {skipped_count} games\n"
                f"  Errors: {error_count} rows\n"
            )
        )

    def _find_team(self, team_name: str) -> Team:
        """Find team by name with fuzzy matching"""
        # Try exact match first
        team = Team.objects.filter(name__iexact=team_name).first()
        if team:
            return team

        # Try partial match
        team = Team.objects.filter(name__icontains=team_name).first()
        if team:
            return team

        # Common name mappings
        name_map = {
            'Washington Football Team': 'Washington Commanders',
            'Washington Redskins': 'Washington Commanders',
            'Oakland Raiders': 'Las Vegas Raiders',
            'San Diego Chargers': 'Los Angeles Chargers',
            'St. Louis Rams': 'Los Angeles Rams',
        }

        mapped_name = name_map.get(team_name)
        if mapped_name:
            return Team.objects.filter(name__icontains=mapped_name).first()

        return None

    def _parse_score(self, score_str: str) -> int:
        """Parse score string to integer"""
        if not score_str:
            return None
        try:
            return int(float(score_str))
        except (ValueError, TypeError):
            return None

    def _parse_week(self, week_str: str) -> int:
        """Parse week string to integer"""
        if not week_str:
            return 1
        try:
            # Handle "Week 1", "1", etc.
            return int(week_str.replace('Week', '').strip())
        except (ValueError, TypeError):
            return 1