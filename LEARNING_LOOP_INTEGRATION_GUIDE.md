# 🔄 Learning Loop Integration Guide

## Complete Documentation for Integrating the Learning Loop into Your Project

### Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Integration Methods](#integration-methods)
5. [Step-by-Step Integration](#step-by-step-integration)
6. [Code Examples](#code-examples)
7. [Data Flow](#data-flow)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [API Reference](#api-reference)

---

## Overview

The Learning Loop is a sophisticated continuous learning system that collects feedback from multiple sources, processes it, and uses it to improve AI agents, advisors, and system performance in real-time.

### What It Does:
- **Collects feedback** from users, agents, social media, and 1,770+ spiders
- **Analyzes patterns** to identify improvements and regressions
- **Triggers optimizations** automatically based on insights
- **Validates improvements** to ensure changes are beneficial
- **Maintains baselines** for performance comparison

### Intelligence Sources:
- **1,770 Spider Army** - Real-time market, news, and innovation data
- **Bluesky Integration** - Expert opinions and social trends
- **Reddit Integration** - Community consensus and discussions
- **User Feedback** - Direct input from platform users
- **Agent Self-Reporting** - Performance metrics from 151 agents
- **System Monitoring** - Internal performance data

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LEARNING LOOP CORE                       │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Feedback   │  │   Pattern    │  │  Optimization │      │
│  │  Collection  │→ │   Analysis   │→ │   Trigger     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↑                                      ↓              │
│  ┌──────────────┐                     ┌──────────────┐      │
│  │  Validation  │ ← ← ← ← ← ← ← ← ← ← │   Action     │      │
│  └──────────────┘                     └──────────────┘      │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│                      DATA SOURCES                             │
├───────────────────────────────────────────────────────────────┤
│  • Spider Army (1,770 spiders)                               │
│  • Bluesky Social Intelligence                               │
│  • Reddit Community Intelligence                             │
│  • User Feedback                                             │
│  • Agent Performance Metrics                                 │
│  • System Monitoring Dashboard                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Learning Loop Instance (`backend/intelligence/learning_loop.py`)

```python
from backend.intelligence.learning_loop import learning_loop

# The global singleton instance
learning_loop  # Already initialized and ready to use
```

### 2. Feedback Item Structure

```python
from backend.intelligence.learning_loop import FeedbackItem
from datetime import datetime

feedback = FeedbackItem(
    id="unique_id_123",
    timestamp=datetime.now(),
    source="your_component",      # Where feedback came from
    category="performance",        # Type: performance/accuracy/usability/error
    target="specific_agent",       # What it's about
    rating=0.85,                  # 0.0 to 1.0 score
    message="Detailed feedback",   # Human-readable message
    context={                      # Additional data
        'metric': 'response_time',
        'value': 1.2
    },
    metadata={}                    # Optional metadata
)
```

### 3. Learning Insight Structure

```python
from backend.intelligence.learning_loop import LearningInsight

insight = LearningInsight(
    id="insight_456",
    timestamp=datetime.now(),
    insight_type="pattern",       # pattern/anomaly/improvement/regression
    description="Found pattern",
    confidence=0.9,
    affected_components=["agent_1", "agent_2"],
    recommendations=["Increase cache size", "Optimize query"],
    impact_score=0.75
)
```

---

## Integration Methods

### Method 1: Direct Feedback Submission

```python
import asyncio
from backend.intelligence.learning_loop import learning_loop

async def submit_feedback_example():
    # Submit user feedback
    result = await learning_loop.submit_user_feedback(
        target="income_builder",
        rating=0.9,
        message="Found great job matches!",
        category="accuracy"
    )

    # Submit agent performance feedback
    await learning_loop.submit_agent_feedback(
        agent_id="job_matcher",
        metrics={
            'matches_found': 15,
            'user_satisfaction': 0.85,
            'response_time': 1.2
        }
    )
```

### Method 2: Automatic Collection Integration

```python
from backend.intelligence.learning_loop import learning_loop, FeedbackItem

class YourComponent:
    def __init__(self):
        self.learning_enabled = True

    async def process_task(self, task_data):
        start_time = time.time()

        try:
            # Your processing logic
            result = await self._do_processing(task_data)

            # Automatically send success feedback
            if self.learning_enabled:
                feedback = FeedbackItem(
                    id=f"task_{task_data['id']}",
                    timestamp=datetime.now(),
                    source=self.__class__.__name__,
                    category="performance",
                    target="task_processing",
                    rating=0.9,  # Success
                    message=f"Task completed in {time.time() - start_time:.2f}s",
                    context={
                        'task_type': task_data.get('type'),
                        'duration': time.time() - start_time,
                        'success': True
                    }
                )
                learning_loop._store_feedback(feedback)

            return result

        except Exception as e:
            # Send error feedback
            if self.learning_enabled:
                feedback = FeedbackItem(
                    id=f"error_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    source=self.__class__.__name__,
                    category="error",
                    target="task_processing",
                    rating=0.1,  # Error
                    message=str(e),
                    context={
                        'task_type': task_data.get('type'),
                        'error_type': type(e).__name__
                    }
                )
                learning_loop._store_feedback(feedback)
            raise
```

### Method 3: Webhook/Event Integration

```python
from django.dispatch import receiver
from django.db.models.signals import post_save
from backend.intelligence.learning_loop import learning_loop

@receiver(post_save, sender=YourModel)
def model_save_feedback(sender, instance, created, **kwargs):
    """Send feedback when model is saved"""
    if created:
        # New instance created
        asyncio.create_task(
            learning_loop.submit_user_feedback(
                target=f"{sender.__name__}",
                rating=1.0,
                message=f"New {sender.__name__} created",
                category="usability"
            )
        )
```

---

## Step-by-Step Integration

### Step 1: Import Required Components

```python
# Basic imports
from backend.intelligence.learning_loop import (
    learning_loop,
    FeedbackItem,
    LearningInsight
)
from datetime import datetime
import asyncio
```

### Step 2: Identify Feedback Points

Determine where in your code you want to collect feedback:
- After task completion
- On error occurrence
- When users interact
- At performance checkpoints
- During data processing

### Step 3: Implement Feedback Collection

```python
class YourService:
    async def execute_operation(self, data):
        # Track operation start
        operation_id = f"op_{datetime.now().timestamp()}"
        start_time = datetime.now()

        try:
            # Your operation
            result = await self._process(data)

            # Send success feedback
            feedback = FeedbackItem(
                id=operation_id,
                timestamp=datetime.now(),
                source="YourService",
                category="performance",
                target="operation_execution",
                rating=0.95,
                message="Operation successful",
                context={
                    'duration': (datetime.now() - start_time).total_seconds(),
                    'input_size': len(data),
                    'output_size': len(result)
                }
            )
            learning_loop._store_feedback(feedback)

            return result

        except Exception as e:
            # Send error feedback
            error_feedback = FeedbackItem(
                id=f"error_{operation_id}",
                timestamp=datetime.now(),
                source="YourService",
                category="error",
                target="operation_execution",
                rating=0.0,
                message=str(e),
                context={
                    'error_type': type(e).__name__,
                    'operation_id': operation_id
                }
            )
            learning_loop._store_feedback(error_feedback)
            raise
```

### Step 4: Connect to Intelligence Sources

```python
class EnhancedService:
    def __init__(self):
        self.connect_intelligence_sources()

    def connect_intelligence_sources(self):
        """Connect to spider army and social intelligence"""
        # Spider Army Intelligence
        from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
        self.spider_orchestrator = get_spider_orchestrator()

        # Social Intelligence
        from backend.intelligence.bluesky_learning_bridge import bluesky_learning_bridge
        self.bluesky_bridge = bluesky_learning_bridge

        from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge
        self.reddit_bridge = get_reddit_learning_bridge()

    async def get_enriched_insights(self, query):
        """Get insights from all intelligence sources"""
        insights = {}

        # Get spider intelligence
        spider_stats = await self.spider_orchestrator.get_spider_statistics()
        insights['spider_intelligence'] = spider_stats

        # Get social intelligence
        if self.bluesky_bridge:
            bluesky_insights = await self.bluesky_bridge.get_insights_for_query(query)
            insights['bluesky'] = bluesky_insights

        if self.reddit_bridge:
            reddit_consensus = await self.reddit_bridge.get_community_consensus(query)
            insights['reddit'] = reddit_consensus

        return insights
```

### Step 5: React to Learning Insights

```python
class AdaptiveComponent:
    def __init__(self):
        self.performance_threshold = 0.8
        self.setup_learning_listener()

    def setup_learning_listener(self):
        """Listen for learning insights"""
        # Check for insights periodically
        asyncio.create_task(self._monitor_insights())

    async def _monitor_insights(self):
        while True:
            # Get recent insights
            insights = await learning_loop.get_recent_insights(hours=1)

            for insight in insights:
                if self._affects_component(insight):
                    await self._adapt_to_insight(insight)

            await asyncio.sleep(300)  # Check every 5 minutes

    def _affects_component(self, insight):
        """Check if insight affects this component"""
        return self.__class__.__name__ in insight.affected_components

    async def _adapt_to_insight(self, insight):
        """Adapt behavior based on insight"""
        if insight.insight_type == "regression":
            # Performance degraded - take action
            logger.warning(f"Performance regression detected: {insight.description}")
            self.performance_threshold *= 0.9  # Relax threshold temporarily

        elif insight.insight_type == "improvement":
            # Performance improved - optimize further
            logger.info(f"Performance improvement: {insight.description}")
            self.performance_threshold *= 1.1  # Raise threshold
```

---

## Code Examples

### Example 1: Web Endpoint with Learning

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from backend.intelligence.learning_loop import learning_loop
import json
import asyncio

@require_http_methods(["POST"])
def process_user_request(request):
    """Process request with learning feedback"""
    try:
        data = json.loads(request.body)
        request_id = f"req_{datetime.now().timestamp()}"

        # Process request
        result = process_data(data)

        # Send success feedback
        asyncio.create_task(
            learning_loop.submit_user_feedback(
                target="api_endpoint",
                rating=1.0,
                message="Request processed successfully",
                category="performance"
            )
        )

        return JsonResponse({
            'success': True,
            'result': result,
            'request_id': request_id
        })

    except Exception as e:
        # Send error feedback
        asyncio.create_task(
            learning_loop.submit_user_feedback(
                target="api_endpoint",
                rating=0.0,
                message=f"Request failed: {str(e)}",
                category="error"
            )
        )

        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

### Example 2: Agent with Self-Learning

```python
class SmartAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.performance_history = []
        self.learning_enabled = True

    async def execute_task(self, task):
        """Execute task with learning integration"""
        start_time = datetime.now()

        # Get intelligence from spiders
        from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
        orchestrator = get_spider_orchestrator()
        spider_insights = await orchestrator.get_spider_statistics()

        try:
            # Use spider intelligence to enhance task execution
            if spider_insights.get('signals_processed', 0) > 100:
                # We have good intelligence data
                result = await self._execute_with_intelligence(task, spider_insights)
            else:
                # Fallback to basic execution
                result = await self._execute_basic(task)

            # Calculate performance
            duration = (datetime.now() - start_time).total_seconds()
            performance_score = self._calculate_performance(result, duration)

            # Store in history
            self.performance_history.append(performance_score)

            # Send learning feedback
            if self.learning_enabled:
                feedback = FeedbackItem(
                    id=f"{self.agent_id}_task_{task.id}",
                    timestamp=datetime.now(),
                    source=f"agent_{self.agent_id}",
                    category="performance",
                    target="task_execution",
                    rating=performance_score,
                    message=f"Task completed in {duration:.2f}s",
                    context={
                        'task_type': task.type,
                        'duration': duration,
                        'spider_intelligence_used': spider_insights.get('signals_processed', 0) > 100,
                        'result_quality': self._assess_quality(result)
                    }
                )
                learning_loop._store_feedback(feedback)

            # Check if we should adapt
            if len(self.performance_history) > 10:
                await self._check_adaptation_needed()

            return result

        except Exception as e:
            # Send error feedback
            if self.learning_enabled:
                error_feedback = FeedbackItem(
                    id=f"{self.agent_id}_error_{datetime.now().timestamp()}",
                    timestamp=datetime.now(),
                    source=f"agent_{self.agent_id}",
                    category="error",
                    target="task_execution",
                    rating=0.0,
                    message=str(e),
                    context={
                        'task_type': task.type,
                        'error_type': type(e).__name__
                    }
                )
                learning_loop._store_feedback(error_feedback)
            raise

    async def _check_adaptation_needed(self):
        """Check if agent needs to adapt based on performance"""
        recent_performance = self.performance_history[-10:]
        avg_performance = sum(recent_performance) / len(recent_performance)

        if avg_performance < 0.7:
            # Performance is degrading - request optimization
            await learning_loop.request_optimization(
                component=f"agent_{self.agent_id}",
                reason="Performance below threshold",
                current_score=avg_performance,
                target_score=0.85
            )
```

### Example 3: Dashboard Integration

```python
class DashboardWithLearning:
    def __init__(self):
        self.learning_loop = learning_loop
        self.cache_duration = 60  # seconds
        self.last_update = None

    async def get_dashboard_data(self):
        """Get dashboard data with learning insights"""

        # Get base dashboard data
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': await self._get_metrics(),
            'alerts': await self._get_alerts()
        }

        # Add learning insights
        data['learning'] = {
            'recent_insights': await self.learning_loop.get_recent_insights(hours=24),
            'feedback_count': len(self.learning_loop.feedback_buffer),
            'active_optimizations': await self.learning_loop.get_active_optimizations(),
            'performance_trends': await self._get_performance_trends()
        }

        # Add spider intelligence
        from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
        orchestrator = get_spider_orchestrator()
        data['spider_intelligence'] = await orchestrator.get_spider_statistics()

        # Add social intelligence
        data['social_intelligence'] = {
            'bluesky_active': await self._check_bluesky_active(),
            'reddit_active': await self._check_reddit_active()
        }

        # Cache and return
        self.last_update = data
        return data

    async def _get_performance_trends(self):
        """Calculate performance trends from learning data"""
        trends = {}

        # Get feedback by category
        for category in ['performance', 'accuracy', 'usability', 'error']:
            category_feedback = [
                f for f in self.learning_loop.feedback_buffer
                if f.category == category
            ]

            if category_feedback:
                # Calculate average rating over time
                ratings = [f.rating for f in category_feedback[-100:]]
                trends[category] = {
                    'current': ratings[-1] if ratings else 0,
                    'average': sum(ratings) / len(ratings),
                    'trend': 'improving' if ratings[-1] > ratings[0] else 'declining',
                    'samples': len(ratings)
                }

        return trends
```

### Example 4: Automated Testing with Learning

```python
class TestSuiteWithLearning:
    def __init__(self):
        self.learning_loop = learning_loop
        self.test_results = []

    async def run_tests(self):
        """Run tests and feed results to learning loop"""
        test_run_id = f"test_run_{datetime.now().timestamp()}"

        # Run test suite
        results = await self._execute_tests()

        # Analyze results
        passed = sum(1 for r in results if r['passed'])
        total = len(results)
        success_rate = passed / total if total > 0 else 0

        # Send aggregate feedback
        feedback = FeedbackItem(
            id=test_run_id,
            timestamp=datetime.now(),
            source="test_suite",
            category="accuracy",
            target="system_quality",
            rating=success_rate,
            message=f"Test run: {passed}/{total} passed",
            context={
                'passed': passed,
                'failed': total - passed,
                'total': total,
                'failed_tests': [r['name'] for r in results if not r['passed']]
            }
        )
        learning_loop._store_feedback(feedback)

        # Send individual test feedback for failures
        for result in results:
            if not result['passed']:
                error_feedback = FeedbackItem(
                    id=f"{test_run_id}_{result['name']}",
                    timestamp=datetime.now(),
                    source="test_suite",
                    category="error",
                    target=result['component'],
                    rating=0.0,
                    message=f"Test failed: {result['error']}",
                    context=result
                )
                learning_loop._store_feedback(error_feedback)

        # Check if we need to trigger alerts
        if success_rate < 0.8:
            await self._trigger_quality_alert(success_rate, results)

        return results
```

---

## Data Flow

### 1. Feedback Collection Flow

```
Your Component → FeedbackItem → learning_loop._store_feedback()
                                         ↓
                                 feedback_buffer
                                         ↓
                              Pattern Analysis (async)
                                         ↓
                                 Learning Insights
                                         ↓
                              Optimization Triggers
```

### 2. Intelligence Integration Flow

```
Spider Army (1,770) ─┐
Bluesky Intelligence ├→ Learning Loop → Pattern Analysis → Insights
Reddit Intelligence  ─┤                         ↓
User Feedback ────────┘                  Agent/Advisor Updates
```

### 3. Optimization Flow

```
Low Performance Detection → Request Optimization → Generate Actions
                                    ↓
                           Execute Optimizations
                                    ↓
                           Validate Improvements → Update Baselines
```

---

## Best Practices

### 1. Feedback Quality

```python
# ❌ Bad: Vague feedback
feedback = FeedbackItem(
    source="component",
    rating=0.5,
    message="Not good"
)

# ✅ Good: Detailed, actionable feedback
feedback = FeedbackItem(
    id=f"component_action_{timestamp}",
    timestamp=datetime.now(),
    source="specific_component",
    category="performance",
    target="database_query",
    rating=0.5,
    message="Query timeout after 30s on large dataset",
    context={
        'query_type': 'aggregation',
        'dataset_size': 1000000,
        'timeout_seconds': 30,
        'expected_time': 5
    }
)
```

### 2. Async Integration

```python
# ❌ Bad: Blocking feedback submission
def process_request(request):
    result = do_work()
    learning_loop.submit_user_feedback(...)  # Blocks!
    return result

# ✅ Good: Non-blocking async submission
async def process_request(request):
    result = await do_work()
    asyncio.create_task(  # Non-blocking
        learning_loop.submit_user_feedback(...)
    )
    return result
```

### 3. Error Handling

```python
# ✅ Good: Graceful degradation
async def enhanced_operation(data):
    try:
        # Try to get intelligence
        insights = await get_spider_intelligence()
        return await process_with_insights(data, insights)
    except Exception as e:
        # Log but don't fail
        logger.warning(f"Intelligence unavailable: {e}")
        # Fallback to basic processing
        return await process_basic(data)
```

### 4. Performance Considerations

```python
class OptimizedComponent:
    def __init__(self):
        self.feedback_batch = []
        self.batch_size = 10
        self.last_flush = datetime.now()

    async def add_feedback(self, feedback):
        """Batch feedback for efficiency"""
        self.feedback_batch.append(feedback)

        # Flush if batch is full or timeout
        if (len(self.feedback_batch) >= self.batch_size or
            (datetime.now() - self.last_flush).seconds > 60):
            await self._flush_feedback()

    async def _flush_feedback(self):
        """Send batched feedback"""
        if self.feedback_batch:
            for feedback in self.feedback_batch:
                learning_loop._store_feedback(feedback)
            self.feedback_batch = []
            self.last_flush = datetime.now()
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Learning Loop Not Collecting Feedback

```python
# Check if learning is active
if not learning_loop.learning_active:
    await learning_loop.start_learning()

# Verify feedback is being stored
print(f"Feedback buffer size: {len(learning_loop.feedback_buffer)}")
print(f"Insights generated: {len(learning_loop.insights)}")
```

#### 2. Intelligence Sources Not Connected

```python
async def verify_intelligence_sources():
    """Verify all intelligence sources are connected"""

    # Check Spider Army
    from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
    orchestrator = get_spider_orchestrator()
    stats = await orchestrator.get_spider_statistics()
    print(f"Spider Army: {stats['summary']['total_deployed']} spiders active")

    # Check Bluesky
    try:
        from backend.intelligence.bluesky_learning_bridge import bluesky_learning_bridge
        print(f"Bluesky: {'Connected' if bluesky_learning_bridge else 'Not connected'}")
    except:
        print("Bluesky: Not available")

    # Check Reddit
    try:
        from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge
        bridge = get_reddit_learning_bridge()
        print(f"Reddit: Connected with {len(bridge.subreddit_mapping)} categories")
    except:
        print("Reddit: Not available")
```

#### 3. Performance Issues

```python
# Monitor learning loop performance
async def check_learning_performance():
    stats = {
        'feedback_rate': len(learning_loop.feedback_buffer) / 3600,  # per hour
        'insight_generation_rate': len(learning_loop.insights) / 3600,
        'optimization_success_rate': learning_loop.optimization_metrics.get('success_rate', 0),
        'memory_usage': sys.getsizeof(learning_loop.feedback_buffer) / 1024 / 1024  # MB
    }
    return stats
```

#### 4. Debugging Feedback Flow

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('backend.intelligence.learning_loop')
logger.setLevel(logging.DEBUG)

# Add debug wrapper
class DebuggedComponent:
    async def process(self, data):
        logger.debug(f"Processing started: {data}")

        # Create feedback with debug info
        feedback = FeedbackItem(
            id=f"debug_{datetime.now().timestamp()}",
            source="DebuggedComponent",
            category="debug",
            target="process",
            rating=1.0,
            message="Debug feedback",
            context={'debug': True, 'data': data}
        )

        logger.debug(f"Feedback created: {feedback.id}")
        learning_loop._store_feedback(feedback)
        logger.debug(f"Feedback stored, buffer size: {len(learning_loop.feedback_buffer)}")

        return "processed"
```

---

## API Reference

### Core Methods

#### `learning_loop.start_learning()`
Starts the continuous learning process.

```python
await learning_loop.start_learning()
```

#### `learning_loop.stop_learning()`
Stops the learning process.

```python
await learning_loop.stop_learning()
```

#### `learning_loop.submit_user_feedback(target, rating, message, category)`
Submit user feedback.

```python
await learning_loop.submit_user_feedback(
    target="component_name",
    rating=0.85,  # 0.0 to 1.0
    message="Feedback message",
    category="performance"  # performance/accuracy/usability/error
)
```

#### `learning_loop.submit_agent_feedback(agent_id, metrics)`
Submit agent performance metrics.

```python
await learning_loop.submit_agent_feedback(
    agent_id="agent_123",
    metrics={
        'response_time': 1.5,
        'accuracy': 0.92,
        'tasks_completed': 10
    }
)
```

#### `learning_loop.get_recent_insights(hours)`
Get recent learning insights.

```python
insights = await learning_loop.get_recent_insights(hours=24)
for insight in insights:
    print(f"{insight.insight_type}: {insight.description}")
```

#### `learning_loop.request_optimization(component, reason, current_score, target_score)`
Request optimization for a component.

```python
await learning_loop.request_optimization(
    component="slow_agent",
    reason="Performance degradation",
    current_score=0.6,
    target_score=0.85
)
```

#### `learning_loop.get_learning_summary()`
Get comprehensive learning statistics.

```python
summary = await learning_loop.get_learning_summary()
print(f"Total feedback: {summary['total_feedback']}")
print(f"Insights generated: {summary['insights_generated']}")
print(f"Active optimizations: {summary['active_optimizations']}")
```

### Data Structures

#### FeedbackItem Fields
- `id` (str): Unique identifier
- `timestamp` (datetime): When feedback was created
- `source` (str): Component that generated feedback
- `category` (str): Type of feedback
- `target` (str): What the feedback is about
- `rating` (float): Score from 0.0 to 1.0
- `message` (str): Human-readable message
- `context` (dict): Additional context data
- `metadata` (dict): Optional metadata

#### LearningInsight Fields
- `id` (str): Unique identifier
- `timestamp` (datetime): When insight was generated
- `insight_type` (str): Type of insight
- `description` (str): Description of insight
- `confidence` (float): Confidence score
- `affected_components` (list): Components affected
- `recommendations` (list): Suggested actions
- `impact_score` (float): Estimated impact

---

## Advanced Integration Examples

### Multi-Source Intelligence Aggregation

```python
class IntelligenceAggregator:
    """Aggregates intelligence from all sources for comprehensive learning"""

    def __init__(self):
        self.setup_sources()

    def setup_sources(self):
        """Initialize all intelligence sources"""
        # Spider Army
        from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
        self.spider_orchestrator = get_spider_orchestrator()

        # Social Intelligence
        from backend.intelligence.bluesky_learning_bridge import bluesky_learning_bridge
        from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge

        self.bluesky = bluesky_learning_bridge
        self.reddit = get_reddit_learning_bridge()

        # Learning Loop
        from backend.intelligence.learning_loop import learning_loop
        self.learning_loop = learning_loop

    async def get_comprehensive_intelligence(self, query):
        """Get intelligence from all sources"""
        intelligence = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'sources': {}
        }

        # Spider Army Data
        spider_stats = await self.spider_orchestrator.get_spider_statistics()
        intelligence['sources']['spiders'] = {
            'active': spider_stats['total_spiders'],
            'signals_processed': spider_stats['signals_processed'],
            'categories': spider_stats['categories']
        }

        # Bluesky Data
        if self.bluesky:
            try:
                bluesky_insights = await self.bluesky.search_intelligence(query)
                intelligence['sources']['bluesky'] = {
                    'posts': len(bluesky_insights),
                    'sentiment': self._calculate_sentiment(bluesky_insights)
                }
            except:
                intelligence['sources']['bluesky'] = {'status': 'unavailable'}

        # Reddit Data
        if self.reddit:
            try:
                consensus = await self.reddit.get_community_consensus(query)
                if consensus:
                    intelligence['sources']['reddit'] = {
                        'consensus': consensus.average_sentiment,
                        'discussions': consensus.total_discussions,
                        'confidence': consensus.confidence
                    }
            except:
                intelligence['sources']['reddit'] = {'status': 'unavailable'}

        # Learning Loop Insights
        recent_insights = await self.learning_loop.get_recent_insights(hours=1)
        intelligence['learning'] = {
            'recent_insights': len(recent_insights),
            'top_insight': recent_insights[0].description if recent_insights else None
        }

        # Generate combined intelligence score
        intelligence['combined_confidence'] = self._calculate_combined_confidence(intelligence)

        return intelligence
```

### Custom Learning Pipeline

```python
class CustomLearningPipeline:
    """Create a custom learning pipeline for specific use cases"""

    def __init__(self, pipeline_name):
        self.name = pipeline_name
        self.learning_loop = learning_loop
        self.stages = []
        self.metrics = defaultdict(list)

    def add_stage(self, stage_func):
        """Add a processing stage to the pipeline"""
        self.stages.append(stage_func)
        return self

    async def process(self, data):
        """Process data through the pipeline with learning"""
        pipeline_id = f"{self.name}_{datetime.now().timestamp()}"
        results = []

        for i, stage in enumerate(self.stages):
            stage_name = stage.__name__
            start_time = datetime.now()

            try:
                # Execute stage
                result = await stage(data)
                duration = (datetime.now() - start_time).total_seconds()

                # Record success
                self.metrics[stage_name].append({
                    'success': True,
                    'duration': duration
                })

                # Send learning feedback
                feedback = FeedbackItem(
                    id=f"{pipeline_id}_stage_{i}",
                    timestamp=datetime.now(),
                    source=self.name,
                    category="performance",
                    target=stage_name,
                    rating=0.9,
                    message=f"Stage completed in {duration:.2f}s",
                    context={
                        'stage': stage_name,
                        'duration': duration,
                        'pipeline': self.name
                    }
                )
                self.learning_loop._store_feedback(feedback)

                results.append(result)
                data = result  # Pass to next stage

            except Exception as e:
                # Record failure
                self.metrics[stage_name].append({
                    'success': False,
                    'error': str(e)
                })

                # Send error feedback
                error_feedback = FeedbackItem(
                    id=f"{pipeline_id}_stage_{i}_error",
                    timestamp=datetime.now(),
                    source=self.name,
                    category="error",
                    target=stage_name,
                    rating=0.0,
                    message=f"Stage failed: {str(e)}",
                    context={
                        'stage': stage_name,
                        'error': type(e).__name__,
                        'pipeline': self.name
                    }
                )
                self.learning_loop._store_feedback(error_feedback)
                raise

        # Analyze pipeline performance
        await self._analyze_performance()

        return results

    async def _analyze_performance(self):
        """Analyze and optimize pipeline performance"""
        for stage_name, metrics in self.metrics.items():
            if len(metrics) >= 10:
                # Calculate success rate
                success_rate = sum(1 for m in metrics if m['success']) / len(metrics)

                if success_rate < 0.8:
                    # Request optimization
                    await self.learning_loop.request_optimization(
                        component=f"{self.name}_{stage_name}",
                        reason="Low success rate",
                        current_score=success_rate,
                        target_score=0.95
                    )
```

---

## Conclusion

The Learning Loop is a powerful system that enables continuous improvement across your entire platform. By following this guide, you can:

1. **Collect feedback** from any component
2. **Integrate intelligence** from 1,770+ spiders and social media
3. **Generate insights** automatically
4. **Trigger optimizations** based on patterns
5. **Validate improvements** continuously

Key takeaways:
- Use `FeedbackItem` for structured feedback
- Always include context for better insights
- Leverage async operations for non-blocking integration
- Connect to intelligence sources for enriched learning
- Monitor and react to learning insights

The system is designed to be flexible and can be integrated into any part of your project with minimal code changes.

---

## Quick Reference Card

```python
# Import
from backend.intelligence.learning_loop import learning_loop, FeedbackItem

# Submit feedback
await learning_loop.submit_user_feedback(
    target="component",
    rating=0.85,
    message="Feedback",
    category="performance"
)

# Store feedback directly
feedback = FeedbackItem(
    id="unique_id",
    timestamp=datetime.now(),
    source="your_component",
    category="performance",
    target="what_its_about",
    rating=0.85,
    message="Details",
    context={}
)
learning_loop._store_feedback(feedback)

# Get insights
insights = await learning_loop.get_recent_insights(hours=24)

# Request optimization
await learning_loop.request_optimization(
    component="slow_component",
    reason="Performance issue",
    current_score=0.6,
    target_score=0.85
)

# Check status
summary = await learning_loop.get_learning_summary()
```

---

## Advanced Patterns

### Pattern 1: Hierarchical Learning

```python
class HierarchicalLearningSystem:
    """Implements multi-level learning with parent-child relationships"""

    def __init__(self):
        self.learning_loop = learning_loop
        self.hierarchy = {
            'system': {
                'agents': ['agent_1', 'agent_2', 'agent_3'],
                'advisors': ['buffett', 'dalio', 'cathie_wood'],
                'spiders': ['financial', 'innovation', 'market']
            }
        }

    async def propagate_learning(self, source_level, insight):
        """Propagate insights through hierarchy"""
        # Bottom-up learning
        if source_level == 'agent':
            # Agent insight affects advisor strategy
            for advisor in self.hierarchy['system']['advisors']:
                await self._update_advisor_strategy(advisor, insight)

        # Top-down learning
        elif source_level == 'system':
            # System insight affects all components
            for category in self.hierarchy['system']:
                for component in self.hierarchy['system'][category]:
                    await self._update_component(component, insight)

    async def _update_component(self, component_id, insight):
        """Update component based on insight"""
        feedback = FeedbackItem(
            id=f"hierarchical_{component_id}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            source="hierarchical_learning",
            category="optimization",
            target=component_id,
            rating=insight.confidence,
            message=f"Applying insight: {insight.description}",
            context={
                'insight_id': insight.id,
                'hierarchy_level': 'component',
                'action': 'strategy_update'
            }
        )
        self.learning_loop._store_feedback(feedback)
```

### Pattern 2: Federated Learning

```python
class FederatedLearningNode:
    """Distributed learning across multiple nodes"""

    def __init__(self, node_id):
        self.node_id = node_id
        self.local_learning = learning_loop
        self.peer_nodes = []

    async def share_insights(self):
        """Share local insights with peer nodes"""
        local_insights = await self.local_learning.get_recent_insights(hours=1)

        for peer in self.peer_nodes:
            await self._send_to_peer(peer, local_insights)

    async def receive_peer_insights(self, peer_id, insights):
        """Integrate insights from peer nodes"""
        for insight in insights:
            # Adapt foreign insight to local context
            adapted_insight = self._adapt_insight(insight, peer_id)

            # Store as feedback for local learning
            feedback = FeedbackItem(
                id=f"federated_{peer_id}_{insight.id}",
                timestamp=datetime.now(),
                source=f"federated_node_{peer_id}",
                category="external_learning",
                target="system",
                rating=insight.confidence * 0.8,  # Reduce confidence for external
                message=f"Federated insight: {insight.description}",
                context={
                    'original_node': peer_id,
                    'insight_type': insight.insight_type,
                    'adapted': True
                }
            )
            self.local_learning._store_feedback(feedback)
```

### Pattern 3: Reinforcement Learning Integration

```python
class ReinforcementLearningAdapter:
    """Integrate RL algorithms with learning loop"""

    def __init__(self):
        self.learning_loop = learning_loop
        self.reward_history = []
        self.action_space = []
        self.state_history = []

    async def execute_action(self, state, action):
        """Execute action and collect reward"""
        # Execute action
        result = await self._perform_action(action, state)

        # Calculate reward
        reward = self._calculate_reward(result, state)

        # Store in learning loop
        feedback = FeedbackItem(
            id=f"rl_{state}_{action}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            source="reinforcement_learning",
            category="performance",
            target="rl_agent",
            rating=reward,
            message=f"Action {action} in state {state}",
            context={
                'state': state,
                'action': action,
                'reward': reward,
                'result': result
            }
        )
        self.learning_loop._store_feedback(feedback)

        # Update history
        self.reward_history.append(reward)
        self.action_space.append(action)
        self.state_history.append(state)

        # Trigger learning if enough history
        if len(self.reward_history) > 100:
            await self._trigger_policy_update()

    async def _trigger_policy_update(self):
        """Update policy based on reward history"""
        avg_reward = sum(self.reward_history[-100:]) / 100

        if avg_reward < 0.5:
            await self.learning_loop.request_optimization(
                component="rl_policy",
                reason="Low average reward",
                current_score=avg_reward,
                target_score=0.8
            )
```

---

## Real-World Integration Examples

### Example: E-commerce Recommendation System

```python
class EcommerceRecommendationLearning:
    """Real-world example: E-commerce with learning loop"""

    def __init__(self):
        self.learning_loop = learning_loop
        self.recommendation_cache = {}
        self.user_interactions = defaultdict(list)

    async def get_recommendations(self, user_id, context):
        """Get product recommendations with learning"""
        start_time = datetime.now()

        # Get base recommendations
        recommendations = await self._generate_recommendations(user_id, context)

        # Enhance with spider intelligence
        from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
        orchestrator = get_spider_orchestrator()
        market_trends = await orchestrator.get_market_intelligence()

        # Enhance with social intelligence
        from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge
        reddit_bridge = get_reddit_learning_bridge()
        trending_products = await reddit_bridge.get_trending_topics("shopping")

        # Combine intelligence
        enhanced_recommendations = self._enhance_with_intelligence(
            recommendations,
            market_trends,
            trending_products
        )

        # Track recommendation generation
        feedback = FeedbackItem(
            id=f"rec_{user_id}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            source="recommendation_engine",
            category="performance",
            target="recommendation_generation",
            rating=0.85,
            message=f"Generated {len(enhanced_recommendations)} recommendations",
            context={
                'user_id': user_id,
                'recommendation_count': len(enhanced_recommendations),
                'generation_time': (datetime.now() - start_time).total_seconds(),
                'intelligence_sources': ['spiders', 'reddit'],
                'context': context
            }
        )
        self.learning_loop._store_feedback(feedback)

        return enhanced_recommendations

    async def track_user_interaction(self, user_id, product_id, action):
        """Track user interactions with recommendations"""
        interaction = {
            'timestamp': datetime.now(),
            'product_id': product_id,
            'action': action  # view, click, purchase, ignore
        }
        self.user_interactions[user_id].append(interaction)

        # Calculate interaction score
        score = {
            'ignore': 0.0,
            'view': 0.3,
            'click': 0.6,
            'purchase': 1.0
        }.get(action, 0.5)

        # Send feedback
        feedback = FeedbackItem(
            id=f"interaction_{user_id}_{product_id}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            source="user_interaction",
            category="accuracy",
            target="recommendation_quality",
            rating=score,
            message=f"User {action} on product {product_id}",
            context={
                'user_id': user_id,
                'product_id': product_id,
                'action': action,
                'score': score
            }
        )
        self.learning_loop._store_feedback(feedback)

        # Check if we need to update recommendations
        recent_interactions = self.user_interactions[user_id][-10:]
        avg_score = sum(i.get('score', 0.5) for i in recent_interactions) / len(recent_interactions)

        if avg_score < 0.4:
            # Poor recommendation performance - request optimization
            await self.learning_loop.request_optimization(
                component=f"recommendations_user_{user_id}",
                reason="Low user engagement",
                current_score=avg_score,
                target_score=0.7
            )
```

### Example: Trading Bot with Learning

```python
class TradingBotWithLearning:
    """Trading bot that learns from market conditions"""

    def __init__(self):
        self.learning_loop = learning_loop
        self.positions = {}
        self.performance_history = []

    async def analyze_opportunity(self, symbol, market_data):
        """Analyze trading opportunity with multi-source intelligence"""

        # Get spider intelligence
        from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
        orchestrator = get_spider_orchestrator()
        spider_signals = await orchestrator.get_financial_signals(symbol)

        # Get social sentiment
        from backend.intelligence.bluesky_learning_bridge import bluesky_learning_bridge
        social_sentiment = await bluesky_learning_bridge.search_intelligence(f"${symbol}")

        # Get Reddit consensus
        from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge
        reddit = get_reddit_learning_bridge()
        reddit_consensus = await reddit.get_community_consensus(symbol)

        # Combine signals
        confidence = self._calculate_confidence(
            spider_signals,
            social_sentiment,
            reddit_consensus,
            market_data
        )

        # Make decision
        decision = {
            'action': 'buy' if confidence > 0.7 else 'hold' if confidence > 0.3 else 'sell',
            'confidence': confidence,
            'symbol': symbol,
            'timestamp': datetime.now()
        }

        # Track decision
        feedback = FeedbackItem(
            id=f"trading_{symbol}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            source="trading_bot",
            category="performance",
            target="trading_decision",
            rating=confidence,
            message=f"Trading decision for {symbol}: {decision['action']}",
            context={
                'symbol': symbol,
                'action': decision['action'],
                'confidence': confidence,
                'spider_signals': len(spider_signals),
                'social_sentiment': social_sentiment,
                'reddit_consensus': reddit_consensus
            }
        )
        self.learning_loop._store_feedback(feedback)

        return decision

    async def track_position_performance(self, symbol, entry_price, exit_price):
        """Track trading performance"""
        profit_loss = (exit_price - entry_price) / entry_price

        # Send performance feedback
        performance_rating = min(1.0, max(0.0, (profit_loss + 0.1) * 5))  # Normalize to 0-1

        feedback = FeedbackItem(
            id=f"position_{symbol}_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            source="trading_bot",
            category="accuracy",
            target="position_performance",
            rating=performance_rating,
            message=f"Position closed: {profit_loss*100:.2f}% P/L",
            context={
                'symbol': symbol,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'profit_loss': profit_loss,
                'performance_rating': performance_rating
            }
        )
        self.learning_loop._store_feedback(feedback)

        # Update performance history
        self.performance_history.append(profit_loss)

        # Check if strategy needs adjustment
        if len(self.performance_history) > 20:
            recent_performance = sum(self.performance_history[-20:]) / 20
            if recent_performance < 0:
                await self.learning_loop.request_optimization(
                    component="trading_strategy",
                    reason="Negative average returns",
                    current_score=recent_performance,
                    target_score=0.05  # Target 5% average return
                )
```

---

## Performance Optimization

### Memory Management

```python
class OptimizedLearningLoop:
    """Memory-efficient learning loop integration"""

    def __init__(self, max_buffer_size=10000):
        self.max_buffer_size = max_buffer_size
        self.feedback_buffer = deque(maxlen=max_buffer_size)
        self.compression_enabled = True

    def store_feedback(self, feedback):
        """Store feedback with compression"""
        if self.compression_enabled:
            # Compress context if too large
            if sys.getsizeof(feedback.context) > 1024:  # 1KB threshold
                feedback.context = self._compress_context(feedback.context)

        self.feedback_buffer.append(feedback)

        # Trigger cleanup if needed
        if len(self.feedback_buffer) >= self.max_buffer_size * 0.9:
            self._cleanup_old_feedback()

    def _compress_context(self, context):
        """Compress large context objects"""
        import json
        import zlib
        json_str = json.dumps(context)
        compressed = zlib.compress(json_str.encode())
        return {
            'compressed': True,
            'data': compressed.hex(),
            'original_size': len(json_str),
            'compressed_size': len(compressed)
        }

    def _cleanup_old_feedback(self):
        """Archive old feedback to reduce memory usage"""
        # Keep only recent high-value feedback
        cutoff_time = datetime.now() - timedelta(hours=24)

        important_feedback = [
            f for f in self.feedback_buffer
            if f.timestamp > cutoff_time or f.rating < 0.3 or f.rating > 0.9
        ]

        self.feedback_buffer = deque(important_feedback, maxlen=self.max_buffer_size)
```

### Batch Processing

```python
class BatchLearningProcessor:
    """Process learning feedback in batches for efficiency"""

    def __init__(self, batch_size=100, batch_interval=60):
        self.batch_size = batch_size
        self.batch_interval = batch_interval  # seconds
        self.pending_feedback = []
        self.last_batch_time = datetime.now()
        self.learning_loop = learning_loop

    async def add_feedback(self, feedback):
        """Add feedback to batch"""
        self.pending_feedback.append(feedback)

        # Check if batch should be processed
        should_process = (
            len(self.pending_feedback) >= self.batch_size or
            (datetime.now() - self.last_batch_time).seconds >= self.batch_interval
        )

        if should_process:
            await self.process_batch()

    async def process_batch(self):
        """Process accumulated feedback as batch"""
        if not self.pending_feedback:
            return

        batch_id = f"batch_{datetime.now().timestamp()}"

        # Group feedback by category for efficient processing
        grouped = defaultdict(list)
        for feedback in self.pending_feedback:
            grouped[feedback.category].append(feedback)

        # Process each group
        for category, items in grouped.items():
            # Calculate aggregate metrics
            avg_rating = sum(f.rating for f in items) / len(items)

            # Create batch feedback
            batch_feedback = FeedbackItem(
                id=batch_id,
                timestamp=datetime.now(),
                source="batch_processor",
                category=category,
                target="batch_analysis",
                rating=avg_rating,
                message=f"Batch of {len(items)} {category} feedback items",
                context={
                    'item_count': len(items),
                    'average_rating': avg_rating,
                    'category': category,
                    'individual_ratings': [f.rating for f in items]
                }
            )

            # Store batch feedback
            self.learning_loop._store_feedback(batch_feedback)

            # Store individual items if needed
            for item in items:
                self.learning_loop._store_feedback(item)

        # Clear pending
        self.pending_feedback = []
        self.last_batch_time = datetime.now()
```

---

## Monitoring and Observability

### Learning Loop Dashboard

```python
class LearningLoopDashboard:
    """Real-time monitoring dashboard for learning loop"""

    def __init__(self):
        self.learning_loop = learning_loop
        self.metrics = defaultdict(list)

    async def get_dashboard_metrics(self):
        """Get comprehensive metrics for dashboard"""

        # Basic metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'feedback_count': len(self.learning_loop.feedback_buffer),
            'insight_count': len(self.learning_loop.insights),
            'active_optimizations': await self.learning_loop.get_active_optimizations()
        }

        # Calculate trends
        metrics['trends'] = await self._calculate_trends()

        # Get intelligence source status
        metrics['intelligence_sources'] = await self._check_intelligence_sources()

        # Performance metrics
        metrics['performance'] = await self._get_performance_metrics()

        # Alert status
        metrics['alerts'] = await self._check_alerts()

        return metrics

    async def _calculate_trends(self):
        """Calculate performance trends"""
        trends = {}

        # Group feedback by hour
        hourly_feedback = defaultdict(list)
        for feedback in self.learning_loop.feedback_buffer:
            hour_key = feedback.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_feedback[hour_key].append(feedback.rating)

        # Calculate hourly averages
        for hour, ratings in hourly_feedback.items():
            trends[hour] = {
                'average_rating': sum(ratings) / len(ratings),
                'count': len(ratings)
            }

        return trends

    async def _check_intelligence_sources(self):
        """Check status of all intelligence sources"""
        sources = {}

        # Check Spider Army
        try:
            from backend.intelligence.spider_learning_orchestrator import get_spider_orchestrator
            orchestrator = get_spider_orchestrator()
            stats = await orchestrator.get_spider_statistics()
            sources['spider_army'] = {
                'status': 'active',
                'count': stats['summary']['total_deployed'],
                'signals': stats['summary']['signals_processed']
            }
        except:
            sources['spider_army'] = {'status': 'error'}

        # Check Bluesky
        try:
            from backend.intelligence.bluesky_learning_bridge import bluesky_learning_bridge
            sources['bluesky'] = {
                'status': 'active' if bluesky_learning_bridge else 'inactive'
            }
        except:
            sources['bluesky'] = {'status': 'error'}

        # Check Reddit
        try:
            from backend.intelligence.reddit_learning_bridge import get_reddit_learning_bridge
            bridge = get_reddit_learning_bridge()
            sources['reddit'] = {
                'status': 'active',
                'categories': len(bridge.subreddit_mapping)
            }
        except:
            sources['reddit'] = {'status': 'error'}

        return sources

    async def _check_alerts(self):
        """Check for system alerts"""
        alerts = []

        # Check feedback rate
        recent_feedback = [
            f for f in self.learning_loop.feedback_buffer
            if f.timestamp > datetime.now() - timedelta(minutes=10)
        ]

        if len(recent_feedback) == 0:
            alerts.append({
                'level': 'warning',
                'message': 'No feedback received in last 10 minutes'
            })

        # Check error rate
        error_feedback = [
            f for f in recent_feedback
            if f.category == 'error'
        ]

        if len(error_feedback) > len(recent_feedback) * 0.3:
            alerts.append({
                'level': 'critical',
                'message': f'High error rate: {len(error_feedback)}/{len(recent_feedback)}'
            })

        # Check performance degradation
        if recent_feedback:
            avg_rating = sum(f.rating for f in recent_feedback) / len(recent_feedback)
            if avg_rating < 0.5:
                alerts.append({
                    'level': 'warning',
                    'message': f'Low average performance: {avg_rating:.2f}'
                })

        return alerts
```

### Prometheus Metrics Export

```python
class PrometheusExporter:
    """Export learning loop metrics to Prometheus"""

    def __init__(self):
        self.learning_loop = learning_loop

    def get_metrics(self):
        """Get metrics in Prometheus format"""
        metrics = []

        # Feedback metrics
        metrics.append(f'learning_loop_feedback_total {len(self.learning_loop.feedback_buffer)}')

        # Category breakdown
        categories = defaultdict(int)
        for feedback in self.learning_loop.feedback_buffer:
            categories[feedback.category] += 1

        for category, count in categories.items():
            metrics.append(f'learning_loop_feedback_by_category{{category="{category}"}} {count}')

        # Average ratings
        if self.learning_loop.feedback_buffer:
            avg_rating = sum(f.rating for f in self.learning_loop.feedback_buffer) / len(self.learning_loop.feedback_buffer)
            metrics.append(f'learning_loop_average_rating {avg_rating:.3f}')

        # Insights
        metrics.append(f'learning_loop_insights_total {len(self.learning_loop.insights)}')

        # Active optimizations
        active_opts = asyncio.run(self.learning_loop.get_active_optimizations())
        metrics.append(f'learning_loop_active_optimizations {len(active_opts)}')

        return '\n'.join(metrics)
```

---

## Security Considerations

### Input Validation

```python
class SecureLearningLoop:
    """Security-hardened learning loop integration"""

    def __init__(self):
        self.learning_loop = learning_loop
        self.rate_limiter = {}
        self.blocked_sources = set()

    async def submit_feedback_secure(self, feedback):
        """Submit feedback with security checks"""

        # Validate source
        if feedback.source in self.blocked_sources:
            raise ValueError(f"Source {feedback.source} is blocked")

        # Rate limiting
        if not self._check_rate_limit(feedback.source):
            raise ValueError(f"Rate limit exceeded for {feedback.source}")

        # Validate rating range
        if not 0 <= feedback.rating <= 1:
            raise ValueError(f"Invalid rating: {feedback.rating}")

        # Sanitize message
        feedback.message = self._sanitize_message(feedback.message)

        # Validate context size
        if sys.getsizeof(feedback.context) > 10240:  # 10KB limit
            raise ValueError("Context too large")

        # Submit validated feedback
        self.learning_loop._store_feedback(feedback)

    def _check_rate_limit(self, source, max_per_minute=60):
        """Check rate limit for source"""
        current_time = datetime.now()

        if source not in self.rate_limiter:
            self.rate_limiter[source] = []

        # Remove old entries
        self.rate_limiter[source] = [
            t for t in self.rate_limiter[source]
            if (current_time - t).seconds < 60
        ]

        # Check limit
        if len(self.rate_limiter[source]) >= max_per_minute:
            return False

        # Add current request
        self.rate_limiter[source].append(current_time)
        return True

    def _sanitize_message(self, message):
        """Sanitize user-provided message"""
        # Remove any potential injection attempts
        import re
        # Remove SQL-like patterns
        message = re.sub(r'(DROP|DELETE|INSERT|UPDATE|SELECT)\s+', '', message, flags=re.IGNORECASE)
        # Remove script tags
        message = re.sub(r'<script[^>]*>.*?</script>', '', message, flags=re.IGNORECASE)
        # Limit length
        return message[:1000]
```

---

## Migration Guide

### Migrating from Custom Feedback Systems

```python
class FeedbackMigrator:
    """Migrate from legacy feedback system to learning loop"""

    def __init__(self):
        self.learning_loop = learning_loop

    async def migrate_legacy_feedback(self, legacy_data):
        """Migrate legacy feedback to new format"""
        migrated_count = 0

        for legacy_item in legacy_data:
            try:
                # Convert to new format
                feedback = self._convert_legacy_item(legacy_item)

                # Store in learning loop
                self.learning_loop._store_feedback(feedback)
                migrated_count += 1

            except Exception as e:
                logger.error(f"Failed to migrate item: {e}")

        logger.info(f"Migrated {migrated_count}/{len(legacy_data)} feedback items")
        return migrated_count

    def _convert_legacy_item(self, legacy):
        """Convert legacy format to FeedbackItem"""
        # Map legacy fields to new format
        return FeedbackItem(
            id=legacy.get('id', f"legacy_{datetime.now().timestamp()}"),
            timestamp=datetime.fromisoformat(legacy.get('date', datetime.now().isoformat())),
            source=legacy.get('source', 'legacy_system'),
            category=self._map_category(legacy.get('type')),
            target=legacy.get('component', 'unknown'),
            rating=self._normalize_rating(legacy.get('score')),
            message=legacy.get('comment', ''),
            context=legacy.get('metadata', {}),
            metadata={'migrated': True, 'original_format': 'legacy'}
        )

    def _map_category(self, legacy_type):
        """Map legacy types to new categories"""
        mapping = {
            'bug': 'error',
            'feature': 'usability',
            'speed': 'performance',
            'quality': 'accuracy'
        }
        return mapping.get(legacy_type, 'performance')

    def _normalize_rating(self, legacy_score):
        """Normalize legacy scores to 0-1 range"""
        if legacy_score is None:
            return 0.5
        # Assuming legacy used 1-5 scale
        return (legacy_score - 1) / 4
```

---

*This documentation is part of the Unified AI Platform with continuous learning capabilities powered by 1,770+ spiders, social intelligence, and real-time feedback processing.*