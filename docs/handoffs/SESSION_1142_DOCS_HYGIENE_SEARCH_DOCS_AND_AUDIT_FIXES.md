# Session 1142 — Docs Hygiene + `search_docs` PA Tool + 2 Stale-Audit Fixes

**Date:** 2026-05-24
**Branch state at close:** Three feature branches open (PRs #2178, #2180, #2181), all gated on Chris review/merge. `main` untouched by this session.

---

## TL;DR

Chris opened the session asking whether `docs/PLATFORM_WHAT_IT_IS.md` was a good starting point for re-reading the corpus after a long absence. That triggered:

1. A **docs-hygiene pass** (3 numeric drifts closed, 4 stale `Last Updated` headers refreshed, meta-stale "tonight's audit found" section rewritten, plus a new `check_doc_headers` management command).
2. Discovery that **Rigby had almost no embedded knowledge of `/docs/`**: `Document` table was empty (0 rows, `kb_tool` returned nothing), `.rag/corpus.jsonl` was 17 days stale, and no PA tool wrapped chunked doc retrieval. Closed both gaps: synced 852 active docs to `Document` + embedded all chunks; rebuilt `.rag/corpus.jsonl` (19,305 chunks / 2,017 files); added new `search_docs` PA tool.
3. **Triage of 3 large CodeReviewAgent artifacts** (preserved in `_archived/code_reviews_apr_2026.tar.gz`) — 2 of the flagged findings were still real in current code; both fixed in separate focused PRs.
4. Significant **disk cleanup** (18GB → 8.7GB) — old logs, abandoned ML venv, pycache, 4,725 stale agent-output stubs.

Chris's Session 1143 goal (declared at close): him + Claude Code + Rigby walking the entire `/docs/` corpus to figure out exactly what's in there — approach TBD.

---

## What landed (3 PRs, all open)

### PR #2178 — `feat/advisor-functional-identities`
*Two scopes bundled — advisor work was the original branch; docs-hygiene piggybacked because the advisor-count claim was one of the verifier drifts.*

**Advisor rename (Phase 1.a, pre-session):** 30 advisors renamed from named figures to functional identities. Registry, `ADVISOR_AUDIT.md`, narrative docs all rewritten.

**Docs-hygiene pass (commit `344d7b4e`):**
- Numeric drifts closed (`verify_doc_claims --only-drift`: 3 → 0):
  - `advisor_count_matches_doc` expected_named 16→0, expected_specialists 14→30
  - `pa_tool_count_89` expected 101→105 (then 106 with `search_docs`)
  - `pa_tools_86` expected 101→105 (then 106)
- New management command `core/management/commands/check_doc_headers.py`:
  - Parses `Last Updated: Session N` headers (top-of-doc, first 30 lines, Session-prefixed only)
  - Computes max `Session NNN` body reference (excluding header line itself)
  - Classifies: `clean` / `header_lag` / `frozen` / `no_body_refs` / `no_header`
  - Self-anchors `current_session` from `docs/handoffs/SESSION_NNNN_*.md`
- Category A header refreshes (5 → 0 stale headers):
  - `CAPABILITIES.md` Session 858 → 1142
  - `AGENTS.md` Session 1100 → 1142
  - `DATABASE_MODEL_REFERENCE.md` Session 969b → 1012
  - `PERSONAL_ASSISTANT_ARCHITECTURE.md` Session 931 → 933
- `PLATFORM_WHAT_IT_IS.md` "Stale or drifting (tonight's audit found)" section: replaced 45/65 stale text with current Session 1142 reality (0/73) + historical Session 1099 snapshot preserved

**`search_docs` PA tool (commit `27a08ceb`):**
- Wraps `core.rag.top_k` over `.rag/corpus.jsonl` (rebuilt to 19,305 chunks / 2,017 files)
- Returns ranked chunks with `[docs/path#chunk_id]` citations
- Truncates last chunk's text instead of dropping it on `max_chars` overflow
- `boost_hints` param added to `core/rag.py`: `True` (default) preserves askdocs CLI's legacy learning-loop bias; `False` = neutral ranking (used by `search_docs`)
- `kb_tool` (the existing Document-table tool) is now LIVE because `sync_docs_index_to_documents --embed` populated **852 docs / 14,149 chunks** (was 0/0)
- Both tools complement: `kb_tool` for structural browse, `search_docs` for chunked text retrieval

**Live verification post-restart:** Rigby called `search_docs(query="agent router", k=2)` in 259ms and returned `[docs/CLAUDE.md#6]` + `[docs/24_7_GLOBAL_AI_APP_ATLAS.md#12]` with correct chunks. Both `kb_tool` and `search_docs` operational.

**Gotcha discovered:** `make celery` doesn't restart workers if `.celery*.pid` files exist. Worker process keeps stale PA tool schema list across daphne restart. Fix protocol: `pkill -9 -f celery; rm -f .celery*.pid; make celery`. Memory candidate.

### PR #2180 — `fix/markdown-xss-rehype-sanitize` (off `main`)
Closes the markdown XSS gap from the April 18 CodeReviewAgent audit:

> A. ReactMarkdown render XSS risk — Severity: high
> Problem: ReactMarkdown with remark-gfm can render raw HTML unless sanitized.

Verified current state of all 10 ReactMarkdown sites in `frontend/src/` — none had `rehype-sanitize` applied. Added `rehype-sanitize ^6.0.0` to `package.json` and wired `rehypePlugins={[rehypeSanitize]}` into every `<ReactMarkdown>` invocation (12 instances across 10 files).

Sites patched: `ChatMarkdown.tsx`, `DocumentViewer.tsx`, `DeliverablesTable.tsx`, `AgentsPage.tsx`, `ProjectHubPage.tsx`, `WorkspacePageNew.tsx` (×2), `ContentStudioTab.tsx` (×3), `DeliverablesTab.tsx`, `InitiativesTab.tsx`, `KnowledgeTab.tsx`.

TypeScript check introduces no new errors in any of the 10 patched files (pre-existing errors in unrelated files remain).

**Why not centralize through `ChatMarkdown`:** the 10 files render markdown from different sources (deliverable content, KB documents, blog drafts, etc) with distinct component overrides — refactoring through `ChatMarkdown` would change styling and prop shapes in 9 unrelated UI surfaces. In-place plugin add preserves each site's rendering contract.

### PR #2181 — `fix/pa-cache-race` (off `main`)
Closes the check-then-act race in `get_unified_pa()` from the same audit — verified still present in current code, byte-identical to what the review flagged.

**3 bundled corrections (1 file, 35 insertions / 14 deletions):**
1. **`threading.Lock`** around the check+set in `get_unified_pa`. Verified with 50-thread hammer test → 1 distinct instance (was racing previously).
2. **`clear_pa_cache(0)` no longer wipes the whole cache.** Old `if user_id:` evaluated False for `user_id=0`, silently bulk-clearing. Changed to `is not None`.
3. **Bulk clear mutates in place** (`_pa_instances.clear()`) instead of rebinding (`_pa_instances = {}`). The rebind broke any in-flight coroutine holding a reference to the old dict.

**Risk surfaces** (which call sites can race):
- Celery `pa` worker (`--pool=solo`) — no race
- `views_personal_assistant.py:77, 854` (sync Django views in daphne threadpool) — **race possible**
- `consumers_unified_v2.py:115` (WS consumer) — **race possible**
- `views_assistant_bypass.py:91` (sync view) — **race possible**

---

## Significant disk cleanup (18GB → 8.7GB freed ~9.3GB)

Chris flagged his disk was full mid-session. Audited + cleared in two phases:

**Tier 1 safe wipes (8GB):**
- Old logs (`logs/archive_from_root_2026-04-20/` 4.1GB + scattered root .log/.out files): ~4.3GB
- `__pycache__` + `.pyc` (6,073 dirs, 39k files → 0): ~100MB
- `dump.rdb` (Redis snapshot, auto-regen): 11MB
- `mobile/node_modules/` (rebuild via `cd mobile && npm install`): 501MB
- 13 agent output dirs (`income_builder_outputs/`, `development/`, `diversity/`, etc — all gitignored, all template/stale): 31MB
- `venv_ml/` (abandoned ML venv, no `bin/python`, last touched May 7): 2.7GB

**Tier 2 specific approvals (1.3GB):**
- `backups/database/` (Dec 30 Postgres dumps): 914MB
- `media/rescued_videos/` (one-time migration leftover): 160MB
- `django_debug.log` truncated 236MB → 5.9KB (daphne kept writing to same file handle, no restart)

**Preserved:** the 3 substantive CodeReviewAgent reports as `_archived/code_reviews_apr_2026.tar.gz` (385KB compressed). Two findings actionable → PRs #2180 & #2181.

**One scare:** when wiping the 13 agent output dirs, accidentally deleted the entire tracked `sports/` Django app (32 files). Caught immediately via `ModuleNotFoundError: No module named 'sports'` on next `manage.py` invocation. Fully restored from git via `git checkout -- sports/`. Lesson: always check `git ls-files <dir>` before bulk `rm -rf`.

---

## State of the world at session close

**Branches open (3 from this session + 1 carryover):**
| # | Branch | What | Status |
|---|---|---|---|
| 2178 | `feat/advisor-functional-identities` | Advisor rename + docs hygiene + `search_docs` | OPEN, gated on Chris review |
| 2180 | `fix/markdown-xss-rehype-sanitize` | rehype-sanitize on 10 ReactMarkdown sites | OPEN, gated on Chris review |
| 2181 | `fix/pa-cache-race` | `get_unified_pa` lock + `clear_pa_cache` correctness | OPEN, gated on Chris review |
| 2179 | `fix/decision-13-test-data-contamination` | (pre-existing, unrelated) | OPEN |

**Live runtime state:**
- `verify_doc_claims --only-drift`: 0 drifts (was 3 at session start, was 45/65 per Session 1099 historical baseline)
- `check_doc_headers --only-stale`: 0 `header_lag` (was 5), 9 `frozen` (Category B, deferred for Session 1143 triage)
- `kb_tool` populated: 852/852 docs embedded, 14,149 chunks
- `search_docs` registered (gated on PR #2178 merge): callable as PA tool, 259ms latency on live test
- All 4 Session 1142 verifier sanity checks pass (lock present, 50 threads → 1 instance, `clear_pa_cache(0)` preserves cache, bulk clear preserves dict identity)

**Carryover from Session 1142 not addressed:**
- Memory rule: unbounded growth in `_pa_instances` dict (one entry per user, never evicted) — flagged in same audit, deemed low-priority (matters only at high user counts)
- Category B frozen docs (9 docs untouched since Session 84–1012) — triage queued for Session 1143
- Session 1142 didn't action the Session 1141 carryover items (Jessica Decision 9 schema, Decision 19 retune, ops view fork) — those remain in the punch list

---

## Session 1143 setup (Chris's stated goal)

Walk all of `/docs/` together (Chris + Claude Code + Rigby) to map exactly what's in there. Approach not yet decided.

See `00-START-NEXT-SESSION.md` for the four approach options pitched as opening pitches:
- (A) Top-down by category
- (B) By doc age (start with the 9 frozen Category B docs)
- (C) Query-driven via Rigby's new `search_docs` tool
- (D) By git activity drop-off

Pre-staged context Session 1143 can use:
- `kb_tool` (semantic, via DocumentEmbedding pgvector) — works now
- `search_docs` (chunked text, via `.rag/corpus.jsonl` token-overlap) — works once PR #2178 merges
- `docs/INDEX.md` + `docs/_index.json` — auto-generated index of all docs
- `check_doc_headers` (header-recency check) — works now
- `verify_doc_claims` (numeric claim drift) — works now, all clean
