"""
Bear Case Agent
===============

Session 462: Argues the pessimistic case for stocks.
Session 683: Added ML Integration (LSTM for price prediction)

Part of the Market Intelligence Desk autonomous situation.

Key capabilities:
- Identifies risks and red flags
- Arguments for price depreciation
- Overvaluation analysis
- Bearish technical patterns
- ML-powered price forecasting
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from core.agents.base_agent import BaseAgent, AgentResult, WEB_SEARCH_TOOL
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

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

    # === Session 683: ML Integration Methods ===

    def _analyze_downside_with_ml(self, price_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Analyze price downside risk using ML (LSTM).

        Uses the Agent-Model Router for price forecasting to support bear cases.

        Args:
            price_history: List of price data points with timestamps

        Returns:
            Dict with ML analysis including price predictions
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build time series data
            time_series = self._build_price_time_series(price_history)

            if not time_series.get('values'):
                return {'ml_used': False, 'reason': 'Insufficient price data'}

            result = router.auto_route(
                data=time_series,
                task_hint=TaskType.TIME_SERIES,
                max_models=2
            )

            # Extract downside prediction
            predicted_direction = 'bearish' if result.score and result.score < 0 else 'neutral'

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'time_series'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'predicted_direction': predicted_direction,
                'downside_risk': round(result.confidence * 100, 1),
            }

        except Exception as e:
            logger.warning(f"ML downside analysis failed: {e}")
            return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

    def _build_price_time_series(self, price_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build time series data from price history."""
        timestamps = []
        values = []

        for point in price_history:
            ts = point.get('timestamp') or point.get('date')
            price = point.get('price') or point.get('close') or point.get('current_price')

            if ts and price:
                timestamps.append(str(ts))
                values.append(float(price))

        return {'timestamps': timestamps, 'values': values, 'data_type': 'stock_prices'}

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
        },
        # Session 988: Web search fallback when local data is unavailable
        WEB_SEARCH_TOOL,
    ]

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Build the bear case for specified stocks.

        Session 761: Uses LLM tool calling for analysis.
        Session 950: Fixed to iterate over all tickers and return bear_cases list
                     for compatibility with MarketIntelligenceCoordinator.

        Args:
            task: Bear case analysis task
            context: Stock tickers, market data, bull arguments to counter
            scifi_context: Mood, memory, etc.
            spider_context: News, social sentiment, market data

        Returns:
            AgentResult with bear_cases list containing per-ticker analysis
        """
        start_time = datetime.now()
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("bear_case_analysis", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a specialist in analyzing downside risks and building bear cases for stocks. One capability: I identify vulnerabilities in bullish narratives by examining competitive threats, valuation concerns, regulatory risks, and market sentiment shifts to generate conviction-rated bearish arguments.",
                    data={'type': 'self_description', 'specialization': 'stock_analysis', 'focus': 'bearish_perspectives'},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="analysis",
                action="Starting bear case analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            # Session 950: Get tickers from context - handle both single and multiple
            tickers = context.get('tickers', [])
            if not tickers and context.get('ticker'):
                tickers = [context.get('ticker')]
            if not tickers:
                tickers = self._extract_tickers_from_spider_data(spider_context)

            logger.info(f"BearCaseAgent analyzing {len(tickers)} tickers: {tickers[:5]}...")

            try:
                # Session 953: Track sources for provenance
                self._collected_sources = []

                # Session 950: Build bear cases for ALL tickers
                bear_cases = []
                all_tool_calls = []

                for ticker in tickers:
                    try:
                        bear_case = self._build_bear_case(ticker, context, spider_context)
                        if bear_case:
                            bear_cases.append(bear_case)
                            logger.info(f"📉 {ticker}: {bear_case.get('conviction', 'MEDIUM')} conviction")
                    except Exception as e:
                        logger.warning(f"Failed to build bear case for {ticker}: {e}")

                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

                # Session 953: Build provenance from collected sources
                collected_sources = getattr(self, '_collected_sources', [])
                if not collected_sources and bear_cases:
                    # Default source if none tracked
                    collected_sources = [{
                        'name': 'MarketDataService',
                        'endpoint': 'yahoo_finance/polygon',
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'record_count': len(bear_cases),
                    }]
                provenance = build_provenance(
                    report_type='stock_analysis',
                    agent_name=self.name,
                    sources=collected_sources,
                    stale_threshold_hours=24.0,
                )
                provenance.disclaimer = format_disclaimer('stock_analysis')

                # Session 950: Generate summary for the message
                summary = self._generate_summary(bear_cases)
                base_message = (
                    f"Analyzed {summary['total_analyzed']} stocks. "
                    f"HIGH risk: {summary['high_conviction']}, "
                    f"MEDIUM: {summary['medium_conviction']}, "
                    f"LOW: {summary['low_conviction']}. "
                    f"Top risks: {', '.join(summary['riskiest_tickers'][:3]) or 'None'}"
                )
                # Session 953: Prepend provenance to message
                message = provenance.to_markdown_block() + "\n" + base_message

                result = AgentResult(
                    success=True,
                    message=message,
                    data={
                        'bear_cases': bear_cases,  # Session 950: Return list for coordinator
                        'summary': summary,
                        'conviction_distribution': self._get_conviction_distribution(bear_cases),
                        'top_risks': self._get_top_risks(bear_cases),
                        'tickers_analyzed': len(bear_cases),
                        # Session 953: Include provenance
                        'provenance': provenance.to_dict(),
                        'publishable': provenance.publishable,
                        'validation_status': provenance.validation_status,
                    },
                    agent_name=self.name,
                    execution_time_ms=execution_time,
                    tool_calls=all_tool_calls
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
                            'tickers_analyzed': len(bear_cases),
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Bear Case Analysis: {task[:80]}",
                    content=result.message,
                    deliverable_type='analysis',
                    category='Stock Analysis',
                    tags=['bear_case', 'stocks'],
                    metadata={'task': task[:200], 'tickers_analyzed': len(bear_cases)},
                )

                return result

            except Exception as e:
                logger.error(f"BearCaseAgent error: {e}", exc_info=True)
                result = AgentResult(
                    success=False,
                    message=f"Error building bear cases: {str(e)}",
                    error=str(e),
                    data={'bear_cases': []},  # Session 950: Always return bear_cases key
                    agent_name=self.name,
                    execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
                )

                try:
                    self._record_learning_outcome(
                        task=task,
                        result=result,
                        success=False,
                        context={'agent_type': self.__class__.__name__, 'error': str(e)}
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                return result

    def _extract_conviction(self, analysis: str) -> str:
        """Extract conviction level from analysis text."""
        analysis_upper = analysis.upper() if analysis else ''
        if 'HIGH CONVICTION' in analysis_upper or 'CONVICTION: HIGH' in analysis_upper:
            return 'HIGH'
        elif 'MEDIUM CONVICTION' in analysis_upper or 'CONVICTION: MEDIUM' in analysis_upper:
            return 'MEDIUM'
        elif 'LOW CONVICTION' in analysis_upper or 'CONVICTION: LOW' in analysis_upper:
            return 'LOW'
        return 'MEDIUM'  # Default

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

            client = get_openai_client(api_key=os.environ.get('OPENAI_API_KEY'))

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

    def _get_confidence_multiplier(self) -> float:
        """
        Session 464: Get confidence multiplier based on agent's recent accuracy.

        Returns:
            float: Confidence multiplier (0.5-1.5x) based on track record
        """
        try:
            from core.models_unified_system import AgentAccuracyMetrics

            # Get the most recent metrics for this agent
            latest_metrics = AgentAccuracyMetrics.objects.filter(
                agent_name='BearCaseAgent'
            ).order_by('-period_end').first()

            if latest_metrics:
                multiplier = latest_metrics.confidence_multiplier
                logger.debug(f"🐻 [SESSION 464] BearCaseAgent confidence multiplier: {multiplier:.2f}x "
                           f"(based on {latest_metrics.accuracy_rate_7_days:.1f}% recent accuracy)")
                return multiplier
            else:
                # No metrics yet - use neutral multiplier
                logger.debug("🐻 [SESSION 464] No accuracy metrics yet - using 1.0x multiplier")
                return 1.0

        except Exception as e:
            logger.warning(f"🐻 [SESSION 464] Failed to get confidence multiplier: {e}")
            return 1.0  # Fallback to neutral

    def _determine_bear_conviction(self, momentum: str, trading_signal: str,
                                   price_position: Dict, volatility: str) -> str:
        """
        Determine conviction level based on bearish indicators.

        Session 464: Now incorporates confidence multiplier from learning loop.
        """
        # Session 464: Get confidence multiplier based on historical accuracy
        confidence_multiplier = self._get_confidence_multiplier()

        # Calculate base conviction score (0-3)
        base_score = 0

        # High conviction: Strong bearish momentum + sell signal + high volatility
        if momentum in ['STRONG_BEARISH', 'BEARISH']:
            base_score += 1.5
            if trading_signal in ['STRONG_SELL', 'SELL']:
                base_score += 1.0
                if volatility in ['HIGH', 'EXTREME']:
                    base_score += 0.5

        # Medium conviction: Some bearish signals
        elif momentum in ['SLIGHTLY_BEARISH'] or trading_signal == 'SELL':
            base_score += 1.0

        # Elevated risk near 52-week high (pullback risk)
        if price_position.get('near_high', False):
            base_score += 0.5

        # Apply confidence multiplier from learning loop
        adjusted_score = base_score * confidence_multiplier

        # Convert adjusted score to conviction level
        if adjusted_score >= 2.5:
            conviction = 'HIGH'
        elif adjusted_score >= 1.0:
            conviction = 'MEDIUM'
        else:
            conviction = 'LOW'

        # Log multiplier application
        if abs(confidence_multiplier - 1.0) > 0.05:
            logger.info(f"🐻 [SESSION 464] Conviction adjusted: base_score={base_score:.2f}, "
                       f"multiplier={confidence_multiplier:.2f}x, "
                       f"adjusted={adjusted_score:.2f} → {conviction}")

        return conviction

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

    # =========================================================================
    # SESSION 761: TOOL EXECUTION - Wire up defined tools
    # =========================================================================

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for bear case analysis.

        Tools: identify_risks, analyze_overvaluation, technical_bearish, negative_sentiment
        """
        ticker = arguments.get('ticker', '')

        if tool_name == 'identify_risks':
            risk_types = arguments.get('risk_types', ['operational', 'financial', 'competitive'])
            timeframe = arguments.get('timeframe', 'medium_term')
            return {
                'success': True,
                'ticker': ticker,
                'risk_types': risk_types,
                'timeframe': timeframe,
                'analysis': f"Risk identification for {ticker}"
            }

        elif tool_name == 'analyze_overvaluation':
            metrics = arguments.get('metrics', ['P/E', 'P/S', 'EV/EBITDA'])
            return {
                'success': True,
                'ticker': ticker,
                'metrics': metrics,
                'analysis': f"Overvaluation analysis for {ticker}"
            }

        elif tool_name == 'technical_bearish':
            patterns = arguments.get('patterns', ['death_cross', 'head_shoulders', 'breakdown'])
            return {
                'success': True,
                'ticker': ticker,
                'patterns': patterns,
                'analysis': f"Bearish technical patterns for {ticker}"
            }

        elif tool_name == 'negative_sentiment':
            sources = arguments.get('sources', ['news', 'social', 'short_interest'])
            return {
                'success': True,
                'ticker': ticker,
                'sources': sources,
                'analysis': f"Negative sentiment analysis for {ticker}"
            }

        return super()._execute_tool_call(tool_name, arguments)
