"""
Market Movement Monitor Agent
=============================

Session 461: Watches for unusual price/volume movements.
Equivalent to TransactionMonitorAgent in the blockchain audit system.

Key capabilities:
- Volume spike detection
- Momentum tracking
- Breakout alerts
- After-hours activity monitoring
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_movement_with_ml(movement_data: dict) -> dict:
    """Analyze market movements using ML models (LSTM + Anomaly)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=movement_data,
            task_hint=TaskType.ANOMALY,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'anomaly'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'movement_anomalies': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML movement analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class MarketMovementMonitorAgent(BaseAgent):
    """
    Monitors markets for unusual price and volume movements.

    Tools:
    - detect_volume_spike: Find unusual volume activity
    - track_momentum: Monitor price momentum
    - alert_breakout: Detect technical breakouts
    - scan_after_hours: Monitor pre/post market activity
    """

    name = "MarketMovementMonitorAgent"

    system_prompt = """You are a market movement specialist monitoring for:
1. Unusual volume spikes (>2x average volume)
2. Significant price movements (>5% daily change)
3. Technical breakouts from key levels
4. After-hours and pre-market activity
5. Gap ups/downs at market open

Alert criteria:
- CRITICAL: Circuit breaker triggered, >20% move, trading halted
- HIGH: >10% move on high volume, major gap
- MEDIUM: >5% move, volume 2-3x average
- LOW: Notable but within normal ranges

Focus on stocks without corresponding news explanations for moves."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "detect_volume_spike",
                "description": "Detect unusual volume activity for a stock or market",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker (or 'market' for broad scan)"},
                        "threshold_multiplier": {"type": "number", "description": "Volume threshold vs average (default 2.0)"},
                        "timeframe": {"type": "string", "description": "Timeframe to analyze (1d, 1h, 5m)"}
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "track_momentum",
                "description": "Track price momentum and trend strength",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Technical indicators (RSI, MACD, moving averages)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "alert_breakout",
                "description": "Detect technical breakouts from key levels",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "level_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Level types (resistance, support, 52w high/low)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "scan_after_hours",
                "description": "Monitor pre-market and after-hours activity",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_volume": {"type": "integer", "description": "Minimum volume threshold"},
                        "min_change_pct": {"type": "number", "description": "Minimum % change to alert"}
                    }
                }
            }
        }
    ]

    # Thresholds for alerts
    VOLUME_SPIKE_THRESHOLD = 2.0  # 2x average volume
    PRICE_CHANGE_CRITICAL = 0.20  # 20%
    PRICE_CHANGE_HIGH = 0.10  # 10%
    PRICE_CHANGE_MEDIUM = 0.05  # 5%

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute market movement monitoring.

        Args:
            task: Monitoring task description
            context: Additional context
            scifi_context: Sci-fi features context
            spider_context: Spider data context

        Returns:
            AgentResult with movement findings
        """
        start_time = datetime.now()
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        logger.info(f"MarketMovementMonitorAgent executing: {task[:100]}...")

        try:
            # Get market data from spiders
            market_data = self._get_market_data(context.get('ticker'))

            # Analyze movements
            movements = self._analyze_movements(market_data)

            # Generate alerts
            alerts = self._generate_alerts(movements)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return AgentResult(
                success=True,
                message=f"Market movement scan complete. Found {len(alerts)} alerts.",
                data={
                    'movements': movements,
                    'alerts': alerts,
                    'alert_count': len(alerts),
                    'high_severity_count': len([a for a in alerts if a['severity'] in ['CRITICAL', 'HIGH']]),
                },
                agent_name=self.name,
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"MarketMovementMonitorAgent error: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name
            )

    def _get_market_data(self, ticker: str = None) -> List[Dict[str, Any]]:
        """Fetch market data from spider network."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone

            cutoff = timezone.now() - timedelta(hours=24)
            query = SpiderData.objects.filter(
                spider_name__in=['yahoo_finance', 'coingecko', 'finnhub'],
                created_at__gte=cutoff
            ).order_by('-created_at')[:50]

            results = []
            for data in query:
                raw = data.raw_data or {}
                item = {
                    'source': data.spider_name,
                    'ticker': raw.get('symbol', raw.get('ticker', '')),
                    'price': raw.get('price', raw.get('regularMarketPrice', 0)),
                    'change_pct': raw.get('change_pct', raw.get('regularMarketChangePercent', 0)),
                    'volume': raw.get('volume', raw.get('regularMarketVolume', 0)),
                    'avg_volume': raw.get('avg_volume', raw.get('averageVolume', 0)),
                    'timestamp': str(data.created_at),
                }

                # Filter by ticker if specified
                if ticker and ticker.upper() != item['ticker'].upper():
                    continue

                results.append(item)

            return results

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return []

    def _analyze_movements(self, market_data: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze market data for significant movements."""
        movements = []

        for data in market_data:
            try:
                change_pct = abs(float(data.get('change_pct', 0) or 0))
                volume = float(data.get('volume', 0) or 0)
                avg_volume = float(data.get('avg_volume', 1) or 1)

                volume_ratio = volume / avg_volume if avg_volume > 0 else 0

                movement = {
                    'ticker': data.get('ticker', 'UNKNOWN'),
                    'price': data.get('price', 0),
                    'change_pct': change_pct,
                    'volume_ratio': round(volume_ratio, 2),
                    'is_volume_spike': volume_ratio >= self.VOLUME_SPIKE_THRESHOLD,
                    'is_significant_move': change_pct >= self.PRICE_CHANGE_MEDIUM,
                }

                movements.append(movement)

            except (ValueError, TypeError) as e:
                logger.debug(f"Error parsing market data: {e}")
                continue

        # Sort by significance
        movements.sort(key=lambda x: (x['change_pct'], x['volume_ratio']), reverse=True)

        return movements

    def _generate_alerts(self, movements: List[Dict]) -> List[Dict[str, Any]]:
        """Generate alerts from analyzed movements."""
        alerts = []

        for movement in movements:
            change_pct = movement.get('change_pct', 0)
            volume_ratio = movement.get('volume_ratio', 0)

            # Determine severity
            if change_pct >= self.PRICE_CHANGE_CRITICAL:
                severity = 'CRITICAL'
            elif change_pct >= self.PRICE_CHANGE_HIGH or volume_ratio >= 5:
                severity = 'HIGH'
            elif change_pct >= self.PRICE_CHANGE_MEDIUM or volume_ratio >= 3:
                severity = 'MEDIUM'
            elif movement.get('is_volume_spike') or change_pct >= 0.03:
                severity = 'LOW'
            else:
                continue  # Not significant enough to alert

            alerts.append({
                'ticker': movement['ticker'],
                'severity': severity,
                'type': 'MARKET_MOVEMENT',
                'price': movement['price'],
                'change_pct': change_pct,
                'volume_ratio': volume_ratio,
                'message': self._format_alert_message(movement, severity),
            })

        return alerts

    def _format_alert_message(self, movement: Dict, severity: str) -> str:
        """Format a human-readable alert message."""
        ticker = movement['ticker']
        change = movement['change_pct'] * 100
        vol_ratio = movement['volume_ratio']

        if severity == 'CRITICAL':
            return f"CRITICAL: {ticker} moved {change:.1f}% with {vol_ratio:.1f}x volume!"
        elif severity == 'HIGH':
            return f"HIGH: {ticker} showing {change:.1f}% change, {vol_ratio:.1f}x volume"
        elif severity == 'MEDIUM':
            return f"MEDIUM: {ticker} at {change:.1f}% with elevated volume ({vol_ratio:.1f}x)"
        else:
            return f"LOW: Notable activity in {ticker}: {change:.1f}% change"
