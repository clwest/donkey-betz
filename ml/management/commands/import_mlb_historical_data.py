"""
Import MLB Historical Game Data

Imports MLB games from Kaggle MLB pitch dataset.

Dataset: https://www.kaggle.com/datasets/pschale/mlb-pitch-data-20152018
Files: games.csv
Games: 9,719 games (2015-2019)

Usage:
    python manage.py import_mlb_historical_data --start-season 2018
    python manage.py import_mlb_historical_data --start-season 2015 --limit 500
"""

from django.core.management.base import BaseCommand
from sports.models import Game, Team, League
from datetime import datetime
import csv
import os


class Command(BaseCommand):
    help = 'Import MLB historical game data from Kaggle dataset'

    # MLB team abbreviation mapping
    MLB_TEAM_MAPPING = {
        'ana': 'LAA',  # Los Angeles Angels
        'ari': 'ARI',  # Arizona Diamondbacks
        'atl': 'ATL',  # Atlanta Braves
        'bal': 'BAL',  # Baltimore Orioles
        'bos': 'BOS',  # Boston Red Sox
        'chn': 'CHC',  # Chicago Cubs
        'cha': 'CWS',  # Chicago White Sox
        'cin': 'CIN',  # Cincinnati Reds
        'cle': 'CLE',  # Cleveland Guardians (was Indians)
        'col': 'COL',  # Colorado Rockies
        'det': 'DET',  # Detroit Tigers
        'hou': 'HOU',  # Houston Astros
        'kca': 'KC',   # Kansas City Royals
        'lan': 'LAD',  # Los Angeles Dodgers
        'mia': 'MIA',  # Miami Marlins
        'mil': 'MIL',  # Milwaukee Brewers
        'min': 'MIN',  # Minnesota Twins
        'nya': 'NYY',  # New York Yankees
        'nyn': 'NYM',  # New York Mets
        'oak': 'OAK',  # Oakland Athletics
        'phi': 'PHI',  # Philadelphia Phillies
        'pit': 'PIT',  # Pittsburgh Pirates
        'sdn': 'SD',   # San Diego Padres
        'sea': 'SEA',  # Seattle Mariners
        'sfn': 'SF',   # San Francisco Giants
        'sln': 'STL',  # St. Louis Cardinals
        'tba': 'TB',   # Tampa Bay Rays
        'tex': 'TEX',  # Texas Rangers
        'tor': 'TOR',  # Toronto Blue Jays
        'was': 'WSH',  # Washington Nationals
    }

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
        self.stdout.write(self.style.SUCCESS("  MLB Historical Data Import"))
        self.stdout.write(f"{'='*70}\n")

        self.stdout.write(f"📅 Start season: {start_season}")
        self.stdout.write(f"🔢 Limit: {limit if limit else 'No limit'}")
        self.stdout.write(f"🏃 Mode: {'DRY RUN' if dry_run else 'LIVE IMPORT'}\n")

        # File path
        games_file = '/Users/donkeyking/Donkey_Betz/unified-donkey-betz/mlb-pitch-data/games.csv'

        if not os.path.exists(games_file):
            self.stdout.write(self.style.ERROR(f"❌ Games file not found: {games_file}"))
            return

        # Step 1: Ensure MLB teams exist
        self.stdout.write("📋 Step 1: Ensuring MLB teams exist...")
        team_mapping = self._ensure_mlb_teams(dry_run)
        self.stdout.write(self.style.SUCCESS(f"✅ Prepared {len(team_mapping)} MLB teams\n"))

        # Step 2: Import games
        self.stdout.write("📋 Step 2: Importing MLB games...")
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

    def _ensure_mlb_teams(self, dry_run: bool) -> dict:
        """Ensure MLB teams exist and return mapping"""
        team_mapping = {}

        if not dry_run:
            # Get or create MLB league
            league, created = League.objects.get_or_create(
                sport_type='mlb',
                defaults={'name': 'MLB', 'country': 'USA', 'abbreviation': 'MLB'}
            )

            # Create teams if they don't exist
            for short_code, abbreviation in self.MLB_TEAM_MAPPING.items():
                try:
                    team = Team.objects.get(
                        abbreviation=abbreviation,
                        league__sport_type='mlb'
                    )
                except Team.DoesNotExist:
                    team = Team.objects.create(
                        name=abbreviation,  # Will be updated with full name later
                        abbreviation=abbreviation,
                        league=league
                    )
                    self.stdout.write(f"   ✨ Created team: {abbreviation}")

                team_mapping[short_code] = team
        else:
            self.stdout.write(f"   Would ensure {len(self.MLB_TEAM_MAPPING)} teams exist")

        return team_mapping

    def _import_games(self, games_file: str, team_mapping: dict,
                      start_season: int, limit: int, dry_run: bool) -> dict:
        """Import MLB games from CSV"""

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
                    # Parse date
                    date_str = row['date']
                    if not date_str:
                        stats['skipped'] += 1
                        continue

                    game_date = datetime.strptime(date_str, '%Y-%m-%d')
                    season = game_date.year

                    if season < start_season:
                        stats['skipped'] += 1
                        continue

                    # Get teams
                    home_team_code = row['home_team']
                    away_team_code = row['away_team']

                    if home_team_code not in team_mapping or away_team_code not in team_mapping:
                        stats['errors'] += 1
                        if stats['errors'] <= 5:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"   ⚠️  Unknown team codes: {home_team_code}, {away_team_code}"
                                )
                            )
                        continue

                    home_team = team_mapping[home_team_code]
                    away_team = team_mapping[away_team_code]

                    # Parse scores
                    home_score = int(row['home_final_score']) if row['home_final_score'] else None
                    away_score = int(row['away_final_score']) if row['away_final_score'] else None

                    # Status
                    status = 'final' if home_score is not None and away_score is not None else 'scheduled'

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