---
originating_session: 1159
provenance_confidence: HIGH
provenance_note: Hand-authored Session 1159 handoff. Two-arc session — PA task acks-late fix (carried over from overnight aborted work) + Rigby's batch B/C/D narrative review + EDITING_GUARDRAILS contract. Self-referential pattern: the review applied its own guardrails as it landed.
---

# Session 1159 — PA task acks + narrative B/C/D review + EDITING_GUARDRAILS

**Date:** 2026-05-26 (fifteenth back-to-back session, first post-Session-1158 corpus-narrative work)
**Branch state at session close:** All work merged. Main is clean. Three PRs landed.

---

## TL;DR

Session 1159 had two distinct arcs.

**Arc 1 (carryover from overnight).** Chris had cut a `fix/session-1159-pa-task-acks-late` branch the night before with a one-line `acks_late=False` change to `process_pa_chat_task` in `core/tasks.py`. Server issues forced a Mac restart before he could commit. The session opened with locating the uncommitted change, committing + pushing it, and full stack restart (Docker fleet + u-d-b daphne + celery) post-reboot.

**Arc 2 (the actual session).** Rigby's narrative B/C/D review queued from Session 1158 (worker hung mid-task back then) was retried successfully. All three came back **Template PASS / Voice PASS / Accuracy ITERATE** with the same root cause across files — brittle numeric thresholds, exact counts, model names, hash formulas, and timeouts treated as prose rather than as as-of snapshots of code. The review surfaced a new persistent artifact: **`docs/narratives/EDITING_GUARDRAILS.md`** — a 7-rule contract for every current and future narrative.

The follow-up loop (review → apply → verify → re-apply) demonstrated the EDITING_GUARDRAILS rules eating their own dogfood: PR #2256 added the guardrails *and* still left 4 violations of rules #1 and #5 that needed a second pass in PR #2257.

---

## What shipped

| PR | Theme | Merge SHA |
|----|-------|-----------|
| **#2255** | `acks_late=False` on `process_pa_chat_task` (production code, bypass with Chris-authorization) | `3a7e347c` |
| **#2256** | Narrative B/C/D iterations + new `EDITING_GUARDRAILS.md` | `d73f6824` |
| **#2257** | Narrative B/C/D follow-ups from Rigby's verification | `77c68c01` |

Three squash-merge commits to main, all via bypass-mode (GH Actions billing still down).

---

## PR #2255 — `acks_late=False` on `process_pa_chat_task`

### Context

Background: the global `CELERY_TASK_ACKS_LATE=True` plus an unstable macOS broker connection had been producing PA chat tasks that completed on the worker but failed to ack to Redis afterward. Tasks would sit in `unacked` until the broker's `visibility_timeout` (1 h), and the user saw a perpetually-spinning Rigby reply.

### Change

One line + a four-line comment in `core/tasks.py`:

```python
+# Session 1159: acks_late=False overrides global CELERY_TASK_ACKS_LATE=True for PA chat.
+# Global acks-late + unstable macOS broker conn → tasks complete but post-task ack drops →
+# stuck in `unacked` until visibility_timeout (1h). Acking on receipt is the right tradeoff
+# for chat: a lost message on worker crash is preferable to UI stuck waiting an hour.
+@shared_task(bind=True, time_limit=300, soft_time_limit=280, acks_late=False)
 def process_pa_chat_task(self, ...): ...
```

### Tradeoff named in the comment

For chat, acking on receipt > acking on completion: a lost message on a worker crash (rare, restartable, user just retypes) is preferable to a UI stuck waiting an hour (frequent under current broker conditions, and not visible as a failure).

### Bypass note

This was the only PR in the session that touched production code. The standard Session-1150 bypass protocol explicitly limits self-merge to docs / verifier-baselines (no production code changes). PR #2255 went through with **explicit Chris authorization in-session**, documented in the merge commit body. Future production-code changes during the CI-billing outage should follow the same pattern (explicit per-PR authorization + bypass note).

---

## PR #2256 — narrative B/C/D iterations + EDITING_GUARDRAILS

### What Rigby's review found

Per-narrative verdicts (all 3):
- Template: **PASS**
- Voice: **PASS**
- Accuracy: **ITERATE**

Same root cause across all three narratives — brittle specifics (numeric thresholds, exact counts, model names, hash formulas, timeouts) phrased as facts rather than as as-of snapshots of code.

### Per-narrative changes applied

**B — `CONTENT_PIPELINE.md`:**
- Hedge ClaimsPack ID formula → point to `ClaimsPackBuilder`, not inline `sha256(url+title)[:10]`
- Hedge PublishGate thresholds (0.75 / 0.60 / 0.55) → as-of + code-wins
- Treat bypass title prefixes as illustrative, not canonical
- Add §8 Canonical Sources block

**C — `SIGNAL_INTELLIGENCE.md`:**
- Convert pattern_type drift note → procedure ("enum wins; docs mentioning 7 are stale")
- Convert circuit-breaker threshold drift → procedure ("env wins; both 20 and 50 appear in docs")
- Document `data_type` vocabulary common failure (empty result on invented types like `market_alert`)
- Add §8 Canonical Sources block

**D — `PERSONAL_ASSISTANT.md`:**
- Add **Routing Truth** table to §5 — canonical request path + 6 debug entrypoints + legacy gate boundary
- Hedge GPT-5.2 / iteration cap / timeouts as configurable current values
- Soften "never inferred from text" → "should not be inferred; if observed, file regression"
- Add §8 Canonical Sources block

### New file — `EDITING_GUARDRAILS.md`

The headline artifact of the session. 7-rule editing contract distilled from Rigby's 8-category risk pattern:

1. **No bare numeric thresholds, timeouts, counts** — need pointers or as-of labels
2. **Model names are configurable** — not permanent truths
3. **Lists are illustrative + canonical home** — never duplicate enum/allowlist content
4. **Tool/API path for every UI step** — audience contract is operator-without-UI
5. **Soften absolutes** — "never", "always", "cannot happen" mask runtime edge cases
6. **Explicit legacy vs current boundaries** — every legacy mention needs three sentences (what, trigger, log signature)
7. **Counts as snapshots, not contracts** — capability descriptions beat exact numbers

Each rule has a **Why** line (the failure mode it prevents) and a **How to apply** line (concrete editor guidance). Applies to every current narrative and any future addition.

---

## PR #2257 — Rigby's verification follow-ups

After PR #2256 merged, sent Rigby a "verify the iterations landed" follow-up. She found 4 small under-hedges + 1 framing tweak:

**D (Routing Truth completions):**
- Add provider/Responses-API failure entrypoint (429s, 5xx, rate limits)
- Add iteration-cap entrypoint (output truncates after tool calls)
- Soften remaining "Should never happen now" absolute on the 134s context-build-hang bullet

**B (still under-hedged):**
- ClaimsPack 72-h window + 20-claim cap (sub-constants alongside the existing hash recipe)
- DomainPersona ≥ 0.2 threshold (bare numeric)

**C (still under-hedged):**
- §1 "80 sources" + "every 30 minutes" — now as-of-anchored with inventory + beat schedule pointers
- Strength/confidence/novelty formula weights → point to `SignalAggregationService.aggregate_signals()`

**EDITING_GUARDRAILS intro tweak:** "established the per-narrative template" → "introduced a typical per-narrative template" (acknowledges narratives don't all use the exact same section shape).

### The self-referential pattern

PR #2256 added the EDITING_GUARDRAILS contract *and* still violated rules #1 ("numbers need pointers") and #5 ("soften absolutes") in 5 places. The follow-up loop is the pattern the guardrails formalize: write → review → apply → verify → re-apply.

The lesson is that the rules are *easier* to write than to *internalize* — a single pass at narrative editing isn't enough; the review→re-apply cycle is load-bearing.

---

## Stack restart (post-Mac-reboot from overnight outage)

Pre-flight on Mac restart:
- Docker daemon was down; containers were stopped but their state survived.
- Stale pid files in u-d-b root (`.celery*.pid`, `.daphne.pid`) from previous session's shutdown.
- Disk: 77 GiB free (healthy, well above the disk-pressure threshold from Session 1158).
- Swap: fresh allocation pending (0.00M total post-reboot, as expected).

Restart sequence that worked:
1. `rm -f .celery*.pid .daphne.pid` — clear stale pids.
2. `open -a Docker` — launch Docker Desktop (1 s startup; containers auto-restarted from saved state).
3. `cd ~/development/infra && make udb` — start u-d-b natively (daphne + celery).
4. `make status` — verify 24 docker containers up + u-d-b daphne pid 2904 + celery pid 2981.

Total restart time: ~30 seconds from cold-Mac-boot to fully-functional stack.

---

## New PA conversation

Chris opened a new PA conversation `pa-f93d77e34f5d` for this session. Updated `tools/pa_local.sh` to thread it. Verification ran cleanly:
- Token `e3c7276f00f12b77bda365c7c186577cd854cf2a` → donkeyking
- Conversation `pa-f93d77e34f5d` → donkeyking (created today)
- `platform_config_tool overview` → `service_context: local` confirmed

---

## Lessons / observations

### NEW (1159) — `docs/narratives/EDITING_GUARDRAILS.md` is now load-bearing

Any narrative edit going forward should be reviewed against the 7 rules. Rules #1 (number pointers/as-of), #5 (soften absolutes), and #7 (counts as snapshots) are the highest-frequency violations.

### NEW (1159) — Self-referential dogfood

A guardrails-introducing PR can still violate the same guardrails it introduces. Plan for the follow-up loop; don't assume a single pass.

### NEW (1159) — Production-code bypass needs explicit per-PR Chris authorization

The Session-1150 bypass protocol is for docs/verifier-baselines. PR #2255 set the precedent for production-code bypass during the CI-billing outage: Chris explicitly authorizes in-session, merge commit body names the deviation.

### NEW (1159) — Stack restart playbook works in ~30 s

Post-reboot recovery is: clear pids → Docker → make udb. Tested today; documented above so the next session doesn't have to re-derive it.

### Carryover lessons still relevant

- **(1158)** Recon before sweep.
- **(1158)** Narratives become canon; topic docs get corrected to match.
- **(1158)** Disk + swap pressure mimics Celery bugs — check disk first.
- **(1150)** Local mirrors + bypass docs make self-merge safe during CI outage.
- **(1150)** "One mechanical batch then stop" — applies to docs work too.

---

## What's open going into Session 1160

### Still queued from Session 1158

1. **Reports cleanup mechanical pass** — `DOC-POINTER-V2 Superseded` on 9 Jan-21 docs; upgrade 2 V1 → V2; INDEX.md drift (30 → 33). Fully scriptable.
2. **Patents preservation + cross-linking** — `docs/patents/README.md` with workstream structure + narrative cross-link map; add provenance frontmatter to 16 patent files.
3. **The 783 → 778 not-HIGH untagged handoffs** — alternate treatment for handoffs not cited by Session 1158 narratives.
4. **Old `docs/topics/` sweep** — 7 Feb-March docs deferred from Session 1147 #2221.
5. **Cosmetic `load_all_agents_advisors.py 149→139` fix** — queued from Session 1149.

### Chris-call decisions still pending (from Session 1158)

6. **`docs/reports/donkey-betz-codex-audit.md`** — marketing material (keep) or experiment leftover (archive)?
7. **May 25 09:36 batch** (12 docs in `docs/reports/`) — what agent generated this batch?

### New from Session 1159

8. **PA acks_late observation window** — watch `pa` queue depth + UI behavior over 24-48 h to verify the acks_late=False fix actually resolves the perpetually-spinning Rigby symptom. No regression in worker crash recovery should be observed.
9. **Apply EDITING_GUARDRAILS to other narratives** — the contract was derived from B/C/D but applies to all 15 narratives. A/E/F/G/H/I/J/K/L/M/N/O have not been reviewed under the guardrails yet. Opportunistic, not batch — pick up when next editing each.

### Deferred infrastructure track (avoid during offline-CI window)

10. **`celery-beat-schedule` CONFLICT — detector signal cleanup** — context-kit detector heuristic still flags after Session 1157 closed the code-level footgun.
11. **Pre-existing 3-row PeriodicTask drift** (80 DB rows vs 77 entries in `core/celery.py`).
12. **`exists_on_disk: false` flag** in `_provenance.json` — schema bump v1 → v2.
13. **Beat-schedule the regens** — weekly Celery beat task for `_provenance.json` + 8 `build_*_audit` commands.
14. **Fix `build_learning_bridge_audit.py` generator** — falsely flags "ABC unused".
15. **Redis pooling sweep** — ~40 inline `redis.Redis.from_url(...)` sites.

### Chris-call-only carryovers

16. **Decision Command backend cleanup** — 5 Python files (regressed feature).
17. **DaVinci route removal** — `core/views_davinci.py` still routed.
18. **Mission refresh PR #2190** — preserved branch.

---

## Session telemetry

- **Duration:** ~3 h (10:30 – 13:30 local, includes the stack-restart arc + 3 PRs + handoff)
- **PRs merged:** 3 (1 production code, 2 docs)
- **Files changed across all 3 PRs:** 11 (1 code, 10 docs/index — counts include INDEX regenerations and `pa_local.sh`)
- **New persistent artifact:** `docs/narratives/EDITING_GUARDRAILS.md`
- **Disk pressure:** none (77 GiB free at open, no swap pressure, healthy throughout)
- **GH Actions billing status:** still down (multi-day outage, bypass mode active)
- **Pre-commit security checks:** passed on all 3 commits

---

## Source

- Rigby's Session 1159 internal-ops review memo (B/C/D + cross-narrative drift list + 8-category risk register + 5 next actions + 7 guardrails). Conversation `pa-f93d77e34f5d`.
- The 3 narrative files plus EDITING_GUARDRAILS.md (current state on main).
- `00-START-NEXT-SESSION.md` (priorities at session open, to be overwritten with Session 1160 entry).
