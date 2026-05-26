---
title: "Case Study: Dropping a Fresh AI Into a Complex System (and It Didn't Break)"
status: historical
originating_session: pre-1100 (Codex audit) — relocated Session 1160 (2026-05-26)
provenance_confidence: HIGH
provenance_note: Case-study writeup of a fresh Codex instance auditing the u-d-b repo using context-kit as its sole orientation mechanism. The findings section captures claims that were true at the time the audit ran. Some have been corrected since; see the "What's still true / what changed" block below. Session 1143 originally moved this from `docs/case-studies/` to `docs/reports/`; Session 1160 moved it back per Rigby's Session 1159 review (the doc is a case study with time-bound counts, not a runtime report). Treat `PLATFORM_INVENTORY.md` as the canonical counts source — this document is historical narrative, not runtime truth.
companion_docs:
  - docs/PLATFORM_INVENTORY.md
  - docs/narratives/EDITING_GUARDRAILS.md
---

> **Historical case study — not canonical runtime truth.** This
> doc was written when a fresh Codex instance audited the
> repository. The audit's findings about system counts, env
> templates, and tracked artifacts reflect the repository's state
> at the time of writing, not the current state. For current
> system counts (agents, spiders, services, tasks, models), see
> [`PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md). The value
> of this document is the narrative — how a context-kit-guided
> audit unfolds — not the specific numbers.

---

## What's still true / what changed since this was written

| Claim in the original audit | Status as-of 2026-05-26 |
|---|---|
| `README.md` reports 74 agents | Outdated — current count in `PLATFORM_INVENTORY.md` (sole authoritative source). |
| `docs/BACKEND_REFERENCE.md` reports 72 agents | Outdated — same fix. |
| `docs/topics/README.md` refers to 76 agents | Outdated — topic docs were corrected in Session 1158's drift sweep. |
| Conflicting count claims across docs | **Still true conceptually**, though now mitigated: per `DOC_LIFECYCLE §2c`, `PLATFORM_INVENTORY.md` is the sole authoritative counts source, and `docs/narratives/EDITING_GUARDRAILS.md` (Session 1159) codifies "counts as snapshots, not contracts." |
| `.env.example` had wrong `DJANGO_SETTINGS_MODULE` | The original audit text actually noted that `.env.example` matched the runtime in `manage.py` / `core/asgi.py` / etc. — the doc's headline phrasing is misleading; treat the body text as canonical. |
| Celery ownership reconciliation | **Resolved.** `core/celery.py` is the primary static beat definition source; `django-celery-beat` owns runtime `PeriodicTask` rows; sync/bootstrap commands materialize/repair selected rows. Session 1157 PR #2243 closed the underlying footgun. |
| Multiple overlapping env templates (`.env.example`, `.env.railway`, `.env.production`) | Still present; this is intentional fleet/Railway shape. Treat as background context, not as audit-actionable. |
| Tracked `venv_ml/` and `frontend/dist/` artifacts | **Worth re-checking** in the next disk-cleanup cycle. Session 1158 ran a major disk-pressure cleanup; build artifacts may have been deleted or .gitignore'd since. |
| `ai_core/activate_income_now.py` hardcoded local path + legacy settings | **Likely unchanged**; queued under the "Decision Command backend cleanup" Chris-call carryover. |

---

## Context

This repository was audited by a fresh Codex instance with zero prior knowledge of the codebase.

That matters because the repo is not small, and it is not simple. It spans multiple runtimes, multiple subsystems, and a very large documentation surface. The first challenge was not "what to fix" but "what is real."

For that reason, `context-kit` was the only orientation mechanism used to build an initial system map. In this repository, that is not optional. The documentation layer is intentionally large and persistent, so a new agent has to distinguish between:

- Active runtime truth: the authoritative state of code and configuration
- Archived or historical documents: valuable, but not authoritative for current behavior

This is not clutter. This is a historical memory layer.

## What context-kit Provided

`context-kit inspect` gave the audit a grounded system map before any conclusions were drawn. It identified:

- The primary stack: Python + Django
- The major subsystems: `core/`, `ai_core/`, `frontend/`, `mobile/`, `resolve_node/`, `docs/`, `tests/`, and archives
- The runtime entrypoints: `manage.py`, `Procfile`, and `Dockerfile`
- High-risk signals: a tracked virtualenv, large static assets, multiple env templates, and tracked build artifacts

That first pass mattered because it replaced assumption with structure.

`context-kit hotpath` then made the risk surface explicit by ranking the largest tracked files and surfacing the biggest context offenders. Combined with the canonical docs anchors, this prevented drift in two ways:

- It kept the audit anchored to real files instead of broad memory
- It exposed where the repository's narrative had diverged from its runtime state

The separation between `PLATFORM_WHAT_IT_IS` and `PLATFORM_INVENTORY` was especially useful:

- `PLATFORM_INVENTORY` acted as the runtime-derived snapshot
- `PLATFORM_WHAT_IT_IS` explained the system conceptually and documented its live interpretation

That separation made it possible to audit the repo without collapsing historical narrative into current truth.

## What Codex Did

The audit followed a concrete sequence:

1. Ran `context-kit inspect` to map the repo structure.
2. Checked the root manifests and startup entrypoints to identify the real runtime boundary.
3. Sampled the canonical docs and inventory files to understand how the repository describes itself.
4. Compared docs claims against runtime config and entrypoints.
5. Looked for duplication, dead code, and stale or misleading instructions.
6. Prioritized findings by impact, not by volume.

The important part is that the process stayed anchored to files and execution paths. It did not try to "understand the project" in the abstract. It asked: what does the repository actually do, and where does the documentation stop matching that behavior?

## Key Findings

### 1. Conflicting system counts across docs

The repository contains multiple live-sounding descriptions of the platform that disagree on core counts:

- `README.md` reported 74 agents and 77 spiders
- `docs/BACKEND_REFERENCE.md` reported 72 agents
- `docs/topics/README.md` referred to 76 agents
- `docs/PLATFORM_INVENTORY.md` and `docs/PLATFORM_WHAT_IT_IS.md` reported 83 agents and 80 spiders

Why this matters:

- A new AI agent can easily anchor to the wrong number and propagate it into future reasoning
- Count drift is not cosmetic here; it changes how the system is interpreted
- In a doc-heavy repository, inconsistent counts become compounding context drift risk

### 2. Incorrect `DJANGO_SETTINGS_MODULE` in `.env.example`

`[.env.example](/Users/donkeyking/development/unified-donkey-betz/.env.example)` sets `DJANGO_SETTINGS_MODULE=core.settings`, matching the runtime in `manage.py`, `core/asgi.py`, `core/wsgi.py`, and `core/celery.py`.

Why this matters:

- A developer following the example would start from the wrong settings module
- That creates avoidable onboarding friction and misdiagnosis
- The mismatch is especially dangerous because it looks authoritative

### 3. Celery ownership had to be reconciled

The active Celery docs now agree on the current model: `core/celery.py` is the primary static beat definition source, `django-celery-beat` owns the runtime `PeriodicTask` rows, and sync/bootstrap commands materialize or repair selected rows. `core.settings` only carries Celery routing and scheduler configuration.

Why this matters:

- This is a direct runtime instruction conflict
- An AI agent using the wrong doc could reason about the wrong source of truth
- When docs contradict config, the agent is not just misinformed; it is steered toward the wrong control plane

### 4. Multiple overlapping env templates

The repo contains several environment templates:

- `.env.example`
- `.env.railway`
- `.env.production`
- `.env.railway`

Why this matters:

- Overlapping templates increase the chance of picking the wrong one
- They carry different key names, different ports, and different deployment assumptions
- The result is context drift before runtime even starts

### 5. Committed build/runtime artifacts

The repository tracks both `venv_ml/` and `frontend/dist/`.

Why this matters:

- These are generated artifacts, not source
- Tracking them inflates the repo's surface area and blurs the source boundary
- For a fresh AI agent, they make it harder to distinguish authored code from build output

### 6. Machine-specific legacy script

`ai_core/activate_income_now.py` hardcodes a local filesystem path and uses a legacy settings module reference.

Why this matters:

- It is not portable
- It encodes one machine's path assumptions into the repo
- It looks like live tooling but behaves more like a historical artifact

## Critical Insight

In this system, documentation is not passive. It directly affects AI reasoning.

That means:

- stale docs can produce incorrect AI behavior
- contradictory docs compound drift over time
- repeated inconsistencies become part of the model's working context unless the repository clearly separates runtime truth from archive material

This is the core lesson from the audit: a document system that participates in AI orientation must be treated like part of the runtime, not like background prose.

## What Worked

The strongest signal from this audit is that Codex did not hallucinate its way through the repo.

It:

- used real files
- grounded itself in actual entrypoints and configs
- found concrete mismatches, not vague concerns
- prioritized findings sensibly, with no invented P0s

That is the value of `context-kit` here. It did not merely inform the agent. It constrained the agent's behavior.

## What This Proves

This repo shows that an AI can safely enter an unknown, complex codebase if it is oriented correctly.

`context-kit` functions as:

- an onboarding layer
- a grounding system
- an anti-drift mechanism

That makes it useful not only for humans reading the repository, but for AI agents that need to reason about it without prior memory.

## Cleanup Philosophy

The right way to treat a repository like this is not to erase history.

Instead, separate the layers:

- Canonical Truth Layer: runtime code, config, and inventory snapshots that reflect current behavior
- Historical Archive Layer: older docs, handoffs, and reports that preserve evolution and context

That means:

- marking stale docs as archived or historical when appropriate
- pointing summaries and onboarding docs to canonical sources
- keeping the historical record intact

The goal is not to remove knowledge. The goal is to make knowledge navigable.

## Final Takeaway

When systems become too large to reason about manually, they require structure not just for humans, but for the AI helping build them.
