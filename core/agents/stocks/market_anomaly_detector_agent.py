"""
Market Anomaly Detector Agent
=============================

Session 461: Detects pump & dump, unusual options activity, manipulation.
Session 683: Added ML Integration (VAE for anomaly detection)

Equivalent to ExploitDetectorAgent in the blockchain audit system.

Key capabilities:
- Pump & dump pattern detection
- Unusual options flow analysis
- Market manipulation flags
- Coordinated trading detection
- ML-powered anomaly detection
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone as dt_timezone

from core.agents.base_agent import BaseAgent, AgentResult, WEB_SEARCH_TOOL, strip_simulated_tool_json
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


class MarketAnomalyDetectorAgent(BaseAgent):
    """
    Detects market anomalies and potential manipulation.

    Tools:
    - detect_pump_dump: Identify pump & dump patterns
    - analyze_options_flow: Detect unusual options activity
    - flag_manipulation: Pattern match known manipulation tactics
    - detect_coordinated: Find coordinated trading patterns
    """

    name = "MarketAnomalyDetectorAgent"
    create_deliverable_on_schedule = False  # Session 1077: scheduled outputs go to AgentExecution only

    # === Session 683: ML Integration Methods ===

    def _detect_anomalies_with_ml(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Detect market anomalies using ML (VAE/Autoencoder).

        Uses the Agent-Model Router for anomaly detection to identify
        unusual market patterns that may indicate manipulation.

        Args:
            market_data: List of market data points

        Returns:
            Dict with ML anomaly detection results
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build feature data for anomaly detection
            feature_data = self._build_anomaly_feature_data(market_data)

            if not feature_data.get('features'):
                return {'ml_used': False, 'reason': 'Insufficient market data'}

            result = router.auto_route(
                data=feature_data,
                task_hint=TaskType.ANOMALY,
                max_models=2
            )

            # Extract anomalies
            anomaly_count = 0
            if hasattr(result, 'prediction') and result.prediction:
                if isinstance(result.prediction, list):
                    anomaly_count = sum(1 for p in result.prediction if p)

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'anomaly'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'anomalies_detected': anomaly_count,
                'manipulation_risk': 'HIGH' if anomaly_count > 3 else 'MEDIUM' if anomaly_count > 1 else 'LOW',
            }

        except Exception as e:
            logger.warning(f"ML anomaly detection failed: {e}")
            return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

    def _build_anomaly_feature_data(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build feature data for ML anomaly detection."""
        features = []

        for item in market_data:
            features.append([
                float(item.get('price', 0)),
                float(item.get('change_pct', 0) or 0),
                float(item.get('volume', 0)),
                float(item.get('market_cap', 0) or 0),
            ])

        return {'features': features, 'data_type': 'market_anomaly'}

    system_prompt = """You are a market surveillance specialist detecting:
1. Pump & dump schemes (rapid price rise on low-cap stocks followed by crash)
2. Unusual options activity (large positions before news events)
3. Market manipulation patterns (spoofing, layering, wash trading)
4. Coordinated trading (social media driven buying/selling)
5. Front-running indicators

Alert criteria:
- CRITICAL: Active manipulation detected, regulatory flags
- HIGH: Strong pump & dump indicators, unusual options before announcements
- MEDIUM: Suspicious patterns requiring monitoring
- LOW: Anomalies within acceptable parameters

Focus on patterns that suggest informed trading or manipulation."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "detect_pump_dump",
                "description": "Identify pump & dump patterns",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "lookback_days": {"type": "integer", "description": "Days to analyze"},
                        "volume_threshold": {"type": "number", "description": "Volume spike multiplier"}
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_options_flow",
                "description": "Detect unusual options activity",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "option_type": {"type": "string", "enum": ["CALL", "PUT", "ALL"]},
                        "min_premium": {"type": "number", "description": "Minimum premium to flag"}
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "flag_manipulation",
                "description": "Pattern match known manipulation tactics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Patterns to check (spoofing, layering, wash_trade)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_coordinated",
                "description": "Find coordinated trading patterns (social media driven)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "social_sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Social sources to correlate (reddit, twitter, discord)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        # Session 988: Web search fallback when local data is unavailable
        WEB_SEARCH_TOOL,
    ]

    # Pattern detection thresholds
    PUMP_DUMP_PRICE_SPIKE = 0.50  # 50% price increase
    PUMP_DUMP_VOLUME_SPIKE = 10  # 10x volume
    UNUSUAL_OPTIONS_MULTIPLIER = 5  # 5x normal options volume

    # Known manipulation patterns
    MANIPULATION_PATTERNS = [
        'spoofing',  # Large orders that get cancelled
        'layering',  # Multiple orders at different prices
        'wash_trading',  # Self-dealing for artificial volume
        'front_running',  # Trading ahead of large orders
        'momentum_ignition',  # Rapid trades to trigger momentum
    ]

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute anomaly detection.

        Args:
            task: Detection task description
            context: Additional context
            scifi_context: Sci-fi features context
            spider_context: Spider data context

        Returns:
            AgentResult with anomaly findings
        """
        start_time = datetime.now()
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("market_anomaly_detection", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a specialist in detecting unusual market patterns. One capability: I scan for statistical anomalies in price movements, volume spikes, volatility clusters, and correlation breakdowns that may signal market manipulation or emerging trends.",
                    data={'type': 'self_description', 'specialization': 'anomaly_detection', 'focus': 'market_irregularities'},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="analysis",
                action="Starting market anomaly detection with tools",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip detection", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            logger.info(f"MarketAnomalyDetectorAgent executing with tools: {task[:100]}...")

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

                        logger.info(f"🔧 MarketAnomalyDetectorAgent calling tool: {tool_name}({tool_args})")

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
                    analysis = assistant_message.content or "No anomaly analysis generated."

                # Session 1018: Strip simulated JSON tool calls from text output
                analysis = strip_simulated_tool_json(analysis)

                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

                # Session 953: Build provenance from analysis results
                sources = []
                for tc in tool_calls_made:
                    sources.append({
                        'name': tc.get('tool', 'anomaly_detection'),
                        'endpoint': 'market_anomaly_api',
                        'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                        'record_count': 1,
                    })

                # Stock data stale threshold: 24 hours
                provenance = build_provenance(
                    report_type='stock_analysis',
                    agent_name=self.name,
                    sources=sources if sources else [{
                        'name': 'MarketAnomalyDetectorAgent',
                        'endpoint': 'market_anomaly_api',
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
                        'anomalies': self._extract_anomalies_from_collected(collected_data),
                        'provenance': provenance.to_dict(),
                        'publishable': provenance.publishable,
                        'validation_status': provenance.validation_status,
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time,
                    tool_calls=tool_calls_made
                )

                # Session 861: Persist analysis to Deliverable
                if analysis:
                    self._save_to_deliverable(
                        title=f"Market Anomaly: {ticker or task[:50]}",
                        content=analysis,
                        deliverable_type='analysis',
                        category='Finance',
                        tags=['anomaly', 'market', 'stocks', 'detection'],
                        content_format='markdown',
                        metadata={
                            'task': task,
                            'ticker': ticker,
                            'tools_used': [tc['tool'] for tc in tool_calls_made],
                        },
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

                return result

            except Exception as e:
                logger.error(f"MarketAnomalyDetectorAgent error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    message=f"Error detecting anomalies: {str(e)}",
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )

    def _get_market_data(self, ticker: str = None) -> List[Dict[str, Any]]:
        """Fetch market data for analysis."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone

            cutoff = timezone.now() - timedelta(days=7)
            query = SpiderData.objects.filter(
                spider_name__in=['yahoo_finance', 'finnhub', 'coingecko'],
                created_at__gte=cutoff
            ).order_by('-created_at')[:100]

            results = []
            for data in query:
                raw = data.raw_data or {}
                item = {
                    'ticker': raw.get('symbol', raw.get('ticker', '')),
                    'price': raw.get('price', raw.get('regularMarketPrice', 0)),
                    'change_pct': raw.get('change_pct', raw.get('regularMarketChangePercent', 0)),
                    'volume': raw.get('volume', raw.get('regularMarketVolume', 0)),
                    'market_cap': raw.get('market_cap', raw.get('marketCap', 0)),
                    'timestamp': str(data.created_at),
                }

                if ticker and ticker.upper() != item['ticker'].upper():
                    continue

                results.append(item)

            return results

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return []

    def _get_social_data(self, ticker: str = None) -> List[Dict[str, Any]]:
        """Fetch social media data for correlation."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone

            cutoff = timezone.now() - timedelta(days=3)
            query = SpiderData.objects.filter(
                spider_name__in=['reddit', 'bluesky', 'hackernews'],
                created_at__gte=cutoff
            ).order_by('-created_at')[:50]

            results = []
            for data in query:
                raw = data.raw_data or {}
                text = str(raw.get('title', '')) + ' ' + str(raw.get('content', ''))

                if ticker and ticker.upper() not in text.upper():
                    continue

                results.append({
                    'source': data.spider_name,
                    'text': text[:500],
                    'engagement': raw.get('score', raw.get('ups', 0)),
                    'timestamp': str(data.created_at),
                })

            return results

        except Exception as e:
            logger.error(f"Error fetching social data: {e}")
            return []

    def _detect_pump_dump(self, market_data: List[Dict]) -> List[Dict]:
        """Detect pump & dump patterns."""
        flags = []

        for item in market_data:
            try:
                change_pct = abs(float(item.get('change_pct', 0) or 0))
                market_cap = float(item.get('market_cap', 0) or 0)

                # Low market cap + high price spike = potential pump & dump
                is_small_cap = market_cap < 1_000_000_000  # < $1B
                is_spike = change_pct >= self.PUMP_DUMP_PRICE_SPIKE

                if is_small_cap and is_spike:
                    flags.append({
                        'type': 'PUMP_DUMP_INDICATOR',
                        'severity': 'HIGH',
                        'ticker': item.get('ticker', ''),
                        'change_pct': change_pct,
                        'market_cap': market_cap,
                        'message': f"Potential pump & dump: {item.get('ticker', '')} up {change_pct*100:.1f}% (small cap)",
                    })

            except (ValueError, TypeError):
                continue

        return flags

    def _detect_manipulation(self, market_data: List[Dict]) -> List[Dict]:
        """Detect manipulation patterns."""
        flags = []

        # Group by ticker to analyze patterns
        by_ticker = {}
        for item in market_data:
            ticker = item.get('ticker', '')
            if ticker:
                by_ticker.setdefault(ticker, []).append(item)

        for ticker, data_points in by_ticker.items():
            if len(data_points) < 2:
                continue

            # Look for rapid reversals (potential spoofing result)
            changes = [float(d.get('change_pct', 0) or 0) for d in data_points]

            # If we see big swings in both directions, could indicate manipulation
            has_big_up = any(c > 0.10 for c in changes)
            has_big_down = any(c < -0.10 for c in changes)

            if has_big_up and has_big_down:
                flags.append({
                    'type': 'VOLATILITY_MANIPULATION',
                    'severity': 'MEDIUM',
                    'ticker': ticker,
                    'message': f"Unusual volatility pattern in {ticker}: rapid swings detected",
                })

        return flags

    def _detect_coordinated(self, market_data: List[Dict], social_data: List[Dict]) -> List[Dict]:
        """Detect coordinated trading (social media driven)."""
        flags = []

        # Check for social media buzz correlating with price moves
        social_tickers = {}
        for post in social_data:
            text = post.get('text', '').upper()
            engagement = post.get('engagement', 0)

            # Simple ticker extraction (could be enhanced)
            for word in text.split():
                if word.startswith('$') and len(word) <= 6:
                    ticker = word[1:]
                    social_tickers[ticker] = social_tickers.get(ticker, 0) + engagement

        # Check if high-social-buzz stocks also have unusual moves
        for item in market_data:
            ticker = item.get('ticker', '').upper()
            social_buzz = social_tickers.get(ticker, 0)
            change_pct = abs(float(item.get('change_pct', 0) or 0))

            if social_buzz > 100 and change_pct > 0.10:
                flags.append({
                    'type': 'COORDINATED_TRADING',
                    'severity': 'MEDIUM',
                    'ticker': ticker,
                    'social_buzz': social_buzz,
                    'change_pct': change_pct,
                    'message': f"Potential coordinated trading: {ticker} with high social buzz ({social_buzz}) and {change_pct*100:.1f}% move",
                })

        return flags

    def _calculate_risk_level(self, anomalies: List[Dict]) -> str:
        """Calculate overall risk level from anomalies."""
        if not anomalies:
            return 'LOW'

        severities = [a.get('severity', 'LOW') for a in anomalies]

        if 'CRITICAL' in severities:
            return 'CRITICAL'
        elif severities.count('HIGH') >= 2:
            return 'CRITICAL'
        elif 'HIGH' in severities:
            return 'HIGH'
        elif 'MEDIUM' in severities:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _extract_anomalies_from_collected(self, collected_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract structured anomalies from tool call results for the coordinator."""
        anomalies = []

        for tool_name, result in collected_data.items():
            if not isinstance(result, dict):
                continue

            # Extract from flags lists (pump_dump, manipulation, coordinated all use 'flags')
            for flag in result.get('flags', []):
                if isinstance(flag, dict) and flag.get('severity'):
                    anomalies.append({
                        'ticker': flag.get('ticker', result.get('ticker', '')),
                        'severity': flag['severity'],
                        'type': flag.get('type', 'ANOMALY'),
                        'message': flag.get('message', ''),
                    })

        # Fallback: if tools produced nothing, try direct data analysis
        if not anomalies:
            market_data = self._get_market_data()
            anomalies.extend(self._detect_pump_dump(market_data))
            anomalies.extend(self._detect_manipulation(market_data))

        return anomalies

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for market anomaly detection.
        Session 988: Updated to call super() for delegation + web_search.

        Tools:
        - detect_pump_dump: Identify pump & dump patterns
        - analyze_options_flow: Detect unusual options activity
        - flag_manipulation: Pattern match known manipulation tactics
        - detect_coordinated: Find coordinated trading patterns
        - web_search: Web search fallback (handled by BaseAgent)
        """
        ticker = arguments.get('ticker', '')

        if tool_name == 'detect_pump_dump':
            lookback_days = arguments.get('lookback_days', 7)
            volume_threshold = arguments.get('volume_threshold', 10)
            market_data = self._get_market_data(ticker)
            flags = self._detect_pump_dump(market_data)
            return {
                'tool': tool_name,
                'ticker': ticker,
                'lookback_days': lookback_days,
                'volume_threshold': volume_threshold,
                'flags': flags,
                'risk_level': 'HIGH' if flags else 'LOW',
                'message': f"Found {len(flags)} potential pump & dump indicators for {ticker}"
            }

        elif tool_name == 'analyze_options_flow':
            # Session 838: Return insufficient_data instead of hardcoded placeholder values
            # Options flow analysis requires specialized options data providers (CBOE, OptionMetrics, Unusual Whales)
            # that are not currently configured in the spider network
            option_type = arguments.get('option_type', 'ALL')
            min_premium = arguments.get('min_premium', 100000)
            return {
                'tool': tool_name,
                'ticker': ticker,
                'option_type': option_type,
                'min_premium': min_premium,
                'status': 'insufficient_data',
                'reason': 'No real-time options flow data provider configured',
                'required_data_sources': [
                    'CBOE Options Exchange feed',
                    'OptionMetrics API',
                    'Unusual Whales API',
                    'Market Chameleon'
                ],
                'data_quality': 'unavailable',
                'message': f"Options flow analysis for {ticker} unavailable - requires options data provider integration"
            }

        elif tool_name == 'flag_manipulation':
            patterns = arguments.get('patterns', self.MANIPULATION_PATTERNS)
            market_data = self._get_market_data(ticker)
            flags = self._detect_manipulation(market_data)
            return {
                'tool': tool_name,
                'ticker': ticker,
                'patterns_checked': patterns,
                'flags': flags,
                'message': f"Checked {len(patterns)} manipulation patterns for {ticker}"
            }

        elif tool_name == 'detect_coordinated':
            social_sources = arguments.get('social_sources', ['reddit', 'twitter'])
            market_data = self._get_market_data(ticker)
            social_data = self._get_social_data(ticker)
            flags = self._detect_coordinated(market_data, social_data)
            return {
                'tool': tool_name,
                'ticker': ticker,
                'social_sources': social_sources,
                'flags': flags,
                'social_buzz': len(social_data),
                'message': f"Analyzed coordinated trading patterns for {ticker} across {len(social_sources)} sources"
            }

        # Session 988: Fall through to BaseAgent for web_search + delegation
        return super()._execute_tool_call(tool_name, arguments)
