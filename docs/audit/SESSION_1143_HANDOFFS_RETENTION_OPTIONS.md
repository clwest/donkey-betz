---
title: "Session 1143 — Phase 3 handoffs retention options memo (Chris's call)"
status: active
authority: deliverable-decision-pending
session: 1143
date: 2026-05-25
authors: Claude Code (Session 1143), Rigby (PA conversation pa-d19c1674b936)
last_verified: 2026-05-25
---

# Session 1143 — Handoffs Retention Options Memo

> **Decision-ready memo for Chris.** No file moves. Three options (A keep / B archive / C hybrid), with risk framing per Rigby's spec. Pick one (or write a fourth) — the path that gets greenlit becomes Phase 5 execution work.

## TL;DR

**`docs/handoffs/` holds 726 files / 7.1 MB / 27% of all `docs/` disk.** It's the heart of the platform's build history — every session writes one. The question is **how aggressively to retain pre-Session 800 handoffs vs preserve them in place**.

| Option | What it does | Pros | Cons |
|---|---|---|---|
| **A. Keep + V1 banners + INDEX** | Leave all 726 in place; add a single `docs/handoffs/INDEX.md` for navigation; V1 "historical output" banners on Session ≤800 | Zero risk to citations. Maintains lex-sorting. No move churn. | `handoffs/` still hard to scan. Sessions ≤500 (236 files) feel like noise. |
| **B. Archive pre-800 → `docs/archive/handoffs-pre-800/`** | Move 453 pre-Session-800 files to archive with V2-Moved stubs at original paths | Cleaner `handoffs/` (273 active files instead of 726). | Breaks `[docs/handoffs/SESSION_NNN#chunk]` citation identity in prior RAG outputs. Requires kb_tool re-index. |
| **C. Hybrid — keep last 250-300, archive older, freeze naming** | Keep ~Session 800+ in place (273 files); archive earlier in dated buckets (`handoffs-2025/`, `handoffs-early-2026/`) with V2 stubs; lock the naming convention `SESSION_NNNN_TOPIC.md` going forward | Best balance. Recent history scannable. Older history preserved. | Same citation-identity issue as B for the moved files. More setup work (multiple archive subdirs). |

**Rigby's lean:** Option C if Chris values handoffs/ scannability; Option A if citation stability matters more.

**My lean:** Option A. Low-risk, reversible, and the cost (a slightly noisy `handoffs/`) is mostly cognitive, not operational. RAG citations break the moment we move things. Archived handoffs become genuinely hard to find via `search_docs`.

**Default if Chris doesn't pick:** Option A (it's the no-op).

## Inventory

| Metric | Value |
|---|---|
| Total `.md` files at `docs/handoffs/` (no subdirs) | 726 |
| Total disk | 7.1 MB |
| % of all `docs/` disk | 27% |
| Naming patterns | `SESSION_NNNN_TOPIC.md` (most), `HANDOFF_NN_TOPIC.md` (7 early structured plans), `CURRENT.md` (navigation pointer), `SESSION_ROADMAP_DISCONNECTED_FIXES.md` (1 special) |

### Age distribution (by session number)

| Session range | Count | % |
|---|---|---|
| 0001–0500 | 236 | 33% |
| 0501–0800 | 217 | 30% |
| 0801–1000 | 156 | 22% |
| 1001–1100 | 57 | 8% |
| 1101+ | 47 | 7% |
| (non-session-numbered: CURRENT.md, HANDOFF_*, SESSION_ROADMAP_*) | 13 | 2% |

**Cutoff math:**
- ≤Session 800 = **453 files (62%)** — Option B candidate set
- ≤Session 1000 = **609 files (84%)** — alternative cutoff for Option C
- ≥Session 800 = **273 files** stays in place under Option C

### Output character

Sample read of `SESSION_998_GOVERNANCE_HARDENING.md`:
- Standardized header: `**Date**`, `**Focus**`, then `## Problem` / `## What Was Built` body.
- Each handoff IS a session snapshot. They're append-only outputs, not canonical narrative.
- `CURRENT.md` is the **only navigation pointer**; it's hand-maintained ("only 2 entries: Latest + Previous").

**Conclusion:** handoffs are **outputs**, not canon. Their value is historical (build history, decision rationale, white-paper material per Chris's preservation rule). They're not consulted as authoritative for current state — `topics/*` + `PLATFORM_INVENTORY.md` are.

## Risk framing — what breaks if we move

This is the load-bearing decision factor. Per Rigby's Phase 2A pre-flight checklist + DOC_LIFECYCLE.md §Citation-identity caveat:

### 1. RAG citation identity (highest risk)

Rigby's `search_docs` PA tool indexes `.rag/corpus.jsonl` with chunk IDs at the form `[docs/handoffs/SESSION_NNN_TOPIC.md#chunk_K]`. **Moving the file breaks the chunk_id mapping.** V2 stubs at the old path:
- ✅ Prevent 404s on direct human navigation
- ✅ Tell readers "this moved here"
- ❌ Do NOT preserve `[docs/handoffs/SESSION_NNN#chunk_K]` citation identity in prior RAG outputs / deliverables / saved Rigby conversations

**Estimate:** if 453 files move, ~6,000+ historical chunk IDs become stale. Re-indexing fixes future searches; old citations stay broken.

### 2. Grep/string references in code + docs

Sample `grep` from prior audits: ~30 inbound references to specific `docs/handoffs/SESSION_NNN_*.md` files across other docs + Python comments. Each would resolve to a V2 stub (still navigable, just one hop).

### 3. `CURRENT.md` navigation

`CURRENT.md` is a hand-maintained "Latest + Previous" pointer. It points at the most recent handoff. Moving older files doesn't affect it. **Low risk.**

### 4. `docs/INDEX.md` autogen behavior

`python manage.py build_docs_index` scans `docs/**/*.md` and produces `docs/INDEX.md`. Moves require a regen pass to keep INDEX correct. **No risk, just a chore.**

### 5. `search_docs` re-index requirement

After any move, run whatever produces `.rag/corpus.jsonl` (Session 1142 search_docs PA tool — find the regen command). Same for `kb_tool` (852 docs / 14,149 chunks embedded). Until re-indexed, `search_docs` returns stale paths.

## The three options in detail

### Option A. Keep + V1 banners + INDEX

**What:**
- All 726 files stay at `docs/handoffs/SESSION_NNN_*.md`.
- Add `docs/handoffs/INDEX.md` — a single navigation file listing handoffs grouped by 100-session buckets (or by year if we can map session → date). Currently absent; `CURRENT.md` is the only pointer.
- Add V1 stale-but-canonical banner ("historical session output") to all Session ≤800 handoffs (453 files). One-line banner per file.

**Pros:**
- Zero RAG citation identity churn.
- Zero broken inbound references.
- Reversible — banners can be removed later.
- `CURRENT.md` keeps working as-is.

**Cons:**
- `handoffs/` still has 726 files in one flat dir.
- Visually noisy on the filesystem.
- 453 V1 banner edits is a real PR — non-trivial diff size.

**Effort:** ~1-2 hours. Per-file banner script + INDEX.md hand-build (or autogen).

### Option B. Archive pre-Session-800 → `docs/archive/handoffs-pre-800/`

**What:**
- `git mv docs/handoffs/SESSION_<≤800>_*.md docs/archive/handoffs-pre-800/SESSION_<≤800>_*.md` for all 453 files
- V2-Moved stubs at the original paths (4-line stub per file)
- Re-index `search_docs` corpus + rebuild `docs/INDEX.md`
- Update `CURRENT.md` if it cites anything ≤800 (it doesn't; points at Session 1126)

**Pros:**
- `handoffs/` becomes 273 files (62% reduction).
- Scannable.
- Pre-800 archive is genuinely closed history — Sessions 1-800 covered the build, current cycle is 1100+.

**Cons:**
- 453 V2 stubs created (each at original path).
- Breaks `[docs/handoffs/SESSION_NNN#chunk_K]` citation identity in prior RAG outputs.
- Required re-index of `search_docs` + `kb_tool`.
- Larger PR diff than Option A.

**Effort:** ~2-3 hours including stub creation + verification + re-index.

### Option C. Hybrid — keep last ~250-300, archive older, freeze naming

**What:**
- Keep Session ≥800 in place (~273 files).
- Archive `docs/archive/handoffs-2025/` (early-Session 1-500, ~236 files) and `docs/archive/handoffs-early-2026/` (Session 501-799, ~217 files) — two dated buckets.
- V2-Moved stubs at original paths.
- Lock naming convention: `SESSION_NNNN_TOPIC.md` (always 4 digits, sequential) going forward — document in `docs/00-START-HERE/DOC_LIFECYCLE.md`.

**Pros:**
- Best scannability win.
- Two date-bounded archive buckets preserve historical groupings.
- Naming-convention lock prevents future drift (Rigby's audit doc question #7).

**Cons:**
- Same citation-identity churn as Option B (453 files moved).
- Most operational work (multi-dir + naming convention doc + reindex).

**Effort:** ~3-4 hours.

## Recommendation: Option A

My read after writing the inventory:

1. **Citation identity is the real cost.** Every prior `search_docs` answer Rigby gave that cited a handoff chunk by path will resolve to a V2 stub, not the original chunk. That's not just "one hop more" — it's "the body content is at a different chunk_id and search_docs won't surface the canonical text anymore." For docs Rigby actively cites (build history, decision rationale), that's worse than visual clutter.

2. **The cognitive cost of 726 files is real but bounded.** A single `INDEX.md` grouping by 100-session bucket compresses 726 → ~8 buckets visually. `CURRENT.md` already handles "where's the latest?"

3. **Option A is reversible.** If 6 months from now we want to archive pre-800, V1 banners come off cleanly and the move can proceed.

4. **Per Chris's session directive,** docs-only mode prefers conservative moves over aggressive consolidation.

**However** — Chris's actual preference may differ. He might value scannability over citation stability. The path that gets picked drives Phase 5 execution.

## PLATFORM_INVENTORY + docs/INDEX as the sole "counts" source going forward (Rigby's add-on)

Independent of which retention option Chris picks, this paragraph is queued for follow-up:

`PLATFORM_INVENTORY.md` (autogen via `generate_platform_inventory`) and `docs/INDEX.md` (autogen via `build_docs_index`) are the **only** authoritative counts in the corpus going forward. Every other doc that quotes a count (agent count, spider count, model count, deliverable count) is a **snapshot** of a moment, not a current claim. The Session 1142 verifier (`verify_doc_claims --only-drift`) enforces this for tagged claims; everything else gets a DOC-POINTER-V1 banner if it ages past 3 months.

This locks the "reality score" cluster (Phase 4 finding) from regenerating — no future doc should write "Reality Score: 99.9%" as a numeric claim; if it does, the verifier flags it. Suggested addition to `docs/00-START-HERE/DOC_LIFECYCLE.md` after Chris approves Phase 4's Tier 2 dispositions.

## What's NOT in scope for this memo

- **No file moves.** This is decision-prep only.
- **No V1 banner application.** Whichever option Chris picks becomes Phase 5 execution.
- **No naming-convention spec.** Option C would include it; otherwise out of scope here.
- **No `kb_tool` re-index plan details.** Options B/C would need that as part of Phase 5; covered briefly above but not specified.

## Decision needed — Chris

Pick A / B / C (or write a fourth). Reply in the chat or comment on PR #2193. Once locked, the execution PR opens against the chosen direction.

| | A: Keep | B: Archive pre-800 | C: Hybrid + naming-lock |
|---|---|---|---|
| Citation safety | ✅ | ❌ | ❌ |
| Scannability | ❌ | ✅ | ✅✅ |
| Effort | Low | Medium | High |
| Reversibility | ✅ | Slow | Slow |
| My lean | ⭐ | | |
| Rigby's lean | | | ⭐ (if scannability matters) |

---

## Cross-references

- Session 1143 master audit: [`SESSION_1143_DOCS_AUDIT.md`](SESSION_1143_DOCS_AUDIT.md) — Phase 3 was originally proposed here.
- Abandoned-features audit: [`SESSION_1143_ABANDONED_FEATURES_AUDIT.md`](SESSION_1143_ABANDONED_FEATURES_AUDIT.md)
- Phase 4 redundancy hunt: [`SESSION_1143_REDUNDANCY_HUNT.md`](SESSION_1143_REDUNDANCY_HUNT.md)
- Methodology spec (V2 stub + citation caveat): [`/docs/00-START-HERE/DOC_LIFECYCLE.md`](../00-START-HERE/DOC_LIFECYCLE.md)

**Authors:** Claude Code (Session 1143) + Rigby (PA conversation `pa-d19c1674b936`). Decision-prep memo per Rigby's Phase 3 spec. No files moved; awaiting Chris's per-option pick.
