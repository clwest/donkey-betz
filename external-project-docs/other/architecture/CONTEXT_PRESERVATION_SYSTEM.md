# Context Preservation System for TRULY_COMPLETE

## 🎯 **Purpose**

This document defines how to use TRULY_COMPLETE as the single source of truth for completing the Donkey Betz project without losing context between Claude Code sessions.

---

## 📋 **System Overview**

### **Core Principles**
1. **One File Per System** - Each major system has its own detailed tracking file
2. **Progressive Updates** - Files are updated AS work happens, not after
3. **Context Handoff** - Each file ends with "Next Session Should..." section
4. **Implementation Tracking** - Detailed logs of what was tried/completed
5. **No External Dependencies** - All context needed is IN the file

---

## 🔄 **The Context Preservation Workflow**

### **1. Starting a Work Session**
```markdown
1. Read CLAUDE.md for project overview
2. Check CONTEXT_PRESERVATION_SYSTEM.md (this file)
3. Read the HANDOFF section at bottom of relevant TRULY_COMPLETE file
4. Continue from exact point described in handoff
```

### **2. During Work Session**
```markdown
1. Update "Current Session Log" section in real-time
2. Document each attempt (success or failure)
3. Update completion percentage after each milestone
4. Add new discoveries to "Known Issues" section
```

### **3. Ending a Work Session**
```markdown
1. Update "Implementation Progress" with what was completed
2. Update "Next Session Should..." with exact next steps
3. Include any error messages or blockers encountered
4. Update overall completion percentage
```

---

## 📁 **Required Sections for Each System File**

### **1. Status Header (Always at Top)**
```markdown
# [System Name] - Path to 100% Completion

## 🎯 **CURRENT STATUS: [X]% Complete**

**Last Updated**: [Date/Time]
**Last Session**: [Brief summary of last work]
**Next Priority**: [Exact next task to do]
**Blocker**: [Any blocking issue]
```

### **2. Current Session Log (Update in Real-Time)**
```markdown
## 📝 **CURRENT SESSION LOG**

### Session: [Date/Time]
**Goal**: [What you're trying to accomplish]

#### Attempt 1: [Description]
- **Action**: [What you did]
- **Result**: [What happened]
- **Error**: [Any error messages]
- **Next**: [What to try next]

#### Attempt 2: [Description]
...
```

### **3. Implementation Progress**
```markdown
## 📊 **IMPLEMENTATION PROGRESS**

### ✅ **Completed**
- [X] Task 1: Description (Session: Date)
- [X] Task 2: Description (Session: Date)

### 🔄 **In Progress**
- [ ] Task 3: Description
  - Subtask 3.1: Status
  - Subtask 3.2: Status

### 📋 **Not Started**
- [ ] Task 4: Description
- [ ] Task 5: Description
```

### **4. Code References**
```markdown
## 💻 **CODE REFERENCES**

### Key Files
- `path/to/file.py` - Purpose, last modified in session X
- `path/to/file.ts` - Purpose, last modified in session Y

### Key Functions
- `functionName()` in `file.py:123` - What it does
- `componentName` in `file.tsx:45` - What it renders

### API Endpoints
- `POST /api/endpoint/` - Purpose, authentication required
- `GET /api/endpoint/{id}/` - Purpose, returns format
```

### **5. Known Issues & Solutions**
```markdown
## 🐛 **KNOWN ISSUES & SOLUTIONS**

### Issue 1: [Description]
- **Symptoms**: What you see
- **Cause**: Root cause if known
- **Solution**: How to fix
- **Workaround**: Temporary fix if needed

### Issue 2: [Description]
...
```

### **6. Testing Checklist**
```markdown
## ✓ **TESTING CHECKLIST**

### Unit Tests
- [ ] Test 1: Description
- [ ] Test 2: Description

### Integration Tests
- [ ] Test 1: Description
- [ ] Test 2: Description

### Manual Testing
- [ ] Scenario 1: Steps to test
- [ ] Scenario 2: Steps to test
```

### **7. Handoff Section (CRITICAL - Update Before Ending Session)**
```markdown
## 🤝 **HANDOFF TO NEXT SESSION**

### **Next Session Should Start By:**
1. Check if [specific condition] is still true
2. Run [specific command] to verify status
3. Continue implementing [specific feature] in [specific file]

### **Current State:**
- Working on: [Exact feature/fix]
- Last error: [Copy of error message]
- Next step: [Specific action to take]

### **Commands to Run:**
```bash
# Verify environment
cd /path/to/project
source .venv/bin/activate

# Check current status
python manage.py check
npm run build

# Continue from
git status  # Should show changes in X, Y, Z
```

### **Don't Forget:**
- [Any special considerations]
- [Environment variables needed]
- [Services that must be running]
```

---

## 📊 **Master Progress Tracking**

Each system file should update this table in their header:

| Component | Description | Status |
|-----------|-------------|---------|
| Backend Auth | JWT token validation | 🔴 Broken |
| Frontend Auth | Token in requests | 🔴 Missing |
| API Client | Auth headers | 🟡 Partial |
| Token Refresh | Auto refresh | 🔴 Not Impl |
| Error Handling | Auth errors | 🟡 Basic |

**Legend**: 🔴 Broken/Missing | 🟡 Partial/Issues | 🟢 Working

---

## 🚀 **Quick Start for New Session**

```bash
# 1. Check overall status
cat TRULY_COMPLETE/README.md | grep "Current %"

# 2. Find priority system
cat TRULY_COMPLETE/README.md | grep "CRITICAL"

# 3. Read handoff
tail -n 50 TRULY_COMPLETE/AUTHENTICATION.md

# 4. Start work
code TRULY_COMPLETE/AUTHENTICATION.md
```

---

## 📝 **File Naming Convention**

- System files: `SYSTEM_NAME.md` (e.g., AUTHENTICATION.md)
- Reference files: `REFERENCE_*.md` (e.g., REFERENCE_API_ENDPOINTS.md)
- Meta files: `META_*.md` (e.g., META_CONTEXT_SYSTEM.md)

---

## 🔄 **Update Protocol**

### **Every 30 minutes during work:**
1. Save progress to Current Session Log
2. Update completion percentage if changed
3. Commit changes with message: "WIP: [System] - [What you're doing]"

### **Before ending session:**
1. Complete full handoff section
2. Update all progress tracking
3. Commit with message: "SESSION: [System] - [What was accomplished]"

### **When blocked:**
1. Document the blocker in detail
2. List what was tried
3. Suggest alternatives for next session
4. Update status to "BLOCKED: [reason]"

---

## 🎯 **Success Metrics**

A properly maintained TRULY_COMPLETE file should allow:
- New session to continue within 5 minutes of reading
- No loss of context between sessions
- Clear understanding of what works/doesn't work
- Exact reproduction of any errors
- Confidence in completion percentage

---

## 🚨 **Critical Rules**

1. **NEVER** mark something complete without testing
2. **ALWAYS** update the handoff before stopping
3. **DOCUMENT** errors exactly as they appear
4. **UPDATE** percentages based on working functionality
5. **INCLUDE** all commands and file paths used

---

## 📚 **Template for New System Files**

When adding a new system to TRULY_COMPLETE, copy the template from:
`TRULY_COMPLETE/TEMPLATE_SYSTEM.md`

This ensures consistent structure across all tracking files.