"""
Intelligent Job Matcher with ML Learning and Memory

This enhanced system uses machine learning, embeddings, and memory to:
- Learn from successful/failed applications
- Remember which agents work best for which job types
- Improve matching over time
- Use embeddings to understand job requirements deeply

Features:
- Embedding-based semantic job matching
- ML model that learns from application outcomes
- Memory system that tracks agent performance
- Continuous improvement through feedback loops
"""

import logging
import json
import numpy as np
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class JobApplicationMemory:
    """Memory of a job application and its outcome"""
    application_id: str
    job_id: str
    job_title: str
    job_embedding: List[float]
    agent_id: str
    agent_name: str
    match_score: float
    applied_at: datetime
    outcome: str = "pending"  # pending, interview, rejected, hired
    feedback_score: float = 0.0
    learned_features: Dict[str, Any] = field(default_factory=dict)


class IntelligentJobMatcher:
    """
    Advanced job matching system with ML and memory capabilities
    """

    def __init__(self):
        # Import all our powerful systems
        from agents.registry import agent_registry
        from ml_pipeline.enhanced_ml_pipeline import EnhancedMLPipeline
        from core.memory_system import MemorySystem

        self.agent_registry = agent_registry
        self.ml_pipeline = EnhancedMLPipeline()
        self.memory = MemorySystem()

        # Initialize embeddings
        self._initialize_embeddings()

        # Application memory
        self.application_memory: Dict[str, JobApplicationMemory] = {}

        # Learning metrics
        self.agent_success_rates = {}
        self.job_type_patterns = {}
        self.skill_importance_weights = {}

        logger.info("🧠 Intelligent Job Matcher initialized with ML and Memory systems")

    def _initialize_embeddings(self):
        """Initialize embedding models"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load embedding model: {e}")
            self.embedder = None

    async def match_job_with_learning(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match a job to the best agent using ML and historical learning

        Args:
            job: Job opportunity details

        Returns:
            Best match with agent and confidence score
        """
        # Generate job embedding
        job_embedding = await self._get_job_embedding(job)

        # Search memory for similar successful applications
        similar_successes = await self._find_similar_successful_applications(job_embedding)

        # Get all agents and score them
        agent_scores = []

        for agent_id, agent in self.agent_registry.agents.items():
            # Base score from agent capabilities
            base_score = await self._calculate_base_agent_score(agent, job)

            # ML-enhanced score using historical performance
            ml_score = await self._calculate_ml_score(agent_id, job, job_embedding)

            # Memory-based adjustments
            memory_score = await self._calculate_memory_score(agent_id, similar_successes)

            # Combined score with weights
            final_score = (
                base_score * 0.3 +  # Agent capabilities
                ml_score * 0.4 +    # ML predictions
                memory_score * 0.3   # Historical success
            )

            agent_scores.append({
                'agent_id': agent_id,
                'agent': agent,
                'base_score': base_score,
                'ml_score': ml_score,
                'memory_score': memory_score,
                'final_score': final_score,
                'confidence': self._calculate_confidence(base_score, ml_score, memory_score)
            })

        # Sort by final score
        agent_scores.sort(key=lambda x: x['final_score'], reverse=True)
        best_match = agent_scores[0] if agent_scores else None

        if best_match:
            # Store this matching decision in memory
            await self._store_matching_decision(job, best_match, job_embedding)

            # Log the learning
            logger.info(f"""
            🎯 Intelligent Match Found:
               Job: {job.get('title')}
               Agent: {best_match['agent'].get('name')}
               Scores: Base={best_match['base_score']:.2f}, ML={best_match['ml_score']:.2f}, Memory={best_match['memory_score']:.2f}
               Final Score: {best_match['final_score']:.2f}
               Confidence: {best_match['confidence']:.1%}
            """)

            return {
                'agent_id': best_match['agent_id'],
                'agent': best_match['agent'],
                'match_score': best_match['final_score'],
                'confidence': best_match['confidence'],
                'reasoning': {
                    'base_score': best_match['base_score'],
                    'ml_score': best_match['ml_score'],
                    'memory_score': best_match['memory_score']
                }
            }

        return None

    async def _get_job_embedding(self, job: Dict[str, Any]) -> np.ndarray:
        """Generate embedding for a job"""
        if not self.embedder:
            # Fallback to simple feature vector
            return self._create_simple_feature_vector(job)

        # Combine all job text
        job_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('tags', []))}"

        # Generate embedding
        embedding = self.embedder.encode(job_text)

        # Store in memory for fast retrieval
        await self.memory.store_embedding(
            key=f"job_{job.get('id', job.get('url', ''))}",
            embedding=embedding.tolist(),
            metadata=job
        )

        return embedding

    async def _find_similar_successful_applications(self, job_embedding: np.ndarray) -> List[JobApplicationMemory]:
        """Find similar successful applications from memory"""
        similar_apps = []

        for app_id, app_memory in self.application_memory.items():
            if app_memory.outcome in ['interview', 'hired']:
                # Calculate similarity
                similarity = self._calculate_similarity(
                    job_embedding,
                    np.array(app_memory.job_embedding)
                )

                if similarity > 0.7:  # High similarity threshold
                    similar_apps.append(app_memory)

        # Sort by feedback score
        similar_apps.sort(key=lambda x: x.feedback_score, reverse=True)

        return similar_apps[:5]  # Top 5 similar successes

    async def _calculate_base_agent_score(self, agent: Dict[str, Any], job: Dict[str, Any]) -> float:
        """Calculate base score from agent capabilities"""
        score = 0.0

        # Check specialization match
        agent_spec = agent.get('specialization', '').lower()
        job_title = job.get('title', '').lower()
        job_desc = job.get('description', '').lower()

        if agent_spec and agent_spec in job_title:
            score += 30

        # Check skills match
        agent_skills = [s.lower() for s in agent.get('skills', [])]
        job_text = f"{job_title} {job_desc}"

        for skill in agent_skills:
            if skill in job_text:
                score += 10

        # Experience level bonus
        if 'senior' in job_title and agent.get('experience_level') == 'expert':
            score += 20
        elif 'junior' in job_title and agent.get('experience_level') == 'intermediate':
            score += 10

        return min(score, 100) / 100  # Normalize to 0-1

    async def _calculate_ml_score(self, agent_id: str, job: Dict[str, Any], job_embedding: np.ndarray) -> float:
        """Calculate ML-based score using the ML pipeline"""
        try:
            # Prepare features for ML model
            features = {
                'agent_id': agent_id,
                'job_category': self._categorize_job(job),
                'job_seniority': self._extract_seniority(job),
                'required_skills_count': len(job.get('tags', [])),
                'agent_success_rate': self.agent_success_rates.get(agent_id, 0.5),
                'job_embedding': job_embedding.tolist() if isinstance(job_embedding, np.ndarray) else job_embedding
            }

            # Get ML prediction
            prediction = await self.ml_pipeline.predict_match_score(features)

            return prediction.get('match_score', 0.5)

        except Exception as e:
            logger.warning(f"ML scoring failed: {e}")
            return 0.5  # Default neutral score

    async def _calculate_memory_score(self, agent_id: str, similar_successes: List[JobApplicationMemory]) -> float:
        """Calculate score based on memory of similar successful applications"""
        if not similar_successes:
            return 0.5  # Neutral score if no memory

        # Check if this agent succeeded in similar jobs
        agent_successes = [
            app for app in similar_successes
            if app.agent_id == agent_id
        ]

        if agent_successes:
            # High score if agent succeeded in similar jobs
            avg_feedback = sum(app.feedback_score for app in agent_successes) / len(agent_successes)
            return avg_feedback

        # Check if similar agents succeeded
        similar_agent_types = self._find_similar_agents(agent_id)
        similar_agent_successes = [
            app for app in similar_successes
            if app.agent_id in similar_agent_types
        ]

        if similar_agent_successes:
            # Moderate score if similar agents succeeded
            avg_feedback = sum(app.feedback_score for app in similar_agent_successes) / len(similar_agent_successes)
            return avg_feedback * 0.7  # Slightly discounted

        # Low score if no relevant history
        return 0.3

    def _calculate_confidence(self, base_score: float, ml_score: float, memory_score: float) -> float:
        """Calculate confidence in the match"""
        scores = [base_score, ml_score, memory_score]

        # High confidence if all scores agree
        variance = np.var(scores)
        mean_score = np.mean(scores)

        # Lower confidence if scores disagree
        confidence = mean_score * (1 - variance)

        return max(0.1, min(0.99, confidence))

    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        if len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0

        # Cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def _store_matching_decision(self, job: Dict[str, Any], match: Dict[str, Any], embedding: np.ndarray):
        """Store the matching decision in memory for future learning"""
        app_id = f"app_{hashlib.md5(f"{job.get('id', '')}_{match['agent_id']}_{datetime.now()}".encode()).hexdigest()}"

        memory = JobApplicationMemory(
            application_id=app_id,
            job_id=job.get('id', job.get('url', '')),
            job_title=job.get('title', ''),
            job_embedding=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
            agent_id=match['agent_id'],
            agent_name=match['agent'].get('name', ''),
            match_score=match['final_score'],
            applied_at=datetime.now(),
            learned_features={
                'base_score': match['base_score'],
                'ml_score': match['ml_score'],
                'memory_score': match['memory_score'],
                'confidence': match['confidence']
            }
        )

        self.application_memory[app_id] = memory

        # Also store in persistent memory system
        await self.memory.store_memory(
            key=app_id,
            content={
                'job': job,
                'agent_id': match['agent_id'],
                'match_score': match['final_score'],
                'timestamp': datetime.now().isoformat()
            }
        )

    async def update_application_outcome(self, application_id: str, outcome: str, feedback_score: float):
        """
        Update the outcome of an application for learning

        Args:
            application_id: ID of the application
            outcome: 'interview', 'rejected', 'hired'
            feedback_score: 0-1 score of how well it went
        """
        if application_id in self.application_memory:
            memory = self.application_memory[application_id]
            memory.outcome = outcome
            memory.feedback_score = feedback_score

            # Update agent success rate
            agent_id = memory.agent_id
            if agent_id not in self.agent_success_rates:
                self.agent_success_rates[agent_id] = []

            self.agent_success_rates[agent_id].append(feedback_score)

            # Calculate running average
            self.agent_success_rates[agent_id] = np.mean(self.agent_success_rates[agent_id][-20:])  # Last 20 applications

            # Train ML model with this outcome
            await self._train_ml_with_outcome(memory)

            logger.info(f"""
            📊 Learning from Application Outcome:
               Application: {application_id}
               Outcome: {outcome}
               Feedback: {feedback_score:.2f}
               Agent: {memory.agent_name}
               New Success Rate: {self.agent_success_rates.get(agent_id, 0):.2%}
            """)

    async def _train_ml_with_outcome(self, memory: JobApplicationMemory):
        """Train the ML model with application outcome"""
        try:
            # Prepare training data
            training_data = {
                'features': memory.learned_features,
                'outcome': memory.outcome,
                'feedback_score': memory.feedback_score,
                'job_embedding': memory.job_embedding
            }

            # Send to ML pipeline for training
            await self.ml_pipeline.update_model(training_data)

        except Exception as e:
            logger.error(f"Failed to train ML model: {e}")

    def _categorize_job(self, job: Dict[str, Any]) -> str:
        """Categorize job into types"""
        title = job.get('title', '').lower()

        if 'senior' in title or 'lead' in title:
            return 'senior'
        elif 'junior' in title or 'entry' in title:
            return 'junior'
        elif 'manager' in title or 'director' in title:
            return 'management'
        else:
            return 'mid-level'

    def _extract_seniority(self, job: Dict[str, Any]) -> int:
        """Extract seniority level from job"""
        title = job.get('title', '').lower()

        if 'senior' in title or 'lead' in title:
            return 3
        elif 'mid' in title or not ('junior' in title or 'senior' in title):
            return 2
        else:
            return 1

    def _find_similar_agents(self, agent_id: str) -> List[str]:
        """Find agents similar to the given agent"""
        target_agent = self.agent_registry.agents.get(agent_id, {})
        if not target_agent:
            return []

        similar = []
        target_spec = target_agent.get('specialization', '').lower()

        for aid, agent in self.agent_registry.agents.items():
            if aid != agent_id:
                if agent.get('specialization', '').lower() == target_spec:
                    similar.append(aid)

        return similar[:5]  # Top 5 similar agents

    def _create_simple_feature_vector(self, job: Dict[str, Any]) -> np.ndarray:
        """Create simple feature vector when embeddings unavailable"""
        features = []

        # Job type features
        title = job.get('title', '').lower()
        features.append(1 if 'senior' in title else 0)
        features.append(1 if 'junior' in title else 0)
        features.append(1 if 'remote' in title else 0)
        features.append(1 if 'python' in title else 0)
        features.append(1 if 'javascript' in title else 0)

        # Pad to standard size
        while len(features) < 384:  # Standard embedding size
            features.append(0)

        return np.array(features[:384])

    async def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning system"""
        total_applications = len(self.application_memory)

        outcomes = {}
        for memory in self.application_memory.values():
            outcomes[memory.outcome] = outcomes.get(memory.outcome, 0) + 1

        top_agents = sorted(
            self.agent_success_rates.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'total_applications_tracked': total_applications,
            'outcomes': outcomes,
            'average_success_rate': np.mean(list(self.agent_success_rates.values())) if self.agent_success_rates else 0,
            'top_performing_agents': [
                {'agent_id': agent_id, 'success_rate': rate}
                for agent_id, rate in top_agents
            ],
            'learning_enabled': True,
            'ml_model_active': self.ml_pipeline is not None,
            'embeddings_active': self.embedder is not None,
            'memories_stored': len(self.application_memory)
        }


# Integration with job application flow
async def apply_with_learning(job_opportunities: List[Dict[str, Any]]):
    """Apply to jobs using the intelligent matching system"""
    matcher = IntelligentJobMatcher()

    print("\n🧠 INTELLIGENT JOB MATCHING WITH ML & MEMORY\n")
    print("=" * 60)

    for job in job_opportunities:
        print(f"\n📋 Job: {job.get('title')} at {job.get('company')}")

        # Find best match using ML and memory
        match = await matcher.match_job_with_learning(job)

        if match:
            print(f"   🤖 Best Agent: {match['agent'].get('name')}")
            print(f"   📊 Match Score: {match['match_score']:.2f}")
            print(f"   🎯 Confidence: {match['confidence']:.1%}")
            print(f"   📈 Scoring Breakdown:")
            print(f"      - Capabilities: {match['reasoning']['base_score']:.2f}")
            print(f"      - ML Prediction: {match['reasoning']['ml_score']:.2f}")
            print(f"      - Historical Success: {match['reasoning']['memory_score']:.2f}")
        else:
            print("   ❌ No suitable agent found")

    # Show learning stats
    stats = await matcher.get_learning_stats()
    print("\n" + "=" * 60)
    print("📊 LEARNING SYSTEM STATS\n")
    print(f"Applications Tracked: {stats['total_applications_tracked']}")
    print(f"Average Success Rate: {stats['average_success_rate']:.1%}")
    print(f"ML Model Active: {stats['ml_model_active']}")
    print(f"Embeddings Active: {stats['embeddings_active']}")
    print(f"Memories Stored: {stats['memories_stored']}")


if __name__ == "__main__":
    # Test with sample jobs
    test_jobs = [
        {
            'id': '1',
            'title': 'Senior Python ML Engineer',
            'company': 'AI Corp',
            'description': 'Build ML models using Python and TensorFlow',
            'tags': ['python', 'ml', 'tensorflow']
        },
        {
            'id': '2',
            'title': 'React Frontend Developer',
            'company': 'WebCo',
            'description': 'Create beautiful UIs with React',
            'tags': ['react', 'javascript', 'frontend']
        }
    ]

    asyncio.run(apply_with_learning(test_jobs))