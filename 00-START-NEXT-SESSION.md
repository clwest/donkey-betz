# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2818 CLOSED (afternoon close 2026-07-18; picks up as S2819) — **DISCOVERY-LAYER PILOT SHIPPED WITH LIMITATION**

**Refreshed 2026-07-18 afternoon (SESSION 2818 CLOSED — first post-Group-2700-arc-close session. Executed 2799 §8 item #1 as a discovery-layer authority-boost pilot for `docs/PLATFORM_INVENTORY.md`. Feature PR #3253 (`90ab139a9`, +372 LOC across 3 files). Primary success criterion met (T3 C5 fixed — counts queries now surface PLATFORM_INVENTORY.md#1/#2/#3); ships with documented known regression on non-counts how-to queries (result-set monoculture: 59 chunks × per-chunk bonus floods ranker on weak-overlap queries). Chris ratified ship-with-limitation path; Shape C query-intent gating queued as next arc. **EIGHTH-CONSECUTIVE OP3 TRIGGER — first in pilot-shape session, extends Group 2700 S2811-S2817 7/7 audit-shape streak into cross-shape generality evidence.** SIXTY-SECOND close-cycle post-PLAYBOOK-7.4.4.**

**S2818 ship (1 feature PR + 1 close cascade PR, both merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Discovery-layer authority-boost pilot (2799 §8 item #1) | **#3253** · `90ab139a9` | main | `core/rag.py` (mod), `core/tests/test_rag_authority_boost_2818.py` (new), `docs/research/implementation/RATIFICATION_2026-07-18_s2818_...md` (new envelope) |
| Close cascade | **#TBD** · (SHA at merge) | main | handoff + start-here + pin rotation + docs pipeline |

**Handoff:** `docs/handoffs/SESSION_2818_DISCOVERY_LAYER_PILOT.md`
**Envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md` (frozen at merge per PLAYBOOK-6.10.9)
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 114 rows unchanged this session (ledger appends deferred to Shape C arc where new folds become concrete triggers).

**Arc state at S2818 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817). Follow-on queue advancing: **item #1 SHIPPED** (with limitation); Shape C follow-on now #1 in queue.

---

## S2819 CANDIDATES — SHAPE C IS TOP OF QUEUE

### ⭐ Chris-ratified next arc (from S2818 envelope §6)

1. **⭐ Shape C — query-intent gating** (recommended default). Direct next iteration of S2818 pilot. Smallest next mechanism: add count-intent heuristic (regex on "how many" / "count of" / "total" / "number of" / etc.) as a gate around `_authority_bonus` invocation in `core/rag.py`. Success criterion: Q1-Q4 counts queries still return PLATFORM_INVENTORY.md in top-3 AND Q5 "add a new spider to the network" returns `docs/topics/spider-network.md` to top-3 (the T3 B1 intended target). Same 5-query batch as S2818 pre/post measurements — direct comparison possible.

### From 2799 §8 remaining queue

2. **HIGH-DRIFT rule canonicalization** (Rules #4/#5/#14 per T6) — pilot MQ-T6-8 actionable standard on S1300 §3F (genuinely stale). MEDIUM scope.
3. **Playbook v0.9 amendment (OP3 codification)** — 8/8 triggers now including S2818 first cross-shape datapoint. Well past codification threshold.
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

### Non-2700/non-Colorado

- **BettingPage first-user trace**
- **Stock Intelligence** — end-to-end verify

**Recommended default:** Shape C. It closes the loop on S2818's known regression before compounding more discovery-layer work; Chris explicitly ratified it as this pilot's follow-on; substrate is fresh in context; same measurement batch reusable for direct pre/post comparison.

---

## SESSION PIN — S2818 RETIRED (fresh mint required at S2819 open)

**Pin history (S2818):**

- `pa-43db3c9851764ee7` (label `s2818-discovery-layer-pilot`) minted at S2818 open; **retired at S2818 close (`force=true`, forty-ninth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2819 first-action fresh mint.

**S2819 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2818 handoff — §3 (novel-precedent — first pilot-shape OP3 + first measured-regression ratification), §5 (ledger + provenance), §6 (candidates for S2819)
# If continuing Shape C: also read S2818 envelope §5 (Limitations) + §6 (Follow-On Queue)

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

python manage.py session_lifecycle open --label s2819-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2818 lessons to carry:**

1. **Static per-chunk magnitude on token-overlap RAG scorers is a compromise, not a solution.** PLATFORM_INVENTORY.md's 59 chunks × per-chunk bonus flooded the ranker at both +20 and +8. This ceiling is architectural — attempting further static-magnitude tuning is empirically closed.
2. **OP3 empirical monoculture finding required post-authoring measurement** — open SIGN could not have surfaced it. Reinforces OP3 cross-shape value beyond audit sessions (first pilot-shape trigger).
3. **Ratification of measured regressions is a valid pattern.** Envelope §5 Limitations codifies the trade-off explicitly rather than hiding it. Makes the follow-on well-motivated.
4. **Rigby stop-condition prevented open-ended magnitude iteration.** When +8 failed the same criterion +20 failed, the escalation path fired immediately.
5. **`make celery-recycle` between measurement iterations is clean** — no session freshness drift between +20 and +8 measurements; workers picked up code in both cycles.
6. **Twin-pointer deliverable for pilots** — envelope in `docs/research/implementation/` + optional workspace mirror. S2818 workspace mirror deferred pending workspace-scoped ratification decision (pilots have lighter-weight workspace footprint than arc-scoped envelopes).

---

## Twin-pointer card

📁 **Repo — S2818 artifacts:**

- **Feature PR (1, merged):** #3253 (S2818 authority-boost pilot · `90ab139a9`)
- **Close cascade PR:** #TBD (SHA at merge)
- **Substrate changes:** `core/rag.py` (mod), `core/tests/test_rag_authority_boost_2818.py` (new), `docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md` (new envelope)
- **Handoff:** `docs/handoffs/SESSION_2818_DISCOVERY_LAYER_PILOT.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session)
- **Merge SHA:** `90ab139a9` (feature) → close-cascade SHA filled at merge

🖥️ **Workspace UI — S2818 has NO twin-pointer workspace deliverable this session** — pilots with `authority: ratification-record` in `docs/research/implementation/` are already discoverable via the envelope's frontmatter; separate workspace mirror deferred per lighter-footprint pilot pattern. Group 2700 arc's workspace deliverable (`37d6ca76-89c3-4966-8f4c-decc52ce8169`) remains authoritative for the whole /docs/ restructuring arc; this pilot is a §8 item execution under that arc.

---

## Current repository state (S2818 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2818 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment 8/8 corroborated across shapes**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | **ARC CLOSED (S2817).** §8 follow-on queue item #1 SHIPPED at S2818 with documented limitation. Shape C queued as next arc from envelope §6. |
| Emergent candidates | Shape C intent-gating (top); Playbook v0.9 amendment (8/8); remaining 2799 §8 items |
| Session pin | `pa-43db3c9851764ee7` (retired at S2818 close, force=true, forty-ninth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2819 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2818 open |
| Recycle log | `logs/recycle_events.jsonl` — +2 in-session iterations (+20 tune / +8 tune) + 1 post-merge recycle + 1 close-cascade recycle to come |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session) |
| /docs/ restructuring | **ARC CLOSED (S2817).** Item #1 SHIPPED at S2818. Item #1 follow-on (Shape C) at top of S2819 queue. |
| Next move | Chris picks direction at S2819 open — Shape C is Chris-ratified default from S2818 envelope §6 |

---

## Recommended session-open protocol (S2819, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2818 handoff §3 + §6
4. **If continuing Shape C (default):** read S2818 envelope §5 (Limitations — regression concrete evidence) + §6 (Follow-On Queue) for design context
5. Sanity checks (brew postgres + ledger 114 verify)
6. `git log --oneline -5` — should show S2818 feature + cascade + S2817 chain
7. **Chris picks direction** — Shape C is default; can override to Colorado / non-2700 / other
8. Mint fresh pin scoped `s2819-<Chris's-direction>`
9. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
10. Route scope through Rigby joint SIGN before authoring
11. **For any implementation-shape work:** OP3 two-SIGN pattern (8/8 across shapes now; Shape C is another pilot-shape → tenth cross-shape datapoint)
12. **UPPER BOUND / precision qualifiers** required for count claims
13. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
14. **Anchor-verify at every scope decision point** (16-session trend)
15. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2819:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2818_DISCOVERY_LAYER_PILOT.md`](docs/handoffs/SESSION_2818_DISCOVERY_LAYER_PILOT.md) — **S2818 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md) — **pilot envelope with empirical evidence + §5 Limitations + §6 Follow-On for Shape C**
4. [`core/rag.py`](core/rag.py) — mechanism landing (AUTHORITY_FILE_BONUS + `_authority_bonus`)
5. [`core/tests/test_rag_authority_boost_2818.py`](core/tests/test_rag_authority_boost_2818.py) — test scaffolding for Shape C to extend
6. [`docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`](docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md) — Group 2700 arc-close deliverable; §8 follow-on queue
7. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3 C5 source evidence for the pilot
8. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — arc process framework (v2)
9. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 amendment 8/8 corroborated including cross-shape)
10. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2818 close (unchanged this session)
