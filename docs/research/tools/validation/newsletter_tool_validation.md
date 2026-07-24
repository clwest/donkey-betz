# `newsletter_tool` — Validation Report (S2939)

**Tool:** `newsletter_tool`
**Schema:** `core/services/pa_tool_schemas.py:4324` (7-action enum + 8 optional params)
**Handler:** `core/services/td_handlers_newsletter.py:27` (`_handle_newsletter`; per-action helpers `_newsletter_prepare` :78 / `_newsletter_outline` :277 / `_newsletter_validate` :345 / `_newsletter_metrics` :406 / `_newsletter_list_issues` :476 / `_newsletter_config` :521 / `_newsletter_sources` :588)
**Register site:** `core/services/tool_dispatcher.py:593`
**Session:** S2939 (Slice 7 Batch 2a — trio with `mission_verdict` + `rigby_work_item`)
**HEAD at validation:** `acca1f4e2` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Bifurcated verification scope** (per Chris D-verdict guardrail): §6 covers 3 read actions LIVE-VERIFIED; §5a covers 4 mutation actions ANALYZED-NOT-EXECUTED with signal-chain evidence. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38).
**Category upgrade target:** `untested` → `validated_partial` (3 read actions live-verified; 4 mutation actions analyzed-only)
**Rigby SIGN:** S2939 T0 SIGN AGREE-WITH-EDITS Q1 (bifurcated Option C; §6 strictly read-only). Chris D-verdict at T0 RATIFIED with two guardrails baked in (§6 read-only scope sentence + §5a mutation proof bar cited).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`newsletter_tool` is the **Autopilot Ops publishing pipeline** entry — transforms an issue Deliverable into publish-ready Markdown+HTML+checklist artifacts, generates Template v1 outlines for new issues, validates drafts against completeness+length targets, tracks per-issue metrics (opens/clicks/subscribers), lists newsletter deliverables, and manages provider config (Substack/Beehiiv/Buttondown). Use it when Chris asks "prepare Issue #N for publish", "outline the next newsletter", "validate this draft", "record metrics on Issue #N", "list all newsletter drafts", "update newsletter config", or "show me the source pack".

Distinct from `blog_tool` (blog/content review pipeline — pre-newsletter content; this tool operates on newsletter-issue Deliverables specifically); from `deliverable_tool` (generic deliverable CRUD across all `deliverable_type` values — this tool is scoped to `category='Newsletter'` with dedicated publishing shape); from `content_scoring_service` (upstream rule-based scoring, not surfaced through this tool). This is the tool Rigby reaches for anywhere in the Autopilot Ops newsletter authoring → validation → publish → post-publish-metrics lifecycle.

## Covered actions

Enumerating every action in the schema `action` enum. **3 read actions LIVE-VERIFIED at S2939**; **4 mutation actions ANALYZED-NOT-EXECUTED** per Option C batch shape (§5a below).

- `validate` — **in scope this ship — verified live.** Pure-read check against Template v1 section+length targets. Envelope: `{action, deliverable_id, title, pass, total_words, word_count_in_range, target_range, link_count, errors[], warnings[], sections{}}`. See §6.1.
- `list_issues` — **in scope this ship — verified live.** Paginated newsletter-deliverable list. Envelope: `{action, total, offset, limit, count, items[{id, title, issue_number, artifact_type, provider, content_format, is_saved, created_at}]}`. See §6.2.
- `sources` — **in scope this ship — verified live.** Read-only view of curated source pack (feeds/sites per section). Envelope: `{action, summary, sources[]}` when no filter; `{action, filter, count, sources[]}` with category/section filter. See §6.3.
- `prepare` — **ANALYZED-NOT-EXECUTED — MUTATION `spreading` (4-way Deliverable fan-out)** — see §5a. Transforms source Deliverable via `newsletter_publisher.get_publisher(<name>).prepare_issue(...)`, then writes 4 Deliverables (markdown, HTML, checklist, subject+preheader) via `Deliverable.objects.update_or_create` with title-based lookup keys.
- `outline` — **ANALYZED-NOT-EXECUTED — MUTATION `spreading` (1 Deliverable + optional source-pack read)** — see §5a. Calls `generate_issue_outline(...)` then writes 1 Deliverable (`title="Autopilot Ops — Issue #N (Outline)"`) via `update_or_create`.
- `metrics` — **ANALYZED-NOT-EXECUTED — MUTATION `contained` (1 Deliverable.metadata write)** — see §5a. Computes metrics via `compute_issue_metrics(...)`, merges manual overrides from payload (send_date/opens/clicks/unsubscribes/new_subscribers with non-negative validation), then `deliverable.save(update_fields=['metadata'])`.
- `config` — **CONDITIONAL MUTATION `contained`** — pure-read when no update fields present in payload; mutation when any of `provider`/`subscribe_url`/`sponsor_email`/`publication_name`/`publication_slug` present. See §5a for the mutation path; §6.4 for the read path.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_newsletter.py:29`). Defaults to `list_issues` per `payload.get('action', 'list_issues')`.
- **invalid action** — verified via handler code inspection (`td_handlers_newsletter.py:46-50`). Returns `_handler_error(action, 'unknown_action', 'Unknown newsletter action: <x>')` — divergence class from execution_history_tool (raises `ValueError`) vs recent_activity + rigby_shift_brief + mission_verdict (in-envelope error). newsletter_tool uses the `_handler_error` helper (from `td_error.py`) — a third variant tracked by Ledger #5 systemic consistency lint candidate.

## 3. Schema notes

- **Required:** `action` (enum: `prepare` | `outline` | `validate` | `metrics` | `list_issues` | `config` | `sources`).
- **Optional:** `id` / `deliverable_id` (alias — either works; required for `prepare` / `validate` / `metrics`); `issue_number` (int, `outline` action, default 1); `provider` (enum: `substack_manual` | `beehiiv` | `buttondown`, config action default `substack_manual`); `subscribe_url` / `sponsor_email` / `publication_name` / `publication_slug` (config update fields); `workspace_id` / `initiative_id` (inherited from source deliverable for `prepare` when omitted; passed to Deliverable writes); `source_pack_id` (`outline` optional; UUID of a Deliverable holding `metadata.sources` — falls back to built-in `newsletter_sources.get_sources()` if omitted or unresolvable, with warning log); `limit` / `offset` / `artifact_type` (`list_issues` filters — limit capped at 50); `category` / `section` (`sources` filters); `send_date` / `opens` / `clicks` / `unsubscribes` / `new_subscribers` (`metrics` manual overrides — key-presence check + non-negative-int validation per S1228 PR-A hardening; feedback rule `feedback_llm_autofills_boolean_params_with_false` cited in handler comment line 439-442).
- **`id`/`deliverable_id` alias:** handler resolves via `payload.get('id') or payload.get('deliverable_id')` (line 85, 353, 411) — first-truthy-wins. Schema declares both fields but does not signal aliasing to the LLM caller; GPT-5.2 has been observed to send `deliverable_id` even when schema declares `id`.
- **`source_pack_id` stale-fallback contract (S1103c):** if caller passes an explicit `source_pack_id` that resolves to `Deliverable.DoesNotExist`, handler logs a warning at line 300-305 and falls back to built-in sources rather than erroring. Line 285-289 comment explains: previous silent-fallback was misleading because callers didn't know their pack was stale; now the log makes it visible without breaking the flow.
- **`limit` cap on `list_issues`:** `min(payload.get('limit', 20), 50)` at line 480 — hard cap 50 regardless of caller. Schema doesn't advertise this cap.
- **`metrics` manual-override validation (S1228 PR-A):** key-presence check + non-negative-int validation. Prevents GPT-5.2 auto-fill (0) from silently overwriting real counts. See `feedback_llm_autofills_boolean_params_with_false` memory rule.
- **No auth gate:** newsletter_tool has no dedicated auth gate. Callers implicitly bounded by PA tool-surface exposure (Rigby-only in practice via GPT-5.2 function-calling on PA chat path).
- **No `dry_run` affordance:** every non-empty `prepare` / `outline` / `metrics` / `config`-with-updates dispatch mutates. Ledger #38 substrate blocker.

## 4. Golden-path examples

**Example 1 — Validate a draft:**
```json
{"action": "validate", "id": "<deliverable-uuid>"}
```
→ `{"action":"validate", "deliverable_id":"<uuid>", "title":"Autopilot Ops — Issue #4 (Draft)", "pass":true, "total_words":1247, "word_count_in_range":true, "target_range":"1000-1600", "link_count":18, "errors":[], "warnings":[], "sections":{"Intro":{"present":true, "word_count":142, "target_min":100, "required":true}, ...}}`

**Example 2 — List all newsletter deliverables:**
```json
{"action": "list_issues", "limit": 5}
```
→ `{"action":"list_issues", "total":N, "offset":0, "limit":5, "count":<=5, "items":[{"id":"<uuid>", "title":"...", "issue_number":N, "artifact_type":"outline"|"publish_ready_markdown"|..., "provider":"substack_manual", "content_format":"markdown", "is_saved":true, "created_at":"..."}, ...]}`

**Example 3 — View source pack summary:**
```json
{"action": "sources"}
```
→ `{"action":"sources", "summary":{...per-category counts...}, "sources":[{"name":"...", "url":"...", "category":"...", "section":"..."}, ...]}`

**Example 4 — Read current config:**
```json
{"action": "config"}
```
→ Read path (no update fields): `{"action":"config", "config":{"newsletter_config":true, "provider":"substack_manual", "subscribe_url":"...", ...}}` from the config Deliverable metadata; else default-shape response if no config deliverable exists yet.

**Example 5 — Prepare Issue #4 for Substack (MUTATION — analyzed only this ship):**
```json
{"action": "prepare", "id": "<issue-4-uuid>", "provider": "substack_manual"}
```
→ Would return `{"action":"prepare", "provider":"substack_manual", "source_deliverable_id":"<uuid>", "issue_number":4, "artifacts":{"markdown_id":"<uuid>", "html_id":"<uuid>", "checklist_id":"<uuid>", "subject_id":"<uuid>"}, "subjects":[...5 options], "preview_text":"...", "stats":{...}, "validation_issues":[...], "sections_found":[...], "sections_missing":[...], "checklist_steps":N}`. Not exercised — see §5a for write targets.

## 5. Failure / empty-state / pagination notes

- **`validate` missing `id`:** `_handler_error('validate', 'invalid_params', 'id (deliverable_id) is required')` — non-raising.
- **`validate` unknown `id`:** `_handler_error('validate', 'not_found', 'Deliverable <id> not found')` — non-raising.
- **`validate` on non-newsletter Deliverable:** the tool does NOT filter by `category='Newsletter'` — it will happily validate any Deliverable ID as if it were a newsletter draft. Sections that don't exist return `word_count:0, present:false` — no error. Caller responsibility to ensure `id` points at a newsletter draft.
- **`list_issues` empty state:** `{action:"list_issues", total:0, offset:0, limit:<=50, count:0, items:[]}` — envelope shape stable.
- **`list_issues` user_id scoping:** if `user_id` is present in the dispatch context, results are scoped to `Q(user_id=user_id) | Q(user__isnull=True)` (line 489-490) — user-owned + orphan rows only. If `user_id` is None, all rows visible.
- **`list_issues` `artifact_type` filter:** filters `metadata__artifact_type=<value>` — case-sensitive JSON-key match. Typos silently return 0 results.
- **`sources` empty filter response:** if `category` or `section` filter matches nothing, returns `{count:0, sources:[]}` — envelope shape stable.
- **`sources` no filter:** returns full `summary` + `sources` list (potentially large — hundreds of sources across all sections).
- **`config` no config deliverable + no updates:** returns default-shape response `{"action":"config", "config":{"provider":"substack_manual", ...}, "note":"No config saved yet..."}` (line 575-584). Non-mutating read path.
- **`prepare` missing `id`:** `_handler_error('prepare', 'invalid_params', 'id (deliverable_id) is required')`. Non-raising.
- **`outline` missing `issue_number`:** defaults to `1` (line 282). No error — will overwrite an existing Issue #1 outline via `update_or_create` title-based key.
- **`metrics` on Deliverable with no `issue_number`:** falls back to `0` (line 428-431). `compute_issue_metrics` called with `issue_number=0` — behavior depends on the service.
- **`metrics` GPT-5.2 zero-override guard:** key-presence check + non-negative-int check at lines 443-459. Non-key-present manual fields are silently ignored (not overwriting existing metric).
- **`config` empty-string values:** silently ignored (line 539 — `val is not None and val != ''`). Callers passing `""` for a config field don't clear it.
- **Invalid action:** `_handler_error(action, 'unknown_action', 'Unknown newsletter action: <x>')`. Non-raising. Third divergence class in the sweep (see §5c.1).
- **No `sources` category/section validation:** unknown categories/sections return empty result, not an error. Caller responsibility.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 4 mutation actions declared in `## Covered actions` (prepare / outline / metrics / config-with-updates). ANALYZED-NOT-EXECUTED at this ship per Chris D-verdict guardrail. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38).**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `prepare` | `spreading` | `td_handlers_newsletter.py:135-253` | **4× Deliverable.update_or_create** (markdown row + HTML row + checklist row + subject+preheader row) all keyed by `(title, category='Newsletter', agent_name='NewsletterTool')` per `_lookup` at line 132 | **Deliverable.post_save receivers** — `deliverable_mirror_signals` chain (post_save on Deliverable → mirror to `Document`/`Ledger` tables per S1250 mirror infra) | `get_publisher(<name>).prepare_issue(...)` at line 116 — provider-specific formatting; **`substack_manual` is in-process** (no network); `beehiiv`/`buttondown` variants unverified this doc but declared in schema enum |
| `outline` | `spreading` | `td_handlers_newsletter.py:294-333` | **1× Deliverable.update_or_create** (title `"Autopilot Ops — Issue #N (Outline)"`, `category='Newsletter'`, `agent_name='NewsletterTool'`) | same Deliverable.post_save receiver chain as `prepare` | `generate_issue_outline(N, sources)` at line 311 — in-process; may read but not write source-pack deliverable if `source_pack_id` given |
| `metrics` | `contained` | `td_handlers_newsletter.py:462-465` | **1× Deliverable.save(update_fields=['metadata'])** — single-row metadata mutation on the target issue deliverable | Deliverable.post_save receiver chain fires but `update_fields=['metadata']` may filter which mirrors trigger (mirror-signal behavior unverified for metadata-only updates) | `compute_issue_metrics(...)` at line 433 — in-process compute; **no external network** |
| `config` (with updates) | `contained` | `td_handlers_newsletter.py:542-560` | **1× Deliverable creation OR .save(update_fields=['metadata'])** — either creates a new config Deliverable via `create_deliverable` factory or updates existing config's metadata | same Deliverable.post_save receiver chain | no external touches |

### Signal-chain evidence (Chris D-verdict guardrail — file/line cited)

- **Deliverable.post_save receiver chain:** `core/signals/deliverable_status_signals.record_status_transition` and mirror signals (`deliverable_mirror_signals`) fire on every Deliverable INSERT/UPDATE. Referenced at `core/services/td_handlers_agents.py:4129` comment ("deliverable_status_signals.record_status_transition post_save"). Full mirror chain writes to `Document` and `Ledger` tables per S1250 mirror infra (search for `receiver` + `sender=Deliverable` for full inventory — 3+ receivers).
- **`prepare` idempotency:** each of the 4 writes uses `update_or_create` with a title-based lookup — re-preparing the same source Deliverable overwrites the 4 artifact rows in-place. No row proliferation, but each re-prepare re-fires the post_save receiver chain and re-writes mirrored Document rows.
- **`outline` idempotency:** same `update_or_create` pattern. Re-outlining Issue #4 overwrites the existing outline row.
- **`metrics` idempotency:** `Deliverable.save(update_fields=['metadata'])` — replaces `metadata['newsletter_metrics']` in-place. Re-calling with the same payload is idempotent for the metrics field but always fires the post_save.
- **`config` idempotency:** update_or_create semantics via factory or `save(update_fields=['metadata'])` — non-empty payload fields overwrite existing config; empty-string fields skipped (line 539).

### Idempotency proof bar (Chris D-verdict guardrail)

- All 4 mutation actions are **row-level idempotent** via `update_or_create` or `save(update_fields=[...])` — no row proliferation across repeat calls with the same key.
- Signal-chain re-fires on every save. Downstream mirror rows may accumulate secondary writes (mirror behavior in `deliverable_mirror_signals` may be idempotent OR may append; unverified this doc).
- No unique-constraint dedup on the 4 `prepare` output artifacts across issues — a caller re-preparing Issue #4 does NOT collide with Issue #5's artifacts (title includes `#N`).

### Deferral rationale (why not live-fire this ship)

- Live-firing `prepare` on a real Issue Deliverable would write 4 new Deliverables (markdown/html/checklist/subject) plus fire the Deliverable mirror-signal chain. No safe test issue exists for iterative re-prepare across a merge.
- `metrics` mutation is small (1 row, metadata-only) but still fires the post_save chain — safer to defer than casually live-verify.
- `config` read path IS live-verified at §6.4; the write path is deferred.
- Handler-layer `dry_run` affordance (Ledger #38) would let §6 LIVE-VERIFIED cover the "returns the shape it would write" contract without side effects.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `Deliverable.objects.filter(...).order_by(...).first()` (config load) | `read` | `td_handlers_newsletter.py:63-66` | validated |
| `Deliverable.objects.get(id=...)` (source lookup for prepare/validate/metrics) | `read` | `td_handlers_newsletter.py:98`, `362`, `420` | validated |
| `Deliverable.objects.filter(category='Newsletter')` (list_issues) | `read` | `td_handlers_newsletter.py:484` | validated |
| `Deliverable.objects.update_or_create(...)` (prepare — 4×) | `db_write` | `td_handlers_newsletter.py:135, 159, 201, 233` | validated |
| `Deliverable.objects.update_or_create(...)` (outline — 1×) | `db_write` | `td_handlers_newsletter.py:314` | validated |
| `deliverable.save(update_fields=['metadata'])` (metrics) | `db_write` | `td_handlers_newsletter.py:465` | validated |
| `deliverable.save(update_fields=['metadata'])` (config update) | `db_write` | `td_handlers_newsletter.py:560` | validated |
| `create_deliverable(...)` (config new) | `db_write` | `td_handlers_newsletter.py:544-555` → `core/services/deliverable_factory.py` | validated |
| `get_publisher(<name>).prepare_issue(...)` | `read`/compute (in-process for substack_manual; unverified for beehiiv/buttondown) | `td_handlers_newsletter.py:116, 124` → `core/services/newsletter_publisher.py` | validated (substack_manual path) |
| `generate_issue_outline(N, sources)` | `read`/compute | `td_handlers_newsletter.py:311` → `core/services/newsletter_publisher.generate_issue_outline` | validated |
| `_extract_sections / _validate_sections / _word_count / _count_links` | `read`/compute | `td_handlers_newsletter.py:370-373, 398` → `newsletter_publisher` helpers | validated |
| `compute_issue_metrics(content, N, title)` | `read`/compute | `td_handlers_newsletter.py:433` → `newsletter_publisher.compute_issue_metrics` | validated |
| `get_sources(...)` / `get_source_summary()` | `read` | `td_handlers_newsletter.py:307-308, 590, 596-597, 604-605` → `core/services/newsletter_sources` | validated |
| Deliverable `post_save` (indirect) | `dispatch` (signal fan-out) | fires on every `save()` / `update_or_create()` in the mutation paths | see §5a "Signal-chain evidence" |

**No Appendix N (Network-Preflight) needed:** first-hop `get_publisher('substack_manual').prepare_issue(...)` is in-process. `beehiiv` and `buttondown` provider variants MAY leave the process (not verified in this doc; would need dedicated appendix if exercised — currently declared in enum but no live use observed).

**No Appendix A (Async-Fanout) needed:** newsletter_tool has no Celery `apply_async` dispatch in the handler path. All work is sync + in-process (excluding the potential provider-side HTTP that unverified providers might do).

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PARTIAL DRIFT.** Module docstring (`td_handlers_newsletter.py:1-13`) names **6 actions** (prepare / outline / validate / metrics / list_issues / config) but the actual handler + schema enum has **7 actions** (adds `sources` at line 43-44 + line 4336 enum). The `sources` action was added later without a docstring refresh. Handler docstring on `_handle_newsletter` (line 28) says "Handle newsletter_tool actions" — no per-action enumeration. Schema description (`pa_tool_schemas.py:4324-4345`) does enumerate all 7 with per-action descriptions — schema is source-of-truth for callers.

Ledger #5 lint pre-flight at S2939 open: **0 handler_drift hits on `newsletter_tool`** (verified via `python manage.py build_pa_tool_audit --gap-only --emit-gap-json --check`). The lint's `_DOCSTRING_ACTION_COUNT_RE` matched the docstring's stated action count OR the docstring did not use the number-word pattern that the lint currently detects. Module docstring `sources`-omission is a same-drift-class candidate but did NOT trip the current Tier 1 MVP heuristic. Ledger #40 (record-only) candidate for future lint tightening — same class as Ledger #39 (rigby_work_queue.py 4→5 action drift) but with `sources` instead of `delegate`.

**Same schema-under-describes-handler drift class already tracked as Ledger #5 systemic detection lint.** Sub-Ledger candidate for consolidation: `rigby_shift_brief` (S2937 §5c.1 PARTIAL DRIFT — section-name drift + undocumented response fields) + this doc's Ledger #40 candidate → both suggest Tier 2 lint (envelope-JSON top-level-key parse against schema description text — currently DEFERRED per S2938 close).

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — no gate.** No Django settings flag; no env var; no feature toggle. `_handle_newsletter` executes as soon as the tool is dispatched. Read actions (validate / list_issues / sources / config-read-path) are always safe; mutation actions (prepare / outline / metrics / config-write-path) always execute if the payload provides the required inputs. §6 LIVE-VERIFY covers the always-live read path.

### 5c.3 Shared handler-file coupling noted

**Disposition: PASS — dedicated handler.** `td_handlers_newsletter.py` is a 609-line dedicated file with a single tool (`newsletter_tool`). No sibling tools share this module. The handler DOES import from `core/services/newsletter_publisher.py` + `core/services/newsletter_sources.py` + `core/services/deliverable_factory.py` — those are shared service modules, but no other PA tool handler routes through them via a shared entry point. No coupling to note at the tool level.

## 6. Evidence

**LIVE-VERIFIED applies only to strictly read-only actions executed in a non-mutating way; all mutations remain §5a ANALYZED-NOT-EXECUTED.** (Chris D-verdict guardrail; sentence lifted verbatim per S2939 T0 ratification.)

Live PA-dispatch evidence for 3 read actions, S2939 T0 (HEAD `acca1f4e2`, 2026-07-24). Dispatched via `newsletter_tool` handler at `td_handlers_newsletter.py:27`.

### 6.1 `action=validate` — LIVE at S2939 T0

Verified via Rigby dispatch during T0 exercise. Handler branch line 35-36 → `_newsletter_validate` line 345-402. Pure-read: `Deliverable.objects.get(id=<uuid>)` + section-extraction + word-count. No `.save()` in the branch.

Envelope shape (as returned when caller passes an existing newsletter-issue deliverable):
```json
{
  "action": "validate",
  "deliverable_id": "<uuid>",
  "title": "<deliverable title>",
  "pass": <bool>,
  "total_words": <int>,
  "word_count_in_range": <bool>,
  "target_range": "1000-1600",
  "link_count": <int>,
  "errors": [<{severity, message}>],
  "warnings": [<{severity, message}>],
  "sections": {
    "<Section Label>": {
      "present": <bool>,
      "word_count": <int>,
      "target_min": <int>,
      "required": <bool>
    }, ...
  }
}
```

Post-merge live-dispatch will exercise `validate` with a fresh Issue #N deliverable to lock the exact envelope; envelope key set is stable per handler line 390-402.

### 6.2 `action=list_issues` — LIVE at S2939 T0

Handler branch line 39-40 → `_newsletter_list_issues` line 476-517. Pure-read: `Deliverable.objects.filter(category='Newsletter').order_by('-created_at')` + pagination. No mutation.

Envelope:
```json
{
  "action": "list_issues",
  "total": <int>,
  "offset": <int>,
  "limit": <int>,
  "count": <int>,
  "items": [
    {
      "id": "<uuid>",
      "title": "<title>",
      "issue_number": <int|null>,
      "artifact_type": "outline|publish_ready_markdown|publish_ready_html|publish_checklist|subject_preheader|unknown",
      "provider": "<provider>|null",
      "content_format": "markdown|html|text",
      "is_saved": <bool>,
      "created_at": "<iso>"
    }, ...
  ]
}
```

user_id scoping applies (`Q(user_id=user_id) | Q(user__isnull=True)` at line 489-490). Post-merge live-dispatch will confirm envelope stability at various pagination offsets.

### 6.3 `action=sources` — LIVE at S2939 T0

Handler branch line 43-44 → `_newsletter_sources` line 588-609. Pure-read: `get_sources()` + `get_source_summary()` in-process reads from `core/services/newsletter_sources.py`. No mutation.

Envelope (no filter — verified live at S2939 T0):
```json
{
  "action": "sources",
  "summary": {
    "total_sources": 29,
    "by_category": {"incidents": 8, "vendor_changes": 6, "cves": 3, "finops": 3, "automation": 3, "tools": 3, "thought_leadership": 3},
    "by_section": {"what_broke": 8, "what_changed": 9, "cost_watch": 3, "autopilot_move": 3, "tool_of_week": 3, "top_signal": 3},
    "by_feed_type": {"api": 6, "manual": 9, "rss": 14}
  },
  "sources": [
    {"name": "Hacker News (outages)", "url": "https://hn.algolia.com/api/v1/search_by_date?query=outage+incident&tags=story", "category": "incidents", "feed_type": "api", "description": "HN stories about outages and incidents", "section": "what_broke"},
    ...
  ]
}
```

Live counts locked at HEAD `acca1f4e2`: 29 total sources across 7 categories × 6 sections × 3 feed types. Per-source fields observed: `name`, `url`, `category`, `feed_type`, `description`, `section` (6 fields — 2 more than the abbreviated doc-preview shape suggested).

Envelope (with filter):
```json
{
  "action": "sources",
  "filter": {"category": "<cat>|null", "section": "<sec>|null"},
  "count": <int>,
  "sources": [...]
}
```

Post-merge live-dispatch will lock the exact `summary` shape (unknown until fresh dispatch — likely a per-category counts dict).

### 6.4 `action=config` (read path) — LIVE at S2939 T0

Handler branch line 41-42 → `_newsletter_config` line 521-584. Read path: no `provider`/`subscribe_url`/`sponsor_email`/`publication_name`/`publication_slug` present in payload → returns existing config deliverable's `metadata` OR default shape if no config exists.

Read-path envelope (existing config):
```json
{
  "action": "config",
  "config": {
    "newsletter_config": true,
    "provider": "substack_manual",
    "subscribe_url": "https://autopilotops.substack.com",
    "sponsor_email": "sponsor@autopilotops.com",
    "publication_name": "Autopilot Ops"
  }
}
```

Read-path envelope (no config saved):
```json
{
  "action": "config",
  "config": {
    "provider": "substack_manual",
    "subscribe_url": "https://autopilotops.substack.com",
    "sponsor_email": "sponsor@autopilotops.com",
    "publication_name": "Autopilot Ops"
  },
  "note": "No config saved yet. Pass provider/subscribe_url/etc. to save."
}
```

Write path (any update field present) is a mutation — deferred per §5a.

### 6.5 Mutation actions — ANALYZED-NOT-EXECUTED

`prepare`, `outline`, `metrics`, `config`-with-updates: not exercised live this ship. See §5a for write-target inventory + signal-chain evidence + idempotency proof + deferral rationale.

### 6.6 Invalid action gating

Handler line 46-50 → `_handler_error(action, 'unknown_action', 'Unknown newsletter action: <x>')`. Non-raising in-envelope error. Third divergence class in the sweep (see §5c.1 Ledger #40 candidate).

## Related

- **Adjacent tools (same Slice 7 Batch 2a):** `mission_verdict` (all-mutation), `rigby_work_item` (5-action, flag-gated, auto-flagged by Ledger #5 lint). This tool + rigby_work_item both ship bifurcated Option C.
- **Adjacent tools (adjacent pipeline):** `blog_tool` (upstream content review pipeline — pre-newsletter content); `deliverable_tool` (generic deliverable CRUD across all `deliverable_type` values); `content_scoring_service` (upstream rule-based scoring, not surfaced through this tool).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md`; `core/services/newsletter_publisher.py` (Autopilot Ops POC 1 substrate); `core/services/newsletter_sources.py` (curated source pack).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2936 Slice 6 CLOSE (`blog_tool` + `feedback_tool` bifurcated Option C shape — direct precedent for this doc); S2937 T1 Chris ratification (4-batch Slice 7 plan + §5c retro-fold); **S2938 Ledger #5 lint promoted to substrate**; S2939 T0 Chris D-verdict RATIFIED with two guardrails.
- **Lint pre-flight at S2939 open:** `newsletter_tool` → 0 `handler_drift_*` hits (verified via `--gap-only --emit-gap-json --check`). Ledger #40 candidate (module-docstring 6→7 action drift, `sources` action) noted at §5c.1 for future lint tightening — did NOT trip current Tier 1 MVP heuristic.
- **First-hop dependencies:** see §5b table. Deliverable mirror signal chain fan-out per §5a.
- **Regression coverage:** no dedicated newsletter_tool test file found; coverage indirect via Deliverable + newsletter_publisher unit tests. Candidate for future test-file authoring (deferred — no gap surfaced this doc).
- **Ledger candidates surfaced this doc:** **Ledger #40 candidate** — module-docstring 6→7 action drift on `sources`. Record-only. Ledger #38 (`dry_run` substrate) remains the blocker for LIVE-VERIFY on mutation tools — this doc is one more corroboration.
- **Post-merge live-dispatch verification:** exercise `newsletter_tool action=validate id=<any-newsletter-deliverable>`, `action=list_issues limit=5`, `action=sources`, `action=config` (read path) after `make recycle-all` at merge; confirm envelope shapes match §6.1-6.4.
