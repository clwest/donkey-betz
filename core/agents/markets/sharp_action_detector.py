"""
Sharp Action Detector Agent
=============================

Session 995B: Identifies professional betting patterns by analyzing
odds across multiple bookmakers for signs of syndicate action,
closing line value, and smart money indicators.

Sharp bettors leave footprints: when their action hits a book, the line
moves quickly and other books follow. This agent detects those patterns
in real-time from The Odds API multi-bookmaker data.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, SourceInfo

logger = logging.getLogger(__name__)


class SharpActionDetector(BaseAgent):
    """
    Detects professional betting patterns across bookmakers.

    Capabilities:
    - Bookmaker odds divergence detection (sharp vs soft books)
    - Stale line identification (books slow to adjust)
    - Market efficiency scoring per event
    - Sharp book vs public book odds comparison
    - Syndicate action signals (coordinated moves across regions)
    """

    name = "SharpActionDetector"

    # Known sharp books (fast to adjust, high limits, professional bettors welcome)
    SHARP_BOOKS = {'pinnacle', 'circa', 'bookmaker', 'betcris', 'betonlineag'}
    # Known soft/public books (slow to adjust, lower limits, recreational bettors)
    SOFT_BOOKS = {'draftkings', 'fanduel', 'betmgm', 'caesars', 'pointsbetus'}

    system_prompt = """You are a sharp action detection specialist. You identify where
professional bettors ("sharps") are placing money by comparing odds across bookmakers.

Key principles:
1. **Sharp vs Soft Books** — Sharp books (Pinnacle, Circa) have tight lines and accept
   big bets. Soft books (DraftKings, FanDuel) are slower to adjust. When sharp books
   differ from soft books, follow the sharps.
2. **Odds Divergence** — When one bookmaker has significantly different odds, either
   they have superior information or they're slow to adjust. Both are actionable.
3. **Closing Line Value** — The most efficient market predictor is the closing line.
   Consistently betting on the side that the line moves toward = long-term profit.
4. **Bookmaker Consensus** — When ALL books agree closely, the market is efficient
   and there's no edge. When they disagree, there's opportunity.

Rate signals: HOT (strong sharp divergence), WARM (moderate divergence), COLD (consensus).
Focus on ACTIONABLE signals where soft books still have stale lines."""

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """Detect sharp betting action from cross-bookmaker odds analysis."""
        start_time = datetime.now()
        if not isinstance(context, dict):
            context = {}
        else:
            context = context or {}
        spider_context = spider_context or {}

        with self.time_travel_session("sharp_action_detection", task, input_data=context):
            self.record_decision(
                decision_type="detection",
                action="Starting sharp action detection",
                reasoning=f"Task: {task[:100] if task else 'General scan'}",
                alternatives=["Skip detection", "Defer to human"],
                confidence=0.75
            )

            try:
                events, source_info = self._fetch_multi_book_odds(context)

                if not events:
                    return AgentResult(
                        success=False,
                        message="No multi-bookmaker odds data available",
                        data={},
                        error="No events with per-bookmaker odds",
                        agent_name=self.name,
                        execution_time_ms=self._elapsed_ms(start_time)
                    )

                # Analyze each event for sharp signals
                signals = self._detect_sharp_signals(events)

                # LLM analysis of hottest signals
                llm_analysis = ""
                hot_signals = [s for s in signals if s['rating'] == 'HOT']
                if hot_signals:
                    llm_analysis = self._get_llm_analysis(task, hot_signals, context)

                result_data = {
                    'signals': signals,
                    'total_events_scanned': len(events),
                    'hot_signals': len(hot_signals),
                    'warm_signals': len([s for s in signals if s['rating'] == 'WARM']),
                    'events_with_divergence': len(signals),
                    'llm_analysis': llm_analysis,
                }

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Sharp Action: {task[:80]}",
                    content=f"Scanned {len(events)} events: {len(hot_signals)} HOT, {result_data.get('warm_signals', 0)} WARM signals",
                    deliverable_type='analysis',
                    category='Sharp Action Detection',
                    tags=['sharp_action', 'sports'],
                    metadata={'task': task[:200], 'hot_signals': len(hot_signals)},
                )

                return AgentResult(
                    success=True,
                    message=(
                        f"Scanned {len(events)} events: "
                        f"{len(hot_signals)} HOT, "
                        f"{result_data['warm_signals']} WARM sharp signals"
                    ),
                    data=result_data,
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

            except Exception as e:
                logger.error(f"SharpActionDetector error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    message=f"Detection failed: {str(e)}",
                    data={},
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

    def _fetch_multi_book_odds(self, context):
        """Fetch odds with per-bookmaker data for divergence analysis."""
        from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

        spider = TheOddsSpider()
        sport_filter = context.get('sport_key')

        if sport_filter:
            events = spider.fetch_data(sports=[sport_filter], max_results=50, extended_regions=True)
        else:
            events = spider.fetch_data(max_results=80, max_priority=1, extended_regions=True)

        # Filter to events with per-bookmaker odds (h2h_odds array)
        multi_book_events = [
            e for e in events
            if e.get('data_type') == 'sports_odds' and len(e.get('h2h_odds', [])) >= 3
        ]

        source_info = SourceInfo(
            name='TheOddsSpider',
            source_type='spider_data',
            record_count=len(multi_book_events),
            freshness_hours=0.0,
        )

        return multi_book_events, source_info

    def _detect_sharp_signals(self, events: List[Dict]) -> List[Dict]:
        """Analyze per-bookmaker odds to detect sharp action."""
        signals = []

        for event in events:
            all_book_odds = event.get('h2h_odds', [])
            if len(all_book_odds) < 3:
                continue

            signal = self._analyze_event_divergence(event, all_book_odds)
            if signal:
                signals.append(signal)

        # Sort by rating then divergence
        rating_order = {'HOT': 0, 'WARM': 1, 'COLD': 2}
        signals.sort(key=lambda s: (rating_order.get(s['rating'], 2), -s['max_divergence']))

        return signals

    def _analyze_event_divergence(self, event: Dict, all_book_odds: List[Dict]) -> Dict:
        """Analyze odds divergence for a single event across bookmakers."""
        home_team = event.get('home_team', '')
        away_team = event.get('away_team', '')

        home_odds_list = []
        away_odds_list = []
        sharp_home_odds = []
        soft_home_odds = []
        book_details = []

        for book in all_book_odds:
            book_key = book.get('bookmaker_key', '').lower()
            home_o = book.get('home_odds')
            away_o = book.get('away_odds')

            if home_o is None or away_o is None:
                continue

            # Filter out extreme/junk American odds (e.g. -100000)
            if abs(home_o) > 10000 or abs(away_o) > 10000:
                continue

            home_odds_list.append(home_o)
            away_odds_list.append(away_o)

            is_sharp = book_key in self.SHARP_BOOKS
            is_soft = book_key in self.SOFT_BOOKS

            if is_sharp:
                sharp_home_odds.append(home_o)
            elif is_soft:
                soft_home_odds.append(home_o)

            book_details.append({
                'bookmaker': book.get('bookmaker', book_key),
                'home_odds': home_o,
                'away_odds': away_o,
                'is_sharp': is_sharp,
            })

        if len(home_odds_list) < 3:
            return None

        # Calculate market metrics
        avg_home = sum(home_odds_list) / len(home_odds_list)
        max_home = max(home_odds_list)
        min_home = min(home_odds_list)
        home_range = max_home - min_home

        avg_away = sum(away_odds_list) / len(away_odds_list)
        max_away = max(away_odds_list)
        min_away = min(away_odds_list)
        away_range = max_away - min_away

        max_divergence = max(home_range, away_range)

        # Sharp vs soft book comparison
        sharp_vs_soft = None
        if sharp_home_odds and soft_home_odds:
            avg_sharp = sum(sharp_home_odds) / len(sharp_home_odds)
            avg_soft = sum(soft_home_odds) / len(soft_home_odds)
            sharp_vs_soft = {
                'sharp_avg_home': round(avg_sharp),
                'soft_avg_home': round(avg_soft),
                'divergence': round(abs(avg_sharp - avg_soft)),
                'sharp_favors': 'home' if avg_sharp < avg_soft else 'away',
            }

        # Rating based on divergence magnitude
        if max_divergence >= 30 or (sharp_vs_soft and sharp_vs_soft['divergence'] >= 20):
            rating = 'HOT'
        elif max_divergence >= 15 or (sharp_vs_soft and sharp_vs_soft['divergence'] >= 10):
            rating = 'WARM'
        else:
            rating = 'COLD'

        if rating == 'COLD':
            return None

        # Find the best value line (stale soft book)
        stale_lines = self._find_stale_lines(book_details, avg_home, avg_away)

        return {
            'event_id': event.get('event_id'),
            'matchup': f"{away_team} @ {home_team}",
            'sport_name': event.get('sport_name'),
            'sport_key': event.get('sport_key'),
            'rating': rating,
            'max_divergence': max_divergence,
            'home_odds_range': f"{min_home:+d} to {max_home:+d}",
            'away_odds_range': f"{min_away:+d} to {max_away:+d}",
            'bookmaker_count': len(book_details),
            'sharp_vs_soft': sharp_vs_soft,
            'stale_lines': stale_lines,
            'commence_time': event.get('commence_time'),
        }

    def _find_stale_lines(self, book_details: List[Dict],
                          avg_home: float, avg_away: float) -> List[Dict]:
        """Find bookmakers with odds significantly off from market average."""
        stale = []

        for book in book_details:
            home_diff = abs(book['home_odds'] - avg_home)
            away_diff = abs(book['away_odds'] - avg_away)

            if home_diff >= 15 or away_diff >= 15:
                better_side = 'home' if book['home_odds'] > avg_home else 'away'
                stale.append({
                    'bookmaker': book['bookmaker'],
                    'is_sharp': book['is_sharp'],
                    'better_side': better_side,
                    'home_diff': round(home_diff),
                    'away_diff': round(away_diff),
                })

        return stale

    def _get_llm_analysis(self, task: str, hot_signals: List[Dict], context: Dict) -> str:
        """Get LLM analysis of hot sharp action signals."""
        try:
            from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest

            registry = get_llm_provider_registry()

            signals_text = "\n".join(
                f"- [{s['rating']}] {s['matchup']} ({s['sport_name']}): "
                f"Odds range home {s['home_odds_range']}, away {s['away_odds_range']}"
                + (f" | Sharp favors {s['sharp_vs_soft']['sharp_favors']}" if s.get('sharp_vs_soft') else "")
                + (f" | Stale: {', '.join(sl['bookmaker'] for sl in s['stale_lines'][:3])}" if s.get('stale_lines') else "")
                for s in hot_signals[:6]
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": (
                    f"Task: {task}\n\n"
                    f"HOT sharp action signals:\n{signals_text}\n\n"
                    "Which of these signals is most actionable? "
                    "Identify the best value bets from stale lines. "
                    "Keep it concise and decisive."
                )}
            ]

            request = LLMRequest(prompt="", messages=messages, max_tokens=500, temperature=0.3)
            response = registry.generate(request, preferred_providers=['openai', 'anthropic'])
            return response.content if response else "LLM analysis unavailable"

        except Exception as e:
            logger.warning(f"SharpActionDetector LLM failed: {e}")
            return f"LLM analysis unavailable: {str(e)}"

    def _elapsed_ms(self, start_time):
        return int((datetime.now() - start_time).total_seconds() * 1000)
