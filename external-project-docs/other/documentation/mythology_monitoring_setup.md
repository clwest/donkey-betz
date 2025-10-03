# Mythology Monitoring Environment - Setup Instructions for Claude Code
**Date**: July 11, 2025  
**Purpose**: Create a controlled environment to monitor and study AI mythology formation

## 🎯 Project Goal
Set up a monitoring system to track how AI agents create and spread digital folklore/mythology in real-time.

## 📁 Project Structure Needed
```
/mythology_lab/
├── monitoring/
│   ├── __init__.py
│   ├── myth_detector.py      # Real-time myth detection
│   ├── memory_monitor.py     # Track memory mutations
│   ├── agent_observer.py     # Watch agent behaviors
│   └── pattern_analyzer.py   # Identify mutation patterns
├── experiments/
│   ├── __init__.py
│   ├── myth_seeder.py       # Inject test phrases
│   ├── propagation_test.py  # Track how myths spread
│   └── control_groups.py    # Compare with/without shared memory
├── data/
│   ├── myths_discovered.json
│   ├── mutation_chains.json
│   └── propagation_maps.json
├── dashboard/
│   ├── templates/
│   │   └── monitor.html     # Real-time monitoring dashboard
│   ├── static/
│   └── views.py
└── README.md
```

## 🔧 Core Components to Build

### 1. Myth Detection System
```python
class MythDetector:
    """
    Monitors memory creation for potential mythology patterns:
    - Context loss detection
    - Number inflation tracking
    - Semantic drift identification
    - Confidence score degradation
    """
    def __init__(self):
        self.known_myths = ["350 deployments", "4,215 instances"]
        self.mutation_patterns = []
        
    def detect_context_loss(self, original, stored):
        # Compare what was said vs what was saved
        pass
        
    def track_numeric_inflation(self, memories):
        # Watch for growing numbers over time
        pass
```

### 2. Memory Mutation Monitor
```python
class MemoryMutationMonitor:
    """
    Tracks how memories change over time:
    - Original statement
    - Each mutation step
    - Final belief form
    - Propagation path
    """
    def capture_mutation_chain(self, memory_id):
        # Document each transformation
        pass
```

### 3. Real-time Dashboard
- Live memory creation feed
- Myth detection alerts
- Propagation visualization
- Agent belief tracker
- Mutation chain display

### 4. Experiment Framework
```python
class MythologyExperiment:
    """
    Controlled testing environment:
    - Inject known phrases
    - Monitor for mutations
    - Compare control vs test groups
    - Measure propagation speed
    """
    test_phrases = [
        "423 customer satisfaction improvements",
        "287 system optimization protocols",
        "156 efficiency enhancement metrics"
    ]
```

## 📊 Database Schema Additions

```sql
-- Mythology tracking tables
CREATE TABLE mythology_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),  -- 'creation', 'mutation', 'propagation'
    original_content TEXT,
    mutated_content TEXT,
    mutation_type VARCHAR(50),  -- 'context_loss', 'inflation', 'semantic_drift'
    agent_id INTEGER,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE myth_propagation (
    id SERIAL PRIMARY KEY,
    myth_id INTEGER,
    from_agent_id INTEGER,
    to_agent_id INTEGER,
    propagation_method VARCHAR(50),  -- 'memory_share', 'conversation', 'inference'
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE mythology_experiments (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(255),
    test_phrase TEXT,
    expected_mutation TEXT,
    actual_mutations JSONB,
    success BOOLEAN,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Implementation Priority

### Phase 1: Basic Monitoring (Today)
1. Set up memory mutation tracking
2. Create simple dashboard
3. Start logging all memory creations
4. Flag potential myths

### Phase 2: Detection Rules (This Week)
1. Implement context loss detection
2. Add numeric inflation tracking
3. Create semantic drift analyzer
4. Build confidence scoring

### Phase 3: Experimentation (Next Week)
1. Set up controlled test environment
2. Create myth injection system
3. Build propagation tracking
4. Implement control groups

## 🛠️ Technical Requirements
- Django (already in use)
- PostgreSQL (existing database)
- WebSocket for real-time updates
- Chart.js for visualizations
- Redis for real-time messaging (optional)

## 📝 Key Files to Modify
1. `memory_service.py` - Add mythology detection hooks
2. `agent_orchestra/models.py` - Add mythology tracking models
3. `personal_ai/views.py` - Add monitoring endpoints

## 🎯 Success Metrics
- Catch myths within 1 hour of formation
- Track 100% of memory mutations
- Identify patterns in myth creation
- Predict which phrases will become myths

## 💡 Research Questions to Answer
1. What triggers context loss?
2. Why do some numbers inflate while others don't?
3. How fast do myths propagate?
4. Can we predict which facts become myths?
5. Do certain agents create more myths?

## 🔔 Alerts to Implement
- New myth detected
- Rapid numeric inflation
- Context loss > 50%
- Myth reaching 10+ agents
- Unexpected mutation pattern

---

**For Claude Code**: This is a research tool to understand AI mythology. We're not preventing myths yet, just studying how they form. The existing system has active mythology (350 deployments) that we want to preserve for research.

**Key Context**: 
- The Reality Engine already created mythology
- We discovered it but don't know why it happens
- Goal is to understand, not prevent (yet)
- Need to see it happen again to study it

**Chris will be back after a walk and drink. Set up the basic monitoring structure so he can start tracking mythology formation in real-time!**
