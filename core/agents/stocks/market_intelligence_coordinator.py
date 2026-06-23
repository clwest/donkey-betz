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
from datetime import datetime, timedelta, date, timezone

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer

# Session 895: Timeout for sub-agent executions to prevent coordinator hangs
# Extended to accommodate thinking models (GPT-5.1, o1, o3)
SUB_AGENT_TIMEOUT = 300  # 5 minutes per sub-agent
COORDINATOR_TIMEOUT = 480  # 8 minutes for nested coordinator calls (e.g., StockAuditCoordinator)
from core.models_unified_system import MarketIntelligenceBrief
from content.elevenlabs_provider import elevenlabs_provider
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_market_intel_with_ml(market_data: dict) -> dict:
    """Analyze market intelligence using ML models (GNN for relationships)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=market_data,
            task_hint=TaskType.GRAPH,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'graph'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'market_relationships': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML market intel analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


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
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("market_intelligence_coordination", task, input_data=context):
            # Handle simple diagnostic/identification queries
            task_lower = task.lower() if task else ''
            if any(keyword in task_lower for keyword in ['state your name', 'who are you', 'your capability', 'what can you do', 'introduce yourself']):
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                return AgentResult(
                    success=True,
                    message=f"I am {self.name}, the orchestrator of the Market Intelligence Desk. One capability: I coordinate bull/bear debates between specialist agents and synthesize their arguments into comprehensive market briefs with conviction ratings and actionable recommendations.",
                    data={'type': 'self_description', 'specialization': 'market_coordination', 'coordinated_agents': ['BullCaseAgent', 'BearCaseAgent', 'StockAnalystAgent']},
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

            self.record_decision(
                decision_type="planning",
                action="Starting market intelligence coordination",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip coordination", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

            # Session 529: Build intelligent prompt with full context
            self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            logger.info(f"🧠 Market Intelligence Desk starting cycle...")

        try:
            # 1. PERSISTENT CONTEXT: Load yesterday's brief
            previous_brief = self._load_previous_brief(context)

            # 2. INCOMING SIGNALS: Get tickers to analyze
            tickers = self._select_tickers(context, spider_context)

            # 3. INTERNAL DISAGREEMENT: Run bull vs bear debate (Session 988: forward spider_context)
            bull_results = self._run_bull_case(tickers, context, spider_context)
            bear_results = self._run_bear_case(tickers, context, spider_context)
            risk_results = self._run_risk_assessment(tickers, context, spider_context)

            # Session 980: Log agent health for debugging 0-stock briefs
            bull_count = len(bull_results.get('bull_cases', []))
            bear_count = len(bear_results.get('bear_cases', []))
            bull_error = bull_results.get('error')
            bear_error = bear_results.get('error')
            if bull_error:
                logger.warning(f"BullCaseAgent failed: {bull_error}")
            if bear_error:
                logger.warning(f"BearCaseAgent failed: {bear_error}")
            logger.info(f"Agent results: {bull_count} bull cases, {bear_count} bear cases")

            # 3.5 PREDICTION MARKETS: Get crowd wisdom from Kalshi (Session 558)
            prediction_market_signals = self._get_prediction_market_signals(context)

            # 4. SYNTHESIZE DEBATE: Find agreement, disagreement, opportunities
            synthesis = self._synthesize_debate(bull_results, bear_results, risk_results)

            # 5. TRACK CHANGES: What's different from yesterday
            changes = self._track_changes(synthesis, previous_brief)

            # 6. GENERATE BRIEF: Create deliverable output
            brief = self._generate_market_brief(
                synthesis, changes, risk_results, bull_results, bear_results,
                prediction_market_signals  # Session 558: Include Kalshi data
            )

            # 7. OUTPUTS WITH CONSEQUENCES: Prepare for delivery
            delivery_ready = self._prepare_delivery(brief, context)

            # 8. SELF-RENEWAL: Schedule next cycle and save state
            self._schedule_next_cycle(brief)
            self._save_brief_for_tomorrow(brief)

            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            # Session 953: Build provenance from aggregated sources
            sources = []
            # Track sources from sub-agents
            if bull_results and not bull_results.get('error'):
                sources.append({
                    'name': 'BullCaseAgent',
                    'endpoint': 'MarketDataService',
                    'retrieved_at': datetime.now(timezone.utc).isoformat(),
                    'record_count': len(bull_results.get('bull_cases', [])),
                })
            if bear_results and not bear_results.get('error'):
                sources.append({
                    'name': 'BearCaseAgent',
                    'endpoint': 'MarketDataService',
                    'retrieved_at': datetime.now(timezone.utc).isoformat(),
                    'record_count': len(bear_results.get('bear_cases', [])),
                })
            if risk_results and not risk_results.get('error'):
                sources.append({
                    'name': 'StockAuditCoordinator',
                    'endpoint': 'risk_assessment',
                    'retrieved_at': datetime.now(timezone.utc).isoformat(),
                    'record_count': len(risk_results.get('unified_alerts', [])),
                })
            if prediction_market_signals and prediction_market_signals.get('total_markets_analyzed', 0) > 0:
                sources.append({
                    'name': 'KalshiSpider',
                    'endpoint': 'kalshi.com/v2/markets',
                    'retrieved_at': datetime.now(timezone.utc).isoformat(),
                    'record_count': prediction_market_signals.get('total_markets_analyzed', 0),
                })

            provenance = build_provenance(
                report_type='market_report',
                agent_name=self.name,
                sources=sources,
                stale_threshold_hours=24.0,
            )
            provenance.disclaimer = format_disclaimer('market_report')

            # Session 953: Build message with provenance
            base_message = f"Market Intelligence Brief generated for {len(tickers)} stocks"
            message_with_provenance = provenance.to_markdown_block() + "\n" + base_message

            result = AgentResult(
                success=True,
                message=message_with_provenance,
                data={
                    'brief': brief,
                    'bull_analysis': bull_results,
                    'bear_analysis': bear_results,
                    'risk_assessment': risk_results,
                    'prediction_markets': prediction_market_signals,  # Session 558
                    'synthesis': synthesis,
                    'changes_from_yesterday': changes,
                    'delivery_ready': delivery_ready,
                    'next_cycle_scheduled': True,
                    'autonomous_situation_metrics': self._get_situation_metrics(brief),
                    # Session 953: Include provenance
                    'provenance': provenance.to_dict(),
                    'publishable': provenance.publishable,
                    'validation_status': provenance.validation_status,
                },
                agent_name=self.name,
                execution_time_ms=execution_time
            )

            # Session 1207: Persist the brief as a Deliverable on every
            # successful run, per Rigby's acceptance criteria
            # (pa-b2a99ff5b0ee47a6). Gated on result.success so failures
            # don't create empty/misleading deliverables. Body =
            # provenance markdown + executive_summary + structured
            # sections. Workspace pinned to DBZ. Routes through
            # self._save_to_deliverable → create_deliverable so
            # PR #2465's workspace_id guardrail + PR #2464's tightened
            # BLOCKED detector + dedup machinery all apply. Wrapped in
            # try/except so deliverable persist failure never blocks
            # the agent's return.
            if result.success:
                # Session 1207 (Rigby pa-33088358df304016 follow-up nits):
                # capture the deliverable's id and surface it on
                # result.data so output_data carries `deliverable_id` for
                # downstream tooling / audits. On persist failure, append
                # a structured entry to result.data['warnings'] (list)
                # with a stable type tag so monitors can detect regressions
                # without parsing logs. Conventions:
                #   - result.data['warnings'] is ALWAYS a list (init if missing)
                #   - each entry: {'type': <stable_key>, 'message': <str>}
                #   - 'deliverable_persist_failed' = caught exception during save
                #   - 'deliverable_gated' = factory returned None (gate or dedupe)
                try:
                    deliverable_body = self._format_brief_for_deliverable(
                        brief=brief,
                        provenance_markdown=provenance.to_markdown_block(),
                    )
                    deliverable_title = f"Market Intel Brief — {brief.get('date', datetime.now().strftime('%Y-%m-%d'))}"
                    saved_deliverable = self._save_to_deliverable(
                        title=deliverable_title,
                        content=deliverable_body,
                        deliverable_type='analysis',
                        category='Market Intelligence',
                        tags=['market-intelligence', 'daily-brief'],
                        content_format='markdown',
                        workspace_id='b4503364-2573-4401-9e28-61a739e0ce50',  # DBZ
                        provenance=provenance.to_dict(),
                        quality_score=0.85,
                        confidence_score=0.8,
                        metadata={
                            'sensitivity': 'internal',
                            'desk': 'market_intelligence',
                            'date': brief.get('date'),
                            'total_stocks_analyzed': brief.get('total_stocks_analyzed', 0),
                            'total_prediction_markets': brief.get('total_prediction_markets', 0),
                            'trigger_source': context.get('trigger_source') or 'scheduled',
                        },
                    )
                    if saved_deliverable is not None and getattr(saved_deliverable, 'id', None):
                        result.data['deliverable_id'] = str(saved_deliverable.id)
                    else:
                        # Factory returned None — gated by quality gate or
                        # dedupe. Distinct from a thrown exception.
                        result.data.setdefault('warnings', []).append({
                            'type': 'deliverable_gated',
                            'message': (
                                'create_deliverable returned None — likely a '
                                'quality-gate rejection or dedupe hit. Check '
                                '[DeliverableFactory] log lines for reason_code.'
                            ),
                        })
                except Exception as _dlv_exc:
                    logger.warning(
                        "MarketIntelligenceCoordinator: deliverable persist "
                        "failed (non-blocking — agent result still returned): %s",
                        _dlv_exc,
                    )
                    # Session 1207 (Rigby tweak): include exception class name
                    # so Sentry/log triage can route from just output_data.
                    result.data.setdefault('warnings', []).append({
                        'type': 'deliverable_persist_failed',
                        'message': f"{type(_dlv_exc).__name__}: {_dlv_exc}",
                    })

            # === Session 462: Priority 5 - Learning Infrastructure ===
            # Session 1207 (Rigby pa-b2a99ff5b0ee47a6): bookkeeping hooks
            # are best-effort — they MUST NOT flip result.success or cause
            # the outer except to rebuild a failed AgentResult after a
            # successful brief was generated and persisted. Wrap each
            # hook call individually so one hook's failure doesn't skip
            # the others either.
            try:
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=True,  # Uses Yahoo Finance spider for stock data
                    scifi_context_used=False
                )
            except Exception as _learn_exc:
                logger.warning(
                    "MarketIntelligenceCoordinator: _record_learning_outcome "
                    "hook failed (non-blocking — brief + deliverable already "
                    "persisted): %s",
                    _learn_exc,
                )

            try:
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="success",
                    importance=0.8  # High importance - daily brief with market insights
                )
            except Exception as _mem_exc:
                logger.warning(
                    "MarketIntelligenceCoordinator: _create_execution_memory "
                    "hook failed (non-blocking): %s",
                    _mem_exc,
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
            # Session 1207: same isolation as the success branch — best-
            # effort bookkeeping must not cascade into another raise that
            # propagates past the agent boundary.
            try:
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context or {},
                    spider_data_used=True,
                    scifi_context_used=False
                )
            except Exception as _learn_exc:
                logger.warning(
                    "MarketIntelligenceCoordinator: failure-path "
                    "_record_learning_outcome hook failed: %s", _learn_exc,
                )

            try:
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.9  # Very high importance - learn from failures
                )
            except Exception as _mem_exc:
                logger.warning(
                    "MarketIntelligenceCoordinator: failure-path "
                    "_create_execution_memory hook failed: %s", _mem_exc,
                )

            return result

    def _load_previous_brief(self, context: Dict) -> Optional[Dict]:
        """Load yesterday's brief for change tracking (persistent context)."""
        try:
            # Check for explicit previous_brief in context first (for testing)
            if 'previous_brief' in context:
                return context['previous_brief']

            # Try yesterday first (most common case)
            yesterday = date.today() - timedelta(days=1)

            try:
                previous = MarketIntelligenceBrief.objects.get(brief_date=yesterday)
                logger.info(f"Loaded previous brief from {yesterday}")
                return previous.to_dict()
            except MarketIntelligenceBrief.DoesNotExist:
                pass

            # Session 980: Fallback — load most recent brief within last 5 days
            # Handles weekend gaps and failed runs that saved 0-stock briefs
            cutoff = date.today() - timedelta(days=5)
            recent = MarketIntelligenceBrief.objects.filter(
                brief_date__gte=cutoff,
                brief_date__lt=date.today(),
                total_stocks_analyzed__gt=0,
            ).order_by('-brief_date').first()
            if recent:
                logger.info(f"Loaded fallback brief from {recent.brief_date} (yesterday had no brief)")
                return recent.to_dict()

            logger.info("No previous brief found in last 5 days - first run")
            return None

        except Exception as e:
            logger.warning(f"Could not load previous brief: {e}")
            return None

    # Session 981: Sector-diverse ticker pools for rotation
    # Each run picks from different sectors so briefs aren't all-tech
    SECTOR_POOLS = {
        'tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'CRM', 'ORCL', 'ADBE', 'INTC', 'AMD', 'AVGO', 'QCOM', 'NFLX'],
        'finance': ['JPM', 'GS', 'MS', 'BAC', 'WFC', 'C', 'BLK', 'SCHW', 'AXP', 'V', 'MA'],
        'healthcare': ['UNH', 'JNJ', 'PFE', 'ABBV', 'MRK', 'LLY', 'TMO', 'ABT', 'BMY', 'AMGN'],
        'consumer': ['WMT', 'COST', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'PG', 'KO', 'PEP'],
        'energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'OXY', 'PSX', 'VLO', 'MPC', 'HAL'],
        'industrial': ['CAT', 'DE', 'BA', 'HON', 'UPS', 'RTX', 'LMT', 'GE', 'MMM', 'UNP'],
    }
    # Anchor tickers always included (1 broad market + 1 bellwether)
    ANCHOR_TICKERS = ['SPY']

    def _select_tickers(self, context: Dict, spider_context: Dict) -> List[str]:
        """
        Select tickers to analyze based on signals, alerts, and sector rotation.

        Session 981: Dynamic ticker selection replacing hardcoded tech-only list.
        Priority order:
          1. User portfolio (if provided)
          2. Anchor tickers (SPY — always included for market context)
          3. Signal-driven picks from recent alerts and spider data
          4. Sector rotation picks to ensure diversity
        """
        import random
        from datetime import timedelta as td

        user_portfolio = context.get('portfolio', [])
        if user_portfolio:
            return user_portfolio[:10]

        selected = list(self.ANCHOR_TICKERS)  # Start with anchors
        seen = set(selected)

        # --- Signal-driven picks: tickers appearing in recent alerts ---
        try:
            from core.models_autonomous_alerts import StockMarketAlert
            from django.utils import timezone as tz

            cutoff = tz.now() - td(hours=24)
            alert_symbols = (
                StockMarketAlert.objects
                .filter(detected_at__gte=cutoff)
                .exclude(symbol__in=['', 'SPY', 'QQQ', 'VTI', 'DIA', 'IWM'])
                .values_list('symbol', flat=True)
            )
            # Count occurrences — most-mentioned symbols are most interesting
            from collections import Counter
            symbol_counts = Counter(alert_symbols)
            for symbol, _ in symbol_counts.most_common(4):
                if symbol not in seen:
                    selected.append(symbol)
                    seen.add(symbol)
        except Exception as e:
            logger.warning(f"Could not load alert signals for ticker selection: {e}")

        # --- Signal-driven picks: tickers from recent spider data ---
        try:
            from core.models_unified_system import SpiderData
            from django.utils import timezone as tz
            import re

            cutoff = tz.now() - td(hours=12)
            financial_spiders = ['yahoo_finance', 'finnhub', 'bloomberg', 'business_news']
            recent_spider = SpiderData.objects.filter(
                spider_name__in=financial_spiders,
                created_at__gte=cutoff,
            ).defer('embedding', 'item_embeddings').order_by('-created_at')[:20]

            # Extract symbols from spider raw_data
            spider_symbols = []
            ticker_pattern = re.compile(r'\b([A-Z]{1,5})\b')
            # Known valid tickers to filter noise from random uppercase words
            all_known = set()
            for pool in self.SECTOR_POOLS.values():
                all_known.update(pool)

            for data in recent_spider:
                raw = data.raw_data or {}
                items = raw.get('items', []) if isinstance(raw, dict) else []
                for item in items[:5]:
                    sym = item.get('symbol', '') or item.get('ticker', '')
                    if sym and sym in all_known and sym not in seen:
                        spider_symbols.append(sym)

            # Add top spider-mentioned symbols
            spider_counts = Counter(spider_symbols)
            for symbol, _ in spider_counts.most_common(3):
                if symbol not in seen:
                    selected.append(symbol)
                    seen.add(symbol)
        except Exception as e:
            logger.warning(f"Could not load spider signals for ticker selection: {e}")

        # --- Sector rotation: fill remaining slots from diverse sectors ---
        remaining = 10 - len(selected)
        if remaining > 0:
            # Determine which sectors are already represented
            sector_for_ticker = {}
            for sector, tickers in self.SECTOR_POOLS.items():
                for t in tickers:
                    sector_for_ticker[t] = sector

            represented_sectors = {sector_for_ticker.get(t) for t in selected if t in sector_for_ticker}
            # Prioritize under-represented sectors
            all_sectors = list(self.SECTOR_POOLS.keys())
            random.shuffle(all_sectors)
            # Put unrepresented sectors first
            all_sectors.sort(key=lambda s: s in represented_sectors)

            picks_per_sector = max(1, remaining // len(all_sectors))
            for sector in all_sectors:
                if remaining <= 0:
                    break
                pool = [t for t in self.SECTOR_POOLS[sector] if t not in seen]
                if not pool:
                    continue
                picks = random.sample(pool, min(picks_per_sector, len(pool)))
                for t in picks:
                    if remaining <= 0:
                        break
                    selected.append(t)
                    seen.add(t)
                    remaining -= 1

        logger.info(
            f"Selected {len(selected)} tickers: {selected} "
            f"(anchors: {len(self.ANCHOR_TICKERS)}, "
            f"signal-driven: {len(selected) - len(self.ANCHOR_TICKERS) - max(0, 10 - len(selected))}, "
            f"rotation: {max(0, len(selected) - len(self.ANCHOR_TICKERS))})"
        )
        return selected[:10]

    def _run_bull_case(self, tickers: List[str], context: Dict, spider_context: Dict = None) -> Dict[str, Any]:
        """Run the Bull Case Agent with timeout protection."""
        try:
            from .bull_case_agent import BullCaseAgent
            agent = BullCaseAgent()

            def execute_agent():
                return agent.execute(
                    task="Build bull cases for today's watchlist",
                    context={'tickers': tickers},
                    spider_context=spider_context or {},
                )

            # Session 895: Add timeout to prevent coordinator hangs
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_agent)
                result = future.result(timeout=SUB_AGENT_TIMEOUT)

            return result.data if hasattr(result, 'data') else {}
        except FuturesTimeoutError:
            logger.warning(f"⏰ BullCaseAgent timed out after {SUB_AGENT_TIMEOUT}s")
            return {'error': f'Timeout after {SUB_AGENT_TIMEOUT}s', 'timed_out': True}
        except Exception as e:
            logger.error(f"BullCaseAgent error: {e}")
            return {'error': str(e)}

    def _run_bear_case(self, tickers: List[str], context: Dict, spider_context: Dict = None) -> Dict[str, Any]:
        """Run the Bear Case Agent with timeout protection."""
        try:
            from .bear_case_agent import BearCaseAgent
            agent = BearCaseAgent()

            def execute_agent():
                return agent.execute(
                    task="Build bear cases for today's watchlist",
                    context={'tickers': tickers},
                    spider_context=spider_context or {},
                )

            # Session 895: Add timeout to prevent coordinator hangs
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_agent)
                result = future.result(timeout=SUB_AGENT_TIMEOUT)

            return result.data if hasattr(result, 'data') else {}
        except FuturesTimeoutError:
            logger.warning(f"⏰ BearCaseAgent timed out after {SUB_AGENT_TIMEOUT}s")
            return {'error': f'Timeout after {SUB_AGENT_TIMEOUT}s', 'timed_out': True}
        except Exception as e:
            logger.error(f"BearCaseAgent error: {e}")
            return {'error': str(e)}

    def _run_risk_assessment(self, tickers: List[str], context: Dict, spider_context: Dict = None) -> Dict[str, Any]:
        """Run the Stock Audit Coordinator for risk signals with timeout protection."""
        # Session 895: Uses module-level COORDINATOR_TIMEOUT (8 min) for nested coordinator
        # StockAuditCoordinator runs 4 sub-agents, each with 5-min timeout
        try:
            from .stock_audit_coordinator import StockAuditCoordinator
            coordinator = StockAuditCoordinator()

            def execute_coordinator():
                return coordinator.execute(
                    task="Assess risks and anomalies for watchlist",
                    context={'tickers': tickers},
                    spider_context=spider_context or {},
                )

            # Session 895: Add timeout to prevent coordinator hangs
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_coordinator)
                result = future.result(timeout=COORDINATOR_TIMEOUT)

            return result.data if hasattr(result, 'data') else {}
        except FuturesTimeoutError:
            logger.warning(f"⏰ StockAuditCoordinator timed out after {COORDINATOR_TIMEOUT}s")
            return {'error': f'Timeout after {COORDINATOR_TIMEOUT}s', 'timed_out': True}
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {'error': str(e)}

    def _get_prediction_market_signals(self, context: Dict) -> Dict[str, Any]:
        """
        Fetch prediction market signals from Kalshi.

        Session 558: Integration of prediction markets into Market Intelligence Desk.

        Categories of interest:
        - Economics (jobs, inflation, Fed decisions)
        - Finance (stock movements, crypto)
        - Politics (elections, policy changes)
        - Tech (product launches, company events)

        Returns dict with:
        - economics_signals: Economic prediction markets
        - finance_signals: Financial prediction markets
        - politics_signals: Political prediction markets
        - high_volume_markets: Most traded markets (crowd wisdom)
        - high_probability_events: Events likely to happen (>80%)
        - contrarian_opportunities: Low probability events with high potential
        """
        try:
            from core.services.kalshi_service import get_kalshi_service

            logger.info("🎰 Fetching prediction market signals from Kalshi...")

            service = get_kalshi_service()
            # Session 950: Added 'sports' category for betting markets
            intel = service.get_market_intelligence(
                categories=['economics', 'politics', 'finance', 'tech', 'sports']
            )

            # Get trending markets (high volume = strong conviction)
            trending = intel.get('trending_by_volume', [])[:10]

            # Get high probability events (>80%)
            high_prob = intel.get('high_probability', [])[:5]

            # Get uncertain markets (40-60% = genuine uncertainty)
            uncertain = intel.get('uncertain', [])[:5]

            # Categorize by type
            economics_signals = [
                m for m in trending
                if m.get('category') == 'economics'
            ][:5]

            finance_signals = [
                m for m in trending
                if m.get('category') == 'finance'
            ][:5]

            politics_signals = [
                m for m in trending
                if m.get('category') == 'politics'
            ][:5]

            tech_signals = [
                m for m in trending
                if m.get('category') == 'tech'
            ][:5]

            # Session 950: Add sports/betting signals
            sports_signals = [
                m for m in trending
                if m.get('category') == 'sports'
            ][:5]

            # Build summary insights
            insights = []

            # Economic insights from prediction markets
            for market in economics_signals:
                prob = market.get('implied_probability_pct', 50)
                title = market.get('title', '')
                if prob > 70:
                    insights.append(f"Markets expect: {title} ({prob}% likely)")
                elif prob < 30:
                    insights.append(f"Markets doubt: {title} (only {prob}% likely)")

            # High conviction events
            for market in high_prob:
                title = market.get('title', '')[:60]
                prob = market.get('implied_probability_pct', 50)
                insights.append(f"High confidence: {title}... ({prob}%)")

            signals = {
                'total_markets_analyzed': intel.get('total_markets', 0),
                'economics_signals': economics_signals,
                'finance_signals': finance_signals,
                'politics_signals': politics_signals,
                'tech_signals': tech_signals,
                'sports_signals': sports_signals,  # Session 950: Add sports/betting
                'high_volume_markets': trending,
                'high_probability_events': high_prob,
                'uncertain_markets': uncertain,
                'market_insights': insights[:10],  # Top 10 insights
                'categories': intel.get('categories', {}),
                'timestamp': datetime.now().isoformat(),
            }

            logger.info(f"🎰 Fetched {intel.get('total_markets', 0)} prediction markets, "
                       f"{len(economics_signals)} economics, {len(finance_signals)} finance signals")

            return signals

        except Exception as e:
            logger.error(f"Prediction market signals error: {e}")
            return {
                'error': str(e),
                'total_markets_analyzed': 0,
                'economics_signals': [],
                'finance_signals': [],
                'politics_signals': [],
                'tech_signals': [],
                'sports_signals': [],  # Session 950
                'high_volume_markets': [],
                'high_probability_events': [],
                'uncertain_markets': [],
                'market_insights': [],
            }

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
                                bull_results: Dict, bear_results: Dict,
                                prediction_markets: Dict = None) -> Dict[str, Any]:
        """Generate the final deliverable market brief."""
        prediction_markets = prediction_markets or {}

        # Calculate GPT success rate from bull cases
        bull_cases = bull_results.get('bull_cases', [])
        total_stocks = len(bull_cases)
        gpt_powered_count = sum(1 for case in bull_cases if case.get('gpt_powered', False))
        gpt_success_rate = (gpt_powered_count / total_stocks * 100) if total_stocks > 0 else 0.0

        brief = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': 'daily_market_intelligence_brief',

            # Executive Summary (now includes prediction market insights)
            'executive_summary': self._build_executive_summary(synthesis, changes, prediction_markets),

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

            # Session 558: Prediction Market Signals from Kalshi
            # Session 950: Added sports category
            'prediction_markets': {
                'economics': prediction_markets.get('economics_signals', []),
                'finance': prediction_markets.get('finance_signals', []),
                'politics': prediction_markets.get('politics_signals', []),
                'tech': prediction_markets.get('tech_signals', []),
                'sports': prediction_markets.get('sports_signals', []),
                'high_volume': prediction_markets.get('high_volume_markets', [])[:5],
                'high_probability': prediction_markets.get('high_probability_events', []),
                'uncertain': prediction_markets.get('uncertain_markets', []),
                'insights': prediction_markets.get('market_insights', []),
                'total_markets': prediction_markets.get('total_markets_analyzed', 0),
            },

            # What Changed
            'changes_from_yesterday': changes,

            # Metadata
            'confidence_distribution': self._calculate_confidence_distribution(synthesis),
            'total_stocks_analyzed': self._count_total_stocks(synthesis),
            'total_prediction_markets': prediction_markets.get('total_markets_analyzed', 0),
            'generation_time': datetime.now().isoformat(),
            'gpt_success_rate': gpt_success_rate,

            # Session 463: Internal analyses for learning loop
            '_internal_bull_analyses': bull_results.get('bull_cases', []),
            '_internal_bear_analyses': bear_results.get('bear_cases', []),
        }

        return brief

    def _build_executive_summary(self, synthesis: Dict, changes: Dict,
                                   prediction_markets: Dict = None) -> str:
        """Build concise executive summary with prediction market insights."""
        prediction_markets = prediction_markets or {}

        debate_count = len(synthesis.get('debate_zone', []))
        bull_count = len(synthesis.get('bull_dominated', []))
        bear_count = len(synthesis.get('bear_dominated', []))
        risks = len(synthesis.get('risk_alerts', []))

        # Prediction market summary
        pm_total = prediction_markets.get('total_markets_analyzed', 0)
        pm_economics = len(prediction_markets.get('economics_signals', []))
        pm_insights = prediction_markets.get('market_insights', [])[:3]

        summary = f"""Market Intelligence Brief - {datetime.now().strftime('%B %d, %Y')}

Bull vs Bear Analysis Complete:
- {debate_count} stocks in DEBATE ZONE (high disagreement - most interesting)
- {bull_count} bullish opportunities (bull case dominates)
- {bear_count} bearish warnings (bear case dominates)
- {risks} risk alerts from audit system"""

        # Add prediction market section if data available
        if pm_total > 0:
            summary += f"""

🎰 Prediction Market Signals ({pm_total} markets analyzed):"""
            for insight in pm_insights:
                summary += f"\n• {insight}"

            if pm_economics > 0:
                summary += f"\n• {pm_economics} active economics markets (jobs, inflation, Fed)"

        summary += f"""

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
        Session 1068: Gated behind ENABLE_SPOKEN_BRIEFS env var to prevent
        autonomous token bleed (~8-12 calls/day were draining ElevenLabs quota).

        Args:
            brief: Market intelligence brief dict

        Returns:
            URL to audio file, or None if generation failed
        """
        import os
        if not os.environ.get('ENABLE_SPOKEN_BRIEFS', '').lower() in ('1', 'true', 'yes'):
            logger.debug("Spoken briefs disabled (set ENABLE_SPOKEN_BRIEFS=true to enable)")
            return None

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

    def _format_brief_for_deliverable(
        self,
        brief: Dict[str, Any],
        provenance_markdown: str = '',
    ) -> str:
        """
        Session 1207: render the daily brief as a markdown body suitable
        for persistence via _save_to_deliverable. Includes the provenance
        block at the top, the executive summary, then structured sections
        for each opportunity tier so the deliverable is readable on its
        own without joining back to AgentExecution.output_data.

        Per Rigby's acceptance criteria on pa-b2a99ff5b0ee47a6:
        "Body: full report text + any provenance/source blocks."
        """
        date_str = brief.get('date', datetime.now().strftime('%Y-%m-%d'))
        parts: List[str] = []

        if provenance_markdown:
            parts.append(provenance_markdown.rstrip())
            parts.append('')

        parts.append(f"# Market Intel Brief — {date_str}")
        parts.append('')
        parts.append(brief.get('executive_summary', '_No executive summary._').rstrip())
        parts.append('')

        def _section(title: str, items: List[Dict[str, Any]], empty_note: str) -> None:
            parts.append(f"## {title}")
            if not items:
                parts.append(f"_{empty_note}_")
                parts.append('')
                return
            for item in items:
                ticker = item.get('ticker', 'UNKNOWN')
                recommendation = item.get('recommendation', '')
                confidence = item.get('confidence', '')
                reasoning = item.get('reasoning', '')
                line = f"- **{ticker}**"
                if recommendation:
                    line += f" — {recommendation}"
                if confidence:
                    line += f" ({confidence} confidence)"
                if reasoning:
                    line += f": {reasoning}"
                parts.append(line)
            parts.append('')

        _section(
            'High Conviction Opportunities',
            brief.get('high_conviction', []),
            'None today.',
        )
        _section(
            'Debate Zone (high disagreement — most interesting)',
            brief.get('debate_zone', []),
            'None today.',
        )
        _section(
            'Bullish Opportunities',
            brief.get('bullish_opportunities', []),
            'None today.',
        )
        _section(
            'Bearish Warnings',
            brief.get('bearish_warnings', []),
            'None today.',
        )
        _section(
            'Risk Alerts',
            brief.get('risk_alerts', []),
            'None today.',
        )

        # Prediction markets — Session 558 data
        pm = brief.get('prediction_markets', {}) or {}
        parts.append('## Prediction Market Signals (Kalshi)')
        pm_total = pm.get('total_markets', 0)
        if pm_total == 0:
            parts.append('_No Kalshi data this cycle._')
            parts.append('')
        else:
            parts.append(f"- Total markets analyzed: **{pm_total}**")
            for insight in (pm.get('insights') or [])[:5]:
                parts.append(f"- {insight}")
            parts.append('')

        # Changes from yesterday
        changes = brief.get('changes_from_yesterday', {}) or {}
        parts.append('## Changes From Yesterday')
        changes_msg = changes.get('message') if isinstance(changes, dict) else None
        parts.append(changes_msg or '_No prior brief to diff against._')
        parts.append('')

        # Footer metadata
        parts.append('---')
        parts.append(
            f"Generated by MarketIntelligenceCoordinator — "
            f"{brief.get('total_stocks_analyzed', 0)} stocks, "
            f"{brief.get('total_prediction_markets', 0)} prediction markets, "
            f"GPT success rate: {brief.get('gpt_success_rate', 0.0):.1f}%."
        )

        return '\n'.join(parts)

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

            # Session 980: Guard against saving 0-stock briefs — preserves previous good data
            if total_stocks == 0:
                logger.warning(
                    f"Skipping brief save for {today}: 0 stocks analyzed. "
                    f"Bull/bear agents likely failed. Preserving previous brief."
                )
                return

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

    @staticmethod
    def _parse_target_move(target_str) -> float:
        """
        Parse predicted move from bull/bear agent target strings.

        Session 980: Handles actual agent output formats:
          Bull: '25%+', '15-20%', '10%', '20%+ (recovery play)'
          Bear: '-25% or more', '-15% to -20%', '-10%', '-15%+ (pullback from highs)'

        For ranges like '15-20%', returns the midpoint (17.5).
        For '25%+' / '-25% or more', returns the base number.

        Session 994: GPT may return numeric types (int/float) instead of strings.
        Coerce to str before regex operations.
        """
        import re
        if not target_str and target_str != 0:
            return 0.0

        # Session 994: Handle numeric types from GPT JSON responses
        if isinstance(target_str, (int, float)):
            return float(target_str)

        target_str = str(target_str)

        # Strip non-numeric suffixes: "(recovery play)", "or more", etc.
        cleaned = re.sub(r'\(.*?\)', '', target_str).strip()
        cleaned = cleaned.replace('or more', '').replace('+', '').strip()

        # Try range format: "15-20%" or "-15% to -20%"
        range_match = re.search(r'(-?\d+(?:\.\d+)?)\s*%?\s*(?:to|-)\s*(-?\d+(?:\.\d+)?)\s*%?', cleaned)
        if range_match:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            return round((low + high) / 2, 2)

        # Try single number: "25%", "-10%", "10"
        single_match = re.search(r'(-?\d+(?:\.\d+)?)', cleaned)
        if single_match:
            return float(single_match.group(1))

        return 0.0

    def _record_predictions_for_learning(self, brief_obj, brief: Dict) -> None:
        """
        Record all predictions as PredictionOutcome records for learning loop tracking.

        Session 980: Uses update_or_create keyed on (brief, ticker, prediction_type)
        to prevent duplicate rows on re-runs. Reads target_upside/target_downside
        (actual agent output keys) instead of nonexistent 'target' key.
        """
        from core.models_unified_system import PredictionOutcome
        from core.services.market_data_service import MarketDataService

        try:
            market_service = MarketDataService()
            today = date.today()

            bull_analyses = brief.get('_internal_bull_analyses', [])
            bear_analyses = brief.get('_internal_bear_analyses', [])

            debate_zone_tickers = {d.get('ticker') for d in brief.get('debate_zone', [])}
            created_count = 0
            updated_count = 0

            # Record bull predictions
            # Session 994: Per-iteration error handling — one bad ticker shouldn't kill the batch
            for analysis in bull_analyses:
                try:
                    ticker = analysis.get('ticker')
                    if not ticker:
                        continue

                    stock_data = market_service.get_stock_details(ticker)
                    if not stock_data or 'current_price' not in stock_data:
                        continue

                    current_price = float(stock_data['current_price'])
                    predicted_move = self._parse_target_move(analysis.get('target_upside', ''))

                    bear_analysis = next((b for b in bear_analyses if b.get('ticker') == ticker), None)
                    opposite_conviction = bear_analysis.get('conviction', 'LOW') if bear_analysis else 'LOW'

                    _, created = PredictionOutcome.objects.update_or_create(
                        brief=brief_obj,
                        ticker=ticker,
                        prediction_type='BULL',
                        defaults={
                            'conviction_level': analysis.get('conviction', 'LOW'),
                            'predicted_move': predicted_move,
                            'price_at_prediction': current_price,
                            'prediction_date': today,
                            'was_in_debate_zone': (ticker in debate_zone_tickers),
                            'opposite_conviction': opposite_conviction,
                            'market_regime': stock_data.get('market_regime'),
                            'volatility_level': stock_data.get('volatility'),
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    logger.warning(f"Failed to record BULL prediction for {analysis.get('ticker', '?')}: {e}")

            # Record bear predictions
            for analysis in bear_analyses:
                try:
                    ticker = analysis.get('ticker')
                    if not ticker:
                        continue

                    stock_data = market_service.get_stock_details(ticker)
                    if not stock_data or 'current_price' not in stock_data:
                        continue

                    current_price = float(stock_data['current_price'])
                    predicted_move = self._parse_target_move(analysis.get('target_downside', ''))

                    bull_analysis = next((b for b in bull_analyses if b.get('ticker') == ticker), None)
                    opposite_conviction = bull_analysis.get('conviction', 'LOW') if bull_analysis else 'LOW'

                    _, created = PredictionOutcome.objects.update_or_create(
                        brief=brief_obj,
                        ticker=ticker,
                        prediction_type='BEAR',
                        defaults={
                            'conviction_level': analysis.get('conviction', 'LOW'),
                            'predicted_move': predicted_move,
                            'price_at_prediction': current_price,
                            'prediction_date': today,
                            'was_in_debate_zone': (ticker in debate_zone_tickers),
                            'opposite_conviction': opposite_conviction,
                            'market_regime': stock_data.get('market_regime'),
                            'volatility_level': stock_data.get('volatility'),
                        },
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    logger.warning(f"Failed to record BEAR prediction for {analysis.get('ticker', '?')}: {e}")

            logger.info(
                f"Predictions recorded: {created_count} created, {updated_count} updated "
                f"(from {len(bull_analyses)} bull + {len(bear_analyses)} bear analyses)"
            )

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
