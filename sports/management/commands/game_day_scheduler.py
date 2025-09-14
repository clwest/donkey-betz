"""
Game day scheduler for NFL and NCAAF
Automatically schedules updates based on game times
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from sports.models import Game
from sports.data_enrichment import data_enricher
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Schedule and run game day updates for NFL and NCAAF'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mode',
            type=str,
            choices=['morning', 'pregame', 'live', 'postgame', 'full'],
            default='full',
            help='Update mode: morning, pregame, live, postgame, or full day'
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date to schedule for (YYYY-MM-DD), default is today'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh all odds (ignore cache)'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        force_refresh = options['force']

        # Determine date
        if options['date']:
            target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()

        self.stdout.write(self.style.SUCCESS(f"""
╔═══════════════════════════════════════════════════════════╗
║          GAME DAY SCHEDULER - NFL & NCAAF                ║
╚═══════════════════════════════════════════════════════════╝

Date: {target_date.strftime('%A, %B %d, %Y')}
Mode: {mode.upper()}
Force Refresh: {'YES' if force_refresh else 'NO'}
        """))

        # Get today's games
        games = self.get_games_for_date(target_date)

        if not games:
            self.stdout.write(self.style.WARNING("No games scheduled for this date"))
            return

        self.stdout.write(f"\nFound {len(games)} games:")
        for game in games:
            self.stdout.write(
                f"  • {game.away_team.abbreviation} @ {game.home_team.abbreviation} "
                f"- {game.scheduled_start.strftime('%I:%M %p')} ({game.league.abbreviation})"
            )

        # Execute based on mode
        if mode == 'morning':
            self.morning_update(games, force_refresh)
        elif mode == 'pregame':
            self.pregame_update(games, force_refresh)
        elif mode == 'live':
            self.live_update(games)
        elif mode == 'postgame':
            self.postgame_update(games, force_refresh)
        elif mode == 'full':
            self.full_day_schedule(games, force_refresh)

    def get_games_for_date(self, date):
        """Get all NFL and NCAAF games for a specific date"""
        # Get games scheduled for this date
        start_of_day = timezone.make_aware(
            datetime.combine(date, datetime.min.time())
        )
        end_of_day = start_of_day + timedelta(days=1)

        games = Game.objects.filter(
            Q(league__abbreviation='NFL') | Q(league__abbreviation='NCAAF'),
            scheduled_start__gte=start_of_day,
            scheduled_start__lt=end_of_day,
            is_active=True
        ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start')

        return games

    def morning_update(self, games, force_refresh=False):
        """Morning update - full sync of all games"""
        self.stdout.write(f"\n{'='*40}")
        self.stdout.write(self.style.WARNING("MORNING UPDATE (8:00 AM)"))
        self.stdout.write(f"{'='*40}\n")

        self.stdout.write("Syncing game data from ESPN...")
        nfl_games = [g for g in games if g.league.abbreviation == 'NFL']
        ncaaf_games = [g for g in games if g.league.abbreviation == 'NCAAF']

        if nfl_games:
            call_command('sync_sports_data', sport='nfl')

        if ncaaf_games:
            call_command('sync_sports_data', sport='ncaaf')

        self.stdout.write("\nEnriching with odds data...")

        # Batch update odds for each league
        leagues_updated = set()
        for game in games:
            if game.league.abbreviation not in leagues_updated:
                result = data_enricher.enrich_league_odds_batch(game.league.abbreviation)
                leagues_updated.add(game.league.abbreviation)

                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ {game.league.abbreviation}: {result['games_enriched']} games updated"
                ))

    def pregame_update(self, games, force_refresh=False):
        """Pre-game update - 1 hour before each game"""
        self.stdout.write(f"\n{'='*40}")
        self.stdout.write(self.style.WARNING("PRE-GAME UPDATES"))
        self.stdout.write(f"{'='*40}\n")

        now = timezone.now()

        for game in games:
            time_to_game = game.scheduled_start - now

            # Update if game starts within 90 minutes
            if timedelta(0) <= time_to_game <= timedelta(minutes=90):
                self.stdout.write(
                    f"\n🏈 {game.away_team.abbreviation} @ {game.home_team.abbreviation}"
                )
                self.stdout.write(f"   Starts in {int(time_to_game.total_seconds()/60)} minutes")

                # Update odds
                result = data_enricher.enrich_game_odds(
                    str(game.id),
                    force_refresh=force_refresh
                )

                if result['odds_added'] > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f"   ✓ Odds updated: {result['odds_added']} lines"
                    ))
                elif result['from_cache']:
                    self.stdout.write("   • Using cached odds (still fresh)")

                # Update weather for outdoor games
                if game.league.abbreviation in ['NFL', 'NCAAF']:
                    weather_result = data_enricher.enrich_game_weather(str(game.id))
                    if weather_result['weather_updated']:
                        self.stdout.write(self.style.SUCCESS("   ✓ Weather updated"))

    def live_update(self, games):
        """Launch live updater for games in progress"""
        self.stdout.write(f"\n{'='*40}")
        self.stdout.write(self.style.WARNING("LIVE GAME MONITORING"))
        self.stdout.write(f"{'='*40}\n")

        # Check which games are live
        live_games = []
        for game in games:
            if game.status in ['live', 'status_in_progress', 'status_end_period']:
                live_games.append(game)
                self.stdout.write(
                    f"  • LIVE: {game.away_team.abbreviation} @ {game.home_team.abbreviation}"
                )

        if live_games:
            self.stdout.write(f"\nStarting live odds updater for {len(live_games)} games...")
            call_command('live_odds_updater', interval=5)
        else:
            self.stdout.write("No games currently live")

    def postgame_update(self, games, force_refresh=False):
        """Post-game update - final odds and settlement"""
        self.stdout.write(f"\n{'='*40}")
        self.stdout.write(self.style.WARNING("POST-GAME UPDATE"))
        self.stdout.write(f"{'='*40}\n")

        completed_games = []
        for game in games:
            if game.status in ['final', 'status_final', 'completed']:
                completed_games.append(game)

                self.stdout.write(
                    f"\n📊 {game.away_team.abbreviation} {game.away_score} - "
                    f"{game.home_score} {game.home_team.abbreviation} (FINAL)"
                )

                # Get final odds for record
                result = data_enricher.enrich_game_odds(
                    str(game.id),
                    force_refresh=force_refresh
                )

                # Mark markets as settled
                markets = game.markets.filter(is_active=True)
                for market in markets:
                    market.status = 'settled'
                    market.settled_at = timezone.now()
                    market.save()

                self.stdout.write(self.style.SUCCESS(
                    f"   ✓ Markets settled: {markets.count()}"
                ))

    def full_day_schedule(self, games, force_refresh=False):
        """Full day schedule with all update phases"""
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS("FULL DAY SCHEDULE"))
        self.stdout.write(f"{'='*60}\n")

        # Determine game windows
        if games:
            earliest_game = games.first().scheduled_start
            latest_game = games.last().scheduled_start

            self.stdout.write("📅 Schedule Overview:")
            self.stdout.write(f"   First Game: {earliest_game.strftime('%I:%M %p')}")
            self.stdout.write(f"   Last Game: {latest_game.strftime('%I:%M %p')}")

            self.stdout.write("\n⏰ Update Schedule:")
            self.stdout.write("   08:00 AM - Morning sync (all games)")
            self.stdout.write("   11:00 AM - Pre-game update (early games)")
            self.stdout.write("   12:00 PM - Start live monitoring")
            self.stdout.write("   03:00 PM - Pre-game update (afternoon games)")
            self.stdout.write("   07:00 PM - Pre-game update (prime time)")
            self.stdout.write("   11:00 PM - Post-game settlement")

            # Execute current phase based on time
            now = timezone.now()
            current_hour = now.hour

            if 6 <= current_hour < 11:
                self.morning_update(games, force_refresh)
            elif 11 <= current_hour < 16:
                self.pregame_update(games, force_refresh)
                self.live_update(games)
            elif 16 <= current_hour < 23:
                self.live_update(games)
            else:
                self.postgame_update(games, force_refresh)

            self.stdout.write(f"\n💡 Tip: Set up cron jobs for automatic scheduling:")
            self.stdout.write("   0 8 * * 0,6 python manage.py game_day_scheduler --mode=morning")
            self.stdout.write("   0 11,15,19 * * 0,6 python manage.py game_day_scheduler --mode=pregame")
            self.stdout.write("   */30 12-22 * * 0,6 python manage.py live_odds_updater")
            self.stdout.write("   0 23 * * 0,6 python manage.py game_day_scheduler --mode=postgame")