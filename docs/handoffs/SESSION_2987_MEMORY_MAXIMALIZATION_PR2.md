# SESSION 2987 — Memory Maximalization PR2 (trace + supersede + hygiene + promotion cap-fix)

**Date:** 2026-07-26 evening (US/Denver)
**Merge:** `95d3cdc65` — PR #3633
**Spec deliverable:** `ba968ac1-95b4-4e14-82be-3cb02598edac` (Donkey Betz workspace `b4503364-…`)
**Session shape:** PLAYBOOK-7.7.1 spec→ship, all 9 phases walked (PR2 of 2, closes spec `ba968ac1`)
**Rigby cycles:** 3 SIGN passes (T1 REVISE → A2 pass 1 REVISE → A2 pass 2 PROCEED-TO-MERGE)

---

## Three-part summary

**What was done (plain English):**
Every PA turn's memory-injection block now records the concrete `UserMemoryContext` row IDs it retrieved (in a new "memory utilization trace" payload on the existing OpsRun event). Added supersede fields to `UserMemoryContext` (`is_active`, `superseded_by`, `superseded_at`) so hygiene can retire rows without ever deleting them. Fixed the auto-promotion cap bypass that caused Chris's 1803-vs-200 cap drift discovered at S2986 close — `memory_promotion_service` now respects `MEMORY_MAX_ITEMS` by demoting the oldest+lowest-importance auto-promotion row when at cap, and skipping (with a machine-readable "capped" event) if nothing safe to demote exists. New `memory_hygiene_audit` management command surfaces stale / cap-drift / conflict candidates and can supersede stale rows with `--apply` (never DELETE). PR #3633, sha `95d3cdc65`.

**How it improves the platform (before / after):**
- **Before PR2:** `memory_promotion_service.check_and_promote` bypassed the `MEMORY_MAX_ITEMS` cap check that `remember_tool.save` enforced, so a heavy PA user accumulated auto-promotion rows unbounded (Chris at 1803 rows against a 200 cap at S2986 close). No supersede semantics — hygiene would have had to hard-delete. No way to answer "did memory influence this response?" beyond an OpsRun event that said memory was "available" but not "which rows."
- **After PR2:** Cap bypass closed at the source. `UserMemoryContext` has proper supersede fields with a self-FK so retiring a row leaves the audit trail intact. Every prompt-injection retrieval returns the actual retrieved IDs alongside the context text, ready to land in the audit stream. Hygiene command surfaces the accumulation for manual review + supersedes low-signal stale rows on `--apply`. Live-verified: hygiene command dry-run on Chris shows 12 conflict tag-clusters (e.g. `type='project' tag='infra' rows_with_tag=1249`) and the correct cap-drift breakdown by source.

**Next-session first action:**
S2988 opens with no queued spec — the `ba968ac1` arc is now closed. High-value seed candidates: (a) `F-D3-tracker-scope` — a follow-up to activate the OpsRun tracker for PA turns so the new memory_injected trace payload actually lands in the audit stream (currently the substrate is ready but the event bridge is dormant — see §Post-merge findings), (b) `F-D2-broad` — the deferred non-PA LLM-bypass audit spec (14+ candidates found in Rigby's S2986 sweep), (c) run `memory_hygiene_audit --user chris --stale-days 30 --stale-importance-lt 10 --apply` to actually reconcile the 1803-vs-cap drift now that supersede semantics exist, (d) Rigby Tool Gap Ledger entry — add `OpsRunEvent` + `UserMemoryContext` to `orm_inspect_tool` allowlist (surfaced when Rigby couldn't run PR2 D3 live-verify probes from her tool surface).

---

## Session timeline

Playbook-7.7.1 nine-phase walk (continuation of the S2986 spec arc into PR2):

| Phase | What happened |
|---|---|
| **1 — Spec ingestion** | Reused from S2986 (same spec `ba968ac1`; scope already agreed via S2986 Phase 5 Chris ratification of the 2-PR split). |
| **2 — Pre-code sampling** | Confirmed cap-drift root cause at `memory_promotion_service.py:303` (unbounded `UserMemoryContext.objects.create` with no cap check). Discovered D2 target `ProjectBuilderOrchestrator._build_project_with_llm_only` is **dead-invocation code** — only demo/test callers (`ai_project_builder.py:555` is `__main__`, `epa_handlers_tools.py:2366` calls a different `AIProjectBuilder` class, `command_center_ai.py:982` is a preview response). Identified `OpsRunEvent` as the natural substrate for D3 trace (existing table, existing pattern via `memory_injected` event). |
| **3 — T1 SIGN pass 1** | Routed to Rigby with 5 pre-code findings including the D2 dead-code discovery + a proposed D2 descope. Verdict: **REVISE** with 10 tool_runs. Folded 3 refinements: F-PR2-1 (drop `pruned_at` from migration — not used yet), F-PR2-2 (DEMOTE-oldest-auto_promotion strategy vs pure SKIP — prevents cap-stuck-forever), F-D2-descope (endorsed). |
| **4 — Fold** | 7 same-PR mitigations + 4 future_triggers classified. |
| **5 — Chris framing** | Delivered mid-flight heads-up on D2 descope (dead-code discovery + "do we lose anything? / more work later?" plain-english framing per PLAYBOOK-7.7.3). Chris proceeded (Rigby-endorsed, no re-ratification needed — tightening within already-agreed shape). |
| **6 — Implement** | Migration (3 fields + composite index; auto-generator drift stripped — see §Migration isolation note), `MemoryContextService.get_prompt_context_with_trace`, `_get_weighted_memories` includes `id` + filters `is_active=True`, PA injection block extended with `retrieved_memory_ids` + `layer` in the existing `memory_injected` event, `memory_promotion_service` cap-fix with DEMOTE strategy, `memory_hygiene_audit` command (247 lines), 12 tests, operator doc PR2 section. |
| **7 — A2 SIGN pass 1** | 8 tool_runs at exact line ranges. Verdict: **REVISE** — 3 folds required: F-A2-1 (missed `is_active=True` filter in `get_content_preferences`), F-A2-2 (demotion ordering by `('importance', 'created_at')` — robust to future importance drift), F-A2-3 (`memory_promotion_capped` tracker event needs machine-readable `reason` field). |
| **7 — A2 SIGN pass 2** | 3 tool_runs verified all 3 folds applied correctly. Verdict: **PROCEED-TO-MERGE**. |
| **8 — Ship** | Committed as `a8f46adcd`, pushed, PR #3633 opened, merged via `gh pr merge --admin --squash --delete-branch` at sha `95d3cdc65`. |
| **9 — Recycle + close** | `make recycle-all` clean at `sha=95d3cdc6534d`. Live-dispatch smoke: migration landed (columns present, 1805 rows preserved), remember_tool.save still enforces cap (S2879 envelope shape), hygiene command dry-run for Chris surfaced correct cap-drift + 12 conflict tag-clusters. **Discovery:** `memory_injected` OpsRunEvent has fired ZERO times historically — pre-existing OpsRun tracker scope gap in PA turns (not a PR2 regression). Documented as F-D3-tracker-scope future_trigger. This handoff + 00-START refresh + session_lifecycle close. |

---

## Rigby cycle discipline

**T1 pass 1** — 10 tool_runs verified 5 pre-code findings (dead code confirmed at 4 sites, cap bypass source located, OpsRunEvent substrate confirmed, UserMemoryContext current fields, MemoryContextService return shape). Rigby's zoom-out prompts caught 2 substantive refinements: (a) `pruned_at` field was future-only speculation (drop it), (b) SKIP strategy would freeze memory forever for capped users (prefer DEMOTE).

**A2 pass 1** — 8 tool_runs at exact line ranges (`memory_context_service.py:85-176`, `memory_context_service.py:300-352`, `memory_promotion_service.py:302-397`, migration file, model file, hygiene command). Rigby found the **cache-shape-change search** result clean (no external readers of `{CACHE_PREFIX}:prompt:` key), the **FK ordering** correct (create new before setting superseded_by), the **migration isolation** clean (4 operations only, no drift). But surfaced 3 substantive issues at exact line ranges — the missed `is_active=True` filter in `get_content_preferences` was a real inconsistency that would have shipped superseded rows still influencing preference extraction.

**A2 pass 2** — 3 tool_runs verified all 3 fold sites (memory_context_service:213-220, memory_promotion_service:322-336, memory_promotion_service:338-360). All CONFIRMED. Verdict PROCEED-TO-MERGE.

**Zoom-out per PLAYBOOK-6.10.7:**
- **T1 ZO1** (migration surface): drop `pruned_at` → shipped as fold F-PR2-1.
- **T1 ZO2** (cap-fix strategy): DEMOTE not SKIP → shipped as fold F-PR2-2.
- **A2 ZO1** (importance-first demotion): robust to future importance drift → shipped as fold F-A2-2.
- **A2 ZO2** (OpsRunEvent pollution risk): approved — payload bloat modest (~11 IDs max + short layer string), no cardinality worsening, query value up.

---

## Fold classifications

**Same-PR mitigatable (all shipped in PR #3633):**
- F-PR2-1 — dropped `pruned_at` from migration (add later when actually needed)
- F-PR2-2 — DEMOTE-oldest-auto_promotion cap strategy (with SKIP fallback)
- F-A2-1 — `is_active=True` filter in `get_content_preferences` (parity with `_get_weighted_memories`)
- F-A2-2 — demotion ordering `('importance', 'created_at')` (robust to future importance drift)
- F-A2-3 — `memory_promotion_capped` tracker event includes machine-readable `reason` field
- F-D2-descope — D2 removed from PR2 (target was dead-invocation code)

**Future_trigger (logged for next-session backlog):**
- **F-D3-tracker-scope** (NEW at S2987 close from post-merge smoke discovery): Activate the OpsRun tracker for PA turns OR switch D3 trace substrate to a PA-turn-scoped surface. Currently `memory_injected` OpsRunEvent has never fired (zero rows historically) because `get_active_tracker()` returns `None` in PA turn context. The trace substrate (get_prompt_context_with_trace returning retrieved_ids) IS in place; only the audit-stream bridge is dormant. Not a PR2 regression — pre-existing gap.
- **F-D3-layer-expand** — extend `layer` discriminator beyond `'user_memory_context'` to include `'user_agent_learning'` and `'conversation_memory'` when those retrieval paths are also traced.
- **F-D2-broad** — broader non-PA LLM-bypass audit spec (Rigby's S2986 sweep found 14+ `enforce_real_ai` sites + 9 `client.responses.create` + 80 `client.chat.completions.create` non-PA callsites). Audit each for user-facing personalization impact and decide preflight scope. NOT PR2 scope.
- **F-ZO2** — relevance-threshold pre-injection filter (needs relevance-scoring infra).
- **F-ZO3** — structured citations OR post-hoc classifier for stronger "used" signal (self-report MVP is honest but weaker).
- **Rigby-tool-allowlist** (NEW at S2987 close): Add `OpsRunEvent` + `UserMemoryContext` to `orm_inspect_tool` allowlist so future live-dispatch smokes can be done from Rigby without dropping to shell. Rigby explicitly flagged this at post-merge smoke.

---

## Post-merge findings

**Live-dispatch smoke (four probes):**

1. **Migration landed cleanly (via Rigby's `db_health_tool.verify_table`):** `core_usermemorycontext` table has the 3 new columns (`is_active boolean`, `superseded_at timestamp`, `superseded_by_id bigint`), 1805 rows preserved unchanged, index `core_userme_user_ac_idx` created. Django migration state `up_to_date`.

2. **`remember_tool.save` regression check (via Rigby):** Returns migrated S2879 envelope with new `cap_hit` code as expected — `{success:false, error_code:'cap_hit', error, action:'save', current_count:1805, max_items:200}`. Cap enforcement still works for the `remember_tool` path.

3. **`memory_hygiene_audit --user chris` dry-run (local shell):** 0 stale (correctly — Chris's rows are all recent-enough or high-importance-enough to not hit the default threshold), CAP-DRIFT report shows Chris with 1805 active rows and source breakdown across dozens of `agent:*` sources plus `auto_promotion` (report truncated but shape correct), **12 CONFLICT tag-clusters surfaced**: `type='project'` with tags `infra=1249`, `ci=1161`, `repo=1093`, `release=1055`, `mobile=666`, `deploy=359`, `migration=346`, `rollback=70`, `railway=15`; `type='preference'` with `dm=4`, `notifications=5`, `ops=4`.

4. **D3 `memory_injected` OpsRunEvent probe (local shell):** ZERO rows exist historically. Not a PR2 regression — `get_active_tracker()` returns `None` in PA turn context (pre-existing OpsRun tracker scope gap since Session 628). The `get_prompt_context_with_trace` method IS returning correct `retrieved_ids` at the function-return level (verified by unit tests); only the OpsRunEvent bridge is dormant. Documented as F-D3-tracker-scope future_trigger.

**Chris's cap drift status:** Still at 1805 active rows (up from 1803 at S2986 close — 2 more auto_promotion accumulations landed between S2986 close and S2987 open, before PR2 shipped). Ongoing bypass is now closed. To reconcile historical rows, run `memory_hygiene_audit --user chris --stale-days 30 --stale-importance-lt 10 --apply` (would need re-tuned thresholds since defaults produce 0 stale for Chris's rows).

---

## Migration isolation note

The auto-generated migration from `python manage.py makemigrations core --name s2987_memory_supersede` bundled a LOT of unrelated pre-existing model drift: Narrative + NarrativeAlert + NarrativeEvidence + NarrativeShift model creation, HAIDispatchLog field alterations, FleetPAChatAuditRow field alterations, CuratedSignalEntry field alterations, RigbyWorkItem + LLMCallLog index renames.

These are pre-existing model definitions without corresponding migrations — an accumulation of model-file drift across many arcs. Not related to this session.

Isolated the migration manually to ONLY the 4 UserMemoryContext operations (3 AddField + 1 AddIndex). Header comment documents the choice + names the stripped drift so a future arc that touches those models has a pointer to the drift.

Rigby verified isolation at A2 SIGN pass 1: `core/migrations/0397_s2987_memory_supersede.py` — 4 operations exactly, no drift.

---

## Open follow-ups for S2988+

**High-value seeds** (Chris picks):
- **F-D3-tracker-scope** — activate OpsRun tracker for PA turns so the memory_injected trace payload actually lands in the audit stream. Substrate is ready; only bridge is dormant. ~1 session.
- **F-D2-broad** — broader non-PA LLM-bypass audit spec (defer or open? 14+ candidates). ~1 session for audit doc.
- **`memory_hygiene_audit --apply` on Chris's user** — with re-tuned `--stale-days 30 --stale-importance-lt 10`. ~30 min diagnostic + apply.
- **Rigby-tool-allowlist** — add `OpsRunEvent` + `UserMemoryContext` to `orm_inspect_tool` allowlist. ~15-30 min.

**Deferred from prior sessions** (still open):
- Chris browser visual check on shipped S2985 Canonical Briefing
- Canonical Briefing v2 (scope toggle + Document.file_path index migration)
- Rigby `claude_code_tool` safeguards
- Chris browser visual check on S2984 arcs section
- Systemic auth-XHR treatment
- Live-dispatch smoke on S2982 stage-doc guardrails
- Exercise PLAYBOOK-7.7.4 against sibling repo
- S2980 Theme Signals browser UX smoke
- Phase B Theme Signals — "Why now" LLM summarizer, who-benefits/who-loses, sub-tab persistence
- Rigby Tool Gap Ledger — Fold D from S2982 (`AgentExecution.celery_task_id` uniqueness constraint)
- Playbook v0.9.0 + v0.10.0 front-matter `commit_sha` + `content_hash` PLACEHOLDER fills

---

## Playbook adherence

- ✅ **PLAYBOOK-7.7.1** (spec→ship, 9 phases) — all walked; abort-early clause not triggered.
- ✅ **PLAYBOOK-7.7.2** (SIGN tool_runs mandatory) — 21 total tool_runs across 3 SIGN passes; no rubber-stamps. A2 pass 1 REVISE was substantive (3 real issues caught).
- ✅ **PLAYBOOK-7.7.3** (Chris-facing framing plain English + ≤1 decision) — D2 descope framed with "do we lose anything? / more work later?" mid-flight.
- ✅ **PLAYBOOK-7.4.4** (recycle after merge, `recycle-all` for frontend) — backend-only PR; `make recycle-all` used (diff detection correctly skipped frontend rebuild).
- ✅ **PLAYBOOK-6.10.7** (zoom-out ask per SIGN cycle) — 2 zoom-out prompts on T1 + 2 on A2 (4 total across passes).
- ✅ **PLAYBOOK-6.10.8** (fold classification SIGN discipline) — 6 same-PR + 6 future_triggers classified.
- ✅ **PLAYBOOK-3.2.3** (TransactionTestCase for dispatcher-path tests) — S2987 tests use TransactionTestCase per S2885 Fold 1.

---

**HEAD at close:** `95d3cdc65` (PR #3633 merged; docs cascade PR TBD; recycle-all clean at `sha=95d3cdc6534d`).
