<!-- DOC-POINTER-V1 -->
> **Folder-local pointer; not authoritative for current state.** This README describes what lives in `docs/architecture/`. Earlier versions of this file made platform-wide claims ("master architecture document", "99.9% Reality Score", "34 features", "20+ tools", "Launch readiness 85%") — all of those were Session 85 (Nov 2025) snapshots and have been removed per `docs/00-START-HERE/DOC_LIFECYCLE.md` §2c (sole-counts-source rule).
> For current platform truth, see [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime counts) + [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md) (narrative) + [`docs/canon/INDEX.md`](../canon/INDEX.md) (canon registry) + [`docs/topics/`](../topics/) (subsystem deep-dives).
> Several files in this folder carry `DOC-POINTER-V2 (Session 1143)` banners — those are historical snapshots, useful as build history; do **not** cite them as current state.

# Architecture Documentation

System-design references, agent patterns, and historical integration maps. This folder is part of the docs corpus; it is not the platform's source of truth.

---

## Start here for current architecture

| Need | Go to |
|------|-------|
| Current platform counts (agents, spiders, tools, models) | [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) |
| Narrative overview (what the platform is, glossary) | [`docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md) |
| Canon registry (≤10 authoritative entry-point docs) | [`docs/canon/INDEX.md`](../canon/INDEX.md) |
| Subsystem deep-dives (PA, content pipeline, agents, etc.) | [`docs/topics/`](../topics/) |
| Doc lifecycle rules + V1/V2 banner contract | [`docs/00-START-HERE/DOC_LIFECYCLE.md`](../00-START-HERE/DOC_LIFECYCLE.md) |
| Doc corpus index (all docs, status, references) | [`docs/INDEX.md`](../INDEX.md) |

---

## What's in this folder

See [`INDEX.md`](INDEX.md) for the file list with superseded markers.

Files fall into three buckets:

- **Superseded snapshots** (`DOC-POINTER-V2`): historical architecture maps from Sessions 84–1115. Preserved because they document how the system evolved; not current truth.
- **Pattern docs** (some V1, some V2): describe design patterns (multi-agent routing, prompting, ML architecture) that may still apply conceptually even when specific names or counts have drifted. V1-banner files carry a drift warning pointing at `PLATFORM_INVENTORY`.
- **Domain integration notes** (older, Oct 2025): `learning_system.md`, `partnership_model.md`, `sports_betting_integration.md` — pre-§0-boundary integration write-ups. Treat as historical context.

---

## How architecture truth flows now

The Session 1143 doc lifecycle (locked in `DOC_LIFECYCLE.md` §2c) split documentation into two roles:

1. **Sole-counts-source docs** own specific numbers. For platform runtime counts that's `PLATFORM_INVENTORY.md`; for doc corpus counts that's `docs/INDEX.md`. Everything else points at them.
2. **Narrative/pattern docs** (this folder, `docs/topics/`, etc.) describe behavior, design intent, and history without restating counts.

`python manage.py verify_doc_claims --only-drift` flags any claim that drifts from the runtime.

---

## Per-file pointers

For per-file V1/V2 status see [`INDEX.md`](INDEX.md). Each file should carry its own banner explaining whether it's current-pattern (V1) or superseded (V2) — Session 1145 sweep is completing the unbannered files.
