# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2817 CLOSED (night close 2026-07-18; picks up as S2818) — **GROUP 2700 ARC CLOSED**

**Refreshed 2026-07-18 night (SESSION 2817 CLOSED — TWENTY-FIRST-consecutive same-day multi-ship session and NINE-CLOSE-CASCADE day: S2809-S2817 all closed 2026-07-18. **GROUP 2700 /docs/ RESTRUCTURING ARC CLOSED** with 2799 canonical summary (PR #3251 `4f67e9544`, +390 LOC). Twin-pointer discipline executed: repo doc + workspace deliverable UUID `37d6ca76-89c3-4966-8f4c-decc52ce8169` in Donkey Betz workspace via ORM-direct bypass of `pa_deliverables_tool` diagnostic-flag bug. Arc timeline: S2800 directive (2026-07-16) → S2801 parent → 14 Colorado sessions bumped → S2811-S2816 T1-T6 → **S2817 canonical summary (arc close, this session)**. 17 calendar sessions; 8 same-day arc-close sessions. **SEVENTH-CONSECUTIVE OP3 TRIGGER — 7/7 across ENTIRE arc.** 2799 §8 has 8-item follow-on queue for post-close migration + amendments. SIXTY-FIRST close-cycle post-PLAYBOOK-7.4.4.**

**S2817 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Group 2700 2799 canonical summary (arc close) | **#3251** · `4f67e9544` | main | `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` (+390 LOC, new) |

**Handoff:** `docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md`
**Twin-pointer deliverable:** UUID `37d6ca76-89c3-4966-8f4c-decc52ce8169` in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`)
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day).

**Arc state at S2817 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring — ARC CLOSED.** Parent ✅ + T1-T6 ✅ + 2799 ✅ + twin-pointer ✅. Migration executes post-close per 2799 §7+§8 in follow-up sessions.

---

## S2818 CANDIDATES — ARC CLOSED; SELECT FROM 2799 §8 QUEUE

### ⭐ From 2799 §8 follow-on queue (ranked by architectural uncertainty × risk × unblocked flows)

1. **⭐ Discovery-layer enforcement for DOC_LIFECYCLE §2c** — pilot 1-doc retrieval-weight boost for PLATFORM_INVENTORY.md; measure post-boost success@3 rate on T3 (c) scenarios. HIGH architectural leverage; addresses T3 C5 finding directly; smallest bounded scope (1-doc pilot with measurable outcome).
2. **HIGH-DRIFT rule canonicalization** (Rules #4/#5/#14 per T6) — pilot MQ-T6-8 actionable standard on S1300 §3F (genuinely stale). MEDIUM scope.
3. **Playbook v0.9 amendment (OP3 codification)** — 7/7 triggers over-corroborated; short-scope proposal-only arc.
4. **Parent §4 T5 clause update** per T5 MQ-T5-8 — requires Chris re-ratification per parent §5 Chris-lock. LOW scope.
5. **File moves per 2799 §3 target tree** — pilot `docs/adr/` → `docs/decisions/` (smallest scope + real convention collision per T3 B3).
6. **Per-handoff citation_health verification for S2500-2600 range** — 10-doc pilot.
7. **Retrieval-frequency telemetry design** — schema proposal for `search_docs` corpus.
8. **Generator/automation coordination for autogen output moves** (Rigby SIGN Q3 addition) — blocks 2799 §3.2 audit consolidation.

### Colorado / other (still queued)

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk)
- **Phase 4** — statute-citation content quality
- **Phase 5.1** — un-punt Session 534 spider AJAX
- **GPT fallback for form-selection** on low-confidence

### Non-Colorado / non-2700 arcs

- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** Item #1 discovery-layer enforcement — highest architectural leverage; smallest bounded pilot; directly addresses T3 C5's catastrophic finding (archived Oct 2025 morning report outranks canonical PLATFORM_INVENTORY.md for count queries).

---

## SESSION PIN — S2817 RETIRED (fresh mint required at S2818 open)

**Pin history (S2817):**

- `pa-fee015be9a424576` (label `s2817-group-2700-2799-canonical-summary`) minted at S2817 open; **retired at S2817 close (`force=true`, forty-eighth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2818 first-action fresh mint.

**S2818 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2817 handoff — §3 (novel-precedent), §6 (candidates)
# If continuing 2799 follow-on queue: also read 2799 §7+§8

# Sanity checks
brew services list | grep postgres

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2818-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2817 lessons to carry:**

1. **Group 2700 arc closed in ONE DAY** — parent + all children + canonical summary. First multi-child arc to close in a single day. Enabled by: OP3 two-SIGN pattern catching errors early, Rigby-as-first-class-evidence-source methodology, precision-qualifier discipline, sustained scope discipline (zero folds persisted).
2. **OP3 pattern is 7/7 across ENTIRE arc.** Empirically saturated across every possible session shape. Playbook v0.9 amendment WELL over-corroborated.
3. **Twin-pointer discipline executed live in-session** via ORM-direct bypass. Prior arcs deferred workspace deliverable to post-arc; S2817 created UUID `37d6ca76-...` during close cascade.
4. **Canonical summary is SYNTHESIS not re-audit.** Per Playbook §10 anti-scope: don't re-litigate T1-T6 evidence; don't create implementation plan; don't invent new taxonomies without anchors. 2799 respected all three per Rigby SIGN Q3 zoom-out.
5. **PROPOSED, not RATIFIED.** Rigby SIGN Q4 caught status framing risk. 2799 is PROPOSED pending Chris ratification. Migration executes only after ratification cycle.
6. **Compatibility-first for generator/runtime paths.** DOC_LIFECYCLE §2b + T2 FP-META HARD guardrail + 2799 §8 item #8 all interlock: no mass-move can proceed without per-PR verification that runtime-coupled + autogen invariants hold.

---

## Twin-pointer card

📁 **Repo — S2817 artifacts:**

- **PR (1, merged):** #3251 (2799 canonical summary · `4f67e9544`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` — new (+390 LOC)
- **Handoff:** `docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day)
- **Merge SHA:** `4f67e9544` (2799) → close-cascade SHA filled at merge

🖥️ **Workspace UI — twin-pointer deliverable:**

- **Donkey Betz workspace** (`b4503364-2573-4401-9e28-61a739e0ce50`) contains twin-pointer deliverable **UUID `37d6ca76-89c3-4966-8f4c-decc52ce8169`**
  - `deliverable_type: canonical_summary`
  - `category: research`
  - `diagnostic_status: (empty — ORM-direct bypass of pa_deliverables_tool bug)`
  - Discoverable via `deliverable_tool.list workspace_id=b4503364-...` OR ORM `Deliverable.objects.get(id='37d6ca76-...')`

---

## Current repository state (S2817 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2817 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment WELL past threshold — 7/7 OP3 triggers**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | **ARC CLOSED.** Parent ✅ / T1 ✅ / T2 ✅ / T3 ✅ / T4 ✅ / T5 ✅ / T6 ✅ / **2799 ✅** / twin-pointer ✅. Migration executes post-close per 2799 §7+§8. |
| Emergent candidates | 2799 §8 has 8-item follow-on queue; Playbook v0.9 amendment separate arc; parent §4 T5 clause update requires Chris re-ratification |
| Session pin | `pa-fee015be9a424576` (retired at S2817 close, force=true, forty-eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2818 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2817 open |
| Recycle log | `logs/recycle_events.jsonl` — +18 today across S2809-S2817 (2 per session) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day) |
| /docs/ restructuring | **ARC CLOSED.** Twin-pointer created. Migration queue queued for post-close sessions. |
| Next move | Chris picks from 2799 §8 follow-on queue OR Colorado / non-2700 candidates at S2818 open |

---

## Recommended session-open protocol (S2818, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2817 handoff §3 + §6
4. **If continuing 2799 follow-on queue:** read 2799 §7 (anchor updates) + §8 (queue) for prioritization context
5. Sanity checks (brew postgres + curl /health/ping/)
6. Freshness + ledger 114 verify
7. `git log --oneline -10` to see full day's PR run (18 PRs / 9 features/audits + 9 cascades)
8. **Chris picks direction** — see §S2818 CANDIDATES
9. Mint fresh pin scoped `s2818-<Chris's-direction>`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Route scope through Rigby joint SIGN before authoring
12. **For any arc-shape work:** OP3 two-SIGN pattern (7/7 across Group 2700; empirically saturated)
13. **UPPER BOUND / precision qualifiers** required for count claims
14. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
15. **Anchor-verify at every scope decision point** (15-session trend)
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2818:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md`](docs/handoffs/SESSION_2817_GROUP_2700_2799_CANONICAL_SUMMARY.md) — **S2817 handoff (current)**
3. [`docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`](docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md) — **arc-close deliverable; §7 anchor updates + §8 follow-on queue for post-close prioritization**
4. [`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`](docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md) — parent (Chris-locked S2801)
5. [`docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md`](docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md) — T1
6. [`docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md`](docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md) — T2
7. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3
8. [`docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md`](docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md) — T4
9. [`docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md`](docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md) — T5
10. [`docs/research/domains/docs_restructuring/2706_docs_anchor_drift_audit.md`](docs/research/domains/docs_restructuring/2706_docs_anchor_drift_audit.md) — T6
11. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — arc process framework (v2)
12. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 amendment WELL past — 7/7 OP3 triggers)
13. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2817 close (unchanged all day)
