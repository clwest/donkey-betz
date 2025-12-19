"""
Institutional Watcher Agent
===========================

Session 461: Tracks insider trading & institutional activity.
Equivalent to WhaleWatcherAgent in the blockchain audit system.

Key capabilities:
- Insider trading monitoring (Form 4)
- 13F filing analysis (institutional holdings)
- Large position change alerts
- Insider sentiment analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class InstitutionalWatcherAgent(BaseAgent):
    """
    Monitors insider trading and institutional activity.

    Tools:
    - monitor_insiders: Track Form 4 insider transactions
    - track_13f_filings: Monitor institutional 13F filings
    - alert_large_position: Detect significant position changes
    - analyze_sentiment: Analyze insider buying/selling patterns
    """

    name = "InstitutionalWatcherAgent"

    system_prompt = """You are an insider trading and institutional activity specialist monitoring for:
1. Form 4 filings (insider buys/sells)
2. 13F filings (institutional holdings)
3. Large position changes (>5% ownership changes)
4. Unusual insider activity patterns
5. Cluster buying/selling by multiple insiders

Alert criteria:
- CRITICAL: CEO/CFO selling >50% holdings, multiple insiders selling before earnings
- HIGH: Large insider sales (>$1M), significant position reduction
- MEDIUM: Notable insider activity, institutional position changes
- LOW: Routine insider transactions, minor holdings updates

Focus on transactions that diverge from normal patterns."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "monitor_insiders",
                "description": "Track Form 4 insider transactions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "insider_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Insider types to track (CEO, CFO, Director, 10% Owner)"
                        },
                        "transaction_type": {"type": "string", "enum": ["BUY", "SELL", "ALL"]}
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "track_13f_filings",
                "description": "Monitor institutional 13F holdings filings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "institution": {"type": "string", "description": "Specific institution to track"},
                        "min_position_value": {"type": "number", "description": "Minimum position value to track"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "alert_large_position",
                "description": "Detect significant position changes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "change_threshold_pct": {"type": "number", "description": "Minimum % change to alert (default 5%)"}
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_sentiment",
                "description": "Analyze insider buying/selling sentiment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "lookback_days": {"type": "integer", "description": "Days to analyze (default 90)"}
                    },
                    "required": ["ticker"]
                }
            }
        }
    ]

    # Thresholds
    LARGE_TRANSACTION_VALUE = 1_000_000  # $1M
    SIGNIFICANT_POSITION_CHANGE = 0.05  # 5%
    CRITICAL_POSITION_REDUCTION = 0.50  # 50%

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute institutional activity monitoring.

        Args:
            task: Monitoring task description
            context: Additional context
            scifi_context: Sci-fi features context
            spider_context: Spider data context

        Returns:
            AgentResult with insider activity findings
        """
        start_time = datetime.now()
        context = context or {}

        logger.info(f"InstitutionalWatcherAgent executing: {task[:100]}...")

        try:
            # Get SEC insider data
            insider_data = self._get_insider_data(context.get('ticker'))

            # Analyze patterns
            patterns = self._analyze_patterns(insider_data)

            # Generate alerts
            alerts = self._generate_alerts(insider_data, patterns)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            result = AgentResult(
                success=True,
                message=f"Institutional watch complete. Found {len(alerts)} alerts.",
                data={
                    'insider_data': insider_data,
                    'patterns': patterns,
                    'alerts': alerts,
                    'sentiment': self._calculate_sentiment(insider_data),
                },
                agent_name=self.name,
                execution_time_ms=execution_time
            )

            # Record learning outcome for collective intelligence
            try:
                self._record_learning_outcome(
                    task=task,
                    result=result,
                    success=True,
                    context={
                        'agent_type': self.__class__.__name__,
                        'execution_time_ms': execution_time,
                        'alerts_found': len(alerts),
                        'transactions_analyzed': len(insider_data),
                    }
                )
            except Exception as le:
                logger.warning(f"Failed to record learning outcome: {le}")

            return result

        except Exception as e:
            logger.error(f"InstitutionalWatcherAgent error: {e}")
            result = AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name
            )

            # Record failed learning outcome
            try:
                self._record_learning_outcome(
                    task=task,
                    result=result,
                    success=False,
                    context={
                        'agent_type': self.__class__.__name__,
                        'error': str(e),
                    }
                )
            except Exception as le:
                logger.warning(f"Failed to record learning outcome: {le}")

            return result

    def _get_insider_data(self, ticker: str = None) -> List[Dict[str, Any]]:
        """Fetch insider trading data from SEC filings."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone

            cutoff = timezone.now() - timedelta(days=30)
            query = SpiderData.objects.filter(
                spider_name='sec_edgar',
                created_at__gte=cutoff
            ).order_by('-created_at')[:100]

            results = []
            for data in query:
                raw = data.raw_data or {}
                form_type = str(raw.get('form_type', '')).upper()

                # Look for Form 4 (insider trades) and 13F (institutional)
                if form_type in ['4', 'FORM 4', '13F', '13F-HR']:
                    item = {
                        'company': raw.get('company', raw.get('title', '')),
                        'form_type': form_type,
                        'filed_at': raw.get('filed_at', str(data.created_at)),
                        'insider_name': raw.get('insider_name', raw.get('reporting_owner', '')),
                        'transaction_type': raw.get('transaction_type', ''),
                        'shares': raw.get('shares', 0),
                        'value': raw.get('value', raw.get('transaction_value', 0)),
                        'url': raw.get('url', ''),
                    }

                    # Filter by ticker if specified
                    if ticker and ticker.upper() not in str(item['company']).upper():
                        continue

                    results.append(item)

            return results

        except Exception as e:
            logger.error(f"Error fetching insider data: {e}")
            return []

    def _analyze_patterns(self, insider_data: List[Dict]) -> Dict[str, Any]:
        """Analyze insider activity patterns."""
        patterns = {
            'total_transactions': len(insider_data),
            'buys': 0,
            'sells': 0,
            'total_buy_value': 0,
            'total_sell_value': 0,
            'cluster_activity': [],  # Multiple insiders same direction
            'unusual_activity': [],  # Deviates from historical patterns
        }

        for item in insider_data:
            tx_type = str(item.get('transaction_type', '')).upper()
            value = float(item.get('value', 0) or 0)

            if 'BUY' in tx_type or 'PURCHASE' in tx_type or 'P' == tx_type:
                patterns['buys'] += 1
                patterns['total_buy_value'] += value
            elif 'SELL' in tx_type or 'SALE' in tx_type or 'S' == tx_type:
                patterns['sells'] += 1
                patterns['total_sell_value'] += value

        # Calculate buy/sell ratio
        if patterns['sells'] > 0:
            patterns['buy_sell_ratio'] = round(patterns['buys'] / patterns['sells'], 2)
        else:
            patterns['buy_sell_ratio'] = float('inf') if patterns['buys'] > 0 else 0

        return patterns

    def _generate_alerts(self, insider_data: List[Dict], patterns: Dict) -> List[Dict]:
        """Generate alerts from insider activity."""
        alerts = []

        # Check for large transactions
        for item in insider_data:
            value = float(item.get('value', 0) or 0)
            tx_type = str(item.get('transaction_type', '')).upper()

            if value >= self.LARGE_TRANSACTION_VALUE:
                is_sell = 'SELL' in tx_type or 'SALE' in tx_type or 'S' == tx_type

                severity = 'HIGH' if is_sell else 'MEDIUM'

                alerts.append({
                    'type': 'LARGE_INSIDER_TRANSACTION',
                    'severity': severity,
                    'company': item.get('company', ''),
                    'insider': item.get('insider_name', ''),
                    'transaction_type': 'SELL' if is_sell else 'BUY',
                    'value': value,
                    'message': f"{'Large insider sale' if is_sell else 'Large insider purchase'}: ${value:,.0f} by {item.get('insider_name', 'Unknown')}",
                })

        # Check for cluster selling (multiple insiders selling)
        if patterns['sells'] >= 3 and patterns['buy_sell_ratio'] < 0.5:
            alerts.append({
                'type': 'CLUSTER_SELLING',
                'severity': 'HIGH',
                'message': f"Cluster selling detected: {patterns['sells']} sells vs {patterns['buys']} buys",
                'sell_count': patterns['sells'],
                'buy_count': patterns['buys'],
            })

        return alerts

    def _calculate_sentiment(self, insider_data: List[Dict]) -> Dict[str, Any]:
        """Calculate overall insider sentiment."""
        buys = 0
        sells = 0
        buy_value = 0
        sell_value = 0

        for item in insider_data:
            tx_type = str(item.get('transaction_type', '')).upper()
            value = float(item.get('value', 0) or 0)

            if 'BUY' in tx_type or 'PURCHASE' in tx_type or 'P' == tx_type:
                buys += 1
                buy_value += value
            elif 'SELL' in tx_type or 'SALE' in tx_type or 'S' == tx_type:
                sells += 1
                sell_value += value

        total = buys + sells
        if total == 0:
            return {'sentiment': 'NEUTRAL', 'score': 50, 'description': 'No insider activity'}

        buy_pct = buys / total

        if buy_pct >= 0.7:
            return {'sentiment': 'BULLISH', 'score': 80, 'description': 'Strong insider buying'}
        elif buy_pct >= 0.5:
            return {'sentiment': 'SLIGHTLY_BULLISH', 'score': 60, 'description': 'More buying than selling'}
        elif buy_pct >= 0.3:
            return {'sentiment': 'SLIGHTLY_BEARISH', 'score': 40, 'description': 'More selling than buying'}
        else:
            return {'sentiment': 'BEARISH', 'score': 20, 'description': 'Heavy insider selling'}
