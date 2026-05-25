# Letter to Future Claude Code

**Written:** January 19, 2026 (Session 779)
**Updated:** January 20, 2026 (Session 784) - Added build_docs_index command
**From:** Claude Code (Opus 4.5)
**To:** Future Claude Code Sessions

---

## Welcome, Future Self

You're about to work on the **Unified Donkey Betz** platform - a sophisticated AI content studio with 74 agents, 77 spiders, 9 body systems, and deep integration across every component. This letter will help you understand the system quickly.

---

## First Steps - ALWAYS Do These

```bash
# 1. Read the session handoff FIRST
cat 00-START-NEXT-SESSION.md

# 2. Check CLAUDE.md for system overview
# (It's pre-loaded in your context, but read it if you need details)

# 3. Start the platform
make start
make celery

# 4. Access the UI
open http://localhost:8000/ai-studio/
```

---

## Understanding the Architecture

### The Body Metaphor

This system uses a **biological body metaphor** for its architecture:

| Body System | Purpose | Key File |
|-------------|---------|----------|
| **HEART** | Central health monitoring | `core/services/heart.py` |
| **LUNGS** | Resource & capacity management | `core/services/lungs.py` |
| **BRAIN** | Cognitive processing (LLM calls) | `core/services/brain.py` |
| **SPINE** | Central API routing | `core/services/spine.py` |
| **CIRCULATORY** | Data flow monitoring | `core/services/circulatory.py` |
| **DIGESTIVE** | Data ingestion & processing | `core/services/digestive.py` |
| **MUSCULAR** | Agent work execution | `core/services/muscular.py` |
| **IMMUNE** | Security & threat detection | `core/services/immune.py` |
| **SKIN** | Workspace output (agent file writes) | `core/services/skin.py` |

### Agent Ecosystem (74 Agents)

All agents live in `core/agents/`. They:
- Inherit from `BaseAgent`
- Have isolated tools
- Record decisions via TimeTravelMixin
- Receive spider context automatically
- Can write to workspaces via SKIN Layer

### Spider Network (77 Spiders)

Spiders in `ai_core/spiders/` fetch real data from external sources:
- News, financial, tech, legal, etc.
- Methods: REST API, RSS, Web Scraping
- Data flows to agents via `spider_context_builder.py`

---

## Key Patterns to Know

### 1. Agent Execution Flow
```
User Request → PersonalAssistantAgent → AgentRouter → Specialized Agent → Tools → Output
                                                          ↓
                                              SKIN Layer (file writes)
                                                          ↓
                                              WorkspaceOperation (audit trail)
```

### 2. Learning System
```
Agent Execution → AgentMemory (with safety_class) → Embedding (if approved) → Collective Intelligence
```

**Memory Safety Classes:**
- `test_only` - Never embed
- `exploratory` - Low priority
- `candidate` - Pending review
- `approved` - Embedded into knowledge

### 3. Integration Pipeline (5 Phases)
```
1. Celery Health → monitors task execution
2. Spider Context → agents receive trend data
3. Learning Patterns → historical success patterns
4. Advisor Wisdom → guidance from 25 advisors
5. Feedback Loops → performance tracking
```

---

## Common Tasks

### Running an Agent
```python
from core.tasks import universal_agent_workspace_output
result = universal_agent_workspace_output('AgentName', 'task description')
```

### Checking Agent Status
```bash
.venv/bin/python manage.py shell -c "
from core.agents import list_agents
print(list_agents())
"
```

### Viewing Workspace Outputs
Visit: `http://localhost:8000/ai-studio/workspace`
- Click "View Content" on any operation to see the file

### Triggering Category Rotation
```python
from core.tasks import agent_category_rotation
agent_category_rotation('research')  # or: financial, blockchain, etc.
```

---

## Documentation Structure

| Path | What's There |
|------|--------------|
| `00-START-NEXT-SESSION.md` | **START HERE** - Current session priorities |
| `CLAUDE.md` | System overview, stats, architecture |
| `docs/` | Centralized documentation |
| `docs/INDEX.md` | **Auto-generated** documentation map (1,500+ files indexed) |
| `docs/handoffs/` | 446+ session handoff documents |
| `docs/audits/` | System audit reports |
| `docs/designs/` | Design documents |
| `docs/MEMORY_SAFETY_CLASSIFICATION.md` | Memory safety system |
| `docs/DATABASE_MODEL_REFERENCE.md` | Which DB table for what |

### Regenerating Documentation Index

**IMPORTANT:** After creating or modifying ANY documentation, regenerate the index:

```bash
python manage.py build_docs_index
```

This keeps `docs/INDEX.md` current with file counts, recent sessions, and modification times.

### Agent Workspace Outputs (SKIN Layer)

These directories contain agent-generated files - they're NOT documentation:
- `research/`, `analysis/`, `financial/`, `narrative/`
- `podcast/`, `blockchain/`, `security/`, `development/`
- `content/`, `campaigns/`, `workflows/`, `system/`

---

## GPT-5-mini Warning

If using GPT-5-mini (reasoning model), remember:
```python
# CORRECT
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=messages,
    max_completion_tokens=6000  # NOT max_tokens
    # NO temperature parameter!
)
```

---

## Troubleshooting

### Full Restart
```bash
pkill -f daphne; pkill -f redis; pkill -f celery
rm -f .daphne.pid .celery.pid .celery-beat.pid
make start && make celery
```

### Celery Crashes (macOS)
```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES celery -A core worker -l INFO --pool=solo
```

### Health Check
```bash
curl http://localhost:8000/health/ping/
```

---

## Philosophy & Principles

1. **Read First, Code Second** - Always understand existing code before modifying
2. **Avoid Over-Engineering** - Only add what's explicitly needed
3. **Keep Documentation Updated** - Update handoffs after each session
4. **Use Existing Patterns** - Follow established conventions
5. **Test Before Committing** - Verify changes work
6. **Trust the System** - The integration is verified working (95% score)

---

## Session Numbering

Sessions are numbered sequentially (currently at 784+). Each session should:
1. Read `00-START-NEXT-SESSION.md`
2. Complete the suggested tasks
3. Create a handoff document in `docs/handoffs/`
4. Update `00-START-NEXT-SESSION.md` for the next session
5. **Regenerate docs index:** `python manage.py build_docs_index`
6. Commit with `Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`

---

## Final Advice

The system is **mature and well-integrated**. Most features work. The main work now is:
- UI polish and data display improvements
- Testing edge cases
- Running and monitoring agents
- Responding to user requests

Don't try to "fix" things that aren't broken. The 74 agents, 77 spiders, 9 body systems, and 14 sci-fi features all work together. Trust the architecture.

Good luck, future self!

---

*Written with appreciation for the human who built this with us over 784+ sessions.*
