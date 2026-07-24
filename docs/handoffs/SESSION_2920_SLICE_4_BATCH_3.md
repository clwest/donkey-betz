# Session 2920 — Slice 4 batch 3 (gateway medium-tier read-only trio via template-preservation swap)

**Date:** 2026-07-23
**Branch merged:** `s2920-slice4-batch3` → `main` at `fd4c9d5b0`
**PR:** [#3470](https://github.com/clwest/donkey-betz-platform/pull/3470)
**Duration:** single session, ~2 hours end-to-end
**HEAD at open:** `9561a1932` (S2919 close cascade)
**HEAD at close:** `<TBD>` (this session's close cascade)

---

## Executive summary

Slice 4 batch 3 shipped **3** pure-read gateway tools (mobile 126 · calendar 84 · conceptforge 82 lines) via S2796 doc-only shape after template-preservation swap dropped 3 mutation-capable candidates. **11/17 shipped**.

Original Chris-ratified quartet (mobile + calendar + proactive + self_awareness) collapsed to a trio when Rigby T0 SIGN turn 1 verb-scan flagged mutations in proactive (`.update`×3) + self_awareness (`.create`×1). Attempted swap of proactive+self_awareness for profile+conceptforge in turn 2 was partially blocked when profile also mutated (`.save` at 2415 + `get_or_create()`). Escalated to split-batch: ship the 3 clean read-only tools (mobile + calendar + conceptforge), defer the 3 mutation-capable tools (proactive + self_awareness + profile) to next-session shape-decision SIGN cycle.

Post-merge live verify: all 3 clean at ≤11ms (mobile 4ms / calendar 10ms / conceptforge 11ms). No dev-env drift.

---

## Rigby joint SIGN — 2-turn cycle + Q4 zoom-out, zero rubber-stamp

### T0 SIGN turn 1 — corrected span math + verb-scan flags mutations

- 8 \`repo_tool\` runs (4 handler-anchor searches + 4 boundary reads).
- Corrected 00-START span table:
  - mobile: 814-939 (126 lines; 00-START claimed 127 — minor)
  - proactive: 1560-1697 (138 lines; 00-START claimed 140 — minor)
  - **calendar: 1793-1876 (84 lines; 00-START claimed 166 — MATERIAL, second consecutive session with calendar-span burn: S2919 caught 86 vs 166, S2920 caught 166 vs 84)**
  - self_awareness: 2482-2597 (116 lines; 00-START claimed 118 — minor)
- Verb-scan:
  - mobile: 0/4 mutation verbs → CLEAN
  - proactive: `.update`×3 (`ProactiveAlert.objects.filter(id=alert_id).update(...)` etc.) → MUTATION-CAPABLE
  - calendar: 0/4 → CLEAN
  - self_awareness: `.create`×1 → MUTATION-CAPABLE
- Q1 DISAGREE — refused doc-only sign on original composition.
- Q3 DO NOT AGREE — mutation presence triggers §5a deferral or shape-break; do NOT proceed with uniform doc-only S2796 shape.
- Q2 AGREE per-tool: 0/4 first-hop literals (Appendix N gateway-wide 0/17 continues to hold).

### T0 SIGN turn 2 — swap attempt partially blocked

- Proposed swap: proactive → profile, self_awareness → conceptforge.
- 2 more `repo_tool` runs (handler-anchor searches for profile + conceptforge).
- Verb-scan of swap-ins:
  - conceptforge: 2210-2291 (82 lines; 0/4 verbs) → CLEAN
  - **profile: 2294-2479 (186 lines; `.save`×1 at line 2415 + `EnhancedUserProfile.objects.get_or_create(...)` creation-capable but not matching `.create(` literal grep) → MUTATION-CAPABLE**
- Escalation per turn-1 instruction: split-batch.
  - Ship read-only trio: mobile + calendar + conceptforge.
  - Defer mutation-capable trio: proactive + self_awareness + profile → next-session shape-decision SIGN cycle.

### Q4 zoom-out (per feedback_zoom_out_ask_per_rigby_sign)

- **(a) Legacy-error envelope semantic nuance:** Rigby pushback — sweep guidance should treat `error_code` VALUES as first-class semantics, not just field presence/absence. Substrate arc framing may need refresh; still gated on explicit Chris directive.
- **(b) Codify mutation-scan-swap as explicit template guidance:** Rigby AGREE. 2 triggers now (S2919 vip_invite→narrative + S2920 proactive+self_awareness+profile→conceptforge). Joint recommendation to Chris to codify in sweep-doc or Playbook amendment at S2921.
- **(c) Accretion risk 8/17 → 11/17:** template drift risk unless we formally split "read-only doc-only" vs "mutation-capable" tool-handling templates. Otherwise exceptions accumulate and weaken SIGN standards.
- **(d) Cockpit (431 lines):** still defer to dedicated batch until mutation-shape template is settled — cockpit would amplify ambiguity.

### Chris D-verdict — mid-flight

Chris ratified option (a) at session open (medium-tier read-only pilot). After Rigby SIGN uncovered mutations, joint recommendation presented in plain English with two questions ("Do we lose anything shipping 3 vs 4?" / "More work later?"). Chris ratified: **"Ship 3-tool"**.

Deferred but pending Chris D-verdict at close-cascade:
- Codify mutation-scan-swap pattern (Playbook amendment or sweep-doc update)
- Mutation-shape template for next-session batch 4 (proactive + self_awareness + profile)

---

## Post-merge live-dispatch verify (per PLAYBOOK-7.4.4)

Recycle event recorded clean at `sha=fd4c9d5b0ce8`, zero surviving old PIDs.

| Tool | Action | Latency | Envelope shape | Result |
|---|---|---:|---|---|
| `mobile_tool` | `project_status` | 4ms | `{action, path, name, version, expo_version=~54.0.33, react_native_version=0.81.5, navigation=react-navigation, total_dependencies=29, config_file=app.config.ts, eas_profiles=[dev/preview/production]}` | ✓ full envelope |
| `calendar_tool` | `stats` | 10ms | `{action, total_channels=0, total_episodes=0, by_platform={}}` | ✓ empty-state (dev env) |
| `conceptforge_tool` | `stats` | 11ms | `{action, total_runs=0, avg_quality_score=0.0, by_status={}, by_source_type={}}` | ✓ empty-state (dev env) |

All 3 handlers correctly return their documented envelope shapes. Empty-state on calendar + conceptforge is dev-env expected (no seed data); envelope key contracts hold.

Rigby note: tool handlers themselves do not emit `latency_ms` in their responses — the latency values above came from the tool-run harness wrapper metadata (same as prior batches).

---

## Sweep progress (post-S2920)

- **Slice 4 (`td_handlers_gateway`):** **11/17 shipped.** Batch 3 CLOSED.
- **Remaining 6:** cockpit (431) · podcast (251) · profile (188) · proactive (140) · self_awareness (118) · vip_invite (81).
- **Total corpus untested:** 39 → **36** (batch 3 flipped 3 untested → validated_full via auto-classifier).
- **Gap map:** **63 full · 10 partial · 7 unknown · 36 untested** (from S2919's 60 · 10 · 7 · 39).

**Session cumulative pace:** 3 tools / 1 batch / 1 session (with in-depth 2-turn T0 SIGN + probe-first correction + mutation-scan swap attempts + escalation to split-batch + post-merge live verify).

---

## Ledger corroborations + new candidates

### Corroborated existing patterns

- **Legacy-error envelope** now at **15 instances** post-S2920 (13 mobile / 14 calendar / 15 conceptforge). Substrate arc still gated on explicit Chris directive per 00-START forbidden-list. Rigby Q4(a) surfaced semantic-nuance framing shift that may warrant refresh.
- **Template-preservation swap pattern** now at **2nd batch-level instance** (S2919 vip_invite→narrative + S2920 proactive+self_awareness+profile→conceptforge). Rigby + Claude jointly recommend codification.
- **00-START span-math burn** now at **2nd consecutive session** (S2919 caught calendar=86-claimed vs 166-actual; S2920 caught calendar=166-claimed vs 84-actual). Suggests 00-START source is being stale-copied. Recommend regen from repo receipts at close.
- **Envelope-key asymmetry across actions** — still at 3/3 triggered from S2919 batch 2. Not incremented this batch (mobile has 4-action asymmetry consistent with pattern; calendar likewise; conceptforge likewise; no new distinct sub-pattern).

### New Ledger candidates from batch 3

1. **Multi-tenant leak on `calendar_tool.upcoming`** — 3rd gateway instance (batch 1 campaign_tool.detail + experiment_tool.results + this). Absorbed by single-user pre-prod context per `project_single_user_pre_prod_operating_context`; post-D6 evaluation only.
2. **Mixed user-scoping within single response** — 1st instance. `calendar_tool.stats` returns `total_channels` scoped to `user_id` but `total_episodes` un-scoped (system-wide). Distinct from cross-action envelope-key asymmetry. 2nd instance triggers evaluation.
3. **Filesystem-read handler shape (open + regex)** — 2nd Slice-4 instance (after `discord_tool`). Two-tool corroboration; not a Fold yet.
4. **`limit` does not gate stages/artifacts on `run_detail`** — conceptforge_tool.run_detail returns all stages + all artifacts for a run regardless of `limit`. 1st instance of "limit applies only to top-level list" pattern in gateway. 2nd instance triggers evaluation.
5. **500-byte placeholder heuristic** — mobile_tool.screens uses first-500-byte scan for "Placeholder" or "coming soon" strings. Sharp edge: real screens with `Placeholder` in a type name mis-flag as placeholder. Documented not defect-worthy; usability candidate.

---

## Full-context references

- **PR:** [#3470](https://github.com/clwest/donkey-betz-platform/pull/3470) (merged at `fd4c9d5b0`)
- **Per-tool validation docs (batch 3):**
  - `docs/research/tools/validation/mobile_tool_validation.md`
  - `docs/research/tools/validation/calendar_tool_validation.md`
  - `docs/research/tools/validation/conceptforge_tool_validation.md`
- **T1b canonical template:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`
- **Prior session:** `docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` (workspace deliverable) — no new entries this session; narrative_tool dev-env drift from S2919 still pending triage.
- **Recycle event log:** `logs/recycle_events.jsonl` (sha=fd4c9d5b0ce8, clean)

---

## Open threads for S2921

1. **Chris D-verdict on codification of mutation-scan-swap pattern** — 2 triggers now; Rigby + Claude joint-recommend Playbook amendment or sweep-doc update.
2. **Mutation-shape template design** — needed before shipping proactive + self_awareness + profile (deferred batch). vip_invite (known 3 mutations) also blocks on this template.
3. **00-START source-of-truth regen** — 2nd consecutive session with calendar-span burn suggests stale-copy in 00-START; recommend regenerating span table from `repo_tool` receipts at close.
4. **Legacy-error envelope framing refresh** — Rigby Q4(a) semantic-nuance pushback; still gated on explicit Chris directive.
