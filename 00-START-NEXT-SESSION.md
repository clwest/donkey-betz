# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2801 CLOSED — /docs/ restructuring arc OPEN at Group 2700 (parent-scoping ratified; T1 inventory & topology audit is S2802 default)

**Refreshed 2026-07-16 (SESSION 2801 CLOSED — fifth consecutive same-day multi-ship session (S2797 → S2798 → S2799 → S2800 → S2801). Shape shift: S2797–S2800 all engineering ships; S2801 is a research/scoping ship. Chris directive at S2800 close 2026-07-16: `"Before we do anything else I want you and Rigby to do a deep audit of the /docs/."` Ratified shape at S2801 T1: **parent-scoped research arc `2700`** using the `/docs/research/` pattern as the audit apparatus (dogfooded on `/docs/` itself). Chris D-verdict at T1: `"go ahead with the 6-thread package"`. Ships parent-scoping charter (262 lines) + OPEN_ARCS in-progress row + arc pin rotation. Rigby T1 SIGN-with-edits with tool-grounded evidence (ops_tool + search_docs + kb_tool); anti-rubber-stamp check PASSED per `feedback_verify_rigby_tool_runs_before_trusting_sign`. 4 zoom-out folds persisted rows 90-93 BEFORE Chris D-verdict per PLAYBOOK-6.10.8 — fourth consecutive session with correct fold-timing discipline. Novel: **first arc that dogfoods its own audit apparatus with explicit CHALLENGE mitigation** — row 91 fold surfaces self-referential lock-in risk; T2 charter mandates the challenge. FORTYSECOND close-cycle post-PLAYBOOK-7.4.4.)**

**S2801 ship:**

**PR #3216 · `f3d08d690`** — 3 files, +264 / -1. Parent-scoping doc at `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md` (262 lines) + `docs/research/OPEN_ARCS.md` in-progress row for Group 2700 + `tools/pa_local.sh` arc pin rotation.

**Handoff:** `docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **93 rows** (35 `same_pr_actionable` / 32 `same_pr_mitigatable` / 23 `future_trigger` — approx; rows 90-93 are S2801 T1 folds).

**Arc state:** `2700` **in-progress** (parent shipped). Children `2701..2706` **not-started**. Summary `2799` **not-started**. Full arc will span multiple sessions.

---

## SESSION-OPEN INFRA STORY (S2801)

**Fifth consecutive same-day multi-ship session; shape-shift from engineering to research/scoping.** Discipline transferred cleanly across ship-shape boundary — PLAYBOOK-6.10.7/6.10.8/6.10.9 held identically on a scoping ship as on the engineering ships. Chris directive at S2800 close queued the arc without fresh re-scoping at S2801 open (clean predecessor→successor handoff).

**First arc that dogfoods its own audit apparatus.** T2 charter mandates CHALLENGE candidates against the `/docs/research/` pattern (Rigby fold 91 mitigation). Self-referential lock-in surfaced pre-authoring and baked into child scope directly — first arc where fold-content became child-audit-scope requirement.

**PLAYBOOK-6.10.8 discipline held (fourth consecutive session).** 4 folds persisted between T1 SIGN and Chris "go ahead." Ledger 89 → 93 committed BEFORE joint recommendation to Chris. S2798 missed timing (persisted after); S2799 corrected; S2800 held; S2801 held.

**Rigby T1 SIGN substantive.** Verdict SIGN-WITH-EDITS with scope-changing edits (T3 split into human-pain + audience-segmentation; T6 anchor-drift thread added — 4 threads → 6 threads). Not a rubber-stamp AGREE. tool_runs contained file:line citations to real evidence surfaces. Anti-rubber-stamp check PASSED per `feedback_verify_rigby_tool_runs_before_trusting_sign`.

**Twin workspace deliverable deferred to arc close.** Per parent doc §5 anti-scope + `feedback_twin_deliverable_at_every_ratification` — twin applies to the RATIFIED restructuring plan (canonical summary at `2799`), not to the parent-scoping charter itself.

---

## S2802 CANDIDATES — T1 INVENTORY & TOPOLOGY AUDIT IS THE DEFAULT

### ⭐ T1 (2701) — Docs inventory & topology audit (default candidate)

**Shape:** Group 2700 arc's first child audit. Load parent doc + `DOMAIN_RESEARCH_PLAYBOOK.md §9` (28 canonical questions). First-action fresh mint of pin scoped to T1.

**Scope (from parent §4):** what's IN `/docs/` (dir tree, file counts, auto-gen vs hand-written distribution, freshness histogram, size distribution, subdir purpose taxonomy). Ground-truth inventory that later threads reference.

**Deliverable:** `docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md` with 28-question audit + `## Migration Queue (post-arc)` section (per hard-line non-goals discipline).

**Anti-duplicate discipline:** cite `PLATFORM_INVENTORY.md` for runtime counts (never restate); cite `docs/INDEX.md` for corpus counts.

**Explicitly out (parent §7 anti-scope):** any judgment on what should MOVE (T5/T6's job); T1 measures only.

**Recommended S2802 flow:**
1. Fresh mint of pin scoped to `s2802-t1-docs-inventory-topology`
2. Read parent doc `2700_docs_restructuring_domain_scoping.md` end-to-end
3. Read `DOMAIN_RESEARCH_PLAYBOOK.md §9` (28 questions)
4. Execute inventory sweep (six-parallel-Explore per playbook §13)
5. Author child audit
6. Route to Rigby for T1 SIGN + zoom-out fold set
7. Chris D-verdict
8. Close-cascade

### Alternate candidates (if Chris deprioritizes T1)

- **BettingPage first-user trace + top-1 fix** — pre-existing default before docs arc queued; still owed after arc closes
- **Stock Intelligence** — first non-betting revenue play (behind BettingPage)

### S2800/S2801 follow-ups (all deferred; not blocking)

- **Non-recycle-day no-heartbeat monitor** (S2800 fold row 89 future_trigger) — 7-day trigger fires 2026-07-23
- **Per-signpost adoption telemetry** (S2799 F84) — 7-day trigger fires 2026-07-23
- **AudioAgent TTS payment wall** — separate config; deferred
- **CodeReviewAgent workspace file discovery** — deferred per Rigby T1 (fail-fast > implicit guessing)

### S2797/S2798 standing owed

- Onboarding banner in shared authed Layout (S2798 F3 future_trigger)
- Throttle on `POST /api/onboarding/complete/` (S2798 F4 future_trigger)
- Regression test for `complete_onboarding_view`
- Public deployment of LandingPage (hosting + DNS)
- Waitlist DB capture (Shape B)
- I-0303 scoping (RUR-C1 parent-close blocker)
- Regression tests for 4 S2796 tools
- 8 remaining per-tool docs need "Covered actions"
- 23 tools schema-lint fix
- Wire tenant boundary health → Celery beat
- **`SESSION_819_SYSTEM_AUDIT_*` 19-file cleanup** — DEFERRED per Group 2700 non-goals (no deletions during arc); migration eligible post arc-close
- Doc-note gap-map classifier h3-truncation bug in S2795 F2 template spec

### Deferred (waiting on triggers)

- All S2797-S2800 triggers unchanged
- **NEW: parent doc open decisions O1-O4** — Chris ratifies as they surface during T1-T6 execution; none block T1 open

---

## SESSION PIN — S2801 RETIRED (fresh mint required at S2802 open)

**Pin history (S2801):**

- `pa-9e641d91391f40d8` (label `s2801-docs-restructuring-parent-scoping`) minted S2801 open; **retired at S2801 close (`force=true`, thirtysecond consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-9e641d91391f40d8` (retired)** — intended failure mode forces S2802 first-action fresh mint.

**S2802 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2801 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §7 (Chris directive queue)
# Read parent doc: docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md
# Read DOMAIN_RESEARCH_PLAYBOOK §9 (28 canonical questions)

# Freshness check. Should be FRESH · SHA-match at S2801 close-cascade SHA.
bash tools/pa_local.sh "S2802 open — freshness check: ops_tool.version verdict + head_commit_sha"

# Ledger check: confirm 93-row baseline survived S2801 close cascade
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==93, r
print('OK — 93 rows, counts:', r['counts_by_classification'])
"

# Mint fresh pin scoped to T1 (if T1 selected as candidate)
python manage.py session_lifecycle open --label s2802-t1-docs-inventory-topology

grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2802 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0** — zoom-out ask required; folds classify+persist BEFORE D-verdict; concrete code-state claims MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline.

**S2801 lessons to carry:**

1. **Dogfooding an audit apparatus on itself requires explicit CHALLENGE mitigation.** Row 91 fold's "T2 must CHALLENGE the pattern" instruction IS a T2 child scope requirement. Do not treat the `/docs/research/` pattern as sacred while auditing it.
2. **Fold-content can be child-audit-scope directly.** When a zoom-out fold surfaces a substrate risk that becomes a downstream audit requirement, wire it into the child charter — don't leave it as a comment.
3. **PLAYBOOK-6.10.8 discipline stable (4 consecutive sessions).** Continue the pattern.
4. **Joint Claude+Rigby recommendation shape held.** One package to Chris, not a menu. Chris D-verdict was one word: "go".
5. **Discipline transfers across ship-shape boundary.** Engineering ships (S2797-S2800) and research/scoping ships (S2801) both honor same fold-timing + SIGN + close-cascade rules.

---

## Twin-pointer card

📁 **Repo `/` + `/docs/` — S2801 artifacts:**

- **Parent-scoping doc:** `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md` (262 lines)
- **Arc manifest:** `docs/research/OPEN_ARCS.md` ## In-progress table (Group 2700 row)
- **Handoff:** `docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — 93 rows (rows 90-93 are S2801)
- **Merge SHAs:** ship=`f3d08d690` (PR #3216); close-cascade=filled at merge
- **Predecessors:** S2800 (broken agents), S2799 (signposts), S2798 (onboarding), S2797 (landing)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No new Workspace tab** — research/scoping ship
- **Twin workspace deliverable:** deferred to arc close at `2799` canonical summary
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **93 rows** (rows 90-93 are S2801)
  - `logs/recycle_events.jsonl` — +N events during S2801 close
  - `http://localhost:8000/welcome` — public LandingPage (unchanged since S2797)
  - `http://localhost:8000/workspace` — first-run banner (unchanged since S2798)

---

## Current repository state

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2801 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Arc state | Group 2700 **in-progress** (parent shipped); children 2701..2706 not-started; summary 2799 not-started |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-9e641d91391f40d8` (retired at S2801 close, force=true, thirtysecond consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-9e641d91391f40d8` (retired; forces fresh mint at S2802 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2801 open |
| Recycle log | `logs/recycle_events.jsonl` — +N events during S2801 (post-merge + post-close-cascade) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **93 rows** (rows 90-93 are S2801 T1 folds) |
| Rigby signposts | 14 tools routed via `unified_pa_entrypoint.py:2799` (unchanged since S2799) |
| Worker reap metric | `[CELERY_WORKER_STARTUP_REAP]` continues logging every restart (S2800 handler stable) |
| Non-betting revenue play | Stock Intelligence identified (TIER 1); deferred behind Group 2700 arc + BettingPage |
| Test user for onboarding demo | `s2798_onboarding_test` / `test-onboard-s2798!` — state re-armed at S2798 close |
| Next move | Chris selects at S2802 open (T1 inventory & topology audit default per parent doc §4 + arc-open sequencing) |

---

## Recommended session-open protocol (S2802)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2801 handoff §2 (novel-precedent moments) + §3 (T1 SIGN cycle) + §7 (Chris directive queue)
4. **Read parent doc:** `docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md` end-to-end
5. **Read DOMAIN_RESEARCH_PLAYBOOK §9** (28 canonical questions apply to child audits)
6. **Freshness + ledger 93 verify** — see S2802 open sequence above
7. **Watch for** ledger 93-row baseline surviving cascade merge; freshness FRESH · SHA-match
8. If `staleness_verdict != FRESH` → escalate
9. **Check `brew services list | grep postgres` FIRST** if freshness fails oddly
10. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
11. **Default candidate: T1 (2701) inventory & topology audit** — first child of arc `2700`. Full instructions in `## S2802 CANDIDATES` section above.
12. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
13. Chris directs S2802 P0 selection (T1 unless override)
14. Mint fresh pin scoped to the child (e.g. `s2802-t1-docs-inventory-topology`)
15. Route T1 audit through Rigby joint SIGN before authoring child doc
16. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
17. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file+line evidence + (i)/(ii)/(iii) outcome inline before classify+persist
18. **Non-goals discipline hard-line:** no file moves / deletions / renames / code changes during arc; each child ships `## Migration Queue (post-arc)` section
19. **T2 dogfooding lock-in mitigation (Rigby fold 91):** T2 audit MUST include CHALLENGE candidates against the `/docs/research/` pattern; do not treat it as sacred
20. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2802:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`](docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md) — **Group 2700 parent charter (current)**
3. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — child audit process framework (§9 28 questions, §11 templates, §13 explore-agent sweeps, §14 evidence rules)
4. [`docs/research/OPEN_ARCS.md`](docs/research/OPEN_ARCS.md) — arc-state manifest (Group 2700 in-progress)
5. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
6. [`docs/PLATFORM_WHAT_IT_IS.md`](docs/PLATFORM_WHAT_IT_IS.md) — **anchor for user-ready reasoning**
7. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
8. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2b/§2c/§3 constraints (arc DESIGNS UNDER these)
9. [`docs/canon/INDEX.md`](docs/canon/INDEX.md) — canon registry (≤10 cap)
10. [`docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md`](docs/handoffs/SESSION_2801_DOCS_RESTRUCTURING_ARC_OPEN.md) — **S2801 handoff (current)**
11. [`docs/handoffs/SESSION_2800_FIX_BROKEN_AGENTS.md`](docs/handoffs/SESSION_2800_FIX_BROKEN_AGENTS.md) — S2800 predecessor
12. [`docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md`](docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md) — prior /docs/ audit reference (T5 substrate-integrity cross-ref)
13. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 93 rows at S2801 close (rows 90-93 are S2801)
