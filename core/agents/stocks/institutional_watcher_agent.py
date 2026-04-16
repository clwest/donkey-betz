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

import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone as dt_timezone

from core.agents.base_agent import BaseAgent, AgentResult, WEB_SEARCH_TOOL, strip_simulated_tool_json
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


def analyze_institutional_with_ml(position_data: dict) -> dict:
    """Analyze institutional positions using ML models (GNN + Anomaly)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=position_data,
            task_hint=TaskType.GRAPH,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'graph'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'position_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML institutional analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


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
    create_deliverable_on_schedule = True  # Fixed: was False (Session 1077), outputs were lost in AgentExecution

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
        },
        # Session 988: Web search fallback when local data is unavailable
        WEB_SEARCH_TOOL,
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
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("institutional_watching", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a specialist in tracking institutional investor activity in stocks. One capability: I monitor SEC filings, 13F reports, and insider trading to detect when hedge funds and major institutions are accumulating or distributing positions.",
                    data={'type': 'self_description', 'specialization': 'institutional_activity', 'focus': 'smart_money_tracking'},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="analysis",
                action="Starting institutional watching with tools",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip watching", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            logger.info(f"InstitutionalWatcherAgent executing with tools: {task[:100]}...")

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
                client = get_openai_client()

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

                        logger.info(f"🔧 InstitutionalWatcherAgent calling tool: {tool_name}({tool_args})")

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
                    analysis = assistant_message.content or "No institutional analysis generated."

                # Session 1018: Strip simulated JSON tool calls from text output
                analysis = strip_simulated_tool_json(analysis)

                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

                # Session 953: Build provenance from analysis results
                sources = []
                for tc in tool_calls_made:
                    sources.append({
                        'name': tc.get('tool', 'institutional_analysis'),
                        'endpoint': 'sec_filings',
                        'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                        'record_count': 1,
                    })

                # Stock data stale threshold: 24 hours
                provenance = build_provenance(
                    report_type='stock_analysis',
                    agent_name=self.name,
                    sources=sources if sources else [{
                        'name': 'InstitutionalWatcherAgent',
                        'endpoint': 'sec_filings',
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
                        'alerts': self._extract_institutional_alerts(collected_data),
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
                    title=f"Institutional Activity: {task[:80]}",
                    content=result.message,
                    deliverable_type='analysis',
                    category='Institutional Analysis',
                    tags=['institutional', 'stocks'],
                    metadata={'task': task[:200]},
                )

                return result

            except Exception as e:
                logger.error(f"InstitutionalWatcherAgent error: {e}", exc_info=True)
                result = AgentResult(
                    success=False,
                    message=f"Error watching institutions: {str(e)}",
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
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
                spider_name__in=['sec', 'sec_edgar'],
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
        """
        Calculate overall insider sentiment from transaction data.

        Session 838: Replaced hardcoded discrete scores with continuous scoring
        based on both transaction count and value weighting.
        """
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
        total_value = buy_value + sell_value

        if total == 0:
            return {
                'sentiment': 'NEUTRAL',
                'score': 50,
                'description': 'No insider activity detected',
                'data_quality': 'unavailable',
                'transactions': {'buys': 0, 'sells': 0},
                'values': {'buy_value': 0, 'sell_value': 0}
            }

        # Session 838: Calculate continuous score based on both count and value
        # Count-based component (0-100 scale)
        buy_pct = buys / total
        count_score = buy_pct * 100  # 0 = all sells, 100 = all buys

        # Value-based component (0-100 scale, weighted by transaction value)
        if total_value > 0:
            value_score = (buy_value / total_value) * 100
            # Blend count and value scores (value is weighted more for large transactions)
            blended_score = (count_score * 0.4) + (value_score * 0.6)
        else:
            blended_score = count_score

        # Round to nearest integer
        score = round(blended_score)

        # Determine sentiment label based on continuous score
        if score >= 75:
            sentiment = 'STRONGLY_BULLISH'
            description = f'Heavy insider buying ({buys} buys, ${buy_value:,.0f} value)'
        elif score >= 60:
            sentiment = 'BULLISH'
            description = f'Net insider buying ({buys} buys vs {sells} sells)'
        elif score >= 45:
            sentiment = 'NEUTRAL'
            description = f'Mixed insider activity ({buys} buys, {sells} sells)'
        elif score >= 30:
            sentiment = 'BEARISH'
            description = f'Net insider selling ({sells} sells vs {buys} buys)'
        else:
            sentiment = 'STRONGLY_BEARISH'
            description = f'Heavy insider selling ({sells} sells, ${sell_value:,.0f} value)'

        return {
            'sentiment': sentiment,
            'score': score,
            'description': description,
            'data_quality': 'real',
            'data_source': 'sec_filings',
            'transactions': {'buys': buys, 'sells': sells, 'total': total},
            'values': {
                'buy_value': round(buy_value, 2),
                'sell_value': round(sell_value, 2),
                'net_value': round(buy_value - sell_value, 2)
            },
            'ratios': {
                'buy_pct': round(buy_pct * 100, 1),
                'value_weighted_score': round(blended_score, 1)
            }
        }

    def _extract_institutional_alerts(self, collected_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract structured alerts from tool call results for the coordinator."""
        alerts = []

        for tool_name, result in collected_data.items():
            if not isinstance(result, dict):
                continue

            # Extract from insider transaction lists
            for tx in result.get('transactions', []):
                if not isinstance(tx, dict):
                    continue
                value = float(tx.get('value', 0) or 0)
                if value >= self.LARGE_TRANSACTION_VALUE:
                    tx_type = str(tx.get('transaction_type', '')).upper()
                    is_sell = 'SELL' in tx_type or 'SALE' in tx_type or 'S' == tx_type
                    alerts.append({
                        'ticker': tx.get('company', result.get('ticker', '')),
                        'severity': 'HIGH' if is_sell else 'MEDIUM',
                        'type': 'LARGE_INSIDER_TRANSACTION',
                        'message': f"{'Large insider sale' if is_sell else 'Large insider purchase'}: ${value:,.0f} by {tx.get('insider_name', 'Unknown')}",
                    })

            # Extract from large_positions lists
            for pos in result.get('large_positions', []):
                if not isinstance(pos, dict):
                    continue
                value = float(pos.get('value', 0) or 0)
                if value >= self.LARGE_TRANSACTION_VALUE:
                    alerts.append({
                        'ticker': pos.get('company', result.get('ticker', '')),
                        'severity': 'HIGH',
                        'type': 'LARGE_POSITION_CHANGE',
                        'message': f"Large position change: ${value:,.0f} at {pos.get('company', 'Unknown')}",
                    })

            # Extract sentiment-based alerts
            sentiment = result.get('sentiment', {})
            if isinstance(sentiment, dict) and sentiment.get('sentiment') in ('STRONGLY_BEARISH',):
                alerts.append({
                    'ticker': result.get('ticker', ''),
                    'severity': 'HIGH',
                    'type': 'BEARISH_INSIDER_SENTIMENT',
                    'message': sentiment.get('description', 'Heavy insider selling detected'),
                })

        # Fallback: if tools produced nothing, try direct data analysis
        if not alerts:
            insider_data = self._get_insider_data()
            patterns = self._analyze_patterns(insider_data)
            alerts = self._generate_alerts(insider_data, patterns)

        return alerts

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for institutional activity monitoring.
        Session 988: Updated to call super() for delegation + web_search.

        Tools:
        - monitor_insiders: Track Form 4 insider transactions
        - track_13f_filings: Monitor institutional 13F filings
        - alert_large_position: Detect significant position changes
        - analyze_sentiment: Analyze insider buying/selling patterns
        - web_search: Web search fallback (handled by BaseAgent)
        """
        ticker = arguments.get('ticker', '')

        if tool_name == 'monitor_insiders':
            insider_types = arguments.get('insider_types', ['CEO', 'CFO', 'Director'])
            transaction_type = arguments.get('transaction_type', 'ALL')
            insider_data = self._get_insider_data(ticker)
            return {
                'tool': tool_name,
                'ticker': ticker,
                'insider_types': insider_types,
                'transaction_type': transaction_type,
                'transactions': insider_data[:20],
                'total_count': len(insider_data),
                'message': f"Found {len(insider_data)} insider transactions for {ticker}"
            }

        elif tool_name == 'track_13f_filings':
            institution = arguments.get('institution')
            min_position_value = arguments.get('min_position_value', 1000000)
            insider_data = self._get_insider_data(ticker)
            institutional = [d for d in insider_data if '13F' in d.get('form_type', '')]
            return {
                'tool': tool_name,
                'ticker': ticker,
                'institution': institution,
                'min_position_value': min_position_value,
                'filings': institutional[:10],
                'total_count': len(institutional),
                'message': f"Found {len(institutional)} 13F filings" + (f" for {ticker}" if ticker else "")
            }

        elif tool_name == 'alert_large_position':
            change_threshold = arguments.get('change_threshold_pct', 5.0)
            insider_data = self._get_insider_data(ticker)
            large_positions = [d for d in insider_data if float(d.get('value', 0) or 0) >= self.LARGE_TRANSACTION_VALUE]
            return {
                'tool': tool_name,
                'ticker': ticker,
                'change_threshold_pct': change_threshold,
                'large_positions': large_positions[:10],
                'total_count': len(large_positions),
                'message': f"Found {len(large_positions)} large position changes for {ticker}"
            }

        elif tool_name == 'analyze_sentiment':
            lookback_days = arguments.get('lookback_days', 90)
            insider_data = self._get_insider_data(ticker)
            sentiment = self._calculate_sentiment(insider_data)
            patterns = self._analyze_patterns(insider_data)
            return {
                'tool': tool_name,
                'ticker': ticker,
                'lookback_days': lookback_days,
                'sentiment': sentiment,
                'patterns': patterns,
                'message': f"Insider sentiment for {ticker}: {sentiment['sentiment']} ({sentiment['description']})"
            }

        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)
