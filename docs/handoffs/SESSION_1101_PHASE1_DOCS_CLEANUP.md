---
title: "Session 1101 — Phase 1 docs cleanup (H1 + H3 + H2 + M1 + M2)"
date: 2026-05-07
status: active
session: 1101
previous_handoff: SESSION_1100_CONTEXT_KIT_DRIFT_PREVENTION.md
---

# Session 1101 — Phase 1 docs cleanup (H1 + H3 + H2 + M1 + M2)

## TL;DR

- **What shipped:** Five docs-only cleanup items from `docs/audit/CLEANUP_PLAN.md` Phase 1/3/5: spider-count drift fixes (H1), legacy assistant-route labeling (H3), historical-snapshot isolation in `BACKEND_INVENTORY.md` (H2), audit-workspace top-level index (M1), stable current-handoff pointer (M2).
- **Live conflict resolved:** `context-kit verify` now reports **`CONFLICT: 0`** (was 1 — spider count). VERIFY_REPORT.md regenerated.
- **What's blocking next:** Nothing. Remaining cleanup items (H4 logo replacement, H5 RAG corpus untrack) require deliberate verification cycles and were left for a follow-up session.
- **What's in a weird state:** `docker-compose.yml` is still modified and intentionally uncommitted (carryover from Session 1100).

---

## What Shipped

### H1 — Spider count reconciliation (canonical = 80)

Headline number swapped or DOC-POINTER added on the active load-bearing docs that drifted:

- [`docs/topics/README.md`](../topics/README.md): `77 spiders` → `80 spiders`; `76 agents` → `83 agents` in the topic-table descriptors.
- [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md): added DOC-POINTER-V1 banner; `Spider Network (64 spiders)` → `Spider Network (80 spiders — Session 1100 refresh; canonical: PLATFORM_INVENTORY)`.
- [`docs/SYSTEM_OVERVIEW.md`](../SYSTEM_OVERVIEW.md): added DOC-POINTER-V1 banner; agent/spider lines now annotate Session 858 snapshot with canonical 83/80.
- [`docs/AUTONOMOUS_SYSTEMS.md`](../AUTONOMOUS_SYSTEMS.md): added DOC-POINTER-V1 banner; flagged the Dec 17, 2025 snapshot framing.
- [`docs/BACKEND_REFERENCE.md`](../BACKEND_REFERENCE.md): added DOC-POINTER-V1 banner; TOC line for `Spider Network (77 spiders)` annotated with canonical 80.
- [`docs/CAPABILITIES.md`](../CAPABILITIES.md): historical detail header `Spider Network (70 Spiders)` → `Spider Network (historical detail — canonical = 80; see PLATFORM_INVENTORY)`. Headline table at top already correct (80) from Session 1100.
- [`ai_core/spiders/README.md`](../../ai_core/spiders/README.md): strong "HISTORICAL / ASPIRATIONAL DOCUMENT" banner; the legacy "1,770 specialized spiders / 149 agents" framing now explicitly labeled as an earlier aspirational plan, with canonical counts (80 / 83 / 32) at the top.

`docs/SPIDERS.md` and `docs/topics/spider-network.md` were already on 80 (no edits needed). Historical narrative under `docs/archive/**`, `docs/handoffs/SESSION_*`, `docs/audits/`, `docs/audit-2026/` left untouched per the never-delete-history rule — covered by the M1 banner instead.

### H3 — Legacy `/api/assistant/chat/` labeling in active docs

Where the route appears in active (non-archive) docs, it is now explicitly labeled as a compat shim:

- [`docs/PERSONAL_ASSISTANT_ARCHITECTURE.md`](../PERSONAL_ASSISTANT_ARCHITECTURE.md): added DOC-POINTER-V1 marking it as a Session 931 historical gap-analysis. REST endpoint table reordered: `POST /api/pa/chat/` listed first as **canonical**, both legacy paths labeled "Legacy compatibility shim."
- [`docs/code-review/remediation/02-PHASE2-HIGH-PRIORITY.md`](../code-review/remediation/02-PHASE2-HIGH-PRIORITY.md): historical-remediation banner; pointer to canonical PA topic doc.
- [`docs/code-review/remediation/05-VERIFICATION-CHECKLIST.md`](../code-review/remediation/05-VERIFICATION-CHECKLIST.md): same banner; curl examples preserved as historical, route labeled.
- [`docs/audits/*.md`](../audits/) (3 files: `discovery_api_endpoints.md`, `SESSION_727_INTELLIGENT_PROMPTING_AUDIT.md`, `SESSION_729_MEMORY_SYSTEM_AUDIT.md`): not touched per-file; covered wholesale by the M1 banner on [`docs/audits/INDEX.md`](../audits/INDEX.md).

[`docs/topics/personal-assistant.md`](../topics/personal-assistant.md) already had the canonical/compat note from Session 1100 — no change.

### H2 — Historical snapshot isolated in `BACKEND_INVENTORY.md`

The "Manual Snapshot (history)" table in [`docs/BACKEND_INVENTORY.md`](../BACKEND_INVENTORY.md) was renamed to "Historical Snapshot (Jan–Apr 2026)", wrapped in a `<details>` block, and stamped with a "Do not cite as current truth" note pointing at `PLATFORM_INVENTORY.md`. Numbers preserved verbatim for build-history continuity; they just no longer present as the live reference table.

### M1 — Audit-workspace index

New: [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md). Top-level pointer that:

- Marks `docs/audit/` as the **only** current audit workspace.
- Marks `docs/audit-2026/` and `docs/audits/` as **historical**, do-not-cite-as-current-truth.
- Re-states the canonical PA route (`POST /api/pa/chat/`) so legacy route examples inside the historical workspaces are unambiguously legacy.
- Banner pointers added to:
  - [`docs/audits/INDEX.md`](../audits/INDEX.md) — top-level header now flags it as historical archive + legacy route convention.
  - [`docs/audit-2026/00-AUDIT-PLAN.md`](../audit-2026/00-AUDIT-PLAN.md) — top-level header flags it as a time-bounded April 2026 dossier series.

`docs/audit/README.md` was already in good shape (Session 1100) — no change.

### M2 — Stable current-handoff pointer

New: [`docs/handoffs/CURRENT.md`](CURRENT.md). Two-line pointer (Latest + Previous) so future sessions don't need to lex-sort 600+ files. Update protocol documented inside.

---

## What Didn't (and Why)

- **No runtime code changes.** Phase 1 scope was docs-only; the only verified file outside `docs/` is `ai_core/spiders/README.md` (a docstring file, not runtime).
- **No archive content rewrites.** Memory rule: never delete or rewrite history. All historical docs got pointer banners or explicit framing additions; their original content is intact.
- **Compat routes not changed.** Backend still serves `/api/assistant/chat/` and `/api/v1/assistant/chat/` as compatibility shims (per CLAUDE.md). Only docs were labeled.
- **H4 (donkey-logo replacement) and H5 (.rag corpus untrack) deferred** — both require browser/RAG verification cycles that were out of scope for this session.
- **Per-file edits in `docs/audits/`** intentionally skipped. The wholesale M1 banner covers route-label intent without thrashing 56 historical files.

---

## Verifier Outcome

Before edits (per `docs/verification/VERIFY_REPORT.md` 2026-05-03):

```
- VERIFIED: 2
- DOC_ONLY: 3
- CONFLICT: 1   ← spiders count
- UNKNOWN: 0
```

After edits (regenerated 2026-05-07):

```
- VERIFIED: 2
- DOC_ONLY: 4
- CONFLICT: 0   ← resolved
- UNKNOWN: 0
```

`python manage.py verify_doc_claims --only-drift` (Django-side claim verifier) reported one unrelated drift untouched by this session (`CLAUDE.md` agent taxonomy: claims `73 enabled, 8 rerouted, 2 blocked`; verifier sees `73 enabled, 9 rerouted, 1 blocked`). That is pre-existing and out of Phase 1 scope. Four other findings were Postgres-availability errors, not drift.

---

## Files Changed (exact list)

```
docs/topics/README.md                                       (2 edits)
docs/ARCHITECTURE.md                                        (2 edits)
docs/SYSTEM_OVERVIEW.md                                     (2 edits)
docs/AUTONOMOUS_SYSTEMS.md                                  (1 edit)
docs/BACKEND_REFERENCE.md                                   (2 edits)
docs/CAPABILITIES.md                                        (1 edit)
ai_core/spiders/README.md                                   (1 edit)
docs/PERSONAL_ASSISTANT_ARCHITECTURE.md                     (2 edits)
docs/code-review/remediation/02-PHASE2-HIGH-PRIORITY.md     (1 edit)
docs/code-review/remediation/05-VERIFICATION-CHECKLIST.md   (1 edit)
docs/BACKEND_INVENTORY.md                                   (1 edit — Manual Snapshot block)
docs/audits/INDEX.md                                        (1 edit — historical banner)
docs/audit-2026/00-AUDIT-PLAN.md                            (1 edit — historical banner)
docs/AUDIT_INDEX.md                                         (NEW)
docs/handoffs/CURRENT.md                                    (NEW)
docs/handoffs/SESSION_1101_PHASE1_DOCS_CLEANUP.md           (NEW — this file)
docs/verification/VERIFY_REPORT.md                          (regenerated by `context-kit verify --write`)
00-START-NEXT-SESSION.md                                    (re-pointed at this handoff — see below)
```

No backend, frontend, or runtime code touched.

---

## Live Conflicts Remaining

**None at the verifier level.** `CONFLICT: 0` confirmed via `context-kit verify --json` and `--write` re-runs.

Remaining `DOC_ONLY` findings (4) are not drift — they are canonical doc claims for which no runtime extractor exists yet (agents count, APIs count, frontend pages count, spiders count). These are advisory and align with canonical = 83/80.

---

## Next Session Picks Up With

1. **H4 — `core/static/images/donkey-logo.png` (24 MB) replacement.** Cross-stack, browser verification required. Plan: produce downsized PNG/WebP at the same path, smoke-test `/ai-studio/`, then decide whether to keep tracked or move behind a regen step.
2. **H5 — `.rag/corpus.jsonl` + `.rag/embedding_refs.txt` untrack.** Confirm regen path before removing. Backend-only.
3. **Pre-existing CLAUDE.md taxonomy drift** (`73 enabled, 8 rerouted, 2 blocked` vs verifier's `73/9/1`). Five-character fix in CLAUDE.md if Chris approves; out of Phase 1 scope.
4. **L1/L2 guardrails** (CI gate for verifier; post-merge inventory regen) — the script `scripts/verify_repo_guardrails.py` already exists; wiring into CI is the missing piece.

---

## Rigby / PA / AI Context

- **Conversation ID:** none for this doc-only session.
- **State at end of session:** Active docs aligned with the canonical truth chain. `CONFLICT: 0` at the verifier. Audit + handoff navigation hardened with two new index files.
- **How to resume:** `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-donkeyking-token> .venv/bin/python tools/pa_chat.py "session 1101 follow-up" --conversation <id>`

---

## Cross-References

- Previous handoff: [`SESSION_1100_CONTEXT_KIT_DRIFT_PREVENTION.md`](SESSION_1100_CONTEXT_KIT_DRIFT_PREVENTION.md)
- Cleanup plan: [`docs/audit/CLEANUP_PLAN.md`](../audit/CLEANUP_PLAN.md)
- Audit V1: [`docs/audit/AUDIT_V1.md`](../audit/AUDIT_V1.md)
- New audit index: [`docs/AUDIT_INDEX.md`](../AUDIT_INDEX.md)
- Verification report: [`docs/verification/VERIFY_REPORT.md`](../verification/VERIFY_REPORT.md)
- Canonical truth docs: [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md), [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md)

---

*Written at end of session 2026-05-07. Do not edit after the next session begins. If the next session finds a bug in this handoff's reasoning, add a note at the bottom rather than rewriting — the original reasoning is history.*
