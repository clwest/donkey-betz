"""
Line Movement Analyzer Agent
==============================

Session 995B: Detects meaningful line movements across bookmakers to identify
sharp money action, reverse line movement, and steam moves.

Compares current odds against stored snapshots from the
snapshot_odds_for_line_movement task to detect where professional
bettors are placing significant action.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import (
    build_provenance, SourceInfo,
)

logger = logging.getLogger(__name__)


class LineMovementAnalyzer(BaseAgent):
    """
    Detects sharp money movements and line value shifts.

    Capabilities:
    - Reverse line movement detection (line moves opposite to public betting)
    - Steam move identification (sudden sharp line moves across multiple books)
    - Opening vs current line comparison
    - Bookmaker consensus drift analysis
    - Sharp vs public money disagree signals
    """

    name = "LineMovementAnalyzer"

    system_prompt = """You are an expert line movement analyst. You detect where professional
("sharp") bettors are placing money by analyzing how betting lines move.

Key concepts:
1. **Reverse Line Movement (RLM)** — When 70%+ of public bets are on Team A,
   but the line moves TOWARD Team A (making them more expensive). This means
   sharps are betting Team B with enough money to move the line despite public volume.
2. **Steam Moves** — When a line moves 1+ points in minutes across multiple books
   simultaneously. Indicates coordinated sharp action.
3. **Closing Line Value (CLV)** — The closing line is the most efficient. If you
   consistently beat the closing line, you're a winning bettor long-term.
4. **Stale Lines** — Books that are slow to adjust create temporary value windows.

Your job: Identify the MOST actionable line movements, explain WHY the line moved,
and assess whether the current line still has value or if it's already been corrected.

Rate movements: STEAM (urgent), SHARP (high value), DRIFT (moderate), NOISE (ignore)."""

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """Analyze line movements across bookmakers."""
        start_time = datetime.now()
        if not isinstance(context, dict):
            context = {}
        else:
            context = context or {}
        spider_context = spider_context or {}

        with self.time_travel_session("line_movement_analysis", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting line movement analysis",
                reasoning=f"Task: {task[:100] if task else 'General analysis'}",
                alternatives=["Skip analysis", "Defer to human"],
                confidence=0.75
            )

            try:
                # Fetch current odds
                current_events, source_info = self._fetch_current_odds(context)

                if not current_events:
                    return AgentResult(
                        success=False,
                        message="No current odds data available",
                        data={},
                        error="TheOddsSpider returned no events",
                        agent_name=self.name,
                        execution_time_ms=self._elapsed_ms(start_time)
                    )

                # Load previous snapshots for comparison
                snapshots = self._load_odds_snapshots()

                # Detect movements
                movements = self._detect_movements(current_events, snapshots)

                # Get LLM analysis of significant movements
                llm_analysis = ""
                significant = [m for m in movements if m['rating'] in ('STEAM', 'SHARP')]
                if significant:
                    llm_analysis = self._get_llm_analysis(task, significant, context)

                result_data = {
                    'movements': movements,
                    'total_games_analyzed': len(current_events),
                    'total_movements': len(movements),
                    'steam_moves': len([m for m in movements if m['rating'] == 'STEAM']),
                    'sharp_moves': len([m for m in movements if m['rating'] == 'SHARP']),
                    'drift_moves': len([m for m in movements if m['rating'] == 'DRIFT']),
                    'snapshots_compared': len(snapshots),
                    'llm_analysis': llm_analysis,
                }

                return AgentResult(
                    success=True,
                    message=(
                        f"Analyzed {len(current_events)} games: "
                        f"{result_data['steam_moves']} steam, "
                        f"{result_data['sharp_moves']} sharp, "
                        f"{result_data['drift_moves']} drift moves detected"
                    ),
                    data=result_data,
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

            except Exception as e:
                logger.error(f"LineMovementAnalyzer error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    message=f"Analysis failed: {str(e)}",
                    data={},
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

    def _fetch_current_odds(self, context):
        """Fetch current odds from TheOddsSpider."""
        from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

        spider = TheOddsSpider()
        sport_filter = context.get('sport_key')

        if sport_filter:
            events = spider.fetch_data(sports=[sport_filter], max_results=50, extended_regions=True)
        else:
            events = spider.fetch_data(max_results=80, max_priority=1, extended_regions=True)

        odds_events = [e for e in events if e.get('data_type') == 'sports_odds']

        source_info = SourceInfo(
            name='TheOddsSpider',
            source_type='spider_data',
            record_count=len(odds_events),
            freshness_hours=0.0,
        )

        return odds_events, source_info

    def _load_odds_snapshots(self) -> Dict[str, Dict]:
        """Load previous odds snapshots from SpiderData for line comparison."""
        from core.models_unified_system import SpiderData
        from django.utils import timezone
        from datetime import timedelta

        snapshots = {}
        cutoff = timezone.now() - timedelta(hours=24)

        try:
            recent_odds = SpiderData.objects.filter(
                spider_name='theodds',
                data_type='sports_odds',
                created_at__gte=cutoff,
            ).order_by('created_at')[:500]

            for record in recent_odds:
                raw = record.raw_data or {}
                event_id = raw.get('event_id', '')
                if event_id and event_id not in snapshots:
                    snapshots[event_id] = {
                        'home_odds': raw.get('home_odds'),
                        'away_odds': raw.get('away_odds'),
                        'home_spread': raw.get('home_spread'),
                        'total_line': raw.get('total_line'),
                        'snapshot_time': str(record.created_at),
                        'home_team': raw.get('home_team'),
                        'away_team': raw.get('away_team'),
                    }
        except Exception as e:
            logger.warning(f"Could not load odds snapshots: {e}")

        return snapshots

    def _detect_movements(self, current_events: List[Dict], snapshots: Dict) -> List[Dict]:
        """Compare current odds to snapshots and detect meaningful movements."""
        movements = []

        for event in current_events:
            event_id = event.get('event_id', '')
            if event_id not in snapshots:
                continue

            snap = snapshots[event_id]
            movement = self._compare_odds(event, snap)

            if movement:
                movements.append(movement)

        # Sort by significance (STEAM > SHARP > DRIFT)
        rating_order = {'STEAM': 0, 'SHARP': 1, 'DRIFT': 2, 'NOISE': 3}
        movements.sort(key=lambda m: rating_order.get(m['rating'], 3))

        return movements

    def _compare_odds(self, current: Dict, snapshot: Dict) -> Dict:
        """Compare current odds to a snapshot and classify the movement."""
        home_team = current.get('home_team', '')
        away_team = current.get('away_team', '')

        # Moneyline movement
        curr_home = current.get('home_odds')
        prev_home = snapshot.get('home_odds')
        curr_away = current.get('away_odds')
        prev_away = snapshot.get('away_odds')

        # Spread movement
        curr_spread = current.get('home_spread')
        prev_spread = snapshot.get('home_spread')

        # Total movement
        curr_total = current.get('total_line')
        prev_total = snapshot.get('total_line')

        changes = []
        max_significance = 0

        # Check moneyline movement
        if curr_home and prev_home and curr_away and prev_away:
            ml_shift = abs(curr_home - prev_home)
            if ml_shift >= 5:
                direction = "toward" if curr_home < prev_home else "away from"
                changes.append(
                    f"Moneyline: {home_team} moved {direction} favorite "
                    f"({prev_home:+d} → {curr_home:+d})"
                )
                max_significance = max(max_significance, ml_shift)

        # Check spread movement
        if curr_spread is not None and prev_spread is not None:
            try:
                spread_shift = abs(float(curr_spread) - float(prev_spread))
                if spread_shift >= 0.5:
                    direction = "grew" if abs(float(curr_spread)) > abs(float(prev_spread)) else "shrank"
                    changes.append(
                        f"Spread: {home_team} spread {direction} "
                        f"({float(prev_spread):+.1f} → {float(curr_spread):+.1f})"
                    )
                    max_significance = max(max_significance, spread_shift * 20)
            except (ValueError, TypeError):
                pass

        # Check total movement
        if curr_total is not None and prev_total is not None:
            try:
                total_shift = abs(float(curr_total) - float(prev_total))
                if total_shift >= 0.5:
                    direction = "up" if float(curr_total) > float(prev_total) else "down"
                    changes.append(
                        f"Total: {direction} ({float(prev_total):.1f} → {float(curr_total):.1f})"
                    )
                    max_significance = max(max_significance, total_shift * 15)
            except (ValueError, TypeError):
                pass

        if not changes:
            return None

        # Rate the movement
        if max_significance >= 30:
            rating = 'STEAM'
        elif max_significance >= 15:
            rating = 'SHARP'
        elif max_significance >= 5:
            rating = 'DRIFT'
        else:
            rating = 'NOISE'

        if rating == 'NOISE':
            return None

        return {
            'event_id': current.get('event_id'),
            'matchup': f"{away_team} @ {home_team}",
            'sport_name': current.get('sport_name'),
            'sport_key': current.get('sport_key'),
            'rating': rating,
            'significance': round(max_significance, 1),
            'changes': changes,
            'current_odds': {
                'home_odds': curr_home,
                'away_odds': curr_away,
                'spread': curr_spread,
                'total': curr_total,
            },
            'previous_odds': {
                'home_odds': prev_home,
                'away_odds': prev_away,
                'spread': prev_spread,
                'total': prev_total,
            },
            'snapshot_time': snapshot.get('snapshot_time'),
            'commence_time': current.get('commence_time'),
        }

    def _get_llm_analysis(self, task: str, significant_moves: List[Dict], context: Dict) -> str:
        """Get LLM analysis of significant line movements."""
        try:
            from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest

            registry = get_llm_provider_registry()

            moves_text = "\n".join(
                f"- [{m['rating']}] {m['matchup']} ({m['sport_name']}): "
                + "; ".join(m['changes'])
                for m in significant_moves[:6]
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": (
                    f"Task: {task}\n\n"
                    f"Significant line movements detected:\n{moves_text}\n\n"
                    "Analyze these movements. Which are most likely sharp money? "
                    "Which still have value? Any reverse line movement signals? "
                    "Keep it concise — actionable insights only."
                )}
            ]

            request = LLMRequest(prompt="", messages=messages, max_tokens=500, temperature=0.3)
            response = registry.generate(request, preferred_providers=['openai', 'anthropic'])
            return response.content if response else "LLM analysis unavailable"

        except Exception as e:
            logger.warning(f"LineMovementAnalyzer LLM failed: {e}")
            return f"LLM analysis unavailable: {str(e)}"

    def _elapsed_ms(self, start_time):
        return int((datetime.now() - start_time).total_seconds() * 1000)
