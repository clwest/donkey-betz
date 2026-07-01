---
title: "S1301 Follow-up — build_docs_provenance classifier weights body-match over subject-tag (search_docs filter hazard)"
status: draft
authority: research
session_added: 1301
research_group: 1300
child_slot: P1-followup
domain_slug: memory
date: 2026-07-01
last_verified: 2026-07-01
supersedes: none
related:
  - docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md   # parent audit — this note follows up
  - docs/research/domains/memory/1300_memory_domain_scoping.md               # research group parent
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                # process
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
verifier_loop: |
  v1 (2026-07-01, S1301 close +cascade run): follow-up finding surfaced by
  running the 4-step docs cascade + build_docs_provenance on local after
  S1301 audit merged to main as b54b2409. The cascade rebuilt
  `docs/_provenance.json` (2240 docs; +84 vs 2026-06-23; HIGH 1430 /
  MEDIUM 346 / LOW 0 / UNKNOWN 464). The S1301 audit itself was among
  the +84 new docs — but the classifier assigned it `originating_session:
  1275` (MEDIUM confidence, match_source: body) instead of the correct
  1301 (HIGH confidence, subject-tag). Direct read of `docs/_provenance.json`
  entry for the audit confirms the misclassification. This note is a
  self-contained bug report — the S1301 audit itself was already merged
  to main and is NOT modified. Follow-up PR captures the finding so
  future arcs (Group 1700 Observability or S1302 Memory Persistence)
  can pick it up.
owner: claude (drafted S1301 close +cascade)
---

# S1301 Follow-up — Provenance Classifier Precedence Bug

> **What this is.** A self-contained bug note surfaced during the
> local 4-step docs cascade run at S1301 close (2026-07-01, after
> merge `b54b2409` on main). Not modifying the merged S1301 audit
> (1154 lines, `1301_memory_rag_retrieval_lanes_audit.md`). Not a
> full audit. Not a fix proposal. Just a crisp, reproducible bug
> report so future arcs can pick it up.
>
> **Where it belongs in the arc.** Category D follow-up (child slot
> P1-followup). The S1301 audit already characterized the silent-
> failure class (§14.2) and the corpus-completeness gap (§14.1);
> this note names a related-but-distinct classifier-precedence bug
> that produces the same silent-failure surface.

---

## 1. Finding

**`build_docs_provenance` misclassifies at least one document by
weighting body-mention over subject-tag when both signals exist.**

Concrete instance: the S1301 audit `1301_memory_rag_retrieval_lanes_audit.md`
lands in `docs/_provenance.json` with:

```json
{
  "originating_session": 1275,
  "confidence": "MEDIUM",
  "match_source": "body",
  "first_commit_sha": "b54b2409",
  "first_commit_date": "2026-07-01",
  "first_commit_subject": "docs(session-1301): Memory RAG Retrieval Lanes audit + INDEX v13 (#2775)",
  "sessions_touched": [1275, 1276, 1300, 1301],
  "commit_count": 2,
  "prs": [2775]
}
```

### Expected vs actual

| Field | Expected | Actual | Delta |
|-------|----------|--------|-------|
| `originating_session` | 1301 | 1275 | ⚠️ misclassified |
| `confidence` | HIGH | MEDIUM | ⚠️ tier dropped |
| `match_source` | `subject` | `body` | ⚠️ precedence inverted |
| `sessions_touched` | includes 1301 | includes 1301 | ✅ correct |
| `first_commit_subject` | contains "session-1301" | contains "session-1301" | ✅ correct signal present |
| `prs` | [2775] | [2775] | ✅ correct |

The subject-tag signal (`docs(session-1301):`) is unambiguous and
present in the commit's actual subject line. It should have won.

---

## 2. Root cause hypothesis

The audit doc's body extensively cites `S1275`, `S1276`, `S1300`,
`S1302`, and `S1304` (Playbook v2, Research OS, Group 1300 parent
scoping, downstream child audits). These are all natural references
for a S1301 child audit — parent + peers + siblings.

**Hypothesis:** `build_docs_provenance`'s classifier weighs
body-mention count / recency above the commit-subject-tag signal.
When body citations outnumber the subject signal, the body wins.

The S1301 audit body mentions "1275" enough times that the
classifier concluded "this doc is about S1275" — even though the
subject unambiguously says "session-1301."

**Correct precedence order (per the semantic role of each signal):**

1. **Subject-tag `docs(session-NNNN):`** — the author's explicit
   declaration of what session the doc belongs to. Should be
   authoritative when present.
2. **YAML frontmatter `session:` or `session_added:`** — the doc's
   own self-declaration in structured form.
3. **Body mentions** — tie-breaker only, and never able to override
   a subject-tag signal.

Current precedence appears to be: body wins over subject when body
has more matches. That's inverted.

**Evidence for the ordering hypothesis:** Grep confirms the audit
body has multiple `S1275` and `S1276` mentions (natural cross-refs
for a Category D audit under the Memory arc). The classifier's
`match_source: "body"` field on the entry names body as the winning
signal source. The `sessions_touched` array correctly captures the
session set (including 1301) — showing the classifier *did* see the
subject-tag signal but did not weight it as primary.

---

## 3. Impact

**Same silent-failure surface the S1301 audit characterized
(§14.2), now producing a fresh instance.**

If a caller invokes `search_docs originating_session=1301` (a
natural query — "find chunks from the session that shipped the RAG
Retrieval Lanes audit"), the S1301 audit chunks land in
`_filter_chunks_by_originating_session`'s `excluded_mismatch`
counter because `meta.originating_session == 1275 != 1301`.

**The audit doc disappears from its own session's provenance
query.** The caller sees `result_count: 0` with a `filter` block
showing `excluded_mismatch: N` and has no observable signal that
the classifier is at fault (vs. the corpus genuinely not having
matching material). This is the exact "counters buried in payload,
no log/metric/alert" class §14.2 already flagged.

**Scope of impact:**
- 1 confirmed misclassified document (the S1301 audit itself).
- Unknown number of additional misclassified documents. A full
  audit would enumerate: any doc whose body cites older sessions
  heavily (research library docs are structurally prone to this).
- Category-wide risk: research docs under `docs/research/domains/`
  are especially exposed because they cite parent + peer sessions
  extensively by convention.

**NOT impact:**
- The 464 UNKNOWN entries in the provenance index (S1301 §14.1
  finding) are a distinct class — those are docs where the
  classifier found *no* session signal at all. This bug is about
  docs where signal exists but precedence is wrong.

---

## 4. Reproduction

```bash
# Rebuild provenance from git history (last run: 2026-07-01 at S1301 close)
python manage.py build_docs_provenance

# Inspect the S1301 audit entry
python3 -c "
import json
d = json.load(open('docs/_provenance.json'))['docs']
entry = d.get('docs/research/domains/memory/1301_memory_rag_retrieval_lanes_audit.md')
print(json.dumps(entry, indent=2))
"

# Expected in an ideal world:
#   originating_session: 1301
#   confidence: HIGH
#   match_source: subject
# Actual as of 2026-07-01:
#   originating_session: 1275
#   confidence: MEDIUM
#   match_source: body
```

---

## 5. Recommended remediation direction

**Do not implement here.** Playbook §14.5 forbids implementation
in research. Naming the direction so a future PR can pick it up:

1. **Read `core/management/commands/build_docs_provenance.py`
   heuristic ordering.** Confirm subject-tag is not evaluated as
   the primary signal, and identify where the body-match count
   currently overrides.
2. **Invert precedence.** Subject-tag wins outright when present.
   Frontmatter `session:` wins next. Body-mention is a
   tie-breaker only (used when neither subject-tag nor frontmatter
   provides a signal).
3. **Preserve `sessions_touched`.** The array field is correct
   as-is — the fix is about primary-session assignment, not about
   dropping the body-mention information.
4. **Add classifier drift detection.** After the fix, re-run
   `build_docs_provenance` and compare the diff of `originating_session`
   assignments against the pre-fix state. Docs that flip from
   body-match to subject-tag are the affected set.
5. **Post-fix verification.** Re-query for the S1301 audit entry;
   expect `originating_session: 1301`, `confidence: HIGH`,
   `match_source: subject`.

---

## 6. Cross-arc routing

**Not S1302's problem.** S1302 (Memory Persistence Architecture,
Categories A + B + C) inherits the row-level provenance-semantics
question from S1301 §14.3 D3. This classifier bug is a separate
concern about the *external* provenance index's build heuristic —
not about the row-level persistence question.

**Candidate owners:**
- **Group 1700 (Observability / Telemetry / SLOs)** — if grouped
  with the S1301 §14.2 silent-failure surfacing work, since both
  are about "the platform silently drops results and doesn't tell
  the operator."
- **Category E (Docs Corpus Governance)** if S1304 Docs Corpus ↔
  RAG Boundary audit finds the classifier belongs in that domain.
- **Standalone `build_docs_provenance` bugfix PR** — smallest
  scope; the classifier is a bounded command. Doesn't need a full
  research arc.

**Recommendation:** standalone bugfix PR when someone has time.
This does not need to block Group 1300 or Group 1700 arcs.

---

## 7. Appendix — provenance index totals at S1301 close

Direct read of `docs/_provenance.json` `_meta` block after cascade
run 2026-07-01:

```json
{
  "generated": "<timestamp>",
  "command": "python manage.py build_docs_provenance",
  "git_head": "<sha>",
  "doc_count": 2240,
  "commit_count": 7461,
  "confidence_breakdown": {
    "HIGH": 1430,
    "MEDIUM": 346,
    "LOW": 0,
    "UNKNOWN": 464
  },
  "excludes": [
    "docs/archive/",
    "docs/docs-pattern/"
  ],
  "schema_version": 1
}
```

- **+84 docs** vs the pre-S1301 state (was 2156, now 2240).
- **UNKNOWN count unchanged** at 464 (was 464, now 464). New docs
  shipping with session-tagged commits keep UNKNOWN flat while total
  grows — S1301 §14.1's 21.5% gap improved to 20.7% as a ratio, but
  the absolute count of "docs with no session signal" is stable.
- **This bug is separate** from the UNKNOWN gap. A misclassified
  doc (like this audit) does NOT show up in UNKNOWN — it lands in
  HIGH/MEDIUM/LOW under the wrong session ID, which is arguably
  worse than UNKNOWN because it produces false-positive session
  matches for the wrong session and false-negative for the correct
  one.
