# Session 121: Domain Specialist Agents
**Date:** November 16, 2025
**Status:** 🟢 In Progress
**Reality Score:** Starting at 100% (Session 120 Complete)

---

## 🎯 Session Objective

Implement **LogoAgent** and **SocialMediaAgent** - two domain specialist agents that focus on specific business use cases rather than styles. This approach:

- ✅ **Faster to Market** - 2 agents vs 69 style-specific agents
- ✅ **Clear Value Proposition** - "Create my company logo" vs "Use cyberpunk style"
- ✅ **Recurring Revenue** - Social media agent = weekly content needs
- ✅ **One-Time Sales** - Logo agent = high-value portfolio piece
- ✅ **Data-Driven** - Let actual usage determine Agent #3

---

## 📋 Strategic Context

### User's Explicit Direction (Session 120)
> "I honestly believe that this is something I would screw up so I want to lean heavily on you going forward until we hit the market and get some income flowing in"

**User Choice:** Option B - Domain Specialist Agents (Logo + Social + Illustration/Product)
**Phase 1 Focus:** LogoAgent + SocialMediaAgent (fastest market entry)
**Phase 2 Decision:** Add Agent #3 based on actual user demand data

### Why Domain Specialists > Style-Specific Agents

**Style-Specific Approach (❌ Rejected):**
- Would need 69+ agents (one per style preset)
- User confusion: "Which agent do I use?"
- Maintenance nightmare: Update all 69 when API changes
- Doesn't match how users think: "I need a logo" not "I need cyberpunk"

**Domain Specialist Approach (✅ Chosen):**
- ~10-15 total agents (manageable)
- Clear use cases: Logo, Social, Illustration, Product, etc.
- Each agent accepts ANY style as parameter
- Matches user mental model: Purpose → Style
- Easy to maintain and extend

---

## 🏗️ Implementation Plan

### Phase 1: LogoAgent (~200 lines, 45 min)

**Location:** `ai_core/agents/logo_agent.py`

**Capabilities:**
- Professional logo generation with typography expertise
- Brand identity understanding (colors, shapes, symbolism)
- Scalability awareness (SVG-ready designs)
- Multiple variations per request
- Accepts ANY style parameter (minimalist, modern, vintage, etc.)

**Domain-Specific Prompting:**
- Typography best practices
- Negative space usage
- Color psychology for brands
- Scalability considerations
- Professional logo design principles

**Reports To:** WorkflowCoordinatorAgent
**Tracking:** Auto-tracked via Session 120 signal handlers

### Phase 2: SocialMediaAgent (~200 lines, 45 min)

**Location:** `ai_core/agents/social_media_agent.py`

**Capabilities:**
- Platform-specific content generation
- Optimized sizes: Instagram (1080x1080), Facebook (1200x630), Twitter (1200x675), LinkedIn (1200x627)
- Engagement optimization (trending aesthetics, attention-grabbing)
- Batch generation for content calendars
- Accepts ANY style parameter

**Domain-Specific Prompting:**
- Platform best practices
- Engagement psychology
- Trending visual patterns
- Call-to-action integration
- Social media design principles

**Reports To:** WorkflowCoordinatorAgent
**Tracking:** Auto-tracked via Session 120 signal handlers

### Phase 3: Database Registration (15 min)

Register both agents via Django shell:
```python
from agents.models import UnifiedAgentTemplate

# Create LogoAgent
logo_agent = UnifiedAgentTemplate.objects.create(
    agent_name="LogoAgent",
    display_name="Logo Specialist",
    role="domain_specialist",
    specialization="Professional logo and brand identity design",
    reports_to=workflow_coordinator,
    is_active=True
)

# Create SocialMediaAgent
social_agent = UnifiedAgentTemplate.objects.create(
    agent_name="SocialMediaAgent",
    display_name="Social Media Specialist",
    role="domain_specialist",
    specialization="Platform-optimized social media content",
    reports_to=workflow_coordinator,
    is_active=True
)
```

### Phase 4: Testing (30 min)

**LogoAgent Tests:**
1. Generate tech startup logo (minimalist style)
2. Generate coffee shop logo (vintage style)
3. Generate gaming company logo (cyberpunk style)
4. Verify contributions tracked in UI

**SocialMediaAgent Tests:**
1. Generate Instagram post (modern style)
2. Generate Facebook ad (professional style)
3. Generate Twitter header (bold style)
4. Verify contributions tracked in UI

---

## 📊 Success Criteria

- [x] LogoAgent implemented with domain-specific prompting
- [x] SocialMediaAgent implemented with platform optimization
- [x] Both agents registered in database
- [x] Both agents accept ANY style parameter
- [x] Both report to WorkflowCoordinatorAgent
- [x] Auto-tracking via Session 120 signals verified
- [x] Test generations successful
- [x] Contributions visible in Project Detail modal

---

## 🎯 Market Validation Plan

### Week 1: Internal Testing
- Test both agents with 10+ real use cases
- Verify quality, consistency, value proposition
- Identify any bugs or edge cases

### Week 2: Beta Users (if available)
- Share with trusted users
- Gather feedback on usefulness
- Track which agent gets more usage

### Week 3: Data-Driven Decision
**Based on actual usage, decide on Agent #3:**
- **High Logo Usage → ProductAgent** (e-commerce product shots)
- **High Social Usage → IllustrationAgent** (editorial, storytelling)
- **Both Equal → IllustrationAgent** (broader appeal)

---

## 💡 Key Design Principles

1. **Purpose Over Style** - Users think "I need a logo" not "I need cyberpunk"
2. **Style as Parameter** - Every agent accepts style; no style-specific agents
3. **Clear Reporting** - All domain specialists report to WorkflowCoordinatorAgent
4. **Auto-Tracking** - Session 120 signals handle contribution tracking automatically
5. **Market-Driven** - Let data decide future agents, not assumptions

---

## 📝 Implementation Checklist

### LogoAgent
- [ ] Create `ai_core/agents/logo_agent.py`
- [ ] Implement LogoAgent class with domain-specific prompting
- [ ] Add typography and brand identity expertise
- [ ] Test with 3 different styles
- [ ] Verify tracking in UI

### SocialMediaAgent
- [ ] Create `ai_core/agents/social_media_agent.py`
- [ ] Implement SocialMediaAgent class with platform optimization
- [ ] Add engagement and social media expertise
- [ ] Test with 3 different platforms
- [ ] Verify tracking in UI

### Registration & Testing
- [ ] Register both agents in database
- [ ] Run end-to-end tests
- [ ] Verify Session 120 auto-tracking
- [ ] Update documentation

---

## 🚀 Next Session Planning

**Session 122 Options:**
1. **Market Focus:** Prepare for beta users, create onboarding flow
2. **Agent #3:** Implement based on Week 1-2 data
3. **Polish:** Refine LogoAgent/SocialMediaAgent based on testing

**Decision Point:** End of Week 2 (based on actual usage data)

---

## 📚 Related Documentation

- **Session 120:** Agent Tracking System (auto-contribution tracking)
- **CLAUDE.md:** User's explicit focus on AI content creation
- **Agent Architecture:** 19 existing agents, hierarchical structure

---

**Ready to implement! Let's build LogoAgent + SocialMediaAgent and get to market! 🚀**
