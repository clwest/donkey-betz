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
from datetime import datetime, timedelta

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

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
                from openai import OpenAI
                client = OpenAI()

                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    tools=self.tools,
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

                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

                result = AgentResult(
                    success=True,
                    message=analysis,
                    data={
                        'analysis': analysis,
                        'ticker': ticker,
                        'tool_calls': tool_calls_made,
                        'collected_data': collected_data,
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

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for institutional activity monitoring.

        Tools:
        - monitor_insiders: Track Form 4 insider transactions
        - track_13f_filings: Monitor institutional 13F filings
        - alert_large_position: Detect significant position changes
        - analyze_sentiment: Analyze insider buying/selling patterns
        """
        # Session 744: Handle delegation tool
        if tool_name == 'delegate_to_specialist':
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )

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

        return {'error': f'Unknown tool: {tool_name}'}
