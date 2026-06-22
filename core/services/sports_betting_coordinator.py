"""
Sports Betting Coordinator
===========================

Session 995B: Orchestrates the sports betting intelligence pipeline,
similar to MarketIntelligenceCoordinator for stocks.

Runs GamePredictor + SportsOddsAnalyst + ArbitrageDetector + LineMovementAnalyzer
+ SharpActionDetector to generate comprehensive daily/nightly slate analysis briefs.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from django.utils import timezone

logger = logging.getLogger(__name__)


class SportsBettingCoordinator:
    """
    Orchestrates multi-agent sports betting analysis into unified briefs.

    Pipeline:
    1. GamePredictor — score/outcome predictions
    2. SportsOddsAnalyst — value bets and market analysis
    3. ArbitrageDetector — cross-book arbitrage opportunities
    4. LineMovementAnalyzer — sharp money movements
    5. SharpActionDetector — professional betting patterns

    Produces a unified brief combining all signals with confidence ranking.
    """

    def __init__(self, user=None, sport_key: str = None):
        self.user = user
        self.sport_key = sport_key

    def generate_brief(self) -> Dict[str, Any]:
        """
        Generate a comprehensive sports betting brief by running all agents.

        Returns:
            Dict with combined analysis from all agents plus executive summary.
        """
        start_time = datetime.now()
        brief = {
            'generated_at': timezone.now().isoformat(),
            'sport_filter': self.sport_key,
            'agents_run': [],
            'errors': [],
        }

        context = {}
        if self.sport_key:
            context['sport_key'] = self.sport_key

        # Run agents — each is independent, continue on failure
        predictions = self._run_game_predictor(context)
        brief['predictions'] = predictions
        if predictions:
            brief['agents_run'].append('GamePredictor')

        odds_analysis = self._run_odds_analyst(context)
        brief['odds_analysis'] = odds_analysis
        if odds_analysis:
            brief['agents_run'].append('SportsOddsAnalyst')

        arbitrage = self._run_arbitrage_detector(context)
        brief['arbitrage'] = arbitrage
        if arbitrage:
            brief['agents_run'].append('ArbitrageDetector')

        line_movements = self._run_line_movement_analyzer(context)
        brief['line_movements'] = line_movements
        if line_movements:
            brief['agents_run'].append('LineMovementAnalyzer')

        sharp_action = self._run_sharp_action_detector(context)
        brief['sharp_action'] = sharp_action
        if sharp_action:
            brief['agents_run'].append('SharpActionDetector')

        # Build executive summary
        brief['executive_summary'] = self._build_executive_summary(brief)
        brief['top_plays'] = self._extract_top_plays(brief)

        elapsed = (datetime.now() - start_time).total_seconds()
        brief['generation_time_seconds'] = round(elapsed, 1)

        logger.info(
            f"[BETTING-BRIEF] Generated brief in {elapsed:.1f}s — "
            f"{len(brief['agents_run'])} agents, {len(brief['top_plays'])} top plays"
        )

        return brief

    def _run_game_predictor(self, context: Dict) -> Optional[Dict]:
        """Run GamePredictor agent."""
        try:
            from core.agents.markets.game_predictor import GamePredictor
            agent = GamePredictor()
            result = agent.execute(
                task="Generate predictions for today's games",
                context=context
            )
            if result.success:
                return result.data
            else:
                logger.warning(f"GamePredictor failed: {result.error}")
                return None
        except Exception as e:
            logger.error(f"GamePredictor error: {e}")
            return None

    def _run_odds_analyst(self, context: Dict) -> Optional[Dict]:
        """Run SportsOddsAnalyst agent."""
        try:
            from core.agents.markets.sports_odds_analyst import SportsOddsAnalyst
            # Session 1206: .run() writes AgentExecution telemetry row (Layer 1 audit)
            agent = SportsOddsAnalyst()
            result = agent.run(
                task="Analyze today's betting markets for value opportunities",
                context=context
            )
            if result.success:
                return result.data
            else:
                logger.warning(f"SportsOddsAnalyst failed: {result.error}")
                return None
        except Exception as e:
            logger.error(f"SportsOddsAnalyst error: {e}")
            return None

    def _run_arbitrage_detector(self, context: Dict) -> Optional[Dict]:
        """Run ArbitrageDetector agent."""
        try:
            from core.agents.markets.arbitrage_detector import ArbitrageDetector
            agent = ArbitrageDetector()
            result = agent.execute(
                task="Scan for arbitrage opportunities across all active sports",
                context=context
            )
            if result.success:
                return result.data
            else:
                logger.warning(f"ArbitrageDetector failed: {result.error}")
                return None
        except Exception as e:
            logger.error(f"ArbitrageDetector error: {e}")
            return None

    def _run_line_movement_analyzer(self, context: Dict) -> Optional[Dict]:
        """Run LineMovementAnalyzer agent."""
        try:
            from core.agents.markets.line_movement_analyzer import LineMovementAnalyzer
            agent = LineMovementAnalyzer()
            result = agent.execute(
                task="Detect sharp money line movements in today's games",
                context=context
            )
            if result.success:
                return result.data
            else:
                logger.warning(f"LineMovementAnalyzer failed: {result.error}")
                return None
        except Exception as e:
            logger.error(f"LineMovementAnalyzer error: {e}")
            return None

    def _run_sharp_action_detector(self, context: Dict) -> Optional[Dict]:
        """Run SharpActionDetector agent."""
        try:
            from core.agents.markets.sharp_action_detector import SharpActionDetector
            agent = SharpActionDetector()
            result = agent.execute(
                task="Identify sharp betting action and stale lines",
                context=context
            )
            if result.success:
                return result.data
            else:
                logger.warning(f"SharpActionDetector failed: {result.error}")
                return None
        except Exception as e:
            logger.error(f"SharpActionDetector error: {e}")
            return None

    def _build_executive_summary(self, brief: Dict) -> str:
        """Build a text executive summary from all agent outputs."""
        parts = []
        parts.append(f"Sports Betting Brief — {timezone.now().strftime('%B %d, %Y %I:%M %p')}")

        # Predictions summary
        preds = brief.get('predictions') or {}
        pred_count = preds.get('predictions_generated', 0)
        if pred_count:
            top = preds.get('predictions', [])[:3]
            top_str = ", ".join(
                f"{p['predicted_winner']} ({p['confidence']}%)" for p in top
            )
            parts.append(f"Predictions: {pred_count} games analyzed. Top picks: {top_str}")

        # Arbitrage summary
        arb = brief.get('arbitrage') or {}
        arb_opps = arb.get('arbitrage_opportunities', [])
        if arb_opps:
            hot = [a for a in arb_opps if a.get('rating') == 'HOT']
            parts.append(f"Arbitrage: {len(arb_opps)} opportunities ({len(hot)} HOT)")

        # Line movement summary
        lm = brief.get('line_movements') or {}
        steam = lm.get('steam_moves', 0)
        sharp = lm.get('sharp_moves', 0)
        if steam or sharp:
            parts.append(f"Line Movements: {steam} steam moves, {sharp} sharp moves")

        # Sharp action summary
        sa = brief.get('sharp_action') or {}
        hot_signals = sa.get('hot_signals', 0)
        warm_signals = sa.get('warm_signals', 0)
        if hot_signals or warm_signals:
            parts.append(f"Sharp Action: {hot_signals} HOT signals, {warm_signals} WARM signals")

        return "\n".join(parts)

    def _extract_top_plays(self, brief: Dict) -> List[Dict]:
        """Extract the best plays across all agent outputs, ranked by confidence."""
        plays = []

        # High-confidence predictions
        preds = brief.get('predictions') or {}
        for p in (preds.get('predictions') or [])[:5]:
            if p.get('confidence', 0) >= 65:
                plays.append({
                    'source': 'GamePredictor',
                    'type': 'prediction',
                    'matchup': p.get('matchup'),
                    'pick': p.get('predicted_winner'),
                    'confidence': p.get('confidence'),
                    'sport': p.get('sport_name'),
                    'detail': f"{p.get('home_win_probability')}% home / {p.get('away_win_probability')}% away",
                })

        # HOT arbitrage opportunities
        arb = brief.get('arbitrage') or {}
        for a in (arb.get('arbitrage_opportunities') or []):
            if a.get('rating') in ('HOT', 'GOOD'):
                plays.append({
                    'source': 'ArbitrageDetector',
                    'type': 'arbitrage',
                    'matchup': a.get('matchup', a.get('event', '')),
                    'pick': f"Arb: {a.get('profit_pct', 0):.1f}% guaranteed",
                    'confidence': 90 if a.get('rating') == 'HOT' else 75,
                    'sport': a.get('sport'),
                    'detail': f"{a.get('home_book', '')} vs {a.get('away_book', '')}",
                })

        # STEAM line movements
        lm = brief.get('line_movements') or {}
        for m in (lm.get('movements') or []):
            if m.get('rating') == 'STEAM':
                plays.append({
                    'source': 'LineMovementAnalyzer',
                    'type': 'line_movement',
                    'matchup': m.get('matchup'),
                    'pick': '; '.join(m.get('changes', [])[:2]),
                    'confidence': 80,
                    'sport': m.get('sport_name'),
                    'detail': f"Significance: {m.get('significance')}",
                })

        # HOT sharp action
        sa = brief.get('sharp_action') or {}
        for s in (sa.get('signals') or []):
            if s.get('rating') == 'HOT' and s.get('sharp_vs_soft'):
                svs = s['sharp_vs_soft']
                plays.append({
                    'source': 'SharpActionDetector',
                    'type': 'sharp_action',
                    'matchup': s.get('matchup'),
                    'pick': f"Sharp favors {svs.get('sharp_favors', 'unknown')}",
                    'confidence': 85,
                    'sport': s.get('sport_name'),
                    'detail': f"Divergence: {svs.get('divergence')} pts between sharp/soft books",
                })

        # Sort by confidence
        plays.sort(key=lambda p: p.get('confidence', 0), reverse=True)
        return plays[:10]
