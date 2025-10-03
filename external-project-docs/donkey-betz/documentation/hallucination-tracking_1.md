  Hallucination Tracking system:

  How Does It Detect Hallucinations?

  The system uses multiple sophisticated methods to detect AI hallucinations:

  1. Pattern-Based Detection (backend/mythology_lab/monitoring/myth_detector.py:21-38)

  - Numeric Inflation: Detects when numbers grow by >50% between iterations
  - Mythic Language Markers: Identifies words like "hypothetical", "estimated", "approximately"
  - Known Myths Database: Checks against specific known hallucinations like "350 deployments"
  - False Authority Patterns: Catches phrases like "studies show" without sources
  - Context Loss Detection: Compares original vs stored content for information loss

  2. Semantic Analysis (myth_detector.py:108-146)

  - Tracks how meaning changes across memory chains
  - Calculates semantic drift using SequenceMatcher algorithms
  - Identifies transformation steps where significant changes occur
  - Monitors when "mythic language" gets introduced

  3. Confidence Scoring (myth_detector.py:148-186)

  - Calculates mythology likelihood on 0-1 scale
  - Factors include:
    - Presence of known myths (+0.3)
    - Mythic language markers (+0.1 per marker)
    - Large numbers (>1000: +0.2, >100: +0.1)
    - AI-generated source flag (+0.1)
    - Fiction metadata flag (+0.3)

  What Happens When a Hallucination is Detected?

  1. Event Creation & Logging (models.py:10-64)

  Each detected hallucination creates a MythologyEvent with:
  - Event type (creation, mutation, propagation, detection)
  - Original and mutated content
  - Mutation type (context loss, inflation, semantic drift, etc.)
  - Agent ID and name that created it
  - LLM provider and model information
  - Confidence score
  - Timestamp and metadata

  2. Propagation Tracking (models.py:67-127)

  The system tracks how myths spread via MythPropagation records:
  - Source and destination agents
  - LLM models involved (cross-model tracking)
  - Propagation method (memory share, conversation, inference, retrieval)
  - Generation number (how many hops from origin)
  - Whether it's cross-model propagation

  3. Pattern Analysis (multi_llm_mythology_tracker.py)

  - Builds propagation networks showing myth spread
  - Calculates model susceptibility scores
  - Identifies "super-spreader" models
  - Tracks mutation chains and evolution

  4. Real-Time Alerts (models.py:174-211)

  The system generates MythologyAlert records for:
  - High-confidence mythology detections
  - Rapid propagation events
  - Cross-model contamination
  - Pattern threshold violations

  The Learning Loop

  1. Mythology Guard System (mythology_guard.py)

  The system has proactive prevention mechanisms:

  - Pre-Generation Guards (mythology_guard.py:44-86):
    - Validates prompts for mythology patterns
    - Injects anti-mythology instructions when risk >0.3
    - Applies strong guards when risk >0.6
    - Instructions include: "Base all responses on verified data only"
  - Post-Generation Validation (mythology_guard.py:195-243):
    - Validates responses after generation
    - Checks for context loss between prompt and response
    - Suggests corrections for detected myths
    - Flags responses needing regeneration (risk >0.7)

  2. Learning Mechanisms:

  - Template Learning (mythology_guard.py:174-193):
    - Tracks mythology incidents per prompt template
    - Updates guard effectiveness metrics
    - Adjusts detection patterns based on success rates
  - Agent Mythology Profiles (mentioned in models):
    - Each agent has a mythology behavior profile
    - Tracks susceptibility to different myth types
    - Used to adjust agent prompts and guards
  - Pattern Database Growth:
    - New mythology patterns are added to detection
    - Successful mutations are tracked for future prevention
    - Cross-model patterns are identified and catalogued

  3. Integration with Bidirectional Learning:

  The mythology system integrates with the broader learning system:

  - Memory System Integration:
    - Mythology events are stored in the memory palace
    - Agents can query for known myths to avoid
    - Context includes mythology warnings
  - Cross-Domain Adapter:
    - Mythology patterns are shared across domains
    - Successful prevention strategies are propagated
    - Domain-specific mythology patterns are identified
  - Feedback Loop:
    - User corrections update mythology database
    - Successful detections strengthen pattern matching
    - Failed detections trigger pattern refinement

  Key Features:

  1. Multi-Model Tracking: Tracks how hallucinations spread between different LLM providers (OpenAI, Anthropic, etc.)
  2. Controlled Experiments: Can run experiments to test mythology creation and propagation patterns
  3. Real-Time Dashboard: Frontend visualization showing:
    - Live mythology event feed
    - Propagation network graphs
    - Model susceptibility scores
    - Analytics and metrics
  4. Prevention > Detection: The system prioritizes preventing hallucinations through prompt engineering and guards
  rather than just detecting them after the fact

  This system represents a sophisticated approach to one of AI's most challenging problems - preventing the creation
  and spread of plausible-sounding but false information across multi-agent systems.