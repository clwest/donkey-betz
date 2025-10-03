# Documentation Governance

**Created**: August 8, 2025 | **Session**: 91  
**Status**: OFFICIAL POLICY

## Single Source of Truth

### `/documentation/` is the ONLY Official Documentation

All project documentation MUST be maintained in the `/documentation/` directory structure. This is the single source of truth for the entire project.

## Documentation Structure

```
/documentation/
├── 00-overview/           # System overview & governance
├── 01-architecture/        # Technical architecture
├── 02-core-systems/        # Core system documentation
├── 03-integrations/        # External integrations
├── 04-development/         # Development guides
├── 05-operations/          # Operations & monitoring
├── 06-implementation-logs/ # Implementation records
├── 07-session-history/     # Session tracking
├── 08-planning/            # Future planning
├── 09-reference/           # Reference materials
└── 10-ai-agent-integration/ # Current AI work
```

## Other Documentation Locations

### Allowed Exceptions
These locations may contain documentation for specific purposes:

1. **Root Level Files** (temporary/operational):
   - `CLAUDE.md` - Active session instructions
   - `README.md` - Project entry point
   - `CONSOLIDATION_PLAN.md` - Current consolidation effort
   - `*.md` reports - Temporary analysis reports

2. **Prompt Sets** (`/backend/prompt_sets/prompts/`):
   - AI system prompts and templates
   - Not project documentation - these are DATA

3. **Archive** (`/archive/`):
   - Historical/deprecated documentation
   - Not for active reference

### Not Allowed
- Documentation in code directories (except inline code comments)
- Duplicate documentation across multiple locations
- Wiki-style documentation outside `/documentation/`
- Personal notes or drafts in the main codebase

## Documentation Rules

1. **All new documentation** → `/documentation/` only
2. **Updates to existing docs** → Update in `/documentation/`
3. **Found docs elsewhere** → Migrate to `/documentation/` or delete
4. **Session handoffs** → `/documentation/07-session-history/`
5. **Implementation details** → `/documentation/06-implementation-logs/`

## Migration Policy

When consolidating or cleaning up:
1. Check if content exists in `/documentation/`
2. If yes → Delete the duplicate
3. If no → Move to appropriate `/documentation/` subdirectory
4. Update all references to point to new location

## Enforcement

- All AI assistants should enforce this policy
- Code reviews should reject PRs with documentation outside `/documentation/`
- Regular audits to ensure compliance

## Quick Reference

| Content Type | Location |
|-------------|----------|
| API Documentation | `/documentation/03-integrations/` |
| System Architecture | `/documentation/01-architecture/` |
| Development Guides | `/documentation/04-development/` |
| Session Notes | `/documentation/07-session-history/` |
| Memory/AI Systems | `/documentation/02-core-systems/` |
| Future Plans | `/documentation/08-planning/` |
| Current AI Work | `/documentation/10-ai-agent-integration/` |

---
*This policy is effective immediately and supersedes any previous documentation practices.*