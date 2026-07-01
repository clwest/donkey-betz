# Start Here — Unified Donkey Betz

**Last updated:** Session 1279 (2026-07-02) — added Research Library entry-point row after S1279 Research OS installation.

This dir holds **methodology anchors** for working in the `/docs/` corpus. For session priorities, runtime state, and active work, see the project root:

## Mandatory entry points (read in order)

1. [`/CLAUDE.md`](../../CLAUDE.md) — primary system context, always loaded into the session. Includes the **Research Library** subsection (see #6 below).
2. [`/00-START-NEXT-SESSION.md`](../../00-START-NEXT-SESSION.md) — current session priorities + carryovers.
3. [`/docs/PLATFORM_WHAT_IT_IS.md`](../PLATFORM_WHAT_IT_IS.md) — narrative anchor.
4. [`/docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) — runtime anchor (regenerable, wins on conflict).
5. [`/docs/24_7_GLOBAL_AI_APP_ATLAS.md`](../24_7_GLOBAL_AI_APP_ATLAS.md) — strategy anchor.
6. [`/docs/research/process/RESEARCH_OPERATING_SYSTEM.md`](../research/process/RESEARCH_OPERATING_SYSTEM.md) — **Research OS** — the canonical process framework every Claude Code session executes. Read §0–§5 (bootstrap + request classification) before any non-trivial work; §8 for the matching startup contract.

## Research Library

Added S1279 (installation of the Research OS as canonical workflow):

- [`/docs/research/process/RESEARCH_OPERATING_SYSTEM.md`](../research/process/RESEARCH_OPERATING_SYSTEM.md) — the OS (v2.1). Superset containing the playbook. Governs every request class.
- [`/docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](../research/DOMAIN_RESEARCH_PLAYBOOK.md) — playbook v2 (research-class specialization of the OS).
- [`/docs/research/ARCHITECTURE_INDEX.md`](../research/ARCHITECTURE_INDEX.md) — library navigation + timeline + decision matrix.
- [`/docs/research/OPEN_ARCS.md`](../research/OPEN_ARCS.md) — machine-readable live manifest of research groups.
- [`/docs/research/process/claude_research_startup_introspection.md`](../research/process/claude_research_startup_introspection.md) — evidence base for the OS (S1276 introspection).

Reading the OS makes every other doc discoverable via cross-references. Do not scavenger-hunt; start at the OS.

## Methodology anchors (this dir)

- [`DOC_LIFECYCLE.md`](DOC_LIFECYCLE.md) — pointer header conventions (V1 stats-drift, V2 supersession) + root-stability rule. Read before moving, renaming, or superseding any `/docs/` file.
- [`INDEX.md`](INDEX.md) — index of files in this dir.

## Behavior + translation anchors (root of `docs/`)

- [`/docs/UDB_BEHAVIOR_LAYER.md`](../UDB_BEHAVIOR_LAYER.md) — Rigby's voice + display rules + constraint preservation.
- [`/docs/UDB_TRANSLATION_LAYER.md`](../UDB_TRANSLATION_LAYER.md) — audience contract (same truth → different explanation).

## Live drift checks

```bash
python manage.py verify_doc_claims --only-drift   # numeric drift detector
python manage.py check_doc_headers --only-stale   # header staleness
python manage.py build_docs_index                 # regenerate docs/INDEX.md + _index.json
.venv/bin/context-kit doctor                      # expected floor: 10 OK / 2 warnings
```

## Recent corpus audit

Session 1143 produced a deep audit of `/docs/`: [`audit/SESSION_1143_DOCS_AUDIT.md`](../audit/SESSION_1143_DOCS_AUDIT.md). It contains per-subdir verdicts, pathology list, and a phased action queue for cleanup work.

---

**Prior version:** the previous README (pre-Session 1143) pointed at a Session 84-era video-chaining status that had drifted ~16 months stale. Git history preserves it. The corpus white-paper preservation rule applies to handoffs / audits / topic docs — not orientation pages that exist to reflect current state.
