# T1b — Family-Doc Template Extraction

**Parent:** [S2900 substrate arc scoping](S2900_substrate_arc_scoping.md)
**Session estimate:** 1–2 sessions.
**Depends on:** T1a output-schema contract must be stable before template rigidifies (parent §3).
**Ratchet posture:** mandatory-on-touch, advisory-warn-on-legacy (Rigby SIGN D REVISE, adopted).

---

## 1. Goal

Extract a canonical template for per-tool validation docs. Current state: 22 per-tool validation docs, but only 14 have an explicit "Covered actions" section (per `PA_TOOLS_GAP_MAP.md` headline). Uniformity is drifting.

Template canonicalizes:
- Required top-of-file frontmatter (tool name, schema path, handler path, register site, session, HEAD, ship shape, category upgrade target).
- Required sections (§1 Purpose, §Covered actions, §3 Schema notes, §4 Golden-path examples, §5 Evidence, §6 Raw appendix if 2-tier).
- Optional sections (§5a mutation-deferred list, §7 Notes / caveats).

## 2. Ratchet-and-warn posture (per Rigby SIGN D REVISE)

**Mandatory (blocks gap-map ratchet green):**
- Any **new** per-tool validation doc (authored during a sweep session).
- Any **edited** per-tool validation doc (existing doc modified in a way that changes the covered-actions surface).

**Advisory-warn (does not block; surfaces in gap-map):**
- Legacy per-tool docs that predate T1b. Warning fires in gap-map "template compliance" column; only ratchets to blocking on next-touch.

**Rationale:** mandatory-block on all 22 legacy docs would create bulk-retrofit churn (parent §2 anti-goal). Pure advisory would let drift continue. The ratchet-on-touch middle path converges toward uniformity without a big-bang migration.

## 3. Template content

Draft template file location: `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (leading underscore = "not a real validation doc").

Sections that the T1a harness output can pre-populate (via a companion `pa_tool_scaffold_validation_doc` sub-command, if MVP allows):
- Frontmatter (all fields extractable from harness JSON + tool schema).
- §3 Schema notes (extractable from schema introspection).
- §4 Golden-path examples (READ_ONLY dispatches from harness artifact).
- §Covered actions (list of dispatched actions from harness artifact).

Sections that require human judgment (harness cannot pre-populate):
- §1 Purpose / when-to-use (narrative).
- §5 Evidence discussion (interpretation of harness output).
- §7 Notes / caveats (edge cases discovered during sweep).

## 4. Gap-map lint extension

`build_pa_tool_audit` command gains a "template compliance" column in `PA_TOOLS_GAP_MAP.md`:

| Column value | Meaning |
|---|---|
| `✓` | Doc has all mandatory sections. |
| `warn` (advisory) | Legacy doc missing sections; not blocking, will ratchet-on-touch. |
| `✗` (blocking) | New/edited doc missing mandatory sections; blocks gap-map green. |

## 5. Non-goals

- **Not** a bulk retrofit of the 22 existing docs. Ratchet-on-touch handles this over time.
- **Not** a substrate for enforcing narrative quality of §1 Purpose or §5 Evidence prose — template governs structure only.
- **Not** a replacement for judgment during sweep-session validation. Template is scaffolding; sweep is still human-driven.

## 6. Ship shape

- Template file at `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md`.
- Lint extension in `build_pa_tool_audit` management command (or its callee) enforcing ratchet-and-warn posture.
- Documentation of the ratchet posture in the template file's header comment (so future doc authors see it immediately).
- Optional: `pa_tool_scaffold_validation_doc` sub-command that generates a template-conformant stub from a T1a harness artifact (deferred to T1b hardening session if v1 is tight).
