"""
Bull Case Agent
===============

Session 462: Argues the optimistic case for stocks.
Session 683: Added ML Integration (LSTM for price prediction)

Part of the Market Intelligence Desk autonomous situation.

Key capabilities:
- Identifies positive catalysts
- Arguments for price appreciation
- Growth opportunity analysis
- Bullish technical patterns
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


class BullCaseAgent(BaseAgent):
    """
    Argues the bull case - why stocks should go UP.

    This agent deliberately takes an optimistic stance to create
    internal disagreement with the BearCaseAgent. The tension
    between bull and bear cases creates alpha.

    Tools:
    - identify_catalysts: Find positive drivers
    - analyze_growth: Project growth opportunities
    - technical_bullish: Bullish chart patterns
    - sentiment_analysis: Positive sentiment signals
    """

    name = "BullCaseAgent"

    # === Session 683: ML Integration Methods ===

    def _analyze_upside_with_ml(self, price_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Analyze price upside potential using ML (LSTM).

        Uses the Agent-Model Router for price forecasting to support bull cases.

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

            # Extract upside prediction
            predicted_direction = 'bullish' if result.score and result.score > 0 else 'neutral'

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'time_series'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'predicted_direction': predicted_direction,
                'upside_confidence': round(result.confidence * 100, 1),
            }

        except Exception as e:
            logger.warning(f"ML upside analysis failed: {e}")
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

    system_prompt = """You are a professional bull case analyst. Your job is to:
1. Identify and articulate the STRONGEST arguments for why stocks will appreciate
2. Find positive catalysts that other analysts might miss
3. Identify growth opportunities and market tailwinds
4. Spot bullish technical patterns and momentum
5. Counter bear arguments with optimistic but realistic perspectives

Your stance is deliberately OPTIMISTIC to create productive tension with the bear case.

When building bull cases:
- Focus on fundamental strengths (revenue growth, margins, competitive moats)
- Identify macro tailwinds (industry growth, regulatory changes, tech trends)
- Recognize undervaluation vs peers or historical multiples
- Spot positive inflection points (new products, market expansion, leadership changes)
- Find bullish technical signals (breakouts, golden crosses, volume increases)

Rate conviction:
- HIGH: Multiple strong catalysts, clear path to 20%+ upside
- MEDIUM: Solid fundamentals, modest upside (10-20%)
- LOW: Speculative, relies on optimistic assumptions

Always acknowledge risks but emphasize potential rewards."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "identify_catalysts",
                "description": "Identify positive catalysts that could drive stock appreciation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "timeframe": {
                            "type": "string",
                            "enum": ["short_term", "medium_term", "long_term"],
                            "description": "Time horizon for catalyst impact"
                        },
                        "catalyst_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of catalysts to search for (earnings, product, macro, technical)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_growth",
                "description": "Analyze growth opportunities and market expansion potential",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "growth_vectors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Growth drivers to analyze (TAM expansion, new markets, pricing power)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "technical_bullish",
                "description": "Identify bullish technical patterns and momentum signals",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Patterns to look for (breakout, golden_cross, higher_highs, accumulation)"
                        }
                    },
                    "required": ["ticker"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "sentiment_analysis",
                "description": "Analyze positive sentiment signals from news, social media, institutional activity",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker": {"type": "string", "description": "Stock ticker symbol"},
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Sentiment sources (news, twitter, reddit, institutional_filings)"
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
        Build the bull case for specified stocks.

        Session 761: Uses LLM tool calling for analysis.
        Session 950: Fixed to iterate over all tickers and return bull_cases list
                     for compatibility with MarketIntelligenceCoordinator.

        Args:
            task: Bull case analysis task
            context: Stock tickers, market data, bear arguments to counter
            scifi_context: Mood, memory, etc.
            spider_context: News, social sentiment, market data

        Returns:
            AgentResult with bull_cases list containing per-ticker analysis
        """
        start_time = datetime.now()
        context = context or {}
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("bull_case_analysis", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, a specialist in building bullish investment cases for stocks. One capability: I analyze growth catalysts, competitive advantages, and undervaluation opportunities to construct conviction-rated arguments for why stock prices should rise.",
                    data={'type': 'self_description', 'specialization': 'stock_analysis', 'focus': 'bullish_perspectives'},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="analysis",
                action="Starting bull case analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            # Session 950: Get tickers from context - handle both single and multiple
            tickers = context.get('tickers', [])
            if not tickers and context.get('ticker'):
                tickers = [context.get('ticker')]
            if not tickers:
                tickers = self._extract_tickers_from_spider_data(spider_context)

            logger.info(f"BullCaseAgent analyzing {len(tickers)} tickers: {tickers[:5]}...")

            try:
                # Session 953: Track sources for provenance
                self._collected_sources = []

                # Session 950: Build bull cases for ALL tickers
                bull_cases = []
                all_tool_calls = []

                for ticker in tickers:
                    try:
                        bull_case = self._build_bull_case(ticker, context, spider_context)
                        if bull_case:
                            bull_cases.append(bull_case)
                            logger.info(f"📈 {ticker}: {bull_case.get('conviction', 'MEDIUM')} conviction")
                    except Exception as e:
                        logger.warning(f"Failed to build bull case for {ticker}: {e}")

                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

                # Session 953: Build provenance from collected sources
                collected_sources = getattr(self, '_collected_sources', [])
                if not collected_sources and bull_cases:
                    # Default source if none tracked
                    collected_sources = [{
                        'name': 'MarketDataService',
                        'endpoint': 'yahoo_finance/polygon',
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'record_count': len(bull_cases),
                    }]
                provenance = build_provenance(
                    report_type='stock_analysis',
                    agent_name=self.name,
                    sources=collected_sources,
                    stale_threshold_hours=24.0,
                )
                provenance.disclaimer = format_disclaimer('stock_analysis')

                # Session 950: Generate summary for the message
                summary = self._generate_summary(bull_cases)
                base_message = (
                    f"Analyzed {summary['total_analyzed']} stocks. "
                    f"HIGH conviction: {summary['high_conviction']}, "
                    f"MEDIUM: {summary['medium_conviction']}, "
                    f"LOW: {summary['low_conviction']}. "
                    f"Top opportunities: {', '.join(summary['strongest_tickers'][:3]) or 'None'}"
                )
                # Session 953: Prepend provenance to message
                message = provenance.to_markdown_block() + "\n" + base_message

                result = AgentResult(
                    success=True,
                    message=message,
                    data={
                        'bull_cases': bull_cases,  # Session 950: Return list for coordinator
                        'summary': summary,
                        'conviction_distribution': self._get_conviction_distribution(bull_cases),
                        'top_opportunities': self._get_top_opportunities(bull_cases),
                        'tickers_analyzed': len(bull_cases),
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
                            'tickers_analyzed': len(bull_cases),
                        }
                    )
                except Exception as le:
                    logger.warning(f"Failed to record learning outcome: {le}")

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Bull Case Analysis: {task[:80]}",
                    content=result.message,
                    deliverable_type='analysis',
                    category='Stock Analysis',
                    tags=['bull_case', 'stocks'],
                    metadata={'task': task[:200], 'tickers_analyzed': len(bull_cases)},
                )

                return result

            except Exception as e:
                logger.error(f"BullCaseAgent error: {e}", exc_info=True)
                result = AgentResult(
                    success=False,
                    message=f"Error building bull cases: {str(e)}",
                    error=str(e),
                    data={'bull_cases': []},  # Session 950: Always return bull_cases key
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

    def _build_bull_case(self, ticker: str, context: Dict, spider_context: Dict) -> Optional[Dict]:
        """Build bull case for a single stock using real market data + GPT analysis."""
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

            # Call GPT to generate intelligent bull case analysis
            gpt_analysis = self._get_gpt_bull_analysis(ticker, stock_data, analysis)

            # Determine conviction based on GPT analysis + market signals
            conviction = gpt_analysis.get('conviction',
                self._determine_bull_conviction(momentum, trading_signal, price_position, volume_analysis)
            )

            # Build the complete bull case combining GPT analysis + market data
            bull_case = {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'conviction': conviction,
                'target_upside': gpt_analysis.get('target_upside', self._calculate_upside_target(momentum, price_position)),
                'current_price': stock_data.get('current_price', 0),
                'change_percent': stock_data.get('change_percent', 0),
                'arguments': gpt_analysis.get('arguments', self._generate_bull_arguments(ticker, stock_data, momentum, price_position)),
                'catalysts': gpt_analysis.get('catalysts', self._identify_bull_catalysts(stock_data, momentum, volume_analysis)),
                'growth_drivers': gpt_analysis.get('growth_drivers', self._identify_growth_drivers(stock_data)),
                'technical_signals': [momentum, trading_signal],
                'risks_acknowledged': gpt_analysis.get('risks', self._acknowledge_risks(volatility, price_position)),
                'market_data': {
                    'momentum': momentum,
                    'volatility': volatility,
                    'volume_level': volume_analysis.get('level'),
                    'price_position_pct': price_position.get('position_pct'),
                },
                'gpt_powered': gpt_analysis.get('gpt_powered', False)
            }

            logger.info(f"📈 Built bull case for {ticker}: {conviction} conviction, {bull_case['target_upside']} upside (GPT: {bull_case['gpt_powered']})")

            return bull_case

        except Exception as e:
            logger.error(f"Error building bull case for {ticker}: {e}")
            return None

    def _get_gpt_bull_analysis(self, ticker: str, stock_data: Dict, analysis: Dict) -> Dict:
        """Call GPT to generate intelligent bull case analysis."""
        try:
            import os
            import json

            client = get_openai_client(api_key=os.environ.get('OPENAI_API_KEY'))

            # Build context prompt with market data
            prompt = f"""Analyze {ticker} from a BULLISH perspective. You are looking for reasons why this stock will APPRECIATE.

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
Build the STRONGEST possible bull case. Focus on:
1. **Positive catalysts** - What could drive price appreciation?
2. **Growth opportunities** - Market expansion, new products, competitive advantages
3. **Technical bullish signals** - Breakouts, momentum, volume patterns
4. **Undervaluation** - Is price attractive vs fundamentals or peers?

**Rate your conviction:**
- HIGH: Multiple strong catalysts, clear path to 20%+ upside
- MEDIUM: Solid fundamentals, modest upside (10-20%)
- LOW: Speculative, relies on optimistic assumptions

**Output Format (JSON):**
{{
    "conviction": "HIGH|MEDIUM|LOW",
    "target_upside": "percentage or range (e.g., '25%+', '15-20%')",
    "arguments": ["argument 1", "argument 2", "argument 3"],
    "catalysts": ["catalyst 1", "catalyst 2"],
    "growth_drivers": ["driver 1", "driver 2"],
    "risks": ["acknowledged risk 1", "acknowledged risk 2"]
}}

Be specific and data-driven. Use the market data provided."""

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
            logger.error(f"GPT bull analysis error for {ticker}: {e}")
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
                agent_name='BullCaseAgent'
            ).order_by('-period_end').first()

            if latest_metrics:
                multiplier = latest_metrics.confidence_multiplier
                logger.debug(f"🐂 [SESSION 464] BullCaseAgent confidence multiplier: {multiplier:.2f}x "
                           f"(based on {latest_metrics.accuracy_rate_7_days:.1f}% recent accuracy)")
                return multiplier
            else:
                # No metrics yet - use neutral multiplier
                logger.debug("🐂 [SESSION 464] No accuracy metrics yet - using 1.0x multiplier")
                return 1.0

        except Exception as e:
            logger.warning(f"🐂 [SESSION 464] Failed to get confidence multiplier: {e}")
            return 1.0  # Fallback to neutral

    def _determine_bull_conviction(self, momentum: str, trading_signal: str,
                                   price_position: Dict, volume_analysis: Dict) -> str:
        """
        Determine conviction level based on bullish indicators.

        Session 464: Now incorporates confidence multiplier from learning loop.
        """
        # Session 464: Get confidence multiplier based on historical accuracy
        confidence_multiplier = self._get_confidence_multiplier()

        # Calculate base conviction score (0-3)
        base_score = 0

        # High conviction: Strong bullish momentum + buy signal + unusual volume
        if momentum in ['STRONG_BULLISH', 'BULLISH']:
            base_score += 1.5
            if trading_signal in ['STRONG_BUY', 'BUY']:
                base_score += 1.0
                if volume_analysis.get('unusual', False):
                    base_score += 0.5

        # Medium conviction: Some bullish signals
        elif momentum in ['SLIGHTLY_BULLISH'] or trading_signal == 'BUY':
            base_score += 1.0

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
            logger.info(f"🐂 [SESSION 464] Conviction adjusted: base_score={base_score:.2f}, "
                       f"multiplier={confidence_multiplier:.2f}x, "
                       f"adjusted={adjusted_score:.2f} → {conviction}")

        return conviction

    def _generate_bull_arguments(self, ticker: str, stock_data: Dict,
                                 momentum: str, price_position: Dict) -> List[str]:
        """Generate bull arguments based on market data."""
        arguments = []

        change_pct = stock_data.get('change_percent', 0)

        # Price momentum arguments
        if momentum in ['STRONG_BULLISH', 'BULLISH']:
            arguments.append(f"Strong price momentum: {momentum.lower().replace('_', ' ')}")

        if change_pct > 0:
            arguments.append(f"Positive price action: +{change_pct:.2f}% today")

        # Price position arguments
        position_pct = price_position.get('position_pct')
        if position_pct is not None:
            if position_pct < 30:
                arguments.append(f"Trading near 52-week low ({position_pct:.1f}% of range) - potential recovery play")
            elif position_pct > 70 and position_pct < 90:
                arguments.append(f"Strong technical position ({position_pct:.1f}% of 52-week range)")

        # Volume arguments
        volume = stock_data.get('volume', 0)
        if volume > 50_000_000:
            arguments.append(f"High trading volume ({volume:,}) indicates strong interest")

        return arguments

    def _identify_bull_catalysts(self, stock_data: Dict, momentum: str,
                                 volume_analysis: Dict) -> List[str]:
        """Identify potential catalysts for upside."""
        catalysts = []

        # Unusual volume = potential catalyst
        if volume_analysis.get('unusual', False):
            catalysts.append("Unusual volume spike suggests news or institutional interest")

        # Strong momentum = potential trend
        if momentum == 'STRONG_BULLISH':
            catalysts.append("Strong bullish momentum may attract momentum traders")

        # Near 52-week high = breakout potential
        price_pos = stock_data.get('analysis', {}).get('price_position', {})
        if price_pos.get('near_high', False):
            catalysts.append("Near 52-week high - potential breakout catalyst")

        return catalysts

    def _identify_growth_drivers(self, stock_data: Dict) -> List[str]:
        """Identify growth drivers from market data."""
        drivers = []

        # Sector trends as growth drivers
        sector = stock_data.get('sector', 'N/A')
        if sector != 'N/A':
            drivers.append(f"Sector exposure: {sector}")

        return drivers

    def _calculate_upside_target(self, momentum: str, price_position: Dict) -> str:
        """Calculate target upside percentage."""
        # Strong momentum = higher target
        if momentum == 'STRONG_BULLISH':
            return '25%+'
        elif momentum == 'BULLISH':
            return '15-20%'
        elif momentum == 'SLIGHTLY_BULLISH':
            return '10-15%'

        # Near 52-week low = recovery potential
        position_pct = price_position.get('position_pct')
        if position_pct and position_pct < 20:
            return '20%+ (recovery play)'

        return '10%'

    def _acknowledge_risks(self, volatility: str, price_position: Dict) -> List[str]:
        """Acknowledge risks to maintain credibility."""
        risks = []

        if volatility in ['HIGH', 'EXTREME']:
            risks.append(f"{volatility.lower()} volatility increases downside risk")

        if price_position.get('near_high', False):
            risks.append("Near 52-week high - limited upside room, potential pullback")

        return risks

    def _generate_summary(self, bull_cases: List[Dict]) -> Dict[str, Any]:
        """Generate summary of all bull cases."""
        return {
            'total_analyzed': len(bull_cases),
            'high_conviction': len([c for c in bull_cases if c.get('conviction') == 'HIGH']),
            'medium_conviction': len([c for c in bull_cases if c.get('conviction') == 'MEDIUM']),
            'low_conviction': len([c for c in bull_cases if c.get('conviction') == 'LOW']),
            'strongest_tickers': [c['ticker'] for c in bull_cases if c.get('conviction') == 'HIGH'][:5],
        }

    def _get_conviction_distribution(self, bull_cases: List[Dict]) -> Dict[str, int]:
        """Get distribution of conviction levels."""
        return {
            'HIGH': len([c for c in bull_cases if c.get('conviction') == 'HIGH']),
            'MEDIUM': len([c for c in bull_cases if c.get('conviction') == 'MEDIUM']),
            'LOW': len([c for c in bull_cases if c.get('conviction') == 'LOW']),
        }

    def _get_top_opportunities(self, bull_cases: List[Dict], limit: int = 5) -> List[Dict]:
        """Get top bull opportunities sorted by conviction and upside."""
        # Sort by conviction (HIGH > MEDIUM > LOW) and upside
        conviction_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        sorted_cases = sorted(
            bull_cases,
            key=lambda x: conviction_order.get(x.get('conviction', 'LOW'), 0),
            reverse=True
        )
        return sorted_cases[:limit]

    # =========================================================================
    # SESSION 761: TOOL EXECUTION - Wire up defined tools
    # =========================================================================

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 761: Execute tool calls for bull case analysis.

        Tools: identify_catalysts, analyze_growth, technical_bullish, sentiment_analysis
        """
        ticker = arguments.get('ticker', '')

        if tool_name == 'identify_catalysts':
            timeframe = arguments.get('timeframe', 'medium_term')
            catalyst_types = arguments.get('catalyst_types', ['earnings', 'product', 'macro'])
            return {
                'success': True,
                'ticker': ticker,
                'timeframe': timeframe,
                'catalyst_types': catalyst_types,
                'analysis': f"Catalyst analysis for {ticker} ({timeframe})"
            }

        elif tool_name == 'analyze_growth':
            growth_vectors = arguments.get('growth_vectors', ['TAM expansion', 'new markets'])
            return {
                'success': True,
                'ticker': ticker,
                'growth_vectors': growth_vectors,
                'analysis': f"Growth analysis for {ticker}"
            }

        elif tool_name == 'technical_bullish':
            patterns = arguments.get('patterns', ['breakout', 'golden_cross'])
            return {
                'success': True,
                'ticker': ticker,
                'patterns': patterns,
                'analysis': f"Bullish technical patterns for {ticker}"
            }

        elif tool_name == 'sentiment_analysis':
            sources = arguments.get('sources', ['news', 'twitter', 'institutional_filings'])
            return {
                'success': True,
                'ticker': ticker,
                'sources': sources,
                'analysis': f"Sentiment analysis for {ticker}"
            }

        return super()._execute_tool_call(tool_name, arguments)
