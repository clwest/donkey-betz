"""
Management command to sync odds from The Odds API
"""
import os
import requests
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from sports.models import (
    League, Team, Game, Sportsbook, BettingMarket, OddsLine,
    SportType, GameStatus, BetType, MarketStatus
)


class Command(BaseCommand):
    help = 'Sync odds data from The Odds API'
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get('THE_ODDS_API_KEY')
        self.base_url = 'https://api.the-odds-api.com/v4'
        self.sportsbooks = {}
        self.leagues = {}
        self.teams = {}
        
    def add_arguments(self, parser):
        parser.add_argument(
            '--sport',
            type=str,
            default='all',
            help='Sport to sync (ncaaf, nfl, nba, mlb, or all)'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode - only fetch data, don\'t save'
        )
    
    def handle(self, *args, **options):
        if not self.api_key:
            self.stdout.write(self.style.ERROR('THE_ODDS_API_KEY not found in environment'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'API Key: {self.api_key[:10]}...'))
        
        # Initialize sportsbooks
        self.init_sportsbooks()
        
        # Map sports
        sports_map = {
            'ncaaf': 'americanfootball_ncaaf',
            'nfl': 'americanfootball_nfl',
            'nba': 'basketball_nba',
            'mlb': 'baseball_mlb',
        }
        
        if options['sport'] == 'all':
            sports = list(sports_map.values())
        else:
            sports = [sports_map.get(options['sport'], options['sport'])]
        
        for sport_key in sports:
            self.sync_sport_odds(sport_key, test_mode=options['test'])
    
    def init_sportsbooks(self):
        """Initialize sportsbooks in database"""
        books = [
            ('draftkings', 'DraftKings', 'DK', True),
            ('fanduel', 'FanDuel', 'FD', True),
            ('betmgm', 'BetMGM', 'MGM', False),
            ('caesars', 'Caesars', 'CZR', False),
            ('pointsbetus', 'PointsBet', 'PB', False),
            ('williamhill_us', 'William Hill', 'WH', False),
        ]
        
        for key, name, abbr, is_sharp in books:
            book, created = Sportsbook.objects.get_or_create(
                abbreviation=abbr,
                defaults={
                    'name': name,
                    'is_sharp': is_sharp,
                    'metadata': {'external_id': key, 'api_provider': 'THE_ODDS_API'}
                }
            )
            self.sportsbooks[key] = book
            if created:
                self.stdout.write(f"  Created sportsbook: {name}")
    
    def sync_sport_odds(self, sport_key, test_mode=False):
        """Sync odds for a specific sport"""
        self.stdout.write(f"\n🏈 Syncing {sport_key}...")
        
        # Get league
        league_map = {
            'americanfootball_ncaaf': 'NCAAF',
            'americanfootball_nfl': 'NFL',
            'basketball_nba': 'NBA',
            'baseball_mlb': 'MLB',
        }
        
        league_abbr = league_map.get(sport_key, sport_key.upper())
        try:
            league = League.objects.get(abbreviation=league_abbr)
            self.leagues[sport_key] = league
        except League.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"  League {league_abbr} not found"))
            return
        
        # Fetch odds
        url = f"{self.base_url}/sports/{sport_key}/odds/"
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american',
            'bookmakers': ','.join(self.sportsbooks.keys())
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"  API Error: {response.status_code}"))
                return
            
            games_data = response.json()
            self.stdout.write(f"  Found {len(games_data)} games with odds")
            
            # Check API usage
            remaining = response.headers.get('x-requests-remaining', 'N/A')
            self.stdout.write(f"  API credits remaining: {remaining}")
            
            if test_mode:
                self.stdout.write("  TEST MODE - not saving to database")
                return
            
            # Process games
            with transaction.atomic():
                for game_data in games_data:
                    self.process_game_odds(game_data, league)
            
            # Summary
            games_count = Game.objects.filter(league=league).count()
            markets_count = BettingMarket.objects.filter(game__league=league).count()
            odds_count = OddsLine.objects.filter(market__game__league=league).count()
            
            self.stdout.write(self.style.SUCCESS(f"  ✅ Complete! Games: {games_count}, Markets: {markets_count}, Odds: {odds_count}"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error: {e}"))
    
    def process_game_odds(self, game_data, league):
        """Process odds for a single game"""
        # Get or create teams
        home_team = self.get_or_create_team(game_data['home_team'], league)
        away_team = self.get_or_create_team(game_data['away_team'], league)
        
        # Get or create game
        game, created = Game.objects.get_or_create(
            external_id=game_data['id'],
            defaults={
                'league': league,
                'home_team': home_team,
                'away_team': away_team,
                'scheduled_start': datetime.fromisoformat(game_data['commence_time'].replace('Z', '+00:00')),
                'status': GameStatus.SCHEDULED,
                'venue_name': f"{home_team.city} Stadium",
                'metadata': {'api_provider': 'THE_ODDS_API'}
            }
        )
        
        if created:
            self.stdout.write(f"    Created game: {away_team.abbreviation} @ {home_team.abbreviation}")
        
        # Process bookmaker odds
        for bookmaker_data in game_data.get('bookmakers', []):
            self.process_bookmaker_odds(game, bookmaker_data)
    
    def get_or_create_team(self, team_name, league):
        """Get or create a team"""
        if team_name in self.teams:
            return self.teams[team_name]
        
        # Try to find existing team
        team = Team.objects.filter(
            name__icontains=team_name.split()[-1],  # Last word (e.g., "Wolfpack")
            league=league
        ).first()
        
        if not team:
            # Create new team with unique abbreviation using get_or_create
            abbr = team_name[:3].upper()
            
            # Use get_or_create with the unique constraint fields
            team, created = Team.objects.get_or_create(
                league=league,
                abbreviation=abbr,
                defaults={
                    'name': team_name,
                    'city': team_name.rsplit(' ', 1)[0] if ' ' in team_name else team_name,
                    'metadata': {'api_provider': 'THE_ODDS_API'}
                }
            )
            self.stdout.write(f"    Created team: {team_name} ({abbr})")
        
        self.teams[team_name] = team
        return team
    
    def process_bookmaker_odds(self, game, bookmaker_data):
        """Process odds from a single bookmaker"""
        sportsbook = self.sportsbooks.get(bookmaker_data['key'])
        if not sportsbook:
            return
        
        for market_data in bookmaker_data['markets']:
            market_type = self.get_market_type(market_data['key'])
            if not market_type:
                continue
            
            # Get or create market
            market, created = BettingMarket.objects.get_or_create(
                game=game,
                market_type=market_type,
                defaults={
                    'market_name': f"{game.away_team.abbreviation} @ {game.home_team.abbreviation} - {market_type}",
                    'status': MarketStatus.OPEN,
                }
            )
            
            # Process outcomes
            for outcome_data in market_data['outcomes']:
                self.create_odds_line(market, sportsbook, outcome_data, market_data.get('point'))
    
    def get_market_type(self, market_key):
        """Convert API market key to our BetType"""
        mapping = {
            'h2h': BetType.MONEYLINE,
            'spreads': BetType.SPREAD,
            'totals': BetType.TOTAL,
        }
        return mapping.get(market_key)
    
    def create_odds_line(self, market, sportsbook, outcome_data, point=None):
        """Create or update odds line"""
        # Deactivate old lines for this market/sportsbook
        OddsLine.objects.filter(
            market=market,
            sportsbook=sportsbook,
            is_current=True
        ).update(is_current=False)
        
        # Parse odds
        american_odds = outcome_data['price']
        if american_odds > 0:
            decimal_odds = (american_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(american_odds)) + 1
        
        # Determine if home or away
        is_home = outcome_data['name'] == market.game.home_team.name
        
        # Create new line based on market type
        odds_data = {
            'market': market,
            'sportsbook': sportsbook,
            'decimal_odds': Decimal(str(decimal_odds)),
            'is_current': True,
            'metadata': {
                'outcome_name': outcome_data['name'],
                'american_odds': american_odds,
                'implied_probability': 1 / decimal_odds
            }
        }
        
        if market.market_type == BetType.MONEYLINE:
            if is_home:
                odds_data['home_odds'] = american_odds
            else:
                odds_data['away_odds'] = american_odds
        elif market.market_type == BetType.SPREAD:
            if is_home:
                odds_data['home_spread'] = Decimal(str(point)) if point else Decimal('0')
                odds_data['home_odds'] = american_odds
            else:
                odds_data['away_spread'] = Decimal(str(point)) if point else Decimal('0')
                odds_data['away_odds'] = american_odds
        elif market.market_type == BetType.TOTAL:
            odds_data['total_line'] = Decimal(str(point)) if point else Decimal('0')
            if 'over' in outcome_data['name'].lower():
                odds_data['over_odds'] = american_odds
            else:
                odds_data['under_odds'] = american_odds
        
        OddsLine.objects.create(**odds_data)