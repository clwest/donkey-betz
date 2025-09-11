"""
Management command to sync sports data from multiple providers

This command replaces the need for Polygon.io by pulling data from:
- ESPN Hidden API (free, comprehensive)
- TheSportsDB.com (free, community-driven)
- The Odds API (free tier available)

Usage:
    python manage.py sync_sports_data --leagues --teams --games --odds
    python manage.py sync_sports_data --all
    python manage.py sync_sports_data --sport nfl --date 2024-09-15
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from sports.data_providers import sports_data_manager
from sports.models import League, SportType


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync sports data from multiple free providers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--leagues',
            action='store_true',
            help='Sync leagues from all providers',
        )
        parser.add_argument(
            '--teams',
            action='store_true',
            help='Sync teams for all leagues',
        )
        parser.add_argument(
            '--games',
            action='store_true',
            help='Sync games for all leagues',
        )
        parser.add_argument(
            '--odds',
            action='store_true',
            help='Sync odds data',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync everything (leagues, teams, games, odds)',
        )
        parser.add_argument(
            '--sport',
            type=str,
            help='Sync only specific sport (nfl, nba, mlb, etc.)',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Sync games for specific date (YYYY-MM-DD format)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to sync games for (default: 7)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏈 Starting Sports Data Sync with Free Providers')
        )
        
        # Log what we're about to do
        providers_info = [
            "📺 ESPN Hidden API (free, comprehensive)",
            "🏆 TheSportsDB.com (free, community-driven)", 
            "💰 The Odds API (free tier)",
        ]
        
        self.stdout.write("Available data sources:")
        for provider in providers_info:
            self.stdout.write(f"  • {provider}")
        
        sync_all = options['all']
        
        # Sync leagues
        if options['leagues'] or sync_all:
            self.sync_leagues()
        
        # Sync teams  
        if options['teams'] or sync_all:
            self.sync_teams(options.get('sport'))
        
        # Sync games
        if options['games'] or sync_all:
            self.sync_games(
                sport=options.get('sport'),
                date=options.get('date'),
                days=options.get('days', 7)
            )
        
        # Sync odds
        if options['odds'] or sync_all:
            self.sync_odds(options.get('sport'))
        
        self.stdout.write(
            self.style.SUCCESS('✅ Sports data sync completed!')
        )

    def sync_leagues(self):
        """Sync leagues from all providers"""
        self.stdout.write("🔄 Syncing leagues...")
        
        results = sports_data_manager.sync_leagues()
        
        self.stdout.write(
            f"  ✅ Created: {results['created']} leagues"
        )
        self.stdout.write(
            f"  🔄 Updated: {results['updated']} leagues"
        )
        
        if results['errors'] > 0:
            self.stdout.write(
                self.style.WARNING(f"  ⚠️ Errors: {results['errors']}")
            )

    def sync_teams(self, sport_filter=None):
        """Sync teams for leagues"""
        self.stdout.write("🔄 Syncing teams...")
        
        leagues = League.objects.filter(is_active=True)
        
        if sport_filter:
            sport_type = self._get_sport_type(sport_filter)
            if sport_type:
                leagues = leagues.filter(sport_type=sport_type)
        
        total_created = 0
        total_updated = 0
        total_errors = 0
        
        for league in leagues:
            self.stdout.write(f"  📋 Syncing teams for {league.name}...")
            
            results = sports_data_manager.sync_teams(league)
            
            total_created += results['created']
            total_updated += results['updated'] 
            total_errors += results['errors']
            
            if results['created'] > 0 or results['updated'] > 0:
                self.stdout.write(
                    f"    ✅ {league.abbreviation}: +{results['created']} new, ~{results['updated']} updated"
                )
        
        self.stdout.write(
            f"  📊 Total: {total_created} created, {total_updated} updated, {total_errors} errors"
        )

    def sync_games(self, sport=None, date=None, days=7):
        """Sync games for leagues"""
        self.stdout.write("🔄 Syncing games...")
        
        leagues = League.objects.filter(is_active=True)
        
        if sport:
            sport_type = self._get_sport_type(sport)
            if sport_type:
                leagues = leagues.filter(sport_type=sport_type)
        
        # Determine date range
        if date:
            start_date = datetime.strptime(date, '%Y-%m-%d').date()
            dates = [start_date]
        else:
            # Sync for next `days` days
            today = timezone.now().date()
            dates = [today + timedelta(days=i) for i in range(days)]
        
        total_created = 0
        total_updated = 0
        total_errors = 0
        
        for league in leagues:
            for sync_date in dates:
                date_str = sync_date.strftime('%Y-%m-%d')
                self.stdout.write(f"  📅 Syncing {league.abbreviation} games for {date_str}...")
                
                results = sports_data_manager.sync_games(league, date_str)
                
                total_created += results['created']
                total_updated += results['updated']
                total_errors += results['errors']
                
                if results['created'] > 0 or results['updated'] > 0:
                    self.stdout.write(
                        f"    🎮 {league.abbreviation} {date_str}: +{results['created']} new, ~{results['updated']} updated"
                    )
        
        self.stdout.write(
            f"  📊 Total games: {total_created} created, {total_updated} updated, {total_errors} errors"
        )

    def sync_odds(self, sport=None):
        """Sync odds data from The Odds API"""
        self.stdout.write("🔄 Syncing odds data...")
        
        # Map our sport types to Odds API sport keys
        odds_api_sports = {
            SportType.NFL: 'americanfootball_nfl',
            SportType.NCAAF: 'americanfootball_ncaaf', 
            SportType.NBA: 'basketball_nba',
            SportType.NCAAB: 'basketball_ncaab',
            SportType.MLB: 'baseball_mlb',
            SportType.NHL: 'icehockey_nhl',
            SportType.SOCCER: 'soccer_epl',  # Premier League as default
            SportType.MMA: 'mma_mixed_martial_arts',
            SportType.TENNIS: 'tennis_atp',
        }
        
        if sport:
            sport_type = self._get_sport_type(sport)
            if sport_type and sport_type in odds_api_sports:
                sports_to_sync = [odds_api_sports[sport_type]]
            else:
                self.stdout.write(
                    self.style.WARNING(f"Sport '{sport}' not supported for odds sync")
                )
                return
        else:
            sports_to_sync = list(odds_api_sports.values())
        
        total_updated = 0
        total_errors = 0
        
        for sport_key in sports_to_sync:
            self.stdout.write(f"  💰 Syncing odds for {sport_key}...")
            
            results = sports_data_manager.sync_odds(sport_key)
            
            total_updated += results['updated']
            total_errors += results['errors']
            
            if results['updated'] > 0:
                self.stdout.write(
                    f"    💸 {sport_key}: {results['updated']} odds updated"
                )
        
        if total_errors > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠️ Note: {total_errors} errors occurred. This is normal for free tier API limits."
                )
            )
        
        self.stdout.write(
            f"  📊 Total odds: {total_updated} updated, {total_errors} errors"
        )

    def _get_sport_type(self, sport_str):
        """Convert string to SportType enum"""
        sport_mapping = {
            'nfl': SportType.NFL,
            'ncaaf': SportType.NCAAF,
            'college-football': SportType.NCAAF,
            'nba': SportType.NBA,
            'ncaab': SportType.NCAAB,
            'college-basketball': SportType.NCAAB,
            'mlb': SportType.MLB,
            'baseball': SportType.MLB,
            'nhl': SportType.NHL,
            'hockey': SportType.NHL,
            'soccer': SportType.SOCCER,
            'football': SportType.SOCCER,  # For international users
            'mma': SportType.MMA,
            'ufc': SportType.MMA,
            'tennis': SportType.TENNIS,
            'golf': SportType.GOLF,
            'boxing': SportType.BOXING,
            'esports': SportType.ESPORTS,
        }
        
        return sport_mapping.get(sport_str.lower())