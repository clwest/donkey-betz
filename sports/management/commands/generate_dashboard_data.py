"""
Management command to generate sample sports analytics data for dashboard testing.

This command creates realistic test data including:
- Sample leagues, teams, and games
- Mock odds lines and movements
- Simulated bets and performance data
- Arbitrage opportunities
- Betting recommendations
"""

import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from sports.models import (
    League, Team, Game, Sportsbook, BettingMarket, OddsLine, LineMovement,
    Bet, BankrollManagement, ArbitrageOpportunity, BettingRecommendation,
    SportsAnalytics, GameStatus, MarketStatus
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample sports analytics data for dashboard testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=1,
            help='Number of test users to create'
        )
        parser.add_argument(
            '--games',
            type=int,
            default=20,
            help='Number of games to create'
        )
        parser.add_argument(
            '--bets',
            type=int,
            default=50,
            help='Number of sample bets per user'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing sports data...'))
            self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('Generating sports analytics dashboard data...'))
        
        # Create test users if needed
        users = self.create_test_users(options['users'])
        
        # Create sports data structure
        leagues = self.create_leagues()
        sportsbooks = self.create_sportsbooks()
        teams = self.create_teams(leagues)
        games = self.create_games(leagues, teams, options['games'])
        
        # Create betting infrastructure
        markets = self.create_betting_markets(games)
        odds_lines = self.create_odds_lines(markets, sportsbooks)
        
        # Create sample bets and analytics
        for user in users:
            self.create_user_data(user, odds_lines, options['bets'])
        
        # Generate arbitrage opportunities
        self.create_arbitrage_opportunities(games, markets, sportsbooks)
        
        # Generate recommendations
        self.create_recommendations(users, games, markets)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated dashboard data:\n'
                f'- {len(users)} users\n'
                f'- {len(leagues)} leagues\n'
                f'- {len(teams)} teams\n'
                f'- {len(games)} games\n'
                f'- {len(markets)} betting markets\n'
                f'- {len(odds_lines)} odds lines\n'
                f'- {options["bets"] * len(users)} total bets'
            )
        )
    
    def clear_data(self):
        """Clear existing sports data"""
        models_to_clear = [
            BettingRecommendation, ArbitrageOpportunity, SportsAnalytics,
            Bet, LineMovement, OddsLine, BettingMarket, Game, Team, League,
            Sportsbook, BankrollManagement
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'  Cleared {count} {model.__name__} records')
    
    def create_test_users(self, count):
        """Create test users for dashboard data"""
        users = []
        for i in range(count):
            username = f'testuser{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'first_name': f'Test',
                    'last_name': f'User {i+1}'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                
                # Create bankroll management
                BankrollManagement.objects.create(
                    user=user,
                    initial_balance=Decimal('10000.00'),
                    current_balance=Decimal(str(random.uniform(8000, 15000))),
                    kelly_multiplier=0.25,
                    max_bet_percentage=0.10,
                    total_wagered=Decimal('0.00'),
                    total_profit=Decimal('0.00')
                )
            
            users.append(user)
        
        return users
    
    def create_leagues(self):
        """Create sample leagues"""
        leagues_data = [
            ('NFL', 'National Football League', 'nfl'),
            ('NBA', 'National Basketball Association', 'nba'),
            ('NCAAF', 'College Football', 'ncaaf'),
            ('NCAAB', 'College Basketball', 'ncaab'),
            ('MLB', 'Major League Baseball', 'mlb')
        ]
        
        leagues = []
        for abbrev, name, sport_type in leagues_data:
            league, created = League.objects.get_or_create(
                abbreviation=abbrev,
                defaults={
                    'name': name,
                    'sport_type': sport_type
                }
            )
            leagues.append(league)
        
        return leagues
    
    def create_sportsbooks(self):
        """Create sample sportsbooks"""
        sportsbooks_data = [
            ('DK', 'DraftKings'),
            ('FD', 'FanDuel'),
            ('MGM', 'BetMGM'),
            ('CZR', 'Caesars Sportsbook'),
            ('PB', 'PointsBet')
        ]
        
        sportsbooks = []
        for abbreviation, name in sportsbooks_data:
            sportsbook, created = Sportsbook.objects.get_or_create(
                abbreviation=abbreviation,
                defaults={
                    'name': name
                }
            )
            sportsbooks.append(sportsbook)
        
        return sportsbooks
    
    def create_teams(self, leagues):
        """Create sample teams"""
        teams_data = {
            'NFL': ['Chiefs', 'Bills', 'Cowboys', 'Packers', 'Patriots', 'Steelers'],
            'NBA': ['Lakers', 'Warriors', 'Celtics', 'Heat', 'Bucks', 'Nets'],
            'NCAAF': ['Alabama', 'Georgia', 'Ohio State', 'Michigan', 'Clemson', 'Notre Dame'],
            'NCAAB': ['Duke', 'Kentucky', 'UNC', 'Kansas', 'Villanova', 'Gonzaga'],
            'MLB': ['Yankees', 'Dodgers', 'Red Sox', 'Astros', 'Giants', 'Braves']
        }
        
        teams = []
        for league in leagues:
            if league.abbreviation in teams_data:
                for team_name in teams_data[league.abbreviation]:
                    team, created = Team.objects.get_or_create(
                        name=team_name,
                        league=league,
                        defaults={
                            'abbreviation': team_name[:3].upper(),
                            'city': team_name,
                            'is_active': True
                        }
                    )
                    teams.append(team)
        
        return teams
    
    def create_games(self, leagues, teams, count):
        """Create sample games"""
        games = []
        
        for _ in range(count):
            # Pick random league and get teams from that league
            league = random.choice(leagues)
            league_teams = [t for t in teams if t.league == league]
            
            if len(league_teams) < 2:
                continue
            
            home_team, away_team = random.sample(league_teams, 2)
            
            # Generate game date (mix of past, present, future)
            days_offset = random.randint(-30, 30)
            scheduled_start = timezone.now() + timedelta(days=days_offset)
            
            # Determine game status based on date
            if days_offset < -1:
                status = random.choice([GameStatus.FINAL, GameStatus.FINAL])
                home_score = random.randint(0, 35)
                away_score = random.randint(0, 35)
            elif days_offset <= 0:
                status = random.choice([GameStatus.LIVE, GameStatus.FINAL])
                home_score = random.randint(0, 35) if status == GameStatus.FINAL else random.randint(0, 21)
                away_score = random.randint(0, 35) if status == GameStatus.FINAL else random.randint(0, 21)
            else:
                status = GameStatus.SCHEDULED
                home_score = away_score = None
            
            game, created = Game.objects.get_or_create(
                home_team=home_team,
                away_team=away_team,
                scheduled_start=scheduled_start,
                defaults={
                    'league': league,
                    'status': status,
                    'home_score': home_score,
                    'away_score': away_score
                }
            )
            
            if created:
                games.append(game)
        
        return games
    
    def create_betting_markets(self, games):
        """Create betting markets for games"""
        market_types = ['spread', 'moneyline', 'total']
        markets = []
        
        for game in games:
            for market_type in market_types:
                market, created = BettingMarket.objects.get_or_create(
                    game=game,
                    market_type=market_type,
                    defaults={
                        'market_name': f'{market_type.title()} for {game}',
                        'status': MarketStatus.OPEN
                    }
                )
                markets.append(market)
        
        return markets
    
    def create_odds_lines(self, markets, sportsbooks):
        """Create odds lines for markets"""
        odds_lines = []
        
        for market in markets:
            for sportsbook in sportsbooks:
                # Generate realistic odds based on market type
                if market.market_type == 'spread':
                    home_spread = random.uniform(-14, 14)
                    away_spread = -home_spread
                    home_odds = random.randint(-120, -100)
                    away_odds = random.randint(-120, -100)
                    odds_data = {
                        'home_spread': home_spread,
                        'away_spread': away_spread,
                        'home_odds': home_odds,
                        'away_odds': away_odds
                    }
                elif market.market_type == 'moneyline':
                    home_odds = random.choice([
                        random.randint(-300, -150),  # Favorite
                        random.randint(120, 300)     # Underdog
                    ])
                    away_odds = random.choice([
                        random.randint(-300, -150),  # Favorite  
                        random.randint(120, 300)     # Underdog
                    ])
                    odds_data = {
                        'home_odds': home_odds,
                        'away_odds': away_odds
                    }
                else:  # total
                    total_line = random.uniform(40, 65)
                    over_odds = random.randint(-120, -100)
                    under_odds = random.randint(-120, -100)
                    odds_data = {
                        'total_line': total_line,
                        'over_odds': over_odds,
                        'under_odds': under_odds
                    }
                
                odds_line, created = OddsLine.objects.get_or_create(
                    market=market,
                    sportsbook=sportsbook,
                    defaults=odds_data
                )
                
                if created:
                    odds_lines.append(odds_line)
                    
                    # Create some line movements
                    if random.random() < 0.3:  # 30% chance of movement
                        self.create_line_movements(odds_line)
        
        return odds_lines
    
    def create_line_movements(self, odds_line):
        """Create line movements for an odds line"""
        movements_count = random.randint(1, 5)
        
        for i in range(movements_count):
            timestamp = timezone.now() - timedelta(
                minutes=random.randint(1, 1440)  # Last 24 hours
            )
            
            # Generate movement
            old_odds = odds_line.odds + random.randint(-20, 20)
            old_line = odds_line.line_value
            if old_line:
                old_line += Decimal(str(random.uniform(-2, 2)))
            
            LineMovement.objects.create(
                odds_line=odds_line,
                timestamp=timestamp,
                old_odds=old_odds,
                new_odds=odds_line.odds,
                old_line_value=old_line,
                new_line_value=odds_line.line_value,
                movement_size=abs(odds_line.odds - old_odds)
            )
    
    def create_user_data(self, user, odds_lines, bets_count):
        """Create bets and analytics for a user"""
        # Create sample bets
        for _ in range(bets_count):
            odds_line = random.choice(odds_lines)
            
            # Determine bet outcome based on game status
            if odds_line.market.game.status == GameStatus.FINAL:
                status = random.choices(
                    ['won', 'lost'],
                    weights=[0.45, 0.55]  # Slightly losing record
                )[0]
            else:
                status = 'pending'
            
            amount = Decimal(str(random.uniform(25, 500)))
            
            # Get odds based on selection and bet type
            selection = random.choice(['home', 'away', 'over', 'under'])
            if odds_line.market.market_type == 'moneyline':
                odds_taken = odds_line.home_odds if selection == 'home' else odds_line.away_odds
            elif odds_line.market.market_type == 'spread':
                odds_taken = odds_line.home_odds if selection == 'home' else odds_line.away_odds
            else:  # total
                odds_taken = odds_line.over_odds if selection == 'over' else odds_line.under_odds
            
            odds_taken = odds_taken or -110  # Default odds
            
            if status == 'won':
                if odds_taken > 0:
                    profit = amount * (odds_taken / 100)
                else:
                    profit = amount * (100 / abs(odds_taken))
            elif status == 'lost':
                profit = -amount
            else:
                profit = Decimal('0')
            
            bet_date = timezone.now() - timedelta(
                days=random.randint(0, 60)
            )
            
            Bet.objects.create(
                user=user,
                market=odds_line.market,
                sportsbook=odds_line.sportsbook,
                odds_line=odds_line,
                bet_type=odds_line.market.market_type,
                selection=selection,
                odds_taken=odds_taken,
                stake=amount,
                status=status,
                result_amount=profit
            )
    
    def create_arbitrage_opportunities(self, games, markets, sportsbooks):
        """Create sample arbitrage opportunities"""
        for _ in range(10):  # Create 10 arbitrage opportunities
            game = random.choice(games)
            game_markets = [m for m in markets if m.game == game]
            
            if not game_markets:
                continue
            
            market = random.choice(game_markets)
            
            ArbitrageOpportunity.objects.create(
                game=game,
                market_type=market.market_type,
                profit_percentage=Decimal(str(random.uniform(2, 8))),
                total_stake=Decimal(str(random.uniform(1000, 5000))),
                sportsbooks_involved=random.sample(
                    [sb.name for sb in sportsbooks], 
                    random.randint(2, 3)
                ),
                bet_breakdown=self.generate_bet_breakdown(),
                expires_at=timezone.now() + timedelta(hours=random.randint(1, 24)),
                is_active=True
            )
    
    def create_recommendations(self, users, games, markets):
        """Create sample betting recommendations"""
        for user in users:
            for _ in range(random.randint(3, 8)):  # 3-8 recommendations per user
                game = random.choice(games)
                game_markets = [m for m in markets if m.game == game]
                
                if not game_markets:
                    continue
                
                market = random.choice(game_markets)
                
                BettingRecommendation.objects.create(
                    user=user,
                    game=game,
                    betting_market=market,
                    recommended_bet=random.choice(['home', 'away', 'over', 'under']),
                    confidence_score=Decimal(str(random.uniform(65, 95))),
                    expected_value=Decimal(str(random.uniform(-5, 15))),
                    kelly_bet_size=Decimal(str(random.uniform(50, 300))),
                    reasoning=self.generate_reasoning(),
                    is_active=random.choice([True, True, False]),  # 2/3 active
                    followed=random.choice([True, False]),
                    outcome=random.choice(['won', 'lost', 'pending'])
                )
    
    def generate_bet_breakdown(self):
        """Generate realistic bet breakdown for arbitrage"""
        return {
            'sportsbook_1': {
                'bet': 'home',
                'odds': -110,
                'stake': 550
            },
            'sportsbook_2': {
                'bet': 'away', 
                'odds': 120,
                'stake': 450
            }
        }
    
    def generate_reasoning(self):
        """Generate sample reasoning for recommendations"""
        reasons = [
            "Strong value play based on line movement analysis and team performance metrics.",
            "Kelly criterion suggests optimal bet size due to positive expected value calculation.",
            "Historical matchup data shows consistent pattern favoring this outcome.",
            "Market inefficiency detected across multiple sportsbooks for this selection.",
            "Advanced analytics model indicates significant edge over market consensus.",
            "Weather conditions and injury reports create betting value opportunity.",
            "Sharp money movement suggests professional bettors are backing this play."
        ]
        return random.choice(reasons)