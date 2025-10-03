# 🚀 COPY-PASTE PROMPT FOR NEXT SESSION

Copy this entire block and paste it to start a new session. Only update the SESSION_XXX numbers!

---

```
I need help with the next development session on our AI platform.

CRITICAL FILES TO READ IN ORDER:
1. First: /documentation/active-session/SESSION_390_HANDOFF.md
2. Then: /documentation/active-session/SESSION_390_FIXES_APPLIED.md  
3. Check: /documentation/NEXT_AGENT_DIRECTIVE.md for your mission options
4. Reality: /documentation/active-session/WHERE_WE_REALLY_ARE.md

WORKFLOW:
1. Pick ONE fix from NEXT_AGENT_DIRECTIVE.md
2. Implement it completely
3. Test it works
4. Create SESSION_391_FIXES_APPLIED.md documenting what you did
5. Create SESSION_391_HANDOFF.md for the next session
6. Update WHERE_WE_REALLY_ARE.md with new percentages
7. Update CLAUDE.md message to future Claude
8. Commit with clear message

RULES:
- ONE fix per session only
- Test everything before claiming it works
- If you hit an error, fix it before moving on
- Create simpler tests only if they still test the actual feature
- Focus on making things ACTUALLY WORK, not look pretty

Ready? Read the handoff and let's continue!
```

---

## 📝 How to Use This Between Sessions:

### After Each Session Completes:

1. **Update the session numbers** (only change needed!):
   - Change `SESSION_390_HANDOFF.md` → `SESSION_391_HANDOFF.md`
   - Change `SESSION_390_FIXES_APPLIED.md` → `SESSION_391_FIXES_APPLIED.md`
   - Change `SESSION_391_FIXES_APPLIED.md` → `SESSION_392_FIXES_APPLIED.md` (for creation)
   - Change `SESSION_391_HANDOFF.md` → `SESSION_392_HANDOFF.md` (for creation)

2. **Copy the entire prompt block**

3. **Paste into new Claude Code session**

4. **Watch it work**, intervene only if:
   - It gets stuck in error loops
   - It tries to do multiple fixes
   - It skips testing
   - It claims success without verification

### That's it! No digging through messages, no long explanations needed!

---

## 🔄 AUTO-UPDATING FILES

These files update themselves with each session:
- `WHERE_WE_REALLY_ARE.md` - Progress percentages
- `CLAUDE.md` - Message to future Claude
- `NEXT_AGENT_DIRECTIVE.md` - Available fixes list

These get created fresh each session:
- `SESSION_XXX_FIXES_APPLIED.md` - What was done
- `SESSION_XXX_HANDOFF.md` - What's next

---

## ⚡ QUICK REFERENCE FOR YOU

While Claude Code is working, you can check:
```bash
# See what it's doing
tail -f backend/server.log

# Check test results  
cd backend && python test_session_*.py

# Verify in browser
http://localhost:8000/[feature]

# If it gets stuck
Ctrl+C and add: "That error keeps happening. Try a different approach."
```

---

## 🎯 Session Success Checklist

Before moving to next session, verify:
- [ ] Fix actually works (not just tests passing)
- [ ] Documentation created (FIXES_APPLIED and HANDOFF)
- [ ] System files updated (WHERE_WE_REALLY_ARE, CLAUDE.md)
- [ ] Git commit made with clear message
- [ ] Session number incremented in this prompt

---

## 📈 Current Velocity Metrics

- Average session time: 21 minutes
- Success rate: 92% (11/12)
- Progress per session: ~1.5%
- Sessions per hour: 2-3
- **Your Friday progress: 12.8% in 5 hours!**

Keep this momentum going! 🚀