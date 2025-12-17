"""
Bear Case Agent
===============

Session 462: Argues the pessimistic case for stocks.
Part of the Market Intelligence Desk autonomous situation.

Key capabilities:
- Identifies risks and red flags
- Arguments for price depreciation
- Overvaluation analysis
- Bearish technical patterns
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class BearCaseAgent(BaseAgent):
    """
    Argues the bear case - why stocks should go DOWN.

    This agent deliberately takes a pessimistic stance to create
    internal disagreement with the BullCaseAgent. The tension
    between bull and bear cases protects against groupthink.

    Tools:
    - identify_risks: Find negative catalysts
    - analyze_overvaluation: Valuation red flags
    - technical_bearish: Bearish chart patterns
    - negative_sentiment: Warning signals
    """

    name = "BearCaseAgent"

    system_prompt = """You are a professional bear case analyst. Your job is to:
1. Identify and articulate the STRONGEST arguments for why stocks will depreciate
2. Find risks and red flags that bullish analysts might overlook
3. Identify overvaluation, deteriorating fundamentals, and headwinds
4. Spot bearish technical patterns and distribution
5. Counter bull arguments with skeptical but realistic perspectives

Your stance is deliberately PESSIMISTIC to create productive tension with the bull case.

When building bear cases:
- Focus on fundamental weaknesses (declining margins, rising debt, market share loss)
- Identify macro headwinds (rising rates, recession risk, regulatory threats)
- Recognize overvaluation vs peers or historical averages
- Spot negative inflection points (guidance cuts, insider selling, layoffs)
- Find bearish technical signals (breakdowns, death crosses, distribution patterns)

Rate conviction:
- HIGH: Multiple serious risks, clear path to 20%+ downside
- MEDIUM: Concerning trends, modest downside (10-20%)
- LOW: Speculative concerns, relies on pessimistic assumptions

Always acknowledge bull arguments but emphasize potential risks."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "identify_risks",
                "description": "Identify negative catalysts that could drive stock depreciation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "timeframe": {
                            "type": "string",
                            "enum": ["short_term", "medium_term", "long_term"],
                            "description": "Time horizon for risk impact"
                        },
                        "risk_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of risks (fundamental, competitive, macro, technical)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_overvaluation",
                "description": "Analyze overvaluation risks and mean reversion potential",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "valuation_metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to analyze (P/E vs history, P/S vs peers, EV/EBITDA vs sector)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "technical_bearish",
                "description": "Identify bearish technical patterns and momentum signals",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Patterns to look for (breakdown, death_cross, lower_lows, distribution)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "negative_sentiment",
                "description": "Analyze negative sentiment signals from news, insider activity, analyst downgrades",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sentiment sources (news, analyst_ratings, insider_sales, short_interest)"
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
        Build the bear case for specified stocks.

        Args:
            task: Bear case analysis task
            context: Stock tickers, market data, bull arguments to counter
            scifi_context: Mood, memory, etc.
            spider_context: News, social sentiment, market data

        Returns:
            AgentResult with bear case arguments and conviction rating
        """
        start_time = datetime.now()
        context = context or {}

        logger.info(f"BearCaseAgent executing: {task[:100]}...")

        try:
            # Get tickers to analyze (from context or spider data)
            tickers = context.get('tickers', self._extract_tickers_from_spider_data(spider_context))

            if not tickers:
                return AgentResult(
                    success=False,
                    error="No tickers provided for bear case analysis",
                    agent_name=self.name
                )

            # Build bear cases for each ticker
            bear_cases = []
            for ticker in tickers[:10]:  # Limit to 10 tickers per cycle
                case = self._build_bear_case(ticker, context, spider_context)
                if case:
                    bear_cases.append(case)

            # Generate summary
            summary = self._generate_summary(bear_cases)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return AgentResult(
                success=True,
                message=f"Bear case analysis complete for {len(bear_cases)} stocks",
                data={
                    'bear_cases': bear_cases,
                    'summary': summary,
                    'conviction_distribution': self._get_conviction_distribution(bear_cases),
                    'top_risks': self._get_top_risks(bear_cases),
                },
                agent_name=self.name,
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"BearCaseAgent error: {e}")
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name
            )

    def _extract_tickers_from_spider_data(self, spider_context: Dict) -> List[str]:
        """Extract stock tickers from spider intelligence."""
        # This would parse spider data for mentioned tickers
        # For now, return a default watchlist
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META']

    def _build_bear_case(self, ticker: str, context: Dict, spider_context: Dict) -> Optional[Dict]:
        """Build bear case for a single stock using real market data + GPT analysis."""
        try:
            # Get real market data from MarketDataService
            from core.services.market_data_service import get_market_data_service
            market_service = get_market_data_service()

            # Fetch enriched stock data
            stock_data = market_service.get_stock_details(ticker)

            if stock_data.get('error'):
                logger.warning(f"Could not fetch data for {ticker}: {stock_data['error']}")
                return None

            # Extract enriched analysis
            analysis = stock_data.get('analysis', {})
            momentum = analysis.get('momentum', 'NEUTRAL')
            volatility = analysis.get('volatility', 'UNKNOWN')
            volume_analysis = analysis.get('volume_analysis', {})
            price_position = analysis.get('price_position', {})
            trading_signal = analysis.get('trading_signal', 'HOLD')

            # Call GPT to generate intelligent bear case analysis
            gpt_analysis = self._get_gpt_bear_analysis(ticker, stock_data, analysis)

            # Determine conviction based on GPT analysis + market signals
            conviction = gpt_analysis.get('conviction',
                self._determine_bear_conviction(momentum, trading_signal, price_position, volatility)
            )

            # Build the complete bear case combining GPT analysis + market data
            bear_case = {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'conviction': conviction,
                'target_downside': gpt_analysis.get('target_downside', self._calculate_downside_target(momentum, price_position, volatility)),
                'current_price': stock_data.get('current_price', 0),
                'change_percent': stock_data.get('change_percent', 0),
                'arguments': gpt_analysis.get('arguments', self._generate_bear_arguments(ticker, stock_data, momentum, price_position, volatility)),
                'risks': gpt_analysis.get('risks', self._identify_bear_risks(stock_data, momentum, volume_analysis, price_position)),
                'valuation_concerns': gpt_analysis.get('valuation_concerns', self._identify_valuation_concerns(stock_data, price_position)),
                'technical_signals': [momentum, trading_signal],
                'bull_rebuttals': gpt_analysis.get('bull_rebuttals', self._counter_bull_arguments(momentum, price_position)),
                'market_data': {
                    'momentum': momentum,
                    'volatility': volatility,
                    'volume_level': volume_analysis.get('level'),
                    'price_position_pct': price_position.get('position_pct'),
                },
                'gpt_powered': gpt_analysis.get('gpt_powered', False)
            }

            logger.info(f"📉 Built bear case for {ticker}: {conviction} conviction, {bear_case['target_downside']} downside (GPT: {bear_case['gpt_powered']})")

            return bear_case

        except Exception as e:
            logger.error(f"Error building bear case for {ticker}: {e}")
            return None

    def _get_gpt_bear_analysis(self, ticker: str, stock_data: Dict, analysis: Dict) -> Dict:
        """Call GPT to generate intelligent bear case analysis."""
        try:
            from openai import OpenAI
            import os
            import json

            client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

            # Build context prompt with market data
            prompt = f"""Analyze {ticker} from a BEARISH perspective. You are looking for reasons why this stock will DEPRECIATE.

**Current Market Data:**
- Price: ${stock_data.get('current_price', 0):.2f}
- Change Today: {stock_data.get('change_percent', 0):+.2f}%
- Volume: {stock_data.get('volume', 0):,}
- 52-Week High: ${analysis.get('price_position', {}).get('fifty_two_week_high', 0):.2f}
- 52-Week Low: ${analysis.get('price_position', {}).get('fifty_two_week_low', 0):.2f}
- Price Position: {analysis.get('price_position', {}).get('position_pct', 0):.1f}% of 52-week range
- Momentum: {analysis.get('momentum', 'UNKNOWN')}
- Volatility: {analysis.get('volatility', 'UNKNOWN')}
- Volume Level: {analysis.get('volume_analysis', {}).get('level', 'UNKNOWN')}
- Trading Signal: {analysis.get('trading_signal', 'HOLD')}

**Your Task:**
Build the STRONGEST possible bear case. Focus on:
1. **Downside risks** - What could drive price depreciation?
2. **Overvaluation concerns** - Is price too high vs fundamentals or peers?
3. **Technical bearish signals** - Breakdowns, distribution, weakness
4. **Headwinds** - Competitive threats, market saturation, regulatory risks

**Rate your conviction:**
- HIGH: Multiple serious risks, clear path to 20%+ downside
- MEDIUM: Concerning trends, modest downside (10-20%)
- LOW: Speculative concerns, relies on pessimistic assumptions

**Output Format (JSON):**
{{
    "conviction": "HIGH|MEDIUM|LOW",
    "target_downside": "percentage or range (e.g., '-25%', '-15% to -20%')",
    "arguments": ["argument 1", "argument 2", "argument 3"],
    "risks": ["risk 1", "risk 2"],
    "valuation_concerns": ["concern 1", "concern 2"],
    "bull_rebuttals": ["rebuttal to bull argument 1", "rebuttal 2"]
}}

Be specific and data-driven. Use the market data provided. Counter any obvious bull arguments."""

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000
            )

            # Parse GPT response
            content = response.choices[0].message.content

            # Try to parse as JSON
            try:
                result = json.loads(content)
                result['gpt_powered'] = True
                return result
            except json.JSONDecodeError:
                # If not JSON, extract what we can
                logger.warning(f"GPT response not JSON for {ticker}, using fallback parsing")
                return {'gpt_powered': False}

        except Exception as e:
            logger.error(f"GPT bear analysis error for {ticker}: {e}")
            return {'gpt_powered': False}

    def _determine_bear_conviction(self, momentum: str, trading_signal: str,
                                   price_position: Dict, volatility: str) -> str:
        """Determine conviction level based on bearish indicators."""
        # High conviction: Strong bearish momentum + sell signal + high volatility
        if momentum in ['STRONG_BEARISH', 'BEARISH']:
            if trading_signal in ['STRONG_SELL', 'SELL']:
                if volatility in ['HIGH', 'EXTREME']:
                    return 'HIGH'
                return 'MEDIUM'

        # Medium conviction: Some bearish signals
        if momentum in ['BEARISH', 'SLIGHTLY_BEARISH'] or trading_signal == 'SELL':
            return 'MEDIUM'

        # High conviction if near 52-week high (pullback risk)
        if price_position.get('near_high', False):
            return 'MEDIUM'  # Elevated risk near highs

        # Low conviction: Weak or mixed signals
        return 'LOW'

    def _generate_bear_arguments(self, ticker: str, stock_data: Dict,
                                 momentum: str, price_position: Dict, volatility: str) -> List[str]:
        """Generate bear arguments based on market data."""
        arguments = []

        change_pct = stock_data.get('change_percent', 0)

        # Price momentum arguments
        if momentum in ['STRONG_BEARISH', 'BEARISH']:
            arguments.append(f"Weak price momentum: {momentum.lower().replace('_', ' ')}")

        if change_pct < 0:
            arguments.append(f"Negative price action: {change_pct:.2f}% today")

        # Price position arguments
        position_pct = price_position.get('position_pct')
        if position_pct is not None:
            if position_pct > 80:
                arguments.append(f"Trading near 52-week high ({position_pct:.1f}% of range) - limited upside, pullback risk")
            elif position_pct < 20:
                arguments.append(f"Continued weakness near lows ({position_pct:.1f}% of range)")

        # Volatility arguments (bears love volatility as risk)
        if volatility in ['HIGH', 'EXTREME']:
            arguments.append(f"{volatility.lower()} volatility increases downside risk")

        # Volume arguments (unusual volume on down days = distribution)
        volume = stock_data.get('volume', 0)
        if volume > 50_000_000 and change_pct < 0:
            arguments.append(f"High volume ({volume:,}) on down day suggests distribution")

        return arguments

    def _identify_bear_risks(self, stock_data: Dict, momentum: str,
                            volume_analysis: Dict, price_position: Dict) -> List[str]:
        """Identify downside risks."""
        risks = []

        # Unusual volume on negative price action = bad sign
        if volume_analysis.get('unusual', False):
            change = stock_data.get('change_percent', 0)
            if change < 0:
                risks.append("Unusual volume on down day suggests institutional selling")

        # Weak momentum = trend risk
        if momentum in ['STRONG_BEARISH', 'BEARISH']:
            risks.append("Bearish momentum may accelerate if support breaks")

        # Near 52-week high = pullback risk
        if price_position.get('near_high', False):
            risks.append("Near 52-week high - vulnerable to profit-taking")

        # Near 52-week low = further downside risk
        if price_position.get('near_low', False):
            risks.append("Near 52-week low - support may break, triggering further selling")

        return risks

    def _identify_valuation_concerns(self, stock_data: Dict, price_position: Dict) -> List[str]:
        """Identify valuation concerns."""
        concerns = []

        # High price position can indicate overvaluation
        position_pct = price_position.get('position_pct')
        if position_pct and position_pct > 85:
            concerns.append(f"Extended valuation: trading at {position_pct:.1f}% of 52-week range")

        # Add sector-specific concerns if available
        sector = stock_data.get('sector', 'N/A')
        if sector != 'N/A':
            concerns.append(f"Sector exposure: {sector} (monitor sector headwinds)")

        return concerns

    def _calculate_downside_target(self, momentum: str, price_position: Dict, volatility: str) -> str:
        """Calculate target downside percentage."""
        # Strong bearish momentum = higher downside target
        if momentum == 'STRONG_BEARISH':
            return '-25% or more'
        elif momentum == 'BEARISH':
            return '-15% to -20%'
        elif momentum == 'SLIGHTLY_BEARISH':
            return '-10% to -15%'

        # Near 52-week high + high volatility = pullback risk
        position_pct = price_position.get('position_pct')
        if position_pct and position_pct > 85 and volatility in ['HIGH', 'EXTREME']:
            return '-15%+ (pullback from highs)'

        return '-10%'

    def _counter_bull_arguments(self, momentum: str, price_position: Dict) -> List[str]:
        """Counter potential bull arguments to maintain credibility."""
        rebuttals = []

        # Counter "it's going up"
        if momentum in ['BULLISH', 'STRONG_BULLISH']:
            rebuttals.append("Yes momentum is positive, but this creates pullback risk and overbought conditions")

        # Counter "it's near lows, recovery play"
        if price_position.get('near_low', False):
            rebuttals.append("Near 52-week low doesn't guarantee recovery - could break support")

        # Counter "high volume is bullish"
        rebuttals.append("High volume can indicate distribution, not accumulation")

        return rebuttals

    def _generate_summary(self, bear_cases: List[Dict]) -> Dict[str, Any]:
        """Generate summary of all bear cases."""
        return {
            'total_analyzed': len(bear_cases),
            'high_conviction': len([c for c in bear_cases if c.get('conviction') == 'HIGH']),
            'medium_conviction': len([c for c in bear_cases if c.get('conviction') == 'MEDIUM']),
            'low_conviction': len([c for c in bear_cases if c.get('conviction') == 'LOW']),
            'riskiest_tickers': [c['ticker'] for c in bear_cases if c.get('conviction') == 'HIGH'][:5],
        }

    def _get_conviction_distribution(self, bear_cases: List[Dict]) -> Dict[str, int]:
        """Get distribution of conviction levels."""
        return {
            'HIGH': len([c for c in bear_cases if c.get('conviction') == 'HIGH']),
            'MEDIUM': len([c for c in bear_cases if c.get('conviction') == 'MEDIUM']),
            'LOW': len([c for c in bear_cases if c.get('conviction') == 'LOW']),
        }

    def _get_top_risks(self, bear_cases: List[Dict], limit: int = 5) -> List[Dict]:
        """Get top bear risks sorted by conviction and downside."""
        # Sort by conviction (HIGH > MEDIUM > LOW) and downside
        conviction_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        sorted_cases = sorted(
            bear_cases,
            key=lambda x: conviction_order.get(x.get('conviction', 'LOW'), 0),
            reverse=True
        )
        return sorted_cases[:limit]
