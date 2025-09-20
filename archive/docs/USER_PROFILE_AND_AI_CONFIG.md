# User Profile, AI Configuration & Command Control System

## 🎯 Unified User-AI Integration Architecture

This document consolidates the User Profile system, AI Configuration, and Command & Control mechanisms that work together to create a personalized, intelligent platform experience.

## 1. User Profile System Architecture

### Current User Model
**Location:** `/persistence/models.py` - `UnifiedUser`
**Status:** Basic authentication only - needs extension

### Required Profile Extensions
```python
class UnifiedUser(models.Model):
    # Existing fields
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)

    # NEEDED: Professional Profile
    skills = JSONField(default=list)  # ["Python", "React", "ML"]
    experience_years = models.IntegerField(default=0)
    current_role = models.CharField(max_length=255, blank=True)
    industries = JSONField(default=list)  # ["Tech", "Finance"]

    # NEEDED: Work Preferences
    job_preferences = JSONField(default=dict)
    # {
    #   "remote": true,
    #   "contract": true,
    #   "full_time": false,
    #   "hourly_rate_min": 100,
    #   "salary_min": 120000
    # }

    # NEEDED: AI Agent Configuration
    assigned_agents = JSONField(default=list)  # Agent IDs
    ai_preferences = JSONField(default=dict)
    # {
    #   "llm_model": "gpt-5-mini",
    #   "reasoning_level": "medium",
    #   "automation_level": "semi-auto"
    # }

    # NEEDED: Documents & Credentials
    resume = models.FileField(upload_to='resumes/', blank=True)
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
```

### Profile Completion Tracking
```python
class UserProfileCompletion(models.Model):
    user = models.OneToOneField(UnifiedUser)
    skills_completed = models.BooleanField(default=False)
    experience_completed = models.BooleanField(default=False)
    preferences_completed = models.BooleanField(default=False)
    documents_completed = models.BooleanField(default=False)

    @property
    def completion_percentage(self):
        fields = [
            self.skills_completed,
            self.experience_completed,
            self.preferences_completed,
            self.documents_completed
        ]
        return (sum(fields) / len(fields)) * 100
```

## 2. AI Configuration System

### User-Specific AI Settings
**Integration with GPT-5 Models** (per GPT-5_CONFIG_UPDATE.md)

```python
class UserAIConfiguration(models.Model):
    user = models.OneToOneField(UnifiedUser)

    # Model Selection (GPT-5 tier based on user needs)
    default_model = models.CharField(
        max_length=50,
        choices=[
            ('gpt-5-nano', 'Fast & Economical'),  # $0.05/$0.40
            ('gpt-5-mini', 'Balanced'),           # $0.25/$2.00
            ('gpt-5', 'Maximum Intelligence'),    # $1.25/$10.00
        ],
        default='gpt-5-mini'
    )

    # Reasoning Configuration
    reasoning_level = models.CharField(
        max_length=20,
        choices=[
            ('minimal', 'Quick responses'),
            ('low', 'Basic reasoning'),
            ('medium', 'Standard analysis'),
            ('high', 'Deep reasoning')
        ],
        default='medium'
    )

    # Automation Preferences
    automation_level = models.CharField(
        max_length=20,
        choices=[
            ('manual', 'I approve everything'),
            ('semi-auto', 'Notify me of actions'),
            ('auto', 'Act on my behalf')
        ],
        default='semi-auto'
    )

    # Cost Controls
    daily_token_limit = models.IntegerField(default=100000)
    monthly_spending_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.00
    )

    # Memory Preferences
    memory_retention_days = models.IntegerField(default=90)
    share_memory_across_agents = models.BooleanField(default=True)
```

### Agent Assignment & Configuration
```python
class UserAgentAssignment(models.Model):
    user = models.ForeignKey(UnifiedUser)
    agent_name = models.CharField(max_length=100)
    agent_type = models.CharField(max_length=50)  # income, advisor, analyst

    # Agent-specific overrides
    custom_model = models.CharField(max_length=50, blank=True)
    custom_instructions = models.TextField(blank=True)

    # Permissions
    can_execute_actions = models.BooleanField(default=False)
    can_spend_tokens = models.BooleanField(default=True)
    daily_action_limit = models.IntegerField(default=10)

    # Performance tracking
    tasks_completed = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    last_active = models.DateTimeField(auto_now=True)
```

## 3. Command & Control System

### Central Command Hub
**Purpose:** Orchestrate user interactions across all system components

```python
class UserCommandCenter:
    """Central hub for user-specific command and control"""

    def __init__(self, user: UnifiedUser):
        self.user = user
        self.memory_manager = UnifiedMemoryManager()
        self.agent_orchestrator = AgentOrchestrator()
        self.profile_manager = ProfileManager(user)

    def process_user_intent(self, intent: str) -> dict:
        """Route user intent to appropriate system"""
        context = self.gather_user_context()

        # Determine action type
        if self.is_profile_update(intent):
            return self.profile_manager.update_from_intent(intent)
        elif self.is_opportunity_search(intent):
            return self.route_to_opportunity_agents(intent, context)
        elif self.is_application_action(intent):
            return self.execute_application_workflow(intent, context)
        else:
            return self.personal_assistant.respond(intent, context)

    def gather_user_context(self) -> dict:
        """Aggregate all user context for decision making"""
        return {
            'profile': self.profile_manager.get_complete_profile(),
            'preferences': self.user.ai_preferences,
            'recent_activities': self.memory_manager.get_recent_memories(),
            'active_agents': self.get_active_agents(),
            'current_opportunities': self.get_tracked_opportunities()
        }

    def route_to_opportunity_agents(self, intent: str, context: dict):
        """Intelligent routing based on user profile and preferences"""

        # Select agents based on user skills and preferences
        relevant_agents = self.select_relevant_agents(context)

        # Orchestrate multi-agent collaboration
        results = self.agent_orchestrator.collaborate(
            agents=relevant_agents,
            task=intent,
            user_context=context
        )

        return self.format_opportunity_results(results)
```

### WebSocket Command Protocol
```javascript
// Frontend command structure
class CommandProtocol {
    // User profile commands
    static updateProfile(data) {
        return {
            type: 'PROFILE_UPDATE',
            payload: data,
            auth: getAuthToken()
        };
    }

    // AI configuration commands
    static configureAI(settings) {
        return {
            type: 'AI_CONFIG',
            payload: {
                model: settings.model,
                reasoning: settings.reasoning,
                automation: settings.automation
            }
        };
    }

    // Agent control commands
    static controlAgent(agentId, action) {
        return {
            type: 'AGENT_CONTROL',
            payload: {
                agent_id: agentId,
                action: action,  // 'start', 'stop', 'configure'
                params: {}
            }
        };
    }

    // Opportunity commands
    static opportunityAction(oppId, action) {
        return {
            type: 'OPPORTUNITY_ACTION',
            payload: {
                opportunity_id: oppId,
                action: action,  // 'save', 'apply', 'dismiss'
                user_context: getUserContext()
            }
        };
    }
}
```

### Backend Command Handler
```python
# /intelligence/consumers.py
class UnifiedCommandConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        data = json.loads(text_data)
        command_type = data.get('type')

        # Route to appropriate handler
        handlers = {
            'PROFILE_UPDATE': self.handle_profile_update,
            'AI_CONFIG': self.handle_ai_config,
            'AGENT_CONTROL': self.handle_agent_control,
            'OPPORTUNITY_ACTION': self.handle_opportunity_action,
        }

        handler = handlers.get(command_type)
        if handler:
            result = await handler(data['payload'])
            await self.send_response(result)

    async def handle_profile_update(self, payload):
        """Update user profile and propagate to agents"""
        user = self.scope['user']
        profile_manager = ProfileManager(user)

        # Update profile
        updated_fields = profile_manager.update(**payload)

        # Notify relevant agents
        await self.notify_agents_of_profile_change(updated_fields)

        # Refresh opportunity recommendations
        await self.trigger_opportunity_refresh()

        return {'status': 'success', 'updated': updated_fields}
```

## 4. Integration Flow

### User Onboarding & Profile Setup
```
1. New User Registration
   ↓
2. AI Configuration Wizard
   - Select preferred AI model (cost vs intelligence)
   - Set automation preferences
   - Configure spending limits
   ↓
3. Profile Interview (via Personal Assistant)
   - Collect skills via conversational AI
   - Understand work preferences
   - Set income goals
   ↓
4. Agent Assignment
   - Auto-assign relevant agents based on profile
   - Configure agent permissions
   - Set agent-specific AI models
   ↓
5. Initial Opportunity Scan
   - Agents search based on profile
   - Present personalized results
```

### Real-Time Profile Adaptation
```python
class ProfileAdaptationEngine:
    """Learn and adapt user profile from interactions"""

    def observe_user_action(self, action_type: str, data: dict):
        """Track user actions to refine profile"""

        if action_type == 'opportunity_viewed':
            self.learn_preferences_from_view(data)
        elif action_type == 'opportunity_applied':
            self.strengthen_skill_confidence(data)
        elif action_type == 'opportunity_dismissed':
            self.adjust_preferences(data)

    def learn_preferences_from_view(self, opportunity_data):
        """Infer preferences from what user clicks on"""
        # Track: rate ranges, technologies, companies, remote vs onsite

    def strengthen_skill_confidence(self, application_data):
        """User applying confirms they have these skills"""
        # Increase confidence score for related skills

    def adjust_preferences(self, dismissed_data):
        """Learn what user doesn't want"""
        # Negative signals to filter future results
```

## 5. Frontend Integration Points

### Profile Management Component
```typescript
// /frontend/src/components/profile/ProfileManager.tsx
interface UserProfile {
    // Basic Info
    username: string;
    email: string;

    // Professional Profile
    skills: Skill[];
    experience: Experience[];
    preferences: WorkPreferences;

    // AI Configuration
    aiSettings: {
        model: 'gpt-5' | 'gpt-5-mini' | 'gpt-5-nano';
        reasoning: 'minimal' | 'low' | 'medium' | 'high';
        automation: 'manual' | 'semi-auto' | 'auto';
    };

    // Agent Assignments
    agents: AgentAssignment[];
}

class ProfileManager extends React.Component {
    updateProfile = async (updates: Partial<UserProfile>) => {
        // Update local state
        this.setState({profile: {...this.state.profile, ...updates}});

        // Send to backend
        await apiClient.put('/api/profile/extended/', updates);

        // Notify OpportunitiesHub of profile changes
        this.props.onProfileUpdate(updates);
    }

    configureAI = async (settings: AISettings) => {
        await apiClient.post('/api/ai/configure/', settings);

        // Update agent configurations
        await this.reconfigureAgents(settings);
    }
}
```

### Command Execution Interface
```typescript
// /frontend/src/services/commandService.ts
class CommandService {
    private ws: WebSocket;
    private commandQueue: Command[] = [];

    executeCommand(command: Command): Promise<CommandResult> {
        return new Promise((resolve, reject) => {
            const commandId = generateId();

            this.ws.send(JSON.stringify({
                id: commandId,
                ...command,
                timestamp: Date.now(),
                user_context: this.getUserContext()
            }));

            // Track for response
            this.pendingCommands[commandId] = {resolve, reject};
        });
    }

    // High-level command methods
    async updateSkills(skills: string[]) {
        return this.executeCommand({
            type: 'PROFILE_UPDATE',
            payload: {skills}
        });
    }

    async quickApply(opportunityId: string) {
        return this.executeCommand({
            type: 'OPPORTUNITY_ACTION',
            payload: {
                opportunity_id: opportunityId,
                action: 'quick_apply',
                resume_id: this.getCurrentResumeId()
            }
        });
    }
}
```

## 6. Database Schema Requirements

### New Tables Needed
```sql
-- User AI Configuration
CREATE TABLE user_ai_configuration (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES unified_users(id),
    default_model VARCHAR(50),
    reasoning_level VARCHAR(20),
    automation_level VARCHAR(20),
    daily_token_limit INTEGER,
    monthly_spending_limit DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- User Agent Assignments
CREATE TABLE user_agent_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES unified_users(id),
    agent_name VARCHAR(100),
    agent_type VARCHAR(50),
    custom_model VARCHAR(50),
    custom_instructions TEXT,
    can_execute_actions BOOLEAN,
    tasks_completed INTEGER DEFAULT 0,
    success_rate FLOAT DEFAULT 0.0,
    last_active TIMESTAMP
);

-- Profile Completion Tracking
CREATE TABLE user_profile_completion (
    user_id INTEGER PRIMARY KEY REFERENCES unified_users(id),
    skills_completed BOOLEAN DEFAULT FALSE,
    experience_completed BOOLEAN DEFAULT FALSE,
    preferences_completed BOOLEAN DEFAULT FALSE,
    documents_completed BOOLEAN DEFAULT FALSE,
    completion_percentage INTEGER GENERATED ALWAYS AS (
        (skills_completed::int + experience_completed::int +
         preferences_completed::int + documents_completed::int) * 25
    ) STORED
);

-- Command Execution Log
CREATE TABLE command_execution_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES unified_users(id),
    command_type VARCHAR(50),
    payload JSONB,
    status VARCHAR(20),
    result JSONB,
    executed_at TIMESTAMP DEFAULT NOW(),
    execution_time_ms INTEGER
);
```

## 7. API Endpoints

### Profile Management
```python
# /api/profile/
GET    /api/profile/extended/          # Full profile with AI config
PUT    /api/profile/extended/          # Update profile
POST   /api/profile/skills/            # Add skills
DELETE /api/profile/skills/{skill}/    # Remove skill
POST   /api/profile/preferences/       # Set work preferences
POST   /api/profile/complete-step/     # Mark profile step complete

# AI Configuration
POST   /api/ai/configure/              # Set AI preferences
GET    /api/ai/models/                 # Available models & costs
POST   /api/ai/test-configuration/     # Test settings with sample
GET    /api/ai/usage-stats/            # Token usage & costs

# Agent Management
GET    /api/agents/assigned/           # User's assigned agents
POST   /api/agents/assign/             # Assign agent to user
DELETE /api/agents/{agent_id}/         # Remove agent
PUT    /api/agents/{agent_id}/config/  # Configure specific agent
GET    /api/agents/{agent_id}/stats/   # Agent performance stats

# Command Execution
POST   /api/commands/execute/          # Execute command
GET    /api/commands/history/          # Command history
GET    /api/commands/status/{cmd_id}/  # Check command status
```

## 8. Critical Integration Sequence

### Implementation Priority Order
1. **Extend UnifiedUser model** with profile fields
2. **Create UserAIConfiguration model** for AI settings
3. **Build Profile API endpoints** for CRUD operations
4. **Implement CommandCenter** for centralized control
5. **Connect OpportunitiesHub** to use profile for filtering
6. **Wire WebSocket commands** for real-time updates
7. **Deploy ProfileManager UI** for user self-service
8. **Integrate Agent assignments** with profile
9. **Enable Quick Apply** with stored resume
10. **Activate learning engine** for profile adaptation

## 9. Environment Configuration

```bash
# Add to .env

# Profile System
MIN_PROFILE_COMPLETION=60  # Minimum % before allowing full features
PROFILE_INTERVIEW_ENABLED=true
AUTO_ASSIGN_AGENTS=true
DEFAULT_AGENT_SET=income_builder,career_advisor,skill_matcher

# AI Configuration Defaults
DEFAULT_AI_MODEL=gpt-5-mini
DEFAULT_REASONING_LEVEL=medium
DEFAULT_AUTOMATION_LEVEL=semi-auto
MAX_DAILY_TOKENS=100000
MAX_MONTHLY_SPEND=50.00

# Command & Control
COMMAND_TIMEOUT_MS=30000
MAX_CONCURRENT_COMMANDS=5
ENABLE_COMMAND_LOGGING=true
COMMAND_RETRY_ATTEMPTS=3
```

## 10. Success Metrics

### KPIs to Track
- Profile completion rate (target: >80%)
- Average time to complete profile (target: <10 minutes)
- AI configuration adoption (target: >60% customize)
- Agent assignment effectiveness (success rate >70%)
- Command execution success rate (target: >95%)
- User engagement with personalized opportunities (CTR >30%)

### Monitoring Dashboard
```python
class UserMetricsDashboard:
    def get_user_metrics(self, user_id: int) -> dict:
        return {
            'profile_completion': self.get_profile_completion(user_id),
            'ai_token_usage': self.get_token_usage(user_id),
            'agent_performance': self.get_agent_stats(user_id),
            'opportunity_engagement': self.get_engagement_metrics(user_id),
            'revenue_generated': self.get_revenue_metrics(user_id),
            'command_success_rate': self.get_command_metrics(user_id)
        }
```

---

**Last Updated:** September 18, 2025
**Priority:** CRITICAL - Foundation for all personalization
**Dependencies:** UnifiedUser model, GPT-5 configuration, WebSocket infrastructure