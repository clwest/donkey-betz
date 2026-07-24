# SESSION 2919 — Slice 4 batch 2 (gateway small-tier read-only quartet)

**Date:** 2026-07-23
**Session pin:** `pa-df807dcffe9940b5`
**Head at open:** `12d3114b9` (S2918 close)
**Head at close:** `be14744153fe` (batch 2) → close cascade adds handoff + 00-START + wrapper bump
**PRs shipped:** [#3468](https://github.com/clwest/donkey-betz-platform/pull/3468) (batch 2) + `<TBD>` (close cascade)

---

## Headline

**Slice 4 (`td_handlers_gateway`) 8/17 shipped.** Batch 2 = 4 pure-read gateway tools (discord + distribution + ats + narrative) via S2796 doc-only shape. Rigby T0 SIGN 2-turn cycle grounded in 15+ `repo_tool` receipts — zero rubber-stamp. Turn 1 DISAGREE walked back 00-START's `~80-line` small-tier framing (materially wrong when boundary math computed from full `_handle_*` census). Q3 verb-scan surfaced 3 mutations in the originally-proposed `vip_invite` (`.create` L973, `.save` L1006/1009), triggering template-preservation swap to `narrative` (107 lines, pure read). Post-merge live verify: 3/4 clean (discord 5ms / distribution 14ms / ats 17ms); narrative surfaced pre-existing dev-env drift — `narrative` table missing from local DB despite migration recorded applied. Not batch-2 defect; logged as Rigby Tool Gap Ledger entry for engineering-backlog triage.

**Sweep progress post-S2919:** Slice 4 = 8/17. Total corpus 43 → 39 untested. Gap map: 56 full → **60 full** · 10 partial · 7 unknown · 39 untested.

---

## What shipped

### Tools (4 — Slice 4 batch 2)

- **`discord_tool`** (`td_handlers_gateway.py:723`, 91 lines, 3 actions: `status` / `commands` / `cogs`) — filesystem read + regex parse of `discord_bot.py`. Only gateway tool with non-ORM first-hop this batch.
- **`distribution_tool`** (`td_handlers_gateway.py:1700`, 93 lines, 4 actions: `platforms` / `listings` / `revenue` / `stats`) — pure ORM SELECT + Sum/Count on `DistributionPlatform` + `ContentDistribution`.
- **`ats_tool`** (`td_handlers_gateway.py:2600`, 93 lines to EOF, 4 actions: `keywords` / `optimizations` / `templates` / `stats`) — pure ORM SELECT + Sum/Avg/Count on `ATSKeywordMapping` + `ResumeOptimizationLog` + `PersonaResumeTemplate`.
- **`narrative_tool`** (`td_handlers_gateway.py:1453`, 107 lines, 5 actions: `narratives` / `shifts` / `evidence` / `alerts` / `help`) — pure ORM SELECT + FK JOIN on `Narrative` / `NarrativeShift` / `NarrativeEvidence` / `NarrativeAlert`. Template-preservation swap from `vip_invite` after Q3 mutation-verb scan.

No TOOL_DEFAULTS or TOOL_ACTION_METADATA entries this batch (all pure READ_ONLY, auto-classifier upgrades docs to `validated_full`).

### Validation docs (4)

- `docs/research/tools/validation/discord_tool_validation.md`
- `docs/research/tools/validation/distribution_tool_validation.md`
- `docs/research/tools/validation/ats_tool_validation.md`
- `docs/research/tools/validation/narrative_tool_validation.md` (§6 amended post-verify with dev-env drift note)

All 4 use T1b canonical template v1 sweep variant.

### Regenerated docs

- `docs/PA_TOOL_AUDIT.md` (161 tools · 117 schemas · 160 handlers · 116 wired both sides)
- `docs/audits/PA_TOOLS_GAP_MAP.md` (60 full · 10 partial · 7 unknown · 39 untested)

### Ledger entry

- **Rigby Tool Gap Ledger** deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0` — appended 1962 chars via `deliverable_tool.append`. Entry: "S2919 — narrative_tool + shifts/evidence/alerts blocked — narrative* tables missing in local dev DB despite migrations recorded as applied". Symptom / root cause / 3 remediation candidates / MEDIUM priority.

---

## Rigby joint SIGN (2-turn cycle + zoom-out, zero rubber-stamp)

### T0 SIGN turn 1 — full `_handle_*` census

**Probes executed (10 `repo_tool` runs):**
- `repo_tool.search` `td_handlers_gateway` → 9 files matched; confirms handlers colocated in single file
- Per-tool `repo_tool.search` `def _handle_<name>` for: vip_invite / conceptforge / calendar / podcast / ats / cockpit / discord / distribution / mobile → 9 line-number anchors captured
- `repo_tool.read_file` `td_handlers_gateway.py:600-1100` → confirms handler bodies exist between anchors

**Turn 1 verdicts:**
- **Q1 DISAGREE**: 00-START's "small-tier" numbers (vip_invite 81 / conceptforge 84 / calendar 86 / podcast 89) came from prior calculation; needed re-verification. Rigby refused to sign a batch composition on unverified spans.
- **(a) Missing anchors**: needed narrative + proactive + self_awareness + profile + repo + analytics before span math was complete.

### T0 SIGN turn 2 — completed census + corrected math

**Additional probes (7 `repo_tool` runs):**
- `def _handle_narrative` → 1453 · `def _handle_proactive` → 1560 · `def _handle_self_awareness` → 2482 · `def _handle_profile` → 2294 · `def _handle_repo` → 101 · `def _handle_analytics` → 643
- `repo_tool.read_file` `td_handlers_gateway.py` in 500-line pages → total_lines=2693 confirmed

**Corrected boundary-math span table (13 remaining Slice 4 tools):**

| Tool | Start line | Span (next − this) |
|---|---|---|
| vip_invite | 941 | 81 |
| discord | 723 | 91 |
| distribution | 1700 | 93 |
| ats | 2600 | 93 (to EOF 2693) |
| conceptforge | 2210 | 84 |
| narrative | 1453 | 107 |
| self_awareness | 2482 | 118 |
| mobile | 814 | 127 |
| proactive | 1560 | 140 |
| calendar | 1793 | 166 |
| profile | 2294 | 188 |
| podcast | 1959 | 251 |
| cockpit | 1022 | 431 |

00-START was RIGHT on: cockpit=431 · vip_invite=81 · discord=91 · distribution=93 · conceptforge=84.
00-START was WRONG on: calendar (claimed 86, actual 166) · podcast (claimed 89, actual 251).
00-START OMITTED from small/medium classification: mobile · narrative · proactive · self_awareness · profile.

**Q1 verdict** (revised after correction) **AGREE-with-edits**: preserve batch-1 pure-read template → discord + distribution + ats + narrative. Note: vip_invite has mutations (see Q3), swap to narrative (107 lines but pure read).

**Q2 verdict AGREE**: 0/4 first-hop literals (`apply_async` / `httpx|requests|urllib.request` / `openai|anthropic|litellm`) in each of the 4 selected spans. Appendix A + Appendix N N/A per gateway-wide S2918 DISAGREE.

**Q3 verdict AGREE-with-edits**: 3 verb-scan finds in `vip_invite` (`.create` L973, `.save` L1006/1009) → template-preservation swap to narrative. Batch-2 final quartet (discord + distribution + ats + narrative) all 0/4 mutation verbs. Narrative tail 1553-1560 verified clean (error return + exception handler only, no hidden `.save/.create/.update/.delete`).

**Q4 zoom-out (required per `feedback_zoom_out_ask_per_rigby_sign`):**
- **(a) Legacy-error envelope corroboration**: batch 2 = different-tool-block instance. If any batch-2 tool surfaces `error_code='legacy_error'` at runtime, 9th instance ready for post-D6 substrate arc evaluation. Confirmed at live-verify: narrative_tool live dispatch returned `error_code='legacy_error'` — but semantic nuance: this is the *value* of the `error_code` field (post-S2909 substrate), not the ABSENCE of the field. Legacy-error tracking may need reframing.
- **(b) Template guidance to codify**: probe-first Q1 (span math + verb scan BEFORE naming batch composition) — proven necessary by this session's correction. Per-tool A/N confirmation after global probe. Post-merge live-verify with latency budget (≤20ms baseline). **Prune** rigid 2-turn ritual — Turn 2 can merge with Turn 1 when evidence complete.
- **(c) Accretion risks halfway through Slice 4**: overfitting on "no mutation verbs == safe" (hidden fan-out unaddressed by verb scan alone); uniform-batch bias (Slice 4 has 431-line cockpit + 251-line podcast outliers); shallow first-hop literal probes (should also grep helpers like `sync_*` / `fetch_*` / `ingest_*` before declaring N/A).
- **(d) Cockpit (431 lines) plan**: reserve dedicated cockpit-only batch (S2914 precedent shape); execute later. Batch 3 drains remaining medium-tier read-only tools (mobile 127 / self_awareness 118 / proactive 140 / calendar 166 or similar).

### Post-merge live verify (per PLAYBOOK-7.4.4)

4 live dispatches, 3 clean + 1 surfaced pre-existing dev-env issue:

| Tool | Action | Latency | Result |
|---|---|---|---|
| `discord_tool` | `status` | 5ms | shape ✓ — 59/100 slots · 25 cogs · 48 top-level · 11 groups · 96 subcommands · guild_id null |
| `distribution_tool` | `stats` | 14ms | shape ✓ — all zeros (no ContentDistribution rows) |
| `ats_tool` | `stats` | 17ms | shape ✓ — all zeros (no ATS rows) |
| `narrative_tool` | `narratives limit=5 domain=politics` | 8ms | **FAILED** — `error_code='legacy_error'` / `relation "narrative" does not exist` |

**Root cause investigation (Claude ORM-verified per `feedback_verify_at_raw_orm_before_trusting_tool_no_data`):**
- Model at `core/models_narrative_drift.py:103` declares `db_table='narrative'` (not default `core_narrative`)
- `django_migrations` records `core::0103_session_471_narrative_drift_detector` as applied
- Migration 0103 contains `CreateModel('Narrative')` at line 17+
- `pg_tables` public schema returns 0 matches on `%narrative%`
- **Verdict**: migration state ≠ table state. Local DB was recreated or migrations reverted at some point. NOT a defect in batch-2 shipped shape (validation doc correctly documents envelope; underlying table missing).
- **Blast radius**: 1 (single-user pre-prod per `project_single_user_pre_prod_operating_context`); narrative_tool was in Rigby's surface but Chris hasn't been actively using it.
- **Remediation candidates in ledger**: (a) `migrate --fake` prior + re-apply cleanly · (b) direct SQL restore from snapshot · (c) investigate whether prod / Railway has same drift.
- **Not blocking S2919 close**; logged for future engineering session.

**Recycle receipt** (per PLAYBOOK-7.4.4): `make recycle-all` at `sha=be14744153fe`, zero surviving PIDs, event recorded in `logs/recycle_events.jsonl`.

---

## Ledger candidates surfaced (batch 2)

Threshold-triggered candidates for post-D6 evaluation (moratorium still in force):

- **Schema-drift "param declared but ignored on subset of actions" — 3/3 trigger** → triggers evaluation. Instances: analytics_tool `role` (S2911) + audit_tool `status` on `citations` (S2918) + ats_tool `category` on non-`keywords` (S2919). narrative_tool `category`/`domain` dual-accept is 4th confirming.
- **Envelope-key asymmetry across actions — 3/3 trigger** → triggers evaluation for candidate harness-lint "consistent-list-key across actions." Instances: batch-1 audit `findings/defects/violations` + batch-1 experiment `tests/test/total_tests` + batch-2 distribution `platforms/listings/revenue/stats` (`revenue` missing `count`).
- **Legacy-error envelope — 12 corroborating instances** (was 8 at S2918 close). Semantic nuance surfaced at live-verify: the observed `error_code='legacy_error'` is a *value* on a post-S2909 envelope field, not the *absence* of the field. Framing may need refresh. Still gated on explicit Chris directive per 00-START forbidden-list.

New sub-shape ledger candidates (below threshold, watching):

- **Divergent `limit` hard-cap (30 vs 50)** — narrative_tool 1st gateway-slice instance.
- **N+1 query pattern in narrative `narratives` action** (`evidence_count` per-row).
- **Envelope-shape intra-tool asymmetry (`total` vs `count`)** — narrative `narratives` uses `total`; sibling actions use `count`. Distinct from cross-action envelope-key asymmetry.
- **`variations` truncation-to-3 undeclared in ats_tool schema** — usability sharp edge.
- **`platform_account` stringified-UUID-not-name in distribution_tool `revenue` grouping** — usability sharp edge.

---

## Handoff to S2920

**Slice 4 (`td_handlers_gateway`) — 8/17 shipped. 9 remaining:**
- calendar (166) · cockpit (431) · conceptforge (84) · mobile (127) · podcast (251) · proactive (140) · profile (188) · self_awareness (118) · vip_invite (81)

**Recommended batch 3 composition (small/medium read-only pilot):**
- Options: (a) mobile + self_awareness + proactive + calendar (medium-tier read-only quartet, 127/118/140/166 lines); (b) conceptforge + self_awareness + proactive + calendar (mix small+medium); (c) reserve vip_invite for dedicated mutation-batch alongside future cockpit-batch shape.
- Cockpit (431 lines) planned as dedicated later batch per S2914 precedent.

**Full session context:** see this handoff (`docs/handoffs/SESSION_2919_SLICE_4_BATCH_2.md`).

---

## PRs

- [#3468](https://github.com/clwest/donkey-betz-platform/pull/3468) — Slice 4 batch 2 (discord + distribution + ats + narrative). Merged at `be14744153fe`.
- `<TBD>` — S2919 close cascade (this handoff + 00-START refresh + wrapper pin bump + narrative doc §6 amendment).
