# `competitor_comparison_tool` — Validation Report (S2915)

**Tool:** `competitor_comparison_tool`
**Schema:** `core/services/pa_tool_schemas.py:2234`
**Handler:** `core/services/td_handlers_core.py:2745` (`_handle_competitor_comparison`)
**Register site:** `core/services/tool_dispatcher.py`
**Session:** S2915 (Path B systematic sweep — Slice 3 batch 5 of `td_handlers_core`)
**HEAD at validation:** `7259caf79` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (**3 READ_ONLY actions in-scope this batch; 4 MUTATION + 1 IRREVERSIBLE actions correctly gated** — see §5a). Auto-classifier will report `validated (full)` per S2911/S2912 precedent because all 8 action names appear in `## Covered actions`.
**Rigby SIGN:** S2915 T0 SIGN AGREE-with-edits — batch 5 introduces §5b first-hop dependency proof shape (Q4 verdict); this tool is the widest-surface MUTATION-heavy handler in batch 5 (8 actions, split 3/4/1 across READ/MUTATION/IRREVERSIBLE) and stresses the new shape on a mixed-safety tool.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Structured competitor comparison generation + storage. Uses RAG evidence from ingested documents to produce a side-by-side `<competitor>` vs Donkey Betz analysis with executive summary + comparison table + gap backlog + tools/stack + sources + quality rubric. Persists results in `CompetitorComparison` rows; can spawn `Initiative` rows from gap backlog + export as `Deliverable` markdown.

Distinct from `intelligence_tool` (multi-desk market intel — no comparison generation), from `content_studio_generate` (deliverable generation without RAG evidence chain), and from `workflow_run_tool.source_pack_comparison` (the workflow-level wrapper that auto-collects sources first via web search + spiders — this tool is the comparison-generation step within that workflow).

## Covered actions

**8 total actions. Split 3 READ_ONLY (in scope) / 4 MUTATION (gated) / 1 IRREVERSIBLE (gated).** Class-prefix inline per action; no `###` subsections (S2915 batch 5 flattening — subsection-heading breaks `NEXT_HEADING_RE` extraction at `core/services/pa_tools_gap_map.py:107`, preexisting from S2914 batch 4 `intelligence_tool_validation.md`; deferred parser fix per D6 moratorium).

- `list` — **READ_ONLY, in scope this ship** — verified live via T1a harness at HEAD `7259caf79`. Direct ORM read of `CompetitorComparison` ordered by `-created_at`; returns id/competitor_name/status/quality_score/evidence_count/summary/created_at. Limit clamped at 50 (default 10).
- `status` — **READ_ONLY, in scope this ship** — verified live via T1a harness. Direct ORM read via `CompetitorComparison.objects.get(id=comparison_id)`; returns status + branch-specific fields (summary+executive_summary for complete; error_message+recommended_queries for needs_sources; error_message for failed). Requires `comparison_id`.
- `detail` — **READ_ONLY, in scope this ship** — verified live via T1a harness. Direct ORM read; returns full `CompetitorComparison` row including all JSON fields (executive_summary_json, quality_rubric_json, sources_json, review_json, comparison_table_json, gap_backlog_json, tools_stack_json). Requires `comparison_id`.
- `generate` — **MUTATION, out of scope this ship** — write + async dispatch. Creates `CompetitorComparison.objects.create(...)` then `generate_competitor_comparison_task.delay(...)`. Requires `competitor_name`. Correctly skipped by harness via `skipped_mutation`.
- `regenerate` — **MUTATION, out of scope this ship** — DB update (`c.save(update_fields=['status', 'error_message', 'updated_at'])`) + async re-dispatch. Requires `comparison_id`. Correctly skipped.
- `create_initiative_from_gap` — **MUTATION, out of scope this ship** — DB write: `Initiative.objects.create(...)` from a gap in the comparison's backlog. Requires `comparison_id` + `gap_index`. Duplicate-name guard prevents re-creation of an existing initiative. Correctly skipped.
- `export_markdown` — **MUTATION, out of scope this ship** — conditional DB write via `create_deliverable(...)` when `save=True` (the default at schema level). Otherwise pure read + string synthesis. Requires `comparison_id`. Correctly skipped.
- `delete` — **IRREVERSIBLE, out of scope this ship** — `c.delete()` on `CompetitorComparison` row. **Not soft-delete**; row is removed from the DB. No confirm/dry_run guard at handler layer. Correctly skipped by harness via `skipped_mutation` (harness treats IRREVERSIBLE + MUTATION the same for gating purposes; the IRREVERSIBLE tag is a classification-only signal for post-hoc audit).

## 3. Schema notes

- **Required:** `action` (enum: 8 values at `pa_tool_schemas.py:2247`).
- **Conditional required (handler-enforced):**
  - `competitor_name` for `generate` (return `{error}` at handler line 2752).
  - `comparison_id` for `status` / `detail` / `delete` / `regenerate` / `create_initiative_from_gap` / `export_markdown` (return `{error}` when missing).
  - `gap_index` for `create_initiative_from_gap` (defaults to 0 if omitted; validated against gap list length at handler line 2939).
- **Optional filters:**
  - `source_document_id` (UUID; source doc for RAG evidence in `generate`).
  - `focus_areas` (list[str]; extra RAG search queries in `generate`).
  - `save` (bool; default true; controls Deliverable creation in `export_markdown`).
  - `auto_research` (bool; default true; controls whether the async task auto-discovers sources).
  - `limit` (int; default 10; capped at 50 for `list`).

## 4. Golden-path examples

**"List recent competitor comparisons."**

```
competitor_comparison_tool  action=list  limit=10
```

**"Show me the status of that Kalshi comparison."**

```
competitor_comparison_tool  action=status  comparison_id=<uuid>
```

**"Give me the full detail on the Kalshi comparison."**

```
competitor_comparison_tool  action=detail  comparison_id=<uuid>
```

**"Generate a comparison for Polymarket" — OUT OF SCOPE this batch (MUTATION):**

```
# competitor_comparison_tool  action=generate  competitor_name=Polymarket
# ↑ Creates CompetitorComparison row + dispatches Celery task. Deferred.
```

**"Delete that comparison" — OUT OF SCOPE this batch (IRREVERSIBLE):**

```
# competitor_comparison_tool  action=delete  comparison_id=<uuid>
# ↑ Hard-deletes the row from DB. No dry_run guard. Deferred.
```

## 5. Failure / empty-state / pagination notes

- **`list` with no comparisons:** returns `{action: 'list', count: 0, comparisons: []}`.
- **`status`/`detail`/`delete`/`regenerate`/`create_initiative_from_gap`/`export_markdown` with unknown `comparison_id`:** returns `{error: f'Comparison {comparison_id} not found'}` at appropriate handler line (2792, 2844, 2877, 2899, 2931, 3001).
- **`status`/`detail` missing `comparison_id`:** returns `{error: 'comparison_id is required for <action> action'}`.
- **`create_initiative_from_gap` with incomplete comparison:** returns `{error: f'Comparison must be complete (current: {c.status})'}` at line 2933.
- **`create_initiative_from_gap` with empty gap backlog:** returns `{error: 'No gaps found in this comparison'}` at line 2937.
- **`create_initiative_from_gap` with out-of-range `gap_index`:** returns `{error: f'gap_index {gap_index} out of range (0-{len(gaps)-1})'}` at line 2939.
- **`create_initiative_from_gap` with existing initiative name:** returns `{error: f'Initiative "{name}" already exists', action}` at line 2954-2958 — duplicate-name guard.
- **`export_markdown` with incomplete comparison:** returns `{error: f'Comparison must be complete (current: {c.status})'}` at line 3003.
- **Unknown action:** returns `{error: f'Unknown action: {action}'}` at line 3138.

## 5a. Mutation containment / gateway allowlist

**5 mutation-class actions gated by harness (4 MUTATION + 1 IRREVERSIBLE).** The gated-out subset:

- **Write paths:** `generate` (create + dispatch), `regenerate` (update + dispatch), `create_initiative_from_gap` (create Initiative), `export_markdown` (conditional create Deliverable when `save=True`).
- **Irreversible path:** `delete` (hard row deletion, no soft-delete, no dry_run guard).

**Containment mechanism (audit metadata):** per-action `TOOL_ACTION_METADATA` records classify each action explicitly (see §5b).

**Containment mechanism (runtime):** none at the handler layer. Per S2914 batch 4 post-merge finding (doc-fix PR #3458), `TOOL_ACTION_METADATA` classification is **descriptive audit metadata**, not a runtime enforcement gate. Live PA runtime WILL dispatch all 8 actions including `delete`; the classification only gates the T1a validation harness. Runtime enforcement would require an explicit handler-side guard.

**Deferral rationale:** exercising `generate` / `regenerate` would spawn real Celery tasks that call LLMs + RAG + web search (multi-minute latency + real cost). Exercising `create_initiative_from_gap` would create a real `Initiative` row. Exercising `export_markdown` (default `save=True`) would create a real `Deliverable` row. Exercising `delete` would irreversibly remove a row. First-live-exercise of each deferred to a dedicated MUTATION-exercise session with explicit budget authorization + rollback plan.

**`delete` action IRREVERSIBLE tagging rationale:** the classification distinguishes `delete` from the other mutations because (a) there's no soft-delete substrate — the row is gone, (b) there's no dry_run guard at handler layer, (c) there's no confirm-required guard, (d) referenced-by rows (e.g., an `Initiative` created via `create_initiative_from_gap`) become orphaned (no FK cascade observed in this handler-read; would need a `models_competitor_comparison.py` audit to confirm cascade behavior). **Ledger candidate this batch** — first IRREVERSIBLE-classified action in Slice 3 (Slice 2 batch 4 had `media_tool.delete` per S2908 Ledger candidate; this is the second instance).

## 5b. First-hop dependency proof (NEW at S2915 batch 5)

**Batch 5 introduces this section per Rigby S2915 T0 SIGN Q4 verdict.** Enumerates direct first-hop callees per action with classification + evidence pointer.

Verdict scheme: `read` / `network` / `llm` / `db_write` / `db_delete` / `dispatch` / `opaque`.

### Action: `list`

| Direct dependency | Classification | Evidence (file:line) |
|---|---|---|
| `CompetitorComparison.objects.order_by('-created_at')[:limit]` | read | `td_handlers_core.py:2815-2816` |

**No-hidden-cost verdict:** ✓ single ORM query.

### Action: `status`

| Direct dependency | Classification | Evidence (file:line) |
|---|---|---|
| `CompetitorComparison.objects.get(id=comparison_id)` | read | `td_handlers_core.py:2789-2790` |

**No-hidden-cost verdict:** ✓ single ORM query.

### Action: `detail`

| Direct dependency | Classification | Evidence (file:line) |
|---|---|---|
| `CompetitorComparison.objects.get(id=comparison_id)` | read | `td_handlers_core.py:2841-2842` |

**No-hidden-cost verdict:** ✓ single ORM query. All JSON fields read from the row's own columns; no cross-model reads.

### Action: `generate` (MUTATION)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `CompetitorComparison.objects.create(...)` | db_write | `td_handlers_core.py:2761-2766` | firm — creates row with competitor_name / source_document_id / generated_by / user_id |
| `generate_competitor_comparison_task.delay(...)` | dispatch | `td_handlers_core.py:2768-2774` | opaque — Celery task at `core/tasks.py` not read this batch; **revisit trigger:** post-merge live-exercise of `generate` in a dedicated MUTATION session |

**No-hidden-cost verdict:** ✗ — the Celery task transitively calls RAG + LLM + web search per schema description ("RAG-powered comparison"). Trust downgraded on Celery task pending its own audit. Handler-side scope is bounded to the row-create + dispatch.

### Action: `regenerate` (MUTATION)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `CompetitorComparison.objects.get(id=comparison_id)` | read | `td_handlers_core.py:2897-2898` | firm |
| `c.save(update_fields=['status', 'error_message', 'updated_at'])` | db_write | `td_handlers_core.py:2902-2904` | firm — status reset to `pending` + error_message cleared |
| `generate_competitor_comparison_task.delay(...)` | dispatch | `td_handlers_core.py:2906-2910` | opaque — same as `generate`; **revisit trigger:** MUTATION session |

**No-hidden-cost verdict:** ✗ — same transitive risk as `generate` via the Celery task.

### Action: `create_initiative_from_gap` (MUTATION)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `CompetitorComparison.objects.get(id=comparison_id)` | read | `td_handlers_core.py:2929-2930` | firm |
| `Initiative.objects.filter(name=name).exists()` | read | `td_handlers_core.py:2954` | firm — duplicate-name guard |
| `Initiative.objects.create(...)` | db_write | `td_handlers_core.py:2970-2981` | firm — creates row with 11 fields including `parent_topic=c.competitor_name` |

**No-hidden-cost verdict:** ✓ direct DB writes only. No transitive network/LLM/dispatch. The `Initiative` model may fire post_save signals (not verified this batch); classification remains firm for the handler's direct scope. **Revisit trigger:** if a post_save signal cascade audit shows Initiative-create triggers spider/agent invocation, downgrade to `dispatch`.

### Action: `export_markdown` (MUTATION when `save=True`)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `CompetitorComparison.objects.get(id=comparison_id)` | read | `td_handlers_core.py:2998-2999` | firm |
| String synthesis (executive summary + table + gap backlog + tools/stack + sources + rubric → markdown) | read | `td_handlers_core.py:3006-3091` | firm — pure in-memory string concat |
| `Deliverable.objects.filter(slug=slug).exists()` | read | `td_handlers_core.py:3102` | firm — slug-collision guard |
| `create_deliverable(...)` (conditional on `save=True`) | db_write | `td_handlers_core.py:3106-3126` | opaque — implementation at `core/services/deliverable_factory.py` not read this batch; **revisit trigger:** deliverable-factory validation batch (partial-validated at S2848+) |

**No-hidden-cost verdict:** conditional. When `save=False`: ✓ pure read + string synthesis. When `save=True` (default): ✗ — `create_deliverable` is opaque; trust downgraded pending factory audit.

### Action: `delete` (IRREVERSIBLE)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `CompetitorComparison.objects.get(id=comparison_id)` | read | `td_handlers_core.py:2874-2875` | firm |
| `c.delete()` | db_delete | `td_handlers_core.py:2880` | firm at handler layer; **opaque at cascade layer** — `models_competitor_comparison.py` not read this batch to verify FK cascade behavior on referenced rows (e.g., Initiative rows created via `create_initiative_from_gap` pointing at this comparison); **revisit trigger:** dedicated `delete` action audit + cascade check |

**No-hidden-cost verdict:** ✗ at cascade layer — cannot claim no hidden cost until FK cascade behavior is verified. This is the tightest example the §5b shape targets: an action classified IRREVERSIBLE at handler layer may still surprise via cascade rules defined in a model file not read this batch.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness competitor_comparison_tool` at HEAD `7259caf79`:

| Action | Outcome | Safety class | Notes |
|---|---|---|---|
| `list` | `success` | READ_ONLY | Empty-DB shape verified |
| `status` | `soft_error` | READ_ONLY | Expected — `comparison_id` required |
| `detail` | `soft_error` | READ_ONLY | Expected — `comparison_id` required |
| `generate` | `skipped_mutation` | MUTATION | Write + dispatch gated |
| `regenerate` | `skipped_mutation` | MUTATION | Write + dispatch gated |
| `create_initiative_from_gap` | `skipped_mutation` | MUTATION | Write gated |
| `export_markdown` | `skipped_mutation` | MUTATION | Conditional write gated |
| `delete` | `skipped_mutation` | IRREVERSIBLE | Hard-delete gated |

3 READ_ONLY dispatched (1 success + 2 soft_error on required-arg-missing paths) + 5 mutations skipped via `skipped_mutation`. Zero bridge_unreachable.

### 6.2 Runtime-not-executed — this ship

- **5 mutation-class actions** — correctly skipped by harness per `skipped_mutation` classification. Live exercise deferred per §5a rationale.

---

## Related

- **Adjacent tools:**
  - `intelligence_tool` (Slice 3 batch 4) — multi-desk market intel; no comparison generation.
  - `workflow_run_tool` (Slice 3 batch 5 sibling — deferred to batch 6 async trio) — orchestration wrapper that runs `source_pack_comparison` workflow which auto-collects sources before calling this tool.
  - `content_studio_generate` — deliverable generation without RAG evidence chain.
  - `research_and_create_tool` (batch 5 sibling) — single-shot research + create chain; no persistent comparison substrate.
  - `deliverable_tool` — deliverable read + edit surface; `export_markdown` creates on this tool's side.
- **Substrate context:** batch 5 (row-create trio) closes Slice 3 at 14/22 tools. `competitor_comparison_tool` is the **widest-surface mixed-safety tool in batch 5** (8 actions, 3 READ_ONLY + 4 MUTATION + 1 IRREVERSIBLE). Stresses the new §5b first-hop dependency proof shape on a real mixed-safety handler with cascade concerns on `delete`.
- **Metadata seed:** 8 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship (3 READ_ONLY + 4 MUTATION + 1 IRREVERSIBLE).
- **Session provenance:** Session G1 (`_handle_competitor_comparison` first ratified).
- **Ledger candidates raised this batch:**
  - **Second IRREVERSIBLE-classified PA tool action.** First was `media_tool.delete` (S2908 Ledger candidate). `competitor_comparison_tool.delete` extends the pattern to Slice 3. **Forward-carry:** if a 3rd IRREVERSIBLE action surfaces in batches 6-7 or Slice 4, evaluate a "IRREVERSIBLE actions require dry_run flag" harness-side lint per PLAYBOOK-6.10 Fold candidate evaluation.
  - **§5b callee-status "opaque" pattern first substantial use.** `research_and_create_tool` §5b marked 3 callees opaque; this tool marks 4 opaques (`generate_competitor_comparison_task`, `create_deliverable`, cascade on `delete`, plus `Initiative` post_save signals). Watch whether "opaque" becomes a permanent-parking-lot vs a trigger for scheduled audits.
  - **Model-file cascade audit gap.** `delete` classification firm at handler layer but opaque at cascade layer (FK behavior in `models_competitor_comparison.py` not read this batch). Reveals a systematic gap: handler validation doesn't cover model-file cascade rules. **Forward-carry:** propose a "cascade audit" companion doc pattern for tools with `db_delete` actions at the next Slice close or if the pattern hits a 2nd instance.
  - **§Covered-actions `###` subsection breaks parity extraction — 2nd instance.** `NEXT_HEADING_RE = re.compile(r'\n#+\s+')` at `core/services/pa_tools_gap_map.py:107` matches ANY next heading including `###`, so `### READ_ONLY subset` subsections truncate the action-name harvest. Preexisting in S2914 `intelligence_tool_validation.md` (also flagged `promote_to_sweep` advisory in `summary.json`). This doc flattens the action list per the S2915 batch 5 workaround. **Forward-carry:** propose narrowing the regex to `##` at Slice 3 CLOSE or if a 3rd instance surfaces in batches 6-7.
