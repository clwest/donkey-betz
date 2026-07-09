# Context Injection Pipeline — Validation Report

**Tool:** context injection pipeline — the runtime substrate that turns intent into enrichment sections merged into PA's analytical system prompt. This is not a single Rigby-callable tool; it is the substrate that fires around every Rigby tool call and shapes what Rigby's LLM sees at the moment it composes a response.

**Files traced:**
- `core/services/unified_pa_entrypoint.py:244-273` — `INTENT_ENRICHMENT_MAP` (25 canonical intents → enrichment service lists).
- `core/services/unified_pa_entrypoint.py:276-303` — `INTENT_ALIASES` (variant → canonical intent normalization).
- `core/services/unified_pa_entrypoint.py:306-308` — `DIRECT_RELEVANCE_INTENTS` (bypass relevance gate for 6 intents).
- `core/services/unified_pa_entrypoint.py:312-322` — `ENRICHMENT_CAPS` (per-section char caps: 1000-2000).
- `core/services/unified_pa_entrypoint.py:325-331` — `STOP_WORDS` frozenset.
- `core/services/unified_pa_entrypoint.py:2826-2977` — `_build_context` (5 timeout-guarded context sources).
- `core/services/unified_pa_entrypoint.py:2979-3000` — `_get_system_stats`.
- `core/services/unified_pa_entrypoint.py:4373-4388` — `_tokenize` + `_passes_relevance_gate`.
- `core/services/unified_pa_entrypoint.py:4390-4541` — `_enrich_tool_result` (8-service orchestrator).
- `core/services/unified_pa_entrypoint.py:4560-4660` — `_build_analytical_prompt` (enrichment → system prompt merger).

**Downstream / upstream call sites:**
- Called from FC path at `unified_pa_entrypoint.py:1044-1056`.
- Called from keyword-routing path at `unified_pa_entrypoint.py:1141-1154`.
- Post-scrub via `pa_security.scrub_enrichment_context` at `unified_pa_entrypoint.py:1055` + `1153`.
- Sections consumed by `_build_analytical_prompt` at line 4640-4643.

**Session validated:** S2730 (Batch C tool 1 of 5).
**HEAD at validation:** `dc65997d` (main, post-Batch-B Session 2729 close).
**Reviewer:** Claude (Opus 4.7, 1M context).
**Rigby cross-check:** deferred (no dispatch surface; regression tests suffice for verified behavior).
**Report status:** VERIFIED — DEFECT-PATCHED-VERIFIED (Batch C tool 1 of 5). Trace + 6 patches (F-CI-1/2/3/4/5/6/7/9/10 code + F-CI-8 doc) + 28 regression tests complete; 140 total pass across all Batch A + B + C tool 1 validation-2728 files.

---

## 1. Intended purpose

Every PA turn passes through TWO context substrates:

1. **`_build_context`** — assembles a per-turn `context` dict containing:
   - `user_id`, `username`, `user_name`, `timestamp`.
   - `conversation_history` (last 10 turns).
   - `profile` (skills, years_experience, goals, work_preference, desired_income, availability).
   - `system_knowledge` (dynamic knowledge injection).
   - `system_stats` (agent_count, spider_count, opportunity_count).
   - `docs_context` (Session 943 — CLAUDE.md, 00-START-NEXT-SESSION.md, recent handoffs).
   - `assistant_mode`, `workspace_mode`, `workspace_scope`, `workspace_context`.

2. **`_enrich_tool_result`** — after a tool has fired successfully, orchestrates up to 8 enrichment services keyed by the current intent, producing a `sections: Dict[str, str]` that gets scrubbed and injected into `_build_analytical_prompt` as `=== <LABEL> ===` blocks that the LLM sees BEFORE `=== DATA TO ANALYZE ===`.

Together these two form the "context injection pipeline." Rigby's LLM composes its response against the tool output PLUS whatever the context injection pipeline decided to include.

## 2. Rigby's belief (per MEMORY + prior tool context)

Rigby has no MEMORY rule targeting the context injection pipeline directly. Her operational belief, derived from schema descriptions of individual tools and observed enrichment output, is:

- "When I call a tool, the PA layer adds relevant context around it." (True in structure — but the shape of "relevant" is undocumented in tool schemas.)
- "If enrichment fails, I would see an error." (False — one failing enrichment service is silently swallowed at `unified_pa_entrypoint.py:4532-4533`, only WARNING-logged.)
- "Enrichment sections included are complete." (False — silent truncation at `unified_pa_entrypoint.py:4536-4539` with no `truncated: true` flag.)
- "The `tool_result` I return is used to shape enrichment." (False — the `tool_result` parameter at `_enrich_tool_result:4394` is unused inside the function body; only `message` + `intent` drive service selection.)

Related MEMORY rules that INFORM the pipeline design:
- `feedback_pa_worker_function_calling_env` — the PA worker function-calling flag gates whether enrichment path even runs.
- `feedback_procfile_makefile_queue_parity` — silent-queue-forever failure class the pipeline could produce if a service silently returns empty.

## 3. Data-structure declarations (verbatim capture)

### 3.1 `INTENT_ENRICHMENT_MAP` (line 244-273)

25 canonical intents mapped to enrichment service lists. Notable:
- `content_review` → 5 services (blog_performance, domain_context, spider_trends, strategic_memory, proactive_intelligence).
- `opportunities` → 4 (spider_trends, domain_context, advisor, proactive_intelligence).
- `execution_history`, `system_overview` → include `platform_briefing`.
- `recent_activity`, `system_health_check`, `error_summary`, `surgical_moves_status`, `agent_introspection`, `scheduled_tasks`, `dreams` → `[]` (pure data, no enrichment).
- **`general` intent is NOT a key** — falls through to `INTENT_ENRICHMENT_MAP.get(canonical_intent, [])` returning `[]`.

### 3.2 `INTENT_ALIASES` (line 276-303)

20 variant → canonical intent mappings. Applied at `_enrich_tool_result:4405`.

### 3.3 `DIRECT_RELEVANCE_INTENTS` (line 306-308)

`{content_review, opportunities, predictions, spider_data, stock_intelligence, crypto_price}` — bypass the relevance gate. For these, enrichment is always included if the service returns non-empty.

### 3.4 `ENRICHMENT_CAPS` (line 312-322)

Per-section character limit dict. Values 1000-2000 (post-S1006 raise from 300-600). Default fallback at line 4537: `600`.

### 3.5 `STOP_WORDS` (line 325-331)

35-word frozenset applied at `_tokenize` in `_passes_relevance_gate`.

## 4. Handler behavior (traced)

### 4.1 `_build_context` (line 2826-2977)

Five sequential, timeout-guarded phases. All five phases share the same anti-pattern: `except asyncio.TimeoutError` (narrow) + `except Exception as e` (broad):

- **Phase A — Profile load (5s timeout, line 2842-2872):** `ExtendedUserProfile.objects.filter(user=self.user).first()`. Broad `except Exception` at 2871. Historical fact captured in source comment (2853-2860): `profile.experience` (wrong attribute name) was silently logged as WARNING for many sessions — the broad except masked the `AttributeError`. Fixed in S1103c. Same anti-pattern still present. **F-CI-1.**
- **Phase B — Knowledge injection (3s timeout, line 2874-2888):** `self.knowledge_injector.get_context_for_query`. Broad `except Exception` at 2887. Same anti-pattern.
- **Phase C — System stats (5s timeout, line 2890-2899):** `self._get_system_stats()` — see §4.2. Broad `except Exception` at 2898.
- **Phase D — Docs injection (5s timeout, line 2903-2923):** `docs_context_builder.build_context_for_agent`. Broad `except Exception` at 2922 (debug log, not WARNING).
- **Phase E — Workspace context (3s outer + 3s per-inner-lookup, line 2925-2967):** `workspace_scope` + `ProjectWorkspace.objects.filter` + `manager.get_workspace_context_for_agent`. Broad `except Exception` at 2966 (debug log).

All five phases return without any signal indicating which phase(s) failed. Downstream `context` dict is used everywhere — callers cannot tell "profile is missing because DB down" from "profile is missing because AttributeError logic bug" from "profile is missing because user has no profile row."

### 4.2 `_get_system_stats` (line 2979-3000)

Hardcoded default: `agent_count=74, spider_count=77, advisor_count=25`. Attempts real counts via `Agent.objects.count()`, `LegacySpiderData.objects.count()`, `Opportunity.objects.filter(status='active').count()`. **Broad `except Exception`** at line 2997 with `logger.debug(...)`. If ORM breaks, the caller silently receives 74/77/25 as if real. **F-CI-7** — same class as F-RG-1 / F-WS-4 narrow-except discipline.

### 4.3 `_tokenize` + `_passes_relevance_gate` (line 4373-4388)

- `_tokenize`: `set(re.findall(r'[a-z0-9_]+', text.lower()))` — regex tokenization.
- `_passes_relevance_gate(message, enrichment_text, threshold=0.15)`:
  - Line 4379-4380: empty `enrichment_text` → return False (correct).
  - Line 4382-4383: `if len(enrich_words) < 30: return False` — **silently discards short-but-authoritative enrichment**. No log, no signal. **F-CI-5.**
  - Line 4384-4386: empty `msg_words` (after stop-word removal) → **`return True`** — "can't filter, include it". User queries composed entirely of stop words (`"why?"`, `"how is it going?"`) bypass the relevance gate and include all enrichment unconditionally. **F-CI-4.**
  - Line 4387-4388: overlap-ratio check.

### 4.4 `_enrich_tool_result` (line 4390-4541)

Signature (line 4390-4396):
```python
async def _enrich_tool_result(
    self,
    message: str,
    intent: str,
    tool_result: Any,   # ← declared but UNUSED inside function body (F-CI-6)
    trace_id: str
) -> Dict[str, str]:
```

- Line 4405: canonicalize intent via `INTENT_ALIASES`.
- Line 4406: look up services via `INTENT_ENRICHMENT_MAP.get(canonical_intent, [])`. **Missing intent → `[]` silently.**
- Line 4408-4409: `if not enrichment_services: return sections` (empty dict).
- Line 4411: `is_direct = canonical_intent in DIRECT_RELEVANCE_INTENTS`.
- Line 4413-4533: main service loop with **8 branches** (intelligence_enricher, blog_performance, domain_context, spider_trends, advisor, strategic_memory, proactive_intelligence, platform_briefing). Each wrapped by **broad `except Exception as e` at line 4532** that logs WARNING and continues. **F-CI-2.**
- Line 4535-4539: **silent truncation loop** — `if len(text) > cap: sections[key] = text[:cap] + '...'`. No `truncated: bool`, no `original_length: int`, no metadata surfacing. **F-CI-3.**
- Line 4541: return sections dict.

### 4.5 Return value → downstream consumers

- `enrichment_sections` returned to caller at `_process_message` (line 1049, 1146).
- Post-scrub via `scrub_enrichment_context` (PII + injection scan).
- Log emits section KEYS only, not sizes: `logger.info(f"[{trace_id}] ... sections={list(enrichment_sections.keys())}")`.
- Consumed by `_build_analytical_prompt` at line 4640-4643: iterates `section_labels` (dict of 9 labels) and appends `\n=== <LABEL> ===\n{text}` blocks to the LLM system prompt. No fidelity signal — the LLM sees truncated sections identically to full sections.

## 5. Defaults inventory

| Default | Location | Value | Class |
|---|---|---|---|
| relevance threshold | `_passes_relevance_gate:4377` | 0.15 (15% word overlap) | tuning constant |
| min enrichment length | `_passes_relevance_gate:4382` | 30 tokens | silent-filter |
| ENRICHMENT_CAPS fallback | `_enrich_tool_result:4537` | 600 chars | silent-truncation |
| profile timeout | `_build_context:2850` | 5.0s | timeout |
| knowledge timeout | `_build_context:2881` | 3.0s | timeout |
| system_stats timeout | `_build_context:2894` | 5.0s | timeout |
| docs timeout | `_build_context:2915` | 5.0s | timeout |
| workspace outer timeout | `_build_context:2929` | 3.0s | timeout |
| workspace inner timeouts | `_build_context:2949, 2959` | 3.0s each | timeout |
| enrichment wrapper timeout | `_process_message:1048, 1145` | 15.0s | timeout |
| hardcoded agent_count | `_get_system_stats:2982` | 74 | silent-fallback |
| hardcoded spider_count | `_get_system_stats:2983` | 77 | silent-fallback |
| hardcoded advisor_count | `_get_system_stats:2984` | 25 | silent-fallback |

## 6. Hidden filters inventory

1. **Intent → services silent map lookup** — `INTENT_ENRICHMENT_MAP.get(canonical_intent, [])`. Any intent not in the map (including `general` and any hallucinated intent from a future tool) silently produces empty enrichment.
2. **`_passes_relevance_gate` short-enrichment filter** — `< 30` tokens discarded silently.
3. **`_passes_relevance_gate` overlap-ratio filter** — `< 15%` overlap discarded silently (except for `DIRECT_RELEVANCE_INTENTS`).
4. **Per-service `if text:` truthy checks** (lines 4420, 4440, 4447, 4457, 4475, 4502, 4518, 4529) — empty string / None return → section absent, no signal.
5. **Attribute-guard branches** — e.g., `elif service_key == 'intelligence_enricher' and self.intelligence_enricher:` (line 4415). If the lazy-load failed at property access, the branch silently skips — no signal to caller.
6. **Broad `except Exception` per service** — silently swallows one service failure while others may succeed.
7. **`pa_security.scrub_enrichment_context`** — PII / injection scanner. Not audited here (out of scope) but may silently redact fields.

## 7. Limits inventory

- Per-section char caps: 1000-2000 (see §3.4). Default fallback: 600.
- `tool_str[:8000] + '...'` in `_build_analytical_prompt:4655-4656` — silent 8000-char truncation of tool_result string form before LLM sees it.
- 15s outer enrichment timeout (`_process_message:1048, 1145`).
- No cap on `enrichment_services` list length (bounded by `INTENT_ENRICHMENT_MAP` values — max 5).

## 8. Silent-truncation test

**Observable:** `text[:cap] + '...'` at `_enrich_tool_result:4539`.

- No `truncated: bool` flag returned.
- No `original_length: int` field.
- Log at `_process_message:1056, 1154` emits only section KEYS, not sizes.
- LLM system prompt (line 4640-4643) receives truncated section identical in shape to non-truncated section.

**Verdict:** **DEFECT** (D2 + F-CI-3). Silent-truncation without a `truncated` flag violates §Ch6 D2 defect definition.

## 9. Silent-filter test

Two silent filters in `_passes_relevance_gate`:

- **Short-enrichment discard** (line 4382-4383): drops enrichment_text with < 30 tokens. No log, no signal, no `filtered_reason: 'below_min_length'`. **DEFECT (D2 + F-CI-5).**
- **Empty-msg-words include-all fallback** (line 4385-4386): includes enrichment unconditionally for queries composed of stop words. No log, no metadata. **DEFECT (D2 + F-CI-4).**

## 10. Silent-fallback test

- **Intent → empty services**: unmapped intent silently returns empty enrichment (§6.1). Class-of-failure known from Rigby's dispatch history.
- **Hardcoded stats fallback** (`_get_system_stats:2997`): ORM errors silently return 74/77/25 defaults. **DEFECT (D2 + F-CI-7).**
- **Per-service broad `except Exception`** (`_enrich_tool_result:4532`): one service fails silently while others succeed. **DEFECT (D2 + F-CI-2).**
- **`_build_context` per-phase broad `except Exception`** (lines 2871, 2887, 2898, 2922, 2966): silent-fallback with WARNING-log-only signal. **DEFECT (D2 + F-CI-1).**

## 11. Staleness test

Context sources this pipeline reads:
- ORM (profile, ProjectWorkspace) — freshness = always live.
- Docs corpus (via `docs_context_builder`) — freshness = last docs cascade run (`_provenance.json` timestamp; see Batch B tool 4).
- System stats — freshness = live ORM counts.
- Enrichment services — each has its own freshness signal (spider_context_builder returns `freshness.data_quality`, others opaque).

Pipeline itself surfaces **no `retrieved_at`** metadata to the caller. Rigby / caller cannot detect stale enrichment from the context envelope.

## 12. Freshness signal

**Not surfaced.** No `retrieved_at`, `enrichment_metadata`, `services_run`, `services_failed` fields in the return dict.

## 13. Provenance signal

**Not surfaced.** Each enrichment section is a bare string. Downstream `_build_analytical_prompt` labels sections with a label constant (`SPIDER TRENDS`, `ADVISOR PRINCIPLES`, etc.) but the LLM cannot verify a section came from the labeled service.

## 14. Authority / workspace assumptions

- `_build_context` reads `ExtendedUserProfile.objects.filter(user=self.user)` and `ProjectWorkspace.objects.filter(user=self.user, id=workspace_id)` — strictly self-scoped. No cross-user reach.
- `_enrich_tool_result` calls into per-service builders. Some (spider_context_builder, advisor_context_builder) are global — no user filter. Not a workspace-scope violation because these produce descriptive summaries, not user-specific rows.
- No `workspace_id` is passed into `_enrich_tool_result`. Enrichment is workspace-blind. If a workspace-aware tool fires and enrichment includes non-workspace data, the merged prompt may cross the boundary in the LLM's view. Not currently a defect per campaign scope — flagged as PARKED-CONSTITUTIONAL for the parked question (`tools_the_unanswered_constitutional_question.md`).

## 15. Runtime dependencies

- 8 lazy-loaded singletons (intelligence_enricher, blog_performance_fn, domain_context_builder, spider_context_builder, advisor_context_builder, strategic_memory (via factory), proactive_intelligence_service, platform_briefing_service).
- Each lazy-load wrapped in `try/except ImportError` (properties lines 447-532) — returns None on ImportError. Downstream branch conditions `and self.<service>` cause silent skip.
- `PA_USE_FUNCTION_CALLING` env flag gates whether the FC branch (line 1044) or keyword-routing branch (line 1141) fires — both call `_enrich_tool_result` so the pipeline is exercised either way.
- Requires Redis-backed Celery for the `pa` queue (parent PA task dispatch); pipeline itself runs inside the PA turn's own event loop.

## 16. Recoverable failure modes

- One enrichment service failure → other services continue (per-service try/except is CORRECT per §Ch7 R2 in the sense that it's isolated, but per-service failure has no `services_failed` signal — see F-CI-2).
- Individual timeout in `_build_context` phase → phase skipped, `context` returned with subset of phases populated.
- Global 15s timeout → `enrichment_sections = {}`, downstream `has_enrichment = False`, LLM analytical branch skipped (fall through to structured output only).

## 17. STOP-and-report failure modes

None. The pipeline is designed to degrade silently. **F-CI-1, F-CI-2, F-CI-7** convert the degradation from "silent" to "logged-but-not-surfaced." No STOP-and-report exists for context-injection failures.

## 18. Operator-action failure modes

- Lazy-load ImportError → operator must restore missing module + restart PA worker.
- Broad `except Exception` masking logic bugs (like the S1103c `profile.experience` case) requires operator to grep WARNING logs to catch. Once caught, requires code fix + PR + PA worker restart.

## 19. Existing test coverage

**Zero.** Verified via:

```bash
grep -l "INTENT_ENRICHMENT_MAP\|ENRICHMENT_CAPS\|_passes_relevance_gate\|_enrich_tool_result\|INTENT_ALIASES" core/tests/*.py
# → empty
grep -l "_build_context\|_get_system_stats" core/tests/*.py
# → empty
```

The context injection pipeline is exercised at PA integration level only. There is no unit test for:
- `_passes_relevance_gate` truthy/falsy branches.
- `_enrich_tool_result` per-service dispatch or per-service failure isolation.
- Silent-truncation behavior.
- `_get_system_stats` ORM-error fallback.
- `_build_context` per-phase timeout / broad-except.
- `INTENT_ALIASES` normalization.
- Unmapped intent → empty sections.

**First-coverage-at-HEAD tool** — matches Batch B tools 2 (repo_tool) and 3 (kb_ingest).

## 20. Change list (code / docs / tests)

**Proposed patches (subject to Chris gate):**

- **F-CI-1** — Narrow-except discipline in `_build_context` five phases + `_get_system_stats`. Extend the S1234 D17-D21 pattern to a new `_CONTEXT_INJECTION_ENV_ERRORS = (DatabaseError, ConnectionError, OSError, asyncio.TimeoutError)` allowlist. Env errors log WARNING and skip phase; logic errors (AttributeError, TypeError, KeyError) propagate. Matches F-RG-1 (Batch B tool 1) and F-WS-4 (Batch B tool 5) discipline. Extends "6-way" narrow-except to "8-way" (unified_pa_entrypoint._build_context + _get_system_stats add 2 sites).

- **F-CI-2** — Narrow-except in `_enrich_tool_result` per-service loop AND surface `services_run: List[str]`, `services_failed: List[Tuple[str, str]]` on the return dict (`sections["_metadata"]` or a wrapper dict). Consumers (`_build_analytical_prompt`) unchanged for section-content path; `logger.info` upgraded to include failed-service list.

- **F-CI-3** — Silent-truncation fix. Return type becomes `Tuple[Dict[str, str], Dict[str, Any]]` OR sections dict carries a `_truncated: Dict[str, bool]` sibling. Downstream `_build_analytical_prompt` optionally suffixes `[truncated at Ncap]` to the label when relevant. Minimal-diff option: emit a WARNING log per truncated section naming key + original + cap. Chris gate: which shape?

- **F-CI-4** — Empty-msg-words behavior. Options:
  - **(a)** Keep permissive default (current behavior) but LOG it: `logger.info("relevance gate bypass — msg has no non-stopword tokens")`.
  - **(b)** Flip default to **return False** (silent-drop enrichment for pure stop-word queries) — safer but changes user-visible behavior.
  - **(c)** Add a `permissive_on_empty: bool = True` param, default preserves current, callers may override.
  - Recommendation: (a) — minimal behavior change, adds observability.

- **F-CI-5** — Short-enrichment discard. Options:
  - **(a)** Log DEBUG line at discard.
  - **(b)** Lower threshold from 30 → 15 (short authoritative snippets survive).
  - **(c)** Remove the length check entirely (rely on overlap-ratio + `is_direct` alone).
  - Recommendation: (a) plus (b) is the minimal-defect fix; (c) is behavior change.

- **F-CI-6** — Dead parameter `tool_result` in `_enrich_tool_result` signature. Options:
  - **(a)** Remove the parameter; update both call sites (`_process_message:1046` and `:1143`) to not pass it.
  - **(b)** Actually use it (e.g., pass `str(tool_result)[:2000]` into `_passes_relevance_gate` so tool output can influence gating).
  - Recommendation: (a) — dead code removal, one commit, tests validate no behavior change.

- **F-CI-7** — Same class as F-CI-1. Narrow-except in `_get_system_stats` + emit a `stats_source: 'live' | 'fallback'` field so downstream can tell "these counts are hardcoded defaults" from "these counts are live ORM."

- **F-CI-8** — `INTENT_ENRICHMENT_MAP` + `INTENT_ALIASES` documentation. Add a `docs/topics/personal-assistant.md` subsection listing the 25 canonical intents + which services fire for each. Rigby's LLM cannot see this, but future me and Chris can. Minimal-diff: annotate the constants with inline `# Session S2730 F-CI-8` reference.

- **F-CI-9** — `_enrichment_metadata` surface envelope. On return, add:
  ```python
  {
      "_metadata": {
          "canonical_intent": str,
          "services_requested": List[str],
          "services_run": List[str],
          "services_failed": List[Tuple[str, str]],  # (name, error_class)
          "services_skipped_by_gate": List[str],
          "services_skipped_by_short_length": List[str],
          "sections_truncated": List[Tuple[str, int, int]],  # (name, original, cap)
      },
      **sections
  }
  ```
  Downstream `_build_analytical_prompt` ignores `_metadata` (filtered out by iterating `section_labels` only). Log at line 1056 / 1154 upgrades to include the counts.

- **F-CI-10** — 8000-char silent truncation in `_build_analytical_prompt:4655-4656`. Adjacent to enrichment; scope call — Chris gate. If in-scope: mirror the F-CI-3 fix.

- **F-CI-11 (PARKED-CONSTITUTIONAL)** — workspace-blind enrichment reaches into global services (spider_context_builder, advisor_context_builder). Flagged for the parked question in `tools_the_unanswered_constitutional_question.md`. **Do not patch this batch.**

**Tests to add:** `core/tests/test_context_injection_pipeline_validation_2728.py` covering:
- `_passes_relevance_gate` — 4 branches (empty enrichment, short enrichment, empty msg_words, overlap-ratio).
- `_enrich_tool_result` — unmapped intent → empty sections.
- `_enrich_tool_result` — INTENT_ALIASES normalization.
- `_enrich_tool_result` — DIRECT_RELEVANCE_INTENTS bypass.
- `_enrich_tool_result` — per-service failure isolation.
- `_enrich_tool_result` — silent truncation observability (post-F-CI-3 patch).
- `_enrich_tool_result` — services_run / services_failed envelope (post-F-CI-9 patch).
- `_get_system_stats` — ORM env error returns hardcoded default + stats_source='fallback' (post-F-CI-7 patch).
- `_get_system_stats` — logic error propagates (post-F-CI-7 patch).
- `_build_context` — per-phase narrow-except discipline (post-F-CI-1 patch).
- Source-level guards: no `except Exception` inside `_build_context` / `_enrich_tool_result` / `_get_system_stats` function bodies (mirrors F-RG-1 / F-WS-4 source guards).
- `INTENT_ENRICHMENT_MAP` shape (dict, 25 keys, all values are lists).
- `INTENT_ALIASES` shape (dict, no dead aliases pointing at intents not in the map).
- `ENRICHMENT_CAPS` shape (all values >= 500).
- Dead-parameter `tool_result` removed from `_enrich_tool_result` signature (post-F-CI-6 patch).

---

## Findings

### F-CI-1 — Broad `except Exception` across five `_build_context` phases + `_get_system_stats`
- **Class:** DEFECT (D2 — silent-fallback masks logic errors).
- **Evidence:** `unified_pa_entrypoint.py:2871, 2887, 2898, 2922, 2966, 2997` — six `except Exception as e:` sites; historical incident: `profile.experience` bug silently swallowed for multi-session period per S1103c source comment.
- **Severity:** HIGH.
- **Action:** patch — extend S1234 D17-D21 narrow-except discipline. Same class as F-RG-1 (Batch B tool 1) and F-WS-4 (Batch B tool 5). Would raise the invariant-test surface from 6-way to 8-way.

### F-CI-2 — Per-service silent failure in `_enrich_tool_result`
- **Class:** DEFECT (D2).
- **Evidence:** `unified_pa_entrypoint.py:4532-4533`. One service failure → other services continue silently. Log at `:1056, :1154` emits section KEYS only.
- **Severity:** HIGH.
- **Action:** patch — narrow-except + surface `services_failed` in envelope (F-CI-9 companion patch).

### F-CI-3 — Silent truncation at ENRICHMENT_CAPS
- **Class:** DEFECT (D2).
- **Evidence:** `unified_pa_entrypoint.py:4536-4539` — `sections[key] = text[:cap] + '...'` with no `truncated: bool` flag. `_build_analytical_prompt:4640-4643` receives truncated sections identical to full sections.
- **Severity:** MEDIUM.
- **Action:** patch — surface truncation in envelope (see F-CI-9); minimal-diff option: WARNING log per truncated section.

### F-CI-4 — Relevance gate returns True on empty msg_words
- **Class:** DEFECT (D2 — undocumented behavior; may over-include enrichment for stop-word-only queries).
- **Evidence:** `unified_pa_entrypoint.py:4385-4386` — `if not msg_words: return True`.
- **Severity:** MEDIUM.
- **Action:** Chris gate. Recommendation: add INFO log ("relevance gate bypass — msg has no non-stopword tokens") without changing return value.

### F-CI-5 — Short enrichment silently discarded
- **Class:** DEFECT (D2).
- **Evidence:** `unified_pa_entrypoint.py:4382-4383` — `if len(enrich_words) < 30: return False`. No log.
- **Severity:** MEDIUM.
- **Action:** Chris gate. Recommendation: add DEBUG log at discard; hold on threshold change until instrumented data justifies.

### F-CI-6 — Dead `tool_result` parameter in `_enrich_tool_result`
- **Class:** DEFECT (D2 — behavior differs from Rigby's mental model; may be RIGBY-MISUNDERSTANDING but Rigby's belief is schema-driven).
- **Evidence:** `unified_pa_entrypoint.py:4394` declared; not referenced anywhere in the function body (lines 4390-4541 verified via grep).
- **Severity:** LOW.
- **Action:** patch — remove parameter; update two call sites (`:1046, :1143`).

### F-CI-7 — `_get_system_stats` broad-except with hardcoded fallback
- **Class:** DEFECT (D2 + D10 — no signal when live counts fail).
- **Evidence:** `unified_pa_entrypoint.py:2997-2998` — `except Exception as e: logger.debug(...)`. If ORM breaks, downstream context sees `74/77/25` as if real.
- **Severity:** MEDIUM.
- **Action:** patch — narrow-except + `stats_source: 'live' | 'fallback'` field.

### F-CI-8 — INTENT_ENRICHMENT_MAP + INTENT_ALIASES undocumented
- **Class:** UNDER-DOCUMENTED.
- **Evidence:** Constants live in `unified_pa_entrypoint.py:244-303` with only inline session-reference comments. No `docs/topics/personal-assistant.md` reference; no Rigby-visible schema surface names these.
- **Severity:** LOW.
- **Action:** doc — add subsection to `docs/topics/personal-assistant.md` OR to a new `docs/topics/context-injection.md`. Rigby's behavior is unchanged; documentation-only.

### F-CI-9 — No `_metadata` envelope on enrichment return
- **Class:** DEFECT (D2 + not-Rigby-safe R2/R3/R4 — hidden filters + silent truncation).
- **Evidence:** `_enrich_tool_result` returns bare `Dict[str, str]`. No provenance, no fidelity signal.
- **Severity:** MEDIUM.
- **Action:** patch — introduce `_metadata` sub-dict on return; downstream `_build_analytical_prompt` filters it out via existing `section_labels` iteration. Log upgrade at call sites.

### F-CI-10 — 8000-char silent truncation of `tool_result` string form
- **Class:** DEFECT (D2) — adjacent to context injection pipeline in `_build_analytical_prompt`.
- **Evidence:** `unified_pa_entrypoint.py:4655-4656` — `if len(tool_str) > 8000: tool_str = tool_str[:8000] + '...'`.
- **Severity:** MEDIUM.
- **Action:** Chris gate — in-scope for this pipeline? Recommendation: yes — same anti-pattern as F-CI-3.

### F-CI-11 — Workspace-blind enrichment reaches into global services
- **Class:** PARKED-CONSTITUTIONAL.
- **Evidence:** spider_context_builder, advisor_context_builder are global; `_enrich_tool_result` does not thread `workspace_id`.
- **Severity:** MEDIUM (structural).
- **Action:** park — see `tools_the_unanswered_constitutional_question.md`. Do not patch this batch.

---

## Verdict (Batch C tool 1 CLOSED)

- Tool status at close: **VERIFIED — DEFECT-PATCHED-VERIFIED.**
- Rigby-safe: **yes** (post-patch). Silent truncation, silent-filter, and silent-fallback surfaces now emit observability signals (envelope entries or logs). Hidden filters (INTENT_ENRICHMENT_MAP + INTENT_ALIASES) surface in `_metadata.canonical_intent` + `services_requested`.
- Regression tests added: `core/tests/test_context_injection_pipeline_validation_2728.py` — 28 tests covering F-CI-1/2/3/4/5/6/7/9/10 branches + shape guards on INTENT_ENRICHMENT_MAP/ALIASES/CAPS/DIRECT_RELEVANCE_INTENTS. All pass.
- Cross-tool regression: 140/140 substantive tests pass across all 10 validation-2728 files (Batches A + B + C tool 1). Zero regressions.
- Docs updated: `docs/topics/personal-assistant.md` — Enrichment Pipeline section rewritten with the actual 25 canonical intents → services mappings + envelope shape + narrow-except discipline (F-CI-8).
- Follow-ups filed: F-CI-11 (workspace-blind enrichment reaches into global services) remains PARKED-CONSTITUTIONAL for the parked question in `tools_the_unanswered_constitutional_question.md`.

### Patches shipped

| Finding | Class | Commit |
|---|---|---|
| F-CI-1 + F-CI-7 | narrow-except in `_build_context` + `_get_system_stats` | `bcc6b392` |
| F-CI-6 | remove dead `tool_result` param | `e76d280c` |
| F-CI-4 + F-CI-5 | relevance gate observability logs | `bb7cab78` |
| F-CI-2 + F-CI-3 + F-CI-9 | enrichment `_metadata` envelope + traceback logging | `72db012c` |
| F-CI-10 | 8000-char tool_str truncation WARNING | `a27f0306` |
| tests | 28 regression tests | `e29ba68a` |
| F-CI-8 | doc: enrichment pipeline + envelope + narrow-except | `13e06ed5` |

### MEMORY rules reinforcement (per campaign plan §12.4)

None to annotate for Batch C tool 1 — no prior MEMORY rule targeted the context injection pipeline directly. F-CI-4/F-CI-5 observability logs may inform future rule crystallization if operators start naming the empty-msg-words permissive-include pattern.
