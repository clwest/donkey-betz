# Session 575: PA Tools Audit & Roadmap

**Date:** December 28, 2025
**Session:** 575
**Focus:** Personal Assistant Self-Awareness & Tools Gap Analysis
**Status:** Audit Complete, Implementation Pending

---

## Executive Summary

The Personal Assistant has only **2 tools** while the system offers **1,343+ API endpoints**. This represents a 0.15% coverage gap where the PA cannot access the vast intelligence, monitoring, and action capabilities that exist in the platform.

**Problem Statement:**
```
User: "What should I focus on?"
PA: "I don't have access to system status data..."

User: "Approve that decision"
PA: "I can't execute actions in the system..."

User: "What's trending?"
PA: "I can't query the spider network..."
```

The PA is effectively blind to 99.85% of the system's capabilities.

---

## Part 1: Current PA Tools (2 Total)

### Tool 1: `delegate_to_agent`

**Location:** `core/agents/personal_assistant_agent.py` (lines 455-614)

**Purpose:** Route tasks to specialized agents

**Parameters:**
- `agent_name` - Enum of 39+ agents
- `task` - Natural language task description
- `context` - Optional context object

**Supported Agents:**
- Research: ResearchAgent, TrendAnalysisAgent, CompetitorAnalysisAgent, CustomerResearchAgent
- Sports: SportsOddsAnalyst, PredictionMarketAnalyst, ArbitrageDetector
- Creation: ImageAgent, VideoAgent, AudioAgent, ThreeDAgent
- Editing: ImageEditingAgent, VideoEditingAgent
- Writing: ContentWriterAgent
- Development: CodeGeneratorAgent, CodeReviewAgent, FullStackDeveloperAgent, DevOpsAgent
- Strategy: BrandIdentityAgent, ContentStrategyAgent, SEOOptimizerAgent, SocialMediaAgent
- Executive: CTOAgent, COOAgent, CreativeDirectorAgent, MeetingCoordinatorAgent
- Specialized: LegalDocDrafterAgent, PodcastCoordinatorAgent, ResolveAgent
- Analysis: StockAuditCoordinator, BlockchainAuditCoordinator, ContentAuditAgent
- Orchestration: WorkflowAgent, AutonomousContentStudioCoordinator

**Limitation:** Generic delegation only - no direct access to agent data, status, or outputs.

---

### Tool 2: `get_sports_data`

**Location:** `core/agents/personal_assistant_agent.py` (lines 615-645)

**Purpose:** Query internal sports API for live scores and odds

**Parameters:**
- `sport` - Enum: nfl, nba, mlb, nhl, ncaaf, ncaab, soccer, ufc
- `team` - Optional team name filter

**Implementation:** Calls `/api/v1/sports/live-odds-scores/` internally

**Added:** Session 575 to fix "I can't access live sports data" responses

**Example Output:**
```
**NFL Scores:**

🔴 **LIVE:**
  Chicago Bears 21 @ San Francisco 49ers 28 (15:00 - 3rd)

✅ **FINAL:**
  New Orleans Saints 34 @ Atlanta Falcons 26 - Saints wins
  Pittsburgh Steelers 13 @ Baltimore Ravens 6 - Steelers wins
```

---

## Part 2: System Capabilities NOT Exposed to PA

### Category A: Intelligence & Monitoring (180+ endpoints)

**System Status & Health:**
| Endpoint | Purpose | PA Access |
|----------|---------|-----------|
| `/api/personal-assistant/attention-items/` | Pending decisions, failed cycles, stale concerns | Context only |
| `/api/neural-orchestra/agents/stats/` | Agent activity statistics | None |
| `/api/ecosystem/stats/` | Ecosystem statistics | None |
| `/api/collective/improvements/` | Agent improvements tracking | None |

**Agent Intelligence:**
| Endpoint | Purpose | PA Access |
|----------|---------|-----------|
| `/api/agents/` | All agents list | None |
| `/api/agents/<id>/profile/` | Individual agent profile | None |
| `/api/collaboration/performance/` | Agent performance metrics | None |
| `/api/teams/messages/<agent_id>/` | Agent-to-agent conversations | None |

**Spider Network:**
| Endpoint | Purpose | PA Access |
|----------|---------|-----------|
| `/api/spiders/priorities/` | Spider priority rankings | None |
| `/api/research/feedback/` | Research feedback metrics | None |
| Spider data by category | Topic-specific data | None |

**Business Intelligence:**
| Endpoint | Purpose | PA Access |
|----------|---------|-----------|
| `/api/opportunities/` | Opportunity pipeline | None |
| `/api/opportunities/revenue/stats/` | Revenue analytics | None |
| `/api/business-ideas/stats/` | Pipeline statistics | None |

**Betting Intelligence:**
| Endpoint | Purpose | PA Access |
|----------|---------|-----------|
| `/api/v1/betting/line-movement/` | Line movement tracking | None |
| `/api/v1/betting/movers/` | Games with significant movement | None |
| `/api/v1/odds/arbitrage/` | Arbitrage detection | None |
| `/api/v1/odds/bankroll/stats/` | Bankroll tracking | None |

---

### Category B: Action Execution (120+ endpoints)

**Boardroom Decisions:**
| Endpoint | Action | PA Access |
|----------|--------|-----------|
| `POST /api/boardroom/decisions/<id>/promote/` | Approve decision | None |
| `POST /api/boardroom/decisions/<id>/reject/` | Reject decision | None |
| `POST /api/boardroom/dreams/<id>/decide/` | Decide on dream | None |

**Project Management:**
| Endpoint | Action | PA Access |
|----------|--------|-----------|
| `POST /api/projects/create/` | Create new project | None |
| `PUT /api/projects/<id>/update/` | Update project | None |
| `POST /api/projects/<id>/learning/trigger/` | Trigger learning | None |

**Workflow Orchestration:**
| Endpoint | Action | PA Access |
|----------|--------|-----------|
| `POST /api/teams/workflows/` | Create workflow | None |
| `POST /api/teams/workflows/<id>/execute/` | Execute workflow | None |

**Content & Distribution:**
| Endpoint | Action | PA Access |
|----------|--------|-----------|
| `POST /api/distribution/content/create/` | Create distribution | None |
| `POST /api/distribution/content/<id>/publish/` | Publish content | None |

**Betting Actions:**
| Endpoint | Action | PA Access |
|----------|--------|-----------|
| `POST /api/v1/betting/place/` | Place a bet | None |
| `POST /api/v1/betting/wager/` | Log wager | None |
| `POST /api/v1/betting/arbitrage/scan/` | Scan for arbitrage | None |

---

## Part 3: Recommended Tools (Prioritized)

### HIGH PRIORITY - Implement First

#### 1. `get_system_status`

**Type:** Data Query
**Implementation Time:** 30 minutes
**Why:** Users constantly ask "what should I focus on?" and PA can't answer

**Parameters:**
```python
{
    "type": "function",
    "function": {
        "name": "get_system_status",
        "description": "Get system attention items, pending decisions, and health status",
        "parameters": {
            "type": "object",
            "properties": {
                "include_details": {
                    "type": "boolean",
                    "description": "Include detailed descriptions (default: true)"
                },
                "category": {
                    "type": "string",
                    "enum": ["all", "decisions", "health", "content", "opportunities"],
                    "description": "Filter by category"
                }
            }
        }
    }
}
```

**Implementation:**
```python
def _get_system_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Query SystemStateAggregator for attention items."""
    from core.services.system_state_aggregator import SystemStateAggregator

    aggregator = SystemStateAggregator()
    items = aggregator.get_attention_items()

    return {
        'success': True,
        'pending_decisions': items.get('boardroom_decisions', []),
        'failed_cycles': items.get('failed_cycles', []),
        'stale_concerns': items.get('stale_concerns', []),
        'overdue_channels': items.get('overdue_channels', []),
        'pending_dreams': items.get('pending_dreams', []),
        'summary': self._format_status_summary(items)
    }
```

**Use Cases:**
- "What needs my attention?"
- "System status"
- "What decisions are pending?"
- "Show me action items"

---

#### 2. `promote_boardroom_decision`

**Type:** Action
**Implementation Time:** 20 minutes
**Why:** Users see decisions in attention items but can't act on them

**Parameters:**
```python
{
    "type": "function",
    "function": {
        "name": "promote_boardroom_decision",
        "description": "Approve a pending decision from the boardroom",
        "parameters": {
            "type": "object",
            "properties": {
                "decision_id": {
                    "type": "string",
                    "description": "The UUID of the decision to approve"
                },
                "notes": {
                    "type": "string",
                    "description": "Optional approval notes"
                }
            },
            "required": ["decision_id"]
        }
    }
}
```

**Implementation:**
```python
def _promote_boardroom_decision(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Approve a pending boardroom decision."""
    import requests

    decision_id = arguments.get('decision_id')
    notes = arguments.get('notes', '')

    response = requests.post(
        f'http://localhost:8000/api/boardroom/decisions/{decision_id}/promote/',
        json={'notes': notes},
        timeout=10
    )

    if response.status_code == 200:
        return {'success': True, 'message': f'Decision {decision_id} approved'}
    return {'success': False, 'error': response.text}
```

**Use Cases:**
- "Approve that decision"
- "Yes, let's go with that"
- "Promote the pending policy"
- Click-to-execute from attention items

---

#### 3. `reject_boardroom_decision`

**Type:** Action
**Implementation Time:** 20 minutes
**Why:** Complement to promote - users need both actions

**Parameters:**
```python
{
    "type": "function",
    "function": {
        "name": "reject_boardroom_decision",
        "description": "Reject a pending decision from the boardroom",
        "parameters": {
            "type": "object",
            "properties": {
                "decision_id": {
                    "type": "string",
                    "description": "The UUID of the decision to reject"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for rejection"
                }
            },
            "required": ["decision_id", "reason"]
        }
    }
}
```

---

#### 4. `query_agent_data`

**Type:** Data Query
**Implementation Time:** 45 minutes
**Why:** Users ask "what are agents doing?" frequently

**Parameters:**
```python
{
    "type": "function",
    "function": {
        "name": "query_agent_data",
        "description": "Query agent activity, learning progress, and performance metrics",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_name": {
                    "type": "string",
                    "description": "Optional: specific agent to query"
                },
                "metric_type": {
                    "type": "string",
                    "enum": ["activity", "learning", "performance", "relationships"],
                    "description": "Type of data to retrieve"
                },
                "time_period": {
                    "type": "string",
                    "enum": ["24h", "7d", "30d"],
                    "description": "Time range for metrics"
                }
            },
            "required": ["metric_type"]
        }
    }
}
```

**Use Cases:**
- "Which agents are most active?"
- "Show me ResearchAgent's learning progress"
- "What did agents do today?"
- "Who worked on my project?"

---

#### 5. `get_spider_intelligence`

**Type:** Data Query
**Implementation Time:** 45 minutes
**Why:** Users ask "what's trending?" and PA can't query spider data

**Parameters:**
```python
{
    "type": "function",
    "function": {
        "name": "get_spider_intelligence",
        "description": "Query spider network for trending topics and fresh data",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["all", "tech", "finance", "sports", "news", "legal", "entertainment"],
                    "description": "Data category to query"
                },
                "hours": {
                    "type": "integer",
                    "description": "How many hours back to look (default: 24)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max items to return (default: 10)"
                }
            }
        }
    }
}
```

**Use Cases:**
- "What's trending in tech?"
- "Any fresh news?"
- "What are spiders finding?"
- "Show me recent financial data"

---

#### 6. `query_betting_intelligence`

**Type:** Data Query
**Implementation Time:** 45 minutes
**Why:** High-value use case - betting dashboard data should be queryable

**Parameters:**
```python
{
    "type": "function",
    "function": {
        "name": "query_betting_intelligence",
        "description": "Query betting analytics including arbitrage, bankroll, and line movement",
        "parameters": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["arbitrage", "bankroll", "line_movement", "value_bets", "summary"],
                    "description": "Type of betting data to query"
                },
                "sport": {
                    "type": "string",
                    "enum": ["nfl", "nba", "mlb", "nhl", "all"],
                    "description": "Sport to filter (optional)"
                },
                "min_edge": {
                    "type": "number",
                    "description": "Minimum edge percentage for value bets"
                }
            },
            "required": ["query_type"]
        }
    }
}
```

**Use Cases:**
- "Find arbitrage opportunities"
- "What's my bankroll status?"
- "Any value bets right now?"
- "Show line movement for NFL"

---

### MEDIUM PRIORITY - Implement After Core Tools

#### 7. `get_opportunity_pipeline`

**Purpose:** Query revenue opportunities and business pipeline

**Use Cases:**
- "Show me top opportunities"
- "What's our revenue potential?"
- "Which content is performing?"

---

#### 8. `create_project`

**Purpose:** Start new projects from conversation

**Use Cases:**
- "Create a project for [topic]"
- "Start a new research project"
- "Organize this into a project"

---

#### 9. `trigger_agent_conversation`

**Purpose:** Start agent debates on topics

**Use Cases:**
- "Have agents discuss this"
- "Get diverse perspectives on [topic]"
- "Start a debate about [issue]"

---

#### 10. `generate_workflow`

**Purpose:** Create multi-step agent workflows

**Use Cases:**
- "Create a content workflow"
- "Set up research pipeline"
- "Multi-agent collaboration on [task]"

---

#### 11. `schedule_content`

**Purpose:** Plan content distribution

**Use Cases:**
- "Publish this to Twitter and LinkedIn"
- "Schedule content for tomorrow"
- "Multi-platform distribution"

---

#### 12. `analyze_project_intelligence`

**Purpose:** Deep-dive into project-specific insights

**Use Cases:**
- "Show me project intelligence"
- "What have agents learned about this?"
- "Project deep-dive"

---

### LOW PRIORITY - Nice to Have

| Tool | Purpose |
|------|---------|
| `scan_arbitrage_opportunities` | Detailed arbitrage across bookmakers |
| `get_team_analytics` | Team performance and collaboration |
| `execute_automation` | Trigger pre-configured automations |
| `place_intelligent_bet` | Act on betting recommendations |
| `publish_content` | One-click multi-platform publishing |
| `export_project` | Generate PDFs, reports |

---

## Part 4: Implementation Plan

### Phase 1: Core Awareness (This Session or Next)

**Time Estimate:** 2-3 hours

1. Add `get_system_status` tool
   - Uses existing `SystemStateAggregator`
   - Format output for PA consumption
   - Add to tools array and handler

2. Add `promote_boardroom_decision` tool
   - Wrap existing API endpoint
   - Add confirmation message
   - Handle errors gracefully

3. Add `reject_boardroom_decision` tool
   - Complement to promote
   - Require reason for rejection

**Outcome:** PA can see system status and act on decisions

---

### Phase 2: Intelligence Queries (Sessions 576-577)

**Time Estimate:** 3-4 hours

4. Add `query_agent_data` tool
   - Aggregate multiple agent endpoints
   - Format learning curves, activity
   - Support filtering by agent/metric

5. Add `get_spider_intelligence` tool
   - Query trending data by category
   - Show data freshness
   - Support time range filtering

6. Add `query_betting_intelligence` tool
   - Arbitrage detection
   - Bankroll summary
   - Line movement analysis

**Outcome:** PA can answer "what's trending?", "what are agents doing?", "any arbitrage?"

---

### Phase 3: Action Capabilities (Sessions 578-579)

**Time Estimate:** 4-5 hours

7. Add `create_project` tool
8. Add `trigger_agent_conversation` tool
9. Add project intelligence queries
10. Add content scheduling

**Outcome:** PA can create projects, trigger conversations, schedule content

---

### Phase 4: Advanced Workflows (Sessions 580+)

**Time Estimate:** 6+ hours

11. Workflow generation
12. Multi-platform publishing
13. Automation execution
14. Advanced betting actions

**Outcome:** Full orchestration capabilities through PA

---

## Part 5: Key Files Reference

### PA Implementation Files

| File | Purpose |
|------|---------|
| `core/agents/personal_assistant_agent.py` | PA agent class, tools array, tool handlers |
| `core/agents/base_agent.py` | Base agent with date injection |
| `core/views_personal_assistant.py` | PA API endpoints |
| `core/services/system_state_aggregator.py` | Attention items service |
| `core/services/pa_intelligence_enricher.py` | Context injection service |

### Service Layers to Expose

| Service | Methods to Expose |
|---------|-------------------|
| `SystemStateAggregator` | `get_attention_items()` |
| `SpiderIntelligenceService` | `get_trending()`, `get_by_category()` |
| `CollectiveIntelligenceService` | `generate_report()`, `get_improvements()` |
| Boardroom endpoints | `promote/`, `reject/` |
| Agent endpoints | `stats/`, `activity/`, `learning/` |

### API Endpoints to Wrap

| Endpoint | Wrap As Tool |
|----------|--------------|
| `/api/boardroom/decisions/<id>/promote/` | `promote_boardroom_decision` |
| `/api/boardroom/decisions/<id>/reject/` | `reject_boardroom_decision` |
| `/api/neural-orchestra/agents/stats/` | Part of `query_agent_data` |
| `/api/spiders/priorities/` | Part of `get_spider_intelligence` |
| `/api/v1/odds/arbitrage/` | Part of `query_betting_intelligence` |

---

## Part 6: Session 575 Accomplishments

### Commits Made

```
903517c feat(Session 575): PA get_sports_data tool - instant scores from internal API
fca416e feat(Session 575): PA Self-Awareness - Real-time data capabilities
0990d5e feat(Session 574): Platform Intelligence Briefing - Omniscient PA
```

### Changes Implemented

1. **PA System Prompt Updated**
   - Added "CRITICAL: YOU HAVE REAL-TIME DATA ACCESS" section
   - Listed 77 spiders, 71 agents
   - Added sports/financial routing instructions
   - Added SportsOddsAnalyst, PredictionMarketAnalyst, ArbitrageDetector to enum

2. **Sports Query Routing**
   - Added 50+ sports patterns (team names, score keywords, leagues)
   - Routes to SportsOddsAnalyst for live odds/scores

3. **Current Date Injection**
   - All agents now receive current date/time in context
   - "Today is Saturday, December 28, 2025 at 08:02 PM MST"
   - Explicit instruction: "Do NOT say your knowledge cutoff is 2024"

4. **`get_sports_data` Tool**
   - Queries internal `/api/v1/sports/live-odds-scores/` API
   - Returns formatted scores with live/final status
   - Supports NFL, NBA, MLB, NHL, NCAAF, NCAAB, Soccer, UFC
   - Filters by team name (optional)

---

## Part 7: Next Session Priorities

### Session 576 Focus: Core Tools Implementation

1. **Implement `get_system_status` tool**
   - Use existing SystemStateAggregator
   - Format attention items for PA
   - Add to tools array

2. **Implement `promote_boardroom_decision` tool**
   - Wrap `/api/boardroom/decisions/<id>/promote/`
   - Return confirmation

3. **Implement `reject_boardroom_decision` tool**
   - Wrap `/api/boardroom/decisions/<id>/reject/`
   - Require reason

4. **Test PA with new tools**
   - "What needs my attention?" → Uses get_system_status
   - "Approve that decision" → Uses promote_boardroom_decision

5. **Update CLAUDE.md and 00-START-NEXT-SESSION.md**

---

## Part 8: Success Metrics

### Before (Session 574)

- PA had 1 tool (delegate_to_agent)
- PA said "I can't access live data" for sports
- PA couldn't see system status
- PA couldn't take actions

### After Session 575

- PA has 2 tools (added get_sports_data)
- PA returns live NFL/NBA/etc scores
- PA knows current date
- PA knows it has 77 spiders + 71 agents

### After Session 576+ (Target)

- PA has 6+ tools
- PA can query system status directly
- PA can approve/reject decisions
- PA can query agent data, spider intelligence
- PA can answer "what should I focus on?"

---

## Appendix A: Full Endpoint Audit

### Data Query Endpoints (180+)

<details>
<summary>Click to expand full list</summary>

**System & Monitoring:**
- `/api/neural-orchestra/agents/stats/`
- `/api/neural-orchestra/debug/`
- `/api/ecosystem/stats/`
- `/api/ecosystem/project-status/`
- `/api/collective/improvements/`
- `/api/collective/boost-agent/`
- `/api/dashboard-stats/`
- `/api/dashboard-api/`

**Agent Data:**
- `/api/agents/`
- `/api/agents/assigned/`
- `/api/agents/<agent_id>/profile/`
- `/api/teams/messages/<agent_id>/`
- `/api/collaboration/performance/`
- `/api/project-contributing-agents/`

**Project Intelligence:**
- `/api/projects/`
- `/api/projects/<id>/learning/`
- `/api/projects/<id>/intelligence/`
- `/api/projects/<id>/intelligence/learning/`
- `/api/projects/<id>/intelligence/conversations/`
- `/api/projects/<id>/intelligence/dreams/`
- `/api/projects/<id>/intelligence/boardroom/`
- `/api/projects/<id>/intelligence/spiders/`

**Business:**
- `/api/business-ideas/list/`
- `/api/business-ideas/stats/`
- `/api/opportunities/`
- `/api/opportunities/stats/`
- `/api/opportunities/revenue/stats/`

**Betting:**
- `/api/v1/sports/live-odds/`
- `/api/v1/sports/live-odds-scores/`
- `/api/v1/betting/line-movement/`
- `/api/v1/betting/movers/`
- `/api/v1/betting/stats/`
- `/api/v1/betting/recent/`
- `/api/v1/odds/markets/`
- `/api/v1/odds/bankroll/stats/`
- `/api/v1/sports/betting-intelligence/`
- `/api/v1/odds/arbitrage/`

</details>

### Action Endpoints (120+)

<details>
<summary>Click to expand full list</summary>

**Boardroom:**
- `POST /api/boardroom/decisions/<id>/promote/`
- `POST /api/boardroom/decisions/<id>/reject/`
- `POST /api/boardroom/dreams/<id>/decide/`

**Projects:**
- `POST /api/projects/create/`
- `POST /api/projects/from-research/`
- `PUT /api/projects/<id>/update/`
- `DELETE /api/projects/<id>/delete/`
- `POST /api/projects/<id>/learning/trigger/`
- `POST /api/projects/<id>/intelligence/conversations/trigger/`
- `POST /api/projects/<id>/intelligence/spiders/refresh/`

**Workflows:**
- `POST /api/teams/workflows/`
- `POST /api/teams/workflows/<id>/execute/`
- `POST /api/teams/workflows/<id>/run/`

**Content:**
- `POST /api/distribution/content/create/`
- `POST /api/distribution/content/<id>/publish/`

**Betting:**
- `POST /api/v1/betting/place/`
- `POST /api/v1/betting/wager/`
- `POST /api/v1/betting/wagers/<id>/settle/`
- `POST /api/v1/betting/arbitrage/scan/`

**Automation:**
- `POST /api/proactive/check/`
- `POST /api/proactive/alerts/create/`
- `POST /api/proactive/automations/create/`
- `POST /api/proactive/automations/<id>/execute/`

</details>

---

## Appendix B: Tool Implementation Template

```python
# Add to tools array in personal_assistant_agent.py
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": """Description of what the tool does.
Use this for:
- Use case 1
- Use case 2""",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    }
}

# Add handler in _execute_tool_call method
if tool_name == "tool_name":
    return self._tool_name_handler(arguments)

# Implement handler method
def _tool_name_handler(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handler implementation."""
    try:
        # Implementation
        return {'success': True, 'data': result}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

---

**End of Session 575 Handoff Document**
