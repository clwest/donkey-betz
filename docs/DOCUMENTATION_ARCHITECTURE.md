# Documentation Architecture

**Session 814** | System Knowledge Base Design

This document defines how `/docs/` serves as the system's institutional knowledge - the "brain" that agents learn from and contribute to.

---

## Philosophy

> "The system should feel like having a competent team, not a bureaucracy."

Documentation is not just reference material. It's:
- **Institutional memory** - What the system knows
- **Operational playbooks** - How to do things well
- **Canon knowledge** - Locked truths that anchor all agents
- **Mission alignment** - What we're trying to achieve

---

## Directory Structure

```
/docs/
├── 00-START-HERE/          # Onboarding for new sessions
├── INDEX.md                # Auto-generated master index
│
├── ══════════════════════════════════════════════════════
├── CORE KNOWLEDGE (Reference)
├── ══════════════════════════════════════════════════════
├── architecture/           # System design docs
├── agents/                 # Agent documentation
├── apis/                   # API specifications
├── body/                   # Body system docs (HEART, LUNGS, etc.)
├── features/               # Feature specifications
├── integrations/           # External service integrations
│
├── ══════════════════════════════════════════════════════
├── OPERATIONAL (How We Work)
├── ══════════════════════════════════════════════════════
├── guides/                 # How-to guides
├── workflows/              # Step-by-step workflows
├── playbooks/              # ⭐ NEW: Gold standard operational docs
│   ├── creator/            # Content creator playbooks
│   ├── devops/             # DevOps & deployment playbooks
│   ├── marketing/          # Marketing & growth playbooks
│   └── development/        # Software development playbooks
│
├── ══════════════════════════════════════════════════════
├── GOVERNANCE (Authority & Control)
├── ══════════════════════════════════════════════════════
├── governance/             # ⭐ NEW: Governance framework
│   ├── SYSTEM_OWNER.md     # Chris = final authority
│   ├── EMERGENCY_PROCEDURES.md
│   ├── stage-1/            # Research briefs
│   ├── stage-2/            # Prototype plans
│   ├── stage-3/            # Evaluation protocols
│   ├── stage-4/            # Technical designs
│   └── stage-5/            # Post-mortems
│
├── ══════════════════════════════════════════════════════
├── STRATEGIC (Where We're Going)
├── ══════════════════════════════════════════════════════
├── missions/               # ⭐ NEW: Active missions/goals
│   ├── CURRENT_MISSION.md  # What agents should focus on
│   ├── Q1_2026.md          # Quarterly objectives
│   └── archive/            # Completed missions
├── roadmaps/               # Long-term planning
├── plans/                  # Implementation plans
│
├── ══════════════════════════════════════════════════════
├── CANON (Locked Authoritative Knowledge)
├── ══════════════════════════════════════════════════════
├── canon/                  # ⭐ NEW: Promoted "gold standard" docs
│   ├── INDEX.md            # Canon registry
│   ├── technical/          # Technical canon
│   ├── operational/        # Operational canon
│   └── creative/           # Creative canon (like DAVINCI_RESOLVE.md)
│
├── ══════════════════════════════════════════════════════
├── RECORD KEEPING (History)
├── ══════════════════════════════════════════════════════
├── handoffs/               # Session handoff documents (464 files)
├── audits/                 # System audits (58 files)
├── reports/                # Status reports (31 files)
├── designs/                # Design documents
│
├── ══════════════════════════════════════════════════════
├── MAINTENANCE
├── ══════════════════════════════════════════════════════
├── archive/                # Superseded/old docs
├── BUGS/                   # Bug tracking
├── code-review/            # Code review outputs
└── pre-launch/             # Pre-launch checklists
```

---

## New Directories Explained

### `/docs/playbooks/` - Gold Standard Operations

Playbooks are **expert-level operational guides** that agents can reference and learn from.

**Criteria for playbooks:**
- Production-ready (not experimental)
- Platform-specific and practical
- Includes real-world defaults and gotchas
- Written for practitioners, not beginners

**Example:** The DaVinci Resolve workflow doc is playbook-worthy.

### `/docs/governance/` - Authority Framework

Governance docs establish **who controls what** and **how decisions are made**.

**Contents:**
- `SYSTEM_OWNER.md` - Chris's authority, override procedures
- `EMERGENCY_PROCEDURES.md` - Kill switches, rollback procedures
- Stage folders (1-5) for the research-to-production pipeline

### `/docs/missions/` - Focus Alignment

Missions tell agents **what to focus on**. Without missions, agents wander.

**Contents:**
- `CURRENT_MISSION.md` - Active focus (injected into all agent prompts)
- Quarterly/monthly goal docs
- Archive of completed missions

### `/docs/canon/` - Locked Truth

Canon docs are **locked, indexed, and fed to all agents as baseline knowledge**.

**Promotion criteria:**
- Expert-level quality
- Factually accurate
- Production-tested
- Approved by System Owner

**Once promoted to canon:**
- Document is locked (no edits without review)
- Indexed in `canon/INDEX.md`
- Prioritized in DocsContextBuilder
- Used as baseline for future agent outputs

---

## How Agents Use Documentation

### Reading (DocsContextBuilder)

```python
# DocsContextBuilder priority order:
1. governance/SYSTEM_OWNER.md     # Always injected
2. missions/CURRENT_MISSION.md    # Always injected
3. canon/*                        # High priority
4. playbooks/* relevant to task   # Task-specific
5. Other docs by relevance        # Standard lookup
```

### Writing (Agent Outputs)

Agents can generate docs, but promotion requires human approval:

```
Agent Output → Review → Approve → Promote to Canon
                  ↓
               Reject → Archive or Delete
```

---

## Maintenance Commands

```bash
# Regenerate master index after changes
python manage.py build_docs_index

# Verify canon integrity
python manage.py verify_canon

# Archive old docs (>90 days, not canon)
python manage.py archive_stale_docs
```

---

## Document Lifecycle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Draft     │ ──▶ │   Active    │ ──▶ │   Canon     │
│  (working)  │     │  (in use)   │     │  (locked)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Rejected   │     │ Superseded  │     │  Archived   │
│  (deleted)  │     │ (archived)  │     │ (preserved) │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## Integration Points

| System | How It Uses Docs |
|--------|------------------|
| **DocsContextBuilder** | Injects relevant docs into agent prompts |
| **TechnicalDocumentAgent** | Generates governance stage docs |
| **ContentWriterAgent** | References playbooks for quality |
| **build_docs_index** | Maintains INDEX.md with cross-references |
| **Human Interface** | DocsIndexPage browses documentation |

---

*Document created: Session 814*
*Status: Active*
*Classification: Internal*
