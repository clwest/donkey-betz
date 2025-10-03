# Documentation Reorganization Plan

## 🎯 Goals
1. **Preserve Agent Workflow**: Keep session handoffs easily accessible
2. **Maintain Context**: Ensure agents can find previous work
3. **Improve Organization**: Better structure without breaking existing patterns
4. **Clear Navigation**: Easy to find any document

## 📁 New Structure

### /documentation/active-session/
**Purpose**: Current active work area (replaces complete-system-review)
```
active-session/
├── CURRENT_SESSION.md -> SESSION_188_HANDOFF.md (symlink)
├── SESSION_188_HANDOFF.md
├── SESSION_188_AUTH_FIX_COMPLETE.md
├── SESSION_187_HANDOFF.md
├── SESSION_187_FRONTEND_FIXES.md
├── ... (last 10 sessions for context)
└── README.md (explains session workflow)
```

### /documentation/session-archive/
**Purpose**: Historical sessions (150+ files)
```
session-archive/
├── sessions-180-189/
│   └── (recent completed sessions)
├── sessions-170-179/
├── sessions-160-169/
├── sessions-150-159/
├── sessions-140-149/
└── older/ (sessions 1-139)
```

### /documentation/system-guides/
**Purpose**: Complete system documentation (was scattered)
```
system-guides/
├── ai-assistant/
│   ├── MAIN_AI_ASSISTANT_COMPLETE_GUIDE.md
│   └── README.md
├── memory-system/
│   ├── MEMORY_SYSTEM_COMPLETE_GUIDE.md
│   └── README.md
├── agent-orchestra/
│   ├── MULTI_AGENT_SYSTEM_COMPLETE_GUIDE.md
│   └── README.md
├── mythology/
│   ├── MYTHOLOGY_SYSTEM_COMPLETE_GUIDE.md
│   └── README.md
├── prompting/
│   ├── PROMPTING_SYSTEM_COMPLETE_GUIDE.md
│   └── README.md
├── ai-insights/
│   ├── AI_INSIGHTS_SYSTEM_COMPLETE_GUIDE.md
│   └── README.md
├── ai-learning/
│   ├── AI_LEARNING_SYSTEM_COMPLETE_GUIDE.md
│   └── README.md
├── content-studio/
│   ├── CONTENT_STUDIO_SYSTEM_COMPLETE_GUIDE.md
│   └── README.md
└── universal-builder/
    ├── UNIVERSAL_BUILDER_SYSTEM_COMPLETE_GUIDE.md
    └── README.md
```

### /documentation/audits-reports/
**Purpose**: All audit and analysis documents
```
audits-reports/
├── system-audits/
│   ├── AUDIT_REPORT.md
│   ├── REALITY_CHECK_REPORT.md
│   └── AGENT_TOOLS_DEEP_DIVE.md
├── database/
│   ├── DATABASE_RESTORATION_COMPLETE.md
│   └── (other DB reports)
└── fixes/
    ├── FIX_IMPLEMENTATION_PLAN.md
    └── CODE_CHANGES.md
```

## 🔄 Migration Strategy

### Phase 1: Create New Structure (No Deletions)
1. Create new directories
2. Copy (not move) key files
3. Create symlinks for active work

### Phase 2: Update References
1. Update CLAUDE.md to point to new locations
2. Create redirect READMEs in old locations
3. Test agent workflow with new structure

### Phase 3: Clean Up (After Verification)
1. Archive old directories
2. Remove duplicates
3. Update documentation

## 🚦 Agent Workflow Preservation

### For New Sessions:
```bash
# Agent starts new session
cd /documentation/active-session/
# Read CURRENT_SESSION.md (always points to latest)
# Create SESSION_189_HANDOFF.md
# Update CURRENT_SESSION.md symlink
```

### For Context:
- Last 10 sessions always in active-session/
- Older sessions in organized archive
- System guides in predictable locations

## ✅ Benefits
1. **Single entry point**: active-session/CURRENT_SESSION.md
2. **Clear history**: Numbered archive folders
3. **System docs organized**: By system, not scattered
4. **No broken workflows**: Symlinks and redirects preserve paths

## 🎯 Next Steps
1. Create directory structure
2. Move SESSION_188 files to active-session/
3. Create CURRENT_SESSION.md symlink
4. Move system guides to system-guides/
5. Archive older sessions
6. Update CLAUDE.md references