# Session 2810 — Attorney sub-form on Case Wizard (row-112 shipped)

**Date:** 2026-07-18 (opened mid-day after S2809 close; mid-afternoon close)
**Session:** S2810
**PRs shipped:** 1 — **PR #3237** (`7de622f24`)
**Predecessor:** [SESSION_2809 P1 back-port](SESSION_2809_P1_BACK_PORT_LESSON3_HARDENING.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** 1 post-merge clean recycle (+ close-cascade recycle to come)

---

## §1 — Ship summary

**One PR shipped, merged with `--admin --squash --delete-branch`. +129 / −2 LOC across 1 file.**

### PR #3237 — Attorney sub-form on Case Wizard (row-112 emergent)

Wires attorney details capture into the Case Wizard modal when a party unchecks "Representing self (pro se)." Backend already handled the payload at `core/views_legal_cases.py:96-160` — this ships the 90%-built substrate that was only missing wizard input.

**Frontend changes (one file: `CreateCaseWizardModal.tsx`, +129/-2 LOC):**
- New `AttorneyForm` interface (9 fields matching backend Attorney model: full_name, firm_name, address/city/state/zip, phone, email, bar_number)
- `PartyForm.attorney: AttorneyForm | null` — null when pro se, populated when represented
- `EMPTY_ATTORNEY` const + `EMPTY_PARTY.attorney = null`
- `AttorneySection` sub-component (subtle bordered card, "Attorney details" heading, 9 field inputs mirroring `PartySection` density)
- `PartySection` inline-expands `AttorneySection` when `!is_pro_se`; toggling the pro-se checkbox creates fresh attorney (unchecked→represented) or clears to null (checked→pro se)
- `handleSubmit` validation: `attorney.full_name` required when `!is_pro_se` (matches implicit backend contract)
- **Payload guard (Rigby SIGN Q3 mitigation):** strip `attorney` sub-object when `full_name` empty OR party is pro se — prevents backend from receiving stray `attorney: {}` that would create hollow Attorney rows

**Value unlock (Rigby tool_runs at SIGN time surfaced this):**
- `legal_doc_drafter_agent.py:4612-4620` already reads `respondent.attorney` and injects `respondent_counsel_name/first_name/email/firm/address` into the motion drafting prompt
- `CaseProfile.get_conferral_recipient()` at `models_legal.py:107-121` uses attorney for conferral-email addressing

Both consumers were wired and waiting; this small wizard patch retroactively lights them up.

---

## §2 — Rigby joint SIGN cycle

**Pin:** `pa-8199cbf50c6e44ac` (S2810 open-ceremony fresh mint post-S2809-close, retired at S2810 close)
**Verdict:** **AGREE across all 3 questions** on the attorney sub-form scope

**Anti-rubber-stamp check:** **PASSED** — Rigby's tool_runs on the shape SIGN included multiple `repo_tool` invocations verifying (a) backend attorney payload handling at `views_legal_cases.py:112-160`, (b) drafter agent consumer at `legal_doc_drafter_agent.py:4612-4620`, (c) `Party.attorney` @property at `models_legal.py:193`, and (d) `get_conferral_recipient` usage at agent line 4623. Every claim in the SIGN dispatch tool-verified.

**3 SIGN questions + verdicts:**

1. **Q1 (UX shape): AGREE-A (inline expand).** Attorney contextually bound to party, no scroll-to-bottom association loss. Simplest interaction; matches user's mental model ("who represents this party").
2. **Q2 (bar_number required?): AGREE optional.** Backend has `blank=True`; requiring adds intake friction; many users don't have it handy at case-creation time.
3. **Q3 (ZOOM-OUT): AGREE with two mitigations.** (i) Require minimal subset when represented — attorney.full_name; (ii) Only include attorney object in payload when meaningful fields provided. Both implemented in `handleSubmit`.

**No zoom-out folds persisted this session.** Ledger holds at 114 rows (unchanged from S2808/S2809).

---

## §3 — Novel-precedent moments

**A. Third consecutive anchor-verify catch in a single session** — this one bigger than the earlier two. The `colorado_family_law_spider.fetch_data` reads-hardcoded-list finding pivoted S2810 mid-flight from "Phase 5 spider beat" to "attorney sub-form." First time we've pivoted an entire scope this deep into a session based on a live-code check.

**B. First same-session multi-pivot chain governed by anchor-verify.** Sequence: audit clean → Phase 5 spider beat scoped → Rigby joint SIGN AGREE → anchor-verify catch (`_get_comprehensive_forms` hardcoded) → Phase 5 rejected → attorney sub-form (row-112) picked → anchor-verify catch (backend already handles payload) → scope reduced to frontend-only → Rigby joint SIGN AGREE → ship. **Two live-code discoveries reshaped scope twice inside one session.** Both saved cycles.

**C. First feature ship that retroactively lights up two backend consumers.** The wizard patch collects attorney data → Party.attorney FK → drafter's `respondent_counsel_*` injection AND conferral-email routing both light up. This is exactly the shape "predicate substrate exists ahead of user-facing surface" that the Colorado arc has been building toward.

**D. Fourteenth-consecutive same-day multi-ship session** — S2797 → ... → S2809 → **S2810**. First back-to-back same-day multi-ship (S2809 and S2810 both closed on 2026-07-18).

---

## §4 — Session-open infra story

**S2810 opened mid-day after S2809 close.** Wrapper `tools/pa_local.sh` pointed at `pa-126c19b80e504be2` (retired at S2809 close). First-action fresh mint: `pa-8199cbf50c6e44ac` labeled `s2810-legal-doesnotexist-bareexcept-audit` (original scope; kept the label even after mid-session pivot). Freshness FRESH · head `d9271f7890d5` · 0/5 stale workers. Ledger 114 rows verified.

**Anti-Lesson-3 audit finding (folded into this handoff per Rigby+Claude joint AGREE on A+C combined):**
- `core/agents/legal/**` sweep: only one `except X: pass` hit — `legal_doc_drafter_agent.py:3836` `except ValueError: pass` inside `extract_date()` regex parser, falls through to `return None`. Legitimate feature-detection pattern.
- Two remaining `except .*DoesNotExist:` sites (lines 1605 + 4574) both already `logger.warning`.
- All 17 `except Exception as e:` handlers log; zero bare `except:`.
- Adjacent legal files (`views_legal.py`, `models_legal.py`, `services/legal_*`) — no new hits.
- **Conclusion:** S2809's back-port was the only Lesson-3 violation in the entire legal codepath. Anti-Lesson-3 scope is closed. No follow-up PR needed.

**Colorado Family Law spider anchor-verify (pivot trigger):**
- `ai_core/spiders/specialized/colorado_family_law_spider.py:222` — `fetch_data` reads `self._get_comprehensive_forms()` (hardcoded static Python list of ~15-25 forms) instead of using the fully-defined Playwright infrastructure at lines 103-214
- Session 534 comment (line 232-234) explicitly documents the punt: "the Colorado Judicial website uses complex AJAX that's difficult to scrape reliably with Playwright. The KEY_FORMS list contains the most important family law forms."
- Impact on Phase 5 scoping: a monthly beat schedule as-scoped would re-emit the same hardcoded list every month, item-hash dedup would skip duplicates, corpus grows by zero. Zero user-value ship.
- **Pivot:** Rejected Phase 5 as scoped. Real Phase 5 (Phase 5.1?) = un-punt Session 534 by fixing `fetch_data` to actually crawl. Deferred to a session willing to take on AJAX debugging with unknowable time budget.

---

## §5 — Twin-pointer card

📁 **Repo — S2810 artifacts:**

- **PR (1, merged):** #3237 (`7de622f24`)
- **Substrate change:** `frontend/src/pages/legal/CreateCaseWizardModal.tsx` — +129/-2 LOC
- **Backend unchanged.** All plumbing was pre-existing at `core/views_legal_cases.py:96-160`, `core/models_legal.py:107-249`, and `core/agents/legal/legal_doc_drafter_agent.py:4612-4620`.
- **Handoff:** `docs/handoffs/SESSION_2810_ATTORNEY_SUBFORM_WIZARD.md`
- **Ledger:** `logs/zoom_out_classifications.jsonl` — **114 rows** (unchanged; no folds persisted)
- **Merge SHA:** `7de622f24` (feature) → close-cascade SHA filled at cascade merge

🖥️ **Workspace UI — `/workspaces` surface:**

- **`http://localhost:8000/legal`** — click "New Case" → wizard opens → uncheck "Representing self (pro se)" on Petitioner or Respondent → attorney sub-form inline expands with 9 fields (full_name required, others optional) → submit creates both Party + Attorney rows in one round-trip.
- **Downstream visibility:** Motion drafts for cases with an attached attorney will now include correctly-named opposing counsel + firm + address in the drafting context via `respondent_counsel_*` prompt injection. Conferral-recipient emails route to opposing counsel when represented.
- **Twin workspace deliverable:** N/A this session; substrate ships directly.

---

## §6 — Next session (S2811) — candidates

**Colorado arc state at S2810 close (unchanged Phase-list; +1 wizard capability):**
- All correctness substrate closed (P0, P1 Lesson-3 hardened, P1.b)
- One case-management capability shipped (Phase 3.2 wizard) — **now with attorney sub-form (S2810 row-112)**
- One user-facing intelligence surface shipped (Phase 4a form-selection)
- 14 consecutive same-day multi-ships (S2797 → S2810)

### Candidates for S2811

**Small / mechanical:**
- **`LegalDocument.generation_context` add `blank=True`** (Phase 2 model quirk from S2803 handoff)
- **`LegalDocumentIngestor` + `LegalContextBuilder` unscoped-query hardening** (Phase 2 punt)

**Medium:**
- **Phase 4 — Statute-citation content quality** (C.R.S. § 14-10-129 language quality)
- **⭐ NEW: Un-punt Session 534 — restore live scraping in `colorado_family_law_spider.fetch_data`** (Phase 5.1). AJAX wrangling with unknowable time budget; treat as its own arc.
- **GPT fallback for form-selection** when keyword-match is low-confidence (row-114 emergent)

**Large:**
- **Phase 4b — LLM-based situation intelligence** (P4a natural upgrade)
- **Wizard extraction to `/legal/cases/new`** route (row-112 emergent; deep-link + draft-persistence + browser-back)
- **7,829-line `legal_doc_drafter_agent.py` mechanical split**

**Non-Colorado arcs (still queued):**
- **Group 2700 /docs restructuring** (queued since S2801; 14 sessions bumped)
- **BettingPage first-user trace**
- **Stock Intelligence**

**Recommended default:** Chris picks fresh at S2811. If the Phase 5.1 AJAX quest appeals, it's the most net-new. If a smaller warm-up, the `blank=True` quirk fix is the safest.

---

## §7 — Chris D-verdict queue

All D-verdicts recorded in-session:

- Continuation authorization ("Let's continue if we have context and room to grow")
- Post-audit direction ("What is you and Rigby's suggestion?" → deferred to joint)
- Phase 5 cadence ("monthly, first Sunday of August" — later mooted by anchor-verify pivot)
- Reframe acceptance ("your call on AJAX lol" — Claude picked attorney sub-form)
- Ship authorization ("ship it")

**No unresolved F-BLOCKING items at close.**

**Emerging scope acknowledged but not derailing:** Phase 5.1 (un-punt Session 534 AJAX scraping) — deferred to its own arc; all prior S2808/S2809 candidates still queued.
