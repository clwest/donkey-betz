"""
Sports-Specific Tools for Agent Execution

Provides real data access and computational tools for sports betting agents.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone

from .base import BaseTool
from sports.data_providers import ESPNProvider, TheOddsAPIProvider
from sports.models import Game, BettingMarket, OddsLine, Team
from sports.services import KellyCriterionService, ArbitrageDetectionService

logger = logging.getLogger(__name__)


class OddsDataAccessTool(BaseTool):
    """Tool for accessing real-time odds data from multiple sportsbooks"""
    
    def __init__(self):
        self.name = "odds_data_access"
        self.description = "Access real-time odds data from multiple sportsbooks"
        self.odds_provider = TheOddsAPIProvider()
    
    def _check_configuration(self) -> bool:
        """Check if tool is properly configured"""
        return True
        
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "sport": "Sport key (e.g., 'americanfootball_nfl')",
                "market": "Market type (h2h, spreads, totals)",
                "game_id": "Optional specific game ID"
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Fetch real-time odds data"""
        try:
            sport = kwargs.get('sport', 'americanfootball_nfl')
            market = kwargs.get('market', 'h2h')
            game_id = kwargs.get('game_id')
            
            # Fetch odds from The Odds API
            odds_data = self.odds_provider.get_odds(sport, [market])
            
            if game_id:
                # Filter for specific game
                odds_data = [
                    game for game in odds_data 
                    if game.get('id') == game_id
                ]
            
            # Also check database for cached odds
            db_odds = []
            if game_id:
                try:
                    game = Game.objects.get(external_id=game_id)
                    markets = BettingMarket.objects.filter(game=game, market_type=market)
                    for market_obj in markets:
                        lines = OddsLine.objects.filter(market=market_obj).order_by('-created_at')[:5]
                        db_odds.append({
                            'market': market_obj.market_type,
                            'lines': [
                                {
                                    'bookmaker': line.bookmaker,
                                    'home_odds': float(line.home_odds),
                                    'away_odds': float(line.away_odds),
                                    'timestamp': line.created_at.isoformat()
                                }
                                for line in lines
                            ]
                        })
                except Game.DoesNotExist:
                    pass
            
            return {
                'success': True,
                'live_odds': odds_data,
                'cached_odds': db_odds,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"OddsDataAccessTool error: {e}")
            return {
                'success': False,
                'error': str(e),
                'live_odds': [],
                'cached_odds': []
            }


class MathematicalCalculationsTool(BaseTool):
    """Tool for performing betting-related mathematical calculations"""
    
    def __init__(self):
        self.name = "mathematical_calculations"
        self.description = "Perform mathematical calculations for betting analysis"
    
    def _check_configuration(self) -> bool:
        """Check if tool is properly configured"""
        return True
        
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "operations": [
                "implied_probability",
                "expected_value",
                "roi_calculation",
                "parlay_odds",
                "hedge_calculation"
            ]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Perform mathematical calculations"""
        try:
            operation = kwargs.get('operation', 'implied_probability')
            
            if operation == 'implied_probability':
                odds = kwargs.get('odds', 0)
                return self._calculate_implied_probability(odds)
            
            elif operation == 'expected_value':
                odds = kwargs.get('odds', 0)
                probability = kwargs.get('probability', 0.5)
                stake = kwargs.get('stake', 100)
                return self._calculate_expected_value(odds, probability, stake)
            
            elif operation == 'roi_calculation':
                profit = kwargs.get('profit', 0)
                stake = kwargs.get('stake', 100)
                return self._calculate_roi(profit, stake)
            
            elif operation == 'parlay_odds':
                legs = kwargs.get('legs', [])
                return self._calculate_parlay_odds(legs)
            
            elif operation == 'hedge_calculation':
                original_bet = kwargs.get('original_bet', {})
                hedge_odds = kwargs.get('hedge_odds', 0)
                return self._calculate_hedge(original_bet, hedge_odds)
            
            else:
                return {'success': False, 'error': f'Unknown operation: {operation}'}
                
        except Exception as e:
            logger.error(f"MathematicalCalculationsTool error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_implied_probability(self, odds: float) -> Dict[str, Any]:
        """Convert odds to implied probability"""
        if odds > 0:  # American odds (positive)
            probability = 100 / (odds + 100)
        elif odds < 0:  # American odds (negative)
            probability = abs(odds) / (abs(odds) + 100)
        else:
            return {'success': False, 'error': 'Invalid odds value'}
        
        return {
            'success': True,
            'odds': odds,
            'implied_probability': probability,
            'percentage': f"{probability * 100:.2f}%"
        }
    
    def _calculate_expected_value(self, odds: float, probability: float, stake: float) -> Dict[str, Any]:
        """Calculate expected value of a bet"""
        if odds > 0:
            potential_profit = stake * (odds / 100)
        else:
            potential_profit = stake * (100 / abs(odds))
        
        ev = (probability * potential_profit) - ((1 - probability) * stake)
        
        return {
            'success': True,
            'expected_value': ev,
            'roi_percentage': (ev / stake) * 100,
            'edge': probability - self._calculate_implied_probability(odds)['implied_probability']
        }
    
    def _calculate_roi(self, profit: float, stake: float) -> Dict[str, Any]:
        """Calculate return on investment"""
        if stake == 0:
            return {'success': False, 'error': 'Stake cannot be zero'}
        
        roi = (profit / stake) * 100
        
        return {
            'success': True,
            'roi_percentage': roi,
            'profit': profit,
            'stake': stake
        }
    
    def _calculate_parlay_odds(self, legs: List[float]) -> Dict[str, Any]:
        """Calculate combined parlay odds"""
        if not legs:
            return {'success': False, 'error': 'No legs provided'}
        
        decimal_odds = []
        for odds in legs:
            if odds > 0:
                decimal_odds.append((odds / 100) + 1)
            else:
                decimal_odds.append((100 / abs(odds)) + 1)
        
        combined_decimal = 1
        for decimal in decimal_odds:
            combined_decimal *= decimal
        
        # Convert back to American odds
        if combined_decimal >= 2:
            american_odds = (combined_decimal - 1) * 100
        else:
            american_odds = -100 / (combined_decimal - 1)
        
        return {
            'success': True,
            'parlay_odds': american_odds,
            'decimal_odds': combined_decimal,
            'potential_payout': combined_decimal * 100  # For $100 bet
        }
    
    def _calculate_hedge(self, original_bet: Dict, hedge_odds: float) -> Dict[str, Any]:
        """Calculate optimal hedge amount"""
        original_stake = original_bet.get('stake', 0)
        original_odds = original_bet.get('odds', 0)
        
        if original_odds > 0:
            original_payout = original_stake * (1 + original_odds / 100)
        else:
            original_payout = original_stake * (1 + 100 / abs(original_odds))
        
        if hedge_odds > 0:
            hedge_stake = original_payout / (1 + hedge_odds / 100)
        else:
            hedge_stake = original_payout / (1 + 100 / abs(hedge_odds))
        
        guaranteed_profit = original_payout - original_stake - hedge_stake
        
        return {
            'success': True,
            'hedge_stake': hedge_stake,
            'guaranteed_profit': guaranteed_profit,
            'original_payout': original_payout
        }


class KellyCriterionTool(BaseTool):
    """Tool for Kelly Criterion bet sizing calculations"""
    
    def __init__(self):
        self.name = "kelly_criterion"
        self.description = "Calculate optimal bet sizes using Kelly Criterion"
        self.kelly_service = KellyCriterionService()
    
    def _check_configuration(self) -> bool:
        """Check if tool is properly configured"""
        return True
        
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "probability": "Win probability (0-1)",
                "odds": "American odds",
                "bankroll": "Current bankroll size",
                "kelly_fraction": "Kelly fraction (default 0.25 for quarter Kelly)"
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Calculate Kelly Criterion bet size"""
        try:
            probability = kwargs.get('probability', 0.5)
            odds = kwargs.get('odds', 100)
            bankroll = kwargs.get('bankroll', 1000)
            kelly_fraction = kwargs.get('kelly_fraction', 0.25)
            
            # Convert American odds to decimal
            if odds > 0:
                decimal_odds = (odds / 100) + 1
            else:
                decimal_odds = (100 / abs(odds)) + 1
            
            # Kelly formula: f = (p * b - q) / b
            # where f = fraction, p = probability, b = decimal odds - 1, q = 1 - p
            b = decimal_odds - 1
            q = 1 - probability
            
            kelly_percentage = (probability * b - q) / b
            
            # Apply Kelly fraction for safety
            adjusted_kelly = kelly_percentage * kelly_fraction
            
            # Calculate bet size
            bet_size = bankroll * adjusted_kelly
            
            # Ensure non-negative
            if bet_size < 0:
                bet_size = 0
                adjusted_kelly = 0
            
            return {
                'success': True,
                'kelly_percentage': kelly_percentage * 100,
                'adjusted_kelly': adjusted_kelly * 100,
                'recommended_bet': bet_size,
                'bankroll': bankroll,
                'kelly_fraction': kelly_fraction,
                'edge': (probability * decimal_odds) - 1
            }
            
        except Exception as e:
            logger.error(f"KellyCriterionTool error: {e}")
            return {'success': False, 'error': str(e)}


class GameDataTool(BaseTool):
    """Tool for accessing game and team information"""
    
    def __init__(self):
        self.name = "game_data"
        self.description = "Access game schedules, team info, and historical data"
        self.espn_provider = ESPNProvider()
    
    def _check_configuration(self) -> bool:
        """Check if tool is properly configured"""
        return True
        
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "operations": ["get_games", "get_team_info", "get_head_to_head"]
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Fetch game and team data"""
        try:
            operation = kwargs.get('operation', 'get_games')
            
            if operation == 'get_games':
                sport = kwargs.get('sport', 'nfl')
                date = kwargs.get('date')
                
                # Try ESPN API first
                espn_data = self.espn_provider.get_scoreboard(sport, date)
                
                # Also get from database
                db_games = []
                if date:
                    target_date = datetime.strptime(date, '%Y-%m-%d')
                    games = Game.objects.filter(
                        scheduled_start__date=target_date.date(),
                        league__abbreviation__iexact=sport
                    )
                else:
                    # Get today's and upcoming games
                    games = Game.objects.filter(
                        scheduled_start__gte=timezone.now() - timedelta(hours=12),
                        scheduled_start__lte=timezone.now() + timedelta(days=7),
                        league__abbreviation__iexact=sport
                    )
                
                for game in games[:20]:  # Limit to 20 games
                    db_games.append({
                        'id': str(game.id),
                        'home_team': game.home_team.name,
                        'away_team': game.away_team.name,
                        'scheduled_start': game.scheduled_start.isoformat(),
                        'status': game.status,
                        'venue': game.venue_name
                    })
                
                return {
                    'success': True,
                    'espn_games': espn_data.get('events', []),
                    'db_games': db_games
                }
            
            elif operation == 'get_team_info':
                team_name = kwargs.get('team_name')
                
                try:
                    team = Team.objects.get(
                        Q(name__icontains=team_name) | 
                        Q(abbreviation__iexact=team_name)
                    )
                    
                    # Get recent games
                    recent_games = Game.objects.filter(
                        Q(home_team=team) | Q(away_team=team),
                        status='completed'
                    ).order_by('-scheduled_start')[:10]
                    
                    game_results = []
                    for game in recent_games:
                        is_home = game.home_team == team
                        game_results.append({
                            'date': game.scheduled_start.isoformat(),
                            'opponent': game.away_team.name if is_home else game.home_team.name,
                            'location': 'home' if is_home else 'away',
                            'score': f"{game.home_score}-{game.away_score}" if game.home_score else 'N/A'
                        })
                    
                    return {
                        'success': True,
                        'team': {
                            'name': team.name,
                            'abbreviation': team.abbreviation,
                            'conference': team.conference,
                            'division': team.division
                        },
                        'recent_games': game_results
                    }
                    
                except Team.DoesNotExist:
                    return {'success': False, 'error': f'Team not found: {team_name}'}
            
            elif operation == 'get_head_to_head':
                team1 = kwargs.get('team1')
                team2 = kwargs.get('team2')
                
                try:
                    t1 = Team.objects.get(Q(name__icontains=team1) | Q(abbreviation__iexact=team1))
                    t2 = Team.objects.get(Q(name__icontains=team2) | Q(abbreviation__iexact=team2))
                    
                    h2h_games = Game.objects.filter(
                        Q(home_team=t1, away_team=t2) | Q(home_team=t2, away_team=t1),
                        status='completed'
                    ).order_by('-scheduled_start')[:10]
                    
                    results = []
                    for game in h2h_games:
                        results.append({
                            'date': game.scheduled_start.isoformat(),
                            'home': game.home_team.name,
                            'away': game.away_team.name,
                            'score': f"{game.home_score}-{game.away_score}" if game.home_score else 'N/A'
                        })
                    
                    return {
                        'success': True,
                        'matchup': f"{t1.name} vs {t2.name}",
                        'games': results
                    }
                    
                except Team.DoesNotExist as e:
                    return {'success': False, 'error': str(e)}
            
            else:
                return {'success': False, 'error': f'Unknown operation: {operation}'}
                
        except Exception as e:
            logger.error(f"GameDataTool error: {e}")
            return {'success': False, 'error': str(e)}


class ArbitrageDetectionTool(BaseTool):
    """Tool for detecting arbitrage opportunities across sportsbooks"""
    
    def __init__(self):
        self.name = "arbitrage_detection"
        self.description = "Detect arbitrage opportunities across multiple sportsbooks"
        self.arb_service = ArbitrageDetectionService()
    
    def _check_configuration(self) -> bool:
        """Check if tool is properly configured"""
        return True
        
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "sport": "Sport to scan",
                "min_profit": "Minimum profit percentage"
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Scan for arbitrage opportunities"""
        try:
            sport = kwargs.get('sport', 'nfl')
            min_profit = kwargs.get('min_profit', 1.0)
            
            # Get all upcoming games
            games = Game.objects.filter(
                scheduled_start__gte=datetime.now(),
                scheduled_start__lte=datetime.now() + timedelta(days=7),
                league__abbreviation__iexact=sport
            )
            
            opportunities = []
            
            for game in games[:20]:  # Limit scan
                markets = BettingMarket.objects.filter(game=game)
                
                for market in markets:
                    # Get latest odds from all bookmakers
                    lines = OddsLine.objects.filter(market=market).order_by('bookmaker', '-created_at')
                    
                    # Group by bookmaker and get latest
                    bookmaker_odds = {}
                    for line in lines:
                        if line.bookmaker not in bookmaker_odds:
                            bookmaker_odds[line.bookmaker] = {
                                'home': float(line.home_odds),
                                'away': float(line.away_odds)
                            }
                    
                    # Check for arbitrage
                    if len(bookmaker_odds) >= 2:
                        arb_check = self._check_arbitrage(bookmaker_odds)
                        if arb_check and arb_check['profit_percentage'] >= min_profit:
                            opportunities.append({
                                'game': f"{game.away_team.name} @ {game.home_team.name}",
                                'market': market.market_type,
                                'profit': arb_check['profit_percentage'],
                                'bets': arb_check['bets']
                            })
            
            return {
                'success': True,
                'opportunities': opportunities,
                'scanned_games': len(games)
            }
            
        except Exception as e:
            logger.error(f"ArbitrageDetectionTool error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_arbitrage(self, bookmaker_odds: Dict) -> Optional[Dict]:
        """Check if arbitrage opportunity exists"""
        best_home_odds = 0
        best_home_book = ""
        best_away_odds = 0
        best_away_book = ""
        
        for book, odds in bookmaker_odds.items():
            if odds['home'] > best_home_odds:
                best_home_odds = odds['home']
                best_home_book = book
            if odds['away'] > best_away_odds:
                best_away_odds = odds['away']
                best_away_book = book
        
        # Convert to decimal and check arbitrage
        if best_home_odds > 0:
            home_decimal = (best_home_odds / 100) + 1
        else:
            home_decimal = (100 / abs(best_home_odds)) + 1
        
        if best_away_odds > 0:
            away_decimal = (best_away_odds / 100) + 1
        else:
            away_decimal = (100 / abs(best_away_odds)) + 1
        
        # Arbitrage exists if sum of inverses < 1
        arb_sum = (1 / home_decimal) + (1 / away_decimal)
        
        if arb_sum < 1:
            profit = (1 - arb_sum) * 100
            
            # Calculate stakes for $1000 total
            home_stake = 1000 * (1 / home_decimal) / arb_sum
            away_stake = 1000 * (1 / away_decimal) / arb_sum
            
            return {
                'profit_percentage': profit,
                'bets': [
                    {'book': best_home_book, 'bet': 'home', 'odds': best_home_odds, 'stake': home_stake},
                    {'book': best_away_book, 'bet': 'away', 'odds': best_away_odds, 'stake': away_stake}
                ]
            }
        
        return None


class LineMovementTool(BaseTool):
    """Tool for tracking and analyzing line movements"""
    
    def __init__(self):
        self.name = "line_movement"
        self.description = "Track and analyze betting line movements"
    
    def _check_configuration(self) -> bool:
        """Check if tool is properly configured"""
        return True
        
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "game_id": "Game ID to track",
                "market_type": "Market type (spread, total, moneyline)"
            }
        }
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Track line movements for a game"""
        try:
            game_id = kwargs.get('game_id')
            market_type = kwargs.get('market_type', 'spread')
            
            if not game_id:
                return {'success': False, 'error': 'Game ID required'}
            
            game = Game.objects.get(id=game_id)
            market = BettingMarket.objects.get(game=game, market_type=market_type)
            
            # Get line history
            lines = OddsLine.objects.filter(market=market).order_by('created_at')
            
            movement_data = []
            bookmaker_movements = {}
            
            for line in lines:
                if line.bookmaker not in bookmaker_movements:
                    bookmaker_movements[line.bookmaker] = []
                
                bookmaker_movements[line.bookmaker].append({
                    'timestamp': line.created_at.isoformat(),
                    'home_odds': float(line.home_odds),
                    'away_odds': float(line.away_odds),
                    'home_spread': float(line.home_spread) if line.home_spread else None,
                    'away_spread': float(line.away_spread) if line.away_spread else None,
                    'total': float(line.total_points) if line.total_points else None
                })
            
            # Analyze movements
            analysis = self._analyze_movements(bookmaker_movements)
            
            return {
                'success': True,
                'game': f"{game.away_team.name} @ {game.home_team.name}",
                'market': market_type,
                'movements': bookmaker_movements,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"LineMovementTool error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_movements(self, movements: Dict) -> Dict:
        """Analyze line movement patterns"""
        steam_moves = []
        reverse_moves = []
        
        for book, history in movements.items():
            if len(history) < 2:
                continue
            
            # Check for steam moves (all books moving same direction)
            initial = history[0]
            latest = history[-1]
            
            if 'home_spread' in initial and initial['home_spread'] is not None:
                spread_move = latest['home_spread'] - initial['home_spread']
                if abs(spread_move) >= 1:  # Significant move
                    steam_moves.append({
                        'book': book,
                        'move': spread_move,
                        'direction': 'home' if spread_move < 0 else 'away'
                    })
        
        return {
            'steam_moves': steam_moves,
            'reverse_moves': reverse_moves,
            'consensus_direction': 'home' if len([m for m in steam_moves if m['direction'] == 'home']) > len([m for m in steam_moves if m['direction'] == 'away']) else 'away'
        }


# Register all sports tools
def register_sports_tools():
    """Register all sports-specific tools in the ToolRegistry"""
    from core.tools import ToolRegistry
    
    tools_to_register = [
        ('odds_data_access', OddsDataAccessTool),
        ('mathematical_calculations', MathematicalCalculationsTool),
        ('kelly_criterion', KellyCriterionTool),
        ('game_data', GameDataTool),
        ('arbitrage_detection', ArbitrageDetectionTool),
        ('line_movement', LineMovementTool)
    ]
    
    registered = []
    for name, tool_class in tools_to_register:
        try:
            ToolRegistry.register(name, tool_class)
            registered.append(name)
            logger.info(f"Registered sports tool: {name}")
        except Exception as e:
            logger.error(f"Failed to register sports tool {name}: {e}")
    
    return registered