# `research_and_create_tool` — Validation Report (S2915)

**Tool:** `research_and_create_tool`
**Schema:** `core/services/pa_tool_schemas.py:537`
**Handler:** `core/services/td_handlers_core.py:444` (`_handle_research_and_create`)
**Register site:** `core/services/tool_dispatcher.py:486`
**Session:** S2915 (Path B systematic sweep — Slice 3 batch 5 of `td_handlers_core`)
**HEAD at validation:** `7259caf79` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_partial` (actionless MUTATION-classed handler; write path documented + gated by harness; §5b first-hop dependency proof grounds the classification).
**Rigby SIGN:** S2915 T0 SIGN AGREE-with-edits — batch 5 introduces the §5b **first-hop dependency proof** shape (Q4 verdict) precisely because `research_and_create_tool` is a three-hop chain (web search → LLM → deliverable write) that no prior sweep batch has covered.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Chain PA tool: given a research topic, runs a web search, sends the results + user request to an LLM, generates markdown content, and saves as a Deliverable. Single-shot "research + create" — the user says "research X and make me a Y" and the tool returns a deliverable link.

Distinct from `web_search` (network probe only — no content generation), from `intelligence_tool.search` (multi-source search with no content generation), from `content_studio_generate` (deliverable generation without research), and from `research_agent` (long-running deep-research agent orchestration; this tool is a single synchronous chain).

## Covered actions

**Actionless handler.** No `action` param — the tool exposes one execution path. Documented-and-gated as MUTATION per §5b.

- `<default>` (the sole execution path) — **out of scope this ship — MUTATION correctly gated by harness** — see §5a + §5b. Runs `WebSearchTool.execute()` → `LLMProviderRegistry.complete()` → `create_deliverable()`. Not exercised live per D6 moratorium on new mutation-class execution during READ_ONLY sweep. Harness reports `skipped_mutation`.

## 3. Schema notes

- **Required:** `query` + `research_topic` (schema `required: ["query", "research_topic"]` at `pa_tool_schemas.py:551`).
- **Optional:** `output_type` (str; default `content`; handler-side type map at lines 555-567 translates to deliverable_type), `output_type_label` (str; default `Content`).
- **No `action` enum** — the schema exposes no `action` field. Handler treats the tool as single-purpose.
- **Handler-side LLM config:** `provider='openai'`, `model_id='gpt-4.1-mini'`, `max_tokens=4000`, `temperature=0.7` (hardcoded at line 521-528; not exposed via schema).
- **Handler-side deliverable metadata:** category `PA Research & Create`, tags `['pa-created', 'research-and-create', output_type]`, format `markdown`, quality_score + confidence_score fixed at `0.7`.

## 4. Golden-path examples

**"Research Serverless AI hosting and create a blog post."**

```
research_and_create_tool  query="Research serverless AI hosting and write a blog post"  research_topic="serverless AI hosting"  output_type=blog  output_type_label="Blog Post"
```

**"Research Kalshi and create a competitor comparison."**

```
research_and_create_tool  query="Research Kalshi and make me a competitor comparison"  research_topic="Kalshi prediction markets"  output_type=comparison  output_type_label="Comparison Analysis"
```

(Both **hypothetical only this batch** — MUTATION gated by harness; not exercised live.)

## 5. Failure / empty-state / pagination notes

- **Web search returns no results:** handler synthesizes `research_text = "(No search results found. Generate content based on general knowledge.)"` at line 492 and proceeds to LLM step — does NOT fail.
- **LLM call raises exception:** caught at handler line 531-533; logs error under `trace_id`; `generated_content = ''`.
- **LLM returns empty content:** handler returns `{success: False, error: 'Content generation failed. Research results were gathered but LLM could not generate the content.', search_results: [...]}` at line 535-540.
- **`create_deliverable` raises `DeliverableGatedError`:** caught at line 614-619 (quality-gate rejection); `deliverable_id = None`; success envelope still returns generated content — the caller can see the content even if it didn't persist as a Deliverable row.
- **`create_deliverable` raises any other exception:** caught at line 620-622; logs error; `deliverable_id = None`.
- **Success envelope:** `{success: True, content, title, output_type, output_type_label, deliverable_id, search_results_count, search_results: [top 3]}`.

## 5a. Mutation containment / gateway allowlist

**This tool is entirely a mutation surface.** No `action` allowlist; the single execution path performs three side-effecting hops:

1. **Network I/O** — `WebSearchTool.execute()` reaches external search provider.
2. **LLM network + cost** — `LLMProviderRegistry.complete()` reaches OpenAI `gpt-4.1-mini` with 4000-token cap.
3. **DB write** — `create_deliverable()` inserts a `Deliverable` row (gated by quality-check; raises `DeliverableGatedError` on gate-rejection when `raise_on_gated=True`).

**Containment mechanism (audit metadata):** classified `MUTATION` via `TOOL_DEFAULTS['research_and_create_tool']` (uniform tool-level default; every dispatch of this actionless tool inherits MUTATION). Precedent: `legal_doc_drafter_agent` (S2910 batch 5) — first actionless-MUTATION `TOOL_DEFAULTS` entry; this is the second. T1a harness respects the classification via `skipped_mutation`.

**Containment mechanism (runtime):** none at the handler layer. Per S2914 batch 4 post-merge finding (`intelligence_tool.search` doc-fix PR #3458), `TOOL_ACTION_METADATA` classification is **descriptive audit metadata**, not a runtime enforcement gate. Live PA runtime WILL dispatch this tool and execute all three hops; the classification only gates the T1a validation harness. Runtime enforcement would require an explicit handler-side guard or global tool-router policy — deferred per D6 moratorium.

**Deferral rationale:** exercising the tool live would burn a real OpenAI call + create a real Deliverable row (both bill/persist). Not appropriate during a sweep-only session. First-live-exercise deferred to a dedicated "MUTATION exercise" session with explicit budget authorization.

## 5b. First-hop dependency proof (NEW at S2915 batch 5)

**Batch 5 introduces this section per Rigby S2915 T0 SIGN Q4 verdict** — explicit-action-allowlist / actionless-MUTATION-classification doesn't prove the callees have no *additional* hidden cost via their own transitive dependencies. This section enumerates the direct first-hop callees of `_handle_research_and_create` with classification + evidence pointer.

Verdict scheme (see `task_breakdown_tool_validation.md` §5b for legend): `read` / `network` / `llm` / `db_write` / `db_delete` / `dispatch` / `opaque`.

### Path: `<default>` (single execution path)

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `WebSearchTool().execute(query, max_results=8, search_type='text')` | network | `td_handlers_core.py:473-474` | opaque — implementation at `core/tools/web_search.py` not read this batch; **revisit trigger:** network-trio batch (batch 6) or dedicated web-search audit |
| `LLMProviderRegistry.complete(provider='openai', model_id='gpt-4.1-mini', ...)` | llm | `td_handlers_core.py:519-529` | opaque — implementation at `core/services/llm_provider_registry.py` not read this batch; classification firm (LLM call to OpenAI); cost = up to 4000 output tokens per invocation; **revisit trigger:** LLM-cost audit session or provider-registry validation batch |
| `create_deliverable(..., raise_on_gated=True)` | db_write | `td_handlers_core.py:590-611` | opaque — implementation at `core/services/deliverable_factory.py` not read this batch; classification firm (creates `Deliverable` row); may raise `DeliverableGatedError` when quality gate rejects; **revisit trigger:** deliverable-factory validation batch (already partial-validated at S2848+ via `deliverable_tool_validation.md`) |
| `UnifiedPAEntrypoint._get_platform_identity()` | read | `td_handlers_core.py:496-497` | opaque — reads platform identity constants for system prompt; classification firm (in-memory read, no I/O) |

**No-hidden-cost verdict:** ✗ — cannot claim no hidden cost. Three callees have declared side effects (network + LLM + DB write) matching the MUTATION classification. Trust downgraded on all three implementations pending their own audits. **This is the intended §5b outcome for MUTATION tools:** the section makes the transitive cost surface explicit rather than hidden.

**No-additional-hidden-cost check:** the three declared callees fully account for the handler's declared behavior. No fourth network / LLM / write path lurks inside the handler body (verified via re-read of `td_handlers_core.py:444-633`). The `slugify` + `uuid.uuid4()` + `django.contrib.auth.get_user_model` + `Token.objects.filter` calls at lines 551-576 are pure in-memory / stateless-ORM-read helpers with no side effects.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness research_and_create_tool` at HEAD `7259caf79`:

Harness output: `actions: []` + `schema_action_count: 0`. The tool is actionless (no `action` enum in schema); the harness has no per-action dispatch loop to run. `TOOL_DEFAULTS['research_and_create_tool']` classifies any dispatch as MUTATION, so the harness would gate a hypothetical dispatch — but the "0 READ_ONLY dispatched" line in summary.json is the expected shape for an actionless-MUTATION tool. Classification is a registry/audit signal here, not a dispatch skip counter.

Artifact: `docs/audits/pa_tools/harness_output/research_and_create_tool.json`.

### 6.2 Runtime-not-executed — this ship

- **Single execution path (implicit)** — MUTATION classification applied at tool level; live exercise deferred per §5a rationale. All three first-hop deps documented in §5b remain unexercised.

---

## Related

- **Adjacent tools:**
  - `web_search` (Slice 2 batch 2) — network probe only, no LLM, no persistence.
  - `intelligence_tool.search` (Slice 3 batch 4) — multi-source search gateway, no content generation.
  - `content_studio_generate` — deliverable generation without research chain.
  - `research_agent` — long-running deep-research agent orchestration (multi-step, this tool is a single synchronous chain).
  - `deliverable_tool` — deliverable read + edit surface; this tool is the create side.
- **Substrate context:** batch 5 (row-create trio) closes Slice 3 at 14/22 tools. `research_and_create_tool` is the **highest-risk tool in batch 5** — three side-effecting hops in one execution path. Motivates the §5b first-hop dependency proof shape introduced this batch.
- **Metadata seed:** 1 `TOOL_DEFAULTS['research_and_create_tool']` entry at `core/services/tool_action_metadata.py` this ship — actionless-uniform MUTATION classification. Second actionless-MUTATION default in the registry after `legal_doc_drafter_agent` (S2910 batch 5). No per-action records needed because the tool exposes no action enum.
- **Session provenance:** Session 1034 (`_handle_research_and_create` first ratified) + Session 1065 (user resolution — `resolved_user` from `user_id` at handler line 570-578) + Session 1169 Layer C Phase 1 (`DeliverableGatedError` opt-in for gate-rejection visibility at line 580-589 + 614-619).
- **Ledger candidates raised this batch:**
  - **Second actionless-MUTATION `TOOL_DEFAULTS` entry.** First was `legal_doc_drafter_agent` (S2910 batch 5); this is the second. Forward-carry: if a 3rd surfaces, evaluate whether a shared "actionless side-effecting chain" pattern warrants naming (multi-hop network+LLM+write in a single tool exposed as one dispatch).
  - **Opaque callee trust-downgrade pattern.** §5b marks 3 callees "opaque, revisit trigger recorded" — first batch to use this specific escape valve. Watch whether the revisit-trigger discipline holds across batches 6+7 (network / async trios) or if opaque-forever creep sets in.
