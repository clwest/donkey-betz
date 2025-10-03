# Smart Agent Selection System Overview

## How Smart Agent Selection Works

The Smart Agent Selection system is a sophisticated pattern-matching algorithm that automatically routes user tasks to the most appropriate agent from a pool of 21 specialized agents.

### 1. Pattern Matching System

The system analyzes your task description against predefined patterns for each of the 21 agents. Each agent has:

- **Keywords**: Single words that indicate the agent's domain (worth 1 point each)
- **Phrases**: Multi-word patterns that strongly indicate the agent (worth 2 points each)  
- **Priority**: A weighting factor (1-11) that boosts certain agents

### 2. Scoring Algorithm

For each agent:
1. Count keyword matches (1 point each)
2. Count phrase matches (2 points each)
3. Apply priority weighting: `score = raw_score * (priority / 10)`
4. Normalize confidence: `confidence = min(score / 5, 1.0)`

### 3. Example Selection Process

Let's say you type: **"create a marketing campaign for my new product"**

**Content Agent:**
- Keywords: "create" (+1)
- Score: 1 * (10/10) = 1.0

**Marketing Agent:**
- Keywords: "marketing", "campaign" (+2)
- Phrases: "marketing campaign" (+2)
- Score: 4 * (5/10) = 2.0  ← **WINNER!**

**Business Agent:**
- Keywords: "product" (not in list)
- Score: 0

**Final Result:** Marketing Agent selected with confidence 0.40 (2.0/5)

### 4. Fallback Logic

If no patterns match:
- Questions (how/what/when/where/why) → Research Agent
- Everything else → Business Agent (default)

### 5. Priority Rankings (Highest to Lowest)

1. **System Analysis Agent** (11) - For meta-queries about the system itself
2. **Content Agent** (10) - Writing and content creation
3. **Market Intelligence Agent** (9) - Stock/market analysis
4. **Business Agent** (8) - General business tasks
5. **Research Agent** (7) - Information gathering
6. **Creative Agent** (6) - Design tasks
7. **Marketing Agent** (5) - Marketing campaigns
8. **Technical Agent** (4) - Coding tasks
9. **Financial Agent** (3) - Budget/finance

### 6. Confidence Messages

The system provides different messages based on confidence levels:

- **>0.8**: "Perfect! I'll deploy the [Agent] for this task."
- **0.5-0.8**: "I think the [Agent] would be best suited for this task."
- **<0.5**: "I'll use the [Agent] to help with this. If you had a different agent in mind, just let me know!"

### 7. Implementation Details

The logs show this process in action:
- `Smart agent selection for task: ...` - Shows the input being analyzed
- Displays scores for each agent
- Shows which agent was selected with what confidence level

## File Locations

- **Implementation**: `ai_partner/services/smart_agent_selector.py`
- **Agent Patterns**: Defined within the same file

## Key Features

1. **Multi-factor Scoring**: Combines keywords, phrases, and priorities
2. **Confidence-based Messaging**: Adapts response based on selection confidence
3. **Intelligent Fallback**: Has sensible defaults for unmatched queries
4. **Priority Weighting**: Certain agents get preference for general queries
5. **Transparent Selection**: Logs show exactly how decisions are made

This system ensures that user tasks are routed to the most appropriate specialized agent, improving response quality and task completion efficiency.