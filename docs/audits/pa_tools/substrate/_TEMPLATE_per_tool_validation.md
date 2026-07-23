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

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

[OPTIONAL — required when tool has mutation actions declared as
ship-deferred in `## Covered actions`.]

Blast-radius classification per mutation action + explicit deferral
rationale + Slice-when-covered pointer.

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
