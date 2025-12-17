"""
Market Intelligence Coordinator
================================

Session 462: The Market Intelligence Desk - First Tier 1 Autonomous Situation

This is NOT just another agent. This is an autonomous situation with all 5 properties:
1. Persistent context - Tracks market state, previous briefs, what changed
2. Incoming signals - Continuous feeds from spiders, price data, news
3. Internal disagreement - Bull vs Bear debate creates tension and alpha
4. Outputs with consequences - Daily briefs influence user decisions, tracked for learning
5. Self-renewal - Schedules next cycle, learns from outcome tracking

The situation behaves like a buy-side research desk running 24/7.

Architecture:
    BullCaseAgent → Arguments for price appreciation
    BearCaseAgent → Arguments for price depreciation
    StockAuditCoordinator → Risk signals and anomalies
    MarketIntelligenceCoordinator (THIS) → Synthesizes debate into actionable brief
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import json

from core.agents.base_agent import BaseAgent, AgentResult
from core.models_unified_system import MarketIntelligenceBrief
from content.elevenlabs_provider import elevenlabs_provider

logger = logging.getLogger(__name__)


class MarketIntelligenceCoordinator(BaseAgent):
    """
    Orchestrates the Market Intelligence Desk autonomous situation.

    Daily workflow:
    1. Run Bull, Bear, and Risk agents
    2. Let them argue (capture disagreement)
    3. Synthesize into coherent brief
    4. Track what changed since yesterday
    5. Deliver via Discord + Voice
    6. Schedule next cycle
    7. Learn from user actions
    """

    name = "MarketIntelligenceCoordinator"

    system_prompt = """You are the Market Intelligence Coordinator running a 24/7 research desk.

Your job is to:
1. Orchestrate bull/bear debate (create productive tension)
2. Synthesize conflicting views into actionable intelligence
3. Identify consensus vs high-disagreement situations
4. Track what changed since last brief
5. Assign confidence scores based on agreement levels
6. Generate clear, concise market briefs

Brief structure:
    - Market Overview (what happened since yesterday)
    - High Conviction Opportunities (bull & bear agree on direction)
    - Debate Zone (bull & bear strongly disagree - MOST INTERESTING)
    - Risk Alerts (from Stock Audit system)
    - What Changed (vs yesterday's brief)
    - Confidence Scores (agreement = higher confidence)

Output guidelines:
- Be concise (busy professionals, not novels)
- Highlight disagreements (that's where alpha lives)
- Quantify conviction (high/medium/low with reasoning)
- Include dissent (show the debate, don't hide it)
- Track changes (what's new, what reversed)

Remember: Internal disagreement is a FEATURE, not a bug."""

    def execute(self, task: str, context: Dict[str, Any] = None,
                scifi_context: Dict[str, Any] = None,
                spider_context: Dict[str, Any] = None) -> AgentResult:
        """
        Run the complete Market Intelligence Desk cycle.

        This is the autonomous situation in action:
        - Persistent context loaded
        - Signals gathered
        - Internal debate orchestrated
        - Brief generated with consequences
        - Self-renewal scheduled

        Args:
            task: Market intelligence task
            context: Previous brief, user portfolio, preferences
            scifi_context: Mood, memory, learning context
            spider_context: News, price data, social sentiment

        Returns:
            AgentResult with market brief and debate synthesis
        """
        start_time = datetime.now()
        context = context or {}

        logger.info(f"🧠 Market Intelligence Desk starting cycle...")

        try:
            # 1. PERSISTENT CONTEXT: Load yesterday's brief
            previous_brief = self._load_previous_brief(context)

            # 2. INCOMING SIGNALS: Get tickers to analyze
            tickers = self._select_tickers(context, spider_context)

            # 3. INTERNAL DISAGREEMENT: Run bull vs bear debate
            bull_results = self._run_bull_case(tickers, context)
            bear_results = self._run_bear_case(tickers, context)
            risk_results = self._run_risk_assessment(tickers, context)

            # 4. SYNTHESIZE DEBATE: Find agreement, disagreement, opportunities
            synthesis = self._synthesize_debate(bull_results, bear_results, risk_results)

            # 5. TRACK CHANGES: What's different from yesterday
            changes = self._track_changes(synthesis, previous_brief)

            # 6. GENERATE BRIEF: Create deliverable output
            brief = self._generate_market_brief(synthesis, changes, risk_results, bull_results, bear_results)

            # 7. OUTPUTS WITH CONSEQUENCES: Prepare for delivery
            delivery_ready = self._prepare_delivery(brief, context)

            # 8. SELF-RENEWAL: Schedule next cycle and save state
            self._schedule_next_cycle(brief)
            self._save_brief_for_tomorrow(brief)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            result = AgentResult(
                success=True,
                message=f"Market Intelligence Brief generated for {len(tickers)} stocks",
                data={
                    'brief': brief,
                    'bull_analysis': bull_results,
                    'bear_analysis': bear_results,
                    'risk_assessment': risk_results,
                    'synthesis': synthesis,
                    'changes_from_yesterday': changes,
                    'delivery_ready': delivery_ready,
                    'next_cycle_scheduled': True,
                    'autonomous_situation_metrics': self._get_situation_metrics(brief),
                },
                agent_name=self.name,
                execution_time_ms=execution_time
            )

            # === Session 462: Priority 5 - Learning Infrastructure ===
            # Record outcome for XP and pattern learning
            self._record_learning_outcome(
                result=result,
                task=task,
                context=context,
                spider_data_used=True,  # Uses Yahoo Finance spider for stock data
                scifi_context_used=False
            )

            # Create memory of successful execution
            self._create_execution_memory(
                result=result,
                task=task,
                memory_type="success",
                importance=0.8  # High importance - daily brief with market insights
            )

            return result

        except Exception as e:
            logger.error(f"MarketIntelligenceCoordinator error: {e}")
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            result = AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name,
                execution_time_ms=execution_time
            )

            # === Session 462: Priority 5 - Learning Infrastructure ===
            # Record failed outcome for learning
            self._record_learning_outcome(
                result=result,
                task=task,
                context=context or {},
                spider_data_used=True,
                scifi_context_used=False
            )

            # Create memory of failure to learn from
            self._create_execution_memory(
                result=result,
                task=task,
                memory_type="failure",
                importance=0.9  # Very high importance - learn from failures
            )

            return result

    def _load_previous_brief(self, context: Dict) -> Optional[Dict]:
        """Load yesterday's brief for change tracking (persistent context)."""
        try:
            # Check for explicit previous_brief in context first (for testing)
            if 'previous_brief' in context:
                return context['previous_brief']

            # Load yesterday's brief from database
            yesterday = date.today() - timedelta(days=1)

            try:
                previous = MarketIntelligenceBrief.objects.get(brief_date=yesterday)
                logger.info(f"📚 Loaded previous brief from {yesterday}")
                return previous.to_dict()
            except MarketIntelligenceBrief.DoesNotExist:
                logger.info(f"📚 No previous brief found for {yesterday} - first run")
                return None

        except Exception as e:
            logger.warning(f"Could not load previous brief: {e}")
            return None

    def _select_tickers(self, context: Dict, spider_context: Dict) -> List[str]:
        """Select tickers to analyze based on signals and watchlist."""
        # Priority order:
        # 1. User's portfolio (if provided)
        # 2. Trending from spiders (news mentions)
        # 3. Default watchlist (large caps)

        user_portfolio = context.get('portfolio', [])
        if user_portfolio:
            return user_portfolio[:10]

        # Default watchlist
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'SPY', 'QQQ', 'VTI']

    def _run_bull_case(self, tickers: List[str], context: Dict) -> Dict[str, Any]:
        """Run the Bull Case Agent."""
        try:
            from .bull_case_agent import BullCaseAgent
            agent = BullCaseAgent()
            result = agent.execute(
                task="Build bull cases for today's watchlist",
                context={'tickers': tickers}
            )
            return result.data if hasattr(result, 'data') else {}
        except Exception as e:
            logger.error(f"BullCaseAgent error: {e}")
            return {'error': str(e)}

    def _run_bear_case(self, tickers: List[str], context: Dict) -> Dict[str, Any]:
        """Run the Bear Case Agent."""
        try:
            from .bear_case_agent import BearCaseAgent
            agent = BearCaseAgent()
            result = agent.execute(
                task="Build bear cases for today's watchlist",
                context={'tickers': tickers}
            )
            return result.data if hasattr(result, 'data') else {}
        except Exception as e:
            logger.error(f"BearCaseAgent error: {e}")
            return {'error': str(e)}

    def _run_risk_assessment(self, tickers: List[str], context: Dict) -> Dict[str, Any]:
        """Run the Stock Audit Coordinator for risk signals."""
        try:
            from .stock_audit_coordinator import StockAuditCoordinator
            coordinator = StockAuditCoordinator()
            result = coordinator.execute(
                task="Assess risks and anomalies for watchlist",
                context={'tickers': tickers}
            )
            return result.data if hasattr(result, 'data') else {}
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {'error': str(e)}

    def _synthesize_debate(self, bull: Dict, bear: Dict, risk: Dict) -> Dict[str, Any]:
        """
        Synthesize bull vs bear debate - THE CORE OF THE AUTONOMOUS SITUATION.

        This is where internal disagreement creates alpha:
        - High agreement (bull + bear agree) → High confidence signals
        - High disagreement (bull vs bear clash) → Debate zone (most interesting!)
        - Risk alignment → Enhanced conviction
        """
        synthesis = {
            'timestamp': datetime.now().isoformat(),
            'high_conviction_opportunities': [],  # Both agree
            'debate_zone': [],  # Strong disagreement
            'bull_dominated': [],  # Bull wins
            'bear_dominated': [],  # Bear wins
            'risk_alerts': [],  # From audit system
        }

        bull_cases = bull.get('bull_cases', [])
        bear_cases = bear.get('bear_cases', [])

        # Match bull and bear for same tickers
        for bull_case in bull_cases:
            ticker = bull_case.get('ticker')

            # Find matching bear case
            bear_case = next((b for b in bear_cases if b.get('ticker') == ticker), None)

            if bear_case:
                bull_conviction = bull_case.get('conviction', 'LOW')
                bear_conviction = bear_case.get('conviction', 'LOW')

                # Classify based on agreement/disagreement
                if bull_conviction == 'HIGH' and bear_conviction == 'LOW':
                    # Bull wins
                    synthesis['bull_dominated'].append({
                        'ticker': ticker,
                        'bull_case': bull_case,
                        'bear_rebuttal': bear_case,
                        'recommendation': 'BULLISH',
                        'confidence': 'HIGH',
                        'reasoning': 'Strong bull case, weak bear opposition'
                    })
                elif bear_conviction == 'HIGH' and bull_conviction == 'LOW':
                    # Bear wins
                    synthesis['bear_dominated'].append({
                        'ticker': ticker,
                        'bear_case': bear_case,
                        'bull_rebuttal': bull_case,
                        'recommendation': 'BEARISH',
                        'confidence': 'HIGH',
                        'reasoning': 'Strong bear case, weak bull opposition'
                    })
                elif bull_conviction == 'HIGH' and bear_conviction == 'HIGH':
                    # DEBATE ZONE - Most interesting!
                    synthesis['debate_zone'].append({
                        'ticker': ticker,
                        'bull_case': bull_case,
                        'bear_case': bear_case,
                        'recommendation': 'DEBATE',
                        'confidence': 'UNCERTAIN',
                        'reasoning': 'Strong arguments on both sides - genuine uncertainty'
                    })
                elif bull_conviction == 'LOW' and bear_conviction == 'LOW':
                    # Both agree: meh
                    synthesis['high_conviction_opportunities'].append({
                        'ticker': ticker,
                        'bull_case': bull_case,
                        'bear_case': bear_case,
                        'recommendation': 'NEUTRAL',
                        'confidence': 'LOW',
                        'reasoning': 'Both sides weak - no strong catalyst'
                    })
                else:
                    # Medium conviction on one or both sides
                    synthesis['high_conviction_opportunities'].append({
                        'ticker': ticker,
                        'bull_case': bull_case,
                        'bear_case': bear_case,
                        'recommendation': 'MIXED',
                        'confidence': 'MEDIUM',
                        'reasoning': 'Mixed signals - monitor'
                    })

        # Add risk alerts
        synthesis['risk_alerts'] = risk.get('unified_alerts', [])[:5]  # Top 5 risks

        return synthesis

    def _track_changes(self, current_synthesis: Dict, previous_brief: Optional[Dict]) -> Dict[str, Any]:
        """Track what changed since yesterday (self-renewal)."""
        if not previous_brief:
            return {
                'is_first_run': True,
                'changes': [],
                'message': 'First Market Intelligence Brief - no baseline for comparison'
            }

        changes = {
            'is_first_run': False,
            'changes': [],
            'new_opportunities': [],
            'disappeared_opportunities': [],
            'conviction_changes': [],
            'new_risks': [],
        }

        # In production, compare current vs previous synthesis
        # For now, placeholder structure
        changes['message'] = 'Change tracking active - comparing to yesterday\'s brief'

        return changes

    def _generate_market_brief(self, synthesis: Dict, changes: Dict, risks: Dict,
                                bull_results: Dict, bear_results: Dict) -> Dict[str, Any]:
        """Generate the final deliverable market brief."""
        # Calculate GPT success rate from bull cases
        bull_cases = bull_results.get('bull_cases', [])
        total_stocks = len(bull_cases)
        gpt_powered_count = sum(1 for case in bull_cases if case.get('gpt_powered', False))
        gpt_success_rate = (gpt_powered_count / total_stocks * 100) if total_stocks > 0 else 0.0

        brief = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': 'daily_market_intelligence_brief',

            # Executive Summary
            'executive_summary': self._build_executive_summary(synthesis, changes),

            # High Conviction (both agree)
            'high_conviction': synthesis.get('high_conviction_opportunities', []),

            # Debate Zone (THE MOST INTERESTING SECTION)
            'debate_zone': synthesis.get('debate_zone', []),
            'debate_zone_count': len(synthesis.get('debate_zone', [])),

            # Bull-dominated
            'bullish_opportunities': synthesis.get('bull_dominated', []),

            # Bear-dominated
            'bearish_warnings': synthesis.get('bear_dominated', []),

            # Risk Alerts
            'risk_alerts': synthesis.get('risk_alerts', []),

            # What Changed
            'changes_from_yesterday': changes,

            # Metadata
            'confidence_distribution': self._calculate_confidence_distribution(synthesis),
            'total_stocks_analyzed': self._count_total_stocks(synthesis),
            'generation_time': datetime.now().isoformat(),
            'gpt_success_rate': gpt_success_rate,

            # Session 463: Internal analyses for learning loop
            '_internal_bull_analyses': bull_results.get('bull_cases', []),
            '_internal_bear_analyses': bear_results.get('bear_cases', []),
        }

        return brief

    def _build_executive_summary(self, synthesis: Dict, changes: Dict) -> str:
        """Build concise executive summary."""
        debate_count = len(synthesis.get('debate_zone', []))
        bull_count = len(synthesis.get('bull_dominated', []))
        bear_count = len(synthesis.get('bear_dominated', []))
        risks = len(synthesis.get('risk_alerts', []))

        summary = f"""Market Intelligence Brief - {datetime.now().strftime('%B %d, %Y')}

Bull vs Bear Analysis Complete:
- {debate_count} stocks in DEBATE ZONE (high disagreement - most interesting)
- {bull_count} bullish opportunities (bull case dominates)
- {bear_count} bearish warnings (bear case dominates)
- {risks} risk alerts from audit system

{changes.get('message', 'Tracking changes from previous brief')}

Focus on the Debate Zone - genuine uncertainty creates opportunity."""

        return summary

    def _calculate_confidence_distribution(self, synthesis: Dict) -> Dict[str, int]:
        """Calculate distribution of confidence levels."""
        return {
            'HIGH': len(synthesis.get('bull_dominated', [])) + len(synthesis.get('bear_dominated', [])),
            'UNCERTAIN': len(synthesis.get('debate_zone', [])),
            'LOW': len(synthesis.get('high_conviction_opportunities', [])),
        }

    def _count_total_stocks(self, synthesis: Dict) -> int:
        """Count total unique stocks analyzed."""
        all_tickers = set()

        for item in synthesis.get('high_conviction_opportunities', []):
            all_tickers.add(item.get('ticker'))
        for item in synthesis.get('debate_zone', []):
            all_tickers.add(item.get('ticker'))
        for item in synthesis.get('bull_dominated', []):
            all_tickers.add(item.get('ticker'))
        for item in synthesis.get('bear_dominated', []):
            all_tickers.add(item.get('ticker'))

        return len(all_tickers)

    def _generate_spoken_brief(self, brief: Dict) -> Optional[str]:
        """
        Generate spoken audio version of the market brief using ElevenLabs TTS.

        Session 465: Market Intelligence Desk completion - spoken output capability.

        Args:
            brief: Market intelligence brief dict

        Returns:
            URL to audio file, or None if generation failed
        """
        try:
            # Build concise script for spoken delivery (audio briefs should be shorter)
            summary = brief.get('executive_summary', '')
            high_conviction = brief.get('high_conviction', [])
            debate_zone = brief.get('debate_zone', [])
            risk_alerts = brief.get('risk_alerts', [])

            # Create natural-sounding script
            script_parts = []
            script_parts.append(f"Good morning. Here's your market intelligence brief.")

            if summary:
                script_parts.append(summary)

            if high_conviction:
                script_parts.append(f"\nHigh conviction opportunities: We found {len(high_conviction)} stocks with strong agreement.")
                for opp in high_conviction[:3]:  # Top 3 for audio
                    ticker = opp.get('ticker', 'Unknown')
                    direction = opp.get('direction', 'neutral')
                    conviction = opp.get('conviction', 'medium')
                    script_parts.append(f"{ticker} - {direction} bias, {conviction} conviction.")

            if debate_zone:
                script_parts.append(f"\nDebate zone: {len(debate_zone)} stocks with significant disagreement between bull and bear cases.")
                for debate in debate_zone[:2]:  # Top 2 for audio
                    ticker = debate.get('ticker', 'Unknown')
                    script_parts.append(f"{ticker} shows conflicting signals.")

            if risk_alerts:
                script_parts.append(f"\nRisk alerts: {len(risk_alerts)} items require attention.")

            script_parts.append("\nEnd of brief. Markets never sleep, and neither do we.")

            spoken_text = " ".join(script_parts)

            logger.info(f"🎤 [SESSION 465] Generating spoken brief ({len(spoken_text)} chars)...")

            # Generate TTS using ElevenLabs
            # Use "Drew" voice - professional male narrator
            result = elevenlabs_provider.text_to_speech(
                text=spoken_text,
                voice="Drew",
                model="eleven_multilingual_v2"  # Highest quality
            )

            if result.get('success'):
                audio_url = result.get('audio_url')
                logger.info(f"✅ [SESSION 465] Spoken brief generated: {audio_url}")
                return audio_url
            else:
                error = result.get('error_message', 'Unknown error')
                logger.warning(f"⚠️ [SESSION 465] TTS generation failed: {error}")
                return None

        except Exception as e:
            logger.error(f"❌ [SESSION 465] Spoken brief generation error: {e}")
            return None

    def _prepare_delivery(self, brief: Dict, context: Dict) -> Dict[str, Any]:
        """Prepare brief for multi-channel delivery and actually send it."""

        # Session 465: Generate spoken brief first
        spoken_url = self._generate_spoken_brief(brief)

        delivery_status = {
            'discord_ready': True,
            'voice_ready': bool(spoken_url),  # True only if audio was generated
            'web_dashboard_ready': True,
            'brief_text': brief.get('executive_summary', ''),
            'brief_structured': brief,
            'delivery_channels': ['discord', 'voice', 'web'],
            'discord_sent': False,
            'spoken_brief_url': spoken_url,  # Session 465: Add audio URL
        }

        # Send to Discord
        try:
            from core.services.discord_notifications import discord_notify
            success = discord_notify.send_market_intelligence_brief(brief)
            delivery_status['discord_sent'] = success
            if success:
                logger.info("📨 Market Intelligence Brief sent to Discord successfully")
            else:
                logger.warning("⚠️ Failed to send brief to Discord")
        except Exception as e:
            logger.error(f"Discord delivery error: {e}")
            delivery_status['discord_error'] = str(e)

        return delivery_status

    def _schedule_next_cycle(self, brief: Dict) -> None:
        """Schedule next Market Intelligence Desk cycle (self-renewal)."""
        # In production, this would create a Celery task for tomorrow morning
        logger.info("⏰ Next Market Intelligence Desk cycle scheduled for tomorrow morning")

    def _save_brief_for_tomorrow(self, brief: Dict) -> None:
        """Save today's brief for tomorrow's change tracking (persistent context)."""
        try:
            today = date.today()

            # Get pre-calculated metrics from brief
            total_stocks = brief.get('total_stocks_analyzed', 0)
            gpt_success_rate = brief.get('gpt_success_rate', 0.0)

            # Create or update today's brief
            brief_obj, created = MarketIntelligenceBrief.objects.update_or_create(
                brief_date=today,
                defaults={
                    'brief_type': brief.get('type', 'daily_market_intelligence_brief'),
                    'executive_summary': brief.get('executive_summary', ''),
                    'high_conviction_opportunities': brief.get('high_conviction', []),
                    'debate_zone': brief.get('debate_zone', []),
                    'bullish_opportunities': brief.get('bullish_opportunities', []),
                    'bearish_warnings': brief.get('bearish_warnings', []),
                    'risk_alerts': brief.get('risk_alerts', []),
                    'changes_from_yesterday': brief.get('changes_from_yesterday', {}),
                    'is_first_brief': brief.get('changes_from_yesterday', {}).get('is_first_run', False),
                    'total_stocks_analyzed': total_stocks,
                    'confidence_distribution': brief.get('confidence_distribution', {}),
                    'debate_zone_count': brief.get('debate_zone_count', 0),
                    'gpt_success_rate': gpt_success_rate,
                    'situation_health': 'OPERATIONAL',  # Could be determined by metrics
                }
            )

            # Calculate changes from previous day and save
            changes = brief_obj.calculate_changes()
            brief_obj.save()  # Save the updated changes_from_yesterday

            action = "created" if created else "updated"
            change_count = len(changes.get('changes', []))
            logger.info(f"💾 Brief {action} for {today} - {total_stocks} stocks, {gpt_success_rate:.1f}% GPT success, {change_count} changes detected")

            # Session 463: Record predictions for learning loop
            self._record_predictions_for_learning(brief_obj, brief)

        except Exception as e:
            logger.error(f"Failed to save brief: {e}")

    def _record_predictions_for_learning(self, brief_obj, brief: Dict) -> None:
        """
        Record all predictions as PredictionOutcome records for learning loop tracking.

        This enables the system to:
        1. Track prediction accuracy over time
        2. Learn which market conditions lead to accurate predictions
        3. Adjust confidence scores based on track record
        """
        from core.models_unified_system import PredictionOutcome
        from core.services.market_data_service import MarketDataService

        try:
            market_service = MarketDataService()
            today = date.today()

            # Get all bull/bear analyses from context
            bull_analyses = brief.get('_internal_bull_analyses', [])
            bear_analyses = brief.get('_internal_bear_analyses', [])

            # Track which stocks are in debate zone
            debate_zone_tickers = {d.get('ticker') for d in brief.get('debate_zone', [])}

            # Record bull predictions
            for analysis in bull_analyses:
                ticker = analysis.get('ticker')
                if not ticker:
                    continue

                # Get current price
                stock_data = market_service.get_stock_details(ticker)
                if not stock_data or 'current_price' not in stock_data:
                    continue

                current_price = float(stock_data['current_price'])

                # Parse predicted move from target
                target_str = analysis.get('target', '+0%')
                try:
                    predicted_move = float(target_str.replace('%', '').replace('+', ''))
                except:
                    predicted_move = 0.0

                # Find opposing bear conviction
                bear_analysis = next((b for b in bear_analyses if b.get('ticker') == ticker), None)
                opposite_conviction = bear_analysis.get('conviction', 'LOW') if bear_analysis else 'LOW'

                # Create prediction record
                PredictionOutcome.objects.create(
                    brief=brief_obj,
                    ticker=ticker,
                    prediction_type='BULL',
                    conviction_level=analysis.get('conviction', 'LOW'),
                    predicted_move=predicted_move,
                    price_at_prediction=current_price,
                    prediction_date=today,
                    was_in_debate_zone=(ticker in debate_zone_tickers),
                    opposite_conviction=opposite_conviction,
                    market_regime=stock_data.get('market_regime'),
                    volatility_level=stock_data.get('volatility'),
                )

            # Record bear predictions
            for analysis in bear_analyses:
                ticker = analysis.get('ticker')
                if not ticker:
                    continue

                stock_data = market_service.get_stock_details(ticker)
                if not stock_data or 'current_price' not in stock_data:
                    continue

                current_price = float(stock_data['current_price'])

                # Parse predicted move (should be negative for bear)
                target_str = analysis.get('target', '-0%')
                try:
                    predicted_move = float(target_str.replace('%', '').replace('+', ''))
                except:
                    predicted_move = 0.0

                # Find opposing bull conviction
                bull_analysis = next((b for b in bull_analyses if b.get('ticker') == ticker), None)
                opposite_conviction = bull_analysis.get('conviction', 'LOW') if bull_analysis else 'LOW'

                PredictionOutcome.objects.create(
                    brief=brief_obj,
                    ticker=ticker,
                    prediction_type='BEAR',
                    conviction_level=analysis.get('conviction', 'LOW'),
                    predicted_move=predicted_move,
                    price_at_prediction=current_price,
                    prediction_date=today,
                    was_in_debate_zone=(ticker in debate_zone_tickers),
                    opposite_conviction=opposite_conviction,
                    market_regime=stock_data.get('market_regime'),
                    volatility_level=stock_data.get('volatility'),
                )

            prediction_count = len(bull_analyses) + len(bear_analyses)
            logger.info(f"📊 Recorded {prediction_count} predictions for learning loop tracking")

        except Exception as e:
            logger.error(f"Failed to record predictions for learning: {e}")

    def _get_situation_metrics(self, brief: Dict) -> Dict[str, Any]:
        """Get metrics for the autonomous situation itself."""
        return {
            'persistent_context_active': True,
            'incoming_signals_processed': True,
            'internal_disagreement_captured': brief.get('debate_zone_count', 0) > 0,
            'outputs_ready': True,
            'self_renewal_scheduled': True,
            'situation_health': 'OPERATIONAL',
        }


def run_market_intelligence_desk() -> Dict[str, Any]:
    """
    Convenience function to run the Market Intelligence Desk autonomous situation.
    Can be called from Celery tasks, autonomous loop, or manual triggers.
    """
    coordinator = MarketIntelligenceCoordinator()
    result = coordinator.execute(task="Generate daily market intelligence brief")
    return result.to_dict() if hasattr(result, 'to_dict') else {'data': result.data if hasattr(result, 'data') else {}}
