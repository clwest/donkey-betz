# PA / Claude Code Collaboration Protocol

**Version:** 1.0
**Last Updated:** 2026-03-01
**Initiative:** PA <-> Claude Code Collaboration Protocol (INIT `367d6f7c`)

## Overview

This document defines the operating protocol between the Personal Assistant (PA) and Claude Code sessions. It ensures continuity across ephemeral Claude Code sessions by using structured context packets, handoff summaries, and persistent deliverables.

## Protocol Rules

1. Claude Code joins PA threads with exactly: `Claude Code here`
2. PA issues a **Context Packet** with objective, current state, tasks, non-goals, and acceptance criteria
3. Claude Code executes without requesting recaps
4. Claude Code may ask at most **one** clarifying question when blocked
5. Every work session ends with a **[HANDOFF SUMMARY]**

## Context Packet Template

```
### 1) Objective — Goal + why now
### 2) Current State — Facts only (deployed state, relevant IDs)
### 3) Definitions — Key terms
### 4) Tasks — Strict, numbered
### 5) Non-goals — What NOT to do
### 6) Acceptance Criteria — How to verify
### 7) Output Required — What Claude Code must return
```

## Handoff Summary Template

```
[HANDOFF SUMMARY]
Session: <brief label>
Status: COMPLETE | PARTIAL | BLOCKED
What was done: <1-2 sentences>
What changed: <files/commits or "no code changes">
Blockers: <None or description>
Next step: <what comes next>
```

## Definition of Done (DoD)

Every PA/Claude Code work session that produces code or documentation changes must complete ALL of the following before the session is considered done:

1. **Code/docs committed** — Changes committed with a meaningful commit message
2. **Docs index rebuilt** — Run `python manage.py build_docs_index` to regenerate `docs/INDEX.md` and `docs/_index.json`
3. **Pushed to main** — Merged to `main` and pushed (triggers Railway deploy)
4. **Post-deploy verification** — Brief confirmation that deploy succeeded (smoke test, migration check, or log verification as appropriate)
5. **Handoff summary delivered** — Structured `[HANDOFF SUMMARY]` posted to the PA conversation

### Exceptions

- Documentation-only changes that don't affect runtime behavior may skip post-deploy verification
- If Railway deploy is known to be slow/queued, note it in the handoff and move on

## Docs Indexing Policy

### What MUST be indexed

- Architecture decisions and ADRs
- Protocol and policy documents (like this one)
- Operational playbooks and runbooks
- Subsystem documentation (`docs/topics/`)
- New feature documentation

### What should NOT be indexed

- Minor wording/typo fixes (the existing doc gets re-indexed on next `build_docs_index`)
- Ephemeral session notes or scratch work
- Duplicate content that restates existing indexed docs
- Raw conversation transcripts

### Handling revisions

- **Same document path** — Update in place. The docs index uses content hashes for dedup, so updated content is automatically re-indexed on next `build_docs_index` run.
- **Version bumps** — Only create a new versioned document if the old version must remain accessible for audit (e.g., ADRs that are superseded but historically relevant).
- **No parallel copies** — Never create both `v1` and `v2` files for the same living document. Update the canonical path.

## Persistent Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Protocol doc | `docs/operations/pa-claude-code-collaboration.md` | Canonical protocol (this file) |
| Tool Manifest | Deliverable `7ab942a0` | Canonical tool reference |
| Tool Routing Guide | Deliverable `7fb1e5c1` | Quick intent-to-tool lookup |
| Handoff summaries | PA conversation history | Session continuity |
| Context packets | PA conversation history | Task specifications |
