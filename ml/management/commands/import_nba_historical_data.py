"""
Import NBA Historical Game Data

Imports NBA games from Kaggle NBA dataset with detailed statistics.

Dataset: https://www.kaggle.com/datasets/nathanlauga/nba-games
Files: games.csv, teams.csv
Games: 26,652 games (1946-2023)

Usage:
    python manage.py import_nba_historical_data --start-season 2018
    python manage.py import_nba_historical_data --start-season 2015 --limit 1000
"""

from django.core.management.base import BaseCommand
from sports.models import Game, Team, League
from datetime import datetime
import csv
import os


class Command(BaseCommand):
    help = 'Import NBA historical game data from Kaggle dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-season',
            type=int,
            default=2018,
            help='Start season year (default: 2018)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of games to import (for testing)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without saving to database'
        )

    def handle(self, *args, **options):
        start_season = options['start_season']
        limit = options['limit']
        dry_run = options['dry_run']

        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS("  NBA Historical Data Import"))
        self.stdout.write(f"{'='*70}\n")

        self.stdout.write(f"📅 Start season: {start_season}")
        self.stdout.write(f"🔢 Limit: {limit if limit else 'No limit'}")
        self.stdout.write(f"🏃 Mode: {'DRY RUN' if dry_run else 'LIVE IMPORT'}\n")

        # File paths
        base_dir = '/Users/donkeyking/Donkey_Betz/unified-donkey-betz/nba-game-data'
        teams_file = os.path.join(base_dir, 'teams.csv')
        games_file = os.path.join(base_dir, 'games.csv')

        if not os.path.exists(teams_file):
            self.stdout.write(self.style.ERROR(f"❌ Teams file not found: {teams_file}"))
            return

        if not os.path.exists(games_file):
            self.stdout.write(self.style.ERROR(f"❌ Games file not found: {games_file}"))
            return

        # Step 1: Load and create NBA teams
        self.stdout.write("📋 Step 1: Loading NBA teams...")
        team_mapping = self._load_teams(teams_file, dry_run)
        self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(team_mapping)} NBA teams\n"))

        # Step 2: Import games
        self.stdout.write("📋 Step 2: Importing NBA games...")
        stats = self._import_games(games_file, team_mapping, start_season, limit, dry_run)

        # Summary
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS("  Import Summary"))
        self.stdout.write(f"{'='*70}")
        self.stdout.write(f"✅ Games imported: {stats['imported']}")
        self.stdout.write(f"🔄 Games updated:  {stats['updated']}")
        self.stdout.write(f"⏭️  Games skipped:  {stats['skipped']}")
        self.stdout.write(f"❌ Errors:         {stats['errors']}")
        self.stdout.write(f"{'='*70}\n")

        if dry_run:
            self.stdout.write(self.style.WARNING("⚠️  DRY RUN - No changes saved to database"))

    def _load_teams(self, teams_file: str, dry_run: bool) -> dict:
        """Load NBA teams and create missing ones"""
        team_mapping = {}  # Maps TEAM_ID -> Team object

        # Get or create NBA league
        if not dry_run:
            league, created = League.objects.get_or_create(
                sport_type='nba',
                name='NBA',
                defaults={'country': 'USA'}
            )
            if created:
                self.stdout.write("   Created NBA league")

        with open(teams_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                team_id = int(row['TEAM_ID'])
                abbreviation = row['ABBREVIATION']
                nickname = row['NICKNAME']
                city = row['CITY']
                full_name = f"{city} {nickname}" if city else nickname

                if not dry_run:
                    # Try to find existing team by abbreviation
                    try:
                        team = Team.objects.get(
                            abbreviation=abbreviation,
                            league__sport_type='nba'
                        )
                    except Team.DoesNotExist:
                        # Create new team
                        team = Team.objects.create(
                            name=full_name,
                            abbreviation=abbreviation,
                            city=city,
                            league=league
                        )
                        self.stdout.write(f"   ✨ Created team: {abbreviation} - {full_name}")

                    team_mapping[team_id] = team
                else:
                    # Dry run - just show what would be created
                    self.stdout.write(f"   Would map: {team_id} -> {abbreviation} ({full_name})")

        return team_mapping

    def _import_games(self, games_file: str, team_mapping: dict,
                      start_season: int, limit: int, dry_run: bool) -> dict:
        """Import NBA games from CSV"""

        stats = {
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        with open(games_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader):
                # Check limit
                if limit and stats['imported'] + stats['updated'] >= limit:
                    self.stdout.write(f"\n⚠️  Reached import limit of {limit} games")
                    break

                try:
                    # Parse season
                    season = int(row['SEASON'])
                    if season < start_season:
                        stats['skipped'] += 1
                        continue

                    # Parse game date
                    game_date_str = row['GAME_DATE_EST']
                    if not game_date_str:
                        stats['skipped'] += 1
                        continue

                    game_date = datetime.strptime(game_date_str, '%Y-%m-%d')

                    # Get teams
                    home_team_id = int(row['HOME_TEAM_ID'])
                    away_team_id = int(row['VISITOR_TEAM_ID'])

                    if home_team_id not in team_mapping or away_team_id not in team_mapping:
                        stats['errors'] += 1
                        continue

                    home_team = team_mapping[home_team_id]
                    away_team = team_mapping[away_team_id]

                    # Parse scores (handle both int and float formats)
                    home_score = int(float(row['PTS_home'])) if row['PTS_home'] else None
                    away_score = int(float(row['PTS_away'])) if row['PTS_away'] else None

                    # Parse game status
                    game_status = row.get('GAME_STATUS_TEXT', 'Final')
                    status = 'final' if 'Final' in game_status else 'scheduled'

                    # Create unique identifier
                    game_identifier = f"NBA-{season}-{row['GAME_ID']}"

                    if not dry_run:
                        # Check if game exists
                        existing_game = Game.objects.filter(
                            home_team=home_team,
                            away_team=away_team,
                            scheduled_start__date=game_date.date()
                        ).first()

                        if existing_game:
                            # Update existing game
                            existing_game.home_score = home_score
                            existing_game.away_score = away_score
                            existing_game.status = status
                            existing_game.save()
                            stats['updated'] += 1
                        else:
                            # Create new game
                            Game.objects.create(
                                home_team=home_team,
                                away_team=away_team,
                                league=home_team.league,
                                scheduled_start=game_date,
                                home_score=home_score,
                                away_score=away_score,
                                status=status
                            )
                            stats['imported'] += 1
                    else:
                        stats['imported'] += 1

                    # Progress indicator
                    if (stats['imported'] + stats['updated']) % 100 == 0:
                        self.stdout.write(
                            f"   Processed {stats['imported'] + stats['updated']} games..."
                        )

                except Exception as e:
                    stats['errors'] += 1
                    if stats['errors'] <= 5:
                        self.stdout.write(
                            self.style.WARNING(f"   ⚠️  Error on row {i}: {e}")
                        )

        if stats['errors'] > 5:
            self.stdout.write(
                self.style.WARNING(f"   ⚠️  ... and {stats['errors'] - 5} more errors")
            )

        return stats