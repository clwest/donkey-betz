"""
Stock Analyst Agent
===================

Session 461: Analyzes SEC filings, fundamentals, and valuations.
Equivalent to SmartContractAuditorAgent in the blockchain audit system.

Key capabilities:
- SEC filing analysis (10-K, 10-Q, 8-K)
- Fundamental analysis (P/E, debt ratios, cash flow)
- Peer comparison
- Risk assessment
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


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

        logger.info(f"StockAnalystAgent executing: {task[:100]}...")

        try:
            # Session 529: Build intelligent prompt with full context
            intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            # Get relevant data from spiders
            filing_data = self._get_sec_filing_data(context.get('ticker'))
            fundamental_data = self._get_fundamental_data(context.get('ticker'))

            # Build analysis prompt with intelligent context
            prompt = self._build_analysis_prompt(task, filing_data, fundamental_data, context, intelligent_context)

            # Get LLM analysis
            analysis = self._get_llm_analysis(prompt)

            # Determine severity
            severity = self._assess_severity(analysis)

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
                                intelligent_context: str = "") -> str:
        """Build the analysis prompt with intelligent context."""
        # Session 529: Include intelligent context for memory, mood, and platform awareness
        prompt = f"""{intelligent_context}

Analyze the following stock data:

TASK: {task}

TICKER: {context.get('ticker', 'Not specified')}

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
