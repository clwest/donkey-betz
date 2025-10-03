# CLAUDE.md Migration Guide

## Why a Fresh Start?

The original CLAUDE.md grew to over 750 lines with months of accumulated changes, making it difficult to find current, relevant information. The new structure focuses on:

1. **Current State** - What's working NOW
2. **Active Development** - What we're building
3. **Essential Patterns** - Proven approaches
4. **Quick Solutions** - Common fixes

## What's Changed?

### Old Structure (750+ lines)
- Historical development timeline
- Legacy issues and fixes
- Outdated React app references
- Accumulated troubleshooting notes
- Mixed platform instructions

### New Structure (200 lines)
- Current feature status
- Active development guidelines
- Essential commands only
- Proven patterns and solutions
- Clear next steps

## Key Information Preserved

### ✅ Kept in New CLAUDE.md
- Quick start commands
- Current feature status (as of July 6, 2025)
- Essential API patterns
- WebSocket implementation
- Error handling patterns
- Common UUID/serialization fixes
- Active development philosophy

### 📁 Moved to Archive
- Historical timeline (Phases 1-8)
- Old bug fixes
- Legacy React app info
- Completed feature announcements
- Old troubleshooting notes

### 📍 Reference Locations
- **Historical Context**: `CLAUDE_ARCHIVE_JULY_2025.md`
- **Detailed Methods**: `METHOD_INDEX_ESSENTIAL.md`
- **Current Tasks**: `CURRENT_STATE/active-tasks.md`
- **Recent Fixes**: `CURRENT_STATE/recent-fixes.md`

## Migration Checklist

When you switch to the new CLAUDE.md:

1. **Rename Files**:
   ```bash
   mv CLAUDE.md CLAUDE_OLD.md
   mv CLAUDE_NEW.md CLAUDE.md
   ```

2. **Verify Key Sections**:
   - [ ] Quick start commands work
   - [ ] Feature status is accurate
   - [ ] Development guidelines are clear
   - [ ] Common issues have solutions

3. **Update Bookmarks**:
   - Archive references → `CLAUDE_ARCHIVE_JULY_2025.md`
   - Method lookups → `METHOD_INDEX_ESSENTIAL.md`
   - Current work → `CURRENT_STATE/`

## Benefits of Fresh Start

1. **Faster Context Loading**: 200 lines vs 750 lines
2. **Current Information**: No outdated instructions
3. **Clear Organization**: Logical sections
4. **Action-Oriented**: Focus on building, not history
5. **Better AI Assistant Performance**: Less token usage

## Recommended Workflow

1. **Start Here**: New `CLAUDE.md` for current context
2. **If Needed**: Check archive for historical decisions
3. **For Methods**: Use `METHOD_INDEX_ESSENTIAL.md`
4. **For Tasks**: Check `CURRENT_STATE/active-tasks.md`

---

Migration prepared on July 6, 2025