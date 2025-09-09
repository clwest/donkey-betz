"""
Sports Analytics Services

Comprehensive services for odds ingestion, line movement tracking, Kelly Criterion calculations,
arbitrage detection, and betting recommendation generation integrated with the agent orchestration system.
"""

import asyncio
import aiohttp
import logging
import math
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.core.cache import cache
from asgiref.sync import sync_to_async

from .models import (
    League, Team, Game, Sportsbook, BettingMarket, OddsLine, LineMovement,
    Bet, BankrollManagement, ArbitrageOpportunity, BettingRecommendation,
    SportsAnalytics, SportType, GameStatus, BetType, MarketStatus, RiskLevel
)
from core.models import PlatformMetrics


logger = logging.getLogger(__name__)


@dataclass
class OddsData:
    """Data structure for odds information"""
    sportsbook_id: str
    home_odds: Optional[int] = None
    away_odds: Optional[int] = None
    home_spread: Optional[float] = None
    away_spread: Optional[float] = None
    total_line: Optional[float] = None
    over_odds: Optional[int] = None
    under_odds: Optional[int] = None
    timestamp: Optional[datetime] = None


@dataclass
class GameData:
    """Data structure for game information"""
    external_id: str
    home_team: str
    away_team: str
    scheduled_start: datetime
    league: str
    season: str
    status: str = GameStatus.SCHEDULED
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    venue_name: Optional[str] = None
    weather_data: Optional[Dict] = None


class OddsIngestionService:
    """Service for ingesting odds data from multiple sportsbooks"""
    
    def __init__(self):
        self.session = None
        self.rate_limits = {}  # Track rate limits per provider
        self.error_counts = {}  # Track errors per provider
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def ingest_all_odds(self, sport_types: List[str] = None):
        """Ingest odds from all configured sportsbooks"""
        if not sport_types:
            sport_types = [choice[0] for choice in SportType.choices]
        
        sportsbooks = await sync_to_async(list)(
            Sportsbook.objects.filter(is_active=True)
        )
        
        tasks = []
        for sportsbook in sportsbooks:
            for sport_type in sport_types:
                tasks.append(
                    self.ingest_sportsbook_odds(sportsbook, sport_type)
                )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log results
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        error_count = len(results) - success_count
        
        logger.info(f"Odds ingestion completed: {success_count} successful, {error_count} errors")
        
        # Record metrics
        await sync_to_async(PlatformMetrics.record_metric)(
            'odds_ingestion_success', success_count, 'counter', 'sports'
        )
        await sync_to_async(PlatformMetrics.record_metric)(
            'odds_ingestion_errors', error_count, 'counter', 'sports'
        )
        
        return results
    
    async def ingest_sportsbook_odds(self, sportsbook: Sportsbook, sport_type: str):
        """Ingest odds from a specific sportsbook for a sport"""
        try:
            # Check rate limits
            if not self._can_make_request(sportsbook.id):
                logger.warning(f"Rate limit exceeded for {sportsbook.name}")
                return
            
            # Get games for this sport
            games = await self._get_games_for_ingestion(sport_type)
            
            for game in games:
                try:
                    odds_data = await self._fetch_game_odds(sportsbook, game)
                    if odds_data:
                        await self._process_odds_data(game, sportsbook, odds_data)
                        
                except Exception as e:
                    logger.error(f"Error processing game {game.id} for {sportsbook.name}: {e}")
                    self._record_error(sportsbook.id)
                    
            self._record_successful_request(sportsbook.id)
            
        except Exception as e:
            logger.error(f"Error ingesting odds from {sportsbook.name}: {e}")
            self._record_error(sportsbook.id)
            raise
    
    async def _get_games_for_ingestion(self, sport_type: str):
        """Get games that need odds updates"""
        # Get games scheduled in the next 7 days
        start_time = timezone.now()
        end_time = start_time + timedelta(days=7)
        
        games = await sync_to_async(list)(
            Game.objects.filter(
                league__sport_type=sport_type,
                scheduled_start__gte=start_time,
                scheduled_start__lte=end_time,
                status__in=[GameStatus.SCHEDULED, GameStatus.LIVE],
                is_active=True
            ).select_related('league', 'home_team', 'away_team')
        )
        
        return games
    
    async def _fetch_game_odds(self, sportsbook: Sportsbook, game: Game) -> Optional[List[OddsData]]:
        """Fetch odds for a specific game from a sportsbook"""
        if not sportsbook.api_endpoint:
            return None
        
        try:
            # Build API URL based on sportsbook configuration
            url = self._build_odds_url(sportsbook, game)
            headers = self._build_headers(sportsbook)
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_odds_response(sportsbook, data)
                else:
                    logger.warning(f"API error {response.status} for {sportsbook.name}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching odds from {sportsbook.name}: {e}")
            return None
    
    def _build_odds_url(self, sportsbook: Sportsbook, game: Game) -> str:
        """Build API URL for fetching odds"""
        # This would be customized per sportsbook
        base_url = sportsbook.api_endpoint.rstrip('/')
        
        # Generic structure - would be customized per provider
        return f"{base_url}/odds/{game.external_id}"
    
    def _build_headers(self, sportsbook: Sportsbook) -> Dict[str, str]:
        """Build headers for API request"""
        headers = {
            'User-Agent': 'Unified-Donkey-Betz/1.0',
            'Accept': 'application/json',
        }
        
        # Add authentication if configured
        auth_config = sportsbook.api_key_config
        if auth_config.get('api_key'):
            headers['X-API-Key'] = auth_config['api_key']
        elif auth_config.get('bearer_token'):
            headers['Authorization'] = f"Bearer {auth_config['bearer_token']}"
        
        return headers
    
    def _parse_odds_response(self, sportsbook: Sportsbook, data: Dict) -> List[OddsData]:
        """Parse odds response from API"""
        # This would be customized per sportsbook API format
        odds_list = []
        
        # Generic parsing - would be customized per provider
        if 'markets' in data:
            for market in data['markets']:
                odds_data = OddsData(
                    sportsbook_id=str(sportsbook.id),
                    timestamp=timezone.now()
                )
                
                if market.get('type') == 'moneyline':
                    odds_data.home_odds = market.get('home_odds')
                    odds_data.away_odds = market.get('away_odds')
                elif market.get('type') == 'spread':
                    odds_data.home_spread = market.get('home_spread')
                    odds_data.away_spread = market.get('away_spread')
                elif market.get('type') == 'total':
                    odds_data.total_line = market.get('total')
                    odds_data.over_odds = market.get('over_odds')
                    odds_data.under_odds = market.get('under_odds')
                
                odds_list.append(odds_data)
        
        return odds_list
    
    @transaction.atomic
    async def _process_odds_data(self, game: Game, sportsbook: Sportsbook, odds_data_list: List[OddsData]):
        """Process and store odds data"""
        for odds_data in odds_data_list:
            # Determine market type
            if odds_data.home_odds and odds_data.away_odds:
                market_type = BetType.MONEYLINE
            elif odds_data.home_spread is not None:
                market_type = BetType.SPREAD
            elif odds_data.total_line is not None:
                market_type = BetType.TOTAL
            else:
                continue
            
            # Get or create market
            market = await sync_to_async(BettingMarket.objects.get_or_create)(
                game=game,
                market_type=market_type,
                defaults={
                    'market_name': f"{game.away_team.abbreviation} @ {game.home_team.abbreviation} {market_type}",
                    'status': MarketStatus.OPEN
                }
            )
            market = market[0]  # get_or_create returns (obj, created)
            
            # Check for existing current line
            current_line = await sync_to_async(
                lambda: OddsLine.objects.filter(
                    market=market,
                    sportsbook=sportsbook,
                    is_current=True
                ).first()
            )()
            
            # Create new line
            new_line = OddsLine(
                market=market,
                sportsbook=sportsbook,
                home_odds=odds_data.home_odds,
                away_odds=odds_data.away_odds,
                home_spread=odds_data.home_spread,
                away_spread=odds_data.away_spread,
                total_line=odds_data.total_line,
                over_odds=odds_data.over_odds,
                under_odds=odds_data.under_odds,
                line_sequence=1,
                is_current=True
            )
            
            # Check for line movement
            if current_line:
                movement = self._detect_line_movement(current_line, new_line)
                if movement:
                    # Mark old line as not current
                    current_line.is_current = False
                    await sync_to_async(current_line.save)()
                    
                    # Set new line sequence
                    new_line.line_sequence = current_line.line_sequence + 1
                    
                    # Save new line
                    await sync_to_async(new_line.save)()
                    
                    # Create line movement record
                    await self._create_line_movement(market, sportsbook, current_line, new_line, movement)
                else:
                    # No significant movement, don't create new line
                    continue
            else:
                # First line for this market/sportsbook
                await sync_to_async(new_line.save)()
    
    def _detect_line_movement(self, old_line: OddsLine, new_line: OddsLine) -> Optional[Dict]:
        """Detect if there's significant line movement"""
        movements = []
        
        # Check moneyline movement
        if old_line.home_odds and new_line.home_odds:
            if abs(old_line.home_odds - new_line.home_odds) >= 10:  # 10 point threshold
                movements.append({
                    'type': 'home_moneyline',
                    'old_value': old_line.home_odds,
                    'new_value': new_line.home_odds,
                    'size': abs(old_line.home_odds - new_line.home_odds)
                })
        
        if old_line.away_odds and new_line.away_odds:
            if abs(old_line.away_odds - new_line.away_odds) >= 10:
                movements.append({
                    'type': 'away_moneyline',
                    'old_value': old_line.away_odds,
                    'new_value': new_line.away_odds,
                    'size': abs(old_line.away_odds - new_line.away_odds)
                })
        
        # Check spread movement
        if old_line.home_spread is not None and new_line.home_spread is not None:
            if abs(old_line.home_spread - new_line.home_spread) >= 0.5:  # 0.5 point threshold
                movements.append({
                    'type': 'spread',
                    'old_value': old_line.home_spread,
                    'new_value': new_line.home_spread,
                    'size': abs(old_line.home_spread - new_line.home_spread)
                })
        
        # Check total movement
        if old_line.total_line is not None and new_line.total_line is not None:
            if abs(old_line.total_line - new_line.total_line) >= 0.5:
                movements.append({
                    'type': 'total',
                    'old_value': old_line.total_line,
                    'new_value': new_line.total_line,
                    'size': abs(old_line.total_line - new_line.total_line)
                })
        
        return movements[0] if movements else None
    
    async def _create_line_movement(self, market: BettingMarket, sportsbook: Sportsbook,
                                  old_line: OddsLine, new_line: OddsLine, movement: Dict):
        """Create line movement record"""
        movement_direction = 'up' if movement['new_value'] > movement['old_value'] else 'down'
        
        # Determine if movement is significant
        is_significant = movement['size'] >= self._get_significance_threshold(movement['type'])
        
        line_movement = LineMovement(
            market=market,
            sportsbook=sportsbook,
            old_line=old_line,
            new_line=new_line,
            movement_size=movement['size'],
            movement_direction=movement_direction,
            is_significant=is_significant
        )
        
        await sync_to_async(line_movement.save)()
        
        # If significant movement, trigger alerts
        if is_significant:
            await self._trigger_movement_alerts(line_movement)
    
    def _get_significance_threshold(self, movement_type: str) -> float:
        """Get threshold for significant movement"""
        thresholds = {
            'home_moneyline': 20,
            'away_moneyline': 20,
            'spread': 1.0,
            'total': 1.0
        }
        return thresholds.get(movement_type, 10)
    
    async def _trigger_movement_alerts(self, movement: LineMovement):
        """Trigger alerts for significant line movements"""
        # This would integrate with notification systems
        logger.info(f"Significant line movement detected: {movement}")
        
        # Record metric
        await sync_to_async(PlatformMetrics.record_metric)(
            'significant_line_movements', 1, 'counter', 'sports'
        )
    
    def _can_make_request(self, sportsbook_id: str) -> bool:
        """Check if we can make a request to this sportsbook"""
        now = timezone.now()
        key = f"rate_limit_{sportsbook_id}"
        
        last_request = self.rate_limits.get(key)
        if not last_request:
            self.rate_limits[key] = now
            return True
        
        # Allow 1 request per second per sportsbook
        if (now - last_request).total_seconds() >= 1:
            self.rate_limits[key] = now
            return True
        
        return False
    
    def _record_successful_request(self, sportsbook_id: str):
        """Record successful request"""
        self.error_counts[sportsbook_id] = 0
    
    def _record_error(self, sportsbook_id: str):
        """Record error for sportsbook"""
        self.error_counts[sportsbook_id] = self.error_counts.get(sportsbook_id, 0) + 1


class KellyCriterionService:
    """Service for Kelly Criterion calculations and risk management"""
    
    @staticmethod
    def calculate_kelly_bet_size(bankroll: BankrollManagement, true_probability: float,
                               odds: int, confidence: float = 1.0) -> Dict[str, Any]:
        """
        Calculate optimal bet size using Kelly Criterion
        
        Args:
            bankroll: User's bankroll management object
            true_probability: Estimated true probability (0-1)
            odds: American odds
            confidence: Confidence multiplier (0-1)
        
        Returns:
            Dictionary with bet size recommendations and analysis
        """
        # Convert American odds to decimal and implied probability
        if odds > 0:
            decimal_odds = (odds / 100) + 1
            implied_probability = 100 / (odds + 100)
        else:
            decimal_odds = (100 / abs(odds)) + 1
            implied_probability = abs(odds) / (abs(odds) + 100)
        
        # Calculate edge
        edge = true_probability - implied_probability
        
        # Kelly formula: f = (bp - q) / b
        # where b = net odds (decimal - 1), p = win probability, q = lose probability
        net_odds = decimal_odds - 1
        lose_probability = 1 - true_probability
        
        if net_odds > 0 and true_probability > implied_probability:
            kelly_fraction = (net_odds * true_probability - lose_probability) / net_odds
        else:
            kelly_fraction = 0
        
        # Apply confidence and multiplier
        kelly_fraction *= confidence * bankroll.kelly_multiplier
        
        # Cap at maximum bet percentage
        kelly_fraction = min(kelly_fraction, bankroll.max_bet_percentage)
        kelly_fraction = max(0, kelly_fraction)  # Never negative
        
        # Calculate bet amounts
        recommended_amount = bankroll.current_balance * Decimal(str(kelly_fraction))
        
        # Risk assessment
        risk_level = KellyCriterionService._assess_risk_level(kelly_fraction)
        
        # Expected value calculation
        expected_value = (true_probability * net_odds - lose_probability) * float(recommended_amount)
        
        return {
            'recommended_amount': recommended_amount,
            'kelly_percentage': kelly_fraction * 100,
            'edge_percentage': edge * 100,
            'risk_level': risk_level,
            'expected_value': Decimal(str(expected_value)),
            'confidence_factor': confidence,
            'true_probability': true_probability,
            'implied_probability': implied_probability,
            'decimal_odds': decimal_odds,
            'bankroll_percentage': kelly_fraction * 100
        }
    
    @staticmethod
    def _assess_risk_level(kelly_fraction: float) -> str:
        """Assess risk level based on Kelly fraction"""
        if kelly_fraction <= 0.01:
            return RiskLevel.VERY_LOW
        elif kelly_fraction <= 0.03:
            return RiskLevel.LOW
        elif kelly_fraction <= 0.06:
            return RiskLevel.MODERATE
        elif kelly_fraction <= 0.10:
            return RiskLevel.HIGH
        elif kelly_fraction <= 0.15:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.EXTREME
    
    @staticmethod
    def calculate_optimal_portfolio_allocation(bankroll: BankrollManagement, 
                                             opportunities: List[Dict]) -> List[Dict]:
        """
        Calculate optimal portfolio allocation across multiple betting opportunities
        using fractional Kelly
        """
        if not opportunities:
            return []
        
        total_kelly = sum(opp.get('kelly_fraction', 0) for opp in opportunities)
        
        # If total Kelly exceeds safe limit, scale down proportionally
        if total_kelly > bankroll.max_bet_percentage:
            scale_factor = bankroll.max_bet_percentage / total_kelly
            for opp in opportunities:
                opp['scaled_kelly'] = opp.get('kelly_fraction', 0) * scale_factor
                opp['recommended_amount'] = bankroll.current_balance * Decimal(str(opp['scaled_kelly']))
        else:
            for opp in opportunities:
                opp['scaled_kelly'] = opp.get('kelly_fraction', 0)
                opp['recommended_amount'] = bankroll.current_balance * Decimal(str(opp['scaled_kelly']))
        
        return sorted(opportunities, key=lambda x: x.get('expected_value', 0), reverse=True)


class ArbitrageDetectionService:
    """Service for detecting arbitrage opportunities"""
    
    @staticmethod
    async def scan_for_arbitrage_opportunities(min_profit_percentage: float = 1.0) -> List[ArbitrageOpportunity]:
        """Scan for arbitrage opportunities across all sportsbooks"""
        opportunities = []
        
        # Get all open markets for games in the next 24 hours
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=24)
        
        markets = await sync_to_async(list)(
            BettingMarket.objects.filter(
                game__scheduled_start__gte=start_time,
                game__scheduled_start__lte=end_time,
                status=MarketStatus.OPEN,
                is_active=True
            ).select_related('game', 'game__home_team', 'game__away_team')
        )
        
        for market in markets:
            market_opportunities = await ArbitrageDetectionService._check_market_arbitrage(
                market, min_profit_percentage
            )
            opportunities.extend(market_opportunities)
        
        # Save discovered opportunities
        saved_opportunities = []
        for opp_data in opportunities:
            opp = ArbitrageOpportunity(**opp_data)
            await sync_to_async(opp.save)()
            saved_opportunities.append(opp)
        
        logger.info(f"Discovered {len(saved_opportunities)} arbitrage opportunities")
        
        return saved_opportunities
    
    @staticmethod
    async def _check_market_arbitrage(market: BettingMarket, min_profit: float) -> List[Dict]:
        """Check a specific market for arbitrage opportunities"""
        opportunities = []
        
        # Get current odds for this market
        current_odds = await sync_to_async(list)(
            OddsLine.objects.filter(
                market=market,
                is_current=True
            ).select_related('sportsbook')
        )
        
        if len(current_odds) < 2:
            return opportunities
        
        if market.market_type == BetType.MONEYLINE:
            # Check moneyline arbitrage
            home_odds = [line for line in current_odds if line.home_odds is not None]
            away_odds = [line for line in current_odds if line.away_odds is not None]
            
            for home_line in home_odds:
                for away_line in away_odds:
                    if home_line.sportsbook_id != away_line.sportsbook_id:
                        arb_calc = ArbitrageDetectionService._calculate_arbitrage(
                            home_line.home_odds, away_line.away_odds
                        )
                        
                        if arb_calc['arbitrage_percentage'] >= min_profit:
                            opportunities.append({
                                'game': market.game,
                                'market_type': market.market_type,
                                'sportsbook_1': home_line.sportsbook,
                                'sportsbook_2': away_line.sportsbook,
                                'odds_1': home_line.home_odds,
                                'odds_2': away_line.away_odds,
                                'selection_1': f"{market.game.home_team.abbreviation} ML",
                                'selection_2': f"{market.game.away_team.abbreviation} ML",
                                'arbitrage_percentage': arb_calc['arbitrage_percentage'],
                                'stake_1_percentage': arb_calc['stake_1_percentage'],
                                'stake_2_percentage': arb_calc['stake_2_percentage'],
                                'minimum_profit': Decimal(str(arb_calc['arbitrage_percentage'])),
                                'expires_at': market.game.scheduled_start,
                                'confidence_score': 0.9,  # High confidence for moneyline arbs
                                'risk_factors': []
                            })
        
        elif market.market_type == BetType.TOTAL:
            # Check over/under arbitrage
            over_odds = [line for line in current_odds if line.over_odds is not None]
            under_odds = [line for line in current_odds if line.under_odds is not None]
            
            for over_line in over_odds:
                for under_line in under_odds:
                    if (over_line.sportsbook_id != under_line.sportsbook_id and
                        over_line.total_line == under_line.total_line):
                        
                        arb_calc = ArbitrageDetectionService._calculate_arbitrage(
                            over_line.over_odds, under_line.under_odds
                        )
                        
                        if arb_calc['arbitrage_percentage'] >= min_profit:
                            opportunities.append({
                                'game': market.game,
                                'market_type': market.market_type,
                                'sportsbook_1': over_line.sportsbook,
                                'sportsbook_2': under_line.sportsbook,
                                'odds_1': over_line.over_odds,
                                'odds_2': under_line.under_odds,
                                'selection_1': f"Over {over_line.total_line}",
                                'selection_2': f"Under {under_line.total_line}",
                                'arbitrage_percentage': arb_calc['arbitrage_percentage'],
                                'stake_1_percentage': arb_calc['stake_1_percentage'],
                                'stake_2_percentage': arb_calc['stake_2_percentage'],
                                'minimum_profit': Decimal(str(arb_calc['arbitrage_percentage'])),
                                'expires_at': market.game.scheduled_start,
                                'confidence_score': 0.85,  # Slightly lower for totals
                                'risk_factors': []
                            })
        
        return opportunities
    
    @staticmethod
    def _calculate_arbitrage(odds_1: int, odds_2: int) -> Dict[str, float]:
        """Calculate arbitrage details for two odds"""
        # Convert to decimal odds
        decimal_1 = OddsLine._american_to_decimal(odds_1)
        decimal_2 = OddsLine._american_to_decimal(odds_2)
        
        # Calculate implied probabilities
        prob_1 = 1 / decimal_1
        prob_2 = 1 / decimal_2
        
        # Check if arbitrage exists
        total_probability = prob_1 + prob_2
        
        if total_probability < 1.0:
            # Arbitrage exists
            arbitrage_percentage = (1 - total_probability) * 100
            
            # Calculate optimal stake percentages
            stake_1_percentage = prob_1 / total_probability * 100
            stake_2_percentage = prob_2 / total_probability * 100
            
            return {
                'arbitrage_percentage': arbitrage_percentage,
                'stake_1_percentage': stake_1_percentage,
                'stake_2_percentage': stake_2_percentage,
                'total_probability': total_probability
            }
        
        return {
            'arbitrage_percentage': 0.0,
            'stake_1_percentage': 0.0,
            'stake_2_percentage': 0.0,
            'total_probability': total_probability
        }


class BettingRecommendationService:
    """Service for generating AI-powered betting recommendations"""
    
    @staticmethod
    async def generate_recommendations_for_user(user, limit: int = 10) -> List[BettingRecommendation]:
        """Generate betting recommendations for a specific user"""
        try:
            # Get user's bankroll
            bankroll = await sync_to_async(
                lambda: BankrollManagement.objects.get(user=user)
            )()
        except BankrollManagement.DoesNotExist:
            # Create default bankroll if doesn't exist
            bankroll = await sync_to_async(BankrollManagement.objects.create)(
                user=user,
                current_balance=Decimal('1000.00'),
                initial_balance=Decimal('1000.00')
            )
        
        # Get upcoming games
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=48)
        
        games = await sync_to_async(list)(
            Game.objects.filter(
                scheduled_start__gte=start_time,
                scheduled_start__lte=end_time,
                status=GameStatus.SCHEDULED,
                is_active=True
            ).select_related('league', 'home_team', 'away_team')[:20]  # Limit games to analyze
        )
        
        recommendations = []
        
        for game in games:
            game_recommendations = await BettingRecommendationService._analyze_game_for_recommendations(
                user, game, bankroll
            )
            recommendations.extend(game_recommendations)
        
        # Sort by expected value and confidence
        recommendations.sort(
            key=lambda x: (x.expected_value * x.confidence_level),
            reverse=True
        )
        
        # Save top recommendations
        saved_recommendations = []
        for rec_data in recommendations[:limit]:
            rec = BettingRecommendation(**rec_data)
            await sync_to_async(rec.save)()
            saved_recommendations.append(rec)
        
        return saved_recommendations
    
    @staticmethod
    async def _analyze_game_for_recommendations(user, game: Game, bankroll: BankrollManagement) -> List[Dict]:
        """Analyze a game for betting opportunities"""
        recommendations = []
        
        # Get markets for this game
        markets = await sync_to_async(list)(
            game.markets.filter(
                status=MarketStatus.OPEN,
                is_active=True
            )
        )
        
        for market in markets:
            market_recs = await BettingRecommendationService._analyze_market(
                user, game, market, bankroll
            )
            recommendations.extend(market_recs)
        
        return recommendations
    
    @staticmethod
    async def _analyze_market(user, game: Game, market: BettingMarket, 
                            bankroll: BankrollManagement) -> List[Dict]:
        """Analyze a specific market for opportunities"""
        recommendations = []
        
        # Get current odds
        current_odds = await sync_to_async(list)(
            market.odds_lines.filter(is_current=True).select_related('sportsbook')
        )
        
        if not current_odds:
            return recommendations
        
        # For this example, we'll use a simple model
        # In production, this would integrate with ML models and advanced analytics
        
        if market.market_type == BetType.MONEYLINE:
            # Analyze moneyline opportunities
            for odds_line in current_odds:
                if odds_line.home_odds and odds_line.away_odds:
                    # Simple model: favor home underdogs and away favorites
                    home_rec = BettingRecommendationService._analyze_moneyline_selection(
                        user, game, market, odds_line, 'home', bankroll
                    )
                    away_rec = BettingRecommendationService._analyze_moneyline_selection(
                        user, game, market, odds_line, 'away', bankroll
                    )
                    
                    if home_rec:
                        recommendations.append(home_rec)
                    if away_rec:
                        recommendations.append(away_rec)
        
        return recommendations
    
    @staticmethod
    def _analyze_moneyline_selection(user, game: Game, market: BettingMarket,
                                   odds_line: OddsLine, selection: str,
                                   bankroll: BankrollManagement) -> Optional[Dict]:
        """Analyze a moneyline selection"""
        if selection == 'home':
            odds = odds_line.home_odds
            team = game.home_team
            selection_name = f"{team.city} {team.name} ML"
        else:
            odds = odds_line.away_odds
            team = game.away_team
            selection_name = f"{team.city} {team.name} ML"
        
        if not odds:
            return None
        
        # Calculate implied probability
        implied_prob = OddsLine._american_to_probability(odds)
        
        # Simple model: estimate true probability based on team performance
        # In production, this would use sophisticated ML models
        team_strength = BettingRecommendationService._estimate_team_strength(team)
        opponent = game.away_team if selection == 'home' else game.home_team
        opponent_strength = BettingRecommendationService._estimate_team_strength(opponent)
        
        # Home field advantage
        if selection == 'home':
            team_strength += 0.03  # 3% home field advantage
        
        # Estimate true probability
        true_prob = team_strength / (team_strength + opponent_strength)
        
        # Check for edge
        edge = true_prob - implied_prob
        
        if edge > 0.02:  # Minimum 2% edge
            # Calculate Kelly bet size
            kelly_calc = KellyCriterionService.calculate_kelly_bet_size(
                bankroll, true_prob, odds, confidence=0.7  # Moderate confidence
            )
            
            if kelly_calc['recommended_amount'] > Decimal('5.00'):  # Minimum $5 bet
                return {
                    'user': user,
                    'game': game,
                    'market': market,
                    'recommended_selection': selection_name,
                    'recommended_sportsbook': odds_line.sportsbook,
                    'recommended_odds': odds,
                    'recommended_stake': kelly_calc['recommended_amount'],
                    'expected_value': kelly_calc['expected_value'],
                    'win_probability': true_prob,
                    'confidence_level': 0.7,
                    'edge_percentage': edge * 100,
                    'risk_level': kelly_calc['risk_level'],
                    'kelly_percentage': kelly_calc['kelly_percentage'],
                    'generating_agent': 'simple-moneyline-analyzer',
                    'analysis_factors': {
                        'implied_probability': implied_prob,
                        'true_probability': true_prob,
                        'edge': edge,
                        'team_strength': team_strength,
                        'opponent_strength': opponent_strength
                    },
                    'reasoning': f"Model estimates {selection_name} has {true_prob:.1%} chance to win vs {implied_prob:.1%} implied probability, creating {edge:.1%} edge.",
                    'model_predictions': {
                        'win_probability': true_prob,
                        'model_confidence': 0.7
                    },
                    'historical_performance': {},
                    'expires_at': game.scheduled_start,
                    'is_active': True
                }
        
        return None
    
    @staticmethod
    def _estimate_team_strength(team: Team) -> float:
        """Estimate team strength (simple model)"""
        # In production, this would use sophisticated metrics
        record = team.current_record
        wins = record.get('wins', 0)
        losses = record.get('losses', 0)
        
        if wins + losses == 0:
            return 0.5  # Default 50%
        
        win_rate = wins / (wins + losses)
        
        # Adjust for strength of schedule, recent performance, etc.
        # For now, just use win rate with some regression to mean
        return 0.3 + (win_rate * 0.4)


class SportsAnalyticsService:
    """Service for generating comprehensive sports analytics"""
    
    @staticmethod
    async def generate_game_analytics(game: Game) -> SportsAnalytics:
        """Generate analytics for a specific game"""
        start_time = timezone.now()
        
        # Collect various analytics
        metrics = await SportsAnalyticsService._calculate_game_metrics(game)
        trends = await SportsAnalyticsService._calculate_game_trends(game)
        predictions = await SportsAnalyticsService._generate_game_predictions(game)
        comparative = await SportsAnalyticsService._generate_comparative_analysis(game)
        
        end_time = timezone.now()
        computation_time = (end_time - start_time).total_seconds()
        
        # Create analytics record
        analytics = SportsAnalytics(
            scope_type='game',
            scope_id=str(game.id),
            analysis_period='game',
            period_start=game.scheduled_start,
            period_end=game.scheduled_start + timedelta(hours=4),  # Estimate game duration
            metrics=metrics,
            trends=trends,
            predictions=predictions,
            comparative_analysis=comparative,
            generated_by='sports-analytics-service',
            computation_time_seconds=computation_time,
            data_quality_score=1.0
        )
        
        await sync_to_async(analytics.save)()
        return analytics
    
    @staticmethod
    async def _calculate_game_metrics(game: Game) -> Dict:
        """Calculate various metrics for a game"""
        metrics = {}
        
        # Betting market metrics
        markets_count = await sync_to_async(game.markets.count)()
        total_handle = await sync_to_async(
            lambda: game.markets.aggregate(Sum('total_volume'))['total_volume__sum'] or 0
        )()
        
        # Line movement metrics
        movements = await sync_to_async(list)(
            LineMovement.objects.filter(
                market__game=game,
                is_significant=True
            )
        )
        
        metrics.update({
            'markets_count': markets_count,
            'total_handle': float(total_handle),
            'significant_movements': len(movements),
            'home_team_record': game.home_team.current_record,
            'away_team_record': game.away_team.current_record,
            'home_ats_record': game.home_team.ats_record,
            'away_ats_record': game.away_team.ats_record
        })
        
        return metrics
    
    @staticmethod
    async def _calculate_game_trends(game: Game) -> Dict:
        """Calculate trends for teams in this game"""
        # Get recent games for both teams
        home_recent = await sync_to_async(list)(
            Game.objects.filter(
                Q(home_team=game.home_team) | Q(away_team=game.home_team),
                scheduled_start__lt=game.scheduled_start,
                status=GameStatus.FINAL
            ).order_by('-scheduled_start')[:10]
        )
        
        away_recent = await sync_to_async(list)(
            Game.objects.filter(
                Q(home_team=game.away_team) | Q(away_team=game.away_team),
                scheduled_start__lt=game.scheduled_start,
                status=GameStatus.FINAL
            ).order_by('-scheduled_start')[:10]
        )
        
        trends = {
            'home_team_form': SportsAnalyticsService._analyze_team_form(game.home_team, home_recent),
            'away_team_form': SportsAnalyticsService._analyze_team_form(game.away_team, away_recent),
            'head_to_head': await SportsAnalyticsService._analyze_head_to_head(game.home_team, game.away_team)
        }
        
        return trends
    
    @staticmethod
    def _analyze_team_form(team: Team, recent_games: List[Game]) -> Dict:
        """Analyze recent form for a team"""
        if not recent_games:
            return {'games_analyzed': 0}
        
        wins = 0
        total_score = 0
        total_allowed = 0
        
        for game in recent_games:
            if game.home_team == team:
                team_score = game.home_score or 0
                opponent_score = game.away_score or 0
            else:
                team_score = game.away_score or 0
                opponent_score = game.home_score or 0
            
            if team_score > opponent_score:
                wins += 1
            
            total_score += team_score
            total_allowed += opponent_score
        
        games_count = len(recent_games)
        
        return {
            'games_analyzed': games_count,
            'wins': wins,
            'losses': games_count - wins,
            'win_rate': wins / games_count if games_count > 0 else 0,
            'avg_points_scored': total_score / games_count if games_count > 0 else 0,
            'avg_points_allowed': total_allowed / games_count if games_count > 0 else 0
        }
    
    @staticmethod
    async def _analyze_head_to_head(team1: Team, team2: Team) -> Dict:
        """Analyze head-to-head matchups between teams"""
        h2h_games = await sync_to_async(list)(
            Game.objects.filter(
                Q(home_team=team1, away_team=team2) | Q(home_team=team2, away_team=team1),
                status=GameStatus.FINAL
            ).order_by('-scheduled_start')[:5]  # Last 5 meetings
        )
        
        if not h2h_games:
            return {'games_found': 0}
        
        team1_wins = 0
        total_games = len(h2h_games)
        
        for game in h2h_games:
            if game.home_team == team1:
                if (game.home_score or 0) > (game.away_score or 0):
                    team1_wins += 1
            else:
                if (game.away_score or 0) > (game.home_score or 0):
                    team1_wins += 1
        
        return {
            'games_found': total_games,
            'team1_wins': team1_wins,
            'team2_wins': total_games - team1_wins,
            'team1_win_rate': team1_wins / total_games if total_games > 0 else 0
        }
    
    @staticmethod
    async def _generate_game_predictions(game: Game) -> Dict:
        """Generate predictions for the game"""
        # Simple prediction model - in production would use ML
        home_strength = BettingRecommendationService._estimate_team_strength(game.home_team)
        away_strength = BettingRecommendationService._estimate_team_strength(game.away_team)
        
        # Home field advantage
        home_strength += 0.03
        
        # Predict win probabilities
        total_strength = home_strength + away_strength
        home_win_prob = home_strength / total_strength
        away_win_prob = away_strength / total_strength
        
        predictions = {
            'home_win_probability': home_win_prob,
            'away_win_probability': away_win_prob,
            'predicted_total_score': 45.0,  # Simple placeholder
            'confidence': 0.6,
            'model_used': 'simple-strength-model'
        }
        
        return predictions
    
    @staticmethod
    async def _generate_comparative_analysis(game: Game) -> Dict:
        """Generate comparative analysis"""
        return {
            'league_average_total': 44.5,  # Placeholder
            'teams_vs_league_avg': {
                'home_team_vs_avg': 'above',
                'away_team_vs_avg': 'below'
            },
            'historical_matchup_average': 42.0
        }