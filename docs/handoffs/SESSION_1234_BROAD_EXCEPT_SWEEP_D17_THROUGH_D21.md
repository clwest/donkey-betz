# Session 1234 (continuation 2) — Broad-except sweep D17 → D21: narrow allowlist + cross-file invariant lock, 5 PRs

**Status:** Same-UTC-day third arc closing Session 1234. Triggered by D16's discovery that broad `except Exception → return []` was hiding `Cannot filter a sliced queryset` TypeError as "no results" in `core.rag_integration.search_embeddings`. Audit revealed the same anti-pattern at 17 additional sites across 4 more files — D17 through D21 narrowed them all under a shared `(DatabaseError, ConnectionError, OSError)` allowlist locked by a 4-way cross-file invariant test.

**Date:** 2026-06-25 (UTC, same day as D1-D16).
**Active conversation:** `pa-0f08fc48ec914917` (continues from morning-brief + docs-corpus arcs; carries forward into Session 1235).
**Companion handoffs:**
- [`SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md`](./SESSION_1234_FIRST_FIRE_FIXES_PLUS_DRIFT_FRAMING.md) — D1-D8 morning-brief arc
- [`SESSION_1234_DOCS_CORPUS_ARC_D9_THROUGH_D16.md`](./SESSION_1234_DOCS_CORPUS_ARC_D9_THROUGH_D16.md) — D9-D16 docs-corpus retrieval arc

## TL;DR

D16 closed at the second handoff revealing the root cause of why semantic_search was returning 0 chunks: a broad `except Exception` was swallowing a `TypeError: Cannot filter a query once a slice has been taken.` and returning `[]` indistinguishable from "no results."

Audit revealed the same anti-pattern at additional sites. D17-D21 narrowed them all:

- **D17 / #2627** — `core/services/scoped_retrieval.py`: 8 sites, single PR
- **D18 / #2628** — `core/services/knowledge_first_router.py`: 6 sites + 2-way invariant
- **D19 / #2629** — `core/services/knowledge_similarity.py`: 1 site + 3-way invariant
- **D20 / #2630** — `core/views_rag_embeddings.py`: 2 of 20 sites (helper-vs-endpoint discriminator) + 4-way invariant
- **D21 / #2631** — `core/rag_integration.search_personal_memories`: full rewrite (was even more broken than search_embeddings — connected to non-existent database) + narrow except matching D17-D20 shape

After D21 every retrieval / personal-memory path uses the narrow allowlist pattern with cross-file shape parity enforced by transitive pairwise tests. Logic errors (TypeError, AttributeError, KeyError) now propagate to tests + production logs instead of being swallowed as "no results."

**Plus a backfill milestone at close:** the `sync_docs_index_to_documents --embed` task that started at session midpoint completed shortly before close. **All 2,732 Documents are now embedded** (36,854 chunks total). Rigby's semantic_search runs against a fully-populated, fully-enriched corpus with zero unembedded docs.

## Session Manifest

### PRs merged (5 total this arc; 22 total across Session 1234)

| # | Title | What |
|---|---|---|
| **#2627** | `fix(session-1234): D17 — scoped_retrieval narrows broad except to env errors only` | 8 sites in core/services/scoped_retrieval.py narrowed to `_RETRIEVAL_ENV_ERRORS = (DatabaseError, ConnectionError, OSError)`. Sites: search() outer, _semantic_search, _keyword_search, _search_by_document_class, get_postmortems, get_incident_docs, get_audit_findings_context, get_scope_stats. 13 new tests. |
| **#2628** | `fix(session-1234): D18 — knowledge_first_router narrows broad except + 2-way invariant lock` | 6 sites narrowed. Same allowlist constant exported separately to allow cross-file consistency checks. New `test_d17_d18_allowlists_have_same_shape` cross-file invariant — discipline lock catches future drift before allowlists diverge. 8 new tests. |
| **#2629** | `fix(session-1234): D19 — knowledge_similarity narrows broad except + 3-way invariant lock` | 1 site (embedding service call). Cross-file invariant extended from 2-way to 3-way: D17 ↔ D18 ↔ D19 pairwise + transitive 3-way frozenset equality. 8 new tests. |
| **#2630** | `fix(session-1234): D20 — views_rag_embeddings selective narrow-except + 4-way invariant lock` | KEY INSIGHT: Not every broad-except is a bug. File has 20 sites; only 2 narrowed (`as _e:` helpers that return None silently). 18 HTTP endpoint handlers (`as e:` returning `Response({'success': False, 'error': str(e)}, status=500)`) stay broad — narrowing them would leak unhandled stack traces to clients (violates API contract). Cross-file invariant extended to 4-way. 10 new tests. |
| **#2631** | `fix(session-1234): D21 — search_personal_memories full rewrite (pivot + narrow except)` | Full rewrite. Pre-D21: connected to non-existent `ai_unified_platform` database, queried non-existent `unified_embeddings` table, broad except → []. Post-D21: Django ORM against `UserEmbedding` model (user-scoped) + `_cosine_similarity_python` helper (JSONField → Python-side cosine; migrate to pgvector VectorField when corpus grows) + strict access control (user_id + is_active=True) + narrow except via new `_PERSONAL_MEMORY_ENV_ERRORS` (same shape as D17-D20). similarity_threshold default 0.7 → 0.4 to match D15. 16 new tests across 4 classes. |

### Docs cascade backfill completed

The `sync_docs_index_to_documents --embed` task that started mid-Session-1234-second-arc completed shortly before this third arc close:

```
Documents: 2732
DocumentEmbeddings: 36854
Documents WITH embeddings: 2732 (100%)
Documents WITHOUT embeddings: 0
```

From 11,809 chunks at session start → 36,854 at close (+25,045 new chunks across 1,820 newly-synced docs + 17 updated). The 12-day-stale + 1820-missing corpus state from session open is fully resolved.

### Discipline locks summary

| Lock | Scope | Where | Effect |
|---|---|---|---|
| 4-way cross-file invariant | D17 + D18 + D19 + D20 `_RETRIEVAL_ENV_ERRORS` tuples must be set-equal | `test_d20_views_rag_embeddings_narrow_except.FourWayCrossFileInvariantTests` | Any future PR that adds a 5th narrow-except file with a different shape fails the test → forces drift to be reviewed explicitly |
| D21 shape parity | `_PERSONAL_MEMORY_ENV_ERRORS` must match D17-D20 retrieval allowlist shape | `test_d21_search_personal_memories.NarrowExceptShapeTests.test_allowlist_matches_d17_d20_shape` | rag_integration's separate constant stays in lockstep with the retrieval-domain files even though it's not part of the 4-way invariant |
| File-level source guards | No bare `except Exception` line in real code in each narrowed file | `test_d{17,18,19,20,21}_*_narrow_except.ExceptionAllowlistShapeTests.test_no_bare_except_exception_remains_in_file` | Catches revert / cleanup-PR drift in each file individually |
| Helper-vs-endpoint discriminator | D20-specific: `except Exception as _e:` (helper) MUST be narrowed; `except Exception as e:` (endpoint) MAY stay broad | `test_d20_views_rag_embeddings_narrow_except.ScopeDiscriminatorTests` | The underscore-alias convention the file already used now has tests enforcing its meaning |

### Behavior changes

| Pre-D17 | Post-D21 |
|---|---|
| `TypeError: Cannot filter a sliced queryset` swallowed → `return []` | TypeError propagates → test failure + production log |
| `AttributeError` on refactored field → `return []` | AttributeError propagates |
| `KeyError` on changed dict schema → `return []` | KeyError propagates |
| `DatabaseError` on connection drop → `return []` (graceful) | DatabaseError still gracefully returns `[]` |
| `ConnectionError` on embedding service down → `return []` (graceful) | ConnectionError still gracefully returns `[]` |
| `OSError` on disk full → `return []` (graceful) | OSError still gracefully returns `[]` |

## Notable findings during the audit

- **6,684 total broad `except Exception` instances across `core/`** (line count) — most are legitimately broad (logging wrappers, async task supervisors, agent-execution catch-alls). The narrow-allowlist pattern applies only to the retrieval / personal-memory subset where the empty-return looks indistinguishable from "no matches."
- **The helper-vs-endpoint discriminator codified in D20** is generalizable: any file where some sites return `None`/`[]` silently AND some sites return explicit JSON error responses needs the same selective approach. The underscore-alias `_e` convention turns out to be a useful marker for the silent-failure-mode sites.
- **D21's full rewrite was bigger than narrow-except** — `search_personal_memories` was structurally broken (wrong database, wrong table, dead credentials). The narrow-except fix was the tip of the iceberg.

## Memory rules referenced (no new ones added this arc)

The two memory rules added at the second-arc close still apply:

- `feedback_docs_pipeline_4_step_cascade.md` — cascade discipline (the backfill that completed here ran via this)
- `feedback_test_real_db_for_queryset_semantics.md` — D16's lesson; D17-D21 are direct applications (the narrow-except sweep was triggered by what that rule predicted)

## Verifier state at close

`verify_doc_claims --only-drift`: **1 medium drift** (pre-existing `BACKEND_INVENTORY.md` services count). Same as the first + second close. Out of scope for this arc.

## Carryover into Session 1235

### Time-bound (unchanged across all three arcs)

- **morning_brief 2nd-fire verification (2026-06-26 13:00 UTC = 07:00 MDT)** — first scheduled fire with D3/D4/D5/D6 live.
- **Operator Edge newsletter Friday-1 dry-run check (2026-06-26 12:00 UTC)**.

### Broad-except sweep follow-ups (NEW — optional, Chris-discretion only)

The 4-way invariant catches drift in the 4 narrowed files. Any "D22" would invent scope:

- Audit additional files in the ~6,600 remaining broad-excepts for retrieval-domain candidates — requires fresh grep + classification.
- Survey non-retrieval domains (orchestration / telemetry / embedding service supervisors) for similar patterns. Different rules apply per domain (D20 showed HTTP endpoints SHOULD broad-catch).
- Generalize the narrow-allowlist pattern as a re-usable decorator if a 6th candidate emerges. Currently the constant is duplicated 4 times — fine while the list is short, would benefit from extraction if it grows.

### Pre-existing carryover (unchanged)

- `BACKEND_INVENTORY.md` services count drift (1 active verifier hit)
- All Session 1232-1233 tail items
- Docs-corpus optional follow-ups from second arc close: narrow `core.rag_integration` broad except outside `search_embeddings`/`search_personal_memories`, `TextProcessor extracted_metadata` clobber, `refresh_docs_corpus` beat task

### Chris-side

- **CI billing** still outstanding. All 22 Session 1234 PRs admin-merged via `--admin`.
- **Anthropic credit refill** at https://console.anthropic.com/billing.

## Recommended Session 1235 plan

1. **Open with `context-kit orient`** — surfaces all 3 Session 1234 handoffs + the 4 new auto-memory rules from today.
2. **Verify morning_brief 06-26 13:00 UTC fire** — close-of-arc proof for D3-D6.
3. **Operator Edge Friday-1 dry-run check** (06-26 12:00 UTC).
4. **Chris reads the 06-26 brief** → Rigby audience-fit verdict → Sub-step D scope.
5. **Optional**: pick one of the deferred follow-ups (BACKEND_INVENTORY drift refresh / TextProcessor clobber / refresh_docs_corpus beat task / new broad-except audit target).

## Net Session 1234 totals (all three arcs combined)

- **22 PRs merged** (#2606-#2631)
- **170+ new tests** across all arcs, all green
- **36 historical leak-victim Deliverables archived**
- **2,729 Documents enriched** with type-aware retrieval metadata (D9/D10)
- **36,854 DocumentEmbedding chunks** — 100% of Document table embedded (backfill complete)
- **8 load-bearing docs structurally reframed** (D8 snapshot framing)
- **17 broad-except sites narrowed** + 1 search_personal_memories rewrite (D17-D21)
- **3 new auto-memory feedback rules**
- **Rigby has type-aware semantic search end-to-end** with logic-error visibility and a populated corpus

## Files touched this arc (D17-D21)

| File | What |
|---|---|
| `core/services/scoped_retrieval.py` | D17 narrow except (8 sites) |
| `core/services/knowledge_first_router.py` | D18 narrow except (6 sites) |
| `core/services/knowledge_similarity.py` | D19 narrow except (1 site) |
| `core/views_rag_embeddings.py` | D20 selective narrow except (2 sites of 20) |
| `core/rag_integration.py` | D21 search_personal_memories full rewrite + helper + new allowlist constant |
| `core/tests/test_d17_scoped_retrieval_narrow_except.py` | D17 contract tests (13) |
| `core/tests/test_d18_knowledge_router_narrow_except.py` | D18 contract + 2-way invariant (8) |
| `core/tests/test_d19_knowledge_similarity_narrow_except.py` | D19 contract + 3-way invariant (8) |
| `core/tests/test_d20_views_rag_embeddings_narrow_except.py` | D20 contract + discriminator + 4-way invariant (10) |
| `core/tests/test_d21_search_personal_memories.py` | D21 cosine helper + pivot + access control (16) |

**55 new tests added across D17-D21**, all green.
