# Next Session — Start Here

---

## READ THIS FIRST — LOCAL vs PRODUCTION RIGBY TRAP

`tools/pa_chat.py:38` has `DEFAULT_BASE_URL = "https://donkey-betz-platform-production.up.railway.app"`. If you don't override `PA_API_URL`, every call goes to prod. The `.env` file's `PA_API_TOKEN` is also the **production** token.

### The correct LOCAL invocation
```bash
PA_API_URL=http://localhost:8000 \
PA_API_TOKEN=<local-chris-token>      \
.venv/bin/python tools/pa_chat.py "message" --conversation <id>
```

**Before your first `pa_chat.py` call each session, ask Rigby to run `platform_config_tool overview` and confirm `service_context: local`.**

The local wrapper at `tools/pa_local.sh` hardcodes the right token + conversation. **Active arc pin state after S1499 close:**

- **NO ACTIVE ARC PIN.** Group 1400 Revenue arc CLOSED at S1499; arc pin `pa-34d43795e1b24bd3` retired at S1499 close per D53 + playbook §16 arc-close discipline (`updated_count: 60`).
- **`tools/pa_local.sh` line 128 still points at retired `pa-34d43795e1b24bd3`** — update to fresh conversation pin at next-session open per pin_rotation_notice from Rigby's session_tool.retire response. Mint fresh via `session_tool.create_fresh` with appropriate title for the chosen next-session work (post-arc T1 ADR / Group 1500 open / cleanup PRs).
- **Recently retired at S1499 close (post-PR-merge):** `pa-877f1919efaa48e4` (S1499 SIGN isolation pin — 22 verdicts / 22 CONFIRM / 0 FLIP / 10 FLAG-EDIT framing refinements folded at commit-time; SIGN-with-edits cycle 1 substantive per D50 pattern; matches S1399 SIGN-clean cycle 1 pattern).
- **Retired at S1406 close:** `pa-8660ea7cfecd4bc6`.
- **Retired earlier:** `pa-4bdd5ad264674ce8` + `pa-637331c5f9574a10` (S1405); `pa-87ee24cd0d3947ce` (S1404); `pa-fba0c4c81fba4922` (S1403); `pa-4a0a28edcb7a45ec` (S1402); `pa-16d8b24d30e7a7d8` (S1401); `pa-aa54193f240f4846` + `pa-4fc3329d0db6484f` (S1399 Group 1300 arc-close).

Use `tools/pa_local.sh` for all chats — **update the hardcoded `--conversation` at line 128 to the fresh pin ID before first Rigby call**.

## READ THIS SECOND — GROUP 1400 REVENUE ARC CLOSED; POST-ARC PHASE OPEN

Session 1499 shipped the Group 1400 xx99 canonical summary at `docs/research/domains/revenue/1499_revenue_canonical_summary.md` (playbook §11.3 12-section template; 1915 lines; **second application of §10 "What This Research Taught Us About How to Do Research"** after S1399 close 2026-07-01). **Rigby SIGN-with-edits cycle 1 substantive** — 22 verdicts / 22 CONFIRM (0 FLIP) / 10 FLAG-EDIT framing refinements folded at commit-time / 0 must-fix / 0 severity flips; matches S1399 SIGN-clean cycle 1 pattern. Parent-Claude 12-checkpoint verifier-loop pre-SIGN caught 4 corrections + folded. ARCHITECTURE_INDEX v25 → v26 bump landed same-commit (§1.29 for S1499 canonical summary + §8 timeline S1499 row + frontmatter v26 preamble with Revenue high-coverage/integration-debt characterization). OPEN_ARCS Group 1400 row moved In-progress → Closed section. **Arc pin `pa-34d43795e1b24bd3` retired at arc-close** per D53 + playbook §16 (`updated_count: 60`). **32 D-decisions ratified across 7 sessions** (D24-D55; only D55 required explicit Chris pick; 31 landed via "agree all" default-lean confirmation).

**8-doc Group 1400 arc COMPLETE.** S1400 arc-open + 6 child audits (S1401 Cat A + S1402 Cat B + S1403 Cat C + S1404 Cat D + S1405 Cat E + S1406 Cat F) + S1499 canonical summary. ~11,715 lines across arc corpus.

**Load-bearing S1499 outputs to inherit at post-arc phase:**

- **5 arc-wide cross-cutting patterns confirmed:** F2 orphan-write 8 sites unanimous; F1 provenance-filter narrow-scope 2 sites; state-machine incomplete 4 models 62% unreachable; learning-loop incomplete 3 sites 2-bucket split; **runtime-owner MISSING UNANIMOUS 6/6 — arc headline finding**.
- **D55 (ii) two sibling JobContracts** ratified (Revenue Employee for Cat A/B/C/D/E + Income/Jobs Employee for Cat F). **T4 R.F3 = (b) DORMANT-PLANNED** Chris-lock — T3 Income/Jobs Employee JobContract SPEC'D but not activated (activation gate: post-T1/T5/T6/T7 foundations + explicit Chris re-ratification 30-60 day horizon per Rigby lean).
- **T1-T10 unified follow-on queue tier structure:** TIER 1 (T4 Chris-locked); TIER 2 umbrella ADRs (T1 parallel-schema/source-of-truth + T5 delivery+ingestion sequential ADR pair + T6 HAI interlock ship-to-go-live prerequisite + T7 write+routing authority PROMOTED from TIER 4 + T8 state-machine completion); TIER 3 Employee OS (T2 Revenue Employee + T3 Income/Jobs Employee spec'd not activated); TIER 4 cleanup (T9 phantom-fix + T10 Celery routing); TIER 5 optional.
- **§10 meta-methodology second application:** all 5 S1399-codified patterns REPLICATED. 4 new S1499 candidate patterns for playbook v3 codification pending third-arc validation (D48 stability-probe gate + D45 recovery pattern + provenance-stamp ORM probe + **parent-Claude 12/12 checkpoint precedent MET at 3-arc threshold — recommended for immediate codification**).

**Load-bearing methodology outputs of S1499 (inherit at post-arc phase):**

- **Parent-Claude 12/12 checkpoint precedent codification-ready.** 3-arc uses (S1404 + S1405 + S1406) MET threshold. Recommended playbook v3 §15 addition for next playbook process session.
- **Rigby SIGN worker-instability recovery pattern replicated at xx99 level itself.** S1499 SIGN pin first-turn triggered ~2400-word batch → worker instability → D45 recovery to titles-only 2-3-verdict batches → 22/22 CONFIRM delivered. Matches S1406 D48 gate precedent.
- **D54 fold pattern (Rigby SIGN failure → xx99 §5 synthesis) validated at 1-arc use.** Pending third-arc validation before playbook v3 codification.
- **Two-sibling JobContract shape** (D55 (ii)) as arc-close resolution for runtime-owner MISSING UNANIMOUS 6/6 — first library precedent for peer-sibling JobContract vs S1304 §18 single-employee shape. Employee OS 1200s arc informs future shape-decision precedent.

**Session close artifacts committed at S1499 close:**

```
docs/research/domains/revenue/1499_revenue_canonical_summary.md      [new; 1915 lines; status: active; sign_status: SIGN-with-edits cycle 1 substantive]
docs/research/ARCHITECTURE_INDEX.md                                  [modified — v25 → v26; §1.29 + §8 timeline + v26 preamble]
docs/research/OPEN_ARCS.md                                           [modified — Group 1400 moved In-progress → Closed]
00-START-NEXT-SESSION.md                                             [modified — this file]
docs/handoffs/SESSION_1499_REVENUE_CANONICAL_SUMMARY_ARC_CLOSE.md    [new — session handoff]
```

Handoff: `docs/handoffs/SESSION_1499_REVENUE_CANONICAL_SUMMARY_ARC_CLOSE.md`.

### NEXT-SESSION MISSION — POST-ARC PHASE (Chris chooses direction at session open)

Group 1400 Revenue arc CLOSED. Post-arc phase begins. **Chris ratifies direction at next-session open** — 3 candidate mission paths:

**Path A — T1 R.E3+R.A1+R.F2 parallel-schema + source-of-truth ADR kick-off** (highest-impact TIER 2 umbrella ADR per §8):
- Draft `docs/adr/00XX-parallel-schema-source-of-truth-revenue.md` per playbook §14.5 research boundary.
- Sub-cases per S1499 §5.2 fold: (a) domain modeling divergence (core Revenue vs intelligence RevenueRecord); (b) runtime/realtime representation divergence (mainline Opportunity vs intelligence_engine realtime).
- Design-preparation phase (not design-decision yet); reconciliation-policy design even if intentional-dual-schema.

**Path B — Group 1500 Sports/DBAO/Intelligence arc-open** (playbook §22 next queue):
- Second application of Chris's Phase 0 F.i/F.ii/F.iii methodology per S1400 D29 two-triggers gate.
- If Group 1500 applies framework unchanged at that arc's xx99 close, playbook v3 §11.1 template addition promotes.
- Parent scoping doc per playbook §11.1 template.

**Path C — Cleanup PRs bundle** (TIER 4 low-effort bounded landings from §8):
- T9 R.E1 4 × 1-line phantom-field fixes (`recorded_at` → `created_at`; `actual_outcome` → `outcome`; remove `notes=` kwarg; `hasattr` guard validation).
- T9 R.F1 `_impl_run_freelance_opportunity_scout` kwarg realignment (`required_skills` not `skills_required`; `gig_url` not `url`; remove `status`/`match_score`/`budget_range`).
- T10 R.A8 Celery route dedup at `settings.py:1277` (`long_running`) vs `:1484` (`content`).
- R.E5 view-file docstring hygiene for `views_revenue_tracking.py` 4 classes.

**Path D — Playbook v3 promotion session** (methodology work):
- Codify §10.2 patterns that hit two-triggers threshold: parent-Claude 12/12 checkpoint precedent (MET at 3-arc); F1/F4-CANDIDATE discipline (MET at 5-arc); sibling-inheritance hypothesis-correction (MET at 5-arc); docs cascade (Chris-ratified); meta-methodology §10 (Chris-ratified).
- Add playbook §14.5 evidence rule for owner-model-qualified consumer inventory.
- Add playbook §15 SIGN rule for pre-SIGN verifier-loop expectation.

**Also queued at post-arc:**
- Subsequent PRs from S1499 §7 anchor-updates: 6 `platform_architecture_inventory.md` §3.32 corrections + NEW `docs/topics/revenue-pipeline.md` first-inventory landing.
- CLAUDE.md 3-employees narrative anchor drift (actual: 4 per S1406 §5.4) → `verify_doc_claims --only-drift` verifier subsequent PR.
- Employee OS 1200s arc: T2 Revenue Employee JobContract implementation (T3 Income/Jobs stays SPEC'D but not activated per T4 R.F3 (b) lock).

**FIRST THING next session open:**
1. `context-kit orient`
2. Confirm `service_context: local` via `platform_config_tool overview` (per Rigby local trap)
3. Update `tools/pa_local.sh` line 128 — retired arc pin `pa-34d43795e1b24bd3` still hardcoded; mint fresh conversation pin via `session_tool.create_fresh` with title matching chosen path (Path A/B/C/D) + edit line 128 conversation ID.
4. Check if S1499 artifact set merged to `main` between sessions
5. If not yet merged: complete Chris merge action + PR merge
6. **Run post-merge docs cascade** per `feedback_docs_cascade_at_every_close.md`: `build_docs_index` → `build_rag_corpus` → `sync_docs_index_to_documents` → `embed_documents --all-unembedded` + `build_docs_provenance`
7. Chris ratifies path choice (A/B/C/D) via fresh Rigby pin
8. Execute chosen path

---

## PA / Rigby context

- **Arc pin at session start:** NONE (Group 1400 arc pin `pa-34d43795e1b24bd3` retired at S1499 close). Fresh pin required for next-session work.
- **S1499 SIGN pin retirement:** `pa-877f1919efaa48e4` retired post-fold via `session_tool.retire` at S1499 close (playbook §15 fresh isolation pin retirement rule).
- **PA Chat tool:** `tools/pa_local.sh "message"` (wrapper — sets URL + local token + conversation) — **line 128 conversation ID must be updated at next-session open** to fresh pin.
- **Local worker restart** needs `PA_USE_FUNCTION_CALLING=true` env or Rigby drops to keyword routing. `make celery` handles it; ad-hoc `celery -A core worker` does not.
- **Rigby SIGN worker-instability pattern (S1405+S1406+S1499 3-session confirmed):** if Rigby generic-errors on turn 1 of a fresh SIGN pin, apply D45 recovery pattern preemptively — warmup-ping first (ultra-short "confirm ready" probe), then batched titles-only SIGN 2-3 findings per prompt, then substantive Q10-Q13 pressure-test. D48 stability-probe gate CODIFICATION-READY at 3-arc use if Group 1500 replicates. Memory rules `feedback_rigby_sign_worker_instability_recovery.md` + `feedback_rigby_deliverable_content.md` + `feedback_rigby_tool_verification.md` apply.
- **Non-standard pa_chat.py invocation for fresh SIGN pin:** `tools/pa_local.sh` hardcodes `--conversation` — for fresh SIGN pin, use direct pa_chat.py invocation with env vars: `PA_API_URL=http://localhost:8000 PA_API_TOKEN=<local-token> .venv/bin/python tools/pa_chat.py "$(cat /tmp/msg.txt)" --tools --conversation <fresh-pin-id>` — write prompt to file first to avoid shell backtick interpretation.

## Repo state at next-session open

- **Branch state (at S1499 close, before merge):** `docs/session-1499-revenue-canonical-summary` PR opens to `main` on push. If merged between sessions, working tree clean and next session branches off `main`.
- **Handoff continuity:** S1499 handoff at `docs/handoffs/SESSION_1499_REVENUE_CANONICAL_SUMMARY_ARC_CLOSE.md`. Prior handoffs: SESSION_1406 (Cat F final); SESSION_1405 (Cat E); SESSION_1404 (Cat D); SESSION_1403 (Cat C); SESSION_1402 (Cat B); SESSION_1401 (Cat A); SESSION_1400 (Group 1400 arc open); SESSION_1399 (Group 1300 canonical summary — first xx99); SESSION_1300-SESSION_1305 (Group 1300 children).
- **ARCHITECTURE_INDEX version:** v26 (bumped this session with §1.29 S1499 canonical summary + §8 timeline row + v26 preamble). Next bump depends on chosen post-arc path.
- **OPEN_ARCS state:** Group 1400 row moved In-progress → Closed section with S1499 canonical summary listed as arc-closing doc. In-progress section now empty; next arc-open populates it.

## Next-session first-action punch list

- [ ] `context-kit orient`
- [ ] Confirm `service_context: local` via `platform_config_tool overview`
- [ ] Update `tools/pa_local.sh` line 128 to fresh conversation pin (retired arc pin `pa-34d43795e1b24bd3` still hardcoded)
- [ ] Check if S1499 artifact set is on `main` — if yes, next session branches off `main`
- [ ] Run post-merge docs cascade if not yet run per `feedback_docs_cascade_at_every_close.md`
- [ ] Chris ratifies post-arc path choice via fresh Rigby pin: (A) T1 parallel-schema + source-of-truth ADR / (B) Group 1500 arc-open + Phase 0 methodology second application / (C) TIER 4 cleanup PRs bundle (T9+T10+R.E5) / (D) Playbook v3 promotion session
- [ ] Execute chosen path per playbook + Research OS discipline

## Reference — where to look

- **Group 1400 canonical summary:** `docs/research/domains/revenue/1499_revenue_canonical_summary.md` — arc-close synthesis + T1-T10 follow-on queue + Employee OS ownership resolution
- **Group 1400 parent scoping doc:** `docs/research/domains/revenue/1400_revenue_domain_scoping.md`
- **Group 1400 child audits:** `docs/research/domains/revenue/1401_*.md` through `1406_*.md`
- **Playbook:** `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.3 canonical summary template + §15 SIGN + §16 arc-close + §17 graduation + §22 next-arc queue)
- **Research OS:** `docs/research/process/RESEARCH_OPERATING_SYSTEM.md`
- **ARCHITECTURE_INDEX v26:** `docs/research/ARCHITECTURE_INDEX.md` — S1499 §1.29 + §8 timeline + v26 preamble
- **OPEN_ARCS:** `docs/research/OPEN_ARCS.md` — Group 1400 Closed section (with S1399 Group 1300)
- **AUDIT_FINDINGS.md #12:** canonical Celery deferred-by-policy list
- **Inventory anchor:** `docs/PLATFORM_INVENTORY.md`
- **Narrative anchor:** `docs/PLATFORM_WHAT_IT_IS.md`
- **S1399 canonical summary:** `docs/research/domains/memory/1399_memory_canonical_summary.md` — first application of playbook §11.3 §10 template (precedent for S1499 second)

## Doctor warnings to expect

- Inventory freshness (stale) — `python manage.py generate_platform_inventory --write` to refresh; S1499 does not update inventory rows (canonical summary only)
- Handoff numbering continuity — legitimate; S1306-S1398 skipped by intent per Rigby lean at S1300 close; Chris's arc-numbering convention preserved for Group 1400 (S1401-S1406 + S1499)
- Narrative anchor freshness — `PLATFORM_WHAT_IT_IS.md` dated 2026-05-24 is older than latest handoff (informational; S1499 §7 will propose narrative updates for subsequent PR)
- Docs cascade — run 4-step cascade + `build_docs_provenance` after S1499 PR merges to `main` per memory rule `feedback_docs_cascade_at_every_close.md`
- CLAUDE.md 3-vs-4 employees narrative drift — flagged for `verify_doc_claims --only-drift` verifier subsequent PR (per S1499 §7.2 fold)
- `tools/pa_local.sh` line 128 hardcoded conversation still points at retired arc pin `pa-34d43795e1b24bd3` — update to fresh pin ID at next-session open (per pin_rotation_notice from session_tool.retire response)
