"""
Action Plan Formatter

Creates beautiful, professional action plans instead of raw JSON dumps
"""

from datetime import datetime
from typing import Dict, Any, List


class ActionPlanFormatter:
    """Format action plans into beautiful, actionable documents"""

    def format_complete_plan(self, plan_data: Dict[str, Any]) -> str:
        """Create a beautifully formatted complete action plan"""

        opportunity = plan_data.get('opportunity_title', 'Business Opportunity')
        plan_id = plan_data.get('id', 'unknown')
        steps = plan_data.get('steps', [])
        timeline = plan_data.get('timeline', '4 weeks')

        # Extract actual AI-generated content from steps
        step_contents = []
        for i, step in enumerate(steps, 1):
            step_data = plan_data.get(f'step_{i}_data', {})
            ai_content = step_data.get('ai_content', '')
            if ai_content and 'GPT-5-mini Error' not in ai_content:
                step_contents.append({
                    'number': i,
                    'title': step,
                    'content': ai_content
                })

        # Create the formatted plan
        formatted_plan = f"""# 🚀 {opportunity} - Master Action Plan

## 📋 Executive Summary
Transform your expertise into a profitable {opportunity.lower()} business using our platform's powerful AI tools and automation capabilities.

**Timeline:** {timeline}
**Difficulty:** Intermediate
**Investment:** Minimal (Platform tools included)
**Potential:** $2,000-$10,000/month

---

## 🎯 Your Success Path

### Phase 1: Foundation (Week 1)
**Goal:** Establish your service foundation using platform tools

#### Day 1-3: Setup & Research
✅ **Use AI Content Studio** to create your brand identity
- Generate professional logo with DALL-E integration
- Design brand colors and style guide
- Create business card templates

✅ **Deploy Research Agent** for market analysis
- Analyze competitor pricing and services
- Identify your unique value proposition
- Find your first 10 potential clients

#### Day 4-7: Content Creation
✅ **Leverage Content-Creator Agent** for materials
- Generate service descriptions and packages
- Create email templates for outreach
- Build FAQ and knowledge base

💡 **Platform Advantage:** No external tools needed - everything integrated!

---

### Phase 2: Launch (Week 2)
**Goal:** Go live with your service

#### Day 8-10: Platform Setup
✅ **Configure Revenue Engine** for payments
- Set up tiered pricing (Basic/Pro/Premium)
- Enable automated invoicing
- Configure subscription management

✅ **Activate Marketing Agent** for promotion
- Create social media campaign
- Design promotional graphics
- Schedule content distribution

#### Day 11-14: First Clients
✅ **Use Outreach Automation**
- Send personalized proposals
- Track engagement with ML Analytics
- A/B test your messaging

🎉 **Milestone:** Land your first 3 paying clients!

---

### Phase 3: Scale (Week 3)
**Goal:** Optimize and expand

#### Day 15-17: Service Optimization
✅ **Deploy Specialized Agents**
- Use coding-agent for automation scripts
- Implement workflow improvements
- Create client onboarding system

#### Day 18-21: Growth Tactics
✅ **Leverage Platform Analytics**
- Track conversion rates
- Optimize pricing strategy
- Identify expansion opportunities

📈 **Target:** 10 active clients by end of week 3

---

### Phase 4: Systemize (Week 4)
**Goal:** Build sustainable business

#### Day 22-24: Automation
✅ **Full Platform Integration**
- Automate repetitive tasks
- Set up recurring revenue streams
- Create passive income products

#### Day 25-28: Scale Strategy
✅ **Growth Planning**
- Hire virtual assistants through agent network
- Expand service offerings
- Plan for $5K+ monthly revenue

🏆 **Success Metrics:**
- 15+ active clients
- $3,000+ monthly recurring revenue
- 80% automated workflows
- 5-star client satisfaction

---

## 💰 Revenue Projections

| Week | Clients | Revenue | Platform Tools Used |
|------|---------|---------|-------------------|
| 1 | 0-2 | $0-500 | AI Content Studio, Research Agent |
| 2 | 3-5 | $500-1,500 | Revenue Engine, Marketing Agent |
| 3 | 6-10 | $1,500-3,000 | ML Analytics, Specialized Agents |
| 4 | 11-15 | $3,000-5,000 | Full Automation Suite |

---

## 🛠️ Platform Tools Checklist

### Essential Tools (Week 1)
- [ ] AI Content Studio - Branding & design
- [ ] Content-Creator Agent - Copy & materials
- [ ] Research Agent - Market analysis

### Growth Tools (Week 2-3)
- [ ] Revenue Engine - Payment processing
- [ ] Marketing Agent - Promotion
- [ ] ML Analytics - Performance tracking

### Scale Tools (Week 4+)
- [ ] Coding Agent - Automation
- [ ] Agent Network - Virtual team
- [ ] Distribution System - Multi-channel reach

---

## 📚 Resources & Support

### Platform Documentation
- **AI Content Studio Guide:** Create stunning visuals with DALL-E
- **Agent Network Tutorial:** Deploy specialized agents
- **Revenue Engine Setup:** Start accepting payments in minutes

### Quick Links
- 🎨 Access AI Content Studio
- 🤖 Deploy Specialized Agents
- 💳 Configure Revenue Engine
- 📊 View ML Analytics Dashboard

---

## ⚡ Quick Start Actions

### Today (Do These Now!)
1. **Create your brand** using AI Content Studio
2. **Research your niche** with Research Agent
3. **Draft your first offer** with Content-Creator

### Tomorrow
1. Set up Revenue Engine for payments
2. Create 5 pieces of marketing content
3. Reach out to 10 potential clients

### This Week
1. Land your first 3 clients
2. Deliver exceptional service
3. Collect testimonials

---

## 🎯 Success Tips

✨ **Leverage Platform Advantages:**
- No external subscriptions needed
- All tools integrated seamlessly
- Real-time analytics and optimization
- 24/7 AI agent support

⚠️ **Avoid Common Mistakes:**
- Don't use external tools like Canva or Gumroad
- Don't manually handle what agents can automate
- Don't ignore the ML Analytics insights
- Don't undercharge - our platform adds premium value

---

## 📈 30-Day Success Metrics

**Week 1:** Foundation ✅
**Week 2:** First Revenue ✅
**Week 3:** Scaling Up ✅
**Week 4:** Systems Built ✅

**30-Day Goals:**
- 💰 $3,000+ in revenue
- 👥 15+ happy clients
- ⚡ 80% automated
- 🚀 Ready to scale to $10K/month

---

*Generated by Income Builder AI System*
*Powered by 102+ Specialized Agents*
*All tools included - no external subscriptions needed!*
"""

        return formatted_plan

    def format_step_content(self, step_data: Dict[str, Any], step_number: int) -> str:
        """Format individual step content"""

        step_title = step_data.get('title', f'Step {step_number}')
        ai_content = step_data.get('ai_content', '')
        real_data = step_data.get('real_data', {})

        # Extract useful data from real_data
        search_results = real_data.get('search_results', {}).get('results', [])
        market_insights = []

        for result in search_results[:3]:
            if result.get('snippet'):
                market_insights.append(f"• {result['snippet']}")

        formatted_step = f"""# Step {step_number}: {step_title}

## 🎯 Objective
{ai_content if ai_content and 'Error' not in ai_content else f'Complete {step_title.lower()} using platform tools'}

## 📊 Market Intelligence
{chr(10).join(market_insights) if market_insights else '• Leverage platform analytics for insights'}

## ✅ Action Items
1. Use AI Content Studio for visual assets
2. Deploy specialized agents for automation
3. Track progress with ML Analytics
4. Optimize based on real-time data

## 🛠️ Platform Tools
- **Primary:** AI Content Studio, Content-Creator Agent
- **Support:** ML Analytics, Revenue Engine
- **Advanced:** Agent Network, Distribution System

## 📈 Success Metrics
- Task completion: 100%
- Time saved: 75% vs manual
- Cost saved: $200+ vs external tools

---
*Powered by Platform AI*
"""

        return formatted_step

    def format_quickstart_guide(self, plan_data: Dict[str, Any]) -> str:
        """Create a quickstart guide"""

        opportunity = plan_data.get('opportunity_title', 'Business Opportunity')

        quickstart = f"""# ⚡ {opportunity} - Quick Start Guide

## 🚀 Start in 5 Minutes

### Step 1: Brand Creation (2 min)
```
1. Open AI Content Studio
2. Generate logo with prompt: "Professional logo for {opportunity.lower()}"
3. Save brand assets
```

### Step 2: Service Setup (2 min)
```
1. Deploy Content-Creator Agent
2. Generate service description
3. Create pricing tiers
```

### Step 3: Launch (1 min)
```
1. Activate Revenue Engine
2. Enable payment processing
3. Go live!
```

## 🎯 First 24 Hours Checklist

⏰ **Hour 1-2:** Setup
- [ ] Create brand identity
- [ ] Write service description
- [ ] Set pricing

⏰ **Hour 3-4:** Content
- [ ] Generate 5 marketing posts
- [ ] Create email templates
- [ ] Build FAQ

⏰ **Hour 5-8:** Outreach
- [ ] Find 20 prospects
- [ ] Send 10 proposals
- [ ] Schedule follow-ups

⏰ **Hour 9-24:** Optimize
- [ ] Track responses
- [ ] Adjust messaging
- [ ] Book first calls

## 💰 Quick Revenue Path

**Day 1:** Setup + First outreach = 0 clients
**Day 3:** Follow-ups + Calls = 1-2 clients
**Day 7:** Referrals + Growth = 3-5 clients
**Day 14:** Systems + Scale = 10+ clients
**Day 30:** Automation + Optimize = $3,000+ MRR

---

*No external tools needed - everything included in platform!*
"""

        return quickstart


# Global formatter instance
action_plan_formatter = ActionPlanFormatter()

def format_action_plan(plan_data: Dict[str, Any]) -> Dict[str, str]:
    """Format action plan data into beautiful documents"""

    formatter = ActionPlanFormatter()

    return {
        'complete_plan': formatter.format_complete_plan(plan_data),
        'quickstart': formatter.format_quickstart_guide(plan_data)
    }