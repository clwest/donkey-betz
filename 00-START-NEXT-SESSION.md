# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2811 CLOSED (late-afternoon close 2026-07-18; picks up as S2812) — Group 2700 T1 /docs/ inventory audit SHIPPED

**Refreshed 2026-07-18 late-afternoon (SESSION 2811 CLOSED — fifteenth-consecutive same-day multi-ship session and FIRST TRIPLE-close-cascade day: S2809 + S2810 + S2811 all closed 2026-07-18. Session pivoted mid-day from Colorado warm-ups (S2809+S2810) to the Group 2700 /docs/ restructuring arc that had been queued since S2800 close (14 sessions bumped). Parent scoping doc `2700_docs_restructuring_domain_scoping.md` was found ALREADY LOCKED at S2801 (2026-07-16) with a 6-thread package — reframed session scope from "author parent" to "author T1" via anchor-verify. T1 (`2701_docs_inventory_topology_audit.md`, PR #3239 `8d5c89386`, +406 LOC) shipped as MEASUREMENTS-ONLY per parent §4 scope: 3201 total .md files, 99 loose at root (~10× target), 3 parallel audit dirs (118 files) + 20 loose *AUDIT.md, ~4% autogen, LOC + freshness distributions, 9-item Migration Queue. Two Rigby SIGN cycles (open-scope + post-authoring pressure-test); post-authoring caught a `docs/18960/` ghost reference (I misread `total 18960` block-count from `ls -la` as a directory). FIFTY-FIFTH close-cycle post-PLAYBOOK-7.4.4.**

**S2811 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Group 2700 T1 audit | **#3239** · `8d5c89386` | main | `docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md` (+406 LOC, new) |

**Handoff:** `docs/handoffs/SESSION_2811_GROUP_2700_T1_INVENTORY_AUDIT.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged; no folds persisted).

**Arc state at S2811 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates still queued.
- **Group 2700 /docs/ restructuring** — Parent ✅ (S2801) / T1 ✅ (S2811) / T2-T6 + 2799 queued.
- **Group 2700 arc-restart pattern** captured as first-class project memory (`project_half_finished_arcs_from_life_interruptions`).

---

## S2812 CANDIDATES — CHRIS PICKS FRESH

### ⭐ Continue Group 2700 arc

- **T2 — `2702_docs_research_pattern_extraction_audit.md`** (per parent §11 next-in-sequence). Reverse-engineer transferable primitives from `docs/research/`: RESEARCH_OPERATING_SYSTEM, OPEN_ARCS manifest, ARCHITECTURE_INDEX matrix, DOMAIN_RESEARCH_PLAYBOOK, xx00/xx99 shape, per-domain slugs, verifier_loop frontmatter. **Anti-pattern to CHALLENGE per parent §4 T2:** "the /docs/research/ pattern is load-bearing therefore off-limits." T2 must produce CHALLENGE candidates — where does the pattern NOT fit outside `/docs/research/`?

### Colorado / other

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5.1** — un-punt Session 534 spider AJAX (large; unknowable time budget)
- **GPT fallback for form-selection** on low-confidence (row-114 emergent)
- **Attorney sub-forms polish** — data flow-through test to verify motion drafting picks up new attorney context

### Non-Colorado / non-2700 arcs

- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** T2 if you want to keep the docs arc momentum fresh across sessions; a warm-up if a next-day break resumes at S2812.

---

## SESSION PIN — S2811 RETIRED (fresh mint required at S2812 open)

**Pin history (S2811):**

- `pa-95b2301d7aba4187` (label `s2811-group-2700-docs-restructuring-parent-scoping` — kept even after mid-session scope refined from "author parent" to "author T1") minted at S2811 open; **retired at S2811 close (`force=true`, forty-second consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-95b2301d7aba4187` (retired)** — intended failure mode forces S2812 first-action fresh mint.

**S2812 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2811 handoff — §3 (novel-precedent), §6 (candidates)
# If continuing Group 2700 arc, also read parent §4 T2 scope block
# Chris picks direction; label pin accordingly

# If services aren't running: make restart
# Check freshness FIRST if anything looks off:
brew services list | grep postgres

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2812-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2812 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2811 lessons to carry:**

1. **Two-SIGN-per-audit pattern lands cleanly for arc-audit work.** Open-scope SIGN + post-authoring pressure-test SIGN caught a real anchor-verify miss (`docs/18960/` ghost) before ship. If T2-T6 repeat this pattern and it consistently catches errors, it may warrant Playbook amendment specific to arc-audit sessions.
2. **`ls -la` block-count line is a Claude anchor-verify trap.** The `total NNNNN` line at the top of `ls -la` output is total disk-blocks, not a directory name. Guard against pattern-matching on it. **Recovery:** always cross-check with `ls -d */` or `find -maxdepth 1 -type d` when enumerating subdirs.
3. **Chris's own standing directives override the "engineering bias over audit" rule.** `feedback_engineering_bias_over_audit` is a session-open bias, not a veto on Chris's explicit requests. The /docs/ restructuring arc was Chris's own S2800 directive; opening it at S2811 was correct despite its audit shape.
4. **Half-finished arcs are a first-class project fact now.** `project_half_finished_arcs_from_life_interruptions` captures Chris's observation that arc-restart happens from life interruptions + late-night → next-morning distraction. Future audits should actively surface arc-restart evidence (parallel-named dirs, doubled files, TODO/PUNT/DEFERRED markers, docs referenced by an arc-open but never authored).
5. **Predecessor handoff drift compounds.** Parent 2700 doc's §3 cited 2618 docs at S2800; T1 measured 3201 at S2811 (+583 in 14 sessions). Every child audit MUST measure current state, not trust parent's baseline. Parent stays as-authored per no-restructure rule; children carry the drift note.
6. **Warm-up ships stack cleanly.** Today shipped: S2809 P1 back-port (~54 LOC) → S2810 attorney sub-form (~130 LOC) → S2811 T1 audit (~406 LOC). Three same-day close cascades. Session-cost-per-ship stays low if scope discipline holds.

---

## Twin-pointer card

📁 **Repo — S2811 artifacts:**

- **PR (1, merged):** #3239 (T1 audit · `8d5c89386`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md` — new (+406 LOC)
- **Related memory changes:**
  - `project_docs_restructuring_arc_queued.md` — updated (4-thread → 6-thread; T1 shipped state)
  - `project_half_finished_arcs_from_life_interruptions.md` — **new**
- **Handoff:** `docs/handoffs/SESSION_2811_GROUP_2700_T1_INVENTORY_AUDIT.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged)
- **Merge SHA:** `8d5c89386` (T1) → close-cascade SHA filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible UI change this session.** T1 is a research/audit deliverable; reachable via same doc index consumers as other research artifacts (search_docs, docs/INDEX.md, DocsIndexPage frontend).
- **Twin workspace deliverable:** N/A this session (per parent §5 — canonical summary at 2799 is where twin-pointer discipline applies for the arc).

---

## Current repository state (S2811 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2811 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | Parent ✅ (S2801) / T1 ✅ (S2811) / T2-T6 + 2799 queued. |
| Emergent candidates | T2 next-in-sequence per parent §11; all prior Colorado candidates still queued |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-95b2301d7aba4187` (retired at S2811 close, force=true, forty-second consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-95b2301d7aba4187` (retired; forces fresh mint at S2812 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2811 open |
| Recycle log | `logs/recycle_events.jsonl` — +6 today across S2809+S2810+S2811 (2 per session) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day) |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable (P1 Lesson-3 hardened + P1.b); ✅ case creation user-driven (+attorney sub-form); ✅ form-selection user-driven (Phase 4a) |
| /docs/ restructuring | Group 2700 arc live; parent locked; T1 shipped; T2 next |
| Next move | Chris picks direction fresh at S2812 open |

---

## Recommended session-open protocol (S2812, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2811 handoff §3 (novel-precedent) + §6 (candidates)
4. **If continuing Group 2700 arc:** also read parent doc §4 T2 scope block (`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`)
5. **Sanity check:** `brew services list | grep postgres`
6. **Services check:** `curl -s http://localhost:8000/health/ping/`
7. **Freshness + ledger 114 verify** — see S2812 open sequence above
8. If `staleness_verdict != FRESH` → escalate (post-travel triage per `feedback_post_travel_port_collision_triage`)
9. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
10. **Chris picks direction** — see §S2812 CANDIDATES above
11. Mint fresh pin scoped `s2812-<Chris's-direction>`
12. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
13. Route scope through Rigby joint SIGN before authoring
14. **For arc-audit work (T2+):** plan for TWO SIGN cycles per audit doc — open-scope + post-authoring pressure-test. S2811 lesson.
15. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
16. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
17. **Anchor-verify at every scope decision point (9-session trend, S2811 corollary: also for author-Claude claims, not just predecessor framings):** any factual claim about live state MUST be re-verified. Watch for `ls -la` `total NNNNN` trap.
18. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2812:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2811_GROUP_2700_T1_INVENTORY_AUDIT.md`](docs/handoffs/SESSION_2811_GROUP_2700_T1_INVENTORY_AUDIT.md) — **S2811 handoff (current)**
3. [`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`](docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md) — parent scoping (Chris-locked S2801) — READ before authoring any T2-T6 or 2799
4. [`docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md`](docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md) — T1 audit (shipped S2811, cite as evidence source)
5. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — canonical arc process framework (v2)
6. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
7. [`docs/INDEX.md`](docs/INDEX.md) — docs corpus counts (cite; never restate)
8. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
9. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2b runtime-coupled + §2c counts anchor + §3 root-stability
10. [`docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md`](docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md) — S2810 predecessor (same-day)
11. [`docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md`](docs/handoffs/SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md) — S2809 predecessor (same-day)
12. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2811 close (unchanged all day)
