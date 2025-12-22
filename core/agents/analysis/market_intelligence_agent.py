"""
Market Intelligence Agent - Clean Architecture
===============================================

Session 385: Phase 4 - Market Intelligence Integration

This agent provides comprehensive financial market intelligence by combining:
- SEC EDGAR filings (8-K, 10-K, 10-Q)
- Cryptocurrency market data (CoinGecko)
- Stock market data (Yahoo Finance)
- Financial news correlation

Tools Available:
    - get_sec_filings: Fetch recent SEC filings with impact analysis
    - get_market_overview: Get combined crypto/stock market overview
    - analyze_filing_impact: Analyze potential market impact of SEC filings
    - get_sector_performance: Get performance data by sector

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

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


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

        try:
            # Build prompt with context
            full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)

            # Record decision
            self.record_decision(
                f"Starting market intelligence analysis",
                context={'task': task},
                confidence=0.8
            )

            # Call GPT with our tools
            messages = [
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": task}
            ]

            response = self.client.chat.completions.create(
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

            # Handle tool calls
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = eval(tool_call.function.arguments) if tool_call.function.arguments else {}

                    self.record_decision(
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
                final_response = self.client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=messages,
                    max_completion_tokens=3000
                )
                analysis = final_response.choices[0].message.content
            else:
                analysis = assistant_message.content

            # Build result
            execution_time = int((time.time() - start_time) * 1000)

            # Record learning outcome
            self._record_learning_outcome(
                {'analysis': analysis[:500], 'tools_used': [t['tool'] for t in tool_calls_made]},
                task,
                context
            )

            return AgentResult(
                success=True,
                message=analysis,
                data={
                    'analysis': analysis,
                    'collected_data': collected_data,
                    'tool_calls': tool_calls_made,
                },
                agent_name=self.name,
                execution_time_ms=execution_time,
                decisions_made=len(tool_calls_made) + 1,
                tool_calls=tool_calls_made
            )

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
            return {"error": f"Unknown tool: {tool_name}"}

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
            all_filings = spider.fetch_data(max_results=limit * 2)  # Fetch extra for filtering

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
                crypto_data = spider.fetch_data(max_results=crypto_limit)

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
                stock_data = spider.fetch_data(max_results=stock_limit)

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
