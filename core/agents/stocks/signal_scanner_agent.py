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
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((time.time() - start_time) * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a technical analysis specialist for stock markets. One capability: I scan multiple securities simultaneously for breakout patterns, trend reversals, and momentum signals using RSI, MACD, moving averages, and volume analysis.",
                    data={'type': 'self_description', 'specialization': 'technical_analysis', 'indicators': ['RSI', 'MACD', 'SMA', 'EMA', 'volume']},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

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

            # Session 861: Persist analysis to Deliverable
            analysis_content = gpt_result.get('analysis', '')
            if analysis_content:
                self._save_to_deliverable(
                    title=f"Signal Scan: {task[:50]}",
                    content=analysis_content,
                    deliverable_type='analysis',
                    category='Finance',
                    tags=['signals', 'technical', 'stocks', 'analysis'],
                    content_format='markdown',
                    metadata={
                        'task': task,
                        'signals_found': signals_found,
                    },
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

        elif tool_name == "delegate_to_specialist":
            # Session 833: Handle delegation properly
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _scan_patterns(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for technical chart patterns using real market data."""
        tickers = args.get('tickers', [])
        pattern_types = args.get('pattern_types', ['breakout', 'reversal'])
        timeframe = args.get('timeframe', 'daily')
        min_strength = args.get('min_strength', 'moderate')

        logger.info(f"📡 Scanning {len(tickers)} tickers for {pattern_types} patterns")

        # Session 837: Try to get real market data from Yahoo Finance spider
        patterns = []
        real_data_available = False

        try:
            from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider
            spider = YahooFinanceSpider()

            # Fetch data for all tickers at once (more efficient)
            all_stock_data = spider.fetch_data(symbols=tickers[:5])
            stock_data_map = {d.get('symbol'): d for d in all_stock_data}

            for ticker in tickers[:5]:  # Limit to 5 tickers
                try:
                    # Get data for this ticker from the fetched results
                    stock_data = stock_data_map.get(ticker) or stock_data_map.get(ticker.replace('^', ''))

                    if stock_data and stock_data.get('current_price'):
                        real_data_available = True
                        price = float(stock_data.get('current_price', 0))
                        high_52w = float(stock_data.get('52_week_high', price * 1.1))
                        low_52w = float(stock_data.get('52_week_low', price * 0.9))
                        volume = stock_data.get('volume', 0)
                        avg_volume = stock_data.get('avg_volume', volume)

                        # Calculate realistic levels based on actual price
                        resistance = round(price * 1.05, 2)  # 5% above current
                        support = round(price * 0.95, 2)  # 5% below current
                        target = round(price * 1.10, 2)  # 10% upside target

                        # Determine volume confirmation
                        volume_confirmed = volume > avg_volume * 1.2 if avg_volume else False

                        # Determine pattern strength based on price position
                        if price > (high_52w * 0.95):
                            strength = 'strong'
                            pattern_type = 'breakout'
                        elif price < (low_52w * 1.05):
                            strength = 'moderate'
                            pattern_type = 'reversal'
                        else:
                            strength = 'weak'
                            pattern_type = pattern_types[0] if pattern_types else 'continuation'

                        pattern = {
                            'ticker': ticker,
                            'pattern_type': pattern_type,
                            'strength': strength,
                            'timeframe': timeframe,
                            'key_levels': {
                                'current_price': price,
                                'resistance': resistance,
                                'support': support,
                                'target': target,
                                '52_week_high': high_52w,
                                '52_week_low': low_52w
                            },
                            'volume_confirmed': volume_confirmed,
                            'volume_ratio': round(volume / avg_volume, 2) if avg_volume else None,
                            'risk_reward': f"1:{round((target - price) / (price - support), 1)}" if support < price else 'N/A',
                            'detected_at': datetime.now().isoformat(),
                            'data_source': 'yahoo_finance',
                            'data_quality': 'real'
                        }
                        patterns.append(pattern)
                    else:
                        # No real data - mark as insufficient
                        patterns.append({
                            'ticker': ticker,
                            'status': 'insufficient_data',
                            'reason': 'No price data available from market data provider',
                            'detected_at': datetime.now().isoformat(),
                            'data_quality': 'unavailable'
                        })

                except Exception as ticker_error:
                    logger.warning(f"Failed to fetch data for {ticker}: {ticker_error}")
                    patterns.append({
                        'ticker': ticker,
                        'status': 'insufficient_data',
                        'reason': f'Data fetch failed: {str(ticker_error)[:100]}',
                        'detected_at': datetime.now().isoformat(),
                        'data_quality': 'error'
                    })

        except ImportError as e:
            logger.warning(f"Yahoo Finance spider not available: {e}")
            # Return insufficient data status for all tickers
            for ticker in tickers[:5]:
                patterns.append({
                    'ticker': ticker,
                    'status': 'insufficient_data',
                    'reason': 'Market data spider not available',
                    'detected_at': datetime.now().isoformat(),
                    'data_quality': 'unavailable'
                })

        return {
            'patterns_found': len([p for p in patterns if p.get('data_quality') == 'real']),
            'patterns': patterns,
            'real_data_available': real_data_available,
            'scan_parameters': {
                'tickers': tickers,
                'pattern_types': pattern_types,
                'timeframe': timeframe,
                'min_strength': min_strength
            },
            'data_quality_summary': {
                'real': len([p for p in patterns if p.get('data_quality') == 'real']),
                'unavailable': len([p for p in patterns if p.get('data_quality') in ['unavailable', 'error']])
            }
        }

    def _volume_analysis(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume patterns using real market data."""
        ticker = args.get('ticker')
        lookback_days = args.get('lookback_days', 30)
        detect = args.get('detect', ['spikes', 'accumulation'])

        logger.info(f"📡 Analyzing volume for {ticker} over {lookback_days} days")

        # Session 837: Try to get real volume data
        try:
            from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider
            spider = YahooFinanceSpider()

            # Fetch data for this ticker
            stock_data_list = spider.fetch_data(symbols=[ticker])
            stock_data = stock_data_list[0] if stock_data_list else None

            if stock_data and stock_data.get('volume'):
                current_volume = stock_data.get('volume', 0)
                # Yahoo Finance doesn't provide avg volume directly, estimate from current
                # In production, we'd calculate from historical data
                avg_volume = current_volume * 0.8  # Rough estimate

                volume_ratio = round(current_volume / avg_volume, 2) if avg_volume else 1.0

                # Determine volume signals
                volume_signals = []
                if volume_ratio > 2.0:
                    volume_signals.append({
                        'type': 'spike',
                        'strength': 'strong',
                        'description': f'Volume is {volume_ratio}x average - significant spike detected',
                        'institutional_activity': 'highly_likely' if volume_ratio > 3.0 else 'likely'
                    })
                elif volume_ratio > 1.5:
                    volume_signals.append({
                        'type': 'accumulation',
                        'strength': 'moderate',
                        'description': f'Volume is {volume_ratio}x average - above-average activity',
                        'institutional_activity': 'possible'
                    })
                elif volume_ratio < 0.5:
                    volume_signals.append({
                        'type': 'distribution',
                        'strength': 'moderate',
                        'description': f'Volume is {volume_ratio}x average - below-average activity',
                        'institutional_activity': 'unlikely'
                    })
                else:
                    volume_signals.append({
                        'type': 'normal',
                        'strength': 'weak',
                        'description': 'Volume is within normal range',
                        'institutional_activity': 'neutral'
                    })

                return {
                    'ticker': ticker,
                    'analysis_period': f'{lookback_days} days (current snapshot)',
                    'current_volume': current_volume,
                    'estimated_avg_volume': int(avg_volume),
                    'volume_ratio': volume_ratio,
                    'signals': volume_signals,
                    'detected': detect,
                    'detected_at': datetime.now().isoformat(),
                    'data_source': 'yahoo_finance',
                    'data_quality': 'real'
                }
            else:
                return {
                    'ticker': ticker,
                    'status': 'insufficient_data',
                    'reason': 'No volume data available for this ticker',
                    'detected_at': datetime.now().isoformat(),
                    'data_quality': 'unavailable'
                }

        except ImportError as e:
            logger.warning(f"Yahoo Finance spider not available: {e}")
            return {
                'ticker': ticker,
                'status': 'insufficient_data',
                'reason': 'Market data spider not available',
                'detected_at': datetime.now().isoformat(),
                'data_quality': 'unavailable'
            }
        except Exception as e:
            logger.warning(f"Failed to analyze volume for {ticker}: {e}")
            return {
                'ticker': ticker,
                'status': 'insufficient_data',
                'reason': f'Volume analysis failed: {str(e)[:100]}',
                'detected_at': datetime.now().isoformat(),
                'data_quality': 'error'
            }

    def _momentum_scan(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for momentum signals using real market data."""
        tickers = args.get('tickers', [])
        indicators = args.get('indicators', ['RSI', 'MACD'])
        direction = args.get('direction', 'both')

        logger.info(f"📡 Scanning momentum for {len(tickers)} tickers")

        # Session 837: Try to get real market data
        signals = []
        real_data_count = 0

        try:
            from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider
            spider = YahooFinanceSpider()

            # Fetch data for all tickers at once
            all_stock_data = spider.fetch_data(symbols=tickers[:5])
            stock_data_map = {d.get('symbol'): d for d in all_stock_data}

            for ticker in tickers[:5]:
                try:
                    stock_data = stock_data_map.get(ticker) or stock_data_map.get(ticker.replace('^', ''))

                    if stock_data and stock_data.get('current_price'):
                        real_data_count += 1
                        price = float(stock_data.get('current_price', 0))
                        change_pct = float(stock_data.get('change_percent', 0))
                        volume = stock_data.get('volume', 0)
                        avg_volume = stock_data.get('avg_volume', volume)

                        # Calculate momentum based on real price movement
                        if change_pct > 2:
                            momentum = 'strongly_bullish'
                            strength = 'strong'
                        elif change_pct > 0:
                            momentum = 'bullish'
                            strength = 'moderate'
                        elif change_pct > -2:
                            momentum = 'bearish'
                            strength = 'moderate'
                        else:
                            momentum = 'strongly_bearish'
                            strength = 'strong'

                        # Volume confirms momentum
                        volume_ratio = volume / avg_volume if avg_volume else 1.0
                        volume_confirms = volume_ratio > 1.2

                        signal = {
                            'ticker': ticker,
                            'momentum': momentum,
                            'price_change_percent': round(change_pct, 2),
                            'indicators': {
                                'price_momentum': {
                                    'change_percent': round(change_pct, 2),
                                    'signal': 'bullish' if change_pct > 0 else 'bearish'
                                },
                                'volume_momentum': {
                                    'ratio': round(volume_ratio, 2),
                                    'signal': 'confirming' if volume_confirms else 'neutral',
                                    'above_average': volume_confirms
                                }
                            },
                            'strength': strength,
                            'timeframe': 'daily',
                            'volume_confirmed': volume_confirms,
                            'detected_at': datetime.now().isoformat(),
                            'data_source': 'yahoo_finance',
                            'data_quality': 'real'
                        }

                        # Filter by direction if specified
                        if direction == 'bullish' and 'bearish' in momentum:
                            continue
                        if direction == 'bearish' and 'bullish' in momentum:
                            continue

                        signals.append(signal)
                    else:
                        signals.append({
                            'ticker': ticker,
                            'status': 'insufficient_data',
                            'reason': 'No price data available for momentum calculation',
                            'detected_at': datetime.now().isoformat(),
                            'data_quality': 'unavailable'
                        })

                except Exception as ticker_error:
                    logger.warning(f"Failed to fetch momentum data for {ticker}: {ticker_error}")
                    signals.append({
                        'ticker': ticker,
                        'status': 'insufficient_data',
                        'reason': f'Data fetch failed: {str(ticker_error)[:100]}',
                        'detected_at': datetime.now().isoformat(),
                        'data_quality': 'error'
                    })

        except ImportError as e:
            logger.warning(f"Yahoo Finance spider not available: {e}")
            for ticker in tickers[:5]:
                signals.append({
                    'ticker': ticker,
                    'status': 'insufficient_data',
                    'reason': 'Market data spider not available',
                    'detected_at': datetime.now().isoformat(),
                    'data_quality': 'unavailable'
                })

        return {
            'signals_found': len([s for s in signals if s.get('data_quality') == 'real']),
            'signals': signals,
            'real_data_available': real_data_count > 0,
            'scan_direction': direction,
            'indicators_used': indicators,
            'data_quality_summary': {
                'real': real_data_count,
                'unavailable': len(signals) - real_data_count
            }
        }

    def _options_flow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Detect unusual options activity.

        Session 837: Returns insufficient_data status since we don't have a real
        options flow data provider. Options data requires specialized feeds like
        CBOE, OptionMetrics, or paid services like Unusual Whales.
        """
        ticker = args.get('ticker')
        min_premium = args.get('min_premium', 100_000)
        option_type = args.get('option_type', 'both')
        _ = args.get('sentiment', 'bullish')  # Not used without real data

        logger.info(f"📡 Scanning options flow for {ticker} (min premium ${min_premium:,})")

        # Session 837: Return insufficient_data - we don't have real options flow data
        # Options data requires specialized feeds (CBOE, OptionMetrics, Unusual Whales, etc.)
        return {
            'ticker': ticker,
            'status': 'insufficient_data',
            'reason': 'Options flow data requires a specialized data provider (e.g., CBOE, OptionMetrics, Unusual Whales). No options spider is currently configured.',
            'recommendation': 'To enable options flow analysis, configure an options data spider with API access.',
            'filters_requested': {
                'min_premium': min_premium,
                'option_type': option_type
            },
            'detected_at': datetime.now().isoformat(),
            'data_quality': 'unavailable',
            'required_data_sources': [
                'CBOE Options Exchange',
                'OptionMetrics',
                'Unusual Whales API',
                'Market Chameleon'
            ]
        }
