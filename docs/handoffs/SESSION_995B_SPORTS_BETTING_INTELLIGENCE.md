---
originating_session: 995
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 995B: Sports Betting Intelligence System

**Date:** February 12, 2026
**Type:** Feature — Multi-phase sports betting intelligence build

---

## What Changed

### Phase 1: PA Integration (First-Class Sports Betting Support)

1. **Sports betting intent** in `unified_pa_entrypoint.py`
   - Pattern: betting, odds, spread, moneyline, arbitrage, sharp action, line movement, wager, parlay, etc.
   - Routes to `sports_betting_tool`

2. **Payload builder** — Maps sub-intents to actions: overview, arbs, predictions, sharp_action, line_movements, wagers, live_odds, brief

3. **Result formatter** — Formats all 8 action types for natural language PA responses

4. **Tool handler** `_handle_sports_betting()` in `tool_dispatcher.py`
   - `overview`: Dashboard stats (pending/settled wagers, arb count, active sports)
   - `arbs`: Live arbitrage opportunities from HumanAttentionItem
   - `predictions`: Game predictions from MLPrediction
   - `sharp_action`: Runs SharpActionDetector agent live
   - `line_movements`: Runs LineMovementAnalyzer agent live
   - `wagers`: User's PlacedWager history
   - `brief`/`live_odds`: Full betting brief via SportsBettingCoordinator

### Phase 2: Three New Agents

5. **GamePredictor** (`core/agents/markets/game_predictor.py`)
   - Predicts game outcomes from odds consensus (implied probabilities, spreads, totals)
   - Stores predictions in `sports.models.MLPrediction`
   - LLM analysis via LLMProviderRegistry

6. **LineMovementAnalyzer** (`core/agents/markets/line_movement_analyzer.py`)
   - Compares current odds to stored SpiderData snapshots
   - Detects moneyline, spread, and total movements
   - Rates: STEAM > SHARP > DRIFT > NOISE

7. **SharpActionDetector** (`core/agents/markets/sharp_action_detector.py`)
   - Compares sharp books (Pinnacle, Circa) vs soft books (DraftKings, FanDuel)
   - Detects odds divergence, stale lines
   - Rates: HOT > WARM > COLD

### Phase 3: Intelligence Pipeline

8. **SportsBettingCoordinator** (`core/services/sports_betting_coordinator.py`)
   - Orchestrates all 5 betting agents: GamePredictor + SportsOddsAnalyst + ArbitrageDetector + LineMovementAnalyzer + SharpActionDetector
   - Produces unified briefs with executive summary + top plays (ranked by confidence)
   - Each agent runs independently — one failure doesn't kill the pipeline

9. **Celery tasks** in `core/tasks.py`:
   - `generate_daily_betting_brief` — Runs coordinator at 9 AM + 7 PM, stores brief as SpiderData
   - `evaluate_ml_predictions` — Checks MLPrediction accuracy every 6h using TheOddsSpider scores

10. **Beat schedule** in `core/settings.py`:
    - `generate-daily-betting-brief`: `crontab(hour='9,19', minute='0')`
    - `evaluate-ml-predictions`: `crontab(hour='*/6', minute='45')`

11. **Agent registration** in `agent_router.py` — All 3 new agents added to imports + AGENT_MAP

---

## Files Changed

| File | Action | Details |
|------|--------|---------|
| `core/agents/markets/game_predictor.py` | CREATE | ~350 lines |
| `core/agents/markets/line_movement_analyzer.py` | CREATE | ~350 lines |
| `core/agents/markets/sharp_action_detector.py` | CREATE | ~330 lines |
| `core/services/sports_betting_coordinator.py` | CREATE | ~290 lines |
| `core/agents/markets/__init__.py` | MODIFY | Added 3 imports + __all__ |
| `core/agent_router.py` | MODIFY | Added 3 agents to imports + AGENT_MAP |
| `core/services/unified_pa_entrypoint.py` | MODIFY | Added intent, payload, formatter |
| `core/services/tool_dispatcher.py` | MODIFY | Added registration + handler |
| `core/tasks.py` | MODIFY | Added 2 Celery tasks |
| `core/settings.py` | MODIFY | Added 2 beat schedule entries |

**Total:** 4 new files, 6 modified files. No models, no migrations.

---

## System Impact

| Metric | Before | After |
|--------|--------|-------|
| Market agents | 3 | 6 |
| PA intents | 37 | 38 |
| PA tool handlers | 51 | 52 |
| Celery tasks | 262 | 264 |
| Beat schedule entries | +2 | generate-daily-betting-brief, evaluate-ml-predictions |

---

## Data Flow

```
TheOddsSpider → fetch_data() / fetch_scores()
       ↓
  [5 Agents]
  GamePredictor → MLPrediction model
  SportsOddsAnalyst → value bets
  ArbitrageDetector → HumanAttentionItem (watch)
  LineMovementAnalyzer → SpiderData snapshots comparison
  SharpActionDetector → sharp vs soft book divergence
       ↓
  SportsBettingCoordinator → unified brief + top plays
       ↓
  PA sports_betting_tool → natural language responses
       ↓
  Celery: generate_daily_betting_brief (9AM/7PM)
  Celery: evaluate_ml_predictions (every 6h)
```
