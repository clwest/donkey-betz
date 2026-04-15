"""
Prediction Market Analyst Agent
================================

Session 558: Analyzes Kalshi prediction market data to identify:
- Mispriced markets (probability vs reality)
- High-conviction opportunities
- Trend reversals and momentum shifts
- Arbitrage across correlated markets

Uses Kalshi spider data for real-time market intelligence.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


# =============================================================================
# Session 683: ML Integration for Prediction Markets (LSTM+Anomaly)
# =============================================================================

def analyze_market_data_with_ml(market_data: dict) -> dict:
    """Analyze prediction market data using ML models."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(data=market_data, task_hint=TaskType.TIME_SERIES, max_models=2)
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'time_series'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'predictions': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML market analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class PredictionMarketAnalyst(BaseAgent):
    """
    Analyzes prediction markets from Kalshi to identify trading opportunities.

    Capabilities:
    - Market mispricing detection
    - Probability trend analysis
    - Cross-market correlation
    - Event impact assessment
    - Confidence scoring
    """

    name = "PredictionMarketAnalyst"

    system_prompt = """You are a Prediction Market Analyst specializing in Kalshi markets.

Your job is to analyze prediction market data and provide actionable insights:

1. **Market Analysis**
   - Identify mispriced markets (probability doesn't match fundamentals)
   - Spot momentum shifts (probabilities moving fast)
   - Find high-volume markets (smart money signals)
   - Detect arbitrage opportunities (related markets with inconsistent pricing)

2. **Category Expertise**
   - Economics: Jobs reports, inflation, GDP, Fed decisions
   - Politics: Elections, policy changes, confirmations
   - Tech: Product launches, earnings, company events
   - Finance: Stock prices, crypto, market moves
   - Weather: Temperature, hurricanes, climate events

3. **Signal Generation**
   - HIGH CONVICTION: >80% probability with supporting data
   - CONTRARIAN: Market may be wrong (fundamentals diverge)
   - MOMENTUM: Probability shifted >10% recently
   - ARBITRAGE: Related markets priced inconsistently

4. **Risk Assessment**
   - Time to resolution (closer = more confident)
   - Volume/liquidity (higher = better execution)
   - Category volatility (politics > weather typically)
   - Event dependency (what could change the outcome)

Output Format:
- Be concise and actionable
- Include probability, volume, and reasoning
- Flag risks and uncertainties
- Suggest position sizing (small/medium/large)
- Note related markets to watch

Remember: Markets are forward-looking. Look for what others are missing."""

    # Session 763: Mission Control configuration
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='opportunity',
        default_urgency='medium',
        min_confidence=0.0,
        actions=[
            {'id': 'watch', 'label': 'Watch Market', 'style': 'primary', 'description': 'Track this market'},
            {'id': 'research_more', 'label': 'Research More', 'style': 'success', 'description': 'Deep dive research'},
            {'id': 'pass', 'label': 'Pass', 'style': 'secondary', 'description': 'Skip this opportunity'},
        ],
        payload_fields=['markets_analyzed', 'opportunities_found', 'confidence'],
        max_items_per_hour=5
    )

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Analyze prediction markets and generate insights.

        Args:
            task: Analysis request (e.g., "analyze economics markets")
            context: Additional context (portfolio, preferences)
            scifi_context: Agent mood, memory, learning
            spider_context: Real-time market data from Kalshi spider

        Returns:
            AgentResult with market analysis and trading signals
        """
        start_time = datetime.now()
        context = context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("prediction_market_analysis", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting prediction market analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            try:
                # Fetch market data from Kalshi spider
                markets = self._get_kalshi_markets(context)

                if not markets:
                    return AgentResult(
                        success=False,
                        message="No prediction market data available",
                        data={},
                        error="Kalshi spider returned no data",
                        agent_name=self.name,
                        execution_time_ms=self._elapsed_ms(start_time)
                    )

                # Analyze markets
                analysis = self._analyze_markets(markets, task, context)

                # Generate trading signals
                signals = self._generate_signals(markets, analysis)

                # Build response using LLM
                response = self._generate_analysis_report(task, markets, analysis, signals, context)

                # Record learning outcome
                try:
                    self._record_learning_outcome(
                        result=None,
                        task=task,
                        context=context,
                        success=True
                    )
                except Exception as learn_err:
                    logger.debug(f"Learning outcome recording skipped: {learn_err}")

                result = AgentResult(
                    success=True,
                    message=response,
                    data={
                        'markets_analyzed': len(markets),
                        'signals': signals,
                        'analysis': analysis,
                        'categories': self._count_categories(markets),
                        'total_volume': sum(m.get('volume', 0) for m in markets),
                    },
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

                # Session 763: Create Mission Control attention item
                self._maybe_create_attention_item(result, task, context)

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Prediction Market: {task[:80]}",
                    content=result.message,
                    deliverable_type='analysis',
                    category='Prediction Markets',
                    tags=['prediction', 'markets'],
                    metadata={'task': task[:200]},
                )

                return result

            except Exception as e:
                logger.error(f"PredictionMarketAnalyst error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    message=f"Analysis failed: {str(e)}",
                    data={},
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

    def _get_kalshi_markets(self, context: Dict) -> List[Dict]:
        """Fetch markets from Kalshi spider."""
        try:
            from ai_core.spiders.specialized.kalshi_spider import KalshiSpider

            spider = KalshiSpider()
            category = context.get('category')

            if category:
                markets = spider.get_markets_by_category(category)
            else:
                markets = spider.fetch_data(max_results=100)

            # Filter to prediction markets only
            return [m for m in markets if m.get('data_type') == 'prediction_market']

        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
            return []

    def _analyze_markets(self, markets: List[Dict], task: str, context: Dict) -> Dict:
        """Analyze markets for patterns and opportunities."""
        analysis = {
            'high_conviction': [],  # >80% probability
            'contrarian_opportunities': [],  # Potentially mispriced
            'momentum_plays': [],  # Fast-moving probabilities
            'uncertain_markets': [],  # 40-60% probability (toss-ups)
            'high_volume': [],  # >50k volume (smart money)
            'category_breakdown': {},
        }

        for market in markets:
            prob = market.get('implied_probability_pct', 50)
            volume = market.get('volume', 0)
            category = market.get('category', 'general')

            # Track by category
            if category not in analysis['category_breakdown']:
                analysis['category_breakdown'][category] = []
            analysis['category_breakdown'][category].append(market)

            # High conviction (likely outcomes)
            if prob >= 80 or prob <= 20:
                analysis['high_conviction'].append({
                    'market': market,
                    'direction': 'YES' if prob >= 80 else 'NO',
                    'confidence': abs(prob - 50) / 50,  # 0-1 scale
                })

            # Uncertain / toss-up markets
            if 40 <= prob <= 60:
                analysis['uncertain_markets'].append(market)

            # High volume (smart money indicators)
            if volume >= 50000:
                analysis['high_volume'].append(market)

        return analysis

    def _generate_signals(self, markets: List[Dict], analysis: Dict) -> List[Dict]:
        """Generate trading signals from analysis."""
        signals = []

        # High conviction signals
        for item in analysis['high_conviction'][:5]:
            market = item['market']
            signals.append({
                'type': 'HIGH_CONVICTION',
                'ticker': market.get('ticker'),
                'title': market.get('title'),
                'direction': item['direction'],
                'probability': market.get('implied_probability_pct'),
                'volume': market.get('volume', 0),
                'confidence': item['confidence'],
                'reasoning': f"Market shows {item['direction']} at {market.get('implied_probability_pct'):.1f}% with {market.get('volume', 0):,} volume",
                'suggested_size': 'medium' if item['confidence'] > 0.6 else 'small',
            })

        # Uncertain market signals (potential value plays)
        for market in analysis['uncertain_markets'][:3]:
            if market.get('volume', 0) >= 10000:  # Only liquid markets
                signals.append({
                    'type': 'UNCERTAIN_VALUE',
                    'ticker': market.get('ticker'),
                    'title': market.get('title'),
                    'direction': 'RESEARCH',
                    'probability': market.get('implied_probability_pct'),
                    'volume': market.get('volume', 0),
                    'confidence': 0.5,
                    'reasoning': f"Toss-up market at {market.get('implied_probability_pct'):.1f}% - research for edge",
                    'suggested_size': 'small',
                })

        # High volume signals
        for market in analysis['high_volume'][:3]:
            prob = market.get('implied_probability_pct', 50)
            if 30 <= prob <= 70:  # Not already in high conviction
                signals.append({
                    'type': 'SMART_MONEY',
                    'ticker': market.get('ticker'),
                    'title': market.get('title'),
                    'direction': 'WATCH',
                    'probability': prob,
                    'volume': market.get('volume', 0),
                    'confidence': 0.6,
                    'reasoning': f"High volume ({market.get('volume', 0):,}) indicates smart money interest",
                    'suggested_size': 'medium',
                })

        return signals

    def _generate_analysis_report(self, task: str, markets: List[Dict],
                                   analysis: Dict, signals: List[Dict],
                                   context: Dict) -> str:
        """Generate natural language analysis report using LLM."""
        try:
            from openai import OpenAI
            import os

            client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

            # Prepare market summary
            market_summary = []
            for market in markets[:15]:  # Top 15 by volume
                market_summary.append({
                    'title': market.get('title', '')[:80],
                    'probability': market.get('implied_probability_pct'),
                    'volume': market.get('volume', 0),
                    'category': market.get('category'),
                })

            prompt = f"""Analyze these prediction markets and provide insights:

Task: {task}

Markets (top 15 by volume):
{json.dumps(market_summary, indent=2)}

Analysis Summary:
- High conviction markets: {len(analysis['high_conviction'])}
- Uncertain/toss-up markets: {len(analysis['uncertain_markets'])}
- High volume markets: {len(analysis['high_volume'])}
- Categories: {list(analysis['category_breakdown'].keys())}

Generated Signals: {len(signals)}

Provide a concise analysis covering:
1. Key market themes today
2. Top opportunities (with reasoning)
3. What to watch (potential movers)
4. Risk factors

Keep it actionable and under 400 words."""

            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=800,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
            # Fallback to basic report
            return self._basic_report(markets, signals)

    def _basic_report(self, markets: List[Dict], signals: List[Dict]) -> str:
        """Generate basic report without LLM."""
        lines = [
            f"**Prediction Market Analysis**",
            f"Analyzed {len(markets)} markets, generated {len(signals)} signals.",
            "",
            "**Top Signals:**"
        ]

        for signal in signals[:5]:
            lines.append(f"- [{signal['type']}] {signal['title'][:50]}... ({signal['probability']:.0f}%)")

        return "\n".join(lines)

    def _count_categories(self, markets: List[Dict]) -> Dict[str, int]:
        """Count markets by category."""
        counts = {}
        for market in markets:
            cat = market.get('category', 'general')
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _elapsed_ms(self, start_time: datetime) -> int:
        """Calculate elapsed time in milliseconds."""
        return int((datetime.now() - start_time).total_seconds() * 1000)
