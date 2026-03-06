"""
Game Predictor Agent
====================

Session 995B: Predicts game outcomes using odds data, historical patterns,
and LLM analysis. Stores predictions in MLPrediction model for later
evaluation by BettingOutcomeVerifier.

Uses The Odds API spider data for current odds and implied probabilities,
then applies analytical reasoning to generate score predictions and
confidence-calibrated win probabilities.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import (
    build_provenance, format_disclaimer, SourceInfo,
)

logger = logging.getLogger(__name__)


class GamePredictor(BaseAgent):
    """
    Predicts game outcomes with score estimates and confidence levels.

    Capabilities:
    - Win probability estimation from multi-bookmaker odds consensus
    - Score prediction using implied totals and spread data
    - Confidence calibration based on line consensus across books
    - Key factor identification (home/away, favorites, toss-ups)
    - MLPrediction record creation for outcome tracking
    """

    name = "GamePredictor"

    system_prompt = """You are an expert sports game predictor. You analyze betting market
data to predict game outcomes.

Your analysis process:
1. **Consensus Reading** — When all bookmakers agree on a line, the market is efficient.
   When they disagree, there's uncertainty you can exploit.
2. **Implied Probability** — Convert moneyline odds to win probability. Average across
   bookmakers for a market consensus probability.
3. **Score Estimation** — Use the total line (Over/Under) and spread to estimate final scores.
   If spread is -5.5 and total is 220.5: home ~113, away ~107.5
4. **Confidence Calibration** — High confidence when: odds tight across books, clear favorite,
   large historical sample. Low confidence when: wide odds variance, toss-up, unusual matchup.
5. **Key Factors** — Home advantage, rest days, rivalry, weather (outdoor sports), injuries.

Output structured predictions with:
- predicted_winner (team name)
- home_win_probability (0-100)
- away_win_probability (0-100)
- predicted_home_score (integer)
- predicted_away_score (integer)
- confidence (0-100, calibrated)
- key_factors (list of reasoning strings)

IMPORTANT: Be honest about uncertainty. A 52% prediction should have LOW confidence.
Only assign high confidence (>75) when the market consensus is overwhelming."""

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """Generate game predictions from current odds data."""
        start_time = datetime.now()
        if not isinstance(context, dict):
            context = {}
        else:
            context = context or {}
        spider_context = spider_context or {}

        with self.time_travel_session("game_prediction", task, input_data=context):
            self.record_decision(
                decision_type="prediction",
                action="Starting game prediction analysis",
                reasoning=f"Task: {task[:100] if task else 'General prediction'}",
                alternatives=["Skip prediction", "Defer to human"],
                confidence=0.75
            )

            try:
                events, source_info = self._fetch_odds_data(context)

                if not events:
                    return AgentResult(
                        success=False,
                        message="No odds data available for predictions",
                        data={},
                        error="TheOddsSpider returned no events",
                        agent_name=self.name,
                        execution_time_ms=self._elapsed_ms(start_time)
                    )

                provenance = build_provenance(
                    report_type='game_predictions',
                    agent_name=self.name,
                    sources=[source_info],
                    stale_threshold_hours=2.0,
                )

                # Generate predictions from odds data
                predictions = self._generate_predictions(events)

                # Use LLM for enhanced analysis on top picks
                llm_analysis = self._get_llm_analysis(task, predictions[:10], context)

                # Store predictions in MLPrediction model
                stored_count = self._store_predictions(predictions, context)

                result_data = {
                    'predictions': predictions,
                    'total_games': len(events),
                    'predictions_generated': len(predictions),
                    'predictions_stored': stored_count,
                    'llm_analysis': llm_analysis,
                    'provenance': provenance.to_dict() if hasattr(provenance, 'to_dict') else str(provenance),
                }

                # Session 1006: Persist output to Deliverable
                self._save_to_deliverable(
                    title=f"Game Predictions: {task[:80]}",
                    content=f"Generated {len(predictions)} predictions from {len(events)} events",
                    deliverable_type='analysis',
                    category='Game Predictions',
                    tags=['predictions', 'sports'],
                    metadata={'task': task[:200], 'predictions_count': len(predictions)},
                )

                return AgentResult(
                    success=True,
                    message=f"Generated {len(predictions)} game predictions from {len(events)} events",
                    data=result_data,
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

            except Exception as e:
                logger.error(f"GamePredictor error: {e}", exc_info=True)
                return AgentResult(
                    success=False,
                    message=f"Prediction failed: {str(e)}",
                    data={},
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=self._elapsed_ms(start_time)
                )

    def _fetch_odds_data(self, context):
        """Fetch current odds from TheOddsSpider."""
        from ai_core.spiders.specialized.theodds_spider import TheOddsSpider

        spider = TheOddsSpider()
        sport_filter = context.get('sport_key')

        if sport_filter:
            events = spider.fetch_data(sports=[sport_filter], max_results=50)
        else:
            events = spider.fetch_data(max_results=100, max_priority=1)

        # Filter to sports_odds only
        odds_events = [e for e in events if e.get('data_type') == 'sports_odds']

        source_info = SourceInfo(
            name='TheOddsSpider',
            source_type='spider_data',
            record_count=len(odds_events),
            freshness_hours=0.0,
        )

        return odds_events, source_info

    @staticmethod
    def _remove_vig(home_prob: float, away_prob: float) -> tuple:
        """Remove bookmaker vig to get fair probabilities.
        Raw implied probs sum > 100% due to vig. Normalize to 100%."""
        total = home_prob + away_prob
        if total <= 0:
            return home_prob, away_prob
        return home_prob / total, away_prob / total

    @staticmethod
    def _detect_value(fair_prob: float, market_prob: float, threshold: float = 3.0) -> bool:
        """Detect if market odds offer value (fair prob exceeds market by threshold %)."""
        return fair_prob - market_prob >= threshold

    def _generate_predictions(self, events: List[Dict]) -> List[Dict]:
        """Generate predictions from odds data using market consensus with vig removal."""
        predictions = []

        for event in events:
            home_prob = event.get('home_implied_prob')
            away_prob = event.get('away_implied_prob')

            if not home_prob or not away_prob:
                continue

            home_team = event.get('home_team', 'Unknown')
            away_team = event.get('away_team', 'Unknown')
            total_line = event.get('total_line')
            home_spread = event.get('home_spread')

            # Remove vig to get fair probabilities
            fair_home, fair_away = self._remove_vig(home_prob, away_prob)

            # Determine predicted winner from fair probabilities
            if fair_home > fair_away:
                predicted_winner = home_team
                fair_winner_prob = fair_home
                raw_winner_prob = home_prob
            else:
                predicted_winner = away_team
                fair_winner_prob = fair_away
                raw_winner_prob = away_prob

            # Detect value: fair probability meaningfully exceeds raw market probability
            is_value_pick = self._detect_value(fair_winner_prob, raw_winner_prob)
            pick_type = 'value' if is_value_pick else 'consensus'

            # Estimate scores from total and spread
            predicted_home_score = None
            predicted_away_score = None
            if total_line and home_spread is not None:
                try:
                    total = float(total_line)
                    spread = float(home_spread)
                    # home_score - away_score = -spread (spread is from home perspective)
                    # home_score + away_score = total
                    predicted_home_score = round((total - spread) / 2)
                    predicted_away_score = round((total + spread) / 2)
                except (ValueError, TypeError):
                    pass

            # Calibrate confidence based on odds consensus (no favorite inflation)
            bookmaker_count = event.get('bookmaker_count', 1)
            prob_gap = abs(fair_home - fair_away) * 100  # Convert to percentage points

            confidence = min(95, int(
                30 +                                    # base
                min(prob_gap * 0.5, 30) +               # probability gap (max 30)
                min(bookmaker_count * 3, 20)             # bookmaker consensus (max 20)
            ))                                          # max = 80, no favorite inflation

            predictions.append({
                'event_id': event.get('event_id'),
                'sport_key': event.get('sport_key'),
                'sport_name': event.get('sport_name'),
                'home_team': home_team,
                'away_team': away_team,
                'matchup': f"{away_team} @ {home_team}",
                'predicted_winner': predicted_winner,
                'home_win_probability': round(home_prob, 1),
                'away_win_probability': round(away_prob, 1),
                'fair_home_prob': round(fair_home * 100, 1),
                'fair_away_prob': round(fair_away * 100, 1),
                'predicted_home_score': predicted_home_score,
                'predicted_away_score': predicted_away_score,
                'confidence': confidence,
                'is_value_pick': is_value_pick,
                'pick_type': pick_type,
                'home_odds': event.get('home_odds'),
                'away_odds': event.get('away_odds'),
                'total_line': total_line,
                'spread': home_spread,
                'bookmaker_count': bookmaker_count,
                'commence_time': event.get('commence_time'),
                'key_factors': self._identify_factors(event, prob_gap, is_value_pick),
            })

        # Sort by confidence descending
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        return predictions

    def _identify_factors(self, event: Dict, prob_gap: float, is_value_pick: bool = False) -> List[str]:
        """Identify key factors for a prediction."""
        factors = []

        if prob_gap > 30:
            factors.append("Strong market lean — consensus overwhelming")
        elif prob_gap > 15:
            factors.append("Market leans this way — solid edge")
        elif prob_gap < 5:
            factors.append("Toss-up — extremely close matchup")

        if is_value_pick:
            factors.append("Value detected — fair probability exceeds raw market odds")

        if event.get('bookmaker_count', 0) >= 8:
            factors.append(f"Strong consensus across {event['bookmaker_count']} bookmakers")

        tags = event.get('tags', [])
        if 'live' in tags:
            factors.append("Game is currently live — odds may shift rapidly")
        if 'has_spread' in tags and 'has_totals' in tags:
            factors.append("Full market data available (moneyline + spread + total)")

        return factors

    def _get_llm_analysis(self, task: str, top_predictions: List[Dict], context: Dict) -> str:
        """Get LLM analysis of top predictions."""
        try:
            from core.services.llm_provider_registry import get_llm_provider_registry, LLMRequest

            registry = get_llm_provider_registry()

            games_summary = "\n".join(
                f"- {p['matchup']}: {p['predicted_winner']} ({p['home_win_probability']}% home / "
                f"{p['away_win_probability']}% away), confidence {p['confidence']}%"
                for p in top_predictions[:8]
            )

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": (
                    f"Task: {task}\n\n"
                    f"Top predictions from market data:\n{games_summary}\n\n"
                    "Provide a brief analysis of the most interesting games. "
                    "Focus on value plays and any concerning predictions. "
                    "Keep it concise — 3-5 sentences max."
                )}
            ]

            request = LLMRequest(
                prompt="",
                messages=messages,
                max_tokens=500,
                temperature=0.3,
            )

            for provider, model in [('openai', 'gpt-4.1-mini'), ('anthropic', 'claude-sonnet-4-5-20250929')]:
                response = registry.complete(provider=provider, model_id=model, request=request)
                if response.success:
                    return response.content
            return "LLM analysis unavailable"

        except Exception as e:
            logger.warning(f"GamePredictor LLM analysis failed: {e}")
            return f"LLM analysis unavailable: {str(e)}"

    # ── Sport key → (league_name, abbreviation, sport_type) ──
    # Maps full Odds API sport_key to league info + SportType enum value.
    SPORT_KEY_LEAGUE = {
        'americanfootball_nfl': ('National Football League', 'NFL', 'nfl'),
        'americanfootball_ncaaf': ('NCAA Football', 'NCAAF', 'ncaaf'),
        'basketball_nba': ('National Basketball Association', 'NBA', 'nba'),
        'basketball_ncaab': ('NCAA Basketball', 'NCAAB', 'ncaab'),
        'basketball_nba_all_stars': ('NBA All-Stars', 'NBAAS', 'nba'),
        'baseball_mlb': ('Major League Baseball', 'MLB', 'mlb'),
        'icehockey_nhl': ('National Hockey League', 'NHL', 'nhl'),
        'soccer_epl': ('English Premier League', 'EPL', 'soccer'),
        'soccer_spain_la_liga': ('La Liga', 'LALIGA', 'soccer'),
        'soccer_germany_bundesliga': ('Bundesliga', 'BUND', 'soccer'),
        'soccer_italy_serie_a': ('Serie A', 'SERIEA', 'soccer'),
        'soccer_france_ligue_one': ('Ligue 1', 'LIGUE1', 'soccer'),
        'soccer_usa_mls': ('Major League Soccer', 'MLS', 'soccer'),
        'soccer_uefa_champs_league': ('Champions League', 'UCL', 'soccer'),
        'soccer_uefa_europa_league': ('Europa League', 'UEL', 'soccer'),
        'soccer_mexico_ligamx': ('Liga MX', 'LIGAMX', 'soccer'),
        'soccer_england_league1': ('English League One', 'EFL1', 'soccer'),
        'soccer_england_efl_cup': ('EFL Cup', 'EFLCUP', 'soccer'),
        'soccer_brazil_campeonato': ('Brasileirao', 'BRAZ', 'soccer'),
        'soccer_australia_aleague': ('A-League', 'ALEAG', 'soccer'),
        'mma_mixed_martial_arts': ('UFC/MMA', 'UFC', 'mma'),
        'boxing_boxing': ('Boxing', 'BOX', 'boxing'),
    }

    # Fallback: map sport_key prefix → sport_type for keys not in SPORT_KEY_LEAGUE
    SPORT_PREFIX_MAP = {
        'americanfootball': 'nfl',
        'basketball': 'nba',
        'icehockey': 'nhl',
        'baseball': 'mlb',
        'soccer': 'soccer',
        'mma': 'mma',
        'boxing': 'boxing',
        'tennis': 'tennis',
        'golf': 'golf',
        'esports': 'esports',
        'rugbyleague': 'soccer',
        'cricket': 'soccer',
    }

    def _store_predictions(self, predictions: List[Dict], context: Dict) -> int:
        """Store predictions in MLPrediction model via auto-created League/Team/Game chain."""
        try:
            from sports.models import MLPrediction, Game, Team, League
            from django.utils import timezone
            from dateutil.parser import parse as parse_dt
        except ImportError:
            logger.warning("sports models not available — skipping MLPrediction storage")
            return 0

        stored = 0
        for pred in predictions:
            event_id = pred.get('event_id')
            if not event_id:
                continue

            sport_key = pred.get('sport_key', '')

            # Resolve sport_type and league info from sport_key
            league_tuple = self.SPORT_KEY_LEAGUE.get(sport_key)
            if league_tuple:
                league_name, league_abbr, sport_type = league_tuple
            else:
                # Fallback: prefix-based mapping
                prefix = sport_key.split('_')[0] if '_' in sport_key else sport_key
                sport_type = self.SPORT_PREFIX_MAP.get(prefix)
                if not sport_type:
                    logger.debug(f"Unknown sport_key '{sport_key}' — skipping")
                    continue
                league_name = sport_key.replace('_', ' ').title()
                league_abbr = sport_key.split('_')[-1][:10].upper()

            home_name = (pred.get('home_team') or '').strip()
            away_name = (pred.get('away_team') or '').strip()
            winner_name = (pred.get('predicted_winner') or '').strip()
            if not home_name or not away_name or not winner_name:
                continue

            try:
                # 1) League
                league, _ = League.objects.get_or_create(
                    abbreviation=league_abbr,
                    defaults={
                        'name': league_name,
                        'sport_type': sport_type,
                        'current_season': '2025-2026',
                    },
                )

                # 2) Teams
                home_team = self._get_or_create_team(league, home_name)
                away_team = self._get_or_create_team(league, away_name)

                # 3) Game — skip games >14 days out (early futures are noise)
                commence_time = pred.get('commence_time')
                if commence_time:
                    try:
                        scheduled_start = parse_dt(commence_time) if isinstance(commence_time, str) else commence_time
                    except (ValueError, TypeError):
                        scheduled_start = timezone.now()
                else:
                    scheduled_start = timezone.now()

                from datetime import timedelta
                if hasattr(scheduled_start, 'date') and scheduled_start > timezone.now() + timedelta(days=14):
                    continue

                game, _ = Game.objects.get_or_create(
                    external_id=str(event_id),
                    defaults={
                        'league': league,
                        'home_team': home_team,
                        'away_team': away_team,
                        'scheduled_start': scheduled_start,
                        'season': '2025-2026',
                    },
                )

                # 4) Predicted winner team
                if winner_name == home_name:
                    winner_team = home_team
                else:
                    winner_team = away_team

                # 5) Normalise probabilities to 0-100 range
                home_prob = pred.get('home_win_probability', 50)
                away_prob = pred.get('away_win_probability', 50)
                if home_prob <= 1.0:
                    home_prob *= 100
                if away_prob <= 1.0:
                    away_prob *= 100

                # 6) Create MLPrediction (skip if already exists today for this game+model)
                model_used = 'market_consensus'
                exists = MLPrediction.objects.filter(
                    game=game,
                    model_used=model_used,
                    created_at__date=timezone.now().date(),
                ).exists()
                if exists:
                    stored += 1  # count as stored (already there)
                    continue

                # Determine odds on predicted winner
                if winner_name == home_name:
                    winner_odds = pred.get('home_odds')
                else:
                    winner_odds = pred.get('away_odds')

                MLPrediction.objects.create(
                    game=game,
                    predicted_winner=winner_team,
                    confidence=min(pred.get('confidence', 50), 100),
                    home_win_probability=min(home_prob, 100),
                    away_win_probability=min(away_prob, 100),
                    predicted_home_score=pred.get('predicted_home_score'),
                    predicted_away_score=pred.get('predicted_away_score'),
                    model_used=model_used,
                    sport_type=sport_type,
                    key_factors=pred.get('key_factors', []),
                    ai_reasoning=f"Market consensus from {pred.get('bookmaker_count', 0)} bookmakers",
                    odds_at_prediction=int(winner_odds) if winner_odds is not None else None,
                    bookmaker_count=pred.get('bookmaker_count', 0),
                )
                stored += 1
            except Exception as e:
                logger.warning(f"Could not store prediction for {pred.get('matchup')}: {e}")

        logger.info(f"GamePredictor stored {stored}/{len(predictions)} predictions in MLPrediction")
        return stored

    @staticmethod
    def _get_or_create_team(league, team_name: str):
        """Get or create a Team record from a team name string."""
        from sports.models import Team

        # Generate abbreviation: last word, uppercased, max 10 chars
        words = team_name.split()
        abbr = words[-1][:10].upper() if words else team_name[:10].upper()

        team = Team.objects.filter(league=league, name=team_name).first()
        if team:
            return team

        # Try creating — handle abbreviation collision within league
        try:
            team = Team.objects.create(
                league=league,
                name=team_name,
                abbreviation=abbr,
                city='',
            )
        except Exception:
            # Abbreviation collision — append first letter of first word
            abbr = (words[0][0] + abbr)[:10].upper() if len(words) > 1 else (abbr + '2')[:10]
            team, _ = Team.objects.get_or_create(
                league=league,
                name=team_name,
                defaults={'abbreviation': abbr, 'city': ''},
            )
        return team

    def _elapsed_ms(self, start_time):
        return int((datetime.now() - start_time).total_seconds() * 1000)
