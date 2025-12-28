"""
Management command to enrich sports data with additional information
from multiple API sources (ESPN, The Odds API, TheSportsDB, WeatherAPI)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from sports.models import Game
from sports.data_enrichment import data_enricher
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Enrich sports data with team records, logos, odds, and weather information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sport',
            type=str,
            default='all',
            help='Sport type to enrich (nfl, ncaaf, nba, ncaab, mlb, nhl, or all)'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date to enrich games for (YYYY-MM-DD format)'
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Number of days ahead to enrich games (default: 7)'
        )
        parser.add_argument(
            '--enrich-teams',
            action='store_true',
            help='Enrich team data (logos, records)'
        )
        parser.add_argument(
            '--enrich-odds',
            action='store_true',
            help='Enrich games with betting odds'
        )
        parser.add_argument(
            '--enrich-weather',
            action='store_true',
            help='Enrich outdoor games with weather data'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Enrich everything (teams, odds, weather)'
        )

    def handle(self, *args, **options):
        sport = options['sport']
        date = options['date']
        days_ahead = options['days_ahead']
        enrich_teams = options['enrich_teams']
        enrich_odds = options['enrich_odds']
        enrich_weather = options['enrich_weather']

        # If --all flag is set, enable all enrichment options
        if options['all']:
            enrich_teams = True
            enrich_odds = True
            enrich_weather = True

        # If no specific enrichment is requested, default to all
        if not any([enrich_teams, enrich_odds, enrich_weather]):
            enrich_teams = True
            enrich_odds = True
            enrich_weather = True

        # Determine which sports to process
        if sport == 'all':
            sports_to_enrich = ['nfl', 'ncaaf', 'nba', 'ncaab', 'mlb', 'nhl']
        else:
            sports_to_enrich = [sport.lower()]

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS("Starting Sports Data Enrichment"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))

        total_teams_enriched = 0
        total_games_enriched = 0
        total_odds_added = 0
        total_weather_added = 0

        for sport_type in sports_to_enrich:
            self.stdout.write(f"\n{'-'*40}")
            self.stdout.write(self.style.WARNING(f"Processing {sport_type.upper()}"))
            self.stdout.write(f"{'-'*40}\n")

            # Enrich team data
            if enrich_teams:
                self.stdout.write("Enriching team data (logos, records)...")
                team_result = data_enricher.enrich_all_teams(sport_type.upper())

                total_teams_enriched += team_result['teams_updated']

                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Teams updated: {team_result['teams_updated']}"
                ))
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Logos added: {team_result['logos_added']}"
                ))
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Records updated: {team_result['records_updated']}"
                ))

                if team_result['errors']:
                    for error in team_result['errors'][:5]:  # Show first 5 errors
                        self.stdout.write(self.style.ERROR(f"  ✗ {error}"))

            # Get games to enrich
            games_query = Game.objects.filter(
                league__sport_type=sport_type,
                is_active=True
            )

            if date:
                # Specific date
                target_date = datetime.strptime(date, '%Y-%m-%d').date()
                games_query = games_query.filter(scheduled_start__date=target_date)
            else:
                # Next X days
                end_date = timezone.now() + timedelta(days=days_ahead)
                games_query = games_query.filter(
                    scheduled_start__gte=timezone.now(),
                    scheduled_start__lte=end_date
                )

            games = games_query.all()

            if not games:
                self.stdout.write(f"  No games found for {sport_type.upper()}")
                continue

            self.stdout.write(f"\nProcessing {len(games)} games...")

            # Enrich each game
            for game in games:
                game_enriched = False

                # Enrich with odds
                if enrich_odds:
                    odds_result = data_enricher.enrich_game_odds(str(game.id))
                    if odds_result['odds_added'] > 0:
                        total_odds_added += odds_result['odds_added']
                        game_enriched = True
                        self.stdout.write(
                            f"  • {game.away_team.abbreviation} @ {game.home_team.abbreviation}: "
                            f"{odds_result['odds_added']} odds added"
                        )
                    elif odds_result['errors']:
                        self.stdout.write(self.style.WARNING(
                            f"  • {game.away_team.abbreviation} @ {game.home_team.abbreviation}: "
                            f"No odds found"
                        ))

                # Enrich with weather (outdoor sports only)
                if enrich_weather and sport_type in ['nfl', 'ncaaf', 'mlb']:
                    weather_result = data_enricher.enrich_game_weather(str(game.id))
                    if weather_result['weather_updated']:
                        total_weather_added += 1
                        game_enriched = True
                        self.stdout.write(
                            f"    → Weather data added for {game.venue_name}"
                        )

                if game_enriched:
                    total_games_enriched += 1

        # Print summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS("Enrichment Complete!"))
        self.stdout.write(f"{'='*60}\n")

        self.stdout.write(self.style.SUCCESS(f"Total teams enriched: {total_teams_enriched}"))
        self.stdout.write(self.style.SUCCESS(f"Total games enriched: {total_games_enriched}"))
        self.stdout.write(self.style.SUCCESS(f"Total odds added: {total_odds_added}"))
        self.stdout.write(self.style.SUCCESS(f"Total weather data added: {total_weather_added}"))

        # Check API keys
        self.stdout.write(f"\n{'-'*40}")
        self.stdout.write("API Key Status:")
        self.stdout.write(f"{'-'*40}")

        from django.conf import settings

        if getattr(settings, 'THE_ODDS_API_KEY', ''):
            self.stdout.write(self.style.SUCCESS("  ✓ The Odds API key configured"))
        else:
            self.stdout.write(self.style.WARNING(
                "  ⚠ The Odds API key not configured (set THE_ODDS_API_KEY in settings)"
            ))

        if getattr(settings, 'WEATHER_API_KEY', ''):
            self.stdout.write(self.style.SUCCESS("  ✓ Weather API key configured"))
        else:
            self.stdout.write(self.style.WARNING(
                "  ⚠ Weather API key not configured (set WEATHER_API_KEY in settings)"
            ))

        self.stdout.write("\n")