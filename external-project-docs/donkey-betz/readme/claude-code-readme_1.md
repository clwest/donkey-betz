# Claude Code Compatibility Notes

## Why Some Files Are Excluded

Claude Code has content filters that can be triggered by certain technical terms or patterns. We've identified and excluded files that contain:

1. **Authentication/Security Terms**: Even placeholder credentials can trigger filters
2. **Mythology/Misinformation Tracking**: Technical terms about tracking false information
3. **System Manipulation Terms**: Words like "injection", "mutation", "propagation"

## Excluded Files

### Documentation
- `CLAUDE.md` → Backed up as `CLAUDE.md.backup`
- `INTELLIGENT_AGENT_PROMPTING.md` → Backed up as `INTELLIGENT_AGENT_PROMPTING.md.backup`
- Various mythology-related documentation files

### Directories
- `backend/mythology_lab/` - System for tracking misinformation
- `donkey-betz-frontend/src/features/mythology-lab/` - Frontend components

## How to Access Original Files

All excluded files are either:
1. Backed up with `.backup` extension
2. Still accessible locally (just excluded from Claude Code)

To restore a file:
```bash
mv FILENAME.backup FILENAME
```

## Alternative Access

For code review of excluded files:
1. Use your local IDE (VSCode, etc.)
2. Review specific sections by copying relevant parts
3. Use the cleaned versions (like `PROJECT_STATUS.md`)

## Modifying .claudeignore

The `.claudeignore` file works like `.gitignore`. To include a file again:
1. Remove its entry from `.claudeignore`
2. Or comment it out with `#`

---

These exclusions ensure Claude Code runs smoothly without triggering false positives from technical terminology.
