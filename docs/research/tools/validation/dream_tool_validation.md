# `dream_tool` — Validation Report (S2913)

**Tool:** `dream_tool`
**Schema:** `core/services/pa_tool_schemas.py:28`
**Handler:** `core/services/td_handlers_core.py:282` (`_handle_dream`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 3 of `td_handlers_core`)
**HEAD at validation:** `b2a2ae0e5` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (READ_ONLY subset validated; 3 MUTATION actions `approve` + `dismiss` + `create` explicitly excluded — see §5a). Auto-classifier will report `validated (full)` per S2911/S2912 precedent because all 6 action names appear in `## Covered actions`.
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits — V2 read/mutation split verified; **`approve` has async side effect via post_save signal → `execute_single_dream.delay()`** (Celery cascade). Metadata note captures the async downstream.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Browse and act on agent dreams: view top-scored dreams, view details, approve or dismiss dreams, or manually add a new dream/idea. Answers "what dreams do we have?", "show me dream X's details", "approve/dismiss dream Y", "add a new dream". Dreams are creative proposals emitted by agents — `AgentDream` rows with composite scoring across creativity/actionability/relevance/vividness axes.

Distinct from `initiative_tool` / `work_tool` (which manage first-class Initiative rows) — dreams are the pre-Initiative substrate. Approving a dream via `dream_tool.approve` fires a `post_save` signal that promotes it to a real Initiative + dispatches `execute_single_dream.delay()` Celery task for downstream agent execution.

## Covered actions

**READ_ONLY actions covered only (3 of 6 total actions).** 3 MUTATION actions (`approve` + `dismiss` + `create` — excluded — see §5a) are out of scope for this ship.

- `list_top` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{action, dreams, count}` — top-N dreams filtered `composite_score >= 0.5`, `select_related('agent')`, ordered by `composite_score desc, dreamed_at desc`.
- `details` — **in scope this ship** — verified live via T1a harness (`error_captured` on missing `id`; success path via handler trace). Returns full dream detail including all scoring axes + decision outcome + user reaction + linked initiative_id.
- `approve` — **mutation — deferred (fires post_save signal → Celery cascade)** — see §5a
- `dismiss` — **mutation — deferred to future MUTATION-coverage batch** — see §5a
- `create` — **mutation — deferred (writes new AgentDream row)** — see §5a
- `stats` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms). Returns `{action, total_dreams, by_outcome, shown_to_user, with_initiative, avg_scores}` — aggregates + averages across composite/creativity/actionability/relevance scores.

## 3. Schema notes

- **Required:** `action` (enum: `list_top, details, approve, dismiss, stats, create`).
- **Conditional required (handler-enforced, per action):**
  - `id` for `details` — raises `ValueError('id is required for dream details')` at handler line 321.
  - `id` for `approve` — raises `ValueError('id is required to approve a dream')` at handler line 350.
  - `id` for `dismiss` — raises `ValueError('id is required to dismiss a dream')` at handler line 367.
  - `title` for `create` (non-empty after strip) — raises `ValueError` at handler line 385.
- **Optional (`create`):** `content` (defaults to `title` if empty), `dream_type` (default `'creative_idea'` per schema, `'user_request'` per handler).
- **Optional (`approve` / `dismiss`):** `feedback` (defaults to `'Approved via PA'` / `'Dismissed via PA'`).
- **Optional (`list_top`):** `limit` (default 10).
- **NOTE:** dream_tool uses `raise ValueError` on missing-arg paths (not inline `{error}` envelope like most Slice 3 tools). This is the "clean fail-loud → TOOL_EXCEPTION" pattern preferred by S2910 `brainstorm_tool` baseline.

## 4. Golden-path examples

**"Show me the top dreams:"**

```
dream_tool  action=list_top
```

**"Give me stats on all dreams:"**

```
dream_tool  action=stats
```

**"Details of dream X:"**

```
dream_tool  action=details  id=<uuid>
```

**"Approve dream X:"** *(NOT exercised this ship — see §5a)*

```
dream_tool  action=approve  id=<uuid>  feedback=<optional>
```

**"Dismiss dream X:"** *(NOT exercised this ship — see §5a)*

```
dream_tool  action=dismiss  id=<uuid>
```

**"Add a new dream manually:"** *(NOT exercised this ship — see §5a)*

```
dream_tool  action=create  title=<title>  content=<content>  dream_type=<type>
```

## 5. Failure / empty-state / pagination notes

- **`list_top` with no dreams above 0.5 threshold** — returns `{action: list_top, dreams: [], count: 0}`. Consistent shape.
- **`details` missing `id`** — raises `ValueError` → dispatcher wraps as `TOOL_EXCEPTION` at HTTP 500. Clean fail-loud (same shape as `brainstorm_tool` baseline).
- **`details` for unknown UUID** — raises `AgentDream.DoesNotExist` → dispatcher wraps as `TOOL_EXCEPTION`. Fail-loud.
- **`approve` / `dismiss` missing `id`** — raises `ValueError` → `TOOL_EXCEPTION`. MUTATION-skipped at metadata layer this ship.
- **`create` missing `title`** — raises `ValueError("'title' is required for create action")`. MUTATION-skipped this ship.
- **`create` when no active agent exists** — raises `ValueError("No active agent found to attribute dream to")` at handler line 393. Rare edge case; MUTATION-skipped this ship.
- **`stats` with empty AgentDream table** — returns `{total_dreams: 0, by_outcome: {}, shown_to_user: 0, with_initiative: 0, avg_scores: {avg_*: 0, ...}}`. Consistent shape.
- **Unknown action** — raises `ValueError(f"Unknown dream action: {action}")` at handler line 440.

## 5a. Mutation containment (per Rigby T1 SIGN V2)

- **Mutating actions excluded this ship:**
  - `approve` — writes `AgentDream.decision_outcome='approved'` + `user_reaction='loved'` + `user_feedback` via `.save(update_fields=['decision_outcome', 'user_reaction', 'user_feedback'])` at handler line 355. **CRITICAL SIDE EFFECT:** fires `post_save` signal which triggers `promote_to_initiative()` + `execute_single_dream.delay()` (async Celery dispatch). This is a chained MUTATION cascade — approving a dream promotes it to a first-class Initiative AND kicks off downstream agent execution. Classified `MUTATION` (not IRREVERSIBLE because the dream row itself can be re-classified; but the Initiative promotion and Celery dispatch are hard to unwind).
  - `dismiss` — writes `AgentDream.decision_outcome='rejected'` + `user_reaction='dismissed'` + `user_feedback` via `.save(update_fields=[...])` at handler line 372. No signal cascade (unlike `approve`). Classified `MUTATION`.
  - `create` — writes a new `AgentDream` row via `.objects.create` at handler line 395. Attributes to a PA agent (resolved via `Agent.filter(name__icontains='personal assistant').first()` with active-agent fallback at handler lines 388-391). Classified `MUTATION`. Notable: `dream_type` handler default is `'user_request'` while schema default (per description) is `'creative_idea'` — schema-vs-handler default drift; not blocking.
- **Containment mechanism:** per-action `TOOL_ACTION_METADATA` records with `safety_class='MUTATION'` at `tool_action_metadata.py`; harness `resolve_safety()` skips at dispatch.
- **dependency_surface note:** `internal + async Celery` — Django ORM against `AgentDream` + post_save signal → `promote_to_initiative` (creates Initiative row) + `execute_single_dream.delay` (Celery long_running queue dispatch of downstream agent). No external bridge; no LLM cost on the tool itself but the Celery cascade dispatches agents that may incur LLM cost.
- **Deferral rationale:** `approve` has the widest blast radius via post_save signal cascade — approving a test dream would create a real Initiative + dispatch real agent execution. Doc-only sweep cannot exercise safely. Deferred to a future MUTATION-coverage batch that pairs with signal-suppression + Celery-dry-run harness patterns (peer to `dream.approve` async cascade + `universal_agent_tool` LLM cost + `conversation_tool.summary` async).

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness dream_tool` at HEAD `b2a2ae0e5` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list_top` | `success` | 200 | ~1 ms | `action, dreams, count` |
| `details` | `error_captured` | 500 | ~1 ms | — (`ValueError` on missing id) |
| `approve` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `dismiss` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |
| `stats` | `success` | 200 | ~1 ms | `action, total_dreams, by_outcome, shown_to_user, with_initiative, avg_scores` |
| `create` | `skipped_mutation` | — | 0 ms | — (metadata-driven skip) |

Artifact: `docs/audits/pa_tools/harness_output/dream_tool.json` — 3 READ_ONLY (2 success + 1 error_captured clean-raise) + 3 MUTATION skipped.

**Envelope-shape observation:** all read actions return clean success at HTTP 200 or clean `ValueError → TOOL_EXCEPTION` fail-loud on missing-arg paths. **This is the S2910 `brainstorm_tool` baseline shape**, NOT the inline `{error}` envelope drift seen in other Slice 3 tools. Positive observation — dream_tool uses the preferred fail-loud pattern.

### 6.2 Runtime-not-executed — this ship

- **`list_top` with populated dream data** — the harness ran against whatever's in the local DB; real dream shape (scoring axes + agent attribution) may or may not have been exercised.
- **`details` with a real dream UUID** — the harness ran the missing-id error path; success path not exercised.
- **All 3 write actions (`approve` / `dismiss` / `create`)** — MUTATION-skipped (see §5a). Real dream state transitions + signal cascades + Celery dispatches not exercised.

---

## Related

- **Adjacent tools:**
  - `initiative_tool` / `work_tool` — first-class Initiative management; `dream_tool.approve` PROMOTES to Initiative via post_save signal.
  - `brainstorm_tool` (Slice 2) — multi-agent creative discussions; different concern from single-agent dream ideation.
  - `learning_tool` (batch 3 peer) — PA tool-usage insights; different creative substrate.
- **Substrate context:** batch 3 peer of `messaging_tool`, `learning_tool`, `governance_tool`. All 4 tools no-network on selected READ_ONLY action.
- **Metadata seed:** 6 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship.
- **Async cascade note:** `approve` fires `promote_to_initiative()` + `execute_single_dream.delay()` via post_save signal — this is a chained MUTATION+MUTATION+ASYNC cascade unique to this tool's approve path. Similar cascade class: `conversation_tool.summary` (async LLM summarization), `universal_agent_tool` (async agent execution — S2912). Consider a substrate-level "post_save signal cascade" annotation on the sweep-arc close, but do NOT open substrate arc (D6 moratorium).
- **Fail-loud pattern:** `dream_tool` uses `raise ValueError` on all missing-arg / not-found paths (S2910 `brainstorm_tool` baseline). Positive envelope observation — no inline `{error}` drift.
- **`dream_type` default drift:** schema description says default `'creative_idea'`; handler at :383 defaults to `'user_request'`. Minor drift; not blocking. Forward-carry observation.
