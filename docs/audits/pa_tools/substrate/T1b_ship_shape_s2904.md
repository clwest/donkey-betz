# T1b — Ship-Shape Proposal (S2904)

**Parent frame:** [T1b_family_doc_templates.md](T1b_family_doc_templates.md) (thread doc), [S2900_substrate_arc_scoping.md](S2900_substrate_arc_scoping.md) (arc parent).
**Author:** Claude (S2904 open, 2026-07-22).
**Status:** POST-RIGBY-SIGN v2 — pending Chris D-verdict.
**Ship shape:** Doc + code, single PR. Doc-only touches on the 19 legacy validation docs remain out of scope (arc parent §5 anti-goal).
**Rigby SIGN status:** T1 routed 2026-07-22 with tool-grounded verification (10 tool_runs). Rigby returned SIGN A/B/C AGREE-with-edits, D REVISE (blocking, 2 concerns), E/F AGREE-with-edits, zoom-out Q1-Q9 with same-PR + forward-carry classification. All same-PR mitigations folded into this v2 draft. Rigby recommendation: **approve directionally, block merge until D-1 + D-2 land**; both are folded here.

---

## 1. Corpus survey (evidence for two-variant declaration)

**Ground-truth counts at HEAD `d24176fd5` (verified by direct enumeration, S2904):**

- **19** `*_tool_validation.md` files (per-tool validation docs, the T1b template scope).
- **14** have `## Covered actions` heading → **sweep-shape**.
- **5** follow the S2796 20-numbered-section shape → **protocol-shape**.
- **13** additional `*_validation.md` files exist but are OUT OF SCOPE for T1b: 10 substrate docs (already excluded via `SUBSTRATE_DOC_STEMS` at `pa_tools_gap_map.py:75`) + 3 per-tool-adjacent docs that don't follow the `*_tool_validation.md` naming (`agent_introspection_run_agent_validation.md`, `kb_ingest_validation.md`, `workspace_retrieval_validation.md`).

**Family A — sweep shape (14 docs).** Post-S2892 sweep-batch output. Sections:

- `## 1. Purpose / when-to-use`
- `## Covered actions` (**bare heading today; T1b will loosen the regex per Rigby ZO-Q3 same-PR — see §4.2**)
- `## 3. Schema notes`
- `## 4. Golden-path examples`
- `## 5. Failure / empty-state / pagination notes` (or `...staleness / attribution notes` — variant title, same section)
- `## 5a. Mutation containment (per Rigby SIGN zoom-out #1)` — **optional**; present when the tool has mutation actions being ship-deferred (S2894+ pattern; observed in scheduled_tasks, governor, workspace_budget, spider_status, ops_digest, autopilot)
- `## 6. Evidence`
- `## 7. Raw evidence appendix (Tier-2)` — **optional**; present when the tool has >50 exercised actions (S2895 2-tier pattern; observed only in autopilot to date)
- `## Related`

Tools in sweep shape: `active_priority`, `agent_control`, `agent_memory`, `autopilot`, `diagnostics`, `governor`, `heartbeat_history`, `infra_health`, `ops_digest`, `ops_tool`, `scheduled_tasks`, `spider_status`, `status_snapshot`, `workspace_budget`.

**Family B — protocol shape (5 docs).** S2796-original heavy shape. 20 numbered sections + Findings + Verdict:

- §1 Intended purpose / §2 Rigby's belief / §3 Schema claim / §4 Handler behavior / §5 Defaults inventory / §6 Hidden filters / §7 Limits inventory / §8-§11 Silent-truncation/-filter/-fallback/-staleness tests / §12-§14 Freshness/provenance/authority signals / §15 Runtime dependencies / §16-§18 Recoverable/STOP-and-report/operator-action failure modes / §19 Existing test coverage / §20 Change list
- `## Findings`
- `## Verdict`

Tools in protocol shape: `claude_code_tool`, `deliverable_tool`, `repo_tool`, `search_docs_kb_tool`, `session_tool`.

**Frontmatter — TARGET STATE (not current state).** Rigby SIGN A edit: today, sweep docs have a stable 9-field frontmatter (Tool / Schema / Handler / Register site / Session / HEAD / Ship shape / Category upgrade target / Rigby SIGN); protocol docs have variant-specific keys (e.g., `session_tool` adds `Main handler`, `Downstream service`, `Reviewer`, `Session validated`, `Report status`). T1b's "v1 required fields" are the **target** to converge on; lint checks **presence, not exact key set** — extra keys are allowed.

## 2. Proposed template shape

**Default: sweep variant.** Rationale: 14 of 19 per-tool docs; also aligns with T1a harness output which pre-populates §Covered actions + §4 Golden-path.

**Retained variant: protocol.** The 5 S2796 docs remain valid. Author-declared in frontmatter. Do NOT retrofit; do NOT deprecate.

### 2.1 Sweep variant mandatory sections

- `## 1. Purpose / when-to-use`
- `## Covered actions` — matched via the loosened regex per §4.2 (optional numbering accepted)
- `## 3. Schema notes`
- `## 4. Golden-path examples`
- `## 5. Failure / empty-state / pagination notes` (prefix match on `## 5. Failure` — variant titles allowed)
- `## 6. Evidence`
- `## Related`

### 2.2 Sweep variant optional sections

- `## 5a. Mutation containment` — required when tool has mutation actions declared as ship-deferred in `## Covered actions`
- `## 7. Raw evidence appendix (Tier-2)` — recommended when exercised action count >50 (per S2895 2-tier pattern)

### 2.3 Protocol variant mandatory sections

- `## 1. Intended purpose`
- `## 2. Rigby's belief`
- `## 3. Schema claim (verbatim capture)`
- `## 4. Handler behavior (traced)`
- `## Findings`
- `## Verdict`

(§5-§20 remain load-bearing for the protocol variant's diagnostic depth, but lint does NOT require the full 20-section spread — author judgment on which of §5-§20 are load-bearing for the specific tool.)

### 2.4 Frontmatter — v1 required fields (presence check only)

- `**Tool:**`, `**Schema:**`, `**Handler:**` (or `**Main handler:**` — either accepted, presence check on the pattern `**{Main }?Handler:**`)
- `**Register site:**`
- `**Session:**` (or `**Session validated:**` — presence check on `**Session[a-z ]*:**`)
- `**HEAD at validation:**`
- `**Ship shape:**` (or `**Report status:**` — protocol variant equivalent; either accepted)
- `**Category upgrade target:**` (sweep-variant-only; protocol variant may omit)
- `**Rigby SIGN:**` (sweep) OR `**Rigby cross-check:**` (protocol) — either accepted
- **NEW: `**Template variant:**`** — accepted values: exactly `sweep` OR `protocol` (case-sensitive, whitespace-trimmed). Any other value → lint fail.
- **NEW: `**Template version:**`** — accepted values: matches `^v\d+$` (currently only `v1` has defined semantics). Absent → advisory `warn` (legacy); present but non-matching → lint fail (per Rigby SIGN C edit).

**Extra keys allowed.** Protocol docs may have additional frontmatter keys (`Downstream service`, `Reviewer`, `Session validated`, etc.). Lint enforces presence-not-exact.

## 3. Ratchet-and-warn lint semantics

Per T1b_family_doc_templates.md §2 (Rigby SIGN D REVISE, adopted at arc-open), updated per S2904 Rigby SIGN C edit:

| Doc state | Lint verdict | Rationale |
|---|---|---|
| No `Template version:` frontmatter field | `warn` (advisory) | Legacy pre-T1b doc. Does NOT block gap-map. |
| `Template version: v1` + `Template variant: sweep` + all §2.1 sections present + all §2.4 required fields present | `pass` | New/edited T1b-conformant sweep doc. |
| `Template version: v1` + `Template variant: protocol` + all §2.3 sections present + all §2.4 required fields present | `pass` | New/edited T1b-conformant protocol doc. |
| `Template version:` present but value doesn't match `^v\d+$` (e.g. `Template version: 1`) | `fail` (**blocking**) | Rigby SIGN C: prevents ambiguous drift. |
| `Template version: v1` present but section/frontmatter check fails | `fail` (**blocking**) | Author declared v1 compliance but the doc doesn't meet it. Blocks gap-map ratchet green. |
| `Template variant:` present but value not in `{sweep, protocol}` | `fail` (**blocking**) | Invalid variant declaration. |

**Ratchet firing rule:** the T1b template version marker is opt-in. A sweep session author OR a re-sweep author writes `Template version: v1` when they touch a doc, at which point the mandatory-section check activates. Legacy docs stay `warn`-flagged until touched.

**Forward-carry trigger (per Rigby ZO-Q2 — warn-noise escalation ladder):** if `warn` count stalls above threshold after 5+ sweep sessions (currently 19 `warn`, target: monotonic decrease of ≥1 per touched-doc PR), escalate — any TOUCHED legacy doc must upgrade to `Template version: v1` in same PR. Do NOT escalate untouched legacy. Log to Rigby Tool Gap Ledger as `future_trigger` at T1b ship.

## 4. Lint implementation plan

Extension lives in `core/services/pa_tools_gap_map.py` (not `build_pa_tool_audit.py` — the classifier is pure logic, the command is thin shell).

### 4.1 Extend `index_validation_docs`

**Rigby SIGN D-1 mitigation (blocking, same-PR):** current implementation at `pa_tools_gap_map.py:136` does `docs = sorted(docs_dir.glob('*_validation.md'))` which would include `_TEMPLATE_per_tool_validation.md`. Add an explicit filter:

```python
docs = sorted(
    p for p in docs_dir.glob('*_validation.md')
    if not p.name.startswith('_')
)
```

Extend return shape with:

- `template_version_by_stem: Dict[str, Optional[str]]` — value of `**Template version:**` frontmatter field, or `None` if absent.
- `template_variant_by_stem: Dict[str, Optional[str]]` — value of `**Template variant:**` frontmatter field, or `None` if absent.
- `frontmatter_fields_by_stem: Dict[str, Set[str]]` — set of `**Field:**` keys observed above the first `---` divider.
- `heading_titles_by_stem: Dict[str, List[str]]` — ordered list of `##`-level heading titles.

### 4.2 Regex loosening (Rigby SIGN D-2 blocking, same-PR)

**Change to `pa_tools_gap_map.py:96`:**

```python
COVERED_ACTIONS_HEADING_RE = re.compile(
    r'^#+\s+(?:\d+[\.\)\-–—:]?\s*)?covered\s+actions\b',
    re.IGNORECASE | re.MULTILINE,
)
```

Accepts:
- `## Covered actions` ✓ (bare — current form)
- `## 2. Covered actions` ✓ (numbered with period)
- `## 2) Covered actions` ✓ (numbered with paren)
- `## 2 — Covered actions` ✓ (numbered with em-dash)

Rejects:
- `## Actions covered` ✗ (word-order — Rigby SIGN E test requirement)
- `### Not really covered actions` ✗ (extra prefix words)

**Regression test coverage in `tests/services/test_pa_tools_gap_map.py`:** all four accept forms + both reject forms (per Rigby SIGN E edit 2).

**Non-goal:** T1b does not require doc authors to switch to numbered form. Bare `## Covered actions` remains the recommended form; numbered form is accepted for future flexibility.

### 4.3 New pure function

```python
def evaluate_template_compliance(
    stem: str,
    docs_index: Dict[str, Any],
) -> Dict[str, Any]:
    """Return {'verdict': 'pass' | 'warn' | 'fail', 'missing': [...], 'variant': str | None}.

    Ratchet semantics per T1b §3. Presence-not-exact for frontmatter fields
    per Rigby ZO-Q9.
    """
```

Behavior:
- No `Template version:` → `{'verdict': 'warn', 'missing': [], 'variant': None}` (legacy advisory)
- `Template version:` present but doesn't match `^v\d+$` → `fail` with `template_version_invalid` in missing list
- `Template variant:` present but not in `{sweep, protocol}` → `fail` with `template_variant_invalid`
- `Template version: v1` + variant valid + section/frontmatter check → `pass` if all mandatory sections present + all required frontmatter fields present (presence-not-exact), else `fail` with per-item missing list

### 4.4 Extend `build_gap_map` output

Add per-row `template_compliance: 'pass' | 'warn' | 'fail'` and `template_missing: List[str]`. Extend `per_lint` counter with `template_v1_missing_<section-or-field>` tags.

### 4.5 Extend `render_gap_map_markdown` per-tool table

Add `Template` column between `Category` and `Lint`. Values: `✓` / `warn` / `✗`.

### 4.6 Extend `build_pa_tool_audit` gap-map summary

Add a section: `## Template compliance (T1b)` — counts of `pass` / `warn` / `fail` + list of `fail` docs (expected zero at T1b ship since no doc has `Template version: v1` yet; lint gate is live for the next sweep session's doc-author to opt into).

## 5. Ship shape

Single PR: doc + code. Contents:

1. `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` — canonical template file. Contains:
   - Header comment explaining ratchet-and-warn semantics + which variant to pick + presence-not-exact frontmatter rule
   - Sweep-variant skeleton with all mandatory + optional sections + inline comments
   - Protocol-variant skeleton with all mandatory + representative optional sections
   - Reference frontmatter block with all v1 required fields + the 2 new fields
2. Extensions to `core/services/pa_tools_gap_map.py` per §4 (including D-1 `_`-prefix filter + D-2 regex loosening).
3. Unit tests in `tests/services/test_pa_tools_gap_map.py` covering:
   - Legacy doc (no marker) → `warn`
   - v1 sweep doc with all sections → `pass`
   - v1 sweep doc missing `## Covered actions` → `fail` with `template_v1_missing_covered_actions`
   - v1 protocol doc with all sections → `pass`
   - `Template variant: xyz` (invalid) → `fail` with `template_variant_invalid`
   - `Template version: 1` (invalid) → `fail` with `template_version_invalid`
   - Required frontmatter field missing → `fail` with `template_v1_missing_frontmatter_<field>`
   - Extra frontmatter keys → still `pass` (presence-not-exact per ZO-Q9)
   - Regex: `## Covered actions` / `## 2. Covered actions` / `## 2) Covered actions` / `## 2 — Covered actions` all match
   - Regex: `## Actions covered` does NOT match (false-positive check)
   - `_TEMPLATE_per_tool_validation.md` excluded from `index_validation_docs`
   - Both variants pass lint when authored to spec (Rigby ZO-Q6 requirement)
4. Regenerate `docs/audits/PA_TOOLS_GAP_MAP.md` at ship to surface the new column (all 19 legacy docs show `warn`; T1b template file itself excluded).

## 6. What T1b explicitly does NOT ship

- **No bulk retrofit of 19 legacy docs.** They stay `warn` in the gap map until touched.
- **No prose-quality lint.** Only structural presence.
- **No auto-detection of variant.** Author declares in frontmatter.
- **No `pa_tool_scaffold_validation_doc` sub-command** (deferred per T1b thread doc §6 optional; would grow scope beyond MVP).
- **No frontmatter format enforcement on legacy docs** — legacy docs may have minor frontmatter shape variance; lint only checks required-field presence, not exact formatting.
- **No lint on the sub-set of "protocol-only" sections (§5-§20)** — protocol variant enforces the 6 mandatory sections in §2.3, not the full 20.
- **NEW (Rigby SIGN F edit): No normalization of protocol-variant frontmatter keys.** Protocol docs may keep their variant-specific keys (`Downstream service`, `Reviewer`, etc.). Lint enforces presence of the v1 required fields (with alias tolerance per §2.4), not exact key set.
- **NEW (Rigby SIGN F edit): No backfill of `Template version` across the corpus in this PR.** Ratchet stays opt-in per §3; escalation ladder is a forward-carry trigger per Rigby ZO-Q2, not same-PR work.

## 7. Close criteria for T1b (and by extension, this substrate arc)

Per arc parent §6 (all three must close):

- ✅ **T1c** shipped S2901 (Row 161 substrate arc parent §6.1).
- ✅ **T1a** shipped S2902 + S2903 (Row 161 substrate arc parent §6.2).
- **T1b ships when:**
  - Template file at path in §5.1 exists.
  - Lint extension in `pa_tools_gap_map.py` implemented per §4 (including D-1 `_` filter + D-2 regex loosen) + tested per §5.3.
  - Regenerated `PA_TOOLS_GAP_MAP.md` surfaces the Template column.
  - Rigby SIGN AGREE 4/4 on final PR shape.
  - Chris D-verdict on ship.
  - Forward-carry rows logged to Rigby Tool Gap Ledger: ZO-Q2 (warn-noise escalation ladder) + ZO-Q7 (automated corpus-counter script) + ZO-Q8 (structured-parse migration trigger).

## 8. Rigby SIGN T1 fold-log (S2904)

Rigby SIGN routed 2026-07-22 with tool-grounded verification (10 tool_runs: 4× repo_tool read_file for the 3 audit docs + 2 sample validation docs; 1× tree of validation dir; 2× search for `## Covered actions` + `## Verdict`; 1× read of `pa_tools_gap_map.py`).

**Same-PR mitigations folded (all shipped in this v2):**

- **§1 count correction** (Rigby SIGN A + DISAGREE on §1 corpus claim): 22 → 19 per-tool `*_tool_validation.md`; 17 sweep → 14 sweep; distinguish per-tool from adjacent + substrate docs.
- **§1 frontmatter reframe** (Rigby SIGN A edit): "shared frontmatter" is the v1 TARGET, not current state.
- **§2.4 exact accepted values** (Rigby SIGN B edit): `Template variant` regex + `Template version` regex both specified.
- **§2.4 presence-not-exact rule** (Rigby SIGN B edit + ZO-Q9): protocol docs may have extra keys.
- **§3 invalid-value row** (Rigby SIGN C edit): `Template version:` present but non-matching → fail.
- **§4.1 `_`-prefix filter** (Rigby SIGN D-1 blocking): explicit `not p.name.startswith('_')` filter.
- **§4.2 regex loosening** (Rigby SIGN D-2 blocking): accept optional numbering; add regression tests.
- **§5.3 test coverage** (Rigby SIGN E edit): both variants pass + false-positive rejected + numbered form accepted + `_`-file excluded.
- **§6 non-goals additions** (Rigby SIGN F edit): no protocol-frontmatter normalization + no `Template version` backfill.

**Forward-carry triggers (logged; NOT same-PR):**

- **ZO-Q2 warn-noise escalation ladder** — after 5+ sweep sessions with `warn` count stalled, escalate any TOUCHED legacy doc to require `Template version: v1` in same PR. Log to Rigby Tool Gap Ledger `future_trigger`.
- **ZO-Q7 automated corpus counter** — tiny script/helper prints sweep-vs-protocol split + missing-frontmatter counts + top-N offenders. §1 tallies then sourced from output, not eyeballed. Prevents future SIGN cycles from re-litigating counts. Log to Rigby Tool Gap Ledger `future_trigger`.
- **ZO-Q8 structured-parse migration** — if third variant or lint scope expansion happens, migrate from regex to frontmatter parser + markdown AST. Not for T1b. Log to Rigby Tool Gap Ledger `future_trigger`.
- **ZO-Q5 `v1` semantics** — Rigby suggested v1 semantics get pinned in same-PR template header comment; folded into §5.1 template file content.

**Rigby SIGN E test-requirement fold:** at least one test demonstrates a legacy doc remains `warn`-only but still indexes correctly (per Rigby ZO-Q6 same-PR requirement).

## 9. Convergence + Chris routing

Per `feedback_claude_rigby_agree_first_chris_yes_no`: Claude+Rigby converged on this v2 shape. Rigby recommendation: **approve T1b directionally + block merge until D-1 (`_`-filter) + D-2 (regex loosen) land in same PR**. Both are folded per §4.1 + §4.2 above.

**Routed to Chris for D-verdict.** Plain-English framing per `feedback_plain_english_decision_framing_for_chris`:

- **What ships:** the template file + lint extension + tests + regenerated gap map.
- **What Chris loses if he says no:** the sweep-arc close signal. Row 161 substrate arc stays open. The remaining ~76 sweep tools stay at ~4/session pace (not the ~10/session post-substrate pace).
- **More work later if approved as-is:** the 3 forward-carry triggers (ZO-Q2/Q7/Q8) become future backlog items — but they are backlog, not blocking work. None require immediate follow-up.
- **What Chris loses if he approves:** nothing operationally; every existing validation doc continues to work unchanged (all show `warn` in the new column).
