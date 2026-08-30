"""
Import NHL Historical Game Data

Imports NHL games from Kaggle NHL game dataset.

Dataset: https://www.kaggle.com/datasets/martinellis/nhl-game-data
Files: game.csv, team_info.csv
Games: 26,306 games (2000-2021)

Usage:
    python manage.py import_nhl_historical_data --start-season 2018
    python manage.py import_nhl_historical_data --start-season 2015 --limit 500
"""

from django.core.management.base import BaseCommand
from sports.models import Game, Team, League
from datetime import datetime
import csv
import os


class Command(BaseCommand):
    help = 'Import NHL historical game data from Kaggle dataset'

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
        self.stdout.write(self.style.SUCCESS("  NHL Historical Data Import"))
        self.stdout.write(f"{'='*70}\n")

        self.stdout.write(f"📅 Start season: {start_season}")
        self.stdout.write(f"🔢 Limit: {limit if limit else 'No limit'}")
        self.stdout.write(f"🏃 Mode: {'DRY RUN' if dry_run else 'LIVE IMPORT'}\n")

        # File paths
        base_dir = '/Users/donkeyking/Donkey_Betz/unified-donkey-betz/nhl-game-0data'
        teams_file = os.path.join(base_dir, 'team_info.csv')
        games_file = os.path.join(base_dir, 'game.csv')

        if not os.path.exists(teams_file):
            self.stdout.write(self.style.ERROR(f"❌ Teams file not found: {teams_file}"))
            return

        if not os.path.exists(games_file):
            self.stdout.write(self.style.ERROR(f"❌ Games file not found: {games_file}"))
            return

        # Step 1: Load and create NHL teams
        self.stdout.write("📋 Step 1: Loading NHL teams...")
        team_mapping = self._load_teams(teams_file, dry_run)
        self.stdout.write(self.style.SUCCESS(f"✅ Loaded {len(team_mapping)} NHL teams\n"))

        # Step 2: Import games
        self.stdout.write("📋 Step 2: Importing NHL games...")
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
        """Load NHL teams and create missing ones"""
        team_mapping = {}  # Maps team_id -> Team object

        # Get or create NHL league
        if not dry_run:
            league, created = League.objects.get_or_create(
                sport_type='nhl',
                name='NHL',
                defaults={'country': 'USA'}
            )
            if created:
                self.stdout.write("   Created NHL league")

        with open(teams_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                team_id = int(row['team_id'])
                abbreviation = row['abbreviation']
                short_name = row['shortName']
                team_name = row['teamName']
                full_name = f"{short_name} {team_name}"

                if not dry_run:
                    # Try to find existing team by abbreviation
                    try:
                        team = Team.objects.get(
                            abbreviation=abbreviation,
                            league__sport_type='nhl'
                        )
                    except Team.DoesNotExist:
                        # Create new team
                        team = Team.objects.create(
                            name=full_name,
                            abbreviation=abbreviation,
                            city=short_name,
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
        """Import NHL games from CSV"""

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
                    # Parse season (format: "20162017")
                    season_str = row['season']
                    season = int(season_str[:4])  # First 4 digits = start year

                    if season < start_season:
                        stats['skipped'] += 1
                        continue

                    # Parse game date (ISO format with Z)
                    date_str = row['date_time_GMT']
                    if not date_str:
                        stats['skipped'] += 1
                        continue

                    # Remove 'Z' and parse
                    game_date = datetime.strptime(date_str.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')

                    # Get teams
                    home_team_id = int(row['home_team_id'])
                    away_team_id = int(row['away_team_id'])

                    if home_team_id not in team_mapping or away_team_id not in team_mapping:
                        stats['errors'] += 1
                        continue

                    home_team = team_mapping[home_team_id]
                    away_team = team_mapping[away_team_id]

                    # Parse scores
                    home_score = int(row['home_goals']) if row['home_goals'] else None
                    away_score = int(row['away_goals']) if row['away_goals'] else None

                    # Parse game status
                    outcome = row.get('outcome', '')
                    status = 'final' if 'win' in outcome.lower() else 'scheduled'

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