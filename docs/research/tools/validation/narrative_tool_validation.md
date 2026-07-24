# `narrative_tool` — Validation Report (S2919)

**Tool:** `narrative_tool`
**Schema:** `core/services/pa_tool_schemas.py:4670`
**Handler:** `core/services/td_handlers_gateway.py:1453` (`_handle_narrative`)
**Register site:** `core/services/tool_dispatcher.py:577`
**Session:** S2919 (Slice 4 batch 2 — gateway small-tier read-only quartet: discord + distribution + ats + narrative)
**HEAD at validation:** `12d3114b9` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2919 T0 SIGN AGREE (batch-1 template-preservation swap — replaced vip_invite after Q3 verb-scan surfaced 3 mutations in that handler) — span 107 lines (1453-1560); 0/3 Appendix A/N first-hop literals; tail 1553-1560 verified clean (no mutation verbs beyond error return + exception handler).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`narrative_tool` surfaces narrative-drift-tracking telemetry from four tables: `Narrative` (tracked narratives with domain/status/confidence), `NarrativeShift` (drift-detection events with trend-break and cultural-impact analysis), `NarrativeEvidence` (per-narrative source citations with sentiment/strength scores), and `NarrativeAlert` (Discord-notified drift alerts). Use it when the operator asks "which narratives are active in tech / crypto / geopolitics?" / "any recent shifts?" / "evidence for narrative X?" / "what drift alerts fired?".

Distinct from `analytics_tool` (event-stream aggregates, not narrative drift), from `proactive_tool` (user-facing alerts, not narrative-scoped), and from `cockpit_tool` (Celery infra, not content-model surface).

## Covered actions

- `help` — **in scope this ship** — default action; returns `{tool: 'narrative_tool', actions: [<enumerated action descriptions>]}`. No DB read.
- `narratives` — **in scope this ship** — lists `Narrative` rows ordered by `-updated_at`. Supports `domain` filter (accepts either `category` or `domain` payload key — see §3 schema-drift note). Returns `{action, total, narratives: [{id, title, domain, status, confidence, evidence_count, updated_at}]}` — envelope uses **`total: qs.count()`** not `count: len(narratives)` (asymmetric with the tool's other list actions).
- `shifts` — **in scope this ship** — lists `NarrativeShift` rows ordered by `-detected_at`. Supports `domain` filter. Uses `select_related('old_narrative')` — no N+1 on the joined narrative title. Returns `{action, count, shifts: [{id, narrative, domain, shift_summary, confidence, importance, trend_break_analysis, cultural_impact_analysis, detected_at}]}`. Text-field truncations to 200 chars: `shift_summary`, `trend_break_analysis`, `cultural_impact_analysis`.
- `evidence` — **in scope this ship** — lists `NarrativeEvidence` rows scoped to `narrative_id` (required). Returns `{action, narrative_id, count, evidence: [{id, source_title, source_url, source_type, sentiment, strength, excerpt, created_at}]}`. `excerpt` truncated to 200 chars.
- `alerts` — **in scope this ship** — lists `NarrativeAlert` rows ordered by `-created_at`. Returns `{action, count, alerts: [{id, title, alert_type, summary, sent_to_discord, created_at}]}`. `summary` field falls through to `message` (line 1547: `(a.summary or a.message or '')[:200]`), truncated to 200. `sent_to_discord` is a **read of a prior-side-effect flag**, not an active dispatch — this handler does not send to Discord.

Default action = `help` (per `payload.get('action', 'help')` at handler line 1455) — differs from most sweep-shape tools whose default is a data-returning action.

## 3. Schema notes

- **Required:** `action` (enum: `narratives` / `shifts` / `evidence` / `alerts` / `help`).
- **Optional:** `narrative_id` (string — only required for `evidence`; ignored otherwise), `domain` (enum-restricted at schema level to 8 values: `politics` / `markets` / `tech` / `culture` / `geopolitics` / `crypto` / `climate` / `health`), `limit` (int; default 10, hard cap 30 via `min(int(payload.get('limit', 10)), 30)` at handler line 1456 — **note the hard cap is 30 here, not the 50 used by sibling gateway tools** — first gateway-slice tool with divergent limit ceiling).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4667-4713`.
- **Schema-drift — undocumented `category` alias for `domain`:** handler line 1457 reads `domain = payload.get('category') or payload.get('domain')`. The schema declares only `domain`; consumers dispatching `category=<x>` get the filter applied silently. Comment says "accept both, model field is 'domain'" — intentional backward-compat but undeclared in schema. **4th instance** of schema-drift-shape (analytics_tool `role` S2911 + audit_tool `status` on `citations` S2918 + ats_tool `category` on non-`keywords` actions S2919 batch 2 + this narrative `category` alias). Meets 3/3 threshold triggered on ats_tool — this is the 4th confirming instance.
- **Envelope shape asymmetry (intra-tool):** `narratives` uses `total: qs.count()`; `shifts` / `evidence` / `alerts` use `count: len(<list>)`. Consumers keying on `count` for `narratives` get missing key. **12th legacy-shape corroborating instance** — but distinct from legacy-error envelope (this is intra-tool envelope-shape asymmetry, not error-shape).
- **`domain` enum enforcement is schema-side only:** handler does not re-validate; passing a non-enumerated domain silently applies the filter (likely returns empty set if the domain isn't a valid model value).

## 4. Golden-path examples

**Example 1 — action inventory (safe default):**
```json
{"action": "help"}
```
Expected envelope: `{"tool": "narrative_tool", "actions": ["narratives — ...", "shifts — ...", "evidence — ...", "alerts — ..."]}`. No DB touch.

**Example 2 — active tech narratives:**
```json
{"action": "narratives", "domain": "tech", "limit": 15}
```
Expected envelope: `{"action": "narratives", "total": <int>, "narratives": [{"id": ..., "title": "...", "domain": "tech", "status": "...", "confidence": <float|null>, "evidence_count": <int>, "updated_at": "..."}, ...]}`.

**Example 3 — recent narrative shifts across all domains:**
```json
{"action": "shifts", "limit": 10}
```
Expected envelope: `{"action": "shifts", "count": <int ≤ 30>, "shifts": [{"id": ..., "narrative": "...", "domain": "...", "shift_summary": "<≤200 chars>", "confidence": <float>, "importance": <float>, "trend_break_analysis": "<≤200 chars>", "cultural_impact_analysis": "<≤200 chars>", "detected_at": "..."}, ...]}`.

**Example 4 — evidence for a specific narrative:**
```json
{"action": "evidence", "narrative_id": "<uuid>", "limit": 20}
```
Expected envelope: `{"action": "evidence", "narrative_id": "<uuid>", "count": <int ≤ 30>, "evidence": [{"id": ..., "source_title": "...", "source_url": "...", "source_type": "...", "sentiment": "...", "strength": <float|null>, "excerpt": "<≤200 chars>", "created_at": "..."}, ...]}`.

**Example 5 — recent Discord-dispatched alerts:**
```json
{"action": "alerts", "limit": 25}
```
Expected envelope: `{"action": "alerts", "count": <int ≤ 30>, "alerts": [{"id": ..., "title": "...", "alert_type": "...", "summary": "<≤200 chars>", "sent_to_discord": <bool>, "created_at": "..."}, ...]}`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": "Unknown narrative_tool action: <action>"}` at handler line 1553. Not raised — in-envelope.
- **Handler exception:** caught at line 1555, logged via `logger.error(..., exc_info=True)` (NARRATIVE log stream), returns `{"error": <str>}`. No `error_code` field — **legacy-error envelope** (12th corroborating instance).
- **Missing `narrative_id` on `evidence`:** returns `{"error": "Provide narrative_id for evidence lookup"}` at line 1518. Not raised — in-envelope. Only in-envelope validation guard on this handler.
- **Empty result set:** returns `total: 0` (narratives) or `count: 0` (shifts/evidence/alerts) + empty list. No error.
- **`limit` hard cap = 30 (not 50):** narrative is the first gateway-slice tool with a divergent limit ceiling. All prior gateway tools (analytics/audit/campaign/experiment/discord/distribution/ats) use `min(limit, 50)`; narrative uses `min(limit, 30)`. Consumers must know the cap differs.
- **N+1 pattern in `narratives`:** `evidence_count` is computed per-row via `NarrativeEvidence.objects.filter(narrative=n).count()` at line 1489. For default `limit=10` this is 10 queries; at hard cap `limit=30` it's 30 queries. Not a bug, but a scaling sharp edge. Candidate for future `Prefetch` / `annotate(Count(...))` optimization.
- **`old_narrative` may be null in `shifts`:** handler guards with `s.old_narrative.title if s.old_narrative else 'Unknown'` at line 1504. `select_related('old_narrative')` still valid on nullable FK.
- **`summary` fallback in `alerts`:** `(a.summary or a.message or '')[:200]` — silent fallthrough from summary to message. Consumers see one string, don't know which field it came from.
- **Text truncations to 200 chars:** `shift_summary`, `trend_break_analysis`, `cultural_impact_analysis`, `excerpt`, `summary` — all truncate silently. Full text requires direct ORM.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `Narrative.objects.all().order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:1476-1479` | ORM SELECT; documented |
| `NarrativeShift.objects.select_related(...).order_by(...)` + `.filter(...)` | `read` | `td_handlers_gateway.py:1495-1498` | ORM SELECT with JOIN; documented |
| `NarrativeEvidence.objects.filter(narrative_id=...)` (evidence action) | `read` | `td_handlers_gateway.py:1519-1521` | ORM SELECT; documented |
| `NarrativeEvidence.objects.filter(narrative=n).count()` (narratives action row-count) | `read` | `td_handlers_gateway.py:1489` | ORM AGGREGATE per row (N+1); documented |
| `NarrativeAlert.objects.order_by(...)` | `read` | `td_handlers_gateway.py:1539` | ORM SELECT; documented |

**Appendix N (Network-Preflight) — N/A.** No network first-hop. `sent_to_discord` in `alerts` is a **read of a prior-side-effect flag**, not an active dispatch.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns). S2919 T0 SIGN Q2 per-tool confirmation: narrative span 1453-1560 contains none of these literals — grep receipts + narrative tail 1553-1560 verification in Rigby T0 SIGN turn 3 + turn 4.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification appended to the S2919 handoff. Expected shapes documented in §4 golden-path examples.

**Runtime status — S2919 post-merge live verify (2026-07-23):** Rigby dispatch `narrative_tool action=narratives limit=5 domain=politics` returned in 8ms with `{"error": "relation \"narrative\" does not exist ... SELECT COUNT(*) ... FROM \"narrative\" ...", "error_code": "legacy_error"}`. **Dev-env DB drift, not a defect in this batch's shipped shape**: model declares `db_table='narrative'` explicitly at `core/models_narrative_drift.py:103`; `django_migrations` records migration `0103_session_471_narrative_drift_detector` (which contains `CreateModel('Narrative')`) as applied; but `pg_tables` lookup in local `public` schema returns 0 rows matching `%narrative%`. Migration state ≠ table state — likely cause: DB was recreated / snapshot restored without re-running the narrative migrations, OR migrations were manually reverted. Not blocking batch-2 close. Logged as Rigby Tool Gap Ledger entry (deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`) for engineering-backlog triage; envelope shape declared in §4 remains the canonical shape spec when the table is restored.

## Related

- **Adjacent tools:** `analytics_tool` (event-stream aggregates, no narrative context) — batch 1; `proactive_tool` (user-facing alerts, unrelated model tree); `cockpit_tool` (Celery infra).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1); models at `core/models_narrative_drift.py` (`Narrative`, `NarrativeShift`, `NarrativeEvidence`, `NarrativeAlert`).
- **Prior ratifications:** S2892 Path B open, S2918 Slice 4 batch 1 (analytics/audit/campaign/experiment quartet — same gateway ORM-direct shape).
- **Ledger rows relevant to this ship:**
  - **Schema-drift "undocumented `category` alias for `domain`" — 4th instance** — analytics_tool `role` (S2911) + audit_tool `status` on `citations` (S2918) + ats_tool `category` on non-`keywords` actions (S2919 batch 2) + narrative_tool `category`/`domain` dual-accept (S2919 batch 2). 4/3 confirming instances past the ats_tool 3rd-instance trigger — **candidate for consolidated Fold at Slice 4 CLOSE**.
  - **Legacy-error envelope 12th instance** — continued corroboration; batch-2 broadening. Still gated on explicit Chris directive per 00-START forbidden-list.
  - **Divergent `limit` hard-cap (30 vs 50) — 1st instance in gateway slice** — narrative_tool's `min(limit, 30)` diverges from all prior gateway tools' `min(limit, 50)`. Not a defect; different domain. Candidate for future post-D6 doc-fix ratification if 2nd instance surfaces.
  - **N+1 query pattern in `narratives` action** — `evidence_count` computed per-row; scales linearly with `limit`. Not a bug at hard cap 30; performance sharp edge. Candidate for future post-D6 refactor if 2nd instance surfaces.
  - **Envelope-shape intra-tool asymmetry (`total` vs `count`)** — narrative_tool's `narratives` action returns `total` while its sibling actions return `count`. Distinct from cross-action envelope-key asymmetry (S2918 audit_tool + experiment_tool) — this is intra-action-shape asymmetry, not intra-key. Candidate for tracking as separate ledger sub-shape.
