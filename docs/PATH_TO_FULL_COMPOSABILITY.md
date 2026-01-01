# Path to 7/7 Full Cross-Domain Composability

**Created:** December 31, 2025 (Session 653)
**Status:** COMPLETE - 7/7 Open!
**Goal:** Enable ANY agent to work with ANY other agent in ANY system

---

## Final State: 7/7 OPEN!

| System | Status | Fix Applied |
|--------|--------|-------------|
| Hive Mind | OPEN | Native |
| Agent Conversations | OPEN | Native |
| Knowledge Flow | OPEN | Native |
| Spider Data Access | OPEN | Native |
| **Content Studio** | **OPEN** | Session 653 - debater_agents parameter |
| **Campaign Orchestrator** | **OPEN** | Session 653 - Agent delegation |
| **Podcast Coordinator** | **OPEN** | Session 653 - run_multi_agent_debate tool |

---

## Wall #1: Content Studio (Lock Level: LOW)

### Current Implementation

**File:** `core/agents/autonomous_content_studio_coordinator.py`
**Lines:** 445-447

```python
# HARDCODED imports - only these 3 agents can participate
from core.agents.content.topic_miner_agent import TopicMinerAgent
from core.agents.content.contrarian_agent import ContrarianAgent
from core.agents.content.performance_analyst_agent import PerformanceAnalystAgent
```

**Problem:** The debate participants are hardcoded at import time.

### Fix (Estimated: 15 minutes)

```python
def _run_content_debate(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Run a 3-agent debate to select the best topic."""

    # NEW: Accept configurable debaters
    debater_names = tool_input.get('debater_agents', [
        'TopicMinerAgent',
        'ContrarianAgent',
        'PerformanceAnalystAgent'
    ])

    # Use AgentRouter for dynamic agent lookup
    from core.agent_router import AgentRouter
    router = AgentRouter()

    debaters = []
    for name in debater_names:
        agent_class = router.AGENT_MAP.get(name)
        if agent_class:
            debaters.append(agent_class(user=self.user))
        else:
            logger.warning(f"Agent {name} not found in router")

    # Rest of debate logic stays the same...
```

### What Opens Up

After fix, you can:
```
"Debate content strategy with BlockchainAuditCoordinator, StockAuditCoordinator, and CTOAgent"
```

The Content Studio becomes a general-purpose multi-agent debate platform.

---

## Wall #2: Campaign Orchestrator (Lock Level: MEDIUM)

### Current Implementation

**File:** `core/agents/campaign_orchestrator_agent.py`
**Lines:** 666-688

```python
def _generate_ad_copies(self, campaign, trends: List[str]) -> List[Dict[str, Any]]:
    """Generate ad copy variations."""
    # In a full implementation, this would call ContentWriterAgent
    # For now, generate template-based variations

    templates = [
        f"Discover {campaign.product_name} - {campaign.product_description[:100]}...",
        f"Looking for the best {campaign.product_name}? We've got you covered...",
        # ... more templates
    ]
```

**Problem:** Uses hardcoded templates instead of calling specialist agents.

### Fix (Estimated: 45 minutes)

```python
def _generate_ad_copies(self, campaign, trends: List[str]) -> List[Dict[str, Any]]:
    """Generate ad copy variations using ContentWriterAgent."""
    from core.agent_router import AgentRouter
    router = AgentRouter()

    content_writer = router.get_agent('ContentWriterAgent', user=self.user)

    task = f"""Write 5 compelling ad copy variations for:
    Product: {campaign.product_name}
    Description: {campaign.product_description}
    Target Market: {campaign.target_market}
    Trending Topics: {', '.join(trends[:5])}

    Format each as: variant (A-E), text, tone, keywords"""

    result = content_writer.execute(
        task=task,
        context={'campaign_id': str(campaign.id)},
        scifi_context={},
        spider_context={'trends': trends}
    )

    # Parse agent output into structured format
    return self._parse_ad_copies(result.message)


def _generate_social_posts(self, campaign, trends: List[str]) -> Dict[str, List[str]]:
    """Generate social posts using SocialMediaAgent."""
    from core.agent_router import AgentRouter
    router = AgentRouter()

    social_agent = router.get_agent('SocialMediaAgent', user=self.user)

    task = f"""Create social media posts for {campaign.product_name}:
    - 2 Facebook posts (longer form)
    - 2 Instagram posts (with hashtags)
    - 2 Twitter posts (punchy, under 280 chars)

    Target: {campaign.target_market}
    Trends: {', '.join(trends[:5])}"""

    result = social_agent.execute(task, {}, {}, {'trends': trends})
    return self._parse_social_posts(result.message)
```

### What Opens Up

After fix, campaigns can use:
- `ContentWriterAgent` for ad copy
- `SocialMediaAgent` for social posts
- `ImageAgent` for campaign visuals
- `ResearchAgent` instead of SmartTrendingService
- ANY agent for specialized campaign needs

---

## Wall #3: Podcast Coordinator (Lock Level: HIGH)

### Current Implementation

**File:** `core/agents/podcast/podcast_coordinator_agent.py`

**System Prompt (lines 84-88):**
```python
## Voice Assignments
- HOST: Antoni (warm, professional narrator)
- ADVOCATE: Rachel (enthusiastic, optimistic)
- SKEPTIC: Clyde (authoritative, critical)
- ANALYST: Paul (calm, data-driven)
```

**Execute method (lines 198-252):**
```python
def execute(self, task: str, context: Dict, ...):
    # Calls GPT directly with hardcoded system prompt
    # GPT generates entire script with predefined roles
    # No actual agent calls happen
```

**Problem:** The entire podcast is GPT-simulated. Real debate agents (DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent) are never called.

### Fix (Estimated: 2 hours)

This is a significant refactor. The agent needs to:

1. Accept participant agent IDs as parameter
2. Use AgentRouter to instantiate them
3. Run a multi-turn conversation loop
4. Call each agent's execute() for their turns
5. Compile transcript into podcast format

```python
class PodcastCoordinatorAgent(BaseAgent):
    """Orchestrates real multi-agent podcasts."""

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any],
        participant_agents: List[str] = None,  # NEW PARAMETER
        rounds: int = 3
    ) -> AgentResult:
        """Execute podcast with configurable agent participants."""

        # Default to existing debate agents
        if participant_agents is None:
            participant_agents = [
                'ModeratorAgent',      # HOST role
                'DebateAdvocateAgent', # ADVOCATE role
                'DebateSkepticAgent',  # SKEPTIC role
            ]

        from core.agent_router import AgentRouter
        router = AgentRouter()

        # Instantiate participant agents
        participants = []
        for agent_name in participant_agents:
            agent_class = router.AGENT_MAP.get(agent_name)
            if agent_class:
                participants.append({
                    'name': agent_name,
                    'agent': agent_class(user=self.user),
                    'role': self._infer_role(agent_name)  # HOST, ADVOCATE, SKEPTIC, etc.
                })

        # Extract topic from task
        topic = self._extract_topic(task)

        # Run the actual debate
        transcript = []
        conversation_history = []

        for round_num in range(rounds):
            for participant in participants:
                agent = participant['agent']
                role = participant['role']

                # Build turn prompt with conversation history
                turn_task = f"""
                You are participating in a podcast debate about: {topic}
                Your role: {role}
                Round: {round_num + 1}/{rounds}

                Previous discussion:
                {self._format_history(conversation_history[-6:])}

                Provide your perspective in 2-3 sentences. Be direct and engaging.
                """

                # ACTUALLY CALL THE AGENT
                result = agent.execute(
                    task=turn_task,
                    context={'topic': topic, 'round': round_num},
                    scifi_context=scifi_context,
                    spider_context=spider_context
                )

                turn = {
                    'speaker': participant['name'],
                    'role': role,
                    'text': result.message,
                    'round': round_num
                }
                transcript.append(turn)
                conversation_history.append(turn)

        # Convert transcript to podcast script format
        script = self._compile_script(topic, transcript)

        return AgentResult(
            success=True,
            message=f"Podcast created with {len(participants)} agents over {rounds} rounds",
            data={
                'transcript': transcript,
                'script': script,
                'participants': [p['name'] for p in participants]
            }
        )

    def _infer_role(self, agent_name: str) -> str:
        """Infer podcast role from agent name/type."""
        name_lower = agent_name.lower()
        if 'moderator' in name_lower or 'coordinator' in name_lower:
            return 'HOST'
        elif 'advocate' in name_lower or 'bull' in name_lower:
            return 'ADVOCATE'
        elif 'skeptic' in name_lower or 'bear' in name_lower or 'contrarian' in name_lower:
            return 'SKEPTIC'
        else:
            return 'EXPERT'
```

### What Opens Up

After fix, you can:
```
"Create a podcast with BlockchainAuditCoordinator and StockAuditCoordinator debating crypto vs traditional investing"

"Generate a debate between LegalDocDrafterAgent and CTOAgent about AI regulation"

"Make a podcast where ResearchAgent, TrendAnalysisAgent, and MarketIntelligenceAgent discuss market trends"
```

---

## Implementation Priority

| Fix | Effort | Impact | Priority |
|-----|--------|--------|----------|
| Content Studio | 15 min | Medium | 1 (warmup) |
| Campaign Orchestrator | 45 min | Medium | 2 |
| Podcast Coordinator | 2 hours | HIGH | 3 |

**Recommended Order:** Content Studio → Campaign → Podcast

---

## What 7/7 Looks Like

### Before (4/7)
- Hive Mind pairs agents randomly ✅
- Conversations happen between any agents ✅
- Knowledge flows freely ✅
- Spiders serve all agents ✅
- Podcasts use fixed roles ❌
- Campaigns use templates ❌
- Content Studio uses 3 hardcoded agents ❌

### After (7/7)
- Hive Mind pairs agents randomly ✅
- Conversations happen between any agents ✅
- Knowledge flows freely ✅
- Spiders serve all agents ✅
- **Podcasts use any agents you specify** ✅
- **Campaigns delegate to specialist agents** ✅
- **Content Studio debates with any 3 agents** ✅

---

## Example Workflows After 7/7

### Cross-Domain Podcast
```
User: "Create a podcast where BlockchainAuditCoordinator, StockAuditCoordinator,
       and ArbitrageDetector debate crypto vs traditional markets"

System: Instantiates all 3 agents, runs 3-round debate, each agent uses their
        real knowledge and personality, produces transcript → script → audio
```

### Multi-Agent Campaign
```
User: "Create a campaign for my AI startup"

System:
  1. ResearchAgent analyzes market trends
  2. ContentWriterAgent generates ad copy
  3. SocialMediaAgent creates platform-specific posts
  4. ImageAgent generates campaign visuals
  5. SEOOptimizerAgent optimizes for search
```

### Dynamic Content Debate
```
User: "Have the blockchain and stock teams debate which market is safer"

System:
  Debaters: [BlockchainAuditCoordinator, WhaleWatcherAgent, StockAuditCoordinator]
  Runs 3-agent debate with real agent knowledge
  Produces synthesized content strategy
```

---

## Quick Reference: Key Files

| Wall | File | Lines to Modify |
|------|------|-----------------|
| Content Studio | `core/agents/autonomous_content_studio_coordinator.py` | 445-520 |
| Campaign | `core/agents/campaign_orchestrator_agent.py` | 666-750 |
| Podcast | `core/agents/podcast/podcast_coordinator_agent.py` | 198-350 |

---

## Verification Commands After Fix

```bash
# Test Content Studio with custom debaters
.venv/bin/python manage.py shell -c "
from core.agents.autonomous_content_studio_coordinator import AutonomousContentStudioCoordinator
agent = AutonomousContentStudioCoordinator()
result = agent._run_content_debate({
    'channel_id': 1,
    'debater_agents': ['CTOAgent', 'BlockchainAuditCoordinator', 'StockAuditCoordinator']
})
print(result)
"

# Test Podcast with any agents
.venv/bin/python manage.py shell -c "
from core.agents.podcast.podcast_coordinator_agent import PodcastCoordinatorAgent
agent = PodcastCoordinatorAgent()
result = agent.execute(
    task='Debate crypto vs stocks',
    context={},
    scifi_context={},
    spider_context={},
    participant_agents=['BlockchainAuditCoordinator', 'StockAuditCoordinator', 'ArbitrageDetector']
)
print(f'Participants: {result.data[\"participants\"]}')
"
```

---

**Total Time to 7/7: ~3 hours of focused work**
