<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.
> **Note:** content may be stale (last refreshed Session 814) — this file is **runtime-load-bearing**: `core/services/docs_context_builder.py:186` reads from it. Do NOT move; refresh-in-place when content drifts.

# Canon Index

**Status:** ACTIVE | **Last Updated:** Session 814

---

## What Is Canon?

Canon documents are **locked, authoritative knowledge** that:
- Have been reviewed and approved by System Owner
- Are factually accurate and production-tested
- Are fed to all agents as baseline knowledge
- Cannot be edited without formal review

---

## Promotion Criteria

To be promoted to canon, a document must:

1. **Expert-level quality** - Could be sold or published
2. **Factually accurate** - Verified information
3. **Production-tested** - Used in real work
4. **Practically useful** - Solves real problems
5. **System Owner approved** - Chris says "yes"

---

## Canon Registry

### Technical Canon (`/canon/technical/`)

| Document | Topic | Promoted | Session |
|----------|-------|----------|---------|
| *None yet* | | | |

### Operational Canon (`/canon/operational/`)

| Document | Topic | Promoted | Session |
|----------|-------|----------|---------|
| *None yet* | | | |

### Creative Canon (`/canon/creative/`)

| Document | Topic | Promoted | Session |
|----------|-------|----------|---------|
| `DAVINCI_RESOLVE_WORKFLOW.md` | YouTube video production | 2026-01-24 | 814 |

---

## Pending Review

Documents awaiting canon promotion:

| Document | Location | Nominated By | Status |
|----------|----------|--------------|--------|
| Stage 2 Governance Plan | governance/stage-2/ | TechnicalDocumentAgent | Pending |
| Stage 3 Evaluation Protocol | governance/stage-3/ | TechnicalDocumentAgent | Pending |

---

## How To Nominate

1. Document must exist in `/docs/` (any location)
2. Add entry to "Pending Review" section above
3. System Owner reviews and approves/rejects
4. If approved: move to appropriate canon folder, update registry

---

## Usage

Canon documents are:
- **Priority 1** in DocsContextBuilder (injected first)
- **Referenced** by agents when relevant
- **Protected** from accidental modification
- **Versioned** if updates are needed (canon-v2, etc.)

---

*Registry maintained by: System Owner*
*Auto-indexed by: build_docs_index command*
