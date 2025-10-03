# Odds Sports Calculation Agent - Implementation Guide

## Quick Start: Using This System Prompt with Claude Code

### Step 1: Copy the System Prompt
Copy the entire contents of `ODDS_AGENT_SYSTEM_PROMPT.md` to use as your Claude Code assistant's instructions.

### Step 2: Claude Code Commands for Implementation

```bash
# Initialize Claude Code with the Odds Agent prompt
claude --prompt-file ./documentation/ODDS_AGENT_SYSTEM_PROMPT.md

# Or paste the prompt directly when starting a new Claude Code session
```

### Step 3: Agent Implementation Tasks for Claude Code

Tell your Claude Code assistant to:

1. **Create the Agent Template Entry**
   - Add to `/backend/agents/templates.py`
   - Use the specialization: 'odds_calculation'
   
2. **Update Django Models**
   - Add 'odds_calculation' to SPECIALIZATIONS in `/backend/agents/models.py`
   - Create migration: `python manage.py makemigrations`

3. **Create Required Tools**
   - Implement odds_calculator tool
   - Implement arbitrage_scanner tool
   - Add probability_engine tool
   - Create market_analyzer tool

4. **Update Routing Logic**
   - Add odds-specific intent patterns to `/backend/agents/routing.py`
   - Include betting-specific keywords in routing index

5. **Create API Endpoints**
   ```python
   # Specific endpoints for odds calculations
   /api/v1/odds/convert/
   /api/v1/odds/calculate-ev/
   /api/v1/odds/arbitrage/
   /api/v1/odds/kelly/
   ```

6. **Implement Core Functions**
   Create `/backend/agents/tools/odds_calculator.py` with:
   - Odds conversion functions
   - EV calculation
   - Kelly Criterion implementation
   - Arbitrage detection
   - Vig/juice calculations

7. **Add WebSocket Support**
   For real-time odds updates in `/backend/api/consumers.py`

8. **Create Tests**
   `/backend/agents/tests/test_odds_agent.py`

### Step 4: Sample Claude Code Session

```
You: Create the sports Odds Calculation Agent with the system prompt I've provided. Start by implementing the agent template and core calculation functions.

Claude Code: I'll create the Odds Calculation Agent for your betting platform. Let me start by:
1. Adding the agent to templates.py
2. Creating the odds calculation tools
3. Setting up the routing logic
[... Claude Code will handle the implementation ...]
```

### Step 5: Deployment Commands

```bash
# After Claude Code creates the agent
cd /Users/donkeyking/development/donkey-betz-agent-orchestra/backend

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Initialize the new agent
python manage.py shell
>>> from agents.models import AgentTemplate
>>> from agents.templates import AGENT_TEMPLATES
>>> template = AGENT_TEMPLATES['odds_calculation']
>>> AgentTemplate.objects.create(**template)

# Test the agent
python manage.py test agents.tests.test_odds_agent

# Start the services
make dev
```

## Key Implementation Points for Claude Code

### 1. Agent Template Structure
```python
'odds_calculation': {
    'name': 'Odds Calculation Agent',
    'description': 'Betting odds calculation and probability management specialist',
    'specialization': 'odds_calculation',
    'capabilities': [
        'Odds format conversion',
        'Expected value calculations',
        'Kelly Criterion optimization',
        'Arbitrage opportunity detection',
        'Vig/juice analysis',
        'Complex parlay calculations',
        'Live odds adjustments',
        'Market efficiency analysis'
    ],
    'required_tools': [
        'odds_calculator',
        'arbitrage_scanner', 
        'probability_engine',
        'market_analyzer'
    ],
    'system_prompt': """[PASTE THE FULL SYSTEM PROMPT HERE]""",
    'personality_traits': {
        'style': 'precise',
        'tone': 'analytical',
        'detail_level': 'mathematical',
    },
    'routing_keywords': [
        'odds', 'probability', 'betting', 'spread', 'line',
        'handicap', 'parlay', 'arbitrage', 'kelly', 'expected value',
        'vig', 'juice', 'decimal', 'fractional', 'american',
        'moneyline', 'accumulator', 'stake', 'bankroll', 'ev'
    ],
    'llm_config': {
        'temperature': 0.2,  # Low for mathematical precision
        'max_tokens': 1500,
        'model': 'gpt-4'
    }
}
```

### 2. Core Calculation Functions to Implement

```python
# /backend/agents/tools/odds_calculator.py

class OddsCalculator:
    @staticmethod
    def decimal_to_american(decimal_odds: float) -> int:
        """Convert decimal odds to American format"""
        pass
    
    @staticmethod
    def american_to_decimal(american_odds: int) -> float:
        """Convert American odds to decimal format"""
        pass
    
    @staticmethod
    def calculate_implied_probability(odds: float, format: str) -> float:
        """Calculate implied probability from any odds format"""
        pass
    
    @staticmethod
    def calculate_expected_value(
        odds: float, 
        true_probability: float, 
        stake: float
    ) -> float:
        """Calculate expected value of a bet"""
        pass
    
    @staticmethod
    def kelly_criterion(
        odds: float,
        probability: float,
        kelly_fraction: float = 0.25
    ) -> float:
        """Calculate optimal bet size using Kelly Criterion"""
        pass
    
    @staticmethod
    def detect_arbitrage(odds_list: List[float]) -> Dict:
        """Detect arbitrage opportunities across markets"""
        pass
```

### 3. Integration with Existing System

The Odds Calculation Agent should integrate with:
- **Risk Assessment Agent**: For bankroll management
- **Sports Analytics Agent**: For probability inputs
- **Data Analytics Agent**: For historical performance
- **Monitoring Agent**: For real-time odds tracking

### 4. Testing Requirements

Create comprehensive tests for:
- All odds conversion formats
- EV calculations with various inputs
- Kelly Criterion edge cases
- Arbitrage detection accuracy
- API endpoint responses
- WebSocket real-time updates

## Success Criteria

The agent is successfully deployed when:
1. ✅ Agent appears in `/api/v1/agents/` listing
2. ✅ Routing correctly identifies odds-related queries
3. ✅ All calculation functions return accurate results
4. ✅ WebSocket updates work for real-time odds
5. ✅ Integration tests pass with >95% coverage
6. ✅ Agent responds correctly to test prompts

## Sample Test Queries

Test your deployed agent with:
1. "Convert +150 to decimal odds"
2. "Calculate EV for -110 odds with 55% win probability"
3. "Find arbitrage between +120 and -105"
4. "What's the Kelly stake for 2.5 odds with 45% edge?"
5. "Remove the vig from -110/-110 market"

---

*Ready to create your Odds Calculation Agent with Claude Code!*