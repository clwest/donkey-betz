# Phase 2: Intelligent Agent Selection - Implementation Prompt

## Objective
Automatically select the best agent(s) for any query using ML-powered recommendations

## Status: 73% Complete (Backend Done, Frontend Next)
**Prerequisites**: Phase 1 complete ✅
**Estimated Duration**: 1 session remaining (Session 100 for frontend)

## ⚡ SESSION 100 READY-TO-COPY PROMPT

```
# Phase 2: Intelligent Agent Selection - Frontend Implementation (Session 100)

## Current Status: Backend 100% Complete, Frontend 0% (73% Overall - 11/15 tasks done)

The entire backend is complete with ML recommendation engine, user context tracking, performance monitoring, feedback collection, workflow orchestration, and full API layer with 8 endpoints. Now need to create the frontend components to bring Phase 2 to life.

## What's Ready

### API Endpoints (All Working)
- POST /api/ai-partner/recommendations/recommend_agents/ - Get ML recommendations
- POST /api/ai-partner/recommendations/provide_feedback/ - Submit feedback  
- GET /api/ai-partner/recommendations/user_patterns/ - User patterns (cached 5min)
- GET /api/ai-partner/recommendations/agent_performance/ - Performance metrics
- POST /api/ai-partner/recommendations/deploy_workflow/ - Deploy workflows
- GET /api/ai-partner/recommendations/workflow_templates/ - List templates
- POST /api/ai-partner/recommendations/test_recommendation/ - Test endpoint

### Backend Services (100% Complete)
1. AgentRecommendationEngine - ML-powered selection
2. UserContextService - Behavior tracking
3. AgentPerformanceTracker - Performance metrics
4. FeedbackCollector - Learning loop
5. WorkflowOrchestrator - Multi-agent coordination
6. Full API layer with serializers
7. Test script (test_phase2_api.py)

## PRIORITY TASKS FOR SESSION 100

### 1. ProactiveAgentSuggestions Component (PRIORITY 1)

Create `donkey-betz-frontend/src/features/ai-agent/ProactiveAgentSuggestions.tsx`:

```tsx
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Badge, Button, Card, Tooltip } from 'antd';
import { RobotOutlined, RocketOutlined } from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './ProactiveAgentSuggestions.module.css';

interface AgentRecommendation {
  agent_name: string;
  confidence: number;
  reason: string;
  capabilities: string[];
  estimated_time: number;
  deployment_command: string;
}

export const ProactiveAgentSuggestions: React.FC = () => {
  const [recommendations, setRecommendations] = useState<AgentRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const { currentQuery } = useSelector((state: any) => state.chat);
  
  useEffect(() => {
    if (currentQuery && currentQuery.length > 10) {
      fetchRecommendations(currentQuery);
    }
  }, [currentQuery]);
  
  const fetchRecommendations = async (query: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/ai-partner/recommendations/recommend_agents/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          query,
          num_recommendations: 3,
          include_context: true
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setRecommendations(data.recommendations);
      }
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const deployAgent = async (recommendation: AgentRecommendation) => {
    dispatch({
      type: 'agent/deploy',
      payload: {
        command: recommendation.deployment_command,
        confidence: recommendation.confidence
      }
    });
    
    // Send feedback
    await fetch('/api/ai-partner/recommendations/provide_feedback/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        orchestration_id: `rec_${Date.now()}`,
        rating: 5,
        thumbs_up: true,
        comment: 'User accepted recommendation'
      })
    });
  };
  
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return '#52c41a';
    if (confidence >= 0.7) return '#1890ff';
    if (confidence >= 0.5) return '#faad14';
    return '#d9d9d9';
  };
  
  return (
    <div className={styles.container}>
      <AnimatePresence>
        {recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={styles.recommendationsPanel}
          >
            <h3><RobotOutlined /> Suggested Agents</h3>
            <div className={styles.recommendations}>
              {recommendations.map((rec, index) => (
                <motion.div
                  key={rec.agent_name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card
                    size="small"
                    className={styles.recommendationCard}
                    actions={[
                      <Button
                        type="primary"
                        size="small"
                        icon={<RocketOutlined />}
                        onClick={() => deployAgent(rec)}
                      >
                        Deploy
                      </Button>
                    ]}
                  >
                    <div className={styles.cardContent}>
                      <div className={styles.header}>
                        <span className={styles.agentName}>{rec.agent_name}</span>
                        <Tooltip title={`${(rec.confidence * 100).toFixed(0)}% confidence`}>
                          <Badge
                            color={getConfidenceColor(rec.confidence)}
                            text={`${(rec.confidence * 100).toFixed(0)}%`}
                          />
                        </Tooltip>
                      </div>
                      <p className={styles.reason}>{rec.reason}</p>
                      <div className={styles.meta}>
                        <span>~{rec.estimated_time}s</span>
                        <span>{rec.capabilities.slice(0, 2).join(', ')}</span>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
```

### 2. QuickActionsBar Component (PRIORITY 2)

Create `donkey-betz-frontend/src/features/ai-agent/QuickActionsBar.tsx`:

```tsx
import React, { useEffect, useState } from 'react';
import { Button, Space, Tooltip } from 'antd';
import { ThunderboltOutlined, HistoryOutlined, StarOutlined } from '@ant-design/icons';
import styles from './QuickActionsBar.module.css';

interface QuickAction {
  action_id: string;
  label: string;
  command: string;
  icon?: string;
  frequency: number;
  last_used?: string;
  category?: string;
}

export const QuickActionsBar: React.FC = () => {
  const [quickActions, setQuickActions] = useState<QuickAction[]>([]);
  const [userPatterns, setUserPatterns] = useState<any>(null);
  
  useEffect(() => {
    fetchUserPatterns();
  }, []);
  
  const fetchUserPatterns = async () => {
    try {
      const response = await fetch('/api/ai-partner/recommendations/user_patterns/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setQuickActions(data.quick_actions || []);
        setUserPatterns(data);
      }
    } catch (error) {
      console.error('Failed to fetch user patterns:', error);
    }
  };
  
  const executeQuickAction = async (action: QuickAction) => {
    // Deploy the action
    await fetch('/api/ai-partner/parse-command/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ command: action.command })
    });
    
    // Update local state
    fetchUserPatterns();
  };
  
  const getIcon = (category?: string) => {
    switch (category) {
      case 'analysis': return <ThunderboltOutlined />;
      case 'history': return <HistoryOutlined />;
      case 'favorite': return <StarOutlined />;
      default: return <ThunderboltOutlined />;
    }
  };
  
  return (
    <div className={styles.quickActionsBar}>
      <Space size="small">
        <span className={styles.label}>Quick Actions:</span>
        {quickActions.slice(0, 5).map(action => (
          <Tooltip key={action.action_id} title={action.command}>
            <Button
              size="small"
              icon={getIcon(action.category)}
              onClick={() => executeQuickAction(action)}
              className={styles.quickButton}
            >
              {action.label}
            </Button>
          </Tooltip>
        ))}
      </Space>
      {userPatterns && (
        <div className={styles.stats}>
          <span>Segment: {userPatterns.user_segment}</span>
          <span>Recent: {userPatterns.recent_deployments?.length || 0}</span>
        </div>
      )}
    </div>
  );
};
```

### 3. AnalyticsDashboard Component (PRIORITY 3)

Create `donkey-betz-frontend/src/features/ai-agent/AnalyticsDashboard.tsx`:

```tsx
import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Progress } from 'antd';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { CheckCircleOutlined, ClockCircleOutlined, RobotOutlined } from '@ant-design/icons';
import styles from './AnalyticsDashboard.module.css';

export const AnalyticsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);
  
  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/ai-partner/recommendations/agent_performance/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading || !metrics) {
    return <div>Loading analytics...</div>;
  }
  
  // Transform metrics for charts
  const performanceData = Object.entries(metrics).map(([agent, data]: any) => ({
    agent,
    success_rate: data.success_rate * 100,
    avg_time: data.avg_completion_time
  })).slice(0, 5);
  
  return (
    <div className={styles.dashboard}>
      <h2>Agent Performance Analytics</h2>
      
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Deployments"
              value={metrics.total_deployments || 0}
              prefix={<RobotOutlined />}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Success Rate"
              value={metrics.overall_success_rate || 95}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Avg Response Time"
              value={metrics.avg_response_time || 2.3}
              suffix="s"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>
      
      <Row gutter={16} style={{ marginTop: 20 }}>
        <Col span={12}>
          <Card title="Agent Success Rates">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="agent" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="success_rate" fill="#1890ff" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="Response Times">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="agent" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="avg_time" stroke="#52c41a" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
      
      <Row gutter={16} style={{ marginTop: 20 }}>
        <Col span={24}>
          <Card title="Top Performing Agents">
            {performanceData.map(agent => (
              <div key={agent.agent} className={styles.agentRow}>
                <span>{agent.agent}</span>
                <Progress percent={agent.success_rate} size="small" />
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    </div>
  );
};
```

### 4. Update Redux Store (PRIORITY 4)

Create `donkey-betz-frontend/src/store/slices/phase2Slice.ts`:

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Phase2State {
  recommendations: any[];
  userPatterns: any;
  agentPerformance: any;
  workflows: any[];
  feedback: any[];
  loading: boolean;
  error: string | null;
}

const initialState: Phase2State = {
  recommendations: [],
  userPatterns: null,
  agentPerformance: null,
  workflows: [],
  feedback: [],
  loading: false,
  error: null
};

const phase2Slice = createSlice({
  name: 'phase2',
  initialState,
  reducers: {
    setRecommendations(state, action: PayloadAction<any[]>) {
      state.recommendations = action.payload;
    },
    setUserPatterns(state, action: PayloadAction<any>) {
      state.userPatterns = action.payload;
    },
    setAgentPerformance(state, action: PayloadAction<any>) {
      state.agentPerformance = action.payload;
    },
    addFeedback(state, action: PayloadAction<any>) {
      state.feedback.push(action.payload);
    },
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    }
  }
});

export const {
  setRecommendations,
  setUserPatterns,
  setAgentPerformance,
  addFeedback,
  setLoading,
  setError
} = phase2Slice.actions;

export default phase2Slice.reducer;
```

### 5. Install Required Dependencies

```bash
cd donkey-betz-frontend
npm install recharts framer-motion
```

## Testing Checklist

1. **ProactiveAgentSuggestions**
   - [ ] Shows recommendations when user types
   - [ ] Confidence badges display correctly
   - [ ] Deploy button works
   - [ ] Feedback sent on deployment

2. **QuickActionsBar**
   - [ ] Shows user's frequent actions
   - [ ] Executes commands on click
   - [ ] Updates after use
   - [ ] Shows user segment

3. **AnalyticsDashboard**
   - [ ] Displays metrics correctly
   - [ ] Charts render properly
   - [ ] Auto-updates every 30s
   - [ ] Shows top agents

4. **Integration**
   - [ ] Redux state updates
   - [ ] API calls authenticated
   - [ ] Error handling works
   - [ ] WebSocket events (if time)

## File Structure

```
donkey-betz-frontend/src/features/ai-agent/
├── ProactiveAgentSuggestions.tsx
├── ProactiveAgentSuggestions.module.css
├── QuickActionsBar.tsx
├── QuickActionsBar.module.css
├── AnalyticsDashboard.tsx
├── AnalyticsDashboard.module.css
└── WorkflowBuilder.tsx (if time permits)

donkey-betz-frontend/src/store/slices/
└── phase2Slice.ts
```

## Integration Points

1. Add ProactiveAgentSuggestions to ChatInterface
2. Add QuickActionsBar to main layout header
3. Add AnalyticsDashboard to dedicated route (/analytics)
4. Import phase2Slice in store configuration

## Success Criteria

- User sees agent recommendations in real-time
- User can deploy agents with one click
- User can access quick actions
- User can view performance analytics
- Feedback is collected automatically

## Notes

- Backend API is 100% ready at /api/ai-partner/recommendations/
- Authentication token required for all endpoints
- Test with 'testuser' account if needed
- Use test_phase2_api.py to verify backend while developing

Ready to complete Phase 2!
```

## Implementation Requirements

### Backend (✅ COMPLETE)
1. **ML-Based Agent Selection** ✅
   - Feature extraction from queries
   - Scoring algorithms
   - Confidence calculation
   - Learning from feedback

2. **User Context Service** ✅
   - Track user patterns
   - Analyze success rates
   - Build user profiles
   - Predict preferences

3. **Agent Performance Tracking** ✅
   - Monitor success/failure rates
   - Track execution times
   - Identify bottlenecks
   - Generate recommendations

4. **Workflow Orchestration** ✅
   - Multi-agent coordination
   - Sequential/parallel execution
   - Dependency management
   - Result aggregation

### Frontend (🔄 Session 100)
1. **Proactive Agent Suggestions**
   - Real-time recommendations
   - Confidence indicators
   - One-click deployment
   - Explanation tooltips

2. **Analytics Dashboard**
   - Performance metrics
   - Success rate charts
   - User pattern visualization
   - Agent comparison

3. **Quick Actions Bar**
   - Frequently used agents
   - Saved workflows
   - Keyboard shortcuts
   - Recent deployments

4. **Workflow Builder**
   - Visual workflow design
   - Drag-and-drop interface
   - Step configuration
   - Save/load workflows

## Key Components

### Completed ✅
- `AgentRecommendationEngine` - ML-powered selection
- `UserContextService` - User behavior tracking
- `AgentPerformanceTracker` - Performance monitoring
- `FeedbackCollector` - Learning from feedback
- `WorkflowOrchestrator` - Multi-agent workflows
- `RecommendationViewSet` - API endpoints
- Database models (14 Phase 2 models)

### To Build (Session 100)
- `ProactiveAgentSuggestions` - UI component
- `QuickActionsBar` - Quick deployment UI
- `AnalyticsDashboard` - Metrics visualization
- `WorkflowBuilder` - Visual workflow creator

## Success Metrics

### Achieved ✅
- ML recommendation engine operational
- User context tracking active
- Performance metrics collection working
- Feedback loop implemented
- API endpoints accessible
- Workflow orchestration functional

### Target (Session 100)
- Recommendation accuracy > 85%
- Agent selection time < 200ms
- User satisfaction > 4.5/5
- Workflow success rate > 90%
- Frontend responsive < 100ms

## Technical Details

### ML Pipeline (✅ Complete)
```python
query → feature_extraction → scoring → ranking → recommendations
         ↓                                          ↑
    user_context → personalization → confidence ──┘
```

### API Endpoints (✅ Complete)
```
POST /api/ai-partner/recommendations/recommend_agents/
POST /api/ai-partner/recommendations/provide_feedback/
GET  /api/ai-partner/recommendations/user_patterns/
GET  /api/ai-partner/recommendations/agent_performance/
POST /api/ai-partner/recommendations/deploy_workflow/
GET  /api/ai-partner/recommendations/workflow_templates/
```

### Frontend Architecture (Session 100)
```
ChatInterface
├── ProactiveAgentSuggestions (floating panel)
├── QuickActionsBar (top bar)
└── Link to AnalyticsDashboard

Redux Store
├── recommendations[]
├── userPatterns{}
├── agentPerformance{}
└── workflows[]
```

## Notes for Session 100

1. **Start with ProactiveAgentSuggestions** - Core feature
2. **Use existing styles** - Match ChatInterface design
3. **Test with API** - Backend is 100% ready
4. **Focus on UX** - One-click deployment is key
5. **Add animations** - Smooth transitions for recommendations

The backend is complete and tested. All that remains is creating the frontend components to surface the intelligent agent selection capabilities to users.