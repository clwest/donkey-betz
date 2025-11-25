# Code Review Quick Start Guide

Get the code review running in 5 minutes.

---

## Prerequisites

- 8 Claude Code terminal windows (or run sequentially)
- Access to the codebase
- Output directory ready: `docs/code-review/outputs/`

---

## Step 1: Open Terminal Windows

Open 8 separate Claude Code instances (or as many as you can run in parallel).

---

## Step 2: Copy & Paste Prompts

Go to `01-SESSION-PROMPTS.md` and copy each session's prompt into a separate Claude Code instance:

| Window | Prompt to Copy |
|--------|----------------|
| Terminal 1 | Session 1: AI Assistant & LLM Integration |
| Terminal 2 | Session 2: Image Generation Pipeline |
| Terminal 3 | Session 3: Video Pipeline & Processing |
| Terminal 4 | Session 4: Agent System & Orchestration |
| Terminal 5 | Session 5: Frontend & Templates |
| Terminal 6 | Session 6: Database Models & Data Layer |
| Terminal 7 | Session 7: API Integrations & External Services |
| Terminal 8 | Session 8: Security, Config & Infrastructure |

---

## Step 3: Wait for Completion

Each session will:
1. Read the specified files
2. Analyze for issues
3. Generate a detailed report

**Expected time:** 25-45 minutes per session (can run in parallel)

---

## Step 4: Save Outputs

After each session completes, save the report:

```bash
# Save each session's output to:
docs/code-review/outputs/session-1-output.md
docs/code-review/outputs/session-2-output.md
docs/code-review/outputs/session-3-output.md
docs/code-review/outputs/session-4-output.md
docs/code-review/outputs/session-5-output.md
docs/code-review/outputs/session-6-output.md
docs/code-review/outputs/session-7-output.md
docs/code-review/outputs/session-8-output.md
```

---

## Step 5: Run Consolidation

After ALL 8 sessions complete, open a new Claude Code instance and paste the **Session 9: CONSOLIDATION** prompt from `01-SESSION-PROMPTS.md`.

This will:
1. Read all 8 session outputs
2. Merge and deduplicate findings
3. Generate `FINAL-CODE-REVIEW-REPORT.md`

---

## Step 6: Review Final Report

Open `docs/code-review/FINAL-CODE-REVIEW-REPORT.md` and review:

1. **Executive Summary** - Overall health
2. **Critical Issues (P0)** - Fix immediately
3. **Recommendations** - Prioritized action plan

---

## Alternative: Sequential Execution

If you can't run 8 sessions in parallel, run them one at a time:

```bash
# Session 1
# [paste prompt, wait ~30 min, save output]

# Session 2
# [paste prompt, wait ~30 min, save output]

# ... repeat for all 8 sessions ...

# Session 9 - Consolidation
# [paste prompt, generates final report]
```

**Total time (sequential):** ~4-6 hours
**Total time (parallel):** ~1-1.5 hours

---

## File Structure After Completion

```
docs/code-review/
├── 00-REVIEW-ORCHESTRATOR.md      # Overview doc
├── 01-SESSION-PROMPTS.md          # All prompts
├── 02-REPORT-TEMPLATE.md          # Session template
├── 03-FINAL-REPORT-TEMPLATE.md    # Final report template
├── 04-QUICK-START.md              # This file
├── outputs/
│   ├── session-1-output.md        # AI Assistant review
│   ├── session-2-output.md        # Image Generation review
│   ├── session-3-output.md        # Video Pipeline review
│   ├── session-4-output.md        # Agent System review
│   ├── session-5-output.md        # Frontend review
│   ├── session-6-output.md        # Database review
│   ├── session-7-output.md        # API Integration review
│   └── session-8-output.md        # Security & Config review
└── FINAL-CODE-REVIEW-REPORT.md    # Consolidated final report
```

---

## Troubleshooting

### Session times out
- Break large files into chunks
- Focus on most critical files first

### Missing file errors
- Verify file paths in prompts match actual codebase
- Use `ls` or `find` to locate files

### Output too long
- Ask Claude to summarize findings
- Focus on P0 and P1 issues

### Consolidation fails
- Ensure all 8 outputs exist
- Check output format matches template

---

## Tips for Best Results

1. **Don't interrupt sessions** - Let them complete fully
2. **Save outputs immediately** - Before closing terminals
3. **Use the template** - Consistent format helps consolidation
4. **Focus on actionable items** - Skip cosmetic issues
5. **Note line numbers** - Makes fixes easier to locate

---

## Next Steps After Review

1. **Triage P0 issues** - Assign and schedule fixes
2. **Create tickets** - Track each issue in your system
3. **Plan sprints** - Group related fixes
4. **Re-review after fixes** - Verify issues resolved

---

**Ready? Go to `01-SESSION-PROMPTS.md` and start copying prompts!**
