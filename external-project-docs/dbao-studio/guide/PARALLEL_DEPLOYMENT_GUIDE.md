# 🚀 CORE AGENTS PARALLEL DEPLOYMENT GUIDE

## THE POWER TRIO IS READY! 

You now have THREE world-class agent system prompts ready for parallel deployment:

1. 🎲 **Odds Calculation Agent** - The mathematical genius
2. 🛡️ **Risk Assessment Agent** - The bankroll guardian  
3. 🏆 **Sports Analytics Agent** - The sports data wizard

---

## 🎮 PARALLEL DEPLOYMENT STRATEGY

### Step 1: Open Three Terminal Windows

```bash
# Terminal 1: Odds Calculation Agent
cd /Users/donkeyking/development/donkey-betz-agent-orchestra
claude --prompt-file ./documentation/ODDS_AGENT_SYSTEM_PROMPT.md

# Terminal 2: Risk Assessment Agent
cd /Users/donkeyking/development/donkey-betz-agent-orchestra
claude --prompt-file ./documentation/RISK_AGENT_SYSTEM_PROMPT.md

# Terminal 3: Sports Analytics Agent
cd /Users/donkeyking/development/donkey-betz-agent-orchestra
claude --prompt-file ./documentation/SPORTS_AGENT_SYSTEM_PROMPT.md
```

### Step 2: Give Each Claude Code Instance Its Mission

#### Terminal 1 - Odds Agent:
```
"You are the Odds Calculation Agent. Implement yourself in the Agent Orchestra system. 
Create your template in /backend/agents/templates.py with specialization 'odds_calculation', 
implement your calculation tools in /backend/agents/tools/odds_calculator.py, 
and set up your API endpoints."
```

#### Terminal 2 - Risk Agent:
```
"You are the Risk Assessment Agent. Implement yourself in the Agent Orchestra system.
Create your template in /backend/agents/templates.py with specialization 'risk_assessment',
implement your risk analysis tools in /backend/agents/tools/risk_assessor.py,
and set up your monitoring systems."
```

#### Terminal 3 - Sports Agent:
```
"You are the Sports Analytics Agent. Implement yourself in the Agent Orchestra system.
Create your template in /backend/agents/templates.py with specialization 'sports_analytics',
implement your analysis tools in /backend/agents/tools/sports_analyzer.py,
and create your prediction models."
```

---

## 📁 FILE STRUCTURE THEY'LL CREATE

```
/backend/agents/
├── templates.py (all three will update this)
├── tools/
│   ├── odds_calculator.py (Odds Agent creates)
│   ├── risk_assessor.py (Risk Agent creates)
│   └── sports_analyzer.py (Sports Agent creates)
├── tests/
│   ├── test_odds_agent.py
│   ├── test_risk_agent.py
│   └── test_sports_agent.py
└── api/
    ├── odds_endpoints.py
    ├── risk_endpoints.py
    └── sports_endpoints.py
```

---

## 🔧 AVOIDING CONFLICTS

Each agent should work on separate files, but they'll all need to update `templates.py`. To avoid conflicts:

### Option 1: Sequential Template Updates
```python
# Have each agent add their template one at a time
# Agent 1 adds, commits, Agent 2 pulls and adds, etc.
```

### Option 2: Create Separate Template Files
```python
# Each agent creates their own file first:
/backend/agents/templates_odds.py
/backend/agents/templates_risk.py  
/backend/agents/templates_sports.py

# Then merge them into the main templates.py
```

### Option 3: Use Git Branches
```bash
# Each agent works on a branch
git checkout -b feature/odds-agent
git checkout -b feature/risk-agent
git checkout -b feature/sports-agent

# Merge when complete
```

---

## 🎯 INTEGRATION POINTS

These agents are designed to work together! They'll automatically integrate:

### Odds ↔️ Risk Integration
```python
# Odds Agent provides EV calculations
edge = odds_agent.calculate_expected_value(odds, probability)

# Risk Agent uses edge for stake sizing
stake = risk_agent.calculate_kelly_stake(edge, bankroll, confidence)
```

### Sports ↔️ Odds Integration
```python
# Sports Agent provides win probability
win_prob = sports_agent.predict_outcome(team_a, team_b)

# Odds Agent calculates if there's value
value = odds_agent.find_value(market_odds, win_prob)
```

### Sports ↔️ Risk Integration
```python
# Sports Agent provides variance estimate
variance = sports_agent.estimate_variance(matchup)

# Risk Agent adjusts limits based on variance
limits = risk_agent.adjust_limits(variance, bankroll)
```

---

## 🚀 DEPLOYMENT COMMANDS

### After All Agents Complete Their Work:

```bash
# 1. Merge all changes
git add .
git commit -m "Add Odds, Risk, and Sports Analytics Agents"

# 2. Update Django models
cd backend
python manage.py makemigrations
python manage.py migrate

# 3. Initialize all three agents
python manage.py shell
>>> from agents.models import AgentTemplate
>>> from agents.templates import AGENT_TEMPLATES
>>> 
>>> # Create Odds Agent
>>> AgentTemplate.objects.create(**AGENT_TEMPLATES['odds_calculation'])
>>> 
>>> # Create Risk Agent  
>>> AgentTemplate.objects.create(**AGENT_TEMPLATES['risk_assessment'])
>>> 
>>> # Create Sports Agent
>>> AgentTemplate.objects.create(**AGENT_TEMPLATES['sports_analytics'])

# 4. Run tests for all agents
python manage.py test agents.tests

# 5. Start the system
make dev
```

---

## 🧪 TEST THE POWER TRIO

### Test Query 1: Full Analysis Pipeline
```
"Analyze Lakers vs Celtics, current line Lakers -3.5 at -110"

Sports Agent → Provides win probability and projection
Odds Agent → Calculates expected value
Risk Agent → Determines optimal stake size
```

### Test Query 2: Arbitrage Opportunity
```
"Book A has Team X +150, Book B has Team Y -130, is there arbitrage?"

Odds Agent → Detects arbitrage opportunity
Risk Agent → Calculates safe stake distribution
Sports Agent → Provides context on why line divergence exists
```

### Test Query 3: Risk Management
```
"I'm on a 5 game losing streak, down 15% of bankroll, what should I do?"

Risk Agent → Triggers tilt protocol and adjusts limits
Sports Agent → Suggests highest confidence plays only
Odds Agent → Focuses on highest EV opportunities only
```

---

## 📊 MONITORING DASHBOARD

Once deployed, you can monitor all three agents:

```python
# API Endpoints to check status
GET /api/v1/agents/                    # List all agents
GET /api/v1/agents/odds_calculation/   # Odds agent status
GET /api/v1/agents/risk_assessment/    # Risk agent status
GET /api/v1/agents/sports_analytics/   # Sports agent status

# WebSocket for real-time updates
ws://localhost:8000/ws/agent-progress/
```

---

## 🎉 SUCCESS CRITERIA

You'll know the deployment is successful when:

1. ✅ All three agents appear in `/api/v1/agents/` listing
2. ✅ Routing correctly identifies queries for each agent:
   - "Calculate odds" → Odds Agent
   - "Assess risk" → Risk Agent  
   - "Analyze game" → Sports Agent
3. ✅ Agents can call each other through orchestration
4. ✅ WebSocket shows real-time progress for all three
5. ✅ Test calculations return accurate results
6. ✅ Integration tests pass between agents

---

## 🔥 ADVANCED: ORCHESTRATED WORKFLOW

Create a multi-agent workflow that uses all three:

```python
# In orchestrator.py
async def complete_betting_analysis(game_id, current_odds):
    # Step 1: Sports Analytics
    sports_result = await sports_agent.analyze_game(game_id)
    
    # Step 2: Odds Calculation  
    odds_result = await odds_agent.calculate_value(
        current_odds, 
        sports_result['win_probability']
    )
    
    # Step 3: Risk Assessment
    risk_result = await risk_agent.assess_bet(
        odds_result['expected_value'],
        sports_result['variance'],
        user.bankroll
    )
    
    return {
        'recommendation': risk_result['decision'],
        'confidence': sports_result['confidence'],
        'edge': odds_result['edge'],
        'stake': risk_result['stake_size']
    }
```

---

## 🎯 GO TIME!

Your three core agents are ready to build themselves in parallel! 

Open those three terminals, paste the prompts, and watch the magic happen as three specialized AI agents build themselves simultaneously into your betting platform.

The future of automated betting intelligence starts... NOW! 🚀🎲🛡️🏆

---

*Remember: These agents are designed to work together. The Odds Agent calculates, the Sports Agent predicts, and the Risk Agent protects. Together, they form an unstoppable betting intelligence system!*