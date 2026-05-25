---
title: "Doc Lifecycle — pointer headers + root-stability rule"
status: active
authority: canonical
session_added: 1143
last_verified: 2026-05-24
---

# Doc Lifecycle — Pointer Headers + Root-Stability Rule

> **Why this doc exists:** `/docs/` had drifted into 92 loose top-level files + 43 subdirs + 11M of archive with no shared vocabulary for "this is moved" vs "this is stale but in place." Session 1143 locked the conventions below. Every future `/docs/` operation that moves, renames, or supersedes a file MUST follow them.

## 1. Two pointer-header types

Pointer headers are 4–8 line metadata blocks at the very top of a doc. They tell future Claude Codes (and Rigby's `search_docs`) the doc's lifecycle state without anyone having to read the body.

### DOC-POINTER-V1 — stats-drift banner (in-place doc)

For canonical docs that STAY in place but whose numeric claims may drift from runtime reality. Already in use as of Session 1142 (10 files: AGENTS.md, ARCHITECTURE.md, AUTONOMOUS_SYSTEMS.md, BACKEND_REFERENCE.md, CAPABILITIES.md, DISCORD_INTEGRATION.md, PERSONAL_ASSISTANT_ARCHITECTURE.md, SERVICES.md, SPIDERS.md, SYSTEM_OVERVIEW.md).

```markdown
<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md) and [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.
```

**Use when:** the doc is still the canonical place for its topic, but it has counted claims (agent counts, file counts, model counts) that the verifier might flag.

**Stale-but-canonical variant:** if the doc is canonical AND hasn't been refreshed in 3+ months, append `> **Note:** content may be stale — verify against code before relying on specifics.` to the banner. This stays at root (don't move) but tells readers the policy/content side may have drifted, not just the numbers. (Session 1143 addition, Rigby callout: "don't silently present stale policy as canonical without a banner.")

### DOC-POINTER-V2 — supersession/relocation pointer (new, Session 1143)

For docs whose canonical location or meaning CHANGED. Either the doc was moved, an updated version exists elsewhere, or the doc is preserved for historical reference only.

```markdown
<!-- DOC-POINTER-V2 (Session NNNN) -->
> **Status:** Archived | Superseded | Moved | Historical | Deprecated | Stale (Category B)
> **Originally:** Session NNN (YYYY-MM-DD), purpose: <one-line summary>
> **Last verified:** Session NNNN (YYYY-MM-DD)
> **Current canon:** [`docs/X.md`](X.md) — read this instead.
> **Change reason:** duplicate | renamed | re-architecture | incorrect | consolidated | scope changed
> **Preserved because:** white-paper corpus / historical record / link-rot prevention.
```

**Use when:** the file is being kept for the corpus per the never-delete rule, but readers should not treat it as current.

### Status enum (V2 only)

| Status | Meaning |
|---|---|
| **Archived** | Moved into `docs/archive/` subtree. Content preserved, not current. |
| **Superseded** | Replaced by a newer canonical doc. Old doc kept for citation history. |
| **Moved** | Pure relocation. Content still canonical, just at a new path. Stub remains at old path. |
| **Historical** | Captures a specific point-in-time state (e.g. a session-status snapshot). Never current. |
| **Deprecated** | Still accurate historically, but explicitly NOT recommended as a reference (e.g. an old architecture before a redesign). |
| **Stale (Category B)** | Untouched for ≥3 months, may be drifting from reality but not yet verified-wrong. Soft signal. |

## 2. Stub-redirect pattern (for Moved docs)

When a doc moves from `docs/X.md` → `docs/<subdir>/X.md`, **keep a 4-line stub at the old path**:

```markdown
<!-- DOC-POINTER-V2 (Session NNNN) -->
> **Status:** Moved
> **Current canon:** [`docs/<subdir>/X.md`](<subdir>/X.md) — read this instead.
> **Preserved because:** link-rot prevention.
```

That's it. No body. The stub exists to prevent external/historical links from 404'ing. Readers see one screen, click through.

> **Citation-identity caveat:** V2 stubs preserve human navigation but **do not** preserve prior RAG citation identity. Any `[docs/path#chunk_id]` citation Rigby or `search_docs` produced before the move will resolve to the stub, not the canonical chunk. If a doc is heavily cited externally or in archived RAG outputs, prefer leaving it in place with a stale-but-canonical V1 variant banner over moving it.

**Required stub addition (Session 1143):** every V2-Moved stub MUST carry the line `> **Caveat:** Prior RAG citations may no longer resolve to the same chunk_id.` so the trade-off is visible to anyone reading old outputs.

## 3. Root-stability rule (Rigby's lock, Session 1143)

> **Anything referenced by `CLAUDE.md`, `00-START-NEXT-SESSION.md`, or any `*_AUDIT.md` MUST exist at the cited path — either as the canonical doc or as a permanent V2 stub.**

This is non-negotiable. CLAUDE.md is loaded into every session; `*_AUDIT.md` files are autogen'd by mgmt commands that reference each other; both have stable paths that downstream consumers depend on.

Before moving any doc, run:

```bash
grep -rn '<filename>\.md' CLAUDE.md 00-START-NEXT-SESSION.md docs/*_AUDIT.md
```

If any match, the doc must stay at root OR get a permanent stub at the old path. No exceptions.

## 4. Loose vs subdir placement (heuristic)

| Lives at `docs/` root | Lives in a subdir |
|---|---|
| **Anchors** (PLATFORM_WHAT_IT_IS, PLATFORM_INVENTORY, KNOWLEDGE_PIPELINE, UDB_*, 24_7_GLOBAL_AI_APP_ATLAS) | Topic deep dives (`docs/topics/`) |
| **Autogen audits** (`*_AUDIT.md`, regen'd by `build_*` mgmt commands) | Historical audits (`docs/audits/` or `docs/audit-2026/`) |
| **Active indexes** (INDEX.md, AUDIT_INDEX.md, CAPABILITIES.md) | Session handoffs (`docs/handoffs/`) |
| Anything CLAUDE.md cites | Specs (`docs/specs/`) |
| | Plans / proposals (`docs/plans/`) |
| | Anything not actively touched in current cycle |

When in doubt: the more frequently a doc is read, the closer to the root it lives.

## 5. Before-you-move checklist

1. Grep for inbound references: `grep -rn '<filename>\.md' . --include='*.md' --include='*.py'`
2. If CLAUDE.md / `00-START-NEXT-SESSION.md` / `*_AUDIT.md` reference it → root-stable. Stub at minimum.
3. Add the V2 header to the destination file with full fields filled in.
4. Add a stub at the source path (4 lines, V2-Moved status).
5. Run `python manage.py build_docs_index` to refresh `INDEX.md` + `_index.json`.
6. Run `python manage.py verify_doc_claims --only-drift` if the moved doc had counted claims.

## 6. Related conventions

- **DOC-AUTOGEN header** (already in use): for files generated by mgmt commands. Do not hand-edit; refresh via the named command. Listed in `docs/INDEX.md` regenerator.
- **YAML frontmatter** (active anchors): `title`, `status`, `authority`, `last_verified`. Used by anchor docs (PLATFORM_WHAT_IT_IS, UDB_BEHAVIOR_LAYER, etc.). Adopted incrementally; not required for every doc.

---

**Last updated:** Session 1143 (2026-05-24) — initial lock by Claude Code + Rigby during corpus walk-through.
