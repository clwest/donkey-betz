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

import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone as dt_timezone

from core.agents.base_agent import BaseAgent, AgentResult, WEB_SEARCH_TOOL, strip_simulated_tool_json
from core.agents.report_schemas import build_provenance, format_disclaimer
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
    create_deliverable_on_schedule = True  # Fixed: was False (Session 1077), outputs were lost in AgentExecution

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
        },
        # Session 988: Web search fallback when local data is unavailable
        WEB_SEARCH_TOOL,
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

        # Session 750: Time Travel integration
        with self.time_travel_session("market_movement_monitoring", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a specialist in tracking significant market movements. One capability: I monitor intraday price swings, sector rotations, and momentum shifts to alert on stocks making unusual moves that warrant immediate attention.",
                    data={'type': 'self_description', 'specialization': 'movement_monitoring', 'focus': 'realtime_alerts'},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="analysis",
                action="Starting market movement monitoring with tools",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip monitoring", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            logger.info(f"MarketMovementMonitorAgent executing with tools: {task[:100]}...")

        try:
            # Build intelligent prompt with full context
            intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            # Session 761: Build messages for tool-enabled LLM call
            ticker = context.get('ticker', '')
            ticker_context = f"\n\nTarget ticker: {ticker}" if ticker else ""
            spider_summary = f"\n\nMarket Intelligence: {spider_intel['summary']}" if spider_intel['summary'] else ""

            messages = [
                {"role": "system", "content": self.system_prompt + intelligent_context + ticker_context + spider_summary},
                {"role": "user", "content": task}
            ]

            # Session 761: Call LLM with tools enabled
            from openai import OpenAI
            client = OpenAI()

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                tools=self.get_tools_with_delegation(),
                tool_choice="auto",
                max_completion_tokens=4000
            )

            # Process response
            assistant_message = response.choices[0].message
            tool_calls_made = []
            collected_data = {}

            # Session 761: Handle tool calls from LLM
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                    self.record_decision(
                        decision_type="tool_call",
                        action=f"Calling tool: {tool_name}",
                        reasoning=f"LLM requested tool with args: {tool_args}",
                        confidence=0.9
                    )

                    logger.info(f"🔧 MarketMovementMonitorAgent calling tool: {tool_name}({tool_args})")

                    # Execute the tool
                    tool_result = self._execute_tool_call(tool_name, tool_args)
                    tool_calls_made.append({
                        'tool': tool_name,
                        'args': tool_args,
                        'result': tool_result
                    })
                    collected_data[tool_name] = tool_result

                    # Add tool result to conversation for LLM synthesis
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)[:8000]
                    })

                # Get final synthesis from LLM
                final_response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    max_completion_tokens=3000
                )
                analysis = final_response.choices[0].message.content
            else:
                analysis = assistant_message.content or "No movement analysis generated."

            # Session 1018: Strip simulated JSON tool calls from text output
            analysis = strip_simulated_tool_json(analysis)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            # Session 953: Build provenance from analysis results
            sources = []
            for tc in tool_calls_made:
                sources.append({
                    'name': tc.get('tool', 'market_movement'),
                    'endpoint': 'market_data_api',
                    'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                    'record_count': 1,
                })

            # Stock data stale threshold: 24 hours
            provenance = build_provenance(
                report_type='stock_analysis',
                agent_name=self.name,
                sources=sources if sources else [{
                    'name': 'MarketMovementMonitorAgent',
                    'endpoint': 'market_data_api',
                    'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                    'record_count': 1,
                }],
                stale_threshold_hours=24.0,
            )
            provenance.disclaimer = format_disclaimer('stock_analysis')

            message = provenance.to_markdown_block() + "\n" + analysis

            result = AgentResult(
                success=True,
                message=message,
                data={
                    'analysis': analysis,
                    'ticker': ticker,
                    'tool_calls': tool_calls_made,
                    'collected_data': collected_data,
                    'alerts': self._extract_alerts_from_collected(collected_data),
                    'provenance': provenance.to_dict(),
                    'publishable': provenance.publishable,
                    'validation_status': provenance.validation_status,
                },
                agent_name=self.name,
                execution_time_ms=execution_time,
                tool_calls=tool_calls_made
            )

            # Record learning outcome
            try:
                self._record_learning_outcome(
                    task=task,
                    result=result,
                    success=True,
                    context={
                        'agent_type': self.__class__.__name__,
                        'execution_time_ms': execution_time,
                        'tools_used': [tc['tool'] for tc in tool_calls_made],
                    }
                )
            except Exception as le:
                logger.warning(f"Failed to record learning outcome: {le}")

            # Session 1006: Persist output to Deliverable
            self._save_to_deliverable(
                title=f"Market Movement: {task[:80]}",
                content=result.message,
                deliverable_type='analysis',
                category='Market Movement',
                tags=['market', 'stocks'],
                metadata={'task': task[:200]},
            )

            return result

        except Exception as e:
            logger.error(f"MarketMovementMonitorAgent error: {e}", exc_info=True)
            return AgentResult(
                success=False,
                message=f"Error monitoring movements: {str(e)}",
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
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

    def _extract_alerts_from_collected(self, collected_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract structured alerts from tool call results for the coordinator."""
        alerts = []

        for tool_name, result in collected_data.items():
            if not isinstance(result, dict):
                continue

            # Extract from volume spike results
            for spike in result.get('spikes', []):
                ticker = spike.get('ticker', result.get('ticker', ''))
                if not ticker:
                    continue
                volume_ratio = float(spike.get('volume_ratio', 0) or 0)
                change_pct = abs(float(spike.get('change_pct', 0) or 0))
                if volume_ratio >= self.VOLUME_SPIKE_THRESHOLD or change_pct >= self.PRICE_CHANGE_MEDIUM:
                    severity = 'HIGH' if volume_ratio >= 5 or change_pct >= self.PRICE_CHANGE_HIGH else 'MEDIUM'
                    alerts.append({
                        'ticker': ticker,
                        'severity': severity,
                        'type': 'VOLUME_SPIKE',
                        'message': f"Volume spike: {ticker} at {volume_ratio:.1f}x avg volume, {change_pct*100:.1f}% change",
                    })

            # Extract from breakout results
            for breakout in result.get('breakouts', []):
                ticker = result.get('ticker', '')
                if ticker:
                    alerts.append({
                        'ticker': ticker,
                        'severity': 'HIGH',
                        'type': 'BREAKOUT',
                        'message': f"Breakout: {ticker} {breakout.get('type', 'level')} at ${breakout.get('level', 0)}",
                    })

            # Extract items that already have a severity key
            if result.get('severity'):
                alerts.append({
                    'ticker': result.get('ticker', ''),
                    'severity': result['severity'],
                    'type': result.get('type', 'MARKET_MOVEMENT'),
                    'message': result.get('message', ''),
                })

        # Fallback: if tools produced nothing, try direct data analysis
        if not alerts:
            market_data = self._get_market_data()
            movements = self._analyze_movements(market_data)
            alerts = self._generate_alerts(movements)

        return alerts

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for market movement monitoring.
        Session 988: Updated to call super() for delegation + web_search.

        Tools:
        - detect_volume_spike: Find unusual volume activity
        - track_momentum: Monitor price momentum
        - alert_breakout: Detect technical breakouts
        - scan_after_hours: Monitor pre/post market activity
        - web_search: Web search fallback (handled by BaseAgent)
        """
        ticker = arguments.get('ticker', 'SPY')

        if tool_name == 'detect_volume_spike':
            threshold = arguments.get('threshold_multiplier', 2.0)
            timeframe = arguments.get('timeframe', '1d')
            market_data = self._get_market_data(ticker if ticker != 'market' else None)
            spikes = [m for m in market_data if m.get('volume_ratio', 0) >= threshold]
            return {
                'tool': tool_name,
                'ticker': ticker,
                'threshold': threshold,
                'timeframe': timeframe,
                'spikes_found': len(spikes),
                'spikes': spikes[:10],
                'message': f"Found {len(spikes)} volume spikes above {threshold}x threshold"
            }

        elif tool_name == 'track_momentum':
            indicators = arguments.get('indicators', ['RSI', 'MACD'])
            # Session 838: Use real market data instead of hardcoded placeholders
            try:
                from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider
                spider = YahooFinanceSpider()
                stock_data = spider.fetch_data(symbols=[ticker])

                if stock_data and len(stock_data) > 0:
                    data = stock_data[0]
                    price = data.get('current_price', 0)
                    change_pct = data.get('change_percent', 0) or 0

                    # Derive momentum from real price change
                    if change_pct > 3:
                        trend = 'strongly_bullish'
                        rsi_estimate = 70 + min(change_pct * 2, 15)  # Scale with change
                        macd_signal = 'strong_buy'
                    elif change_pct > 1:
                        trend = 'bullish'
                        rsi_estimate = 55 + change_pct * 5
                        macd_signal = 'bullish'
                    elif change_pct > -1:
                        trend = 'neutral'
                        rsi_estimate = 50 + change_pct * 5
                        macd_signal = 'neutral'
                    elif change_pct > -3:
                        trend = 'bearish'
                        rsi_estimate = 45 + change_pct * 5
                        macd_signal = 'bearish'
                    else:
                        trend = 'strongly_bearish'
                        rsi_estimate = 30 + max(change_pct * 2, -15)
                        macd_signal = 'strong_sell'

                    rsi_estimate = max(10, min(90, rsi_estimate))  # Clamp to valid range

                    return {
                        'tool': tool_name,
                        'ticker': ticker,
                        'indicators': indicators,
                        'current_price': price,
                        'change_percent': round(change_pct, 2),
                        'momentum': {
                            'RSI': {'value': round(rsi_estimate, 1), 'signal': trend},
                            'MACD': {'histogram': 'positive' if change_pct > 0 else 'negative', 'signal': macd_signal},
                        },
                        'trend': trend,
                        'data_source': 'yahoo_finance',
                        'data_quality': 'real',
                        'message': f"Momentum analysis for {ticker}: {trend} (change: {change_pct:+.2f}%)"
                    }
                else:
                    return {
                        'tool': tool_name,
                        'ticker': ticker,
                        'indicators': indicators,
                        'status': 'insufficient_data',
                        'reason': f'No market data available for {ticker}',
                        'data_quality': 'unavailable',
                        'message': f"Unable to fetch momentum data for {ticker}"
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch momentum data for {ticker}: {e}")
                return {
                    'tool': tool_name,
                    'ticker': ticker,
                    'indicators': indicators,
                    'status': 'insufficient_data',
                    'reason': f'Error fetching data: {str(e)}',
                    'data_quality': 'error',
                    'message': f"Error analyzing momentum for {ticker}"
                }

        elif tool_name == 'alert_breakout':
            level_types = arguments.get('level_types', ['resistance', 'support'])
            # Session 838: Use real market data instead of hardcoded placeholders
            try:
                from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider
                spider = YahooFinanceSpider()
                stock_data = spider.fetch_data(symbols=[ticker])

                if stock_data and len(stock_data) > 0:
                    data = stock_data[0]
                    price = data.get('current_price', 0)
                    high_52w = data.get('fifty_two_week_high', 0)
                    low_52w = data.get('fifty_two_week_low', 0)

                    # Calculate dynamic support/resistance based on real data
                    resistance = round(price * 1.05, 2)  # 5% above current
                    support = round(price * 0.95, 2)  # 5% below current

                    # Detect breakouts
                    breakouts = []
                    if high_52w and price >= high_52w * 0.98:
                        breakouts.append({
                            'type': '52w_high_breakout',
                            'level': high_52w,
                            'current_price': price,
                            'distance_pct': round((price / high_52w - 1) * 100, 2)
                        })
                    if low_52w and price <= low_52w * 1.02:
                        breakouts.append({
                            'type': '52w_low_breakdown',
                            'level': low_52w,
                            'current_price': price,
                            'distance_pct': round((price / low_52w - 1) * 100, 2)
                        })

                    return {
                        'tool': tool_name,
                        'ticker': ticker,
                        'level_types': level_types,
                        'breakouts': breakouts,
                        'key_levels': {
                            'current_price': price,
                            'resistance': resistance,
                            'support': support,
                            '52w_high': high_52w or 'unavailable',
                            '52w_low': low_52w or 'unavailable'
                        },
                        'data_source': 'yahoo_finance',
                        'data_quality': 'real',
                        'message': f"Key levels for {ticker}: support ${support}, resistance ${resistance}" + (f" - {len(breakouts)} breakout(s) detected!" if breakouts else "")
                    }
                else:
                    return {
                        'tool': tool_name,
                        'ticker': ticker,
                        'level_types': level_types,
                        'status': 'insufficient_data',
                        'reason': f'No market data available for {ticker}',
                        'data_quality': 'unavailable',
                        'message': f"Unable to determine key levels for {ticker}"
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch breakout data for {ticker}: {e}")
                return {
                    'tool': tool_name,
                    'ticker': ticker,
                    'level_types': level_types,
                    'status': 'insufficient_data',
                    'reason': f'Error fetching data: {str(e)}',
                    'data_quality': 'error',
                    'message': f"Error analyzing breakouts for {ticker}"
                }

        elif tool_name == 'scan_after_hours':
            # Session 838: Return insufficient_data status - no after-hours data provider configured
            min_volume = arguments.get('min_volume', 10000)
            min_change = arguments.get('min_change_pct', 2.0)
            return {
                'tool': tool_name,
                'min_volume': min_volume,
                'min_change_pct': min_change,
                'status': 'insufficient_data',
                'reason': 'No real-time after-hours/pre-market data provider configured',
                'required_data_sources': [
                    'Nasdaq TotalView ITCH',
                    'NYSE Arca after-hours feed',
                    'Alpha Vantage Extended Hours',
                    'Polygon.io extended hours API'
                ],
                'data_quality': 'unavailable',
                'message': f"After-hours scanning unavailable - requires extended hours data provider"
            }

        # Session 988: Fall through to BaseAgent for web_search + delegation
        return super()._execute_tool_call(tool_name, arguments)
