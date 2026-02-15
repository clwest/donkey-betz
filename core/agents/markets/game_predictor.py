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

    def _generate_predictions(self, events: List[Dict]) -> List[Dict]:
        """Generate predictions from odds data using market consensus."""
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

            # Determine predicted winner
            if home_prob > away_prob:
                predicted_winner = home_team
                win_confidence = home_prob
            else:
                predicted_winner = away_team
                win_confidence = away_prob

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

            # Calibrate confidence based on odds consensus
            bookmaker_count = event.get('bookmaker_count', 1)
            prob_gap = abs(home_prob - away_prob)

            # Higher confidence when: more books agree, wider probability gap
            confidence = min(95, int(
                30 +  # base
                min(prob_gap * 0.5, 30) +  # probability gap (max 30)
                min(bookmaker_count * 3, 20) +  # bookmaker consensus (max 20)
                (15 if prob_gap > 20 else 0)  # clear favorite bonus
            ))

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
                'predicted_home_score': predicted_home_score,
                'predicted_away_score': predicted_away_score,
                'confidence': confidence,
                'home_odds': event.get('home_odds'),
                'away_odds': event.get('away_odds'),
                'total_line': total_line,
                'spread': home_spread,
                'bookmaker_count': bookmaker_count,
                'commence_time': event.get('commence_time'),
                'key_factors': self._identify_factors(event, prob_gap),
            })

        # Sort by confidence descending
        predictions.sort(key=lambda x: x['confidence'], reverse=True)
        return predictions

    def _identify_factors(self, event: Dict, prob_gap: float) -> List[str]:
        """Identify key factors for a prediction."""
        factors = []

        if prob_gap > 30:
            factors.append("Heavy favorite — market consensus overwhelming")
        elif prob_gap > 15:
            factors.append("Clear favorite — solid market edge")
        elif prob_gap < 5:
            factors.append("Toss-up — extremely close matchup")

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

            response = registry.generate(request, preferred_providers=['openai', 'anthropic'])
            return response.content if response else "LLM analysis unavailable"

        except Exception as e:
            logger.warning(f"GamePredictor LLM analysis failed: {e}")
            return f"LLM analysis unavailable: {str(e)}"

    def _store_predictions(self, predictions: List[Dict], context: Dict) -> int:
        """Store predictions in MLPrediction model for later evaluation."""
        try:
            from sports.models import MLPrediction, Game
            from core.models_unified_system import Agent
            from django.utils import timezone

            agent_obj = Agent.objects.filter(name=self.name).first()
            if not agent_obj:
                logger.warning(f"Agent '{self.name}' not found in DB — skipping MLPrediction storage")
                return 0

            stored = 0
            for pred in predictions:
                if not pred.get('event_id'):
                    continue

                sport_key = pred.get('sport_key', '')
                # Extract short sport type (e.g., 'basketball_nba' -> 'nba')
                sport_type = sport_key.split('_')[-1] if '_' in sport_key else sport_key

                try:
                    MLPrediction.objects.update_or_create(
                        agent=agent_obj,
                        sport_type=sport_type,
                        predicted_winner=pred['predicted_winner'],
                        game_date=timezone.now().date(),
                        defaults={
                            'confidence': pred['confidence'],
                            'home_win_probability': pred['home_win_probability'],
                            'away_win_probability': pred['away_win_probability'],
                            'predicted_home_score': pred.get('predicted_home_score'),
                            'predicted_away_score': pred.get('predicted_away_score'),
                            'model_used': 'market_consensus',
                            'key_factors': pred.get('key_factors', []),
                            'ai_reasoning': f"Market consensus from {pred.get('bookmaker_count', 0)} bookmakers",
                        }
                    )
                    stored += 1
                except Exception as e:
                    logger.debug(f"Could not store prediction for {pred.get('matchup')}: {e}")

            logger.info(f"GamePredictor stored {stored} predictions in MLPrediction")
            return stored

        except ImportError:
            logger.warning("sports.models.MLPrediction not available — skipping storage")
            return 0
        except Exception as e:
            logger.warning(f"Failed to store predictions: {e}")
            return 0

    def _elapsed_ms(self, start_time):
        return int((datetime.now() - start_time).total_seconds() * 1000)
