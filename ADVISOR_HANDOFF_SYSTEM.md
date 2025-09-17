# Action Plan → Advisor → Team Formation System

## Overview
Complete implementation of the Action Plan to Advisor handoff system with team formation and Neural Orchestra visualization.

## System Components

### 1. Backend Infrastructure

#### Action Plan Advisor Handoff (`intelligence/action_plan_advisor_handoff.py`)
- **Purpose**: Core system for advisor selection and team formation
- **Key Classes**:
  - `AdvisorReview`: Dataclass containing advisor feedback
  - `TeamFormation`: Dataclass for assembled AI team
  - `ActionPlanAdvisorHandoff`: Main orchestration class
- **Features**:
  - Domain-based advisor selection (25 advisors)
  - Team formation with 8-12 specialized agents
  - Success probability calculation
  - Budget estimation
  - Immediate action recommendations

#### Action Plan Orchestrator (`intelligence/action_plan_orchestrator.py`)
- **Purpose**: Orchestrates complete flow from plan → advisor → team → execution
- **Workflow Stages**:
  1. Format the action plan
  2. Hand off to advisor for review
  3. Form execution team
  4. Begin execution (ready for implementation)

#### Unified WebSocket Hub (`core/unified_hub.py`)
- **Purpose**: Central WebSocket hub for real-time communication
- **Key Methods**:
  - `send_plan_review()`: Sends advisor review to Neural Orchestra
  - `send_income_builder_data()`: Provides real-time updates
- **Integration**: Connected to System Integration Bridge

### 2. Frontend Components

#### Income Builder (`frontend/src/components/IncomeBuilder.tsx`)
- **New Features**:
  - "Hand Off to Advisor" button for completed plans
  - localStorage persistence for action plans
  - Automatic redirect to Neural Orchestra with plan ID
  - Recovery mechanism for lost plans

#### Neural Orchestra (`frontend/src/components/NeuralOrchestra.tsx`)
- **Plan Review Display**:
  - Prominent card at top of page
  - Shows advisor name, success probability, budget
  - Lists immediate actions (up to 5)
  - Displays assembled team
  - "Start Execution" button for next steps
- **WebSocket Integration**:
  - Receives plan review via WebSocket
  - Updates visualization with team connections
  - Real-time advisor-agent collaboration display

### 3. WebSocket Communication

#### Routes (`core/routing.py`)
- `/ws/neural-orchestra/` → UnifiedWebSocketHub
- `/ws/income-builder/` → UnifiedWebSocketHub
- Proper ASGI configuration with Daphne

#### Message Flow
```
Income Builder → WebSocket → UnifiedHub → Advisor Handoff → Team Formation
                                         ↓
Neural Orchestra ← WebSocket ← UnifiedHub (plan_review message)
```

## Key Features Implemented

### 1. Advisor Selection Algorithm
```python
# Domain mapping to appropriate advisors
domain_advisors = {
    'ai_automation': ['sal_khan_advisor', 'balaji_srinivasan_advisor'],
    'content_creation': ['gary_vaynerchuk_advisor', 'ann_handley_advisor'],
    'web3': ['chris_dixon_advisor', 'linda_xie_advisor'],
    # ... 25 advisors total
}
```

### 2. Team Formation Logic
- Lead agent: Orchestrator
- 3-5 core agents based on plan requirements
- 3-5 specialist agents for specific tasks
- Total team size: 8-12 agents

### 3. Data Persistence
- localStorage for action plans
- Backend sync via API
- Recovery scripts for data restoration

### 4. Real-Time Updates
- WebSocket for instant communication
- API fallback for reliability
- Heartbeat mechanism for connection health

## Fixed Issues

### Backend Fixes
1. **TypeError: non-default argument follows default argument**
   - Solution: Used `field(default_factory=list)` for dataclass list fields

2. **timezone.utc AttributeError**
   - Solution: Changed to `django.utils.timezone`

3. **WebSocket 404 errors**
   - Solution: Proper routing configuration in `core/routing.py`

### Frontend Fixes
1. **Plans disappearing on refresh**
   - Solution: Implemented proper localStorage with `savePlans()` helper

2. **Advisor button not showing**
   - Solution: Display button for completed plans only

3. **Plan review card not visible**
   - Solution: Moved to top of Neural Orchestra page with prominent styling

## Data Recovery Scripts

### `recover_recent_plans.js`
- Restores recently completed action plans
- Includes advisor reviews and team formations
- Run in browser console at Income Builder page

### `restore_plans.js`
- General recovery tool for lost plans
- Checks localStorage and sessionStorage
- Provides debugging functions

## Current Status

✅ **Working Features**:
- Action Plan creation and completion
- Advisor selection and review generation
- Team formation with specialized agents
- WebSocket real-time communication
- Frontend display in Neural Orchestra
- Data persistence and recovery

🔄 **Ready for Next Phase**:
- Execution system implementation
- Spider network integration
- Revenue tracking connection
- ML pipeline activation
- Multi-agent orchestration

## Testing

### WebSocket Connection Test
```python
# test_ws_connection.py
- Tests Neural Orchestra WebSocket
- Verifies plan review handler
- Confirms data flow
```

### Manual Testing
1. Create Action Plan in Income Builder
2. Complete all steps
3. Click "Hand Off to Advisor"
4. Verify redirect to Neural Orchestra
5. Confirm plan review display

## Next Steps (For Next Session)

1. **Connect Execution System**
   - Wire up "Start Execution" button
   - Implement agent task distribution
   - Track execution progress

2. **Spider Integration**
   - Connect 1,770 spiders to agents
   - Establish data pipelines
   - Implement routing protocols

3. **Revenue Pipeline**
   - Connect Income Builder to Revenue Dashboard
   - Track actual earnings
   - Implement payment processing

4. **ML Enhancement**
   - Activate ML Pipeline
   - Connect to Apple MLX
   - Implement learning loops

5. **Complete System Integration**
   - All 7 platform components talking
   - Real-time data flow throughout
   - Production deployment readiness

## Environment Requirements

- Django with Channels
- Redis for channel layer
- Daphne ASGI server
- React with TypeScript
- WebSocket support in browser

## Notes for Next Session

The system is at a crucial point where:
- Frontend and backend are properly connected
- WebSocket communication is working
- Advisor handoff system is complete
- Team formation is operational

Next session should focus on:
- Connecting the remaining AI components
- Implementing actual execution
- Wiring up the spider network
- Activating revenue generation

Enjoy your walk with the dog! 🐕