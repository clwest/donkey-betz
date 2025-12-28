"""
Universal Intelligence Layer - The Brain of the Platform
Coordinates 102 agents with memory and embeddings for any domain
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import redis
import psycopg2
from pgvector.psycopg2 import register_vector
import openai
from collections import defaultdict

# Domain definitions
class Domain(Enum):
    SPORTS_BETTING = "sports_betting"
    DAY_TRADING = "day_trading"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    OPTIONS = "options"
    FOREX = "forex"
    NFT = "nft"
    COMMODITIES = "commodities"
    PREDICTION_MARKETS = "prediction_markets"
    VENTURE_CAPITAL = "venture_capital"

@dataclass
class DecisionContext:
    """Universal context for any decision across any domain"""
    domain: Domain
    entity_id: str  # game_id, stock_ticker, crypto_symbol, property_id
    timestamp: datetime
    data_points: Dict[str, Any]
    risk_level: float  # 0-1 scale
    time_horizon: str  # "minutes", "hours", "days", "weeks", "months"
    user_context: Dict[str, Any]
    market_conditions: Dict[str, Any]

@dataclass
class Memory:
    """Memory unit that can store any type of decision/outcome"""
    id: str
    context: DecisionContext
    decision_made: Dict[str, Any]
    outcome: Optional[Dict[str, Any]]
    embedding: Optional[np.ndarray]
    confidence_score: float
    agents_involved: List[int]
    patterns_detected: List[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResponse:
    """Standardized response from any agent"""
    agent_id: int
    agent_name: str
    confidence: float
    recommendation: str
    analysis: Dict[str, Any]
    supporting_memories: List[Memory]
    detected_patterns: List[str]
    risk_assessment: Dict[str, float]

class UniversalIntelligenceLayer:
    """
    The core intelligence system that orchestrates 102 agents
    with memory and embeddings across all domains
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = self._initialize_agents()
        self.redis_client = self._connect_redis()
        self.pg_conn = self._connect_postgres()
        self.embedding_dim = 1536  # OpenAI embedding dimension
        self.executor = ThreadPoolExecutor(max_workers=20)

        # Memory systems
        self.short_term_memory = {}  # In-memory for speed
        self.memory_index = defaultdict(list)  # Quick lookups by domain/entity

        # Agent specializations
        self.agent_domains = self._map_agent_domains()
        self.agent_capabilities = self._define_agent_capabilities()

        # Pattern library
        self.known_patterns = self._load_pattern_library()

    def _initialize_agents(self) -> Dict[int, Dict]:
        """Initialize all 102 agents with their specializations"""
        agents = {}

        # Define agent squads
        squads = {
            "alpha": list(range(1, 21)),      # Market Analysis Squadron
            "bravo": list(range(21, 41)),     # Sentiment & Social Squadron
            "charlie": list(range(41, 61)),   # Pattern Recognition Squadron
            "delta": list(range(61, 81)),     # Risk Assessment Squadron
            "echo": list(range(81, 103)),     # Execution & Optimization Squadron
        }

        for squad_name, agent_ids in squads.items():
            for agent_id in agent_ids:
                agents[agent_id] = {
                    "id": agent_id,
                    "squad": squad_name,
                    "name": f"Agent_{agent_id}_{squad_name.upper()}",
                    "status": "ready",
                    "specializations": self._get_agent_specializations(agent_id, squad_name),
                    "memory_access": True,
                    "embedding_capability": True,
                    "cross_domain": agent_id % 5 == 0,  # Every 5th agent works across domains
                }

        return agents

    def _get_agent_specializations(self, agent_id: int, squad: str) -> List[str]:
        """Define what each agent specializes in"""
        base_specs = {
            "alpha": ["price_analysis", "volume_analysis", "technical_indicators", "market_structure"],
            "bravo": ["sentiment_analysis", "news_processing", "social_signals", "crowd_psychology"],
            "charlie": ["pattern_matching", "anomaly_detection", "correlation_analysis", "trend_identification"],
            "delta": ["risk_calculation", "portfolio_impact", "downside_protection", "position_sizing"],
            "echo": ["execution_timing", "order_optimization", "slippage_minimization", "exit_strategy"],
        }

        specs = base_specs[squad].copy()

        # Add domain-specific specializations
        if agent_id <= 10:
            specs.append("sports_specialist")
        elif agent_id <= 20:
            specs.append("crypto_specialist")
        elif agent_id <= 30:
            specs.append("equities_specialist")
        elif agent_id <= 40:
            specs.append("options_specialist")
        elif agent_id <= 50:
            specs.append("forex_specialist")
        elif agent_id <= 60:
            specs.append("commodities_specialist")
        elif agent_id <= 70:
            specs.append("real_estate_specialist")
        elif agent_id <= 80:
            specs.append("macro_specialist")
        elif agent_id <= 90:
            specs.append("arbitrage_specialist")
        else:
            specs.append("meta_specialist")  # Agents that coordinate other agents

        return specs

    def _connect_redis(self):
        """Connect to Redis for short-term memory"""
        return redis.Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 0),
            decode_responses=True
        )

    def _connect_postgres(self):
        """Connect to PostgreSQL with pgvector for long-term memory"""
        conn = psycopg2.connect(
            host=self.config.get('pg_host', 'localhost'),
            port=self.config.get('pg_port', 5432),
            database=self.config.get('pg_database', 'intelligence'),
            user=self.config.get('pg_user', 'postgres'),
            password=self.config.get('pg_password', 'postgres')
        )
        register_vector(conn)
        self._ensure_tables_exist(conn)
        return conn

    def _ensure_tables_exist(self, conn):
        """Create necessary tables for intelligence system"""
        with conn.cursor() as cur:
            # Memory table with vector embeddings
            cur.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_memory (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    domain VARCHAR(50),
                    entity_id VARCHAR(255),
                    context_data JSONB,
                    decision_data JSONB,
                    outcome_data JSONB,
                    embedding vector(1536),
                    confidence_score FLOAT,
                    agents_involved INTEGER[],
                    patterns_detected TEXT[],
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    metadata JSONB
                );

                CREATE INDEX IF NOT EXISTS idx_memory_domain ON intelligence_memory(domain);
                CREATE INDEX IF NOT EXISTS idx_memory_entity ON intelligence_memory(entity_id);
                CREATE INDEX IF NOT EXISTS idx_memory_embedding ON intelligence_memory
                    USING ivfflat (embedding vector_cosine_ops);
            """)

            # Pattern library table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_patterns (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    pattern_name VARCHAR(255),
                    pattern_type VARCHAR(50),
                    domain VARCHAR(50),
                    description TEXT,
                    detection_rules JSONB,
                    success_rate FLOAT,
                    occurrences INTEGER DEFAULT 0,
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT NOW(),
                    metadata JSONB
                );

                CREATE INDEX IF NOT EXISTS idx_pattern_type ON intelligence_patterns(pattern_type);
                CREATE INDEX IF NOT EXISTS idx_pattern_domain ON intelligence_patterns(domain);
            """)

            # Agent performance tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS agent_performance (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    agent_id INTEGER,
                    domain VARCHAR(50),
                    decision_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    total_roi FLOAT DEFAULT 0,
                    avg_confidence FLOAT,
                    specialization_scores JSONB,
                    updated_at TIMESTAMP DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_agent_performance ON agent_performance(agent_id, domain);
            """)

            conn.commit()

    async def analyze(self, context: DecisionContext) -> Dict[str, Any]:
        """
        Main entry point for analysis - orchestrates all agents and memory
        """
        print(f"🧠 [Intelligence] Analyzing {context.domain.value} - {context.entity_id}")

        # 1. Embed the current context
        context_embedding = await self._embed_context(context)

        # 2. Search memory for similar scenarios
        similar_memories = await self._search_similar_memories(context_embedding, context.domain)

        # 3. Select relevant agents for this domain/context
        selected_agents = self._select_agents(context, similar_memories)

        # 4. Parallel agent analysis
        agent_responses = await self._orchestrate_agents(
            selected_agents,
            context,
            similar_memories
        )

        # 5. Synthesize insights from all agents
        synthesis = await self._synthesize_intelligence(
            agent_responses,
            context,
            similar_memories
        )

        # 6. Store this analysis in memory
        await self._store_memory(context, synthesis, agent_responses)

        # 7. Update pattern library if new patterns detected
        await self._update_patterns(agent_responses, context)

        return synthesis

    async def _embed_context(self, context: DecisionContext) -> np.ndarray:
        """Convert context into vector embedding"""
        # Serialize context to text for embedding
        context_text = self._serialize_context(context)

        # Get embedding from OpenAI (or your preferred model)
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=context_text
            )
            embedding = np.array(response['data'][0]['embedding'])
        except:
            # Fallback to random embedding for testing
            embedding = np.random.rand(self.embedding_dim)

        return embedding

    def _serialize_context(self, context: DecisionContext) -> str:
        """Convert context to text for embedding"""
        text_parts = [
            f"Domain: {context.domain.value}",
            f"Entity: {context.entity_id}",
            f"Risk Level: {context.risk_level}",
            f"Time Horizon: {context.time_horizon}",
        ]

        # Add key data points
        for key, value in context.data_points.items():
            text_parts.append(f"{key}: {value}")

        # Add market conditions
        for key, value in context.market_conditions.items():
            text_parts.append(f"Market {key}: {value}")

        return " | ".join(text_parts)

    async def _search_similar_memories(
        self,
        embedding: np.ndarray,
        domain: Domain,
        limit: int = 20
    ) -> List[Memory]:
        """Search for similar past scenarios using vector similarity"""
        with self.pg_conn.cursor() as cur:
            # Search across same domain and cross-domain memories
            cur.execute("""
                SELECT
                    id, domain, entity_id, context_data, decision_data,
                    outcome_data, confidence_score, agents_involved,
                    patterns_detected, created_at, metadata,
                    1 - (embedding <=> %s::vector) as similarity
                FROM intelligence_memory
                WHERE domain = %s OR domain = 'cross_domain'
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (embedding.tolist(), domain.value, embedding.tolist(), limit))

            memories = []
            for row in cur.fetchall():
                memory = Memory(
                    id=str(row[0]),
                    context=self._deserialize_context(row[3]),
                    decision_made=row[4],
                    outcome=row[5],
                    embedding=None,  # Don't need to load full embedding
                    confidence_score=row[6],
                    agents_involved=row[7] or [],
                    patterns_detected=row[8] or [],
                    timestamp=row[9],
                    metadata=row[10] or {}
                )
                memory.metadata['similarity'] = row[11]
                memories.append(memory)

        return memories

    def _select_agents(self, context: DecisionContext, memories: List[Memory]) -> List[int]:
        """Select the best agents for this specific context"""
        selected = set()

        # 1. Always include meta-coordinators
        selected.update(range(91, 103))  # Agents 91-102 are meta specialists

        # 2. Include domain specialists
        domain_specialists = {
            Domain.SPORTS_BETTING: range(1, 11),
            Domain.CRYPTO: range(11, 21),
            Domain.DAY_TRADING: range(21, 31),
            Domain.OPTIONS: range(31, 41),
            Domain.FOREX: range(41, 51),
            Domain.COMMODITIES: range(51, 61),
            Domain.REAL_ESTATE: range(61, 71),
        }

        if context.domain in domain_specialists:
            selected.update(domain_specialists[context.domain])

        # 3. Include agents that were successful in similar scenarios
        for memory in memories[:5]:  # Top 5 similar memories
            if memory.metadata.get('similarity', 0) > 0.8:
                selected.update(memory.agents_involved)

        # 4. Include pattern specialists if patterns detected
        if any('pattern' in str(m.patterns_detected) for m in memories):
            selected.update(range(41, 61))  # Charlie squad - pattern recognition

        # 5. Include risk specialists for high-risk contexts
        if context.risk_level > 0.7:
            selected.update(range(61, 81))  # Delta squad - risk assessment

        # Limit to 30 agents max for performance
        return list(selected)[:30]

    async def _orchestrate_agents(
        self,
        agent_ids: List[int],
        context: DecisionContext,
        memories: List[Memory]
    ) -> List[AgentResponse]:
        """Run selected agents in parallel"""
        tasks = []
        for agent_id in agent_ids:
            task = self._run_agent(agent_id, context, memories)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return [r for r in responses if r is not None]

    async def _run_agent(
        self,
        agent_id: int,
        context: DecisionContext,
        memories: List[Memory]
    ) -> Optional[AgentResponse]:
        """Execute a single agent's analysis"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        # Simulate agent processing (replace with actual agent logic)
        await asyncio.sleep(0.1)  # Simulate processing time

        # Agent analyzes based on its specializations
        analysis = {}
        patterns = []
        confidence = 0.5

        for spec in agent['specializations']:
            if 'specialist' in spec:
                confidence += 0.1
            if 'pattern' in spec:
                patterns.append(f"Pattern_{agent_id}_{context.domain.value}")

        # Generate recommendation based on agent type
        if agent['squad'] == 'alpha':
            recommendation = "Market conditions favorable"
        elif agent['squad'] == 'bravo':
            recommendation = "Sentiment is positive"
        elif agent['squad'] == 'charlie':
            recommendation = f"Pattern detected: {patterns[0] if patterns else 'None'}"
        elif agent['squad'] == 'delta':
            recommendation = f"Risk level: {context.risk_level:.2f}"
        else:
            recommendation = "Execute with caution"

        return AgentResponse(
            agent_id=agent_id,
            agent_name=agent['name'],
            confidence=min(confidence, 1.0),
            recommendation=recommendation,
            analysis=analysis,
            supporting_memories=memories[:3],
            detected_patterns=patterns,
            risk_assessment={'overall': context.risk_level}
        )

    async def _synthesize_intelligence(
        self,
        agent_responses: List[AgentResponse],
        context: DecisionContext,
        memories: List[Memory]
    ) -> Dict[str, Any]:
        """Synthesize all agent responses into unified intelligence"""

        # Aggregate recommendations
        recommendations = defaultdict(int)
        total_confidence = 0
        all_patterns = set()
        risk_scores = []

        for response in agent_responses:
            recommendations[response.recommendation] += response.confidence
            total_confidence += response.confidence
            all_patterns.update(response.detected_patterns)
            risk_scores.append(response.risk_assessment.get('overall', 0.5))

        # Calculate consensus
        avg_confidence = total_confidence / len(agent_responses) if agent_responses else 0
        avg_risk = np.mean(risk_scores) if risk_scores else 0.5

        # Find historical performance for similar scenarios
        historical_success_rate = self._calculate_historical_success(memories)

        # Generate final synthesis
        synthesis = {
            "timestamp": datetime.now().isoformat(),
            "domain": context.domain.value,
            "entity": context.entity_id,
            "consensus": {
                "confidence": avg_confidence,
                "risk_score": avg_risk,
                "recommendation": max(recommendations.items(), key=lambda x: x[1])[0] if recommendations else "No consensus",
                "agreement_level": len(recommendations) / len(agent_responses) if agent_responses else 0
            },
            "agent_analysis": {
                "total_agents": len(agent_responses),
                "by_squad": self._group_by_squad(agent_responses),
                "top_insights": self._extract_top_insights(agent_responses),
            },
            "patterns": {
                "detected": list(all_patterns),
                "count": len(all_patterns),
                "historical_match": self._match_historical_patterns(all_patterns, memories)
            },
            "memory_context": {
                "similar_scenarios": len(memories),
                "avg_similarity": np.mean([m.metadata.get('similarity', 0) for m in memories]) if memories else 0,
                "historical_success_rate": historical_success_rate,
                "best_past_outcome": self._get_best_outcome(memories)
            },
            "actionable_intelligence": self._generate_actionable_intelligence(
                agent_responses, memories, context
            ),
            "meta_analysis": {
                "cross_domain_insights": self._extract_cross_domain_insights(memories),
                "confidence_factors": self._analyze_confidence_factors(agent_responses),
                "risk_factors": self._analyze_risk_factors(agent_responses, context)
            }
        }

        return synthesis

    def _calculate_historical_success(self, memories: List[Memory]) -> float:
        """Calculate success rate from similar past scenarios"""
        if not memories:
            return 0.5

        successes = 0
        total = 0

        for memory in memories:
            if memory.outcome:
                total += 1
                if memory.outcome.get('success', False):
                    successes += 1

        return successes / total if total > 0 else 0.5

    def _group_by_squad(self, responses: List[AgentResponse]) -> Dict[str, Any]:
        """Group agent responses by squad"""
        squads = defaultdict(list)
        for response in responses:
            agent = self.agents.get(response.agent_id)
            if agent:
                squads[agent['squad']].append({
                    'agent_id': response.agent_id,
                    'confidence': response.confidence,
                    'recommendation': response.recommendation
                })
        return dict(squads)

    def _extract_top_insights(self, responses: List[AgentResponse], limit: int = 5) -> List[Dict]:
        """Extract the most confident insights"""
        sorted_responses = sorted(responses, key=lambda x: x.confidence, reverse=True)
        insights = []

        for response in sorted_responses[:limit]:
            insights.append({
                'agent': response.agent_name,
                'insight': response.recommendation,
                'confidence': response.confidence,
                'patterns': response.detected_patterns[:3]
            })

        return insights

    def _generate_actionable_intelligence(
        self,
        responses: List[AgentResponse],
        memories: List[Memory],
        context: DecisionContext
    ) -> Dict[str, Any]:
        """Generate specific actionable recommendations"""

        # Determine action based on consensus and risk
        high_confidence = [r for r in responses if r.confidence > 0.7]
        low_risk = [r for r in responses if r.risk_assessment.get('overall', 0.5) < 0.3]

        if len(high_confidence) > len(responses) * 0.6:
            action = "STRONG_EXECUTE"
            urgency = "high"
        elif len(low_risk) > len(responses) * 0.5:
            action = "EXECUTE"
            urgency = "medium"
        else:
            action = "WAIT"
            urgency = "low"

        # Calculate position sizing
        kelly_fraction = self._calculate_kelly_criterion(responses, memories)

        return {
            "primary_action": action,
            "urgency": urgency,
            "position_size": {
                "kelly_percentage": kelly_fraction,
                "recommended_units": max(1, int(kelly_fraction * 10)),
                "max_risk": context.risk_level * 0.02  # 2% max risk per position
            },
            "timing": {
                "optimal_entry": "immediate" if urgency == "high" else "wait_for_confirmation",
                "time_window": context.time_horizon
            },
            "exit_strategy": {
                "take_profit": self._calculate_take_profit(responses, context),
                "stop_loss": self._calculate_stop_loss(responses, context),
                "trailing_stop": context.risk_level < 0.5
            },
            "hedging": {
                "recommended": context.risk_level > 0.7,
                "hedge_ratio": min(0.5, context.risk_level - 0.5) if context.risk_level > 0.7 else 0
            }
        }

    def _calculate_kelly_criterion(
        self,
        responses: List[AgentResponse],
        memories: List[Memory]
    ) -> float:
        """Calculate Kelly Criterion for position sizing"""
        # Simplified Kelly calculation
        win_prob = np.mean([r.confidence for r in responses])
        historical_win_rate = self._calculate_historical_success(memories)

        # Blend current confidence with historical success
        p = (win_prob + historical_win_rate) / 2
        q = 1 - p
        b = 1  # Assuming 1:1 odds for simplicity

        kelly = (p * b - q) / b if b > 0 else 0

        # Apply fractional Kelly for safety (25% of full Kelly)
        return max(0, min(0.25, kelly * 0.25))

    async def _store_memory(
        self,
        context: DecisionContext,
        synthesis: Dict[str, Any],
        agent_responses: List[AgentResponse]
    ):
        """Store the current analysis in memory for future reference"""
        # Store in short-term memory (Redis)
        memory_key = f"memory:{context.domain.value}:{context.entity_id}:{datetime.now().timestamp()}"
        self.redis_client.setex(
            memory_key,
            3600,  # Expire after 1 hour
            json.dumps(synthesis)
        )

        # Store in long-term memory (PostgreSQL)
        embedding = await self._embed_context(context)
        agent_ids = [r.agent_id for r in agent_responses]
        patterns = list(set(p for r in agent_responses for p in r.detected_patterns))

        with self.pg_conn.cursor() as cur:
            cur.execute("""
                INSERT INTO intelligence_memory
                (domain, entity_id, context_data, decision_data, embedding,
                 confidence_score, agents_involved, patterns_detected, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                context.domain.value,
                context.entity_id,
                json.dumps(self._serialize_context_dict(context)),
                json.dumps(synthesis),
                embedding.tolist(),
                synthesis['consensus']['confidence'],
                agent_ids,
                patterns,
                json.dumps({"timestamp": datetime.now().isoformat()})
            ))
            self.pg_conn.commit()

    def _serialize_context_dict(self, context: DecisionContext) -> Dict:
        """Convert context to dictionary for storage"""
        return {
            "domain": context.domain.value,
            "entity_id": context.entity_id,
            "timestamp": context.timestamp.isoformat(),
            "data_points": context.data_points,
            "risk_level": context.risk_level,
            "time_horizon": context.time_horizon,
            "user_context": context.user_context,
            "market_conditions": context.market_conditions
        }

    def _deserialize_context(self, data: Dict) -> DecisionContext:
        """Recreate context from stored data"""
        return DecisionContext(
            domain=Domain(data.get('domain', 'sports_betting')),
            entity_id=data.get('entity_id', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            data_points=data.get('data_points', {}),
            risk_level=data.get('risk_level', 0.5),
            time_horizon=data.get('time_horizon', 'hours'),
            user_context=data.get('user_context', {}),
            market_conditions=data.get('market_conditions', {})
        )

    # Additional helper methods
    def _map_agent_domains(self) -> Dict[Domain, List[int]]:
        """Map domains to specialized agents"""
        return {
            Domain.SPORTS_BETTING: list(range(1, 11)) + list(range(91, 103)),
            Domain.CRYPTO: list(range(11, 21)) + list(range(91, 103)),
            Domain.DAY_TRADING: list(range(21, 31)) + list(range(91, 103)),
            Domain.OPTIONS: list(range(31, 41)) + list(range(91, 103)),
            Domain.FOREX: list(range(41, 51)) + list(range(91, 103)),
            Domain.COMMODITIES: list(range(51, 61)) + list(range(91, 103)),
            Domain.REAL_ESTATE: list(range(61, 71)) + list(range(91, 103)),
        }

    def _define_agent_capabilities(self) -> Dict[str, List[str]]:
        """Define what each agent squad can do"""
        return {
            "alpha": ["market_analysis", "price_discovery", "liquidity_assessment", "order_flow"],
            "bravo": ["sentiment_extraction", "news_impact", "social_momentum", "crowd_dynamics"],
            "charlie": ["pattern_recognition", "anomaly_detection", "cycle_analysis", "correlation_mapping"],
            "delta": ["risk_quantification", "drawdown_analysis", "var_calculation", "stress_testing"],
            "echo": ["execution_optimization", "timing_analysis", "slippage_reduction", "exit_planning"]
        }

    def _load_pattern_library(self) -> Dict[str, Any]:
        """Load known patterns from database"""
        patterns = {}
        with self.pg_conn.cursor() as cur:
            cur.execute("SELECT pattern_name, detection_rules, success_rate FROM intelligence_patterns")
            for row in cur.fetchall():
                patterns[row[0]] = {
                    'rules': row[1],
                    'success_rate': row[2]
                }
        return patterns

    async def _update_patterns(self, responses: List[AgentResponse], context: DecisionContext):
        """Update pattern library with newly detected patterns"""
        new_patterns = set()
        for response in responses:
            new_patterns.update(response.detected_patterns)

        for pattern in new_patterns:
            if pattern not in self.known_patterns:
                # Add new pattern to library
                with self.pg_conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO intelligence_patterns
                        (pattern_name, pattern_type, domain, occurrences)
                        VALUES (%s, %s, %s, 1)
                        ON CONFLICT (pattern_name)
                        DO UPDATE SET occurrences = intelligence_patterns.occurrences + 1
                    """, (pattern, 'detected', context.domain.value))
                    self.pg_conn.commit()

    def _match_historical_patterns(self, patterns: set, memories: List[Memory]) -> Dict:
        """Match current patterns with historical occurrences"""
        matches = {}
        for pattern in patterns:
            occurrences = 0
            success_rate = 0
            for memory in memories:
                if pattern in memory.patterns_detected:
                    occurrences += 1
                    if memory.outcome and memory.outcome.get('success'):
                        success_rate += 1

            matches[pattern] = {
                'occurrences': occurrences,
                'success_rate': success_rate / occurrences if occurrences > 0 else 0
            }
        return matches

    def _get_best_outcome(self, memories: List[Memory]) -> Optional[Dict]:
        """Find the best historical outcome from similar scenarios"""
        best_outcome = None
        best_roi = float('-inf')

        for memory in memories:
            if memory.outcome:
                roi = memory.outcome.get('roi', 0)
                if roi > best_roi:
                    best_roi = roi
                    best_outcome = memory.outcome

        return best_outcome

    def _extract_cross_domain_insights(self, memories: List[Memory]) -> List[Dict]:
        """Extract insights that apply across domains"""
        cross_domain = []
        domains_seen = set()

        for memory in memories:
            if memory.context.domain != memories[0].context.domain:
                domains_seen.add(memory.context.domain)
                cross_domain.append({
                    'domain': memory.context.domain.value,
                    'similarity': memory.metadata.get('similarity', 0),
                    'outcome': memory.outcome
                })

        return cross_domain[:5]  # Top 5 cross-domain insights

    def _analyze_confidence_factors(self, responses: List[AgentResponse]) -> Dict:
        """Analyze what's driving confidence levels"""
        factors = {
            'high_confidence': [],
            'low_confidence': [],
            'consensus_level': 0
        }

        high_conf = [r for r in responses if r.confidence > 0.7]
        low_conf = [r for r in responses if r.confidence < 0.3]

        factors['high_confidence'] = [r.agent_name for r in high_conf[:3]]
        factors['low_confidence'] = [r.agent_name for r in low_conf[:3]]
        factors['consensus_level'] = len(high_conf) / len(responses) if responses else 0

        return factors

    def _analyze_risk_factors(self, responses: List[AgentResponse], context: DecisionContext) -> List[str]:
        """Identify key risk factors"""
        risks = []

        if context.risk_level > 0.7:
            risks.append("High inherent risk level")

        high_risk_agents = [r for r in responses if r.risk_assessment.get('overall', 0) > 0.7]
        if len(high_risk_agents) > len(responses) * 0.3:
            risks.append(f"{len(high_risk_agents)} agents flagged high risk")

        if context.time_horizon == "minutes":
            risks.append("Very short time horizon increases execution risk")

        return risks

    def _calculate_take_profit(self, responses: List[AgentResponse], context: DecisionContext) -> float:
        """Calculate recommended take profit level"""
        # Simple calculation - can be made more sophisticated
        base_target = 0.02  # 2% base target

        # Adjust based on confidence
        avg_confidence = np.mean([r.confidence for r in responses])

        # Higher confidence = higher targets
        return base_target * (1 + avg_confidence)

    def _calculate_stop_loss(self, responses: List[AgentResponse], context: DecisionContext) -> float:
        """Calculate recommended stop loss level"""
        # Risk-based stop loss
        return context.risk_level * 0.01  # 1% per risk unit

# Example usage
async def main():
    config = {
        'redis_host': 'localhost',
        'pg_host': 'localhost',
        'pg_database': 'unified_donkey_betz'
    }

    intelligence = UniversalIntelligenceLayer(config)

    # Example: Analyze a sports betting opportunity
    context = DecisionContext(
        domain=Domain.SPORTS_BETTING,
        entity_id="game_123",
        timestamp=datetime.now(),
        data_points={
            "home_team": "Lakers",
            "away_team": "Warriors",
            "spread": -3.5,
            "total": 220.5,
            "moneyline_home": -150,
            "moneyline_away": +130
        },
        risk_level=0.6,
        time_horizon="hours",
        user_context={"bankroll": 10000, "unit_size": 100},
        market_conditions={"volatility": "medium", "volume": "high"}
    )

    result = await intelligence.analyze(context)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())