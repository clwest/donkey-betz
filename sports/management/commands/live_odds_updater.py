"""
Real-time odds updater for live NFL and NCAAF games
Intelligently updates odds based on game status and cache expiration
"""

import time
import signal
import sys
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from sports.models import Game, BettingMarket
from sports.data_enrichment import data_enricher
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Real-time odds updater for live NFL and NCAAF games'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
        self.stats = {
            'updates': 0,
            'api_calls': 0,
            'from_cache': 0,
            'errors': 0,
            'start_time': None
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Check interval in minutes (default: 5)'
        )
        parser.add_argument(
            '--live-cache',
            type=int,
            default=30,
            help='Cache duration for live games in minutes (default: 30)'
        )
        parser.add_argument(
            '--upcoming-cache',
            type=int,
            default=120,
            help='Cache duration for upcoming games in minutes (default: 120)'
        )
        parser.add_argument(
            '--pre-game-window',
            type=int,
            default=60,
            help='Minutes before game start to begin frequent updates (default: 60)'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Run once and exit (for testing)'
        )

    def signal_handler(self, sig, frame):
        """Handle graceful shutdown"""
        self.stdout.write(self.style.WARNING('\n\nShutting down gracefully...'))
        self.running = False
        self.print_stats()
        sys.exit(0)

    def handle(self, *args, **options):
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        interval = options['interval']
        live_cache = options['live_cache']
        upcoming_cache = options['upcoming_cache']
        pre_game_window = options['pre_game_window']
        test_mode = options['test_mode']

        self.stats['start_time'] = timezone.now()

        self.stdout.write(self.style.SUCCESS(f"""
╔═══════════════════════════════════════════════════════════╗
║         LIVE ODDS UPDATER - NFL & NCAAF                  ║
╚═══════════════════════════════════════════════════════════╝

Configuration:
  • Check Interval: {interval} minutes
  • Live Game Cache: {live_cache} minutes
  • Upcoming Game Cache: {upcoming_cache} minutes
  • Pre-Game Window: {pre_game_window} minutes
  • Test Mode: {'ON' if test_mode else 'OFF'}

Press Ctrl+C to stop gracefully
        """))

        while self.running:
            try:
                self.update_cycle(live_cache, upcoming_cache, pre_game_window)

                if test_mode:
                    self.stdout.write(self.style.SUCCESS("Test mode - exiting after one cycle"))
                    break

                # Sleep for interval
                self.stdout.write(f"\n💤 Sleeping for {interval} minutes...")
                for i in range(interval * 60):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error in update cycle: {e}")
                self.stats['errors'] += 1
                self.stdout.write(self.style.ERROR(f"Error: {e}"))

                if test_mode:
                    raise

                # Sleep before retry
                time.sleep(60)

        self.print_stats()

    def update_cycle(self, live_cache_minutes, upcoming_cache_minutes, pre_game_minutes):
        """Run one update cycle"""
        now = timezone.now()

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.WARNING(f"Update Cycle - {now.strftime('%Y-%m-%d %H:%M:%S')}"))
        self.stdout.write(f"{'='*60}\n")

        # Get games that need updating
        games_to_update = self.get_games_needing_update(
            live_cache_minutes,
            upcoming_cache_minutes,
            pre_game_minutes
        )

        if not games_to_update:
            self.stdout.write("No games need updating at this time")
            return

        # Group games by league for batch updates
        nfl_games = []
        ncaaf_games = []

        for game in games_to_update:
            if game.league.abbreviation == 'NFL':
                nfl_games.append(game)
            elif game.league.abbreviation == 'NCAAF':
                ncaaf_games.append(game)

        # Update NFL games (batch)
        if nfl_games:
            self.update_league_batch('NFL', nfl_games)

        # Update NCAAF games (batch)
        if ncaaf_games:
            self.update_league_batch('NCAAF', ncaaf_games)

    def get_games_needing_update(self, live_cache_min, upcoming_cache_min, pre_game_min):
        """Get games that need odds updates based on status and cache"""
        now = timezone.now()
        games_needing_update = []

        # Get all NFL and NCAAF games
        games = Game.objects.filter(
            Q(league__abbreviation='NFL') | Q(league__abbreviation='NCAAF'),
            is_active=True
        ).select_related('home_team', 'away_team', 'league')

        for game in games:
            needs_update = False
            reason = ""

            # Determine cache duration based on game status
            if game.status in ['live', 'status_in_progress', 'status_end_period']:
                cache_duration = timedelta(minutes=live_cache_min)
                game_type = "LIVE"
            elif game.status in ['scheduled', 'status_scheduled']:
                time_to_game = game.scheduled_start - now

                # If game starts within pre-game window, use live cache timing
                if time_to_game.total_seconds() <= pre_game_min * 60:
                    cache_duration = timedelta(minutes=live_cache_min)
                    game_type = "PRE-GAME"
                else:
                    cache_duration = timedelta(minutes=upcoming_cache_min)
                    game_type = "UPCOMING"
            else:
                # Completed games don't need updates
                continue

            # Check if odds are stale
            markets = game.markets.filter(is_active=True)

            if not markets.exists():
                needs_update = True
                reason = "No odds data"
            else:
                latest_update = markets.latest('updated_at').updated_at
                time_since_update = now - latest_update

                if time_since_update >= cache_duration:
                    needs_update = True
                    minutes_old = int(time_since_update.total_seconds() / 60)
                    reason = f"Cache expired ({minutes_old} min old)"

            if needs_update:
                games_needing_update.append(game)
                self.stdout.write(
                    f"  • [{game_type}] {game.away_team.abbreviation} @ "
                    f"{game.home_team.abbreviation} - {reason}"
                )

        return games_needing_update

    def update_league_batch(self, league, games):
        """Update odds for a league using batch API call"""
        self.stdout.write(f"\n🏈 Updating {league} odds (batch mode)...")

        try:
            # Use batch enrichment for efficiency
            result = data_enricher.enrich_league_odds_batch(league)

            self.stats['updates'] += result['games_enriched']
            self.stats['api_calls'] += result['api_calls']
            self.stats['from_cache'] += result['from_cache']

            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Updated {result['games_enriched']} games "
                f"({result['from_cache']} from cache) with {result['api_calls']} API call"
            ))

            if result['errors']:
                for error in result['errors'][:3]:
                    self.stdout.write(self.style.ERROR(f"  ✗ {error}"))

        except Exception as e:
            logger.error(f"Error updating {league}: {e}")
            self.stats['errors'] += 1
            self.stdout.write(self.style.ERROR(f"  ✗ Failed to update {league}: {e}"))

    def print_stats(self):
        """Print session statistics"""
        if not self.stats['start_time']:
            return

        runtime = timezone.now() - self.stats['start_time']
        hours = runtime.total_seconds() / 3600

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS("Session Statistics"))
        self.stdout.write(f"{'='*60}")
        self.stdout.write(f"Runtime: {runtime}")
        self.stdout.write(f"Games Updated: {self.stats['updates']}")
        self.stdout.write(f"API Calls Made: {self.stats['api_calls']}")
        self.stdout.write(f"Cache Hits: {self.stats['from_cache']}")
        self.stdout.write(f"Errors: {self.stats['errors']}")

        if hours > 0:
            self.stdout.write(f"API Calls/Hour: {self.stats['api_calls']/hours:.1f}")

        # Estimate monthly usage
        if self.stats['api_calls'] > 0 and hours > 0:
            daily_estimate = (self.stats['api_calls'] / hours) * 24
            monthly_estimate = daily_estimate * 30
            self.stdout.write(f"\nProjected Monthly API Usage: {monthly_estimate:.0f} calls")
            self.stdout.write(f"Budget Utilization: {monthly_estimate/500*100:.1f}%")