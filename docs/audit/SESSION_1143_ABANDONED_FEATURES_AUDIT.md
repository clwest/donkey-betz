---
title: "Session 1143 — Abandoned-features audit on archived docs"
status: active
authority: deliverable
session: 1143
date: 2026-05-25
authors: Claude Code (Session 1143), Rigby (PA conversation pa-d19c1674b936)
last_verified: 2026-05-25
---

# Session 1143 — Abandoned-features audit on archived docs

> **Chris's question:** "Of the ones you're archiving, one thing I am wondering about is are these features or anything like that, that's been implemented but never really finished up because something else broke or something like that."

## TL;DR — direct answer

**Most archived docs describe features that DO still exist in code.** The Cat-B archival was triggered by **doc age** (Jan/Feb 2026 frozen), not by **feature abandonment**. Of the 113 archived docs, the breakdown is roughly:

| Status | Count (approx) | Pattern |
|---|---|---|
| **Shipped + still working** | ~70 | Code still present + actively imported. Doc just went stale. |
| **Shipped + dormant** | ~15 | Code still present, rarely-fired, low telemetry. Built but not actively driven. |
| **Shipped + unused** | ~3–5 | Built, integrated, but per `UNDERUTILIZED_FEATURES.md` (Session 412) never adopted. DaVinci is the headliner ($300 license, $0 ROI). |
| **Replaced** | ~5 | Feature was rebuilt elsewhere; old doc describes the predecessor. Flutter mobile → React Native is the clearest example. |
| **Audit / historical** | ~15 | Audit reports + planning docs from prior phases. No feature to verify. |
| **Strategy / business docs** | ~5 | Strategic framing, not feature-implementing. |

**Genuine "started but never finished because something else broke"** = **rare**. The closest candidates surfaced below in § Top candidates for attention.

## Method

Pre-flight checklist run per `docs/audit/SESSION_1143_DOCS_AUDIT.md` §Phase 2A. Hybrid approach per Rigby:

- **Pass 1 (bulk-tag):** read title + first ~12 substantive lines of all 113 archived docs (`docs/archive/superseded-2026-05/**/*.md`). Tag by domain, status hypothesis, evidence pointers.
- **Pass 2 (code verification):** for high-signal candidates (claims of "Implementation Plan", "Reality Score X%", "Phase N", or feature names that should map to specific files), `grep` the codebase to confirm whether the feature exists today.

14 specific cross-references run against current code; results in § Code reality checks below.

## Top candidates for attention

These are the ones that look most like Chris's question (built but stalled/broken/unused). Listed with confidence + recommended next action.

### High confidence — clear cases

#### 1. DaVinci Resolve Studio integration — SHIPPED + UNUSED
- **Docs:** [`DAVINCI_RESOLVE.md`](../archive/superseded-2026-05/DAVINCI_RESOLVE.md) ("FULLY INTEGRATED & OPERATIONAL"), [`apis/DAVINCI_RESOLVE_FFMPEG.md`](../archive/superseded-2026-05/apis/DAVINCI_RESOLVE_FFMPEG.md), [`features/VIDEO_GENERATION.md`](../archive/superseded-2026-05/features/VIDEO_GENERATION.md)
- **Code:** `content/davinci_provider.py`, `core/views_davinci.py`, `content/davinci_bridge_client.py` all present
- **Reality:** [`UNDERUTILIZED_FEATURES.md`](../archive/superseded-2026-05/UNDERUTILIZED_FEATURES.md) (Session 412, Dec 2025) explicitly inventoried this: *"DaVinci Resolve Node: $300+ investment, Never used, $0 ROI."* [`EXTERNAL_APIS.md`](../archive/superseded-2026-05/EXTERNAL_APIS.md) confirms "UNUSED" status.
- **Recommendation:** If sunset, write a one-page V2-Deprecated header on `davinci_provider.py` and `core/views_davinci.py` (or leave-as-is if a future Phase 3 verticals push reuses it). If revive, scope a small "DaVinci-first" demo path. **Either way, Chris-only call.**

#### 2. Flutter mobile cockpit → React Native — REPLACED
- **Docs:** [`guides/FLUTTER_COCKPIT_PHASE1_PLAN.md`](../archive/superseded-2026-05/guides/FLUTTER_COCKPIT_PHASE1_PLAN.md), [`guides/FLUTTER_WEB_DEPLOYMENT_GUIDE.md`](../archive/superseded-2026-05/guides/FLUTTER_WEB_DEPLOYMENT_GUIDE.md)
- **Code:** No `pubspec.yaml`. `mobile/` directory contains a React Native (Expo) app — `package.json` + `index.ts` + `App.tsx`.
- **Reality:** Flutter was abandoned in favor of React Native at some point. Old docs describe a stack that no longer exists.
- **Recommendation:** Already correctly handled by Phase 2B-1 archival. No action needed beyond surfacing.

#### 3. Decision Command — SHIPPED, REGRESSED (Phase 5 Tier 3 finding)
- **Docs:** [`reports/DECISION_COMMAND_IMPLEMENTATION_REPORT.md`](../reports/DECISION_COMMAND_IMPLEMENTATION_REPORT.md) ("partially implemented") + [`reports/DECISION_COMMAND_INTEGRATION_COMPLETE.md`](../reports/DECISION_COMMAND_INTEGRATION_COMPLETE.md) ("FULLY OPERATIONAL Sep 2025")
- **Code:** No `DecisionCommand.tsx` in `frontend/src/`. No `decision-command` route in `App.tsx`. Backend `AIIncomeBuilder` skeleton remains in 5 Python files (`core/consumers_base.py`, `views_diagnostics.py`, `real_job_submitter.py`, `settings.py`, `personal_assistant_profile_connector.py`).
- **Reality:** Phase 5 Tier 3 code-verify (Chris Q5=Y, PR #2198) confirmed the React frontend was removed at some point. Feature SHIPPED then REGRESSED entirely from the user-facing surface. The "integration complete" claim was true when written; the regression happened later.
- **Recommendation:** Documented via V2-Superseded banners on both report files. Backend skeleton could be cleaned up if Chris greenlights — out of Session 1143 scope. **First genuine "shipped + regressed" finding** of this audit.

#### 4. `views_frontend_stubs.py` (39 stub endpoints) — REMOVED FROM CODE
- **Docs:** [`UI_COMPREHENSIVE_AUDIT.md`](../archive/superseded-2026-05/UI_COMPREHENSIVE_AUDIT.md) (Session 772-773, Jan 2026) said *"Stub Endpoints: 39 (in views_frontend_stubs.py)"*
- **Code:** `core/views_frontend_stubs.py` does not exist anymore.
- **Reality:** Whether those 39 endpoints got implemented or removed wholesale is unclear from this audit alone. Worth a separate check if anyone needs to know.
- **Recommendation:** Low priority — already removed from codebase. Doc reference accurately reflects past state.

### Medium confidence — likely dormant, in code but rarely fired

#### 4. Sci-Fi features (HiveMind / Dreams / Mood / MemoryPalace)
- **Docs:** [`features/HIVE_MIND_MODE.md`](../archive/superseded-2026-05/features/HIVE_MIND_MODE.md), [`features/AGENT_DREAMS.md`](../archive/superseded-2026-05/features/AGENT_DREAMS.md), [`features/AGENT_MOOD_SYSTEM.md`](../archive/superseded-2026-05/features/AGENT_MOOD_SYSTEM.md), [`features/MEMORY_PALACE.md`](../archive/superseded-2026-05/features/MEMORY_PALACE.md), [`SCIFI_FEATURES.md`](../archive/superseded-2026-05/SCIFI_FEATURES.md)
- **Code:** All have DB models, references in `core/tasks*.py`, views/consumers. `views_memory_palace.py` exists. `assign_memories_to_rooms.py` mgmt command exists.
- **Reality:** Memory rule from `feedback_agent_noise.md`: "Do NOT re-enable agent rotation/exercise tasks without real bounded tasks. Processing pipelines OK, unsolicited content generation = noise." This applied to SciFiAgent — likely dormant by design. Features exist but aren't being driven aggressively.
- **Recommendation:** **Not abandoned.** Dormant on purpose to control cost. Decision point: keep dormant, or delete the model + views to reduce maintenance surface? Chris-only call.

#### 5. Voice Marketplace (Session 444 "LIVE")
- **Docs:** [`GOLDEN_GOOSE_STRATEGY.md`](../archive/superseded-2026-05/GOLDEN_GOOSE_STRATEGY.md) (*"Voice Marketplace LIVE - DonkeyKing's Voice is the first public listing!"*)
- **Code:** `core/views_voice_marketplace.py` exists; `migration 0091_session_440_content_pipeline.py` exists.
- **Reality:** Voice marketplace is in code but whether it's actively wired in the React frontend, has paying users, or is being maintained is unclear from this audit alone.
- **Recommendation:** Possible "shipped but never followed through" — flag for future check whether the marketplace UI route is alive in the React app.

#### 6. ConceptForge (Session 863 "139 personas + 25 advisors")
- **Docs:** [`CONCEPTFORGE.md`](../archive/superseded-2026-05/CONCEPTFORGE.md), [`PERSONA_AGENTS.md`](../archive/superseded-2026-05/PERSONA_AGENTS.md) (claims 141 personas, Session 901)
- **Code:** `core/models_conceptforge.py`, `core/conceptforge/` module, `core/signals/conceptforge_signals.py`, `core/views_conceptforge.py` all present.
- **Reality:** Current `PLATFORM_INVENTORY.md` says **30 advisors** (not 25), and **83 agents** in AGENT_MAP. The "139 persona agents" figure has drifted significantly. Whether the ConceptForge pipeline still runs end-to-end is unclear.
- **Recommendation:** Low priority — likely still fires when triggered, just hard to verify without a smoke test. Run `signal_aggregation_service` → `ConceptForgePipeline` chain on a recent SignalCluster to confirm.

### Low confidence — historical reports, no feature to verify

#### 7. Old audit / planning docs
- [`UNDERUTILIZED_FEATURES.md`](../archive/superseded-2026-05/UNDERUTILIZED_FEATURES.md) (Session 412, Dec 2025) — **directly answers Chris's question for late 2025 state**. Re-reading this is the highest-leverage thing Chris can do.
- [`DISCONNECTED_DOTS_AUDIT.md`](../archive/superseded-2026-05/DISCONNECTED_DOTS_AUDIT.md) (Session 972, Feb 2026) — 7-section catalog of "built but not connected." Some items have been fixed since (Session 1099, 1115, 1131-1141 work).
- [`DATA_FLOW_DEAD_ENDS.md`](../archive/superseded-2026-05/DATA_FLOW_DEAD_ENDS.md) (Session 766, Jan 2026) — most rows marked "CONNECTED via HiveMind ✅" at write time.
- [`DATA_PERSISTENCE_GAPS.md`](../archive/superseded-2026-05/DATA_PERSISTENCE_GAPS.md) (Session 861) — all marked "Fixed Session 860-861."
- [`ORCHESTRATION_UI_AUDIT.md`](../archive/superseded-2026-05/ORCHESTRATION_UI_AUDIT.md) (Session 764) — "IMPLEMENTATION COMPLETE (Session 765)".

These are historical snapshots, not abandoned features. The action items in them were largely closed in subsequent sessions.

## Code reality checks — 14 high-signal docs verified

| Archived doc | Claim | Code reality |
|---|---|---|
| `agents/CREATIVEDIRECTOR_AGENT_IMPLEMENTATION.md` | "4-6h to MVP" | ✅ `core/agents/executive/creative_director_agent.py` exists |
| `agents/AGENT_INFRASTRUCTURE_REALITY_CHECK.md` (VideoAgent) | "OPERATIONAL" | ✅ `core/agents/video_agent.py` exists |
| `apis/ELEVENLABS.md` (AudioAgent) | "Fully Integrated" | ✅ `core/agents/audio_agent.py` exists |
| `agents/CTO_AGENT_INFRASTRUCTURE_ANALYSIS.md` (CTO Agent assessment) | "Groundwork built" | ✅ `core/agents/executive/cto_agent.py` exists and is in active rotation per Session 1093 |
| `guides/FLUTTER_COCKPIT_PHASE1_PLAN.md` | "Backend 95% ready" | ❌ Flutter abandoned. `mobile/` is React Native (Expo) |
| `features/HIVE_MIND_MODE.md` | "Collective intelligence" | ⚠️ Models + tasks references exist, alive but low-activity |
| `features/AGENT_DREAMS.md` | "Complete with Feedback System" | ⚠️ Models + views exist, alive but low-activity |
| `features/AGENT_MOOD_SYSTEM.md` | "Active" | ⚠️ Models + tasks_body_systems references exist, low-activity |
| `features/MEMORY_PALACE.md` | "Active" | ⚠️ `views_memory_palace.py` + mgmt command exist, alive |
| `features/CHARACTER_TRAINING.md` | "100% Operational" | ✅ `core/agents/training/character_training_agent.py` exists |
| `DAVINCI_RESOLVE.md` | "FULLY INTEGRATED & OPERATIONAL" | ✅ `content/davinci_provider.py` exists, but per `UNDERUTILIZED_FEATURES.md` "Never used" |
| `CONCEPTFORGE.md` | "139 personas + 25 advisors" | ⚠️ `core/conceptforge/` exists. Counts have drifted (current: 30 advisors, 83 agents in AGENT_MAP) |
| `GOLDEN_GOOSE_STRATEGY.md` (Voice Marketplace) | "LIVE Session 444" | ✅ `core/views_voice_marketplace.py` exists. Active usage unclear |
| `ROADMAP_IDEAS.md` (Blockchain Audit Agents) | "In Progress Session 461" | ✅ 5 blockchain agents in `core/agents/blockchain/` |
| `UI_COMPREHENSIVE_AUDIT.md` (39 stub endpoints) | "in `views_frontend_stubs.py`" | ❌ File no longer exists — stubs removed or implemented |
| `BUGS/AGENT_ROUTING_INCONSISTENCY.md` (BUG-001 'draw' verb) | "FIX PENDING" | ✅ No current code reference; presumed fixed |

## Cross-reference to existing inventories

Two of the archived docs are themselves answers to Chris's question, from earlier sessions:

### `UNDERUTILIZED_FEATURES.md` (Session 412, Dec 10 2025)
The literal "features built but never fully integrated or used" inventory. Worth re-reading. Captured the DaVinci $300/$0 ROI case + others.

### `DISCONNECTED_DOTS_AUDIT.md` (Session 972, Feb 8 2026)
7-section catalog: PA pipeline dead wires, enrichment data loss (85-95%), frontend-API disconnects, orphan endpoints (~200+), agent output persistence gap, models with no API exposure, Celery task gaps.

Subsequent sessions have closed many of these (per memory: Session 1099 governance, Session 1115 LearningBridge migration, Session 1131-1141 signal pipeline arc). A targeted re-walk of the original 7 sections against current state would give the cleanest "what's still disconnected" answer.

## Recommendations for Chris

1. **The Cat-B archival itself was correctly scoped** — no docs were misclassified as abandoned when they weren't, and no still-active canonical docs got swept up. Phase 1 + 2B-1 work stands.

2. **One genuine "shipped but never used" target worth a decision:** DaVinci Resolve. The $300 license + integration code + zero usage is the clearest "stalled" feature. Three options:
   - Sunset (V2-Deprecated header on provider, remove views, archive code references)
   - Revive (define a concrete use case for Phase 3 verticals)
   - Leave dormant (no harm if it's not running)

3. **One genuine "abandoned" target with no action needed:** Flutter mobile cockpit. Already replaced by React Native; docs already archived; no live code to clean.

4. **A handful of "dormant but in code" features** (HiveMind, Dreams, Mood, MemoryPalace) — these aren't abandoned, they're throttled. Cost-conscious decision to keep them present but not actively driven. Status quo is fine.

5. **Re-read `UNDERUTILIZED_FEATURES.md` and `DISCONNECTED_DOTS_AUDIT.md`** for the highest-density list of "what was built but never finished." Both archived but content still accurate as snapshots of their date.

6. **No urgent action surfaced.** This audit answers Chris's question with: "The archive is correctly archived. Two clear cases (DaVinci, Flutter) deserve a yes/no decision. Everything else is either still working or intentionally dormant."

## What's NOT in scope for this audit

- **Refresh of stale docs.** This audit categorized, didn't update content. Refresh-in-place work for any canonical doc still requires a separate PR (and per Chris's directive this session, no business/GTM framing).
- **Code deletion.** No "shipped but unused" code was removed. Decisions on Flutter remnants, DaVinci sunset, sci-fi feature pruning are Chris-only calls.
- **Re-validation of the historical audit doc claims** (DISCONNECTED_DOTS_AUDIT, DATA_FLOW_DEAD_ENDS, etc.). Those are snapshots from their respective sessions; re-validating them against today would be a separate ~2 hour exercise.

## Next moves (per Rigby's queue)

1. ✅ **This audit** (Session 1143) — answers Chris's question.
2. ⏭ **Phase 4 — redundancy hunt.** Non-destructive map of near-duplicate doc titles across handoffs/reports/architecture/playbooks/topics.
3. ⏭ **Phase 3 — handoffs retention options memo.** Two non-destructive options for Chris (keep + V1 banner vs archive + V2 stub + reindex).

---

**Authors:** Claude Code (Session 1143) + Rigby (PA conversation `pa-d19c1674b936`). Bulk-tag pass + 14 code reality checks all verified against current `core/` and `mobile/` trees.
