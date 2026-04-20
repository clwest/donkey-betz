---
title: "Docs Pattern — How to Structure /docs/ for AI-Built Platforms"
status: active
source: unified-donkey-betz Sessions 1087–1099
purpose: Teaching framework for reusing this /docs/ structure on future projects
---

# Docs Pattern

A distilled framework for how to structure the `/docs/` directory when you're building a platform with an AI pair (Claude Code, Cursor, Aider, etc.) over many sessions.

**Why this exists:** the `/docs/` folder in `unified-donkey-betz` grew to 600+ files over ~1100 build sessions. What started as notes ended up as the *operating memory* of the platform — embedded into LLM context on every session, searched at runtime, and audited against code. This directory captures the patterns that worked, the ones that didn't, and a bootstrap checklist for the next app.

---

## Core Rule (Zero)

**Never scatter `.md` files at the root of `/docs/`.** Put related docs in a named subdirectory. Flat `/docs/` becomes unmaintainable around ~20 files — the AI can't find anything, humans can't find anything, and nothing has a clear owner.

Already-proven groupings in this repo:
- `docs/topics/` — embeddable subsystem deep-dives
- `docs/current/` — auto-generated API/model/command references
- `docs/handoffs/` — session-by-session build history
- `docs/audit-2026/` — time-bounded audit dossiers
- `docs/docs-pattern/` — *this directory* (the meta-framework)

If a new doc doesn't fit an existing directory, create a new one.

---

## The Pattern — Four Load-Bearing Pieces

1. **The Two-Doc Anchor** — [`01_two_doc_anchor.md`](01_two_doc_anchor.md)
   `<name>_WHAT_IT_IS.md` (narrative) + `<name>_INVENTORY.md` (runtime-derived, regenerable). One file answers *what is this system*, the other answers *what exists right now*. Every other doc points at these when numbers disagree.

2. **The Drift Verifier** — [`02_drift_verifier.md`](02_drift_verifier.md)
   Registered claims + runtime checks + severity rollup. Docs stale the moment you write them; the only long-term answer is automation that catches drift.

3. **Embeddable Topic Docs** — [`03_topic_docs.md`](03_topic_docs.md)
   One doc per subsystem, short and scannable, indexed by `build_docs_index`, embedded into LLM context. If the AI can't see it, it doesn't exist.

4. **Session Handoffs** — [`04_session_handoffs.md`](04_session_handoffs.md)
   `SESSION_####_*.md` files written at the *end* of each session. Become the project's oral history — why decisions were made, what shipped, what to pick up next.

Tie it together with:

5. **The Start-Here Doc** — [`05_start_here.md`](05_start_here.md)
   `00-START-NEXT-SESSION.md` at the repo root. First thing every AI session reads. Contains traps, current priorities, and what just shipped.

---

## Lessons (read these before adopting)

- **Dos and Don'ts** — [`06_dos_and_donts.md`](06_dos_and_donts.md) — 10 rules each, with the real incidents that produced them.

## Porting the Pattern

- **Bootstrap Checklist** — [`07_bootstrap_checklist.md`](07_bootstrap_checklist.md) — first 10 files to create on a new project.
- **Templates** — [`templates/`](templates/) — copy-paste starters for the two anchor docs, session handoff, and the verifier framework.

---

## One-Minute Summary

| Piece | File | Purpose |
|---|---|---|
| Narrative anchor | `docs/<NAME>_WHAT_IT_IS.md` | *What is this system?* — read-once conceptual doc |
| Runtime anchor | `docs/<NAME>_INVENTORY.md` | *What exists right now?* — regenerable, authoritative |
| Drift verifier | `core/services/doc_claim_verification.py` + CLI | Finds stale claims automatically |
| Topic docs | `docs/topics/<subsystem>.md` | Embeddable deep-dives, one per subsystem |
| Handoffs | `docs/handoffs/SESSION_####_*.md` | Build history, one per session |
| Entry point | `00-START-NEXT-SESSION.md` (root) | Where every session begins |

Single principle: **runtime wins**. If a number is in a hand-written doc and the verifier says it's wrong, the verifier is right. Fix the doc, or tag it with a pointer header and move on.
