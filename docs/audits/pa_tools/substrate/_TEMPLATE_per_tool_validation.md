<!--
T1b canonical per-tool validation template (v1).

Ratified S2904 (Row 161 substrate arc, thread 3/3). Ship-shape doc:
`docs/audits/pa_tools/substrate/T1b_ship_shape_s2904.md`.

## How to use this template

1. Copy this file to `docs/research/tools/validation/<tool_name>_validation.md`.
2. Pick a variant in the `**Template variant:**` frontmatter field:
   - `sweep` — the post-S2892 lightweight shape. Default for new docs.
     Use for tools where the goal is "catalog covered actions +
     golden-path examples + failure notes." Fastest to author; feeds
     the T1a auto-harness output.
   - `protocol` — the S2796 heavy shape. Use only for tools where
     STOP-and-report failure-mode analysis is genuinely load-bearing
     (see `deliverable_tool_validation.md`, `session_tool_validation.md`
     for reference examples). Do NOT default to this; the sweep
     variant is the recommended shape.
3. Set `**Template version: v1**`. This is what activates the
   template-compliance lint at
   `core/services/pa_tools_gap_map.py:evaluate_template_compliance`.
4. Delete the variant you're NOT using from this file, then delete
   this entire HTML comment block.
5. Fill in the frontmatter + all mandatory sections for your chosen
   variant. Optional sections may be omitted if not applicable.

## Ratchet-and-warn semantics

- Docs WITHOUT `Template version:` → `warn` in the gap map. Advisory
  only; does NOT block.
- Docs WITH `Template version: v1` → mandatory-section + required-
  frontmatter-field check activates. Missing anything → `fail`
  (blocks gap-map ratchet green).
- The ratchet is opt-in: a sweep-session doc author writes
  `Template version: v1` when authoring or touching a doc. Legacy
  docs stay `warn`-flagged until touched. No bulk retrofit.

## Presence-not-exact frontmatter rule

Lint checks that required v1 fields are PRESENT, not that the
frontmatter has an exact key set. Extra keys (e.g., protocol-
variant `Downstream service`, `Reviewer`) are allowed and ignored
by lint.

## Regex for `## Covered actions` heading

The lint regex accepts:
  ## Covered actions        (bare — recommended form)
  ## 2. Covered actions     (numbered with period)
  ## 2) Covered actions     (numbered with paren)
  ## 2 — Covered actions    (numbered with em-dash)

Rejects:
  ## Actions covered        (word-order mismatch)

Bare form is the recommended default; numbered forms accepted for
future flexibility.
-->

# `<tool_name>` — Validation Report (S<NNNN>)

**Tool:** `<tool_name>`
**Schema:** `core/services/pa_tool_schemas.py:<line>`
**Handler:** `core/services/td_handlers_<slice>.py:<line>` (`_handle_<name>`)
**Register site:** `core/services/tool_dispatcher.py:<line>`
**Session:** S<NNNN> (<sweep-batch context>)
**HEAD at validation:** `<9-char-sha>` (<YYYY-MM-DD>)
**Ship shape:** Doc-only (S2796 shape). <optional: regression-test posture>
**Category upgrade target:** `<current-category>` → `<target-category>`
**Rigby SIGN:** S<NNNN> T1 SIGN <verdict> — <one-line summary + tool_runs pointer>
**Template variant:** sweep
**Template version:** v1

---

<!--
========================================================================
SWEEP VARIANT SKELETON — mandatory sections marked [MANDATORY].
Delete this variant's block if using the protocol variant.
========================================================================
-->

## 1. Purpose / when-to-use

[MANDATORY] One or two paragraphs. What questions this tool answers.
How it's distinct from adjacent tools. When Rigby should pick it.

## Covered actions

[MANDATORY] Enumerate every action in the tool's schema `action` enum.
For each: whether it was exercised live this ship, one-line description,
optional link to §6 evidence subsection.

Bare heading `## Covered actions` is recommended (matches the current
gap-map convention). Numbered form `## 2. Covered actions` also
accepted by the regex.

- `<action_1>` — **in scope this ship** — verified live. <shape/behavior summary>
- `<action_2>` — **runtime-not-executed** — <reason>
- `<action_3>` — **mutation — deferred to Slice X.Yb** — see §5a

## 3. Schema notes

[MANDATORY] Required params, common optional params, defaults,
special-case params. Cross-reference schema line-range for verbatim.

## 4. Golden-path examples

[MANDATORY] 1-3 example dispatches with input JSON + expected response
shape. Focus on the "obvious call" a Rigby operator would make.

## 5. Failure / empty-state / pagination notes

[MANDATORY] What returns when: no data, invalid input, unauthorized,
pagination cursor exhausted, edge cases discovered during exercise.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier
blast-radius taxonomy added S2921)

[OPTIONAL — required when tool has mutation actions declared as
in-scope OR ship-deferred in `## Covered actions`.]

Blast-radius classification per mutation action + explicit
deferral or in-scope rationale + Slice-when-covered pointer (or
"this ship" when in-scope).

### 4-tier blast-radius taxonomy (recommended enum; added S2921)

Introduced as authoring taxonomy — not a governance rule. Doc-only
per S2921 T0 SIGN Q3 Rigby+Claude joint verdict (§5a as-shipped
already accommodated the schema without changing the template) +
Chris ratification. Every mutation action in `## Covered actions`
SHOULD carry one of these labels; deviations MUST be justified
in-doc.

| Tier | Meaning | Typical shape |
|---|---|---|
| `contained` | Single-row INSERT / UPDATE / DELETE on a table with no FK cascade, no `post_save` signal chain, no cross-user reach. Retries produce duplicate rows or idempotent updates but do not corrupt existing state. | Append-only telemetry row; per-user preference toggle on an isolated table; single-row status flip with no downstream observers. |
| `spreading` | Row-level mutation that reaches across rows within the same user's dataset OR into a second table that stores user-scoped state. Includes bulk multi-row `.update()` calls that are user-scoped but broad (e.g. bulk-ack N rows). Blast-radius stays within a single user but is broader than a single row. | Bulk `.update(is_read=True)` over ≤200 rows; `.save()` on a row + a related-model flag flip; `get_or_create` that implicitly writes a new row into a shared table. |
| `cascading` | Mutation that fires FK cascades OR `post_save` / `pre_save` signal chains OR triggers downstream ORM-observer effects. Requires signal-chain grep to classify accurately. | Delete on a parent row that cascades to N child rows; `.save()` on a model whose `post_save` receiver enqueues a Celery task or writes a second row. |
| `external` | Mutation that leaves the process — network call, Celery `apply_async` fan-out, LLM invocation, dispatcher re-entry, or sub-tool invocation as a first-hop side effect of the mutation. | POST to an external service on `.save()`; enqueue a workflow task after row-write; publish to a broker as part of the mutation path. |

Grep discipline required: `contained` claims MUST be backed by a
signal-chain grep (search for `post_save.connect` / `@receiver` on
the model) + FK-cascade check. If either surfaces evidence, the
tier is reclassified up and the doc is amended. First mis-classification
that surfaces post-merge is a Ledger candidate.

### Mutation-scan-swap pattern (sweep-doc-only, S2921 codification)

**Pattern:** During a sweep batch's T0 SIGN, if Rigby's mutation-verb
scan flags a candidate tool as mutation-capable that the batch-open
frame assumed was pure-read, do NOT force the tool into the pure-read
template. Instead:

1. Swap the mutation-capable tool out of the batch (defer to a
   future mutation-shaped batch).
2. Swap in a confirmed pure-read tool from the same slice, OR
3. Escalate to split-batch: ship the confirmed pure-read subset,
   defer the mutation-capable subset to the next appropriate batch.

**Applied at:** S2919 (vip_invite → narrative swap) + S2920
(proactive+self_awareness+profile split-batch escalation). 2
triggers, both inside the current PA-tools sweep.

**Promotion rule (Playbook candidate threshold):** This pattern
stays a sweep-doc note UNTIL a 3rd trigger occurs OUTSIDE the
current PA-tools sweep context (i.e., in a different workstream, a
post-sweep audit, or an unrelated batch-based initiative). At that
point, promote to Playbook via the normal amendment process. Until
then, keep applied but ungoverned — sweep tactic, not global rule.
Precedent for two-trigger sweep-note → three-trigger Playbook
promotion: PLAYBOOK-6.10.6 (S2739 + S2741 sweep-note, promoted at
third trigger).

### Process hygiene — freeze template per ship session (S2921)

If a ship session needs template changes mid-flight (a mutation-shape
gap, a new §5a tier, a §5b appendix that didn't exist yet), the
correct move is to end that ship session with 0-or-1-tool progress
and dedicate the next session to template design. Do NOT edit the
template AND ship multiple tools in the same session — that mixes
"design substrate" with "validate under substrate" and produces the
false-safety hazard where earlier tools in the session were
validated under a different template than later tools. When only 1
low-risk pilot tool is available (unambiguous mutation surface,
`contained` tier), shipping the pilot alongside a template
amendment is acceptable — the pilot itself is the amendment
exercise. When 2+ tools would need to ship under the changing
template, split into design-only + ship-only sessions.

## 5b. First-hop dependency proof

[OPTIONAL — recommended when tool has any first-hop that leaves the
handler (network, Celery fan-out, LLM call, dispatcher re-entry, or
sub-tool invocation). Introduced S2915 (row-create trio). Extended
S2916 with **Appendix N (Network-Preflight)**. Extended S2917 with
**Appendix A (Async-Fanout)** for tools whose first-hop is a Celery
`apply_async` dispatch. Ratified S2917 Fold: standardized appendices
prevent §5b "notes-field creep" into unreviewable policy surface
(row #38 promoted at Slice 3 CLOSE).]

Table format: one row per direct dependency. Columns: `Direct
dependency | Classification | Evidence (file:line) | Callee-status`.
Classification enum: `read` / `network` / `llm` / `db_write` /
`db_delete` / `dispatch` / `opaque`.

### Appendix N — Network-Preflight (first-hop = network)

Fill only if a first-hop leaves the process via HTTP/socket. 5 fields:

- **N1. Endpoint derivation source** — where the URL/host is resolved from (settings, env var, repo config, user payload). Enumerate; note if multi-endpoint.
- **N2. Auth posture** — `bearer_token` / `basic_auth` / `none` / `hmac`. Cite the resolver function. Note redaction behavior.
- **N3. Timeout envelope** — connect/read/write/pool timeouts + retry policy + total-run bound.
- **N4. SSRF / egress allowlist** — allowlist regex + private-IP block behavior. Note if URL source is repo-controlled (may waive allowlist).
- **N5. Redirect + non-2xx handling** — redirect follow behavior + how non-2xx surfaces to the caller.

### Appendix A — Async-Fanout (first-hop = Celery `apply_async` or task-dispatch wrapper)

Fill only if a first-hop dispatches asynchronously into a Celery task
or task-wrapper that resolves to an agent/spider/workflow. Introduced
S2917 batch 7 per Rigby T0 SIGN Q2 AGREE-with-edits.

- **A1. Dispatch target type(s)** — enumerate: `agent_task_wrapper` (Celery task that resolves to an AGENT_MAP entry, e.g. `execute_agent_task`), `workflow_task` (multi-stage task like `run_source_pack_workflow`), `spider_job`, `direct_task`. Note first-hop opacity: what the handler SEES vs what actually runs.
- **A2. Queue name(s) + priority** — Celery queue string(s) declared at each `apply_async` site. Priority optional; document only if set. Note whether queue is a shared-worker queue or dedicated pool.
- **A3. Task_id envelope + polling contract** — three sub-fields:
  - (a) **Identifiers returned**: minimally `task_id`; often also a domain-object id (e.g. `run_id`). Document dual-identifier envelope shape.
  - (b) **Polling endpoint(s)**: how the caller checks completion — `AsyncResult`, a `CeleryTaskEvent` row, a domain-object row with a status field, or a dedicated status action on the same tool.
  - (c) **Idempotency stance**: `none` / `dedupe_key: <key>` / `safe_re_run: yes|no`. Explicit declaration required even if the answer is `none`.
- **A4. Downstream side-effect boundary** — the side effects that fire in the fanned-out work (LLM calls, DB writes, network fetches, sub-tool dispatch, dispatcher re-entry). Cite the task-implementation file+line, not just the entrypoint. Explicit call-out for **dispatcher re-entry** (fanned-out task calling back into `tool_dispatcher._handle_*`) as an audit hotspot.
- **A5. Observability + cancel semantics + revisit triggers** — three sub-fields:
  - (a) **Observability contract**: where the caller checks status; what fields are authoritative; what is best-effort.
  - (b) **Cancel semantics**: revoke path (if any) + `terminate=True/False` + domain-side status marker. Explicit "no cancel" allowed as an answer.
  - (c) **Revisit triggers**: what future evidence would force a re-audit of this Appendix A (schema/handler/queue/task changes; new dispatcher re-entry sites; new opaque callees added downstream).

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

[MANDATORY] Three-item consistency check between what the docstrings /
schema descriptions / module headers CLAIM and what the code ACTUALLY
does. Added S2937 open before Slice 7 batch 1 shipped, motivated by a
concrete drift found in Slice 7 handler-read (Ledger #39): the
`td_handlers_rigby_work_queue.py` module docstring stated "four actions"
+ "No agent dispatch", but the handler has 5 actions with async
dispatch via a service. Without this consistency check, the sweep-close
artifact codifies stale docstrings as "trusted contracts."

Each item requires an explicit one-sentence disposition per doc.
Mismatches surface a Ledger hygiene candidate — recording is required;
same-PR fix is optional.

### 5c.1 Handler / module header claims match action reality

Cross-check the module docstring + tool-schema `description` field
against the handler's actual behavior:
- Number of actions in the `action` enum vs. what the docstring names.
- Which actions are mutations vs. reads (matches §5a classification).
- Whether any action triggers **dispatch** (Celery `apply_async`),
  **external API calls** (network I/O), **LLM invocations**, or other
  side effects — matches §5b Appendix N / Appendix A.

**Disposition:** state PASS / DRIFT + one sentence. On DRIFT, cite
handler line evidence and open a Ledger entry (record-only is fine).

### 5c.2 Gating truth matches runtime behavior

If the tool is flag-gated (Django settings toggle, env var, feature
flag), the doc must state:
- What the tool returns when the flag is OFF (usually a
  short-circuited `disabled_response` shape).
- What §6 LIVE-VERIFY actually verifies given the flag's current
  default state — the disabled-path shape (when flag defaults OFF) OR
  the enabled behavior (when flag defaults ON).

If NOT flag-gated, one sentence noting "no gate — always live" is
sufficient.

**Disposition:** state PASS / DRIFT + one sentence. Flag-gated tools
whose §6 evidence doesn't align with current flag state = DRIFT.

### 5c.3 Shared handler-file coupling noted

When multiple tools share a handler module (e.g., `employee_tool` +
`mission_verdict` both live in `td_handlers_employee.py`), each
per-tool doc must include a short "shared module" cross-link so future
operators editing the shared file don't miss coupled tools.

If the tool has a dedicated handler file (1 tool per file), one
sentence noting "dedicated handler — no shared-module coupling" is
sufficient.

**Disposition:** state coupling status + cite sibling tools if any.

## 6. Evidence

[MANDATORY] Per-action evidence: request/response captures, latency,
observed behaviors, DB row diffs, log excerpts. Sub-section per action
or per action-family.

## 7. Raw evidence appendix (Tier-2)

[OPTIONAL — recommended when exercised action count >50 per S2895
2-tier pattern. See `autopilot_tool_validation.md` §7 for reference.]

Full JSON dumps of raw dispatch responses, grouped by action family.
Excluded from Tier-1 §6 narrative to keep the primary evidence
readable.

## Related

[MANDATORY] Cross-references to: adjacent tools (with distinctions),
substrate docs that touch this tool, prior ratifications, ledger rows.

---

<!--
========================================================================
PROTOCOL VARIANT SKELETON — S2796 heavy shape.
Delete this block if using the sweep variant.

Set frontmatter `**Template variant: protocol**`.
Alias frontmatter fields allowed per §2.4 (Main handler / Session
validated / Report status / Rigby cross-check / etc).
========================================================================
-->

<!--
## 1. Intended purpose (per schema description)

[MANDATORY] Verbatim quote of the schema `description` field.

## 2. Rigby's belief (per schema + MEMORY rules + prior conversations)

[MANDATORY] What Rigby's model of this tool is. MEMORY-rule pointers.
Load-bearing prior beliefs.

## 3. Schema claim (verbatim capture)

[MANDATORY] Full schema block quoted from `pa_tool_schemas.py`. Line
range pointer.

## 4. Handler behavior (traced through code)

[MANDATORY] Step-by-step trace of what the handler does per action.
Line-numbered pointers into `td_handlers_*.py` + downstream service.

## 5. Defaults inventory (per parameter)
## 6. Hidden filters inventory
## 7. Limits inventory
## 8. Silent-truncation test
## 9. Silent-filter test
## 10. Silent-fallback test
## 11. Staleness test
## 12. Freshness signal
## 13. Provenance signal
## 14. Authority / workspace assumptions
## 15. Runtime dependencies
## 16. Recoverable failure modes
## 17. STOP-and-report failure modes
## 18. Operator-action failure modes
## 19. Existing test coverage
## 20. Change list

[Section 5-20 are LOAD-BEARING when the protocol variant is chosen,
but not all 20 are mandatory for lint pass. Author judgment on which
of §5-§20 to include based on tool complexity.]

## Findings

[MANDATORY protocol variant] Discovered bugs, drift, unexpected
behaviors. Cross-reference PRs that mitigated.

## Verdict

[MANDATORY protocol variant] Category upgrade decision + rationale.
Rigby SIGN outcome.
-->
