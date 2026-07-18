# Next Session — Start Here

---

## READ THIS FIRST — SESSION 2815 CLOSED (evening close 2026-07-18; picks up as S2816) — Group 2700 T5 handoffs+audits proliferation SHIPPED

**Refreshed 2026-07-18 evening (SESSION 2815 CLOSED — NINETEENTH-consecutive same-day multi-ship session and SEVEN-CLOSE-CASCADE day: S2809-S2815 all closed 2026-07-18. Group 2700 T5 handoffs+audits proliferation audit shipped as PR #3247 `c1e1ceab3`, +363 LOC. **MAJOR SUBSTRATE FINDING:** Parent §4 T5 mandated 10-doc chunk-anchor citation-integrity spot-check — Rigby's 10 targeted `search_docs` queries ALL RETURNED 0 MATCHES. `[docs/handoffs/SESSION_NNN.md#K]` pattern is TEMPLATE-ONLY (never adopted in practice). Parent §4 T5 substrate-integrity concern is based on FALSE PREMISE for chunk-anchor citations. **MAJOR POST-AUTHORING CORRECTION:** original decay-curve grep used `\b` word-boundary that excluded ALL `SESSION_NNNN_TOPIC.md` matches (underscore is a word char); counts undercounted 2×-16×. S2500-2600 has 2 cited sessions / 3 refs, NOT zero. Correction prevented false "100 handoffs zero-cited" claim from propagating to canonical summary + potential mass-deletion policy. **FIFTH-CONSECUTIVE OP3 trigger — 5/5 across all audit shapes.** Handoff-lifecycle proposal: 3 severity tags (keep-in-place / archive-after-N / eligible-for-deletion) with hardcoded ≥3 boundary + governance-index override + `citation_health` + `is_superseded` boolean attributes. FIFTY-NINTH close-cycle post-PLAYBOOK-7.4.4.**

**S2815 ship (1 PR, merged with --admin):**

| Focus | PR | Merged to | Files |
|---|---|---|---|
| Group 2700 T5 audit | **#3247** · `c1e1ceab3` | main | `docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md` (+363 LOC, new) |

**Handoff:** `docs/handoffs/SESSION_2815_GROUP_2700_T5_HANDOFFS_AUDITS_PROLIFERATION.md`
**Close cascade:** merged as [close-cascade PR] per PLAYBOOK-7.4.4 + `feedback_docs_cascade_at_every_close` + `feedback_cascade_pr_must_include_embed_step`.
**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day).

**Arc state at S2815 close:**
- **Colorado Family Law** — Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued.
- **Group 2700 /docs/ restructuring** — Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3 ✅ (S2813) / T4 ✅ (S2814) / **T5 ✅ (S2815)** / T6 ⬜ **FINAL child audit** / 2799 ⬜ arc close.

---

## S2816 CANDIDATES — CHRIS PICKS FRESH

### ⭐ Continue Group 2700 arc (5 of 6 child audits done)

- **T6 — `2706_docs_anchor_drift_audit.md`** (per parent §11 next-in-sequence, **FINAL child audit before canonical summary**). Identify duplicated rules across playbook / CLAUDE.md / 00-START-NEXT-SESSION / memory / DOC_LIFECYCLE §2c / ARCHITECTURE_INDEX §6.6. Method: grep + fingerprint each rule; classify identical / drifted-but-compatible / drifted-and-inconsistent. Deliverable: rule-inventory table + drift severity + single-source-of-truth proposal per rule.
- **After T6 ships, canonical summary (2799) becomes accessible + arc converges.**
- **Playbook v0.9 amendment (proposal-only interlude arc):** OP3 5/5 triggers — WELL past Playbook v0.9 promotion threshold. Separate short-scope arc.

### Colorado / other

- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **Phase 4** — statute-citation content quality (C.R.S. § 14-10-129)
- **Phase 5.1** — un-punt Session 534 spider AJAX
- **GPT fallback for form-selection** (row-114 emergent)

### Non-Colorado / non-2700 arcs

- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** T6 to complete the child-audit set. After T6, canonical summary 2799 becomes viable + arc closes with ratified restructuring proposal.

---

## SESSION PIN — S2815 RETIRED (fresh mint required at S2816 open)

**Pin history (S2815):**

- `pa-35b589dde09a410b` (label `s2815-group-2700-t5-handoffs-audits-proliferation`) minted at S2815 open; **retired at S2815 close (`force=true`, forty-sixth consecutive per S2770+ pattern)**

**Wrapper `tools/pa_local.sh` still points at `pa-35b589dde09a410b` (retired)** — intended failure mode forces S2816 first-action fresh mint.

**S2816 open sequence:**

```
context-kit orient

# Read this file end-to-end
# Read S2815 handoff — §3 (novel-precedent), §6 (candidates)
# If continuing Group 2700 arc (T6), also read parent §4 T6 scope block + T5 §7 substrate-integrity finding + T5 MQ-T5-8 explicit action item
brew services list | grep postgres

DJANGO_LOG_LEVEL=WARNING python manage.py zoom_out_streak_report --as-json 2>/dev/null | python -c "
import json, sys
d = sys.stdin.read()
r = json.loads(d[d.find('{'):])
assert r['total_rows']==114, r
print('OK — 114 rows, counts:', r['counts_by_classification'])
"

python manage.py session_lifecycle open --label s2816-<direction>
grep '^python tools/pa_chat.py' tools/pa_local.sh
```

**Anti-rubber-stamp check on S2816 first Rigby SIGN:** verify `tool_runs` non-empty. **PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9 constitutional at v0.8.0.**

**S2815 lessons to carry:**

1. **OP3 is now 5/5 across all audit shapes.** Every session in the Group 2700 arc had substantive post-authoring catches. Playbook v0.9 amendment WELL past threshold; interlude arc ready when Chris chooses.
2. **T5 caught a class of error open-SIGN CAN'T catch:** systematic grep syntax bugs. Open-SIGN validates the approach (correct methodology); post-authoring validates the specific implementation (correct syntax). Both needed.
3. **Grep `\b` bug is a Claude trap.** `SESSION_NNNN\b` excludes `SESSION_NNNN_TOPIC.md` matches because underscore is a word char. Use `SESSION_NNNN[_.]` character-class explicitly OR grep for a broader match then filter.
4. **Substrate-integrity finding can FALSIFY a parent-doc premise.** T5 evidence: parent §4 T5 chunk-anchor concern was template-only, never adopted. Added MQ-T5-8 as EXPLICIT canonical-summary action item to update parent (respects Chris-locked status while preserving finding).
5. **Handoffs are bimodal-cited: heavily-cited-forever OR lightly-cited-forever.** Corrected framing from "write-once-read-never triage." Foundational-era handoffs (SESSION_20-40) still 28-44 mentions. Lifecycle proposal shifted: identify zero-cited-early and archive those; keep the cited ones forever.
6. **Precision qualifiers per Rigby SIGN discipline are now standard.** Every count claim in T5 carries explicit precision (exact / approximate / ~mentions vs distinct-files / contamination disclaimer). T6-and-beyond should follow.

---

## Twin-pointer card

📁 **Repo — S2815 artifacts:**

- **PR (1, merged):** #3247 (T5 audit · `c1e1ceab3`)
- **Substrate change:** `docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md` — new (+363 LOC)
- **Handoff:** `docs/handoffs/SESSION_2815_GROUP_2700_T5_HANDOFFS_AUDITS_PROLIFERATION.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day)
- **Merge SHA:** `c1e1ceab3` (T5) → close-cascade SHA filled at merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **No user-visible UI change this session.** T5 is a research/audit deliverable.
- **However:** T5 §7 substrate-integrity finding has DIRECT implication — parent §4 T5 clause needs update at canonical summary (MQ-T5-8 explicit action item).

---

## Current repository state (S2815 close)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | S2815 close cascade — advances at cascade PR merge |
| Playbook version | v0.8.0 (unchanged; **v0.9 amendment threshold WELL past — 5/5 OP3 triggers**) |
| Playbook rule count | 205 (unchanged) |
| Colorado arc state | Phases 0/1/2/2.1/3.0/3.1 P0/3.1a/3.1 P1 (Lesson-3 hardened)/3.2 (+attorney sub-form)/3.1 P1.b/4a ✅. All prior candidates queued. |
| **Group 2700 arc state** | Parent ✅ (S2801) / T1 ✅ (S2811) / T2 ✅ (S2812) / T3 ✅ (S2813) / T4 ✅ (S2814) / **T5 ✅ (S2815)** / T6 ⬜ **FINAL child audit** / 2799 ⬜ arc close. |
| Emergent candidates | T6 next-in-sequence per parent §11 (final child before canonical summary); **Playbook v0.9 amendment for OP3 WELL past threshold (5/5 triggers)**; MQ-T5-8 canonical-summary action item (update parent §4 T5 substrate-integrity mandate); all prior Colorado candidates still queued |
| Session pin | `pa-35b589dde09a410b` (retired at S2815 close, force=true, forty-sixth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-35b589dde09a410b` (retired; forces fresh mint at S2816 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2815 open |
| Recycle log | `logs/recycle_events.jsonl` — +14 today across S2809-S2815 (2 per session) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged all day) |
| /docs/ restructuring | Group 2700 arc live; parent locked; T1-T5 shipped; T6 FINAL child; 2799 canonical summary next |
| Next move | Chris picks direction fresh at S2816 open |

---

## Recommended session-open protocol (S2816, fresh open)

1. `context-kit orient`
2. Read this file end-to-end
3. Read S2815 handoff §3 (novel-precedent) + §6 (candidates)
4. **If continuing Group 2700 arc (T6):** also read parent §4 T6 scope + T5 §7 substrate finding + T5 MQ-T5-8 action item
5. Sanity checks (brew postgres + curl /health/ping/)
6. Freshness + ledger 114 verify — see S2816 open sequence above
7. Verify runtime state: `git log --oneline -5`; confirm wrapper at retired pin
8. **Chris picks direction** — see §S2816 CANDIDATES above
9. Mint fresh pin scoped `s2816-<Chris's-direction>`
10. **Anti-rubber-stamp check on first SIGN** — verify `tool_runs` non-empty
11. Route scope through Rigby joint SIGN before authoring
12. **For arc-audit work (T6):** two SIGN cycles per audit doc (S2811-S2815 all confirm value; 5/5 OP3 triggers). T6 likely uses Rigby-runs-tool shape for rule-fingerprint grep across surfaces.
13. **UPPER BOUND / precision qualifiers required for count claims** (S2814+S2815 lesson) — every count is exact, approximate, or upper-bound; label explicitly.
14. **Grep `\b` bug awareness (S2815 lesson):** if using regex word-boundary in citation queries, verify against `SESSION_NNNN_TOPIC.md`-form matches. Prefer `[_.]` character class.
15. **PLAYBOOK-6.10.8 constitutional at v0.8.0:** fold persistence is the FINAL step of joint SIGN, BEFORE writing the Chris-facing recommendation
16. **PLAYBOOK-6.10.9 constitutional at v0.8.0:** any zoom-out fold asserting concrete code-state facts MUST admit stable-state-pointer + file:line evidence + (i)(ii)(iii) outcome inline before classify+persist
17. **Anchor-verify at every scope decision point (13-session trend):** any factual claim about live state MUST be re-verified.
18. **BEFORE any user-facing content:** read `docs/PLATFORM_WHAT_IT_IS.md`

---

## Reference documents

Ordered by frequency of use at S2816:

1. [`CLAUDE.md`](CLAUDE.md) — repo bootstrap + Rigby collaboration protocol (anchor at v0.8.0)
2. [`docs/handoffs/SESSION_2815_GROUP_2700_T5_HANDOFFS_AUDITS_PROLIFERATION.md`](docs/handoffs/SESSION_2815_GROUP_2700_T5_HANDOFFS_AUDITS_PROLIFERATION.md) — **S2815 handoff (current)**
3. [`docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md`](docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md) — parent scoping (Chris-locked S2801; **MQ-T5-8 action item to update §4 T5 clause**)
4. [`docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md`](docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md) — T1 (S2811)
5. [`docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md`](docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md) — T2 (S2812)
6. [`docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md`](docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md) — T3 (S2813)
7. [`docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md`](docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md) — T4 (S2814)
8. [`docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md`](docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md) — T5 (S2815, cite as citation-graph + substrate source)
9. [`docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`](docs/research/DOMAIN_RESEARCH_PLAYBOOK.md) — arc process framework (v2)
10. [`docs/PLATFORM_INVENTORY.md`](docs/PLATFORM_INVENTORY.md) — runtime counts
11. [`docs/ENGINEERING_PLAYBOOK.md`](docs/ENGINEERING_PLAYBOOK.md) — v0.8.0 (v0.9 amendment WELL past threshold — 5/5 OP3 triggers)
12. [`docs/00-START-HERE/DOC_LIFECYCLE.md`](docs/00-START-HERE/DOC_LIFECYCLE.md) — §2c "sole authoritative counts source" (T3 §7 C5 falsifies at discovery layer; T6 will map drift across all rule surfaces)
13. [`logs/zoom_out_classifications.jsonl`](logs/zoom_out_classifications.jsonl) — 114 rows at S2815 close (unchanged all day)
