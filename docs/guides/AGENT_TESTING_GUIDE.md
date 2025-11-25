# 🤖 Agent Testing Guide - Personal Assistant

**Goal:** Verify the Personal Assistant can orchestrate multiple agents to complete complex tasks

---

## 🎯 Test Prompt

```
Research a snowboarding school and create 3 logos and 2 promo videos
```

**Why This Tests Everything:**
- ✅ Multi-agent orchestration (Research → Creative → Image Gen → Video Gen)
- ✅ Complex workflow (5 distinct steps)
- ✅ Project creation (auto-creates project for 3+ assets)
- ✅ Agent communication (agents coordinate with each other)
- ✅ Real deliverables (3 images + 2 videos)

---

## 📋 Expected Agent Workflow

### Step 1: Research Agent
**Task:** Gather snowboarding school information
**Expected Output:**
- School names, locations, target audience
- Industry insights, branding trends
- Key messaging themes

### Step 2: Creative Director Agent
**Task:** Plan 3 logo concepts
**Expected Output:**
- 3 distinct logo design briefs
- Style recommendations (modern, playful, professional)
- Color palettes and themes

### Step 3: Image Generation Agent (x3)
**Task:** Generate 3 logos based on briefs
**Expected Output:**
- 3 unique logo images (1024x1024)
- Saved to database
- Linked to project

### Step 4: Video Strategy Agent
**Task:** Plan 2 promo video concepts
**Expected Output:**
- 2 video concept briefs
- Scene descriptions
- Motion/style recommendations

### Step 5: Video Generation Agent (x2)
**Task:** Generate 2 promo videos
**Expected Output:**
- 2 video clips (5-10 seconds each)
- Saved to database
- Linked to project

---

## ✅ Success Criteria

**Agent Orchestration:**
- [ ] Personal Assistant accepts the prompt
- [ ] Correctly identifies need for multiple agents
- [ ] Agents execute in logical order
- [ ] Agents communicate/coordinate with each other
- [ ] No errors or failures

**Deliverables:**
- [ ] 3 logo images generated (different styles)
- [ ] 2 promo videos generated
- [ ] All assets linked to auto-created project
- [ ] Assets visible in gallery
- [ ] Project shows 5 total assets (3 images + 2 videos)

**Quality:**
- [ ] Logos are relevant to snowboarding/school theme
- [ ] Videos match promo/marketing purpose
- [ ] Quality is production-ready
- [ ] Assets are downloadable

---

## 🧪 How to Test

### Option 1: Web UI (Recommended)
1. Go to http://localhost:8000/ai-studio/
2. Open **Personal Assistant** tab/section
3. Type the test prompt in chat
4. Submit and watch the workflow execute
5. Verify all 5 assets are created

### Option 2: WebSocket API
```python
# Connect to WebSocket
ws://localhost:8000/ws/personal-assistant/

# Send message
{
  "message": "Research a snowboarding school and create 3 logos and 2 promo videos",
  "user_id": "admin"
}

# Monitor responses
# Should see: Research results → Logo concepts → Images generated → Video concepts → Videos generated
```

### Option 3: Direct API Test
```bash
# If there's a REST endpoint:
curl -X POST http://localhost:8000/api/v1/personal-assistant/message/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_TOKEN" \
  -d '{"message": "Research a snowboarding school and create 3 logos and 2 promo videos"}'
```

---

## 🔍 What to Look For

### During Execution:
- **Progress updates** - "Researching snowboarding schools..."
- **Agent coordination** - "Creative Director consulting with Research Agent..."
- **Status messages** - "Generating logo 1 of 3..."
- **Completion notifications** - "All assets created! View in gallery."

### After Completion:
- **Gallery view** - 3 logos + 2 videos visible
- **Project view** - Auto-created project named "Snowboarding School Campaign" (or similar)
- **Asset quality** - Logos look professional, videos are relevant
- **Metadata** - Each asset has prompt, parameters, timestamps

---

## 🐛 Common Issues & Fixes

### Issue: "No response from assistant"
**Fix:** Check WebSocket connection, verify backend is running

### Issue: "Only images generated, no videos"
**Fix:** Check Runway ML API key, verify video generation is enabled

### Issue: "Research not relevant"
**Fix:** Check if web search is enabled, verify search API working

### Issue: "Assets not linked to project"
**Fix:** Verify project auto-creation logic (3+ assets trigger)

### Issue: "Generic/unthemed output"
**Fix:** Check agent prompt engineering, verify context passing between agents

---

## 📊 Evaluation Criteria

**Pass:**
- All 5 assets generated
- Assets are thematically consistent (snowboarding school theme)
- Workflow completes in <10 minutes
- No errors or failures
- Assets are usable/downloadable

**Partial Pass:**
- Some assets generated but not all
- Theme is present but weak
- Some errors but workflow completes
→ **Action:** Document issues, prioritize fixes

**Fail:**
- No assets generated
- Workflow crashes/hangs
- Output is completely irrelevant
→ **Action:** Debug agent orchestration, fix critical issues

---

## 🎬 Next Steps Based on Results

### If PASS:
1. ✅ **Document the workflow** for YouTube content
2. ✅ **Create demo video** showing this capability
3. ✅ **Plan YouTube content:** "Watch My AI Create a Complete Marketing Campaign"
4. ✅ **Move to DaVinci testing** to edit the outputs

### If PARTIAL:
1. 📝 **List what worked** vs what didn't
2. 🔧 **Prioritize fixes** (critical path only)
3. 🧪 **Re-test** after fixes
4. ✅ **Proceed** once core workflow works

### If FAIL:
1. 🐛 **Debug agent orchestration** (find root cause)
2. 🔧 **Fix critical issues** (agent communication, API integrations)
3. 🧪 **Test with simpler prompt** first ("Create 2 logos")
4. 📈 **Incrementally add complexity** until full workflow works

---

## 💡 Why This Matters

**This is your KILLER FEATURE:**
- Most AI tools: "Generate an image"
- Your platform: "Here's a complete marketing campaign with research, logos, and videos"

**This is what you show in YouTube videos.**
**This is what gets users excited.**
**This is what justifies premium pricing.**

**If this works → You have something truly differentiated.**
**If it doesn't → Fix it before shipping.**

---

**Ready to test?** 🚀

1. Open AI Studio
2. Go to Personal Assistant
3. Type the prompt
4. Watch the magic happen (or debug what breaks!)
