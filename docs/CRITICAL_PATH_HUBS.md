# Critical-Path Hub Files

**Created:** Session 1223 (2026-06-23) — audit #4 close from deliverable `bec077ed-…`.
**Status:** active.
**Anchor type:** convention doc (not a counts source).

> A file qualifies as a **critical-path hub** when (a) it has a high import/reference count across `core/` and `ai_core/`, AND (b) a refactor mistake there can break the whole platform — not just one feature. This doc names the four files that currently meet that bar, and the lightweight gate (header marker + PR template checklist) that protects them.

---

## The four hubs

| File | Role | Why critical |
|---|---|---|
| `core/agent_router.py` | Deterministic agent routing (`AGENT_MAP` lives here) | Every agent dispatch in the platform flows through here. Breaks → no agent runs. |
| `core/services/openai_client_factory.py` | Canonical OpenAI client factory (`get_openai_client`, `get_async_openai_client`, `apply_reasoning_guard`) | Every OpenAI call flows through here. Breaks → no LLM dispatch + Session 1216 Phase E reasoning-guard contract bypassed. |
| `core/celery.py` | Celery app config + beat schedule definitions | Every scheduled task + worker config flows through here. Breaks → no background work, no beat. |
| `core/services/tool_dispatcher.py` | PA tool handler registry (`152` registered handlers) | Every Rigby tool invocation flows through here. Breaks → PA loses all tool access. |

## The gate

Two-layer, low-friction:

1. **Header marker** at the top of each file:

   ```python
   # CRITICAL_PATH_HUB — see docs/CRITICAL_PATH_HUBS.md
   # Changes here can break the whole platform. Request Chris review before merge.
   ```

   This makes the status visible to anyone reading the file (or to an LLM-driven refactor scanning the file head).

2. **PR template checklist** activates conditionally — see `.github/PULL_REQUEST_TEMPLATE.md` § "Critical-path hub change checklist". A 4-item checklist that asks the author to (a) name what they changed, (b) confirm Chris-review, (c) name the rollback lever, (d) name the post-merge verification.

## Promotion / demotion

A file should be **added** to this list when its import-count crosses ~50 references and its blast-radius is platform-wide (vs feature-local).

A file should be **removed** when (a) its responsibility has been split across multiple files, OR (b) the platform no longer routes through it (e.g., the new dispatch is a parallel path that supersedes the old).

Changes to this list itself are also a critical-path-hub change — the registry is what makes the gate work. Update via PR with the checklist filled out.

## Related conventions

- **Narrative-edit checklist** (`docs/narratives/EDITING_GUARDRAILS.md`, Session 1159): protects the `docs/narratives/` corpus from voice/precision drift. Different protection target (precision of language vs. structural correctness of code), same lightweight-gate pattern.
- **Reasoning-contract guard** (`core/services/openai_client_factory.py` itself, Session 1216 Phase E): runtime + AST-lint protection on the reasoning-model contract. The hub gate adds an additional layer of human review on top of that machine-enforceable check.

## Audit lineage

This convention closes finding **#4** ("Silently load-bearing hub files unmarked / unguarded") from Session 1217 self-directed audit deliverable `bec077ed-d89e-4c7c-935e-f06eefad7bec`. Original framing:

> 4 hub files are high-risk but have no explicit critical-path safeguards. A single refactor mistake can break the whole platform. Add `CRITICAL_PATH_HUB` markers + PR template requirement for Chris review on changes to these 4 files. **Effort: M**.

Reference counts at time of audit (Session 1217, 2026-06-23):
- `core/agent_router.py` — ~205 refs (Rigby's audit) / 113 imports verified Session 1223 (narrower grep, same order of magnitude)
- `core/services/openai_client_factory.py` — ~103 / 108
- `core/celery.py` — ~117 / 47
- `core/services/tool_dispatcher.py` — ~57 / 35

Exact ref counts will drift; the qualitative status ("hub file, platform-wide blast radius") is the binding criterion, not the number.
