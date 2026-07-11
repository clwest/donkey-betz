---
title: "Ops Health Tile v2 — SLO Summary Card Ratification Record (2026-07-11)"
status: active
authority: ratification-record
session_added: 2764
ratification_date: 2026-07-11
ratifier: chris
routing: rigby-pa-chat SIGN (freshness + design) + Chris candidate selection + local build + shell smoke test
scope: S2764 — N1: extend Ops Health tile with a third card summarizing SLO breach status
serves_arc: platform observability (Ops Console at Workspace → System → Ops)
precedent_ratifications:
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_health_tile.md (S2761 — original tile + health_summary composition pattern)
  - docs/research/implementation/RATIFICATION_2026-07-11_ops_sibling_401_fix.md (S2762 — sibling api.get pattern)
  - docs/research/implementation/RATIFICATION_2026-07-11_close_ceremony_ledger.md (S2763 — verify-before-build reuse discipline)
ratified_documents:
  - core/views_ops_console.py (amended — health_summary composition extended with slo_status via new _summarize_slos helper)
  - frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx (amended — OpsHealthSummary type extended, tile grid 2-col → 3-col, new SLO card)
head_at_ratification: (filled at merge)
merged_pr: (filled at merge)
sign_sessions:
  - S2764 open freshness check (fresh pin pa-4594e726e18e4ccf) — verdict FRESH · SHA 8785c312… matches HEAD (THIRD data point for recycle-after-merge rule; SECOND independent close-cycle since S2762)
  - S2764 design SIGN (Rigby) — PASS with target vs target_max direction risk called out; addressed via _summarize_slos direction guard
frozen: true
---

# Ops Health Tile v2 — SLO Summary Card Ratification Record

Frozen canonical record of Chris's ratification of the SLO summary card on 2026-07-11. Completes the S2761 tile's third-card slot with breach summary + worst-breach preview. Append-only.

---

## §1. Context

- **Ratification date:** 2026-07-11 (America/Denver operator timezone)
- **Scope:** last-mile UI extension (N1 in S2762 candidate menu, standing net-new proposal).
- **Motivation:** the S2761 tile already surfaced tenant-boundary + staleness counts at-a-glance. The `SLO Status (24h)` grid section below required visual scanning across up to 8 SLO cards to answer "is anything actively breaching?" This card compresses that answer to a single number + worst-breach preview at the tile level, matching the operator-glance discipline.
- **Ratifier:** Chris (candidate selection at S2764 open: "let's do N1 next")

---

## §2. Ratified Deliverables

### §2.1 `core/views_ops_console.py` — `health_summary` extension + `_summarize_slos`

The `health_summary` view now composes a fourth `_safe_call` for the `slo_status` action alongside the existing version + tenant-boundary + staleness dispatches. The list-shaped SLO handler response is reduced by a new module-level helper `_summarize_slos()` into a compact tile-friendly summary:

```json
{
  "slo_status": {
    "total": 8,
    "breach_count": 0,
    "healthy_count": 8,
    "worst_breach": {
      "key": "agent_task_success_rate",
      "name": "execute_agent_task success rate",
      "current": 0.987,
      "target": 0.9995
    } | null
  }
}
```

**Direction guard** (per §3 below): SLOs with `target` present are treated as lower-is-worse (breach gap = target - current); SLOs with `target_max` present are treated as upper-is-worse (breach gap = current - target_max). SLOs with neither, or with non-numeric `current`, are counted but excluded from worst-breach ranking. Errored SLO entries (`error` key present) do not contribute to totals.

**Fail-soft:** if `slo_status` `_handle_ops` raises, `_summarize_slos()` receives an error payload and returns the zero-state summary `{total: 0, breach_count: 0, healthy_count: 0, worst_breach: null}`. The overall endpoint still returns 200 with best-effort data — tile degrades gracefully rather than empty-stating.

### §2.2 `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — Ops Health tile 3rd card

- `OpsHealthSummary` interface extended with `slo_status` block (total / breach_count / healthy_count / worst_breach nullable).
- Tile grid `grid-cols-1 sm:grid-cols-2` → `grid-cols-1 sm:grid-cols-3`.
- New SLO card as 3rd position with `<Zap />` icon (previously unused import — now naturally referenced).
- Header: "SLO Breaches".
- Big number: `breach_count / total` (green when 0 / red when > 0).
- When `worst_breach` present: name + `current` (red, mono, %-formatted if < 1) + `target` (gray, mono, %-formatted if < 1) — 3-line breakdown matching sibling card patterns.
- The existing detailed "SLO Status (24h)" grid section below the tile is unchanged (S1077 code).

---

## §3. Direction Guard (§4.2 Rigby SIGN concern addressed)

Rigby's SIGN response flagged that SLO polarity is not uniform: some SLOs are lower-is-worse (`target` field, e.g. success rates where 99.9% is the floor), others are upper-is-worse (`target_max` field, e.g. timeout rates where 0.2% is the ceiling). A naive `abs(current - target)` gap would mis-rank; a naive `current - target` would give negative gaps on lower-bounded breaches.

`_summarize_slos()` handles both cleanly:

```python
if 'target_max' in s and isinstance(s.get('target_max'), (int, float)):
    gap = current - s['target_max']  # positive when breaching upper bound
    target_display = s['target_max']
elif 'target' in s and isinstance(s.get('target'), (int, float)):
    gap = s['target'] - current  # positive when below lower bound
    target_display = s['target']
else:
    continue  # skip from worst-breach ranking
```

Positive gap = "how far into breach territory." Worst breach = max positive gap. Ties resolve by iteration order (arbitrary but stable per SLO handler order).

**Verified via shell smoke test:** endpoint returns `slo_status: {total: 8, breach_count: 0, healthy_count: 8, worst_breach: null}` — matches the current healthy state; direction guard exercised only via unit-test-shaped inspection of the helper (breach path not currently triggered live).

---

## §4. Rigby SIGN

### §4.1 Freshness (S2764 open, pin `pa-4594e726e18e4ccf`) — THIRD corroboration point

`ops_tool.version` → **FRESH**, `head_commit_sha 8785c312…` matches HEAD of `main` (post-S2763 merge).

**Corroboration signal ladder for `feedback_recycle_after_merge.md`:**

| Cycle | Close event | Post-recycle verdict | Independent? |
|-------|-------------|----------------------|--------------|
| S2762 close | ran `make recycle-all` after PR #3151 merge | FRESH · SHA `7db82c84…` | data point 1 |
| S2763 open  | rechecked same-session after cycle | FRESH · same SHA | same cycle (S2762) |
| S2763 close | ran `make recycle-all` after PR #3152 merge | FRESH · SHA `8785c312…` | data point 2 |
| **S2764 open** | **rechecked same-session after cycle** | **FRESH · same SHA** | **same cycle (S2763)** |

**Now at 2 independent close-cycles, both showing FRESH.** One more from a differently-scoped arc (i.e. a non-Ops-Console close) will be sufficient to propose a Playbook §7.4.1 amendment adding "final `make recycle-all` step post-PR-merge" to the close-ceremony contract.

### §4.2 Design SIGN

**SIGN LEAN: PASS.** Rigby: "clean extension of the existing `health_summary` composition (same safe-call + fail-soft pattern), and frontend change is a straightforward 3rd card without touching the detailed SLO grid."

**Risk called out:** "worst_breach math can silently mis-rank if some SLOs are upper-bounded (`target_max`) vs lower-bounded (`target`) and the handler returns both (or neither) inconsistently — needs a small guard/normalizer so we don't compare apples to oranges or throw on missing fields."

**Response:** direction guard applied per §3 above.

---

## §5. Chris D-Verdict

Sequence:

1. **Session-open candidate selection:** "let's do N1 next" (picked N1 from S2762+S2763 standing candidate menu).
2. **Joint agreement:** no F-BLOCKING decisions surfaced; Rigby's direction risk resolved before code landed.
3. **Post-merge verify (pending):** browser hard-refresh Workspace → System → Ops to confirm the tile now shows 3 cards (Tenant Boundary / Staleness / **SLO Breaches**) instead of 2.

**Effect:** Ops Health tile now answers three glance-level operator questions in one row: "are tenant boundaries being violated?" · "are workers running stale code?" · "**are any SLOs currently breaching?**"

---

## §6. Verify-Before-Build

- **Existing patterns reused:**
  - `core/views_ops_console.py:87-131` — `health_summary` composition (extended by adding a 4th `_safe_call`, no new function).
  - `core/services/td_handlers_ops.py:243-247, 589+` — `_ops_slo_status` handler already existed; consumed here rather than re-implemented.
  - `frontend/src/pages/workspace/tabs/OpsConsoleTab.tsx` — tile grid + card pattern from S2761 tenant-boundary/staleness cards (mirror pattern into 3rd card).
- **What's new:** `_summarize_slos()` helper (single-purpose reducer + direction guard). Not a new abstraction — mirror of the existing "list of dict → single dict" reduce pattern already present in the ops surface.
- **Reuse/extend/correct verdict:** extend an existing view; reuse an existing handler; mirror an existing tile card pattern. No new module, no new API contract, no new data model.

---

## §7. Provenance Chain

- **Predecessor sessions:** S2761 (tile v1) → S2762 (sibling 401 fix) → S2763 (close-ceremony ledger) → **S2764 (tile v2 SLO card)**
- **Reference infra:** `core/views_ops_console.py:87-131` (composition), `core/services/td_handlers_ops.py:589+` (SLO handler), `frontend/src/lib/api.ts:13-40` (axios instance)
- **Engineering Playbook v0.5.0:** PLAYBOOK-7.4.1 (close-ceremony 1-PR bundle) + Cycle 1A verify-before-build applied (§6 above)
- **Memory rules applied:** `feedback_last_mile_ui.md` (browser-visible operator surface), `feedback_recycle_after_merge.md` (THIRD data point; SECOND independent close-cycle), `feedback_local_truth_no_production.md` (local build + shell smoke test = shipped), `feedback_claude_rigby_agree_first_chris_yes_no.md` (Rigby SIGN reached PASS with risk callout resolved before code landed)
- **Codification watch:** `feedback_recycle_after_merge.md` now has 2 independent close-cycle corroborations. Third independent arc-close → propose Playbook amendment.
