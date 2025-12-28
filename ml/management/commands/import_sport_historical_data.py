"""
Universal Sport Historical Data Import Command

Import historical game data for any sport from CSV files.

Usage:
    python manage.py import_sport_historical_data --sport nfl --file data/nfl_scores.csv
    python manage.py import_sport_historical_data --sport nba --file data/nba_games.csv --start-season 2018
"""

from django.core.management.base import BaseCommand
from sports.models import Team, League
from ml.core.sport_configs import SPORT_CONFIGS
import csv
from datetime import datetime


class Command(BaseCommand):
    help = 'Import historical data for any sport'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sport',
            type=str,
            required=True,
            choices=['nfl', 'nba', 'mlb', 'nhl'],
            help='Sport type (nfl, nba, mlb, nhl)'
        )
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to CSV file with historical data'
        )
        parser.add_argument(
            '--start-season',
            type=int,
            default=2018,
            help='Start season year (default: 2018)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview import without saving to database'
        )

    def handle(self, *args, **options):
        sport = options['sport']
        file_path = options['file']
        start_season = options['start_season']
        dry_run = options['dry_run']

        config = SPORT_CONFIGS.get(sport)
        if not config:
            self.stdout.write(self.style.ERROR(f"❌ Unknown sport: {sport}"))
            return

        self.stdout.write(f"\n{'='*70}")
        self.stdout.write(self.style.SUCCESS(f"  {config.name} Historical Data Import"))
        self.stdout.write(f"{'='*70}\n")

        self.stdout.write(f"📁 File: {file_path}")
        self.stdout.write(f"📅 Start season: {start_season}")
        self.stdout.write(f"🏃 Mode: {'DRY RUN' if dry_run else 'LIVE IMPORT'}\n")

        # Delegate to sport-specific importer
        if sport == 'nfl':
            self.import_nfl(file_path, start_season, dry_run)
        elif sport == 'nba':
            self.import_nba(file_path, start_season, dry_run)
        elif sport == 'mlb':
            self.import_mlb(file_path, start_season, dry_run)
        elif sport == 'nhl':
            self.import_nhl(file_path, start_season, dry_run)

    def import_nfl(self, file_path: str, start_season: int, dry_run: bool):
        """Import NFL data from spreadspoke_scores.csv"""
        # Use existing import_nfl_historical_data logic
        self.stdout.write("ℹ️  For NFL imports, use:")
        self.stdout.write("   python manage.py import_nfl_historical_data\n")
        self.stdout.write(self.style.WARNING(
            "   (NFL import already has dedicated command with full functionality)"
        ))

    def import_nba(self, file_path: str, start_season: int, dry_run: bool):
        """
        Import NBA data from Kaggle NBA games dataset

        Expected CSV format:
        GAME_DATE_EST, HOME_TEAM_ID, VISITOR_TEAM_ID, SEASON,
        PTS_home, PTS_away, FG_PCT_home, FG_PCT_away, etc.
        """
        self.stdout.write("🏀 Importing NBA games...\n")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                games_imported = 0
                games_updated = 0
                games_skipped = 0

                # Get or create NBA league
                league, _ = League.objects.get_or_create(
                    sport_type='nba',
                    name='NBA',
                    defaults={'country': 'USA'}
                )

                for row in reader:
                    try:
                        # Parse season (e.g., "2018" from SEASON field)
                        season = int(row.get('SEASON', 0))
                        if season < start_season:
                            games_skipped += 1
                            continue

                        # Parse game date
                        game_date_str = row.get('GAME_DATE_EST', '')
                        if not game_date_str:
                            continue

                        game_date = datetime.strptime(game_date_str, '%Y-%m-%d')

                        # Get teams (need team ID to name mapping)
                        home_team_id = int(row.get('HOME_TEAM_ID', 0))
                        away_team_id = int(row.get('VISITOR_TEAM_ID', 0))

                        # TODO: Implement team ID to Team model mapping
                        # For now, skip if we can't find teams
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Team mapping not implemented yet for NBA.\n"
                                f"   Need to map team IDs ({home_team_id}, {away_team_id}) to Team models.\n"
                            )
                        )
                        return

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f"   ⚠️  Error parsing row: {e}")
                        )
                        continue

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ File not found: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Import error: {e}"))

    def import_mlb(self, file_path: str, start_season: int, dry_run: bool):
        """Import MLB data"""
        self.stdout.write("⚾ Importing MLB games...\n")
        self.stdout.write(self.style.WARNING(
            "⚠️  MLB import not yet implemented.\n"
            "   Expected CSV format:\n"
            "   - date, home_team, away_team, home_runs, away_runs, season\n"
        ))

    def import_nhl(self, file_path: str, start_season: int, dry_run: bool):
        """Import NHL data"""
        self.stdout.write("🏒 Importing NHL games...\n")
        self.stdout.write(self.style.WARNING(
            "⚠️  NHL import not yet implemented.\n"
            "   Expected CSV format:\n"
            "   - date, home_team, away_team, home_goals, away_goals, season\n"
        ))

    def _get_or_create_team(self, team_name: str, sport_type: str) -> Team:
        """Get or create team by name"""
        # Try exact match first
        try:
            return Team.objects.get(name=team_name, league__sport_type=sport_type)
        except Team.DoesNotExist:
            pass

        # Try abbreviation match
        try:
            return Team.objects.get(abbreviation=team_name, league__sport_type=sport_type)
        except Team.DoesNotExist:
            pass

        # Create new team (should ideally not happen - teams should be pre-loaded)
        self.stdout.write(
            self.style.WARNING(f"⚠️  Creating new team: {team_name}")
        )

        league, _ = League.objects.get_or_create(
            sport_type=sport_type,
            name=sport_type.upper(),
            defaults={'country': 'USA'}
        )

        team = Team.objects.create(
            name=team_name,
            abbreviation=team_name[:3].upper(),
            league=league
        )

        return team