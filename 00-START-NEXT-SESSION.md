# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2812 CLOSED (late-afternoon close 2026-07-18; picks up as S2813) — Group 2700 T2 pattern extraction SHIPPED

**Refreshed 2026-07-18 late-afternoon (SESSION 2812 CLOSED — sixteenth-consecutive same-day multi-ship session and FIRST FOUR-CLOSE-CASCADE day: S2809 + S2810 + S2811 + S2812 all closed 2026-07-18. Group 2700 T2 pattern-extraction audit shipped as PR #3241 `a70b01265`, +434 LOC. Enumerates 31 transferable primitives from `docs/research/` across 6 categories (Structural / Naming / Frontmatter / Body / Process / Operational) with per-primitive load-bearing rationale, applicability-boundary challenge, and transferability verdict (WHOLE / CORE-ONLY / REJECT / RESEARCH-ONLY BY DESIGN). Highest-leverage transferable primitive: FP-META (frontmatter as extensible control-plane header) — CORE-ONLY with HARD guardrail against autogen + runtime-coupled paths per Rigby SIGN post-authoring Q2. Second consecutive trigger for OP3 two-SIGN-per-audit pattern; one more (T3) satisfies Playbook v0.9 promotion threshold. FIFTY-SIXTH close-cycle post-PLAYBOOK-7.4.4.**

**S2812 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Group 2700 T2 audit | **#3241** · `a70b01265` | main | `docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md` (+434 LOC, new) |

**Handoff:** `docs/handoffs/SESSION_2812_GROUP_2700_T2_PATTERN_EXTRACTION.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day).

**Arc state at S2812 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring** — Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3-T6 + 2799 queued.

---

## S2813 CANDIDATES — CHRIS PICKS FRESH

### ⭐ Continue Group 2700 arc

- **T3 — `2703_docs_human_user_pain_points_audit.md`** (per parent §11 next-in-sequence). Trace concrete user journeys: (a) "Chris asks 'where do I see X?'" (b) "fresh Claude asked to fix Y" (c) "Rigby asked to search for Z"; measure discoverability hops until each lands on the right doc. Method: pick 5-10 real scenarios, walk each, log hops + friction. Third consecutive OP3 trigger would satisfy Playbook v0.9 promotion threshold.

### Colorado / other

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5.1** — un-punt Session 534 spider AJAX (large; unknowable time budget)
- **GPT fallback for form-selection** on low-confidence (row-114 emergent)

### Non-Colorado / non-2700 arcs

- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** T3 — arc momentum is strong, three-audit-in-a-row streak makes T4-T6 easier to slot in, and the OP3 pattern gets its promotion trigger.

---

## SESSION PIN — S2812 RETIRED (fresh mint required at S2813 open)

**Pin history (S2812):**

- `pa-2859cc425c90417c` (label `s2812-group-2700-t2-research-pattern-extraction`) minted at S2812 open; **retired at S2812 close (`force=true`, forty-third consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-2859cc425c90417c` (retired)** — intended failure mode forces S2813 first-action fresh mint.

**S2813 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2812 handoff — §3 (novel-precedent), §6 (candidates)
# If continuing Group 2700 arc, also read parent §4 T3 scope block + T2 primitive list for reference
# Chris picks direction; label pin accordingly

# If services aren't running: make restart
brew services list | grep postgres

# Verify ledger baseline 114 held
DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2813-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2813 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2812 lessons to carry:**

1. **Two-SIGN-per-audit pattern PROVEN across audit shapes.** S2811 T1 measurement audit + S2812 T2 primitive extraction audit both benefited from post-authoring SIGN. T1 catch: `docs/18960/` ghost (factual). T2 catch: 2 missing primitives + FP-META guardrail gap (coverage). Different failure modes; same rescue mechanism. **One more consistent trigger at T3 authoring** and this becomes Playbook v0.9 amendment candidate.
2. **Applicability-boundary language is now standard for T2+ audits.** Verdict scale (WHOLE / CORE-ONLY / REJECT / RESEARCH-ONLY BY DESIGN) alone can nudge misreads; adding qualifiers (human-authored only / excludes autogen / excludes runtime anchors / requires tooling / safe default not mandate) preserves the simple scale while preventing "let's put frontmatter everywhere" errors.
3. **CONCEPT vs MECHANISM distinction is a first-class arc discipline.** T2's MQ-T2-7 explicitly clarifies that OFF-LIMITS applies to MECHANISMS (SIGN pins, xx00 numbering, 28-Q template) even when CONCEPTS (second-order review, predictable entry point, comprehensive coverage) transfer. Prior arcs conflated these; T2 made the distinction explicit for canonical summary consumption.
4. **Highest-leverage transferable primitive is FP-META** — every non-autogen human-authored doc could adopt `title/status/authority/date/last_verified/related` core frontmatter tomorrow with minimal cost + significant discoverability win. **HARD guardrail:** do NOT force on machine-generated content (`docs/*_AUDIT.md` batch + `docs/INDEX.md` + runtime-coupled paths per DOC_LIFECYCLE §2b).
5. **Rigby's tool_runs surface load-bearing primitives Claude-alone would miss.** Open SIGN Q3 zoom-out surfaced 5 missing primitives (FP-META meta, BP5 epistemic labeling, PP5 SIGN pin discipline, PP6 OPEN_ARCS ledger, NP3 numbering-is-indexing-not-type). Post-authoring SIGN Q1 surfaced 2 more (SP5 runtime-coupled stability, OP4 registration/visibility). **7 of 31 primitives (~23%) came from Rigby's tool-grounded pressure-test, not Claude's initial pass.**
6. **Four-close-cascade day sustains** when scope discipline holds. Today: S2809 (~54 LOC) + S2810 (~130 LOC) + S2811 T1 (~406 LOC) + S2812 T2 (~434 LOC) = 4 features/audits shipped. All followed the SIGN → author → SIGN → ship → cascade → recycle sequence. Session-cost-per-ship stays low.

---

## Twin-pointer card

📁 **Repo — S2812 artifacts:**

- **PR (1, merged):** #3241 (T2 audit · `a70b01265`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md` — new (+434 LOC)
- **Handoff:** `docs/handoffs/SESSION_2812_GROUP_2700_T2_PATTERN_EXTRACTION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day)
- **Merge SHA:** `a70b01265` (T2) → close-cascade SHA filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible UI change this session.** T2 is a research/audit deliverable.
- **Twin workspace deliverable:** N/A this session (per parent §5 — canonical summary at 2799 is where twin-pointer discipline applies for the arc).

---

## Current repository state (S2812 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2812 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3-T6 + 2799 queued. |
| Emergent candidates | T3 next-in-sequence per parent §11; OP3 two-SIGN pattern one trigger from Playbook v0.9 amendment threshold; all prior Colorado candidates still queued |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-2859cc425c90417c` (retired at S2812 close, force=true, forty-third consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-2859cc425c90417c` (retired; forces fresh mint at S2813 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2812 open |
| Recycle log | `logs/recycle_events.jsonl` — +8 today across S2809+S2810+S2811+S2812 (2 per session) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day) |
| Colorado Family Law agent status | ✅ Dispatch works E2E; ✅ persistence reliable (P1 Lesson-3 hardened + P1.b); ✅ case creation user-driven (+attorney sub-form); ✅ form-selection user-driven (Phase 4a) |
| /docs/ restructuring | Group 2700 arc live; parent locked; T1 + T2 shipped; T3 next |
| Next move | Chris picks direction fresh at S2813 open |

---

## Recommended session-open protocol (S2813, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2812 handoff §3 (novel-precedent) + §6 (candidates)
4. **If continuing Group 2700 arc (T3):** also read parent doc §4 T3 scope block + skim T2 primitive list (§4-§9) as evidence source
5. **Sanity check:** `brew services list | grep postgres`
6. **Services check:** `curl -s http://localhost:8000/health/ping/`
7. **Freshness + ledger 114 verify** — see S2813 open sequence above
8. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
9. **Chris picks direction** — see §S2813 CANDIDATES above
10. Mint fresh pin scoped `s2813-<Chris's-direction>`
11. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
12. Route scope through Rigby joint SIGN before authoring
13. **For arc-audit work (T3+):** plan for TWO SIGN cycles per audit doc — open-scope + post-authoring pressure-test. S2811 + S2812 lessons prove the pattern.
14. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
15. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
16. **Anchor-verify at every scope decision point (10-session trend):** any factual claim about live state MUST be re-verified. Watch for `ls -la` `total NNNNN` trap.
17. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2813:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2812_GROUP_2700_T2_PATTERN_EXTRACTION.md`](docs/handoffs/SESSION_2812_GROUP_2700_T2_PATTERN_EXTRACTION.md) — **S2812 handoff (current)**
3. [`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`](docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md) — parent scoping (Chris-locked S2801) — READ before authoring T3-T6 or 2799
4. [`docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md`](docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md) — T1 audit (shipped S2811, cite as evidence source)
5. [`docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md`](docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md) — T2 audit (shipped S2812, cite as evidence source)
6. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — canonical arc process framework (v2)
7. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts (cite; never restate)
8. [`docs/INDEX.md`](docs/INDEX.md) — docs corpus counts (cite; never restate)
9. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (205 rules)
10. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2b runtime-coupled + §2c counts anchor + §3 root-stability
11. [`docs/handoffs/SESSION_2811_GROUP_2700_T1_INVENTORY_AUDIT.md`](docs/handoffs/SESSION_2811_GROUP_2700_T1_INVENTORY_AUDIT.md) — S2811 T1 predecessor (same-day)
12. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2812 close (unchanged all day)
