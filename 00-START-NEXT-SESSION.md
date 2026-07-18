# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2819 CLOSED (afternoon close 2026-07-18; picks up as S2820) — **SHAPE C INTENT-GATING SHIPPED**

**Refreshed 2026-07-18 afternoon (SESSION 2819 CLOSED — second same-day post-Group-2700-arc-close session; direct-continuation follow-on from S2818 pilot. Shape C query-intent gating for AUTHORITY_FILE_BONUS. Feature PR #3255 (`13844fc82`, +553 LOC across 4 files) closes the loop on S2818's documented non-counts monoculture regression while preserving both counts + "list all" behavior. **NINTH-CONSECUTIVE OP3 TRIGGER — first INITIAL-ESCALATE → RE-VERDICT-SHIP cycle** (Rigby's initial escalate was correct against my flawed success criterion; corrected framing produced ship). Two novel findings: (1) success-criterion hygiene gotcha (aspirational vs empirical target labels); (2) start-here doc self-contamination (S2819 wrote "add a new spider to the network" as example text; now that phrase retrieves 00-START). Both queued as S2820+ follow-ons. SIXTY-THIRD close-cycle post-PLAYBOOK-7.4.4.**

**S2819 ship (1 feature PR + 1 close cascade PR, both merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Shape C query-intent gating for AUTHORITY_FILE_BONUS | **#3255** · `13844fc82` | main | `core/rag.py` (mod), `core/tests/test_rag_intent_gating_2819.py` (new), `core/tests/test_rag_authority_boost_2818.py` (mod), `docs/research/implementation/RATIFICATION_2026-07-18_s2819_...md` (new envelope) |
| Close cascade | **#TBD** · (SHA at merge) | main | handoff + start-here + pin rotation + docs pipeline |

**Handoff:** `docs/handoffs/SESSION_2819_SHAPE_C_INTENT_GATING.md`
**Envelope:** `docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md` (frozen at merge per PLAYBOOK-6.10.9)
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — 114 rows unchanged (folds deferred to ledger append at next arc close per S2818 pattern).

**Arc state at S2819 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring — ARC CLOSED** (S2817). Follow-on queue: item #1 SHIPPED at S2818 + S2819 (2-session direct-continuation pilot chain). Discovery-layer arc has produced 2 pilots + 2 novel findings + 1 empirically-validated mechanism.

---

## S2820 CANDIDATES — 00-START CONTAMINATION FIX IS TOP OF QUEUE

### ⭐ Top of queue (novel from S2819 §5.2)

1. **⭐ 00-START-NEXT-SESSION.md self-contamination fix** (highest architectural leverage of remaining discovery-layer work). Concrete evidence: current Q5 top-1 = `docs/00-START-NEXT-SESSION.md#3` for query "add a new spider to the network" because S2819 candidate description mentions the exact phrase as example text. Same class as T3 §7 C2 pain (start-here doc dominates when queries touch its example text). Smallest mechanism options:
   - (a) exclude `docs/00-START-NEXT-SESSION.md` + `docs/handoffs/SESSION_*.md` from `search_docs` corpus (surgical + reversible)
   - (b) reduce per-chunk weight for these classes in `top_k` (per-chunk cap or file-class deprioritization)
   - (c) example-text detection in ranker (heavier lift)
   Success criterion: Q5 top-1 returns to `docs/AGENTS_REFERENCE.md#35` (matches pre-boost baseline). Reuses same 6-query batch as S2818+S2819 for direct comparison.

### From 2799 §8 remaining queue + S2818/S2819 follow-ons

2. **Multi-doc `AUTHORITY_FILE_BONUS` expansion** — now UNBLOCKED by S2819 Shape C proving gated mechanism works. Candidates from S2818 SIGN Q3: `DOC_LIFECYCLE.md`, `PLATFORM_WHAT_IT_IS.md`, `CLAUDE.md`. Requires per-doc intent gates (S2819 §5 Q4 coupling risk) since each doc has different intent match.
3. **Playbook v0.9 amendment (OP3 codification)** — 9/9 triggers now including INITIAL-ESCALATE → RE-VERDICT-SHIP variant. Well past codification threshold.
4. **HIGH-DRIFT rule canonicalization** (Rules #4/#5/#14 per T6) — pilot MQ-T6-8 actionable standard on S1300 §3F (genuinely stale). MEDIUM scope.
5. **Parent §4 T5 clause update** per T5 MQ-T5-8 — requires Chris re-ratification per parent §5 Chris-lock. LOW scope.
6. **File moves per 2799 §3 target tree** — pilot `docs/adr/` → `docs/decisions/` (smallest scope + real convention collision per T3 B3).
7. **Per-handoff citation_health verification for S2500-2600 range** — 10-doc pilot.
8. **Retrieval-frequency telemetry design** — schema proposal for `search_docs` corpus.
9. **Generator/automation coordination for autogen output moves** (Rigby SIGN Q3 addition) — blocks 2799 §3.2 audit consolidation.

### Colorado / other (still queued)

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk)
- **Phase 4** — statute-citation content quality
- **Phase 5.1** — un-punt Session 534 spider AJAX
- **GPT fallback for form-selection** on low-confidence

### Non-2700/non-Colorado

- **BettingPage first-user trace**
- **Stock Intelligence** — end-to-end verify

**Recommended default:** Item #1 (00-START contamination fix). Closes the last observable regression from the two-pilot discovery-layer arc; substrate maximally fresh in context; same 6-query batch reusable for direct pre/post. If Chris signals "no more discovery-layer for now" — item #2 (multi-doc AUTHORITY_FILE_BONUS expansion) is unblocked and represents the natural mechanism scaling. If Chris pivots to net-new engineering — BettingPage or Stock Intelligence remain queued.

---

## SESSION PIN — S2819 RETIRED (fresh mint required at S2820 open)

**Pin history (S2819):**

- `pa-ebadb78a43034ff7` (label `s2819-shape-c-intent-gating`) minted at S2819 open; **retired at S2819 close (`force=true`, fiftieth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at retired pin** — intended failure mode forces S2820 first-action fresh mint.

**S2820 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2819 handoff — §3 (novel-precedent — first INITIAL-ESCALATE→RE-VERDICT-SHIP + first self-contamination surfaced live), §6 (candidates for S2820), §7 (lessons)
# If continuing 00-START contamination fix: also read S2819 envelope §5.2 (self-contamination finding) + S2819 §6 (follow-on queue additions)

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

python manage.py session_lifecycle open --label s2820-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**S2819 lessons to carry:**

1. **Success criteria must be empirically grounded in the pre-change baseline.** T3 §3 "intended target" labels are aspirational (where the user *should* end up), not empirical (where search *actually* went). Baseline capture must include per-named-target presence check before locking criterion. Codifiable methodology gotcha (first trigger; observe 1-2 more before Playbook amendment).
2. **Post-authoring SIGN catches CRITERION errors, not just implementation errors.** Rigby's initial ESCALATE was correct against my flawed criterion; corrected framing produced SHIP. OP3 pattern is about evidence framing, not just code.
3. **Same-session doc-writes can contaminate the corpus** — writing example text in start-here docs re-embeds them and biases future retrieval. Watch for this in future pilot arcs when authoring 00-START and handoffs mid-pilot.
4. **Empirical-pattern-extension discipline is a defensible ship criterion.** Rigby SIGN Q2 added exactly one pattern (`list all`) based on live evidence; declined two speculative additions. Sets precedent for future pattern-set expansions: evidence-first, not speculation-first.
5. **INITIAL-ESCALATE → RE-VERDICT-SHIP is a valid closure pattern.** When Rigby escalates on the criterion Claude gave her, and the criterion itself is the error, correcting the criterion and re-routing is the right move — not accepting the escalate uncritically.
6. **Direct-continuation pilot arcs are viable when substrate is fresh.** S2818 → S2819 same day worked because Shape C was already Chris-ratified top-of-queue with narrow scope. Don't force this shape when substrate isn't fresh.

---

## Twin-pointer card

📁 **Repo — S2819 artifacts:**

- **Feature PR (1, merged):** #3255 (Shape C intent-gating · `13844fc82`)
- **Close cascade PR:** #TBD (SHA at merge)
- **Substrate changes:** `core/rag.py` (mod), `core/tests/test_rag_intent_gating_2819.py` (new, 15 tests), `core/tests/test_rag_authority_boost_2818.py` (mod, 1 test), `docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md` (new envelope)
- **Handoff:** `docs/handoffs/SESSION_2819_SHAPE_C_INTENT_GATING.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session; folds deferred to next arc close)
- **Merge SHA:** `13844fc82` (feature) → close-cascade SHA filled at merge

🖥️ **Workspace UI — S2819 has NO twin-pointer workspace deliverable this session** — pilots keep envelope in `docs/research/implementation/` as authoritative; workspace mirror deferred per S2818 pilot pattern (arc-scoped envelopes get workspace mirror; single-pilot ratifications don't). Group 2700 arc's workspace deliverable (`37d6ca76-89c3-4966-8f4c-decc52ce8169`) remains authoritative for the /docs/ restructuring arc under which S2818 + S2819 are §8 executions.

---

## Current repository state (S2819 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2819 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment 9/9 corroborated including INITIAL-ESCALATE→RE-VERDICT-SHIP variant**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | **ARC CLOSED (S2817).** §8 follow-on: item #1 SHIPPED across S2818 (unconditional boost) + S2819 (Shape C gate). 00-START contamination fix queued as S2820 top-of-queue (novel from S2819 §5.2). |
| Emergent candidates | 00-START contamination (top); multi-doc AUTHORITY_FILE_BONUS (now unblocked); Playbook v0.9 (9/9); remaining 2799 §8 items |
| Session pin | `pa-ebadb78a43034ff7` (retired at S2819 close, force=true, fiftieth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — retired pin (forces fresh mint at S2820 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2819 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 in-session recycle + 1 post-merge recycle + 1 close-cascade recycle to come |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — 114 rows (unchanged this session; folds deferred per S2818 pattern) |
| /docs/ restructuring | **ARC CLOSED (S2817).** Item #1 SHIPPED with 2-pilot chain S2818+S2819. Discovery-layer arc has 2 novel findings + 1 empirically-validated gated mechanism + queued next-mechanism (00-START contamination fix). |
| Next move | Chris picks direction at S2820 open — 00-START contamination fix is default; multi-doc expansion secondary; net-new engineering pivots also available |

---

## Recommended session-open protocol (S2820, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2819 handoff §3 + §6 + §7
4. **If continuing 00-START contamination fix (default):** read S2819 envelope §5.2 (self-contamination) + §6 (follow-on queue) for design context; also T3 §7 C2 in `docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md` for the class-of-pain framing
5. Sanity checks (brew postgres + ledger 114 verify)
6. `git log --oneline -5` — should show S2819 feature + cascade + S2818 chain
7. **Chris picks direction** — 00-START contamination fix is default; can override to multi-doc expansion / Colorado / non-2700 / other
8. Mint fresh pin scoped `s2820-<Chris's-direction>`
9. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
10. Route scope through Rigby joint SIGN before authoring
11. **For any implementation-shape work:** OP3 two-SIGN pattern (9/9 across shapes now with INITIAL-ESCALATE→RE-VERDICT-SHIP variant)
12. **BASELINE CAPTURE DISCIPLINE (S2819 lesson):** include FULL top-K + per-named-target presence check for every named target doc in success criterion BEFORE locking. Don't set "restore X to top-3" without first verifying X was ever there.
13. **UPPER BOUND / precision qualifiers** required for count claims
14. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional** at v0.8.0
15. **Anchor-verify at every scope decision point** (17-session trend)
16. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2820:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap
2. [`docs/handoffs/SESSION_2819_SHAPE_C_INTENT_GATING.md`](docs/handoffs/SESSION_2819_SHAPE_C_INTENT_GATING.md) — **S2819 handoff (current)**
3. [`docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2819_shape_c_intent_gating.md) — **S2819 envelope with §5.1 success-criterion hygiene + §5.2 self-contamination + §6 follow-on queue**
4. [`docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md`](docs/research/implementation/RATIFICATION_2026-07-18_s2818_platform_inventory_authority_boost_pilot.md) — S2818 pilot envelope (predecessor)
5. [`core/rag.py`](core/rag.py) — mechanism landing (`AUTHORITY_FILE_BONUS` + `_authority_bonus` + `_COUNT_INTENT_PATTERNS` + `_looks_like_count_query` + `top_k(authority_gate=)`)
6. [`core/tests/test_rag_intent_gating_2819.py`](core/tests/test_rag_intent_gating_2819.py) — test scaffolding for further gating extensions
7. [`docs/handoffs/SESSION_2818_DISCOVERY_LAYER_PILOT.md`](docs/handoffs/SESSION_2818_DISCOVERY_LAYER_PILOT.md) — S2818 handoff (predecessor)
8. [`docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`](docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md) — Group 2700 arc-close deliverable; §8 follow-on queue authorizes both S2818 + S2819
9. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3 C5 (counts) + C2 (start-here dominance) + B1 (non-counts scenario) source evidence
10. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 amendment 9/9 corroborated including INITIAL-ESCALATE→RE-VERDICT-SHIP)
11. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2819 close (unchanged this session)
