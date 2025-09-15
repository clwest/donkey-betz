"""
Market Data Spider - Real-Time Market Intelligence
=================================================

Specialized spider for gathering real-time market data, trading signals,
and market microstructure intelligence for trading agents and advisors.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class MarketDataSpider(BaseIntelligenceSpider):
    """Real-time market data and trading intelligence spider"""

    def __init__(self, spider_id: str, targets: List[SpiderTarget], subscribers: List[str], redis_config: Dict[str, Any]):
        super().__init__(spider_id, targets, subscribers, redis_config)

        self.major_indices = ['SPY', 'QQQ', 'IWM', 'VIX']
        self.crypto_pairs = ['BTC-USD', 'ETH-USD', 'BNB-USD']
        self.forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY']

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process market data"""
        try:
            if any(exchange in target.url for exchange in ['binance', 'coinbase']):
                return await self._process_crypto_market_data(raw_data, target)
            elif 'polygon.io' in target.url:
                return await self._process_polygon_data(raw_data, target)
            else:
                return await self._process_general_market_data(raw_data, target)
        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
            return None

    async def _process_crypto_market_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process cryptocurrency market data"""
        try:
            market_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data_type': 'crypto_market',
                'symbols': {},
                'market_metrics': {},
                'trading_signals': []
            }

            # Process different crypto data formats
            if 'symbol' in data and 'price' in data:
                # Single symbol data
                symbol = data['symbol']
                market_data['symbols'][symbol] = self._process_crypto_ticker(data)
            elif isinstance(data, list):
                # Multiple symbols
                for item in data:
                    if 'symbol' in item:
                        market_data['symbols'][item['symbol']] = self._process_crypto_ticker(item)
            elif 'data' in data:
                # API wrapper format
                if isinstance(data['data'], list):
                    for item in data['data']:
                        if 'symbol' in item:
                            market_data['symbols'][item['symbol']] = self._process_crypto_ticker(item)

            # Calculate market metrics
            market_data['market_metrics'] = self._calculate_crypto_market_metrics(market_data['symbols'])

            # Generate trading signals
            market_data['trading_signals'] = self._generate_crypto_signals(market_data['symbols'])

            quality_score = self._calculate_market_data_quality(market_data)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="crypto_market_data",
                content=market_data,
                metadata={
                    'symbols_count': len(market_data['symbols']),
                    'signals_count': len(market_data['trading_signals']),
                    'data_source': 'crypto_exchange'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['crypto', 'market_data', 'trading', 'real_time'],
                target_agents=['crypto_trading_agent', 'arbitrage_agent'],
                target_advisors=['crypto_expert', 'options_master']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing crypto market data: {e}")
            return None

    def _process_crypto_ticker(self, ticker_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual crypto ticker data"""
        processed = {
            'symbol': ticker_data.get('symbol'),
            'price': float(ticker_data.get('price', 0)),
            'volume': float(ticker_data.get('volume', 0)),
            'change_24h': float(ticker_data.get('priceChangePercent', 0)),
            'high_24h': float(ticker_data.get('highPrice', 0)),
            'low_24h': float(ticker_data.get('lowPrice', 0)),
            'open_price': float(ticker_data.get('openPrice', 0)),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        # Calculate additional metrics
        if processed['price'] > 0 and processed['open_price'] > 0:
            processed['intraday_change'] = ((processed['price'] - processed['open_price']) / processed['open_price']) * 100

        if processed['high_24h'] > 0 and processed['low_24h'] > 0:
            processed['daily_range'] = ((processed['high_24h'] - processed['low_24h']) / processed['low_24h']) * 100

        return processed

    def _calculate_crypto_market_metrics(self, symbols_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall crypto market metrics"""
        metrics = {
            'total_volume': 0.0,
            'avg_change_24h': 0.0,
            'positive_movers': 0,
            'negative_movers': 0,
            'high_volume_symbols': [],
            'volatility_index': 0.0
        }

        if not symbols_data:
            return metrics

        changes = []
        volumes = []
        volatilities = []

        for symbol, data in symbols_data.items():
            volume = data.get('volume', 0)
            change = data.get('change_24h', 0)
            daily_range = data.get('daily_range', 0)

            volumes.append(volume)
            changes.append(change)
            volatilities.append(daily_range)

            if change > 0:
                metrics['positive_movers'] += 1
            elif change < 0:
                metrics['negative_movers'] += 1

        # Calculate aggregated metrics
        metrics['total_volume'] = sum(volumes)
        metrics['avg_change_24h'] = sum(changes) / len(changes) if changes else 0
        metrics['volatility_index'] = sum(volatilities) / len(volatilities) if volatilities else 0

        # Identify high volume symbols
        if volumes:
            avg_volume = sum(volumes) / len(volumes)
            metrics['high_volume_symbols'] = [
                symbol for symbol, data in symbols_data.items()
                if data.get('volume', 0) > avg_volume * 2
            ]

        return metrics

    def _generate_crypto_signals(self, symbols_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals based on crypto data"""
        signals = []

        for symbol, data in symbols_data.items():
            price = data.get('price', 0)
            change_24h = data.get('change_24h', 0)
            volume = data.get('volume', 0)
            daily_range = data.get('daily_range', 0)

            # Volume spike signal
            if volume > 0:  # Would need historical data for proper volume analysis
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'volume_analysis',
                    'signal': 'monitor',
                    'strength': 0.5,
                    'reason': f'Current volume: {volume:,.0f}'
                })

            # Momentum signal
            if abs(change_24h) > 5:  # Significant 24h change
                signal_direction = 'bullish' if change_24h > 0 else 'bearish'
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'momentum',
                    'signal': signal_direction,
                    'strength': min(1.0, abs(change_24h) / 20),  # Normalize to 0-1
                    'reason': f'24h change: {change_24h:.2f}%'
                })

            # Volatility signal
            if daily_range > 10:  # High volatility
                signals.append({
                    'symbol': symbol,
                    'signal_type': 'volatility',
                    'signal': 'high_volatility',
                    'strength': min(1.0, daily_range / 50),
                    'reason': f'Daily range: {daily_range:.2f}%'
                })

        return signals

    async def _process_polygon_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process Polygon.io market data"""
        try:
            market_data = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data_type': 'equity_market',
                'tickers': {},
                'market_summary': {},
                'technical_indicators': {}
            }

            # Process Polygon API response
            if 'results' in data:
                for result in data['results']:
                    ticker = result.get('T', 'UNKNOWN')
                    market_data['tickers'][ticker] = {
                        'symbol': ticker,
                        'close': result.get('c'),
                        'high': result.get('h'),
                        'low': result.get('l'),
                        'open': result.get('o'),
                        'volume': result.get('v'),
                        'vwap': result.get('vw'),
                        'timestamp': result.get('t'),
                        'num_transactions': result.get('n')
                    }

            # Calculate market summary
            market_data['market_summary'] = self._calculate_market_summary(market_data['tickers'])

            # Calculate technical indicators
            market_data['technical_indicators'] = self._calculate_technical_indicators(market_data['tickers'])

            quality_score = self._calculate_market_data_quality(market_data)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="equity_market_data",
                content=market_data,
                metadata={
                    'tickers_count': len(market_data['tickers']),
                    'data_source': 'polygon_io'
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['equity', 'market_data', 'real_time', 'technical'],
                target_agents=['equity_trading_agent', 'technical_analysis_agent'],
                target_advisors=['options_master', 'ray_dalio']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing Polygon data: {e}")
            return None

    def _calculate_market_summary(self, tickers: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate market summary from ticker data"""
        summary = {
            'total_volume': 0,
            'avg_price_change': 0.0,
            'advance_decline_ratio': 0.0,
            'high_volume_tickers': [],
            'price_leaders': {'gainers': [], 'losers': []}
        }

        if not tickers:
            return summary

        price_changes = []
        volumes = []
        positive_moves = 0
        total_moves = 0

        for symbol, data in tickers.items():
            open_price = data.get('open', 0)
            close_price = data.get('close', 0)
            volume = data.get('volume', 0)

            if open_price and close_price:
                change = ((close_price - open_price) / open_price) * 100
                price_changes.append(change)

                if change > 0:
                    positive_moves += 1
                total_moves += 1

                # Track gainers and losers
                if change > 2:  # Significant gainer
                    summary['price_leaders']['gainers'].append({
                        'symbol': symbol,
                        'change': change,
                        'price': close_price
                    })
                elif change < -2:  # Significant loser
                    summary['price_leaders']['losers'].append({
                        'symbol': symbol,
                        'change': change,
                        'price': close_price
                    })

            if volume:
                volumes.append(volume)
                summary['total_volume'] += volume

        # Calculate summary metrics
        if price_changes:
            summary['avg_price_change'] = sum(price_changes) / len(price_changes)

        if total_moves > 0:
            summary['advance_decline_ratio'] = positive_moves / total_moves

        # Sort price leaders
        summary['price_leaders']['gainers'] = sorted(
            summary['price_leaders']['gainers'],
            key=lambda x: x['change'],
            reverse=True
        )[:5]

        summary['price_leaders']['losers'] = sorted(
            summary['price_leaders']['losers'],
            key=lambda x: x['change']
        )[:5]

        return summary

    def _calculate_technical_indicators(self, tickers: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate technical indicators (simplified)"""
        indicators = {
            'market_breadth': 0.0,
            'volatility_index': 0.0,
            'momentum_score': 0.0,
            'volume_profile': {}
        }

        if not tickers:
            return indicators

        # Market breadth (% of stocks advancing)
        advancing = sum(1 for data in tickers.values()
                       if data.get('close', 0) > data.get('open', 0))
        total_stocks = len(tickers)
        indicators['market_breadth'] = (advancing / total_stocks) * 100 if total_stocks > 0 else 0

        # Average volatility
        volatilities = []
        for data in tickers.values():
            high = data.get('high', 0)
            low = data.get('low', 0)
            close = data.get('close', 0)
            if high and low and close:
                true_range = (high - low) / close * 100
                volatilities.append(true_range)

        indicators['volatility_index'] = sum(volatilities) / len(volatilities) if volatilities else 0

        # Volume profile
        volume_ranges = {'low': 0, 'medium': 0, 'high': 0}
        volumes = [data.get('volume', 0) for data in tickers.values() if data.get('volume')]

        if volumes:
            q33 = np.percentile(volumes, 33)
            q66 = np.percentile(volumes, 66)

            for volume in volumes:
                if volume <= q33:
                    volume_ranges['low'] += 1
                elif volume <= q66:
                    volume_ranges['medium'] += 1
                else:
                    volume_ranges['high'] += 1

        indicators['volume_profile'] = volume_ranges

        return indicators

    async def _process_general_market_data(self, data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process general market data"""
        try:
            market_data = data.copy() if isinstance(data, dict) else {'raw_data': data}
            market_data['timestamp'] = datetime.now(timezone.utc).isoformat()

            quality_score = self.calculate_data_quality(market_data)

            intelligence = IntelligenceData(
                spider_id=self.spider_id,
                source_url=target.url,
                data_type="general_market_data",
                content=market_data,
                metadata={'data_source': 'general_market'},
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['market_data', 'general'],
                target_agents=['market_analysis_agent'],
                target_advisors=['financial_strategist']
            )

            return intelligence

        except Exception as e:
            self.logger.error(f"Error processing general market data: {e}")
            return None

    def _calculate_market_data_quality(self, market_data: Dict[str, Any]) -> float:
        """Calculate quality score for market data"""
        score = 0.0

        # Data completeness
        if 'symbols' in market_data or 'tickers' in market_data:
            data_count = len(market_data.get('symbols', market_data.get('tickers', {})))
            score += min(0.4, data_count / 10)  # Up to 10 symbols = full score

        # Metrics calculated
        if 'market_metrics' in market_data or 'market_summary' in market_data:
            score += 0.3

        # Signals or indicators
        if 'trading_signals' in market_data or 'technical_indicators' in market_data:
            score += 0.3

        return score

    def get_required_fields(self) -> List[str]:
        return ['symbol', 'price', 'timestamp']

    def get_timestamp_field(self) -> Optional[str]:
        return 'timestamp'

    def get_relevance_keywords(self) -> List[str]:
        return ['market', 'trading', 'price', 'volume', 'crypto', 'equity']

    def validate_data_accuracy(self, data: Dict[str, Any]) -> bool:
        try:
            # Check price values
            if 'price' in data:
                price = float(data['price'])
                if price <= 0:
                    return False

            # Check volume values
            if 'volume' in data:
                volume = float(data['volume'])
                if volume < 0:
                    return False

            # Check percentage changes
            for field in ['change_24h', 'intraday_change']:
                if field in data:
                    change = float(data[field])
                    if abs(change) > 1000:  # Unreasonable change
                        return False

            return True
        except (ValueError, TypeError):
            return False