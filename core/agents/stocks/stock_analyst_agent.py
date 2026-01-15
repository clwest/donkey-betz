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

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from core.agents.base_agent import BaseAgent, AgentResult
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

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute stock analysis.

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
                action="Starting stock analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            logger.info(f"StockAnalystAgent executing: {task[:100]}...")

        try:
            # Session 736: Extract spider intelligence for real-time market data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ StockAnalystAgent using spider intelligence: {len(spider_intel['trends'])} trends, market_data={bool(spider_intel['market_data'])}")

            # Session 529: Build intelligent prompt with full context
            intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            # Get relevant data from spiders
            filing_data = self._get_sec_filing_data(context.get('ticker'))
            fundamental_data = self._get_fundamental_data(context.get('ticker'))

            # Session 736: Merge spider market data if available
            if spider_intel['market_data']:
                fundamental_data = {**(fundamental_data or {}), 'spider_market_data': spider_intel['market_data']}

            # Build analysis prompt with intelligent context and spider data (Session 736)
            prompt = self._build_analysis_prompt(
                task, filing_data, fundamental_data, context,
                intelligent_context, spider_intel['summary']
            )

            # Get LLM analysis
            analysis = self._get_llm_analysis(prompt)

            # Determine severity
            severity = self._assess_severity(analysis)

            # Session 683: Run ML analysis for price trend forecasting
            ml_insights = self._analyze_price_trends_with_ml(context.get('ticker'), fundamental_data)

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
                message=f"Stock analysis complete for {context.get('ticker', 'unknown')}",
                data={
                    'analysis': analysis,
                    'severity': severity,
                    'ticker': context.get('ticker'),
                    'filing_data': filing_data,
                    'fundamental_data': fundamental_data,
                    'ml_analysis': ml_insights,  # Session 683: Add ML analysis
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
                        'ticker': context.get('ticker'),
                        'severity': severity,
                    }
                )
            except Exception as le:
                logger.warning(f"Failed to record learning outcome: {le}")

            return result

        except Exception as e:
            logger.error(f"StockAnalystAgent error: {e}")
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
