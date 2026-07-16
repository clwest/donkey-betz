# Session 2797 — Public landing page at `/welcome` (first user-visible market ship)

**Date:** 2026-07-15
**Session:** S2797
**Branch/PR:** `s2797-public-landing-page` → **PR #3207** (merged as `63aa705f5`)
**Predecessor:** [SESSION_2796_TD_HANDLERS_OPS_SLICE1.md](SESSION_2796_TD_HANDLERS_OPS_SLICE1.md)
**Playbook:** v0.8.0 (205 rules) — unchanged
**Recycle cycle:** thirty-seventh post-PLAYBOOK-7.4.4

---

## §1 — Ship summary

**First user-visible market-shipping ship** after 10 consecutive substrate sessions. Adds public unauth `/welcome` route — a URL Chris can share with prospects. Complements S2796's persisted `project_market_shipping_priority_2026_07_15` directive.

**Ship shape A (Rigby SIGN-WITH-EDITS with 4 mitigations adopted):**

- New unauth route `/welcome` → `LandingPage.tsx` (~280 lines)
- Two mailto CTAs — primary open-ended + secondary with pre-filled structured lead-quality body
- Copy in editable constants at top of file — Chris iterates without touching JSX
- Ultra-static — no auth checks, no API calls, no analytics, no live widgets
- `/` UNCHANGED — still `CommandCenterPage` (root-domain discoverability deferred as future_trigger)
- LoginPage tweak: "New here? Learn more →" link to `/welcome`

**T2 pivot — copy corrected from sports-betting to "AI with receipts" framing:**

At T1 I anchored on the name and skipped `docs/PLATFORM_WHAT_IT_IS.md` — directly violated `feedback_cycle_1a_verify_before_build`. Chris caught it at T2 review: "why is the Welcome focused on sports betting if that's not the core part of the platform?" Sports betting is one of ~5 output types per the anchor doc; the actual differentiator is the verifiable operating model. Rewrote copy to lead with **"AI with receipts"**, feature the two-AI operating model (Claude proposes, Rigby verifies with tool_runs, both cite evidence), and added a new **"How it looks in practice"** section pulling 3 real session examples from S2795 / S2796 / S2797.

**Files changed (4):**

| File | Change | Purpose |
|------|--------|---------|
| `frontend/src/pages/LandingPage.tsx` | new (~280 lines, including T2 copy rewrite) | Public landing page with operating-model framing + 3 real session examples |
| `frontend/src/App.tsx` | +8 lines | Wire `/welcome` unauth route |
| `frontend/src/pages/LoginPage.tsx` | +8 lines | "New here? Learn more →" link |
| `tools/pa_local.sh` | +1 / -1 | Fresh S2797 pin `pa-4eed0b501f284250` |

**Verification:**

- `npm run typecheck` — zero new errors from changed files (pre-existing errors in `WorkspacePageNew.tsx` + `paStore.ts` unchanged)
- `npm run dev` starts clean at port 3000
- `make frontend-ship` — built + collectstatic + Daphne restart
- **Chris visually verified** at `http://localhost:8000/welcome` and approved T2 copy ("I think that looks great")

**Ledger state at close:** `logs/zoom_out_classifications.jsonl` — **72 rows** (29 `same_pr_actionable` / 23 `same_pr_mitigatable` / 16 `future_trigger`). Rows 69-72 are S2797 F1-F4 folds.

---

## §2 — Novel-precedent moments

**First user-visible market-shipping PR after 10 sessions of substrate.** Direct payoff of the `project_market_shipping_priority_2026_07_15` signal persisted at S2796 open. Bias toward user-visible leans held at S2797 open — Chris confirmed the shift ("go with your lean, that's fine").

**First Chris-caught positioning miss at review.** T1 ship shipped copy anchored on the name (sports betting). T2 Chris review flagged the miss: "sports betting isn't the core." Root cause: I skipped `docs/PLATFORM_WHAT_IT_IS.md` before writing marketing copy, despite it being source #1 in `context-kit orient`. Direct `feedback_cycle_1a_verify_before_build` violation. Chris caught it before merge — human-in-the-loop verification working as designed. **This exact moment became landing-page content:** the S2797 T1 example in the "How it looks in practice" section is Rigby's SIGN admission that she couldn't fully certify V4 without an extra file read. The verifiable-AI pattern is self-illustrating.

**First landing page whose "proof" section is real session data.** The 3 examples in the "How it looks in practice" section are literal Rigby SIGN receipts:
- S2795 duplicate-work catch (Rigby found `build_pa_tool_audit` before Claude built a parallel command)
- S2796 over-claiming pushback (Rigby's F1 evidence-admission fold)
- S2797 live-in-this-session verification-limits admission (Rigby's V4 "I did the search, didn't do the direct read, can't strictly certify")

The receipts are the marketing.

**First ship where the T2 pivot commit message explicitly names the T1 miss.** T2 commit body reads: *"I anchored on the name and skipped the anchor doc. Direct violation of `feedback_cycle_1a_verify_before_build`. Chris caught it before merge — exactly the human-in-the-loop pattern this platform is built around."* Codifying the miss in the commit history is the same evidence-admission discipline we ship as product.

---

## §3 — T1 + T2 SIGN cycles detail

**Pin:** `pa-4eed0b501f284250` (label `s2797-user-visible-scoping`), minted at S2797 T1 open via `session_lifecycle open`. Freshness FRESH · SHA-match at mint. **Retire scheduled at S2797 close** (force=true, twenty-eighth consecutive per S2770+ pattern).

### T1 SIGN cycle (landing-page scoping)

Presented Chris-picked lean (candidate #1 — public landing page) + 4 verification claims + 4 zoom-out asks. Rigby responded with 3 `repo_tool` calls (including repo-wide `search` for "Waitlist" returning 0 matches).

Rigby verdict: **SIGN-WITH-EDITS**. V1-V3 AGREE. V4 SIGN-WITH-EDITS (repo-wide search strongly supports the "no Waitlist model" claim, but she flagged she couldn't strictly certify without a direct `core/models.py` read — non-blocking since Shape A doesn't need a Waitlist model).

**4 folds classified + persisted BEFORE Chris D-verdict per PLAYBOOK-6.10.8:**

| # | Ledger row | Class | Fold |
|---|-----------|-------|------|
| F1 | 69 | `same_pr_actionable` | Landing page ultra-static — no auth checks / API calls / analytics / live widgets |
| F2 | 70 | `same_pr_actionable` | Two mailto CTAs — primary open-ended + secondary pre-filled with structured lead-quality body |
| F3 | 71 | `same_pr_actionable` | Copy in editable constants at top of `LandingPage.tsx` — Chris iterates without touching JSX |
| F4 | 72 | `future_trigger` | `/welcome`-off-`/` discoverability risk deferred; triggers on first prospect complaint / inbound organic traffic |

### T2 pivot (copy correction)

Chris review of built page at `http://localhost:8000/welcome`: *"why is the Welcome focused on sports betting if that's not the core part of the platform?"*

Read `docs/PLATFORM_WHAT_IT_IS.md` (should have done at T1 open). Confirmed platform is autonomous multi-agent intelligence with ~5 output types (content / decisions / stock briefs / sports bets / code) — sports betting is one output, not the core.

Proposed 3 positioning framings + option to write his own. Chris picked **"AI with receipts"** and requested **real examples** from the sessions we've been building. Wrote T2 copy pivot in one pass; rebuilt via `make frontend-ship`; Chris visually approved.

**No new folds at T2** — the copy pivot is a same-PR correction, not a new SIGN cycle with concerns. The T1 folds remain load-bearing.

### T3 tagline tightening (post-merge, close-cascade)

Post-merge, Chris asked: *"Is it too late to change the tagline to something like: AI with receipts. One AI proposes. One AI verifies. You decide with proof."* Answer: no — copy is in editable constants per Rigby F3 exactly for this. Updated:

- `hero_headline`: "AI that shows its work." → **"AI with receipts."**
- `hero_sub`: prose paragraph → **"One AI proposes. One AI verifies. You decide with proof."**

Rebuilt via `make frontend-ship`, Chris re-verified at `http://localhost:8000/welcome` and approved. Bundled into the S2797 close-cascade PR. **This T3 iteration is direct evidence of the Rigby F3 pattern working as intended — copy iteration without a code-touch, without another SIGN cycle, without a full PR round-trip.**

---

## §4 — Constitutional posture

- **Playbook v0.8.0 (205 rules)** — unchanged
- **PLAYBOOK-6.10.7** zoom-out ask: ✅ Z1-Z4 explicit asks; drove 4 folds
- **PLAYBOOK-6.10.8** fold classify+persist BEFORE D-verdict: ✅ rows 69-72 persisted before Chris "go with your lean"
- **PLAYBOOK-6.10.9** evidence admission: ✅ V4 SIGN-WITH-EDITS honestly admits verification limits; stable-state pointer `5994883a2309` + file+line evidence for all claims
- **PLAYBOOK-7.4.4** recycle-after-merge: ✅ `make recycle-all` initiated post-merge (thirty-seventh cycle)
- **`feedback_engineering_bias_over_audit`**: ✅ net-new engineering (engineering-first session #11 in row); market-shipping refinement per `project_market_shipping_priority`
- **`feedback_cycle_1a_verify_before_build`**: ⚠️ **VIOLATED at T1** (skipped `PLATFORM_WHAT_IT_IS.md` before writing marketing copy). Chris caught at T2 review. Corrected via same-PR pivot. Rule holds — the failure is instructive, not the failure of the rule.
- **`feedback_verify_rigby_tool_runs_before_trusting_sign`**: ✅ 3+ tool_runs verified before trusting T1 SIGN; V4 partial-verification honestly flagged
- **`feedback_claude_rigby_agree_first_chris_yes_no`**: ✅ joint recommendation before Chris D-verdict at T1; T2 correction is a Chris-driven revision, not a Rigby-Chris disagreement
- **`feedback_zoom_out_ask_per_rigby_sign`**: ✅ Z1-Z4 asks
- **`project_market_shipping_priority_2026_07_15`**: ✅ first user-visible ship after directive was persisted
- **`feedback_local_truth_no_production`**: ✅ local pass = shipped; Chris visually verified at localhost:8000
- **`feedback_gh_pr_merge_admin_until_billing_fixed`**: ✅ `--admin` flag on merge

---

## §5 — Twin-pointer card

📁 **Repo `/` + `/docs/` — S2797 artifacts:**

- **Ship page:** `frontend/src/pages/LandingPage.tsx` (~280 lines; copy in `COPY = {}` constants at top-of-file per Rigby F3)
- **Route wiring:** `frontend/src/App.tsx` lines 5-6 (import) + wiring under unauth block (after `/login`)
- **Login link back:** `frontend/src/pages/LoginPage.tsx` (bottom of form)
- **Handoff:** `docs/handoffs/SESSION_2797_PUBLIC_LANDING_PAGE.md` (this file)
- **PR:** [#3207](https://github.com/clwest/donkey-betz-platform/pull/3207) merged as `63aa705f5`
- **Live URL (local):** `http://localhost:8000/welcome`
- **Predecessors:** S2796 (market-shipping priority signal + gap-map slice), S2795 (gap map ship), S2733 (validation campaign retrospective)

🖥️ **Workspace UI — `/workspaces` surface:**

- **No Workspace tab this ship** — LandingPage is public marketing surface, not a workspace tab
- **Live surfaces at close:**
  - `logs/zoom_out_classifications.jsonl` — **72 rows** (29/23/16); rows 69-72 are S2797 F1-F4
  - `logs/recycle_events.jsonl` — +1 event (post-#3207, sha=`63aa705f5`)
  - `http://localhost:8000/welcome` — first user-visible market surface

---

## §6 — Open items / follow-ups

### Immediate follow-ups

- **Copy iteration** — Chris can edit `COPY = {}` constants in `LandingPage.tsx` and rebuild (`make frontend-ship`) without another PR
- **Real-world testing** — first share of `donkeybetz.com/welcome` (or equivalent public URL) with a prospect will test the mailto funnel + copy positioning
- **F4 discoverability trigger conditions** — fire on: (a) first prospect complaint about landing at `/login`; (b) inbound organic traffic observed in logs; (c) Chris switches from manual to broader outreach

### Deferred to future sessions (per S2797 F3 mitigation + market-shipping priority)

- **Onboarding / signup flow** — first-user routing to `/betting` (or a "first useful thing to do") after auth. Currently authenticated users land at `/` = CommandCenterPage (Chris's operator tool, not a first-user surface).
- **Waitlist DB capture (Shape B)** — if mailto quality/volume becomes insufficient; trigger: first Chris signal that emails are noisy or missing structured data
- **Public deployment** — landing page is local-only until hosted. Requires: (a) production hosting decision; (b) DNS pointing donkeybetz.com to `/welcome`; (c) auth-app split (e.g. `app.donkeybetz.com`) if we don't want root domain to be marketing
- **BettingPage first-user trace** — 9-tab, 3023-line surface; unknown state for a first user. Candidate deferred at S2797 candidate menu (#3).
- **Second real-example refresh** — as more sessions accumulate, the 3 examples in "How it looks in practice" may be worth refreshing to feature more recent / more compelling receipts

### Still outstanding (unchanged from S2796 close)

- **F4 (telemetry-backed complaints) future_trigger** — fires when `tool_call_error_rate` query surface exists
- **`diagnostics_tool` 3 PR-2 placeholder actions** — implement or remove
- **`status_snapshot_tool` version-source reconciliation**
- **`active_priority_tool` TTL clamp verification**
- **Regression tests for 4 S2796 validation docs**
- **8 remaining per-tool docs need "Covered actions" flat-list sections**
- **23 tools schema-lint `actions_not_mentioned_in_description`**
- **I-0303 scoping open** — RUR-C1 parent-close direct blocker
- **`SESSION_819_SYSTEM_AUDIT_*` cleanup** — 16 untracked files
- **Model drift arc** — 38+ auto-migrations queued
- **Doc-note the gap-map classifier h3-truncation bug** in the S2795 F2 template spec

---

## §7 — Repo state at close

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `63aa705f5` (S2797 ship #3207) — cascade PR advances this at close |
| Playbook version | v0.8.0 (unchanged) |
| Playbook rule count | 205 (unchanged) |
| RUR-C1 state | Unchanged; I-0303 still not opened |
| Session pin | `pa-4eed0b501f284250` (retire at S2797 close, force=true, twenty-eighth consecutive) |
| Wrapper default pin | `tools/pa_local.sh` — `pa-4eed0b501f284250` (retired at close; forces fresh mint at S2798 open) |
| Postgres :5432 | pg15 (July DB) — brew launchd `started` |
| Freshness log | `logs/session_freshness.jsonl` — grew by 1 at S2797 open |
| Recycle log | `logs/recycle_events.jsonl` — +1 event (post-#3207) |
| Zoom-out ledger | `logs/zoom_out_classifications.jsonl` — **72 rows** (29 actionable / 23 mitigatable / 16 future_trigger) |
| PA tool audit | `docs/PA_TOOL_AUDIT.md` — unchanged (no code changes to PA tools this ship) |
| PA tools gap map | `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` — unchanged (last regen at S2796 close) |
| **Public marketing surface** | **`http://localhost:8000/welcome` — first user-visible market ship live locally** |
