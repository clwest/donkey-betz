<!-- DOC-POINTER-V1 (Session 1145) -->
> **⚠ Aspirational architecture / not implemented as specified.** The M3 + Apple MLX + scikit-learn ML stack described here was an exploration design from Jan 2026; the current ML reality lives in the agent-system body-systems architecture, not in a separate MLX pipeline. Do not treat this doc as current system state.
> **Last reviewed for drift labeling:** Session 1145 (2026-05-25)
> **Current truth:** [`docs/topics/body-systems.md`](../topics/body-systems.md) (9 health systems + BodyCoordinator) + [`docs/topics/agent-system.md`](../topics/agent-system.md) (current agent architecture) + [`docs/PLATFORM_INVENTORY.md`](../PLATFORM_INVENTORY.md) (runtime ML/agent stats).
> **Note:** Preserved as exploration/rejected-approach context. Specific performance targets, model choices (DistilBERT local, FinBERT, etc.), and "Digital Twin" framings do not match what was built. The active ML touchpoints today are governed by `MLEngine` (deadlock fix in Session 1085 #1871) + body-systems coordinator.

# ML Pipeline Architecture - M3 MacBook Pro Optimized

## System Specifications
- **Hardware:** M3 MacBook Pro, 18GB RAM
- **Primary:** Local ML processing with Apple's Neural Engine
- **Secondary:** HuggingFace API for specialized tasks
- **Storage:** Local SQLite + PostgreSQL for historical data

## Architecture Overview

### 🏠 LOCAL ML STACK (Primary - 80% of workload)

#### 1. Pattern Recognition Models
**Apple MLX Framework (M3 optimized)**
```python
# Sports → Crypto Pattern Detection
- LSTM/GRU models for time series correlation
- Model size: ~500MB-2GB (fits comfortably in memory)
- Inference: <50ms latency
- Training: On historical NBA/crypto data

# Options IV → Sports Betting Edge
- Custom neural network for volatility transfer
- Real-time feature extraction from market data
- Model size: ~1GB
```

#### 2. User Behavior Learning (100% Local - Privacy First)
**scikit-learn + Custom Models**
```python
# Digital Twin Development
- Track every decision you make
- Learn your risk tolerance patterns
- Personal confidence scoring
- SQLite database (never leaves your machine)

# Models:
- Random Forest for decision pattern recognition
- Gradient Boosting for confidence calibration
- Clustering for opportunity similarity detection
```

#### 3. Real-Time Market Processing
**Apple Core ML + MLX**
```python
# Live Data Processing
- News sentiment analysis (DistilBERT locally)
- Market volatility pattern detection
- Real-time opportunity scoring
- Cross-domain signal correlation

# Performance Target:
- <100ms end-to-end latency
- Process 1000+ data points/second
```

### ☁️ HUGGINGFACE INTEGRATION (Strategic - 20% of workload)

#### When to Use HuggingFace API:
1. **Complex NLP Analysis**
   - Earnings call sentiment (need 70B+ models)
   - SEC filing analysis
   - Social media whale detection

2. **Specialized Financial Models**
   - FinBERT for advanced financial text
   - Sector-specific pattern recognition
   - Complex correlation analysis

3. **Model Training Support**
   - Transfer learning from pre-trained models
   - Feature extraction for local models
   - Validation against state-of-the-art models

## Implementation Stack

### Local Development Environment
```bash
# Apple ML Stack
pip install mlx
pip install coremltools
pip install tensorflow-macos
pip install tensorflow-metal

# Data Processing
pip install pandas numpy scipy
pip install scikit-learn
pip install pytorch

# Market Data
pip install yfinance alpha_vantage
pip install ccxt  # Crypto exchanges
pip install requests beautifulsoup4
```

### Model Deployment Strategy
```python
# Local Model Serving
FastAPI server running on localhost
- Real-time inference endpoints
- Model versioning and A/B testing
- Performance monitoring

# Integration with Django Backend
- ML predictions via internal API
- WebSocket streaming for live updates
- Redis cache for model outputs
```

## Data Flow Architecture

### 1. Data Ingestion (Local)
```
Sports API → Market Data → News Feeds
           ↓
    Feature Engineering (M3)
           ↓
    Local ML Models (MLX/Core ML)
           ↓
    Decision Scoring & Ranking
```

### 2. Cross-Domain Pattern Detection
```
NBA Injury News → Sentiment Analysis (Local)
                ↓
        Pattern Matching (Local LSTM)
                ↓
        BTC Volatility Prediction
                ↓
        Confidence Score (Your Digital Twin)
```

### 3. User Learning Loop
```
Your Decision → Feature Extraction → Local Model Update
     ↓                                      ↑
Outcome Tracking → Performance Analysis → Model Retraining
```

## Performance Targets

### Local Processing
- **Inference Latency:** <100ms
- **Memory Usage:** <8GB (leave 10GB for system)
- **Model Loading:** <5 seconds
- **Training Time:** <30 minutes per model

### HuggingFace Integration
- **API Calls:** <100/day (cost optimization)
- **Response Time:** <2 seconds
- **Fallback:** Local models if API unavailable
- **Caching:** 24-hour Redis cache for expensive calls

## Security & Privacy

### Local Data Protection
- All personal decision data stays local
- SQLite encryption for sensitive patterns
- No decision data sent to external APIs
- Your "Digital Twin" remains private

### API Security
- HuggingFace tokens in environment variables
- Rate limiting and error handling
- No personal data in API requests
- Anonymized market data only

## Scalability Plan

### Phase 1: Local MVP (Current)
- Basic pattern recognition
- Simple user behavior tracking
- Local inference only

### Phase 2: Hybrid Intelligence (Next 30 days)
- HuggingFace integration for complex analysis
- Advanced cross-domain correlation
- Real-time opportunity detection

### Phase 3: Production Scale (Future)
- Model ensemble strategies
- Automated retraining pipelines
- Multi-model confidence scoring

## ROI Metrics

### Performance Tracking
- Decision accuracy improvement over time
- Cross-domain pattern success rates
- Personal confidence calibration accuracy
- System response time and reliability

### Business Impact
- Opportunity detection speed
- False positive reduction
- Decision confidence improvement
- Automated vs manual decision success rates