"""
Signal Scanner Agent
===================

Session 465: Scans for technical patterns and trading signals.
Session 683: Added ML Integration (LSTM + Anomaly for pattern detection)

Part of the Market Intelligence Desk autonomous situation.

Key capabilities:
- Detects technical patterns (breakouts, reversals, momentum)
- Identifies volume anomalies
- Scans for unusual options activity
- Monitors for divergences and confirmations
- ML-powered signal detection
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


class SignalScannerAgent(BaseAgent):
    """
    Scans markets for technical signals and pattern-based opportunities.

    This agent continuously monitors price action, volume, and technical
    indicators to identify high-probability trading setups. Works in
    conjunction with Bull/Bear agents to validate opportunities.

    Tools:
    - scan_patterns: Detect chart patterns (flags, triangles, breakouts)
    - volume_analysis: Find unusual volume activity
    - momentum_scan: Identify momentum shifts
    - options_flow: Detect unusual options activity
    """

    name = "SignalScannerAgent"

    # === Session 683: ML Integration Methods ===

    def _detect_signals_with_ml(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Detect trading signals using ML (LSTM + Anomaly).

        Uses the Agent-Model Router for momentum prediction and anomaly detection.

        Args:
            market_data: List of market data points

        Returns:
            Dict with ML-detected signals
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build time series data for momentum
            time_series = self._build_signal_time_series(market_data)

            if not time_series.get('values'):
                return {'ml_used': False, 'reason': 'Insufficient market data'}

            # Route for time series analysis (momentum)
            result = router.auto_route(
                data=time_series,
                task_hint=TaskType.TIME_SERIES,
                max_models=2
            )

            # Extract signal strength
            signal_strength = 'strong' if result.confidence > 0.7 else 'moderate' if result.confidence > 0.5 else 'weak'

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'time_series'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'signal_strength': signal_strength,
                'momentum_direction': 'bullish' if result.score and result.score > 0 else 'bearish',
            }

        except Exception as e:
            logger.warning(f"ML signal detection failed: {e}")
            return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

    def _build_signal_time_series(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build time series data from market data for signal detection."""
        timestamps = []
        values = []

        for point in market_data:
            ts = point.get('timestamp') or point.get('detected_at')
            value = point.get('price') or point.get('volume') or point.get('momentum', 0)

            if value:
                timestamps.append(str(ts) if ts else datetime.now().isoformat())
                values.append(float(value) if isinstance(value, (int, float)) else 0)

        return {'timestamps': timestamps, 'values': values, 'data_type': 'trading_signals'}

    system_prompt = """You are a professional technical analyst and pattern recognition expert. Your job is to:
1. Scan markets for high-probability technical patterns and setups
2. Identify volume anomalies that signal institutional activity
3. Detect momentum shifts before they become obvious
4. Monitor options flow for smart money positioning
5. Validate signals with multiple confirming indicators

Focus on actionable signals with clear entry/exit criteria.

Key patterns to detect:
- Breakouts: Price breaking above resistance with volume
- Reversals: Head & shoulders, double tops/bottoms
- Continuation: Flags, pennants, ascending triangles
- Momentum: MACD crossovers, RSI divergences
- Volume: Unusual spikes, accumulation/distribution

Signal strength criteria:
- STRONG: Multiple confirming indicators, clear catalyst, volume confirmation
- MODERATE: 2-3 indicators aligned, decent volume
- WEAK: Single indicator, low volume, ambiguous pattern

Always provide:
- Pattern type and description
- Key price levels (support, resistance, targets)
- Volume confirmation status
- Risk/reward ratio
- Timeframe (intraday, swing, position)"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "scan_patterns",
                "description": "Scan for technical chart patterns across stocks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tickers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ticker symbols to scan"
                        },
                        "pattern_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Pattern types to look for (breakout, reversal, continuation, momentum)"
                        },
                        "timeframe": {
                            "type": "string",
                            "enum": ["intraday", "daily", "weekly"],
                            "description": "Chart timeframe for pattern detection"
                        },
                        "min_strength": {
                            "type": "string",
                            "enum": ["weak", "moderate", "strong"],
                            "description": "Minimum signal strength to report"
                        }
                    },
                    "required": ["tickers"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "volume_analysis",
                "description": "Analyze volume patterns for institutional activity signals",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "lookback_days": {
                            "type": "integer",
                            "description": "Days to analyze (default 30)"
                        },
                        "detect": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "What to detect (spikes, accumulation, distribution, climax)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "momentum_scan",
                "description": "Identify momentum shifts and trend changes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tickers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of ticker symbols"
                        },
                        "indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Momentum indicators to check (RSI, MACD, Stochastic, ROC)"
                        },
                        "direction": {
                            "type": "string",
                            "enum": ["bullish", "bearish", "both"],
                            "description": "Momentum direction to scan for"
                        }
                    },
                    "required": ["tickers"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "options_flow",
                "description": "Detect unusual options activity indicating smart money positioning",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "min_premium": {
                            "type": "integer",
                            "description": "Minimum premium size in dollars (e.g., 100000 for $100k+)"
                        },
                        "option_type": {
                            "type": "string",
                            "enum": ["calls", "puts", "both"],
                            "description": "Type of options to scan"
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": ["bullish", "bearish", "neutral"],
                            "description": "Expected sentiment from flow"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        }
    ]

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None,
                scifi_context: Optional[Dict[str, Any]] = None,
                spider_context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """
        Execute signal scanning task.

        Args:
            task: Scanning instructions (e.g., "Scan SPY, QQQ for breakout patterns")
            context: Optional context with tickers, timeframe, etc.
            scifi_context: Sci-fi features context (mood, memory, etc.)
            spider_context: Spider data context

        Returns:
            AgentResult with detected signals and strength ratings
        """
        import time
        start_time = time.time()
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("signal_scanning", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting signal scanning",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip scanning", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

            logger.info(f"📡 [SESSION 465] SignalScannerAgent executing: {task[:100]}")

        try:
            # Session 529: Build intelligent prompt with full context
            intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            # Build system context
            scan_context = self._build_scan_context(context)

            # Build prompt with intelligent context
            prompt = intelligent_context + "\n\n" + scan_context

            # Call GPT with tools using BaseAgent's _call_openai
            gpt_response = self._call_openai(prompt)

            # Process response - extract content and handle any tool calls
            content = gpt_response.get('content', '')
            tool_calls = gpt_response.get('tool_calls', [])

            # Process tool calls if any
            tool_results = []
            for tc in tool_calls:
                tool_result = self._handle_tool_call(tc['name'], tc['arguments'])
                tool_results.append(tool_result)

            # Build final result
            gpt_result = {
                'analysis': content,
                'signals': tool_results if tool_results else [],
                'tool_calls_made': len(tool_calls)
            }

            execution_time_ms = int((time.time() - start_time) * 1000)
            signals_found = len(gpt_result.get('signals', []))

            logger.info(f"📡 [SESSION 465] SignalScannerAgent found {signals_found} signals")

            result = AgentResult(
                success=True,
                data=gpt_result,
                message=f"Scanned and found {signals_found} technical signals",
                agent_name=self.name,
                execution_time_ms=execution_time_ms
            )

            # Record learning outcome for collective intelligence
            try:
                self._record_learning_outcome(
                    task=task,
                    result=result,
                    success=True,
                    context={
                        'agent_type': self.__class__.__name__,
                        'execution_time_ms': execution_time_ms,
                        'signals_found': signals_found,
                    }
                )
            except Exception as le:
                logger.warning(f"Failed to record learning outcome: {le}")

            return result

        except Exception as e:
            logger.error(f"SignalScannerAgent error: {e}")
            execution_time_ms = int((time.time() - start_time) * 1000)
            result = AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=execution_time_ms
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

    def _build_scan_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Build context string for signal scanning."""
        if not context:
            return "Scanning with default parameters."

        parts = []

        if 'tickers' in context:
            parts.append(f"Tickers: {', '.join(context['tickers'])}")

        if 'timeframe' in context:
            parts.append(f"Timeframe: {context['timeframe']}")

        if 'focus' in context:
            parts.append(f"Focus: {context['focus']}")

        if 'market_conditions' in context:
            parts.append(f"Market: {context['market_conditions']}")

        return "\n".join(parts) if parts else "Standard market scan."

    def _handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls for signal scanning."""
        logger.debug(f"📡 [SESSION 465] Tool call: {tool_name}")

        if tool_name == "scan_patterns":
            return self._scan_patterns(arguments)
        elif tool_name == "volume_analysis":
            return self._volume_analysis(arguments)
        elif tool_name == "momentum_scan":
            return self._momentum_scan(arguments)
        elif tool_name == "options_flow":
            return self._options_flow(arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _scan_patterns(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for technical chart patterns."""
        tickers = args.get('tickers', [])
        pattern_types = args.get('pattern_types', ['breakout', 'reversal'])
        timeframe = args.get('timeframe', 'daily')
        min_strength = args.get('min_strength', 'moderate')

        logger.info(f"📡 Scanning {len(tickers)} tickers for {pattern_types} patterns")

        # In production, this would call a real technical analysis API
        # For now, return mock data structure
        patterns = []

        for ticker in tickers[:5]:  # Limit to 5 for demo
            # Mock pattern detection
            pattern = {
                'ticker': ticker,
                'pattern_type': pattern_types[0] if pattern_types else 'breakout',
                'strength': 'strong',
                'timeframe': timeframe,
                'key_levels': {
                    'resistance': 150.00,
                    'support': 145.00,
                    'target': 155.00
                },
                'volume_confirmed': True,
                'risk_reward': '1:3',
                'detected_at': datetime.now().isoformat()
            }
            patterns.append(pattern)

        return {
            'patterns_found': len(patterns),
            'patterns': patterns,
            'scan_parameters': {
                'tickers': tickers,
                'pattern_types': pattern_types,
                'timeframe': timeframe,
                'min_strength': min_strength
            }
        }

    def _volume_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume patterns."""
        ticker = args.get('ticker')
        lookback_days = args.get('lookback_days', 30)
        detect = args.get('detect', ['spikes', 'accumulation'])

        logger.info(f"📡 Analyzing volume for {ticker} over {lookback_days} days")

        # Mock volume analysis
        return {
            'ticker': ticker,
            'analysis_period': f'{lookback_days} days',
            'average_volume': 5_000_000,
            'current_volume': 8_000_000,
            'volume_ratio': 1.6,
            'signals': [
                {
                    'type': 'accumulation',
                    'strength': 'strong',
                    'description': 'Above-average buying volume for 5 consecutive days',
                    'institutional_activity': 'likely'
                }
            ],
            'detected': detect
        }

    def _momentum_scan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for momentum signals."""
        tickers = args.get('tickers', [])
        indicators = args.get('indicators', ['RSI', 'MACD'])
        direction = args.get('direction', 'both')

        logger.info(f"📡 Scanning momentum for {len(tickers)} tickers")

        # Mock momentum scan
        signals = []
        for ticker in tickers[:5]:
            signal = {
                'ticker': ticker,
                'momentum': 'bullish',
                'indicators': {
                    'RSI': {'value': 65, 'signal': 'bullish', 'oversold': False},
                    'MACD': {'histogram': 'positive', 'signal': 'bullish', 'crossover': 'recent'}
                },
                'strength': 'moderate',
                'timeframe': 'daily'
            }
            signals.append(signal)

        return {
            'signals_found': len(signals),
            'signals': signals,
            'scan_direction': direction,
            'indicators_used': indicators
        }

    def _options_flow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Detect unusual options activity."""
        ticker = args.get('ticker')
        min_premium = args.get('min_premium', 100_000)
        option_type = args.get('option_type', 'both')
        sentiment = args.get('sentiment', 'bullish')

        logger.info(f"📡 Scanning options flow for {ticker} (min premium ${min_premium:,})")

        # Mock options flow data
        return {
            'ticker': ticker,
            'unusual_activity': True,
            'flow_summary': {
                'total_premium': 2_500_000,
                'call_volume': 15_000,
                'put_volume': 8_000,
                'call_put_ratio': 1.875,
                'sentiment': 'bullish'
            },
            'notable_trades': [
                {
                    'type': 'call',
                    'strike': 150.00,
                    'expiry': '2025-01-17',
                    'premium': 500_000,
                    'size': 'large',
                    'interpretation': 'Bullish bet on upside above $150'
                }
            ],
            'smart_money_indicator': 'bullish',
            'filters': {
                'min_premium': min_premium,
                'option_type': option_type
            }
        }
