"""
Market Data Service
===================

Session 462: Real market data integration for Market Intelligence Desk.

Provides enriched market data for Bull/Bear agents:
- Real-time prices from Yahoo Finance
- Price change analysis (% moves, volatility)
- Volume analysis (unusual activity detection)
- Sector/industry context
- Technical indicators (momentum, trends)

This service transforms raw market data into intelligence that
Bull and Bear agents can debate about.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for fetching and enriching market data for intelligent analysis.

    Uses Yahoo Finance spider for real-time data, then enriches with:
    - Unusual activity detection
    - Momentum indicators
    - Sector trends
    - Volume spikes
    """

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    def get_market_snapshot(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive market snapshot for specified symbols.

        Args:
            symbols: List of ticker symbols (default: watchlist)

        Returns:
            Dict with market data, unusual activity, sector trends
        """
        try:
            # Fetch real-time data from Yahoo Finance spider
            raw_data = self._fetch_from_yahoo_finance(symbols)

            # Enrich with analysis
            enriched = self._enrich_market_data(raw_data)

            # Detect unusual activity
            unusual_activity = self._detect_unusual_activity(enriched)

            # Analyze sector trends
            sector_trends = self._analyze_sector_trends(enriched)

            # Calculate market sentiment
            market_sentiment = self._calculate_market_sentiment(enriched)

            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'stocks': enriched,
                'unusual_activity': unusual_activity,
                'sector_trends': sector_trends,
                'market_sentiment': market_sentiment,
                'total_stocks': len(enriched),
            }

            logger.info(f"📊 Market snapshot generated: {len(enriched)} stocks, "
                       f"{len(unusual_activity)} unusual activity alerts")

            return snapshot

        except Exception as e:
            logger.error(f"Market snapshot error: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'stocks': [],
                'error': str(e)
            }

    def get_stock_details(self, symbol: str) -> Dict[str, Any]:
        """
        Get detailed analysis for a single stock.

        Args:
            symbol: Ticker symbol

        Returns:
            Dict with comprehensive stock analysis
        """
        try:
            raw_data = self._fetch_from_yahoo_finance([symbol])
            if not raw_data:
                return {'symbol': symbol, 'error': 'No data available'}

            stock_data = raw_data[0]
            enriched = self._enrich_single_stock(stock_data)

            logger.info(f"📈 Stock details fetched for {symbol}")
            return enriched

        except Exception as e:
            logger.error(f"Stock details error for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def _fetch_from_yahoo_finance(self, symbols: List[str] = None) -> List[Dict]:
        """Fetch real-time data from Yahoo Finance spider."""
        try:
            from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider

            spider = YahooFinanceSpider()

            # Use provided symbols or default watchlist
            if symbols:
                data = spider.fetch_data(max_results=len(symbols), symbols=symbols)
            else:
                # Default to major stocks + indices
                data = spider.fetch_data(max_results=20)

            return data

        except Exception as e:
            logger.error(f"Yahoo Finance fetch error: {e}")
            return []

    def _enrich_market_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Enrich raw market data with additional analysis."""
        enriched = []

        for stock in raw_data:
            enriched_stock = self._enrich_single_stock(stock)
            enriched.append(enriched_stock)

        return enriched

    def _enrich_single_stock(self, stock: Dict) -> Dict:
        """Add enrichment analysis to a single stock."""
        symbol = stock.get('symbol', 'UNKNOWN')
        price = stock.get('current_price', 0)
        change_pct = stock.get('change_percent', 0)
        volume = stock.get('volume', 0)

        # Calculate momentum
        momentum = self._calculate_momentum(change_pct)

        # Detect volatility
        volatility = self._detect_volatility(change_pct, stock)

        # Volume analysis
        volume_analysis = self._analyze_volume(volume, stock)

        # Price position (vs 52-week range)
        price_position = self._calculate_price_position(stock)

        # Enriched stock data
        enriched = {
            **stock,  # All original data
            'analysis': {
                'momentum': momentum,
                'volatility': volatility,
                'volume_analysis': volume_analysis,
                'price_position': price_position,
                'trading_signal': self._generate_trading_signal(momentum, volatility, volume_analysis),
            },
            'enriched_at': datetime.now().isoformat(),
        }

        return enriched

    def _calculate_momentum(self, change_pct: float) -> str:
        """Calculate momentum category."""
        if change_pct > 5:
            return 'STRONG_BULLISH'
        elif change_pct > 2:
            return 'BULLISH'
        elif change_pct > 0:
            return 'SLIGHTLY_BULLISH'
        elif change_pct > -2:
            return 'SLIGHTLY_BEARISH'
        elif change_pct > -5:
            return 'BEARISH'
        else:
            return 'STRONG_BEARISH'

    def _detect_volatility(self, change_pct: float, stock: Dict) -> str:
        """Detect volatility level."""
        abs_change = abs(change_pct)

        if abs_change > 10:
            return 'EXTREME'
        elif abs_change > 5:
            return 'HIGH'
        elif abs_change > 2:
            return 'MODERATE'
        else:
            return 'LOW'

    def _analyze_volume(self, volume: int, stock: Dict) -> Dict:
        """Analyze volume for unusual activity."""
        # In production, would compare to average volume
        # For now, use simple thresholds

        if not volume:
            return {'level': 'NO_DATA', 'unusual': False}

        # Simplified volume analysis
        if volume > 100_000_000:
            level = 'VERY_HIGH'
            unusual = True
        elif volume > 50_000_000:
            level = 'HIGH'
            unusual = True
        elif volume > 10_000_000:
            level = 'NORMAL'
            unusual = False
        else:
            level = 'LOW'
            unusual = False

        return {
            'level': level,
            'volume': volume,
            'unusual': unusual,
        }

    def _calculate_price_position(self, stock: Dict) -> Dict:
        """Calculate price position within 52-week range."""
        price = stock.get('current_price', 0)
        high_52w = stock.get('fifty_two_week_high', price)
        low_52w = stock.get('fifty_two_week_low', price)

        if not price or not high_52w or not low_52w:
            return {'position_pct': None, 'near_high': False, 'near_low': False}

        # Calculate % position in range
        range_size = high_52w - low_52w
        if range_size == 0:
            position_pct = 50.0
        else:
            position_pct = ((price - low_52w) / range_size) * 100

        # Near 52-week high/low?
        near_high = position_pct > 90
        near_low = position_pct < 10

        return {
            'position_pct': round(position_pct, 1),
            'near_high': near_high,
            'near_low': near_low,
            'fifty_two_week_high': high_52w,
            'fifty_two_week_low': low_52w,
        }

    def _generate_trading_signal(self, momentum: str, volatility: str, volume_analysis: Dict) -> str:
        """Generate simple trading signal."""
        unusual_volume = volume_analysis.get('unusual', False)

        # Strong momentum + unusual volume = strong signal
        if momentum == 'STRONG_BULLISH' and unusual_volume:
            return 'STRONG_BUY'
        elif momentum == 'BULLISH':
            return 'BUY'
        elif momentum == 'STRONG_BEARISH' and unusual_volume:
            return 'STRONG_SELL'
        elif momentum == 'BEARISH':
            return 'SELL'
        else:
            return 'HOLD'

    def _detect_unusual_activity(self, enriched_stocks: List[Dict]) -> List[Dict]:
        """Detect stocks with unusual activity."""
        unusual = []

        for stock in enriched_stocks:
            analysis = stock.get('analysis', {})
            symbol = stock.get('symbol', 'UNKNOWN')
            change_pct = stock.get('change_percent', 0)

            # Criteria for unusual activity
            is_unusual = (
                analysis.get('volume_analysis', {}).get('unusual', False) or
                analysis.get('volatility') in ['HIGH', 'EXTREME'] or
                abs(change_pct) > 5 or
                analysis.get('price_position', {}).get('near_high', False) or
                analysis.get('price_position', {}).get('near_low', False)
            )

            if is_unusual:
                unusual.append({
                    'symbol': symbol,
                    'name': stock.get('name', symbol),
                    'change_percent': change_pct,
                    'price': stock.get('current_price', 0),
                    'volume': stock.get('volume', 0),
                    'momentum': analysis.get('momentum'),
                    'volatility': analysis.get('volatility'),
                    'trading_signal': analysis.get('trading_signal'),
                    'reasons': self._get_unusual_reasons(stock, analysis),
                })

        # Sort by absolute price change
        unusual.sort(key=lambda x: abs(x.get('change_percent', 0)), reverse=True)

        return unusual

    def _get_unusual_reasons(self, stock: Dict, analysis: Dict) -> List[str]:
        """Get reasons why this stock has unusual activity."""
        reasons = []

        change_pct = stock.get('change_percent', 0)
        if abs(change_pct) > 10:
            reasons.append(f"Extreme price move: {change_pct:+.2f}%")
        elif abs(change_pct) > 5:
            reasons.append(f"Large price move: {change_pct:+.2f}%")

        volume_analysis = analysis.get('volume_analysis', {})
        if volume_analysis.get('unusual'):
            reasons.append(f"High volume: {volume_analysis.get('level')}")

        volatility = analysis.get('volatility')
        if volatility in ['HIGH', 'EXTREME']:
            reasons.append(f"{volatility.lower()} volatility")

        price_pos = analysis.get('price_position', {})
        if price_pos.get('near_high'):
            reasons.append("Near 52-week high")
        elif price_pos.get('near_low'):
            reasons.append("Near 52-week low")

        return reasons

    def _analyze_sector_trends(self, enriched_stocks: List[Dict]) -> Dict[str, Any]:
        """Analyze trends by sector."""
        sector_data = {}

        for stock in enriched_stocks:
            sector = stock.get('sector', 'N/A')
            if sector == 'N/A':
                continue

            if sector not in sector_data:
                sector_data[sector] = {
                    'count': 0,
                    'avg_change': 0,
                    'total_change': 0,
                    'gainers': 0,
                    'losers': 0,
                }

            change_pct = stock.get('change_percent', 0)
            sector_data[sector]['count'] += 1
            sector_data[sector]['total_change'] += change_pct

            if change_pct > 0:
                sector_data[sector]['gainers'] += 1
            elif change_pct < 0:
                sector_data[sector]['losers'] += 1

        # Calculate averages
        for sector, data in sector_data.items():
            if data['count'] > 0:
                data['avg_change'] = round(data['total_change'] / data['count'], 2)

        # Sort by average change
        sorted_sectors = sorted(
            sector_data.items(),
            key=lambda x: x[1]['avg_change'],
            reverse=True
        )

        return {
            'sectors': dict(sorted_sectors),
            'best_performing': sorted_sectors[0][0] if sorted_sectors else None,
            'worst_performing': sorted_sectors[-1][0] if sorted_sectors else None,
        }

    def _calculate_market_sentiment(self, enriched_stocks: List[Dict]) -> Dict[str, Any]:
        """Calculate overall market sentiment."""
        if not enriched_stocks:
            return {'sentiment': 'UNKNOWN', 'score': 0}

        total_change = sum(s.get('change_percent', 0) for s in enriched_stocks)
        avg_change = total_change / len(enriched_stocks)

        gainers = sum(1 for s in enriched_stocks if s.get('change_percent', 0) > 0)
        losers = sum(1 for s in enriched_stocks if s.get('change_percent', 0) < 0)

        # Sentiment score (-100 to +100)
        sentiment_score = round(avg_change * 10, 1)

        # Sentiment category
        if avg_change > 2:
            sentiment = 'VERY_BULLISH'
        elif avg_change > 0.5:
            sentiment = 'BULLISH'
        elif avg_change > -0.5:
            sentiment = 'NEUTRAL'
        elif avg_change > -2:
            sentiment = 'BEARISH'
        else:
            sentiment = 'VERY_BEARISH'

        return {
            'sentiment': sentiment,
            'score': sentiment_score,
            'avg_change': round(avg_change, 2),
            'gainers': gainers,
            'losers': losers,
            'unchanged': len(enriched_stocks) - gainers - losers,
        }


# Global instance
_market_data_service = None


def get_market_data_service() -> MarketDataService:
    """Get or create the global MarketDataService instance."""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service
