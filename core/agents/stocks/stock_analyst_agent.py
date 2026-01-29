"""
Stock Analyst Agent
===================

Session 461: Analyzes SEC filings, fundamentals, and valuations.
Session 683: Added ML Integration (LSTM for price trend forecasting)

Equivalent to SmartContractAuditorAgent in the blockchain audit system.

Key capabilities:
- SEC filing analysis (10-K, 10-Q, 8-K)
- Fundamental analysis (P/E, debt ratios, cash flow)
- Peer comparison
- Risk assessment
- ML-powered price trend forecasting (LSTM/Prophet) - Session 683
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_stock_with_ml(stock_data: dict) -> dict:
    """Analyze stock data using ML models (LSTM for time series)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=stock_data,
            task_hint=TaskType.TIME_SERIES,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'time_series'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'price_prediction': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML stock analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class StockAnalystAgent(BaseAgent):
    """
    Analyzes stocks using SEC filings and fundamental data.

    Tools:
    - analyze_filing: Deep dive into SEC filings
    - check_valuation: P/E, P/B, DCF analysis
    - compare_peers: Industry peer comparison
    - assess_risk: Overall risk assessment
    """

    name = "StockAnalystAgent"

    system_prompt = """You are a professional stock analyst with expertise in:
1. SEC filing analysis (10-K, 10-Q, 8-K forms)
2. Fundamental analysis (financial ratios, cash flow, margins)
3. Competitive analysis and peer comparison
4. Risk assessment and red flag detection

When analyzing stocks:
- Focus on material information and changes
- Look for discrepancies between filings and press releases
- Identify accounting red flags
- Compare metrics to industry averages
- Provide actionable insights with severity ratings

Alert on:
- CRITICAL: Accounting irregularities, going concern warnings
- HIGH: Significant revenue/margin declines, debt covenant breaches
- MEDIUM: Below-average performance vs peers
- LOW: Minor metric changes, informational updates"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_filing",
                "description": "Deep analysis of an SEC filing (10-K, 10-Q, 8-K)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "filing_type": {"type": "string", "enum": ["10-K", "10-Q", "8-K"]},
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas to analyze (revenue, debt, risks, etc.)"
                        }
                    },
                    "required": ["ticker", "filing_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_valuation",
                "description": "Analyze stock valuation using multiple metrics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Valuation metrics (P/E, P/B, EV/EBITDA, DCF)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "compare_peers",
                "description": "Compare stock to industry peers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "peer_tickers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Peer company tickers for comparison"
                        },
                        "comparison_metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to compare"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "assess_risk",
                "description": "Comprehensive risk assessment for a stock",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "risk_categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Risk areas (financial, operational, market, regulatory)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        }
    ]

    # Session 763: Mission Control configuration
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='insight',
        default_urgency='medium',
        min_confidence=0.0,
        actions=[
            {'id': 'review', 'label': 'Review Analysis', 'style': 'primary', 'description': 'Mark as reviewed'},
            {'id': 'set_alert', 'label': 'Set Alert', 'style': 'warning', 'description': 'Create price/event alert'},
            {'id': 'watchlist', 'label': 'Add to Watchlist', 'style': 'success', 'description': 'Track this stock'},
            {'id': 'dismiss', 'label': 'Dismiss', 'style': 'secondary', 'description': 'Not relevant'},
        ],
        payload_fields=['ticker', 'severity', 'analysis'],
        max_items_per_hour=5
    )

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute stock analysis using LLM with tools.

        Session 761: Rewritten to actually use tools with LLM instead of
        direct method calls. The LLM decides which tools to use based on
        the task, executes them, and synthesizes the results.

        Args:
            task: Analysis task description
            context: Additional context (ticker, filing data, etc.)
            scifi_context: Sci-fi features context (mood, memory, etc.)
            spider_context: Spider data context

        Returns:
            AgentResult with analysis findings
        """
        start_time = datetime.now()
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 858: Extract user context for personalized financial analysis
        user_context = context.get('user', {})
        self._user_context = user_context

        # Session 858: Enhance task with user's risk tolerance and investment goals
        if user_context and user_context.get('has_user_context'):
            user_name = user_context.get('name', '')
            risk_tolerance = user_context.get('risk_tolerance', 'moderate')
            goals = user_context.get('goals', [])

            # Build user context addition to task
            user_context_parts = []
            if user_name:
                user_context_parts.append(f"Analyzing for: {user_name}")
            if risk_tolerance:
                user_context_parts.append(f"Risk tolerance: {risk_tolerance}")
            if goals:
                goals_text = ", ".join(goals[:3]) if isinstance(goals, list) else str(goals)
                user_context_parts.append(f"Investment goals: {goals_text}")

            if user_context_parts:
                task = f"{task}\n\n[Investor Profile: {'; '.join(user_context_parts)}]"
                logger.info(f"📈 Session 858: Enhanced stock analysis with user profile for {user_name or 'user'}")

        # Session 750: Time Travel integration
        with self.time_travel_session("stock_analysis", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a comprehensive stock analysis specialist. One capability: I analyze SEC filings, earnings reports, and financial statements to produce detailed fundamental analysis with valuation metrics and investment recommendations.",
                    data={'type': 'self_description', 'specialization': 'fundamental_analysis', 'focus': 'valuation'},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="analysis",
                action="Starting stock analysis with tools",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            logger.info(f"StockAnalystAgent executing with tools: {task[:100]}...")

        try:
            # Session 736: Extract spider intelligence for real-time market data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ StockAnalystAgent using spider intelligence")

            # Build intelligent prompt with full context
            intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            # Session 761: Build messages for tool-enabled LLM call
            ticker = context.get('ticker', '')
            ticker_context = f"\n\nTarget ticker: {ticker}" if ticker else ""
            spider_summary = f"\n\nSpider Intelligence: {spider_intel['summary']}" if spider_intel['summary'] else ""

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

                    logger.info(f"🔧 StockAnalystAgent calling tool: {tool_name}({tool_args})")

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
                        "content": json.dumps(tool_result)[:8000]  # Truncate for context limits
                    })

                # Get final synthesis from LLM
                final_response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    max_completion_tokens=3000
                )
                analysis = final_response.choices[0].message.content
            else:
                analysis = assistant_message.content or "No analysis generated."

            # Determine severity
            severity = self._assess_severity(analysis)

            # Session 683: Run ML analysis for price trend forecasting
            ml_insights = self._analyze_price_trends_with_ml(ticker, collected_data)

            # Enhance analysis with ML insights
            if ml_insights.get('ml_used'):
                ml_summary = f"\n\n**ML Price Analysis (LSTM/Prophet):**\n"
                ml_summary += f"- Models Used: {', '.join(ml_insights['models_used'])}\n"
                ml_summary += f"- Confidence: {ml_insights['confidence']}\n"
                if ml_insights.get('ml_insights'):
                    ml_summary += f"- Trend Forecast: {ml_insights['ml_insights']}\n"
                analysis += ml_summary

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            result = AgentResult(
                success=True,
                message=analysis,
                data={
                    'analysis': analysis,
                    'severity': severity,
                    'ticker': ticker,
                    'tool_calls': tool_calls_made,  # Session 761: Include tool calls
                    'collected_data': collected_data,
                    'ml_analysis': ml_insights,
                },
                agent_name=self.name,
                execution_time_ms=execution_time,
                tool_calls=tool_calls_made  # Session 761: Add to result
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
                        'ticker': ticker,
                        'severity': severity,
                        'tools_used': [tc['tool'] for tc in tool_calls_made],
                    }
                )
            except Exception as le:
                logger.warning(f"Failed to record learning outcome: {le}")

            # Session 763: Create Mission Control attention item
            self._maybe_create_attention_item(result, task, context)

            # Session 861: Persist analysis to Deliverable
            self._save_to_deliverable(
                title=f"Stock Analysis: {ticker}" if ticker else f"Stock Analysis: {task[:60]}",
                content=analysis,
                deliverable_type='analysis',
                category='Finance',
                tags=['stock', 'analysis', ticker] if ticker else ['stock', 'analysis'],
                content_format='markdown',
                metadata={
                    'ticker': ticker,
                    'severity': severity,
                    'tools_used': [tc['tool'] for tc in tool_calls_made],
                    'ml_used': ml_insights.get('ml_used', False),
                },
            )

            return result

        except Exception as e:
            logger.error(f"StockAnalystAgent error: {e}", exc_info=True)
            result = AgentResult(
                success=False,
                message=f"Error analyzing stock: {str(e)}",
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

    def _get_sec_filing_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch SEC filing data from spider network."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone

            cutoff = timezone.now() - timedelta(days=7)
            filings = SpiderData.objects.filter(
                spider_name='sec_edgar',
                created_at__gte=cutoff
            ).order_by('-created_at')[:10]

            results = []
            for filing in filings:
                raw = filing.raw_data or {}
                if ticker and ticker.upper() in str(raw).upper():
                    results.append({
                        'title': raw.get('title', raw.get('company', '')),
                        'form_type': raw.get('form_type', ''),
                        'filed_at': raw.get('filed_at', ''),
                        'url': raw.get('url', ''),
                    })

            return {'filings': results, 'count': len(results)}

        except Exception as e:
            logger.error(f"Error fetching SEC data: {e}")
            return {'filings': [], 'count': 0, 'error': str(e)}

    def _get_fundamental_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch fundamental data from spider network."""
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone

            cutoff = timezone.now() - timedelta(days=1)
            data = SpiderData.objects.filter(
                spider_name='yahoo_finance',
                created_at__gte=cutoff
            ).order_by('-created_at').first()

            if data and data.raw_data:
                return data.raw_data
            return {}

        except Exception as e:
            logger.error(f"Error fetching fundamental data: {e}")
            return {'error': str(e)}

    def _build_analysis_prompt(self, task: str, filing_data: Dict,
                                fundamental_data: Dict, context: Dict,
                                intelligent_context: str = "",
                                spider_summary: str = "") -> str:
        """Build the analysis prompt with intelligent context."""
        # Session 529: Include intelligent context for memory, mood, and platform awareness
        # Session 736: Include spider intelligence summary
        spider_section = ""
        if spider_summary:
            spider_section = f"""
REAL-TIME MARKET INTELLIGENCE (Spider Network):
{spider_summary}
"""

        prompt = f"""{intelligent_context}

Analyze the following stock data:

TASK: {task}

TICKER: {context.get('ticker', 'Not specified')}
{spider_section}
SEC FILINGS:
{filing_data}

FUNDAMENTAL DATA:
{fundamental_data}

Provide:
1. Key findings from filings
2. Fundamental analysis
3. Risk factors identified
4. Overall assessment with severity (CRITICAL/HIGH/MEDIUM/LOW)
5. Recommended actions
"""
        return prompt

    def _get_llm_analysis(self, prompt: str) -> str:
        """Get LLM analysis."""
        try:
            from openai import OpenAI
            import os

            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
            # Session 494: Use gpt-5-mini (reasoning model)
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=6000  # Reasoning model needs more tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return f"Analysis error: {e}"

    def _assess_severity(self, analysis: str) -> str:
        """Determine severity from analysis."""
        analysis_lower = analysis.lower()

        if any(word in analysis_lower for word in ['critical', 'fraud', 'material misstatement', 'going concern']):
            return 'CRITICAL'
        elif any(word in analysis_lower for word in ['high', 'significant decline', 'covenant breach', 'warning']):
            return 'HIGH'
        elif any(word in analysis_lower for word in ['medium', 'below average', 'concerning']):
            return 'MEDIUM'
        else:
            return 'LOW'

    # =========================================================================
    # SESSION 683: ML INTEGRATION - LSTM FOR PRICE TREND FORECASTING
    # =========================================================================

    def _analyze_price_trends_with_ml(self, ticker: str, fundamental_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use ML models to analyze price trends and forecast future movements.

        Session 683: Integrates the Agent-Model Router to auto-select LSTM/Prophet
        for time series price analysis.
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            # Build time series data from price history
            time_series_data = self._build_price_time_series(ticker, fundamental_data)

            if not time_series_data.get('timestamp') or len(time_series_data['timestamp']) < 5:
                return {
                    'ml_used': False,
                    'reason': 'Insufficient price history for time series analysis'
                }

            # Get router and run auto-selection (should select LSTM/Prophet for time series)
            router = get_agent_model_router()
            result = router.auto_route(time_series_data, max_models=2)

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'unknown'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'selection_reason': result.auto_selection.get('selection_reason', ''),
                'data_points': len(time_series_data.get('timestamp', [])),
                'score': round(result.score, 4) if result.score else None,
            }

        except ImportError as e:
            logger.warning(f"ML router not available: {e}")
            return {'ml_used': False, 'reason': f'ML not available: {e}'}
        except Exception as e:
            logger.warning(f"ML analysis error: {e}")
            return {'ml_used': False, 'reason': f'ML error: {e}'}

    def _build_price_time_series(self, ticker: str, fundamental_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build time series data from price history.

        Extracts timestamp and price data suitable for LSTM/Prophet analysis.
        """
        timestamps = []
        prices = []

        # Try to extract from fundamental_data
        if isinstance(fundamental_data, dict):
            # Check for historical price data
            price_history = fundamental_data.get('price_history', [])
            if price_history:
                for entry in price_history:
                    if isinstance(entry, dict):
                        ts = entry.get('timestamp') or entry.get('date')
                        price = entry.get('price') or entry.get('close')
                        if ts and price:
                            timestamps.append(str(ts))
                            prices.append(float(price))

            # Or check for recent prices
            recent_prices = fundamental_data.get('recent_prices', [])
            if recent_prices and not prices:
                for i, price in enumerate(recent_prices):
                    timestamps.append(f"T-{len(recent_prices) - i}")
                    prices.append(float(price))

        # If no data found, try to get from spider network
        if not prices:
            try:
                from core.models_unified_system import SpiderData
                from django.utils import timezone

                cutoff = timezone.now() - timedelta(days=30)
                data = SpiderData.objects.filter(
                    spider_name__in=['yahoo_finance', 'polygon_spider'],
                    created_at__gte=cutoff
                ).order_by('-created_at')[:30]

                for entry in data:
                    raw = entry.raw_data or {}
                    if ticker and ticker.upper() in str(raw).upper():
                        price = raw.get('current_price') or raw.get('price')
                        if price:
                            timestamps.append(str(entry.created_at.date()))
                            prices.append(float(price))

            except Exception as e:
                logger.warning(f"Error fetching price history: {e}")

        return {
            'timestamp': timestamps,
            'price': prices,
            'ticker': ticker
        }

    # =========================================================================
    # SESSION 761: TOOL EXECUTION - Wire up defined tools
    # =========================================================================

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for stock analysis.

        Tools: analyze_filing, check_valuation, compare_peers, assess_risk
        """
        # First check if base class handles it (delegation)
        try:
            return super()._execute_tool_call(tool_name, arguments)
        except NotImplementedError:
            pass

        ticker = arguments.get('ticker', '')

        if tool_name == 'analyze_filing':
            filing_type = arguments.get('filing_type', '10-K')
            focus_areas = arguments.get('focus_areas', [])
            filing_data = self._get_sec_filing_data(ticker)
            return {
                'success': True,
                'ticker': ticker,
                'filing_type': filing_type,
                'focus_areas': focus_areas,
                'filing_data': filing_data,
                'analysis': f"SEC {filing_type} analysis for {ticker}"
            }

        elif tool_name == 'check_valuation':
            metrics = arguments.get('metrics', ['P/E', 'P/B', 'EV/EBITDA'])
            fundamental_data = self._get_fundamental_data(ticker)
            return {
                'success': True,
                'ticker': ticker,
                'metrics': metrics,
                'valuation_data': fundamental_data,
                'analysis': f"Valuation analysis for {ticker} using {', '.join(metrics)}"
            }

        elif tool_name == 'compare_peers':
            peer_tickers = arguments.get('peer_tickers', [])
            comparison_metrics = arguments.get('comparison_metrics', ['P/E', 'Revenue Growth'])
            return {
                'success': True,
                'ticker': ticker,
                'peers': peer_tickers,
                'metrics': comparison_metrics,
                'analysis': f"Peer comparison for {ticker} vs {', '.join(peer_tickers) if peer_tickers else 'industry'}"
            }

        elif tool_name == 'assess_risk':
            risk_categories = arguments.get('risk_categories', ['financial', 'operational', 'market'])
            return {
                'success': True,
                'ticker': ticker,
                'risk_categories': risk_categories,
                'analysis': f"Risk assessment for {ticker} covering {', '.join(risk_categories)}"
            }

        elif tool_name == "delegate_to_specialist":
            # Session 833: Handle delegation properly
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )
        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
            }
