# Active Session Directory

## 🎯 Purpose
This is the **primary working directory** for current AI agent sessions. All active work happens here.

## 📋 Quick Start for Agents

### Starting a New Session:
1. Read `CURRENT_SESSION.md` (symlink to latest handoff)
2. Complete tasks listed in the handoff
3. Create `SESSION_[NUMBER]_HANDOFF.md` when done
4. Update `CURRENT_SESSION.md` symlink to point to your handoff

### Finding Context:
- **Last 10 sessions**: Available in this directory
- **Older sessions**: Check `/session-archive/`
- **System documentation**: See `/system-guides/`

## 📁 File Structure
```
CURRENT_SESSION.md     → Always points to latest handoff (symlink)
SESSION_188_HANDOFF.md → Most recent completed handoff
SESSION_187_HANDOFF.md → Previous session
...                    → Last ~10 sessions for context
```

## 🔄 Workflow Example
```bash
# Agent reads current state
cat CURRENT_SESSION.md

# Agent works on tasks...

# Agent creates handoff
vim SESSION_189_HANDOFF.md

# Update symlink for next agent
ln -sf SESSION_189_HANDOFF.md CURRENT_SESSION.md
```

## 📚 Related Documentation
- **System Guides**: `/documentation/system-guides/`
- **Session Archive**: `/documentation/session-archive/`
- **Audit Reports**: `/documentation/audits-reports/`

## ⚡ Key Files Always Here
- Current session handoff
- Recent session handoffs (context)
- Any active work files
- Fix implementation tracking

---
*This directory replaced `/complete-system-review/` for better organization*