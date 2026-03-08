"""
Sports Odds Analyst Agent
==========================

Session 558: Analyzes sports betting odds from The Odds API to identify:
- Value bets (odds better than implied probability)
- Line movements (sharp money indicators)
- Arbitrage opportunities (bookmaker discrepancies)
- Toss-up games (close matchups for research)

Session 918: Added provenance tracking and structured JSON output.
- ReportProvenance block tracks data sources, timestamps, freshness
- SportsReportSchema provides structured output for downstream agents
- Publishing gates based on data freshness validation

Uses The Odds spider for real-time odds from 40+ bookmakers.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
import json

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from core.agents.report_schemas import (
    ReportProvenance, SportsReportSchema, GameAnalysis,
    Claim, Recommendation, RiskFlag, SourceInfo,
    build_provenance, format_disclaimer
)
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


# =============================================================================
# Session 683: ML Integration for Sports Odds (LSTM)
# =============================================================================

def analyze_odds_with_ml(odds_data: dict) -> dict:
    """Analyze sports odds using ML models for forecasting."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(data=odds_data, task_hint=TaskType.TIME_SERIES, max_models=2)
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'time_series'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'line_predictions': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML odds analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class SportsOddsAnalyst(BaseAgent):
    """
    Analyzes sports betting odds to identify value and opportunities.

    Capabilities:
    - Value bet detection (odds vs true probability)
    - Line movement analysis (sharp vs public money)
    - Cross-bookmaker arbitrage detection
    - Game matchup analysis
    - Sport-specific insights
    """

    name = "SportsOddsAnalyst"

    system_prompt = """You are a Sports Odds Analyst specializing in betting market analysis.

Your job is to analyze sports odds and provide actionable insights:

1. **Odds Analysis**
   - Convert American odds to implied probability
   - Identify value bets (odds > true probability)
   - Spot line movements (where is sharp money going?)
   - Find bookmaker discrepancies (arbitrage potential)

2. **Sport Expertise**
   - NFL: Spread analysis, totals, injury impacts
   - NBA: Rest days, back-to-backs, pace analysis
   - MLB: Pitching matchups, bullpen usage
   - NHL: Goalie matchups, home ice advantage
   - Soccer: Form, head-to-head, league positions
   - UFC: Style matchups, recent performance

3. **Signal Types**
   - VALUE BET: Odds offer positive expected value
   - SHARP MOVE: Line moved despite public betting other way
   - TOSS-UP: Close game worth researching
   - FADE PUBLIC: Go against heavy public betting
   - ARBITRAGE: Odds mismatch across books

4. **Key Metrics**
   - Implied Probability: What odds say will happen
   - Spread: Point differential expectation
   - Total (O/U): Combined score expectation
   - Moneyline: Straight up win probability
   - Book count: How many bookmakers offering

5. **Risk Factors**
   - Injury news (check before betting)
   - Weather (outdoor sports)
   - Motivation (playoff implications, rivalries)
   - Rest advantage (scheduling)
   - Home/away splits

Output Format:
- Be concise and actionable
- Include odds, probability, and edge estimate
- Flag risks (injuries, weather, news pending)
- Note timing (game start, line freshness)
- Suggest unit sizing (1-3 units based on confidence)

All times are in MST (Mountain Time).

Remember: Sharp money moves lines. Look for where the line went AGAINST public betting."""

    # Session 763: Mission Control configuration
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='opportunity',
        default_urgency='medium',
        min_confidence=0.0,
        actions=[
            {'id': 'watch', 'label': 'Watch Game', 'style': 'primary', 'description': 'Track this matchup'},
            {'id': 'paper_trade', 'label': 'Paper Trade', 'style': 'success', 'description': 'Record a paper bet'},
            {'id': 'research_more', 'label': 'Research', 'style': 'warning', 'description': 'Need more analysis'},
            {'id': 'pass', 'label': 'Pass', 'style': 'secondary', 'description': 'No bet'},
        ],
        payload_fields=['games_analyzed', 'value_bets', 'arbitrage_found'],
        max_items_per_hour=5
    )

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Analyze sports odds and generate betting insights.

        Args:
            task: Analysis request (e.g., "analyze NFL games today")
            context: Additional context (bankroll, preferences)
            scifi_context: Agent mood, memory, learning
            spider_context: Real-time odds from The Odds API spider

        Returns:
            AgentResult with odds analysis and betting signals
        """
        start_time = datetime.now()
        # Session 875: Ensure context is a dict (defensive fix for list being passed)
        if not isinstance(context, dict):
            logger.warning(f"SportsOddsAnalyst received non-dict context (type={type(context).__name__}), using empty dict")
            context = {}
        else:
            context = context or {}
        spider_context = spider_context or {}

        # Session 858: Extract user context for personalized betting analysis
        # Session 1102: Guard against stringified context values
        user_context = context.get('user', {})
        if not isinstance(user_context, dict):
            user_context = {}
        self._user_context = user_context

        # Session 858: Enhance task with user's betting preferences
        if user_context and user_context.get('has_user_context'):
            user_name = user_context.get('name', '')
            betting_prefs = user_context.get('betting_preferences', {})
            risk_tolerance = user_context.get('risk_tolerance', 'moderate')

            # Build user context addition to task
            user_context_parts = []
            if user_name:
                user_context_parts.append(f"Analyzing for: {user_name}")
            if betting_prefs:
                if betting_prefs.get('enabled'):
                    favorite_sports = betting_prefs.get('favorite_sports', [])
                    if favorite_sports:
                        sports_text = ", ".join(favorite_sports[:3]) if isinstance(favorite_sports, list) else str(favorite_sports)
                        user_context_parts.append(f"Favorite sports: {sports_text}")
                    bet_risk = betting_prefs.get('risk_level', risk_tolerance)
                    user_context_parts.append(f"Betting risk level: {bet_risk}")
                    bankroll = betting_prefs.get('bankroll')
                    if bankroll:
                        user_context_parts.append(f"Bankroll: ${bankroll}")

            if user_context_parts:
                task = f"{task}\n\n[Bettor Profile: {'; '.join(user_context_parts)}]"
                logger.info(f"🏈 Session 858: Enhanced sports analysis with betting profile for {user_name or 'user'}")

        # Session 750: Time Travel integration
        with self.time_travel_session("sports_odds_analysis", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting sports odds analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence")

            try:
                # Session 918: Fetch odds data with source tracking
                events, source_info = self._get_sports_odds(context)

                if not events:
                    return AgentResult(
                        success=False,
                        message="No sports odds data available",
                        data={},
                        error="The Odds API spider returned no data",
                        agent_name=self.name,
                        execution_time_ms=self._elapsed_ms(start_time)
                    )

                # Session 918: Build provenance block
                provenance = build_provenance(
                    report_type='sports_odds',
                    agent_name=self.name,
                    sources=[source_info],
                    stale_threshold_hours=2.0,  # Sports odds go stale fast
                )
                provenance.disclaimer = format_disclaimer('sports_odds')

                # Analyze odds
                analysis = self._analyze_odds(events, task, context)

                # Generate betting signals
                signals = self._generate_signals(events, analysis)

                # Session 918: Build structured report schema
                structured_report = self._build_structured_report(
                    events, analysis, signals, provenance
                )

                # Build response using LLM (includes provenance header)
                response = self._generate_analysis_report(
                    task, events, analysis, signals, context, provenance
                )

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
                        'events_analyzed': len(events),
                        'signals': signals,
                        'analysis': analysis,
                        'sports': self._count_sports(events),
                        'upcoming_24h': len([e for e in events if self._is_upcoming_24h(e)]),
                        # Session 918: Include structured output
                        'structured_report': structured_report.to_dict(),
                        'provenance': provenance.to_dict(),
                        'publishable': provenance.publishable,
                        'validation_status': provenance.validation_status,
                    },
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

                # Session 763: Create Mission Control attention item
                self._maybe_create_attention_item(result, task, context)

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Sports Odds Analysis: {task[:80]}",
                    content=result.message,
                    deliverable_type='analysis',
                    category='Sports Analysis',
                    tags=['odds', 'sports'],
                    metadata={'task': task[:200], 'events_analyzed': len(events)},
                )

                return result

            except Exception as e:
                logger.error(f"SportsOddsAnalyst error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    message=f"Analysis failed: {str(e)}",
                    data={},
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

    def _get_sports_odds(self, context: Dict) -> tuple:
        """
        Fetch odds from The Odds API spider.

        Session 918: Returns tuple of (events, source_info) for provenance tracking.

        Returns:
            Tuple of (List[Dict], Dict) - events and source metadata
        """
        source_info = {
            'name': 'TheOddsSpider',
            'endpoint': 'the-odds-api.com/v4/sports',
            'retrieved_at': datetime.now(timezone.utc).isoformat(),
            'record_count': 0,
        }

        try:
            from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

            spider = TheOddsSpider()
            sport = context.get('sport')

            if sport:
                # Map common names to API keys
                sport_map = {
                    'nfl': 'americanfootball_nfl',
                    'nba': 'basketball_nba',
                    'mlb': 'baseball_mlb',
                    'nhl': 'icehockey_nhl',
                    'soccer': None,  # Gets all soccer
                    'ufc': 'mma_mixed_martial_arts',
                }
                sport_key = sport_map.get(sport.lower(), sport)
                if sport_key:
                    events = spider.fetch_data(sports=[sport_key], max_results=50)
                else:
                    events = spider.fetch_data(max_results=100)
            else:
                events = spider.fetch_data(max_results=100)

            # Filter to sports odds only
            filtered_events = [e for e in events if e.get('data_type') == 'sports_odds']

            # Session 918: Update source info with actual record count
            source_info['record_count'] = len(filtered_events)

            return filtered_events, source_info

        except Exception as e:
            logger.error(f"Error fetching sports odds: {e}")
            return [], source_info

    def _analyze_odds(self, events: List[Dict], task: str, context: Dict) -> Dict:
        """Analyze odds for patterns and opportunities."""
        analysis = {
            'value_bets': [],  # Potential +EV opportunities
            'toss_ups': [],  # Close games (45-55% implied)
            'heavy_favorites': [],  # >70% implied probability
            'sharp_indicators': [],  # High book count, unusual lines
            'sport_breakdown': {},
            'upcoming_games': [],
        }

        for event in events:
            home_prob = event.get('home_implied_prob') or 50
            away_prob = event.get('away_implied_prob') or 50
            home_odds = event.get('home_odds')
            away_odds = event.get('away_odds')
            sport = event.get('sport_name', 'Unknown')
            book_count = event.get('bookmaker_count', 0) or 0

            # Track by sport
            if sport not in analysis['sport_breakdown']:
                analysis['sport_breakdown'][sport] = []
            analysis['sport_breakdown'][sport].append(event)

            # Upcoming games (next 24 hours)
            if self._is_upcoming_24h(event):
                analysis['upcoming_games'].append(event)

            # Toss-ups (close games)
            if 45 <= home_prob <= 55:
                analysis['toss_ups'].append({
                    'event': event,
                    'edge': abs(50 - home_prob),
                    'type': 'TOSS_UP',
                })

            # Heavy favorites (potential fades or ML value)
            if home_prob >= 70 or away_prob >= 70:
                favorite = event.get('home_team') if home_prob >= 70 else event.get('away_team')
                fav_prob = max(home_prob, away_prob)
                analysis['heavy_favorites'].append({
                    'event': event,
                    'favorite': favorite,
                    'probability': fav_prob,
                })

            # Sharp indicators (many books = liquid market)
            if book_count >= 8:
                # Look for spread value
                spread = event.get('home_spread')
                if spread is not None:
                    analysis['sharp_indicators'].append({
                        'event': event,
                        'book_count': book_count,
                        'spread': spread,
                        'reason': 'High book consensus',
                    })

        return analysis

    def _generate_signals(self, events: List[Dict], analysis: Dict) -> List[Dict]:
        """Generate betting signals from analysis."""
        signals = []

        # Toss-up signals (research opportunities)
        for item in analysis['toss_ups'][:5]:
            event = item['event']
            signals.append({
                'type': 'TOSS_UP',
                'sport': event.get('sport_name'),
                'matchup': event.get('title'),
                'home_team': event.get('home_team'),
                'away_team': event.get('away_team'),
                'home_odds': event.get('home_odds'),
                'away_odds': event.get('away_odds'),
                'home_prob': event.get('home_implied_prob'),
                'spread': event.get('home_spread'),
                'total': event.get('total_line'),
                'game_time': event.get('commence_time_formatted'),
                'reasoning': f"Close matchup at {(event.get('home_implied_prob') or 50):.0f}%/{100-(event.get('home_implied_prob') or 50):.0f}% - research for edge",
                'suggested_units': 1,
            })

        # Heavy favorite signals (fade or value)
        for item in analysis['heavy_favorites'][:3]:
            event = item['event']
            # Check if underdog has value on spread
            spread = event.get('home_spread')
            signals.append({
                'type': 'FAVORITE_ANALYSIS',
                'sport': event.get('sport_name'),
                'matchup': event.get('title'),
                'favorite': item['favorite'],
                'favorite_prob': item['probability'],
                'spread': spread,
                'total': event.get('total_line'),
                'game_time': event.get('commence_time_formatted'),
                'reasoning': f"{item.get('favorite', 'Team')} heavily favored at {(item.get('probability') or 50):.0f}% - check spread value on underdog",
                'suggested_units': 1,
            })

        # Sharp market signals
        for item in analysis['sharp_indicators'][:3]:
            event = item['event']
            signals.append({
                'type': 'SHARP_MARKET',
                'sport': event.get('sport_name'),
                'matchup': event.get('title'),
                'spread': item['spread'],
                'book_count': item['book_count'],
                'game_time': event.get('commence_time_formatted'),
                'reasoning': f"High liquidity ({item['book_count']} books) - sharp money likely involved",
                'suggested_units': 2,
            })

        # Upcoming games summary
        for event in analysis['upcoming_games'][:5]:
            if not any(s['matchup'] == event.get('title') for s in signals):
                signals.append({
                    'type': 'UPCOMING',
                    'sport': event.get('sport_name'),
                    'matchup': event.get('title'),
                    'home_odds': event.get('home_odds'),
                    'away_odds': event.get('away_odds'),
                    'spread': event.get('home_spread'),
                    'total': event.get('total_line'),
                    'game_time': event.get('commence_time_formatted'),
                    'reasoning': 'Game starting within 24 hours - monitor line movement',
                    'suggested_units': 1,
                })

        return signals

    def _build_structured_report(
        self,
        events: List[Dict],
        analysis: Dict,
        signals: List[Dict],
        provenance: ReportProvenance
    ) -> SportsReportSchema:
        """
        Session 918: Build structured report schema from analysis data.

        Creates a JSON-serializable schema that can be used by downstream
        agents, stored for auditing, or rendered in UIs.
        """
        report = SportsReportSchema(provenance=provenance)

        report.total_games_analyzed = len(events)
        report.sports_covered = list(analysis.get('sport_breakdown', {}).keys())
        report.games_in_next_24h = len(analysis.get('upcoming_games', []))

        # Build game analyses by sport
        for event in events:
            sport_name = event.get('sport_name', 'Other').lower()
            game = GameAnalysis(
                game_id=event.get('id', ''),
                sport=event.get('sport_name', ''),
                matchup=event.get('title', ''),
                home_team=event.get('home_team', ''),
                away_team=event.get('away_team', ''),
                home_moneyline=event.get('home_odds'),
                away_moneyline=event.get('away_odds'),
                home_implied_prob=event.get('home_implied_prob'),
                away_implied_prob=event.get('away_implied_prob'),
                spread=event.get('home_spread'),
                total=event.get('total_line'),
                bookmaker_count=event.get('bookmaker_count', 0),
                start_time_utc=event.get('commence_time', ''),
                start_time_local=event.get('commence_time_formatted', ''),
            )

            # Calculate hours until start
            if event.get('commence_time'):
                try:
                    dt = datetime.fromisoformat(
                        event['commence_time'].replace('Z', '+00:00')
                    )
                    now = datetime.now(timezone.utc)
                    game.hours_until_start = max(0, (dt - now).total_seconds() / 3600)
                except (ValueError, TypeError):
                    pass

            # Route to sport-specific list
            if 'nfl' in sport_name or 'football' in sport_name:
                report.nfl_games.append(game)
            elif 'nba' in sport_name or 'basketball' in sport_name:
                report.nba_games.append(game)
            elif 'mlb' in sport_name or 'baseball' in sport_name:
                report.mlb_games.append(game)
            elif 'nhl' in sport_name or 'hockey' in sport_name:
                report.nhl_games.append(game)
            else:
                report.other_games.append(game)

        # Track signal types
        for item in analysis.get('toss_ups', []):
            if 'event' in item and 'id' in item['event']:
                report.toss_up_games.append(item['event']['id'])

        for item in analysis.get('sharp_indicators', []):
            if 'event' in item and 'id' in item['event']:
                report.sharp_market_games.append(item['event']['id'])

        for item in analysis.get('heavy_favorites', []):
            if 'event' in item and 'id' in item['event']:
                report.heavy_favorites.append(item['event']['id'])

        # Add risk flags
        if not provenance.publishable:
            for blocker in provenance.publish_blockers:
                report.risk_flags.append(RiskFlag(
                    severity='high',
                    description=blocker,
                    mitigation='Verify data freshness before acting'
                ))

        # Add standard risk flag about injury data
        report.risk_flags.append(RiskFlag(
            severity='medium',
            description='Injury/lineup data not verified in this report',
            mitigation='Check injury reports before placing any bets'
        ))

        # Confidence based on data quality
        if provenance.validation_status == 'verified':
            report.overall_confidence = 0.7
            report.confidence_rationale = 'Data sources verified and fresh'
        elif provenance.validation_status == 'partially_verified':
            report.overall_confidence = 0.5
            report.confidence_rationale = 'Some data approaching staleness threshold'
        else:
            report.overall_confidence = 0.3
            report.confidence_rationale = 'Data freshness cannot be confirmed'

        return report

    def _generate_analysis_report(
        self,
        task: str,
        events: List[Dict],
        analysis: Dict,
        signals: List[Dict],
        context: Dict,
        provenance: ReportProvenance = None
    ) -> str:
        """
        Generate natural language analysis report using LLM.

        Session 918: Now includes provenance header in the report.
        """
        try:
            from openai import OpenAI
            import os

            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            # Prepare event summary
            event_summary = []
            for event in events[:15]:
                event_summary.append({
                    'matchup': event.get('title', '')[:60],
                    'sport': event.get('sport_name'),
                    'home_odds': event.get('home_odds'),
                    'away_odds': event.get('away_odds'),
                    'spread': event.get('home_spread'),
                    'total': event.get('total_line'),
                    'game_time': event.get('commence_time_formatted'),
                })

            prompt = f"""Analyze these sports betting odds and provide insights:

Task: {task}

Events (next 15):
{json.dumps(event_summary, indent=2)}

Analysis Summary:
- Toss-up games: {len(analysis['toss_ups'])}
- Heavy favorites: {len(analysis['heavy_favorites'])}
- Sharp market indicators: {len(analysis['sharp_indicators'])}
- Sports covered: {list(analysis['sport_breakdown'].keys())}
- Games in next 24h: {len(analysis['upcoming_games'])}

Generated Signals: {len(signals)}

Provide a concise analysis covering:
1. Today's betting landscape (what sports, key matchups)
2. Best opportunities (with reasoning and suggested plays)
3. Games to avoid (why)
4. Line movement alerts (if any patterns)

Keep it actionable and under 400 words. All times are MST."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )

            llm_analysis = response.choices[0].message.content or ""

            # Session 918: Prepend provenance block to report
            if provenance:
                return provenance.to_markdown_block() + "\n" + llm_analysis
            return llm_analysis

        except Exception as e:
            logger.error(f"Error generating analysis report: {e}")
            return self._basic_report(events, signals, provenance)

    def _basic_report(
        self,
        events: List[Dict],
        signals: List[Dict],
        provenance: ReportProvenance = None
    ) -> str:
        """Generate basic report without LLM."""
        lines = []

        # Session 918: Include provenance if available
        if provenance:
            lines.append(provenance.to_markdown_block())
            lines.append("")

        lines.extend([
            f"**Sports Odds Analysis**",
            f"Analyzed {len(events)} events, generated {len(signals)} signals.",
            "",
            "**Top Signals:**"
        ])

        for signal in signals[:5]:
            lines.append(f"- [{signal['type']}] {signal['matchup'][:40]}... ({signal.get('game_time', 'TBD')})")

        return "\n".join(lines)

    def _count_sports(self, events: List[Dict]) -> Dict[str, int]:
        """Count events by sport."""
        counts = {}
        for event in events:
            sport = event.get('sport_name', 'Unknown')
            counts[sport] = counts.get(sport, 0) + 1
        return counts

    def _is_upcoming_24h(self, event: Dict) -> bool:
        """Check if event is within next 24 hours."""
        try:
            commence_time = event.get('commence_time', '')
            if not commence_time:
                return False
            dt = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            return now <= dt <= now + timedelta(hours=24)
        except:
            return False

    def _elapsed_ms(self, start_time: datetime) -> int:
        """Calculate elapsed time in milliseconds."""
        return int((datetime.now() - start_time).total_seconds() * 1000)
