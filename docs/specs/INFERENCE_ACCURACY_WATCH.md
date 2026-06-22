---
title: "Inference Accuracy Watch — 7-day spot-check protocol for the §6.2 cascade"
status: active
session: 1198
generated: 2026-06-22
last_reviewed: 2026-06-22
author: claude (with rigby's §6.2 design memo as input)
companion_docs:
  - INITIATIVES_FIRST_BACKBONE.md            # spec — §6.2 is the cascade source
  - ../handoffs/SESSION_1198_INFERENCE_CASCADE_AND_BASELINE_FIX.md  # what shipped
window:
  starts: 2026-06-23
  ends: 2026-06-30
seeded_agents:
  - ResearchAgent  → Spider Context Utilization — Retune & Implementation (3b)
  - ClaudeCode     → Initiatives-First Wiring + No-Orphan Output (spine 1)
---

# Inference Accuracy Watch — 7-day window starting 2026-06-23

> **What this doc is for.** The Session 1198 §6.2 inference cascade shipped 2 static affinity seeds. Before promoting Step 4 heuristics (PR3) or adding more seeds, we need to confirm the existing seeds are firing correctly. This doc is the operational protocol for that watch — what to sample, what "precision" means, what thresholds trigger seed adjustments.
>
> **Audience.** Operator running the daily checks. Decision is recorded at Day 8 (2026-06-30).
>
> **Bound to** spine Initiative `6941372d-b13c-4631-91c8-749fa65c55a0` (Initiatives-First Wiring + No-Orphan Output) — this watch validates a milestone of that Initiative's arc.

## 1. What to sample

**Daily intake — grep the log channel:**

```bash
# Total inference matches in the last 24h
grep "INFERENCE-MATCH" celery.log | wc -l

# Per-agent breakdown (which seeds are firing)
grep "INFERENCE-MATCH" celery.log | grep -oE "agent=[A-Za-z]+" | sort | uniq -c

# Per-step distribution (Step 1 doesn't log; Step 3 is the interesting case)
grep "INFERENCE-MATCH" celery.log | grep -oE "step=[0-9]+" | sort | uniq -c
```

**Notes on log channel:**

- Step 1 (`explicit_match`) does **NOT** emit `[INFERENCE-MATCH]` — it's a no-op pass-through when the caller provides `initiative_id`. Only Step 3 attachments hit the log.
- Step 5 fall-throughs are visible via Plan C's `[ORPHAN-DELIVERABLE]` log line (separate channel — see Session 1195 PR #2407).
- Cross-check the two channels to estimate inference coverage: if `[INFERENCE-MATCH]` count is N and `[ORPHAN-DELIVERABLE]` count is M, then inference is rescuing N / (N + M) of the orphan-bound creates.

**Spot-check sampling — 5–10 events per day:**

```bash
# Pull the most recent 10 matches with full context
grep "INFERENCE-MATCH" celery.log | tail -10
```

For each sampled match, pull the Deliverable + the inferred Initiative:

```python
.venv/bin/python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
django.setup()
from core.models_deliverables import Deliverable
d = Deliverable.objects.filter(initiative_id='<inferred_initiative_id>').order_by('-created_at')[:5]
for row in d:
    print(f'{row.id}  {row.created_at:%Y-%m-%d %H:%M}  agent={row.agent_name}  title={row.title[:80]}')
"
```

## 2. Precision definition

Each sampled event gets one of three labels:

| Label | Criteria | Counts as |
|---|---|---|
| **Correct** | The Deliverable is genuinely about the inferred Initiative's domain — a reasonable operator would have linked it there explicitly | precision numerator |
| **Ambiguous** | The Deliverable could fit multiple Initiatives; the inferred attachment is "fine, not best" — operator says "I wouldn't have flagged it, but I might have picked differently" | precision numerator (counts as correct for the watch) |
| **Incorrect** | The Deliverable is about something the seed wasn't designed for; attachment is semantically wrong | precision *denominator only* |

**Precision = (correct + ambiguous) / total sampled.**

**Reason ambiguous counts as correct:** the alternative is Plan C orphan-marking, which is worse for attribution. A "fine, not best" link is better than no link.

## 3. Action thresholds

| Observed precision | Action |
|---|---|
| **≥ 80%** | Keep the seed as-is. This is the success target. |
| **60–80%** | Investigate the incorrect cases. Usually one of: (a) confidence floor too low (tighten to 0.93+ on the affinity row); (b) seed too broad (split into multiple Initiatives via more granular agent_name matching — rare given coarse agent grain); (c) recency floor not catching stale initiatives (verify `updated_at` is fresh on the target). |
| **< 60%** | Pull the seed via soft-disable: `AgentInitiativeAffinity.objects.filter(agent_name='X', source='static_seed').update(expires_at=timezone.now())`. Row preserved for forensics. Agent is too broad for static affinity → needs Step 4 heuristics (PR3 trigger). |

## 4. Per-seed expected behavior (baseline)

| Seed | Expected match count/week | What "correct" looks like |
|---|---|---|
| ResearchAgent → Spider Context Retune (3b) | 5–15 matches | Research outputs about spider data, agent/category mapping, vocabulary fixes, retune iterations |
| ClaudeCode → Initiatives-First Wiring (spine 1) | 10–30 matches | Code/PR/migration/recon work on the backbone (Plan C, kind enum, inference, etc.) |

**If ClaudeCode matches drop below 5/week**, that means initiative_id is being passed explicitly more often (good — Step 1 short-circuits and `[INFERENCE-MATCH]` does NOT log). Not a precision failure. Cross-reference with Deliverable.objects.filter(initiative_id=spine_1_id, created_at__gte=...) to see total attaches vs inferred attaches.

## 5. Sample-record schema

Each day, the operator records a structured entry. Suggested format:

```
2026-06-23
  Total INFERENCE-MATCH lines: 8
  Per-agent: ResearchAgent=3, ClaudeCode=5
  Sampled: 4 events
    [d_xxx] ResearchAgent → 3b Retune: correct (spider data analysis)
    [d_yyy] ClaudeCode → spine 1: correct (Plan C Phase 2 follow-up)
    [d_zzz] ResearchAgent → 3b Retune: ambiguous (general spider work, could've gone to investigation)
    [d_www] ClaudeCode → spine 1: correct (kind enum docs update)
  Day precision: 4/4 = 100%
```

Record these as appends to the bound deliverable (linked via `rel:related_to:` to spine Initiative 1) so the watch trail stays attached to the work.

## 6. End-of-week decision (Day 8 — 2026-06-30)

Aggregate the daily precision values into a single decision per seed:

| Outcome | Decision |
|---|---|
| Both seeds precision ≥ 80% | Keep both. Move PR3 (Step 4 heuristics) into active scope. |
| ResearchAgent ≥ 80%, ClaudeCode < 60% | Pull ClaudeCode seed (too broad). Keep ResearchAgent. Watch ResearchAgent for another week. |
| ResearchAgent < 60%, ClaudeCode ≥ 80% | Same as above, mirrored. |
| Both < 60% | Pull both. Revisit §6.2 design — affinity-map approach may be wrong for this workload. Loop Rigby for a Phase 2 design rethink. |

File the decision as a follow-up deliverable in Donkey Betz workspace linked to spine Initiative 1. Include:
- Daily precision values (7-row table)
- Sampled events with labels
- Decision rationale + next action
- Tag the deliverable `session-1198-watch-result` for grep-ability

## 7. Adding new seeds during the watch

**Don't add new seeds before Day 8.** Adding mid-window pollutes the precision signal. If a top-orphan-creator obviously needs seeding (e.g., a new Rigby workflow that picks up a clean target Initiative), file a deliverable and defer the add to the post-watch decision.

Exception: if a seed is producing < 60% precision in the first 3 days AND the operator can identify a confidence/recency adjustment that should fix it without changing the target Initiative, that's an in-watch tweak (not a new seed). Document the tweak in the daily record.

## 8. Soft-disable command reference

For pulling a seed without deleting the row (preserves forensics):

```python
.venv/bin/python -c "
import django, os
from django.utils import timezone
os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
django.setup()
from core.models_inference import AgentInitiativeAffinity
n = AgentInitiativeAffinity.objects.filter(
    agent_name='<AgentName>',
    source='static_seed',
).update(expires_at=timezone.now())
print(f'Soft-disabled {n} row(s)')
"
```

For re-enabling later (clear the TTL):

```python
AgentInitiativeAffinity.objects.filter(agent_name='X', source='static_seed').update(expires_at=None)
```

## 9. Provenance

- Drafted Session 1198 close, post-merge.
- Design inputs: Rigby's §6.2 design memo on `pa-ea12236c83eb4826` + Rigby's offered checklist framing.
- Cascade implementation: PRs #2425-#2429 (model + seed + cascade + factory hook + tests).
- Spine Initiative this watch validates: `6941372d-b13c-4631-91c8-749fa65c55a0` (Initiatives-First Wiring + No-Orphan Output).
