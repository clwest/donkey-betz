"""
Market Intelligence Agent - Clean Architecture
===============================================

Session 385: Phase 4 - Market Intelligence Integration
Session 683: Added ML Integration (GNN for market entity relationship analysis)

This agent provides comprehensive financial market intelligence by combining:
- SEC EDGAR filings (8-K, 10-K, 10-Q)
- Cryptocurrency market data (CoinGecko)
- Stock market data (Yahoo Finance)
- Financial news correlation
- ML-powered entity relationship analysis (GNN) - Session 683

Tools Available:
    - get_sec_filings: Fetch recent SEC filings with impact analysis
    - get_market_overview: Get combined crypto/stock market overview
    - analyze_filing_impact: Analyze potential market impact of SEC filings
    - get_sector_performance: Get performance data by sector
    - ML: GNN analysis for market entity relationships (auto-invoked)

Usage:
    from core.agents.analysis import MarketIntelligenceAgent

    agent = MarketIntelligenceAgent(user=request.user)
    result = agent.execute(
        task="What SEC filings should I pay attention to today?",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone as dt_timezone
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from core.agents.base_agent import BaseAgent, AgentResult, strip_simulated_tool_json
from core.agents.report_schemas import build_provenance, format_disclaimer

logger = logging.getLogger(__name__)

# Session 990: Per-call timeout for external data fetches (spider calls)
SPIDER_FETCH_TIMEOUT = 60  # 60 seconds per spider fetch


@dataclass
class MarketIntelligenceReport:
    """Result from market intelligence analysis."""
    success: bool
    report_type: str  # 'overview', 'sec_filings', 'sector', 'impact_analysis'
    generated_at: datetime

    # SEC Filings
    sec_filings: List[Dict[str, Any]] = field(default_factory=list)
    high_impact_filings: List[Dict[str, Any]] = field(default_factory=list)

    # Market Data
    crypto_summary: Dict[str, Any] = field(default_factory=dict)
    stocks_summary: Dict[str, Any] = field(default_factory=dict)

    # Analysis
    analysis: str = ""
    key_insights: List[str] = field(default_factory=list)
    market_signals: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    data_sources: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'report_type': self.report_type,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'sec_filings': {
                'all': self.sec_filings,
                'high_impact': self.high_impact_filings,
                'total': len(self.sec_filings),
                'high_impact_count': len(self.high_impact_filings),
            },
            'markets': {
                'crypto': self.crypto_summary,
                'stocks': self.stocks_summary,
            },
            'analysis': self.analysis,
            'key_insights': self.key_insights,
            'market_signals': self.market_signals,
            'metadata': {
                'data_sources': self.data_sources,
                'confidence_score': self.confidence_score,
            },
            'error': self.error,
        }


class MarketIntelligenceAgent(BaseAgent):
    """
    Market Intelligence Agent - Financial Market Analyst.

    This agent:
    1. Fetches and analyzes SEC EDGAR filings (8-K, 10-K, 10-Q)
    2. Monitors crypto and stock market movements
    3. Correlates filings with market impact
    4. Generates actionable market intelligence

    It CANNOT:
    - Execute trades
    - Create content
    - Access real-time trading APIs
    """

    name = "MarketIntelligenceAgent"

    system_prompt = """You are MarketIntelligenceAgent, the Financial Market Analyst.

Your job is to provide comprehensive market intelligence by combining multiple data sources:

DATA SOURCES:
- SEC EDGAR filings: 8-K (material events), 10-K (annual reports), 10-Q (quarterly reports)
- Cryptocurrency data: Bitcoin, Ethereum, and major altcoins via CoinGecko
- Stock market data: Major indices and stocks via Yahoo Finance
- Financial news: Market-moving news from various sources

FILING TYPES TO WATCH:
- 8-K (Material Events): Most market-moving - earnings, M&A, leadership changes, material agreements
- 10-K (Annual Report): Comprehensive yearly financials and risk factors
- 10-Q (Quarterly Report): Quarterly financial updates
- 4 (Insider Trading): Shows what executives and large holders are buying/selling
- 13F-HR (Institutional Holdings): What big funds are accumulating

When analyzing SEC filings, look for:
1. Earnings announcements (Item 2.02)
2. Material agreements (Item 1.01)
3. Leadership changes (Item 5.02)
4. M&A activity (Item 2.01)
5. Risk factors (in 10-K/10-Q)

CRITICAL GUIDELINES:
- Always provide context for why a filing matters
- Highlight high-impact filings that could move markets
- Connect filings to broader market trends when relevant
- Be objective - never recommend specific trades
- Note when data might be delayed or incomplete

Available tools:
- get_sec_filings: Fetch recent SEC EDGAR filings with impact scoring
- get_market_overview: Get combined crypto/stock market snapshot
- analyze_filing_impact: Deep analysis of a specific filing's potential impact
- search_company_filings: Search for filings by company name or CIK

You analyze and report - you do NOT give trading advice or recommendations."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_sec_filings",
                "description": "Fetch recent SEC EDGAR filings with automatic impact scoring. Returns 8-K, 10-K, and 10-Q filings.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "form_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by form types: '8-K', '10-K', '10-Q'. Default all.",
                            "default": ["8-K", "10-K", "10-Q"]
                        },
                        "high_impact_only": {
                            "type": "boolean",
                            "description": "Only return high-impact filings (earnings, M&A, leadership)",
                            "default": False
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum filings to return",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_market_overview",
                "description": "Get a comprehensive market overview including top crypto assets, major stock indices, and recent price movements.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_crypto": {
                            "type": "boolean",
                            "description": "Include cryptocurrency data",
                            "default": True
                        },
                        "include_stocks": {
                            "type": "boolean",
                            "description": "Include stock market data",
                            "default": True
                        },
                        "crypto_limit": {
                            "type": "integer",
                            "description": "Number of crypto assets to include",
                            "default": 10
                        },
                        "stock_limit": {
                            "type": "integer",
                            "description": "Number of stocks to include",
                            "default": 10
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_filing_impact",
                "description": "Analyze the potential market impact of SEC filings based on content and historical patterns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filing_type": {
                            "type": "string",
                            "description": "Type of filing to analyze",
                            "enum": ["8-K", "10-K", "10-Q"]
                        },
                        "company_name": {
                            "type": "string",
                            "description": "Company name to filter by (optional)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_company_filings",
                "description": "Search for SEC filings by company name or ticker symbol.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Company name or ticker to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute market intelligence analysis."""
        start_time = time.time()

        # Session 750: Time Travel integration
        with self.time_travel_session("market_intelligence_analysis", task, input_data=context):
            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            try:
                # Build prompt with context
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)

                # Record decision (decision_type, action, ...)
                self.record_decision(
                    "analysis",
                    f"Starting market intelligence analysis",
                    context={'task': task},
                    confidence=0.8
                )

                # Call GPT with our tools
                messages = [
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": task}
                ]

                # Session 1098: wrapped for telemetry + cancellation.
                from core.services.llm_call_wrapper import llm_call_span as _llm_call_span
                _exec_ctx = getattr(self, '_execution_context', {}) or {}
                with _llm_call_span(
                    provider='openai',
                    model='gpt-5-mini',
                    execution_id=_exec_ctx.get('execution_id'),
                    agent_name='MarketIntelligenceAgent',
                    metadata={'step': 'tool_call_plan'},
                ) as _span:
                    response = self.client.chat.completions.create(  # noqa: direct-llm-call — wrapped above
                        model="gpt-5-mini",
                        messages=messages,
                        tools=self.get_tools_with_delegation(),
                        tool_choice="auto",
                        max_completion_tokens=4000
                    )
                    _span.attach_response(response)

                # Process response
                assistant_message = response.choices[0].message
                tool_calls_made = []
                collected_data = {}

                # Handle tool calls
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                        self.record_decision(
                            "tool_call",
                            f"Calling tool: {tool_name}",
                            context={'args': tool_args},
                            confidence=0.9
                        )

                        # Execute the tool
                        tool_result = self._execute_tool(tool_name, tool_args)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'args': tool_args,
                            'result_summary': f"Got {len(tool_result.get('items', []))} items" if isinstance(tool_result, dict) else str(tool_result)[:100]
                        })
                        collected_data[tool_name] = tool_result

                        # Add tool result to conversation
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result)[:8000]  # Truncate for context limits
                        })

                    # Get final analysis from GPT
                    # Session 1098: wrapped for telemetry + cancellation.
                    with _llm_call_span(
                        provider='openai',
                        model='gpt-5-mini',
                        execution_id=_exec_ctx.get('execution_id'),
                        agent_name='MarketIntelligenceAgent',
                        metadata={'step': 'final_analysis'},
                    ) as _final_span:
                        final_response = self.client.chat.completions.create(  # noqa: direct-llm-call — wrapped above
                            model="gpt-5-mini",
                            messages=messages,
                            max_completion_tokens=3000
                        )
                        _final_span.attach_response(final_response)
                    analysis = final_response.choices[0].message.content
                else:
                    analysis = strip_simulated_tool_json(assistant_message.content)

                # Session 683: Run ML analysis on collected market data
                ml_insights = {}
                if collected_data:
                    # Combine all collected data for ML analysis
                    market_data_for_ml = {
                        'filings': collected_data.get('get_sec_filings', {}).get('filings', []),
                        'stocks': collected_data.get('get_market_overview', {}).get('stocks', {}),
                        'crypto': collected_data.get('get_market_overview', {}).get('crypto', {}),
                    }
                    ml_insights = self._analyze_with_ml(market_data_for_ml)

                    # Enhance analysis with ML insights
                    if ml_insights.get('ml_used'):
                        ml_summary = f"\n\n**ML Analysis (GNN):**\n"
                        ml_summary += f"- Models Used: {', '.join(ml_insights['models_used'])}\n"
                        ml_summary += f"- Confidence: {ml_insights['confidence']}\n"
                        ml_summary += f"- Entities Analyzed: {ml_insights['entity_count']} nodes, {ml_insights['relationship_count']} relationships\n"
                        if ml_insights.get('ml_insights'):
                            ml_summary += f"- Insights: {ml_insights['ml_insights']}\n"
                        analysis += ml_summary

                # Build result
                execution_time = int((time.time() - start_time) * 1000)

                # Session 953: Build provenance from analysis results
                sources = []
                for tc in tool_calls_made:
                    sources.append({
                        'name': tc.get('tool', 'market_intelligence'),
                        'endpoint': tc.get('args', {}).get('form_types', ['SEC_EDGAR'])[0] if tc.get('args') else 'market_data',
                        'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                        'record_count': 1,
                    })
                if not sources:
                    sources = [{
                        'name': 'market_intelligence',
                        'endpoint': 'sec_edgar',
                        'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                        'record_count': 0,
                    }]
                provenance = build_provenance(
                    report_type='financial_analysis',
                    agent_name=self.name,
                    sources=sources,
                    stale_threshold_hours=24.0,
                )
                provenance.disclaimer = format_disclaimer('financial_analysis')
                provenance_block = provenance.to_markdown_block()

                result = AgentResult(
                    success=True,
                    message=provenance_block + "\n\n" + analysis,
                    data={
                        'analysis': analysis,
                        'collected_data': collected_data,
                        'tool_calls': tool_calls_made,
                        'ml_analysis': ml_insights,  # Session 683: Add ML analysis to data
                        'provenance': provenance.to_dict(),
                        'publishable': provenance.publishable,
                        'validation_status': provenance.validation_status,
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time,
                    decisions_made=len(tool_calls_made) + 1,
                    tool_calls=tool_calls_made
                )

                # Session 861: Persist analysis to Deliverable
                if analysis:
                    self._save_to_deliverable(
                        title=f"Market Intelligence: {task[:50]}",
                        content=analysis,
                        deliverable_type='analysis',
                        category='Finance',
                        tags=['market', 'intelligence', 'finance', 'sec'],
                        content_format='markdown',
                        metadata={
                            'task': task,
                            'tools_used': [tc.get('tool') for tc in tool_calls_made],
                            'execution_time_ms': execution_time,
                        },
                    )

                # Record learning outcome with proper AgentResult
                try:
                    self._record_learning_outcome(result, task, context)
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

            except Exception as e:
                logger.exception(f"MarketIntelligenceAgent error: {e}")
                return AgentResult(
                    success=False,
                    message=f"Error analyzing markets: {str(e)}",
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a market intelligence tool."""
        if tool_name == "get_sec_filings":
            return self._get_sec_filings(
                form_types=args.get('form_types', ['8-K', '10-K', '10-Q']),
                high_impact_only=args.get('high_impact_only', False),
                limit=args.get('limit', 20)
            )
        elif tool_name == "get_market_overview":
            return self._get_market_overview(
                include_crypto=args.get('include_crypto', True),
                include_stocks=args.get('include_stocks', True),
                crypto_limit=args.get('crypto_limit', 10),
                stock_limit=args.get('stock_limit', 10)
            )
        elif tool_name == "analyze_filing_impact":
            return self._analyze_filing_impact(
                filing_type=args.get('filing_type'),
                company_name=args.get('company_name')
            )
        elif tool_name == "search_company_filings":
            return self._search_company_filings(
                query=args.get('query', ''),
                limit=args.get('limit', 10)
            )

        else:
            # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
            return super()._execute_tool_call(tool_name, args)

    def _get_sec_filings(
        self,
        form_types: List[str] = None,
        high_impact_only: bool = False,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Fetch SEC EDGAR filings."""
        try:
            from ai_core.spiders.specialized.sec_spider import SECSpider

            spider = SECSpider()
            # Session 990: Wrap spider call with timeout to prevent hangs
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(spider.fetch_data, max_results=limit * 2)
                try:
                    all_filings = future.result(timeout=SPIDER_FETCH_TIMEOUT)
                except FuturesTimeoutError:
                    logger.warning(f"SEC spider timed out after {SPIDER_FETCH_TIMEOUT}s")
                    return {'error': 'SEC data fetch timed out', 'items': [], 'filings': []}

            # Filter by form type if specified
            if form_types:
                all_filings = [f for f in all_filings if f.get('form_type') in form_types]

            # Filter high impact only
            if high_impact_only:
                all_filings = [f for f in all_filings if f.get('is_high_impact')]

            # Limit results
            filings = all_filings[:limit]

            # Separate high impact
            high_impact = [f for f in filings if f.get('is_high_impact')]

            return {
                'items': filings,
                'filings': filings,
                'high_impact': high_impact,
                'total': len(filings),
                'high_impact_count': len(high_impact),
                'source': 'sec_edgar',
                'form_types_included': list(set(f.get('form_type') for f in filings))
            }

        except Exception as e:
            logger.error(f"Error fetching SEC filings: {e}")
            return {'error': str(e), 'items': [], 'filings': []}

    def _get_market_overview(
        self,
        include_crypto: bool = True,
        include_stocks: bool = True,
        crypto_limit: int = 10,
        stock_limit: int = 10
    ) -> Dict[str, Any]:
        """Get comprehensive market overview."""
        result = {
            'crypto': {'assets': [], 'summary': {}},
            'stocks': {'assets': [], 'summary': {}},
            'timestamp': datetime.now().isoformat()
        }

        # Get crypto data from CoinGecko spider
        if include_crypto:
            try:
                from ai_core.spiders.specialized.coingecko_spider import CoinGeckoSpider
                spider = CoinGeckoSpider()
                # Session 990: Wrap with timeout — CoinGecko makes 3 sequential calls (30s each)
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(spider.fetch_data, max_results=crypto_limit)
                    try:
                        crypto_data = future.result(timeout=SPIDER_FETCH_TIMEOUT)
                    except FuturesTimeoutError:
                        logger.warning(f"CoinGecko spider timed out after {SPIDER_FETCH_TIMEOUT}s")
                        crypto_data = []

                result['crypto']['assets'] = crypto_data

                # Calculate summary
                if crypto_data:
                    btc = next((c for c in crypto_data if c.get('symbol', '').upper() == 'BTC'), None)
                    eth = next((c for c in crypto_data if c.get('symbol', '').upper() == 'ETH'), None)

                    gainers = [c for c in crypto_data if (c.get('price_change_percentage_24h') or 0) > 0]
                    losers = [c for c in crypto_data if (c.get('price_change_percentage_24h') or 0) < 0]

                    result['crypto']['summary'] = {
                        'btc_price': btc.get('current_price') if btc else None,
                        'btc_change': btc.get('price_change_percentage_24h') if btc else None,
                        'eth_price': eth.get('current_price') if eth else None,
                        'eth_change': eth.get('price_change_percentage_24h') if eth else None,
                        'gainers_count': len(gainers),
                        'losers_count': len(losers),
                        'market_sentiment': 'bullish' if len(gainers) > len(losers) else 'bearish'
                    }
            except Exception as e:
                logger.warning(f"Error fetching crypto data: {e}")
                result['crypto']['error'] = str(e)

        # Get stock data from Yahoo Finance spider
        if include_stocks:
            try:
                from ai_core.spiders.specialized.yahoo_finance_spider import YahooFinanceSpider
                spider = YahooFinanceSpider()
                # Session 990: Wrap with timeout — yfinance has NO built-in timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(spider.fetch_data, max_results=stock_limit)
                    try:
                        stock_data = future.result(timeout=SPIDER_FETCH_TIMEOUT)
                    except FuturesTimeoutError:
                        logger.warning(f"Yahoo Finance spider timed out after {SPIDER_FETCH_TIMEOUT}s")
                        stock_data = []

                result['stocks']['assets'] = stock_data

                # Find indices
                if stock_data:
                    sp500 = next((s for s in stock_data if s.get('symbol') in ['GSPC', '^GSPC', 'SPY']), None)
                    nasdaq = next((s for s in stock_data if s.get('symbol') in ['IXIC', '^IXIC', 'QQQ']), None)
                    dow = next((s for s in stock_data if s.get('symbol') in ['DJI', '^DJI', 'DIA']), None)

                    result['stocks']['summary'] = {
                        'sp500': sp500.get('current_price') if sp500 else None,
                        'sp500_change': sp500.get('change_percent') if sp500 else None,
                        'nasdaq': nasdaq.get('current_price') if nasdaq else None,
                        'nasdaq_change': nasdaq.get('change_percent') if nasdaq else None,
                        'dow': dow.get('current_price') if dow else None,
                        'dow_change': dow.get('change_percent') if dow else None,
                    }
            except Exception as e:
                logger.warning(f"Error fetching stock data: {e}")
                result['stocks']['error'] = str(e)

        return result

    def _analyze_filing_impact(
        self,
        filing_type: str = None,
        company_name: str = None
    ) -> Dict[str, Any]:
        """Analyze potential market impact of filings."""
        filings = self._get_sec_filings(
            form_types=[filing_type] if filing_type else None,
            limit=30
        )

        # Filter by company if specified
        if company_name:
            company_lower = company_name.lower()
            filings['filings'] = [
                f for f in filings.get('filings', [])
                if company_lower in f.get('company', '').lower()
            ]

        # Analyze impact patterns
        analysis = {
            'filing_type': filing_type or 'all',
            'company_filter': company_name,
            'filings_analyzed': len(filings.get('filings', [])),
            'high_impact_keywords': [],
            'impact_summary': '',
            'filings': filings.get('filings', [])[:10]
        }

        # Identify high impact patterns
        high_impact_keywords = ['earnings', 'acquisition', 'merger', 'ceo', 'cfo',
                               'resignation', 'appointment', 'material', 'agreement',
                               'bankruptcy', 'layoff', 'restructuring', 'dividend']

        keyword_counts = {}
        for filing in filings.get('filings', []):
            desc = (filing.get('description', '') + ' ' + ' '.join(filing.get('items', []))).lower()
            for kw in high_impact_keywords:
                if kw in desc:
                    keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

        analysis['high_impact_keywords'] = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        # Generate summary
        if filings.get('filings'):
            high_impact_count = len([f for f in filings['filings'] if f.get('is_high_impact')])
            analysis['impact_summary'] = (
                f"Analyzed {len(filings['filings'])} filings. "
                f"{high_impact_count} flagged as high-impact. "
                f"Key themes: {', '.join(k for k, v in analysis['high_impact_keywords'][:3])}."
            )

        return analysis

    def _search_company_filings(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for filings by company name."""
        all_filings = self._get_sec_filings(limit=50)

        query_lower = query.lower()
        matching = [
            f for f in all_filings.get('filings', [])
            if query_lower in f.get('company', '').lower() or
               query_lower in f.get('title', '').lower()
        ]

        return {
            'query': query,
            'matches': matching[:limit],
            'total_matches': len(matching),
            'source': 'sec_edgar'
        }

    # =========================================================================
    # SESSION 683: ML INTEGRATION - GNN FOR MARKET ENTITY ANALYSIS
    # =========================================================================

    def _analyze_with_ml(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use ML models to analyze market entity relationships.

        Session 683: Integrates the Agent-Model Router to auto-select GNN
        for analyzing relationships between market entities (companies,
        sectors, filings, etc.).
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            # Build graph data from market entities
            graph_data = self._build_market_graph(market_data)

            if not graph_data.get('nodes') or len(graph_data['nodes']) < 2:
                return {
                    'ml_used': False,
                    'reason': 'Insufficient entities for graph analysis'
                }

            # Get router and run auto-selection (should select GNN for graph data)
            router = get_agent_model_router()
            result = router.auto_route(graph_data, max_models=2)

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'unknown'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'selection_reason': result.auto_selection.get('selection_reason', ''),
                'entity_count': len(graph_data['nodes']),
                'relationship_count': len(graph_data['edges']),
            }

        except ImportError as e:
            logger.warning(f"ML router not available: {e}")
            return {'ml_used': False, 'reason': f'ML not available: {e}'}
        except Exception as e:
            logger.warning(f"ML analysis error: {e}")
            return {'ml_used': False, 'reason': f'ML error: {e}'}

    def _build_market_graph(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build graph representation of market entities.

        Creates nodes for: companies, sectors, filings
        Creates edges for: company-filing, company-sector, sector-correlations
        """
        nodes = []
        edges = []
        node_ids = set()

        # Process SEC filings
        filings = market_data.get('filings', [])
        for filing in filings:
            company = filing.get('company', 'Unknown')

            # Add company node
            if company not in node_ids:
                nodes.append({
                    'id': company,
                    'type': 'company',
                    'label': company
                })
                node_ids.add(company)

            # Add filing node
            filing_id = f"filing_{filing.get('form_type', '8K')}_{company}"
            if filing_id not in node_ids:
                nodes.append({
                    'id': filing_id,
                    'type': 'filing',
                    'form_type': filing.get('form_type'),
                    'is_high_impact': filing.get('is_high_impact', False),
                    'label': f"{filing.get('form_type', '8K')} - {company}"
                })
                node_ids.add(filing_id)

                # Company -> Filing edge
                edges.append([company, filing_id])

        # Process stock data
        stocks = market_data.get('stocks', {}).get('assets', [])
        for stock in stocks:
            symbol = stock.get('symbol', '')
            if symbol and symbol not in node_ids:
                nodes.append({
                    'id': symbol,
                    'type': 'stock',
                    'price': stock.get('current_price'),
                    'change': stock.get('change_percent'),
                    'label': symbol
                })
                node_ids.add(symbol)

        # Process crypto data
        crypto = market_data.get('crypto', {}).get('assets', [])
        for coin in crypto:
            symbol = coin.get('symbol', '').upper()
            if symbol and symbol not in node_ids:
                nodes.append({
                    'id': symbol,
                    'type': 'crypto',
                    'price': coin.get('current_price'),
                    'change': coin.get('price_change_percentage_24h'),
                    'label': symbol
                })
                node_ids.add(symbol)

        # Create correlation edges between assets with similar price movements
        all_assets = stocks + crypto
        for i, asset1 in enumerate(all_assets):
            for asset2 in all_assets[i+1:]:
                change1 = asset1.get('change_percent') or asset1.get('price_change_percentage_24h') or 0
                change2 = asset2.get('change_percent') or asset2.get('price_change_percentage_24h') or 0

                # Similar direction and magnitude = potential correlation
                if change1 * change2 > 0 and abs(change1 - change2) < 5:
                    id1 = asset1.get('symbol', '').upper()
                    id2 = asset2.get('symbol', '').upper()
                    if id1 and id2:
                        edges.append([id1, id2])

        return {
            'nodes': nodes,
            'edges': edges
        }
