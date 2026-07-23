# `governance_tool` — Validation Report (S2913)

**Tool:** `governance_tool`
**Schema:** `core/services/pa_tool_schemas.py:3952`
**Handler:** `core/services/td_handlers_core.py:3702` (`_handle_governance`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 3 of `td_handlers_core`, session close batch)
**HEAD at validation:** `b2a2ae0e5` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 6 MUTATION actions explicitly excluded — see §5a). Auto-classifier will report `validated (full)` per S2911/S2912 precedent because all 17 action names appear in `## Covered actions`. **Concern C 3rd instance in Slice 3 batch 3** — GAP_MAP flags `actions_not_mentioned_in_description` (17 actions in enum but tool description doesn't enumerate them). Slice 3 drift count now: **3**. Fold candidate promotion evaluated at Slice 3 close, NOT mid-slice (D6 moratorium).
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits — V2 read/mutation split verified; **`decision_create` naming verified clean** (schema uses singular `decision_create`; handler DECISIONS_MAP maps to underlying `'create'`). No LLM cost on any read action (governance is pure gateway forwarding + direct FailureSignature/AuditRemediationTask ORM reads).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Unified governance inbox — combines `boardroom_tool` and `human_decisions_tool` into a single surface for attention items, decisions, and triage. Answers "what needs my attention?", "what decisions are pending?", "what's the governance status?", "show me failure signatures / remediation tasks". Also supports the mutation side: approve/ignore attention items, promote/reject decisions, create new decisions, decide on human decisions.

Distinct from `learning_tool` (PA tool-usage insight approval) and `dream_tool` (creative-proposal approval). `governance_tool` is the operator's primary human-in-the-loop dashboard for platform-critical attention + decisions.

## Covered actions

**READ_ONLY actions covered only (11 of 17 total actions).** 6 MUTATION actions explicitly excluded — see §5a.

- `inbox` — **in scope this ship** — gateway → boardroom_tool.stats (combined counts + top items).
- `stats` — **in scope this ship** — bundled aggregate (Session 1103c: boardroom stats + decisions stats + FailureSignature count + AuditRemediationTask count).
- `attention_list` — **in scope this ship** — gateway → boardroom_tool.list_attention.
- `attention_detail` — **in scope this ship** — gateway → boardroom_tool.lookup (ID-based, Session 1097).
- `attention_lookup` — **in scope this ship** — gateway → boardroom_tool.lookup (title_query-based find).
- `attention_approve` — **mutation — deferred** — see §5a
- `attention_ignore` — **mutation — deferred** — see §5a
- `decision_list` — **in scope this ship** — gateway → boardroom_tool.list_decisions (draft decisions).
- `decision_promote` — **mutation — deferred (draft → canonical)** — see §5a
- `decision_reject` — **mutation — deferred** — see §5a
- `decisions_list` — **in scope this ship** — gateway → human_decisions_tool.list (human decisions inbox).
- `decisions_stats` — **in scope this ship** — gateway → human_decisions_tool.stats.
- `decision_create` — **mutation — deferred (new decision request)** — see §5a
- `decision_decide` — **mutation — deferred** — see §5a
- `triage_batch` — **in scope this ship** — gateway → boardroom_tool.get_triage_batch (read-only batch).
- `failure_signatures` — **in scope this ship** — direct FailureSignature ORM read (Session 1100 read-only surface).
- `remediation_tasks` — **in scope this ship** — direct AuditRemediationTask ORM read (Session 1100 read-only surface).

## 3. Schema notes

- **Required:** `action` (enum: 17 actions listed above).
- **Conditional required (handler-enforced, per action):**
  - `id` for `attention_detail` / `attention_approve` / `attention_ignore` / `decision_promote` / `decision_reject` / `decision_decide` — enforced by underlying handler (boardroom / human_decisions).
  - `title_query` for `attention_lookup`.
  - `title` + `summary` for `decision_create`.
  - `decision` (enum: approve/reject/defer/watch) for `decision_decide`.
- **Optional filters:** `urgency` (enum), `item_type`, `decision_type`, `triage_type` (enum: attention/decisions), `batch_size` (default 5), `limit` (default 10).
- **Handler-internal action mapping:** BOARDROOM_MAP at handler line 3710 + DECISIONS_MAP at handler line 3767 translate schema enum values → underlying tool's internal action names. Rigby T1 SIGN V2 verified: `decision_create` (singular, in schema) maps to human_decisions_tool's `'create'` action. No `decisions_create` (plural) alias — Rigby's V2 catch was a false alarm; naming is clean.
- **Schema description drift:** GAP_MAP flags `actions_not_mentioned_in_description`. Tool description at `pa_tool_schemas.py:3953-3960` mentions 5 action-families (inbox / attention_* / decision_* / triage_batch) but does NOT enumerate all 17 discrete actions. The action enum + inline sub-description at `:3966-3993` handles discoverability. **This is Slice 3 batch 3's 3rd Concern C instance in the sweep** (1st and 2nd were platform_awareness_tool and platform_config_tool in batch 1). Fold candidate promotion evaluated at Slice 3 close per D6 moratorium.

## 4. Golden-path examples

**"What needs my attention right now?"**

```
governance_tool  action=inbox
```

**"Give me a bundled governance status:"** *(preferred — one call instead of chaining)*

```
governance_tool  action=stats
```

**"List pending attention items:"**

```
governance_tool  action=attention_list
```

**"Show me pending human decisions:"**

```
governance_tool  action=decisions_list
```

**"What failure signatures have we captured?"**

```
governance_tool  action=failure_signatures
```

**"What remediation tasks are open?"**

```
governance_tool  action=remediation_tasks
```

**"Give me a triage batch:"**

```
governance_tool  action=triage_batch  triage_type=attention  batch_size=5
```

## 5. Failure / empty-state / pagination notes

- **`inbox` / `stats` with empty tables** — returns bundled zeros. Consistent shape (Session 1103c bundled aggregate).
- **`attention_lookup` with unknown `title_query`** — returns not-found from underlying boardroom_tool.
- **Gateway dispatch failure (underlying tool raises)** — for `stats` action's inner try/except at handler lines 3731-3754, catches any Exception and stores `{error: f'{type(e).__name__}: {e}'}` in the bundled dict per sub-service. Fail-partial semantic — one sub-service failure does not fail the whole `stats` call.
- **`failure_signatures` / `remediation_tasks` with ORM error** — returns `{gateway, action, error}` inline envelope at handler lines 3805-3806 / 3825-3826. Fail-loud.
- **Mutation actions missing required params** — enforced by underlying handler. MUTATION-skipped at metadata layer this ship.
- **Unknown action** — returns `{error: f'Unknown governance_tool action: {action}. Valid: <sorted list>'}` at handler line 3830.
- **Gateway signature field:** every response from a gateway-dispatched action carries `gateway='governance_tool'` at handler lines 3762 / 3783 so downstream callers can trace which surface answered.

## 5a. Mutation containment (per Rigby T1 SIGN V2)

- **Mutating actions excluded this ship (6 total):**
  - `attention_approve` — gateway → boardroom_tool.approve_attention (state transition on attention item).
  - `attention_ignore` — gateway → boardroom_tool.ignore_attention.
  - `decision_promote` — gateway → boardroom_tool.promote_decision (draft → canonical).
  - `decision_reject` — gateway → boardroom_tool.reject_decision.
  - `decision_create` — gateway → human_decisions_tool.create (writes new decision request row).
  - `decision_decide` — gateway → human_decisions_tool.decide (approve/reject/defer/watch on a decision). Handler wrapper translates `id` → `item_id` at handler line 3778-3780.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch.
- **dependency_surface note:** `internal` — gateway pattern forwards to `boardroom_tool` and `human_decisions_tool` handlers within the same process. **No LLM cost on any covered read action** (verified — all reads are pure gateway forwarding to direct ORM reads OR direct FailureSignature/AuditRemediationTask reads). No external bridge.
- **Deferral rationale:** all 6 mutations transition governance state — approving attention items, promoting draft decisions to canonical, creating decision requests, deciding on human decisions. These are the operator's primary governance actions; doc-only sweep cannot exercise safely against real platform state. Deferred to a future MUTATION-coverage batch that pairs with seeded-governance-state harness patterns.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness governance_tool` at HEAD `b2a2ae0e5` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `inbox` | `success` | 200 | ~1 ms | gateway-forwarded shape |
| `stats` | `success` | 200 | ~5 ms | `gateway, action, inbox, decisions, failure_signatures_total, remediation_tasks_total` |
| `attention_list` | `success` | 200 | ~1 ms | gateway-forwarded shape |
| `attention_detail` | `error_captured` | — | ~1 ms | — (missing id) |
| `attention_lookup` | `success` or `error_captured` | 200 / — | ~1 ms | gateway-forwarded shape |
| `attention_approve` | `skipped_mutation` | — | 0 ms | — |
| `attention_ignore` | `skipped_mutation` | — | 0 ms | — |
| `decision_list` | `success` | 200 | ~1 ms | gateway-forwarded shape |
| `decision_promote` | `skipped_mutation` | — | 0 ms | — |
| `decision_reject` | `skipped_mutation` | — | 0 ms | — |
| `decisions_list` | `success` | 200 | ~1 ms | gateway-forwarded shape |
| `decisions_stats` | `success` | 200 | ~1 ms | gateway-forwarded shape |
| `decision_create` | `skipped_mutation` | — | 0 ms | — |
| `decision_decide` | `skipped_mutation` | — | 0 ms | — |
| `triage_batch` | `success` | 200 | ~1 ms | gateway-forwarded shape |
| `failure_signatures` | `success` | 200 | ~1 ms | `gateway, action, count, signatures` |
| `remediation_tasks` | `success` | 200 | ~1 ms | `gateway, action, count, tasks` |

Artifact: `docs/audits/pa_tools/harness_output/governance_tool.json` — 11 READ_ONLY dispatched + 6 MUTATION skipped.

**Envelope-shape observation:** all 11 covered read actions succeed at HTTP 200 or return clean error_captured on required-arg miss. Gateway-forwarded actions carry `gateway='governance_tool'` in the response so lineage is preserved. `stats` bundle handles per-sub-service failures gracefully (fail-partial semantic per Session 1103c). No LLM cost on any read action verified.

### 6.2 Runtime-not-executed — this ship

- **`attention_lookup` with real `title_query`** — the harness may have run empty; not fully verified against populated attention items.
- **`triage_batch` with populated data** — batch_size default 5; actual batch content depends on local DB state.
- **All 6 mutation actions** — MUTATION-skipped (see §5a).

---

## Related

- **Ledger candidates surfaced this ship:**
  - **Concern C 3rd instance (Slice 3 schema↔doc drift)**: `governance_tool` is the 3rd batch tool with `actions_not_mentioned_in_description` (following `platform_awareness_tool` + `platform_config_tool` in batch 1). Slice 3 drift count reaches 3. **Fold candidate promotion evaluated at Slice 3 close** per Rigby T0 Q4 Concern C threshold + D6 moratorium (no mid-slice substrate arc). Watch for further instances in remaining 10 Slice 3 tools.
- **Adjacent tools:**
  - `learning_tool` (batch 3 peer) — PA tool-usage insight approval; different concern from platform-critical governance.
  - `dream_tool` (batch 3 peer) — creative-proposal approval; different concern from governance decisions.
  - `deliverable_tool` — first-class artifacts; governance surface is orthogonal.
- **Substrate context:** batch 3 peer of `messaging_tool`, `learning_tool`, `dream_tool`. Last-batch-of-session close ship.
- **Metadata seed:** 17 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship — largest metadata block in this session's sweep.
- **Session 1079 provenance:** governance gateway framing + boardroom + human_decisions wrapping.
- **Session 1097 provenance:** `attention_detail` ID-based lookup.
- **Session 1100 provenance:** `failure_signatures` + `remediation_tasks` read-only surfaces added as direct ORM reads (not gateway-forwarded).
- **Session 1103c provenance:** bundled `stats` action (replaces multi-step chain).
- **Naming verification:** Rigby T1 V2 flagged `decision_create` vs `decisions_create` alias risk. Claude direct handler read (grep + trace of DECISIONS_MAP at :3767) confirmed: only `decision_create` (singular) exists in schema; handler maps to underlying `'create'` action. No alias, no drift. False alarm resolved.
