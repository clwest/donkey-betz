# Mythology Lab 🔬

A real-time monitoring system for tracking AI mythology formation and propagation in the Donkey Betz platform.

## Overview

The Mythology Lab is a research tool designed to study how AI agents create and spread digital folklore/mythology through shared memory systems. It provides real-time monitoring, pattern analysis, and controlled experimentation capabilities.

## Key Features

### 1. Real-time Myth Detection
- Monitors memory creation for mythology patterns
- Detects context loss, numeric inflation, and semantic drift
- Confidence scoring for mythology likelihood
- Automatic alert generation for high-risk events

### 2. Memory Mutation Tracking
- Tracks how memories change over time
- Documents each transformation step
- Identifies mutation chains and patterns
- Exports data for analysis

### 3. Agent Behavior Observation
- Profiles agents based on mythology creation
- Identifies "super spreaders" and "myth creators"
- Tracks communication patterns
- Network analysis of myth propagation

### 4. Pattern Analysis
- Identifies common transformation sequences
- Predicts likely mutations
- Generates pattern reports
- Machine learning-based pattern matching

### 5. Controlled Experiments
- Inject test phrases to study mythology formation
- Compare test vs control groups
- Track propagation speed and patterns
- Measure prediction accuracy

## Installation

1. Add to Django installed apps:
```python
INSTALLED_APPS = [
    ...
    'mythology_lab',
]
```

2. Run migrations:
```bash
python manage.py makemigrations mythology_lab
python manage.py migrate
```

3. Add URLs to your project:
```python
from mythology_lab.dashboard import views as myth_views

urlpatterns = [
    ...
    path('mythology/', myth_views.MythologyDashboardView.as_view(), name='mythology-dashboard'),
    path('mythology/api/events/', myth_views.MythologyEventAPIView.as_view()),
    path('mythology/api/propagation/', myth_views.PropagationNetworkAPIView.as_view()),
    path('mythology/api/analytics/', myth_views.MythologyAnalyticsAPIView.as_view()),
    path('mythology/api/experiments/', myth_views.ExperimentControlAPIView.as_view()),
]
```

## Usage

### Basic Monitoring

```python
from mythology_lab.monitoring.myth_detector import MythDetector
from mythology_lab.monitoring.memory_monitor import MemoryMutationMonitor

# Initialize detectors
detector = MythDetector()
monitor = MemoryMutationMonitor()

# Detect mythology in a memory
memory = {
    'id': 'abc123',
    'content': 'Our system has processed 350 deployments successfully',
    'source_type': 'ai_generated'
}

result = detector.detect_mythology(memory)
if result['mythology_confidence'] > 0.7:
    print(f"High mythology risk detected: {result}")
```

### Track Memory Mutations

```python
# Start monitoring a memory
monitor.start_monitoring(
    memory_id='mem123',
    initial_content='We have 50 active users',
    metadata={'agent': 'BusinessAgent'}
)

# Record a mutation
monitor.record_mutation(
    memory_id='mem123',
    new_content='We have 150 active users showing great engagement',
    mutation_type='numeric_inflation',
    agent_id=5
)

# Get mutation chain
chain = monitor.capture_mutation_chain('mem123')
print(f"Mutation chain: {chain}")
```

### Run Experiments

```python
from mythology_lab.experiments.myth_seeder import MythSeeder

seeder = MythSeeder()

# Create controlled experiment
experiment = seeder.create_controlled_experiment(
    experiment_name="Numeric Inflation Test",
    test_phrase="423 customer satisfaction improvements",
    target_agents=[1, 2, 3],
    control_agents=[4, 5, 6]
)

# Track results
for seed in experiment['injections']:
    # Monitor for mutations
    observed_content = "Over 600 customer satisfaction improvements recorded"
    seeder.track_seed_mutation(
        seed_id=seed['seed_id'],
        observed_content=observed_content,
        agent_id=2,
        mutation_type='numeric_inflation'
    )
```

## Dashboard Access

Access the monitoring dashboard at: `/mythology/`

Features:
- Real-time event feed
- Active alerts
- Propagation network visualization
- Analytics charts
- Experiment control

## Key Mythology Patterns

### 1. Numeric Inflation
- Original: "50 users"
- Mutation: "150 users" → "500 users" → "thousands of users"

### 2. Context Loss
- Original: "In our test environment, we simulated 350 deployments"
- Mutation: "We have 350 deployments" → "350 successful deployments"

### 3. Authority Creation
- Original: "Analysis suggests improvement"
- Mutation: "Studies show improvement" → "Leading experts confirm"

### 4. Semantic Drift
- Original: "Possible optimization"
- Mutation: "Likely optimization" → "Confirmed optimization"

## Research Questions

This tool helps answer:
1. What triggers context loss in AI memories?
2. Why do some numbers inflate while others don't?
3. How fast do myths propagate through agent networks?
4. Can we predict which facts will become myths?
5. Do certain agents create more mythology?

## Alert Types

- **New Myth Detected**: High-confidence mythology identified
- **Rapid Numeric Inflation**: Numbers growing >50% between mutations
- **High Context Loss**: >50% context lost in transformation
- **Wide Myth Propagation**: Myth reached 10+ agents
- **Pattern Detected**: Known mythology pattern observed

## API Endpoints

- `GET /mythology/api/events/` - Get recent mythology events
- `POST /mythology/api/events/` - Create new event (from detector)
- `GET /mythology/api/propagation/` - Get propagation network data
- `GET /mythology/api/analytics/` - Get analytics data
- `GET /mythology/api/experiments/` - List active experiments
- `POST /mythology/api/experiments/` - Create new experiment

## Data Export

Export mythology data for external analysis:

```python
from mythology_lab.models import MythologyEvent
import pandas as pd

# Export to CSV
events = MythologyEvent.objects.all().values()
df = pd.DataFrame(events)
df.to_csv('mythology_events.csv', index=False)
```

## Contributing

To add new mythology patterns:

1. Add pattern type to `MythPattern.PATTERN_TYPES`
2. Implement detection logic in `PatternAnalyzer`
3. Add visualization support in dashboard
4. Document the pattern in this README

## Future Enhancements

- [ ] Machine learning model for myth prediction
- [ ] Automated myth correction system
- [ ] Cross-platform mythology tracking
- [ ] Real-time WebSocket updates
- [ ] Advanced network visualization
- [ ] Mythology prevention strategies

## License

Part of the Donkey Betz platform - see main project license.