"""
Signal Aggregation Service - Session 900

Clusters recent SpiderData into SignalClusters, detecting patterns
that can trigger auto-generated conversation topics.

Flow:
1. Fetch recent SpiderData (configurable window)
2. Extract keywords and themes from each signal
3. Cluster signals by semantic similarity
4. Calculate pattern metrics (strength, confidence, novelty)
5. Create/update SignalCluster records
6. Generate AutoTopic suggestions from actionable clusters
"""

import logging
import re
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from django.db.models import Count
from django.utils import timezone

from core.models import SpiderData, Agent
from core.models_signal_intelligence import SignalCluster, AutoTopic
from core.services.content_scoring_service import ContentScoringService

logger = logging.getLogger(__name__)


class SignalAggregationService:
    """
    Session 900: Aggregates spider signals into meaningful patterns.

    This service transforms raw SpiderData into SignalClusters that
    can trigger intelligent conversation topics.
    """

    # Minimum signals needed to form a cluster
    # Raised back to 3 — size=2 created spurious clusters that flooded
    # the initiative pipeline with noise when spiders were active
    MIN_CLUSTER_SIZE = 3

    # Minimum sources needed for confidence
    MIN_SOURCES_FOR_CONFIDENCE = 2

    # Keywords that indicate different pattern types
    PATTERN_TYPE_KEYWORDS = {
        'demand_spike': [
            'need', 'want', 'looking for', 'seeking', 'demand', 'require',
            'how to', 'best way', 'recommend', 'suggestion', 'help with'
        ],
        'trend_emergence': [
            'new', 'emerging', 'trending', 'rising', 'growing', 'gaining',
            'breakthrough', 'innovative', 'revolutionary', 'next big'
        ],
        'sentiment_shift': [
            'changing', 'shift', 'moving away', 'no longer', 'instead',
            'prefer', 'better than', 'replaced', 'obsolete'
        ],
        'opportunity_window': [
            'opportunity', 'chance', 'limited time', 'now', 'urgent',
            'before', 'deadline', 'ending soon', 'act fast'
        ],
        'knowledge_gap': [
            'confused', 'unclear', 'don\'t understand', 'what is',
            'explain', 'help me understand', 'struggling with'
        ],
        'skill_demand': [
            'hiring', 'job', 'position', 'role', 'career', 'salary',
            'remote', 'engineer', 'developer', 'designer', 'manager'
        ],
        'content_gap': [
            'no good content', 'hard to find', 'wish there was',
            'underserved', 'missing', 'gap in', 'need more'
        ],
    }

    # Topic extraction patterns
    TOPIC_PATTERNS = [
        r'\b(AI|ML|machine learning|artificial intelligence)\b',
        r'\b(persona|customer research|user research|UX)\b',
        r'\b(content|marketing|SEO|social media)\b',
        r'\b(crypto|blockchain|web3|defi|nft)\b',
        r'\b(startup|entrepreneur|founder|VC|funding)\b',
        r'\b(remote work|freelance|gig economy)\b',
        r'\b(python|javascript|react|node|api)\b',
        r'\b(data science|analytics|visualization)\b',
        r'\b(automation|workflow|productivity)\b',
        r'\b(security|privacy|compliance)\b',
    ]

    def __init__(self, lookback_hours: int = 6):
        """
        Initialize the service.

        Args:
            lookback_hours: How far back to look for signals (default 6 hours)
        """
        self.lookback_hours = lookback_hours
        self.cutoff_time = timezone.now() - timedelta(hours=lookback_hours)

    @staticmethod
    def _get_governance_mode() -> str:
        """Get current governance mode. Returns 'normal' on any error."""
        try:
            from core.models_governance import GovernanceState
            gs = GovernanceState.objects.filter(scope='global').first()
            return gs.effective_mode if gs else 'normal'
        except Exception:
            return 'normal'

    def aggregate_signals(self) -> List[SignalCluster]:
        """
        Main entry point: aggregate recent signals into clusters.
        Respects governance mode: skipped in freeze/safe_mode.

        Returns:
            List of created/updated SignalCluster objects
        """
        mode = self._get_governance_mode()
        if mode in ('freeze', 'safe_mode'):
            logger.info("Signal aggregation skipped — governance mode: %s", mode)
            return []

        logger.info(f"Starting signal aggregation (lookback: {self.lookback_hours}h, governance: {mode})")

        # 1. Fetch recent spider data
        spider_data = self._fetch_recent_spider_data()
        if not spider_data:
            logger.info("No recent spider data to aggregate")
            return []

        logger.info(f"Found {len(spider_data)} recent spider data items")

        # 2. Extract signals with keywords
        signals = self._extract_signals(spider_data)
        logger.info(f"Extracted {len(signals)} signals with keywords")

        # 3. Cluster signals by topic
        clusters = self._cluster_signals(signals)
        logger.info(f"Formed {len(clusters)} potential clusters")

        # 4. Create SignalCluster records
        created_clusters = self._create_signal_clusters(clusters)
        logger.info(f"Created/updated {len(created_clusters)} SignalCluster records")

        return created_clusters

    def _fetch_recent_spider_data(self) -> List[SpiderData]:
        """Fetch spider data from the lookback window.

        Session 1003: Include records that are either processed OR have embedding_text
        populated (many spiders set embedding_text directly without the is_processed flag).
        This fixes the 18,893 records → 0 clusters problem.
        """
        from django.db.models import Q
        return list(
            SpiderData.objects.filter(
                Q(is_processed=True) | ~Q(embedding_text=''),
                created_at__gte=self.cutoff_time,
            ).order_by('-created_at')[:500]  # Limit for performance
        )

    def _extract_signals(self, spider_data: List[SpiderData]) -> List[Dict]:
        """
        Extract structured signals from spider data.

        Returns list of dicts with:
        - spider_data_id: UUID
        - spider_name: str
        - keywords: List[str]
        - topics: List[str]
        - text_sample: str
        - created_at: datetime
        """
        signals = []

        for sd in spider_data:
            # Get text content from raw_data
            text = self._extract_text_from_spider_data(sd)
            if not text:
                continue

            # Extract keywords and topics
            keywords = self._extract_keywords(text)
            topics = self._extract_topics(text)

            if keywords or topics:
                signals.append({
                    'spider_data_id': str(sd.id),
                    'spider_name': sd.spider_name,
                    'keywords': keywords,
                    'topics': topics,
                    'text_sample': text[:200],
                    'created_at': sd.created_at,
                    'relevance_score': sd.relevance_score or 0,
                })

        return signals

    def _extract_text_from_spider_data(self, sd: SpiderData) -> str:
        """Extract readable text from spider data."""
        text_parts = []

        raw = sd.raw_data or {}

        # Try common fields
        for field in ['title', 'description', 'content', 'text', 'body', 'summary']:
            if field in raw and raw[field]:
                text_parts.append(str(raw[field]))

        # Try items array (common in RSS feeds)
        if 'items' in raw and isinstance(raw['items'], list):
            for item in raw['items'][:5]:  # First 5 items
                if isinstance(item, dict):
                    for field in ['title', 'description', 'summary']:
                        if field in item and item[field]:
                            text_parts.append(str(item[field]))

        # Session 1003: Fall back to embedding_text which many spiders populate directly
        if not text_parts and sd.embedding_text:
            text_parts.append(sd.embedding_text)

        # Also check processed_data
        processed = sd.processed_data or {}
        if not text_parts and isinstance(processed, dict):
            for field in ['summary', 'analysis', 'content', 'description']:
                if field in processed and processed[field]:
                    text_parts.append(str(processed[field]))

        return ' '.join(text_parts)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        text_lower = text.lower()
        keywords = []

        # Check for pattern-type keywords
        for pattern_type, pattern_keywords in self.PATTERN_TYPE_KEYWORDS.items():
            for kw in pattern_keywords:
                if kw in text_lower:
                    keywords.append(kw)

        return list(set(keywords))[:10]  # Dedupe and limit

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topic categories from text."""
        topics = []

        for pattern in self.TOPIC_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            topics.extend([m.lower() if isinstance(m, str) else m[0].lower() for m in matches])

        return list(set(topics))[:5]  # Dedupe and limit

    def _cluster_signals(self, signals: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Cluster signals by topic similarity.

        Returns dict of topic -> list of signals
        """
        clusters = defaultdict(list)

        for signal in signals:
            # Primary clustering by topics
            for topic in signal['topics']:
                clusters[topic].append(signal)

            # Secondary clustering by keywords if no topics
            if not signal['topics'] and signal['keywords']:
                # Use first keyword as cluster key
                cluster_key = f"kw:{signal['keywords'][0]}"
                clusters[cluster_key].append(signal)

        # Filter clusters below minimum size
        return {
            k: v for k, v in clusters.items()
            if len(v) >= self.MIN_CLUSTER_SIZE
        }

    def _create_signal_clusters(self, clusters: Dict[str, List[Dict]]) -> List[SignalCluster]:
        """Create SignalCluster records from clustered signals."""
        created = []

        for topic, signals in clusters.items():
            # Calculate metrics
            source_breakdown = self._calculate_source_breakdown(signals)
            strength = self._calculate_strength(signals, source_breakdown)
            confidence = self._calculate_confidence(source_breakdown)
            novelty = self._calculate_novelty(signals)
            pattern_type = self._detect_pattern_type(signals)

            # Collect keywords across all signals
            all_keywords = []
            for s in signals:
                all_keywords.extend(s['keywords'])
                all_keywords.extend(s['topics'])
            keywords = list(set(all_keywords))[:15]

            # Create sample signals for display
            sample_signals = [
                {
                    'source': s['spider_name'],
                    'text': s['text_sample'][:100],
                }
                for s in signals[:5]  # Top 5 samples
            ]

            # Get time window
            timestamps = [s['created_at'] for s in signals]

            # Generate cluster name
            name = self._generate_cluster_name(topic, pattern_type, keywords)

            # Check for existing active cluster with same topic
            existing = SignalCluster.objects.filter(
                status__in=['detecting', 'active'],
                keywords__contains=[topic]
            ).first()

            if existing:
                # Update existing cluster
                existing.spider_data_ids.extend([s['spider_data_id'] for s in signals])
                existing.spider_data_ids = list(set(existing.spider_data_ids))
                existing.source_breakdown = source_breakdown
                existing.strength = strength
                existing.confidence = confidence
                existing.novelty = novelty
                existing.keywords = keywords
                existing.sample_signals = sample_signals
                existing.signal_window_end = max(timestamps)
                if strength >= 0.5 and confidence >= 0.5:
                    existing.status = 'active'
                    existing.confirmed_at = timezone.now()
                existing.save()
                # Score the updated cluster
                self._apply_scores(existing)
                created.append(existing)
                logger.info(f"Updated existing cluster: {existing.name}")
            else:
                # Create new cluster
                cluster = SignalCluster.objects.create(
                    name=name,
                    pattern_type=pattern_type,
                    spider_data_ids=[s['spider_data_id'] for s in signals],
                    source_breakdown=source_breakdown,
                    strength=strength,
                    confidence=confidence,
                    novelty=novelty,
                    urgency=0.5 if pattern_type == 'opportunity_window' else 0.3,
                    keywords=keywords,
                    sample_signals=sample_signals,
                    signal_window_start=min(timestamps),
                    signal_window_end=max(timestamps),
                    status='active' if (strength >= 0.5 and confidence >= 0.5) else 'detecting',
                    confirmed_at=timezone.now() if (strength >= 0.5 and confidence >= 0.5) else None,
                    expires_at=timezone.now() + timedelta(days=3),
                )
                # Score the new cluster
                self._apply_scores(cluster)
                created.append(cluster)
                logger.info(f"Created new cluster: {cluster.name} (strength={strength:.2f}, track={cluster.track})")

        return created

    def _apply_scores(self, cluster: SignalCluster) -> None:
        """Apply content scoring to a cluster and persist."""
        try:
            scorer = ContentScoringService()
            scores = scorer.score_cluster(cluster)
            for field, value in scores.items():
                setattr(cluster, field, value)
            cluster.save(update_fields=list(scores.keys()))
        except Exception as e:
            logger.warning(f"Failed to score cluster {cluster.id}: {e}")

    def _calculate_source_breakdown(self, signals: List[Dict]) -> Dict[str, int]:
        """Calculate signal count per source."""
        breakdown = defaultdict(int)
        for s in signals:
            breakdown[s['spider_name']] += 1
        return dict(breakdown)

    def _calculate_strength(self, signals: List[Dict], source_breakdown: Dict[str, int]) -> float:
        """
        Calculate pattern strength (0-1).

        Based on:
        - Number of signals
        - Source diversity
        - Relevance scores
        """
        signal_count = len(signals)
        source_count = len(source_breakdown)

        # Normalize signal count (20 signals = 1.0)
        signal_factor = min(1.0, signal_count / 20)

        # Normalize source diversity (5 sources = 1.0)
        diversity_factor = min(1.0, source_count / 5)

        # Average relevance score
        avg_relevance = sum(s['relevance_score'] for s in signals) / signal_count if signals else 0
        relevance_factor = avg_relevance / 100  # Normalize to 0-1

        # Weighted combination
        strength = (signal_factor * 0.4) + (diversity_factor * 0.4) + (relevance_factor * 0.2)

        return round(min(1.0, strength), 2)

    def _calculate_confidence(self, source_breakdown: Dict[str, int]) -> float:
        """
        Calculate pattern confidence (0-1).

        Higher confidence when:
        - Multiple independent sources agree
        - Sources are diverse (not just one spider)
        """
        source_count = len(source_breakdown)

        if source_count < self.MIN_SOURCES_FOR_CONFIDENCE:
            return 0.3  # Low confidence with single source

        # More sources = higher confidence
        confidence = min(1.0, source_count / 4)

        return round(confidence, 2)

    def _calculate_novelty(self, signals: List[Dict]) -> float:
        """
        Calculate pattern novelty (0-1).

        Newer signals = higher novelty.
        """
        if not signals:
            return 0.0

        # Average age in hours
        now = timezone.now()
        ages = [(now - s['created_at']).total_seconds() / 3600 for s in signals]
        avg_age = sum(ages) / len(ages)

        # Novelty decays over 24 hours
        novelty = max(0, 1.0 - (avg_age / 24))

        return round(novelty, 2)

    def _detect_pattern_type(self, signals: List[Dict]) -> str:
        """Detect the most likely pattern type from signals."""
        type_scores = defaultdict(int)

        for signal in signals:
            for kw in signal['keywords']:
                for pattern_type, pattern_keywords in self.PATTERN_TYPE_KEYWORDS.items():
                    if kw in pattern_keywords:
                        type_scores[pattern_type] += 1

        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]

        return 'demand_spike'  # Default

    def _generate_cluster_name(self, topic: str, pattern_type: str, keywords: List[str]) -> str:
        """Generate a human-readable cluster name."""
        # Clean up topic
        topic_clean = topic.replace('kw:', '').replace('_', ' ').title()

        # Pattern type descriptions
        type_descriptions = {
            'demand_spike': 'demand spike',
            'trend_emergence': 'emerging trend',
            'sentiment_shift': 'sentiment shift',
            'opportunity_window': 'opportunity window',
            'knowledge_gap': 'knowledge gap',
            'skill_demand': 'skill demand',
            'content_gap': 'content gap',
            'competitive_signal': 'competitive signal',
            'market_movement': 'market movement',
            'user_need': 'user need',
        }

        type_desc = type_descriptions.get(pattern_type, 'signal pattern')

        return f"{topic_clean} {type_desc}"

    # Maximum auto-topics created per 24h rolling window
    MAX_AUTO_TOPICS_PER_DAY = 10

    def generate_auto_topics(self, min_confidence: float = 0.6) -> List[AutoTopic]:
        """
        Generate AutoTopic suggestions from active SignalClusters.
        Respects governance mode: skipped in freeze/safe_mode, reduced in throttle.

        Args:
            min_confidence: Minimum cluster confidence to consider (raised to 0.6)

        Returns:
            List of created AutoTopic objects
        """
        mode = self._get_governance_mode()
        if mode in ('freeze', 'safe_mode'):
            logger.info("AutoTopic generation skipped — governance mode: %s", mode)
            return []

        # Daily rate limit — prevent topic flood
        recent_count = AutoTopic.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).count()
        if recent_count >= self.MAX_AUTO_TOPICS_PER_DAY:
            logger.info(
                "AutoTopic daily limit reached (%d/%d), skipping generation",
                recent_count, self.MAX_AUTO_TOPICS_PER_DAY,
            )
            return []

        remaining = self.MAX_AUTO_TOPICS_PER_DAY - recent_count

        # Get active clusters that haven't triggered yet
        active_clusters = SignalCluster.objects.filter(
            status='active',
            confidence__gte=min_confidence
        ).exclude(
            auto_topics__status='triggered'  # Not already triggered
        ).order_by('-strength', '-confidence')[:min(5, remaining)]

        created_topics = []

        for cluster in active_clusters:
            # Check if topic already exists
            existing = AutoTopic.objects.filter(
                signal_cluster=cluster,
                status__in=['pending', 'scheduled']
            ).exists()

            if existing:
                continue

            # Skip clusters with no meaningful keywords (all stopwords)
            meaningful = [
                kw for kw in cluster.keywords[:6]
                if kw.lower() not in self._TOPIC_STOPWORDS and len(kw) > 2
            ]
            if not meaningful:
                logger.debug(f"Skipping cluster {cluster.id}: no meaningful keywords in {cluster.keywords[:5]}")
                continue

            # Generate topic name and description
            topic_name = self._generate_topic_name(cluster)
            description = self._generate_topic_description(cluster)
            rationale = self._generate_topic_rationale(cluster)

            # Suggest agents based on cluster type
            suggested_agents = self._suggest_agents_for_cluster(cluster)

            # Suggest conversation type
            conversation_type = self._suggest_conversation_type(cluster)

            auto_topic = AutoTopic.objects.create(
                name=topic_name,
                description=description,
                signal_cluster=cluster,
                derived_from_pattern=cluster.pattern_type,
                rationale=rationale,
                confidence=cluster.confidence,
                urgency=cluster.urgency,
                relevance=cluster.strength,
                suggested_agent_names=suggested_agents,
                suggested_conversation_type=conversation_type,
                status='pending',
                expires_at=timezone.now() + timedelta(days=2),
            )

            created_topics.append(auto_topic)
            logger.info(f"Created AutoTopic: {auto_topic.name}")

        return created_topics

    # Stopwords that produce garbled topic names when joined
    _TOPIC_STOPWORDS = {
        'new', 'now', 'before', 'how to', 'want', 'need', 'explain',
        'help with', 'looking for', 'instead', 'struggling with',
        'trending', 'growing', 'rising', 'with', 'and', 'the', 'for',
        'what', 'why', 'where', 'when', 'how', 'can', 'should', 'would',
        'get', 'make', 'use', 'find', 'best', 'top', 'good', 'more',
    }

    def _generate_topic_name(self, cluster: SignalCluster) -> str:
        """Generate a discussion topic name from cluster."""
        # Filter out stopwords that produce word-salad titles
        keywords = [
            kw for kw in cluster.keywords[:6]
            if kw.lower() not in self._TOPIC_STOPWORDS and len(kw) > 2
        ][:3]

        topic_templates = {
            'demand_spike': "Addressing {} demand",
            'trend_emergence': "Exploring {} trends",
            'sentiment_shift': "Understanding {} sentiment changes",
            'opportunity_window': "Capitalizing on {} opportunity",
            'knowledge_gap': "Filling {} knowledge gaps",
            'skill_demand': "Developing {} skills",
            'content_gap': "Creating {} content",
        }

        template = topic_templates.get(cluster.pattern_type, "Analyzing {}")

        if keywords:
            topic_phrase = ', '.join(keywords)
        else:
            # All keywords were stopwords — use cluster name as fallback
            topic_phrase = cluster.name

        return template.format(topic_phrase)

    def _generate_topic_description(self, cluster: SignalCluster) -> str:
        """Generate extended topic description."""
        sources = list(cluster.source_breakdown.keys())
        signal_count = cluster.total_signals

        return (
            f"This topic emerged from {signal_count} signals across {len(sources)} sources "
            f"({', '.join(sources[:3])}). Key themes: {', '.join(cluster.keywords[:5])}."
        )

    def _generate_topic_rationale(self, cluster: SignalCluster) -> str:
        """Generate explanation of why this topic was chosen."""
        parts = []

        # Source breakdown
        for source, count in list(cluster.source_breakdown.items())[:3]:
            parts.append(f"{count} signals from {source}")

        # Metrics
        parts.append(f"Pattern strength: {cluster.strength:.0%}")
        parts.append(f"Confidence: {cluster.confidence:.0%}")

        # Sample signal
        if cluster.sample_signals:
            sample = cluster.sample_signals[0]
            parts.append(f"Example: \"{sample['text']}...\" ({sample['source']})")

        return ' | '.join(parts)

    def _suggest_agents_for_cluster(self, cluster: SignalCluster) -> List[str]:
        """Suggest agents based on cluster type and keywords."""
        # Map pattern types to agent categories
        agent_suggestions = {
            'demand_spike': ['ContentStrategyAgent', 'MarketIntelligenceAgent'],
            'trend_emergence': ['TrendAnalysisAgent', 'MarketIntelligenceAgent'],
            'sentiment_shift': ['TrendAnalysisAgent', 'ContentStrategyAgent'],
            'opportunity_window': ['MarketIntelligenceAgent', 'ResearchAgent'],
            'knowledge_gap': ['ResearchAgent', 'TechnicalDocumentAgent'],
            'skill_demand': ['ResearchAgent', 'ContentStrategyAgent'],
            'content_gap': ['ContentWriterAgent', 'ContentStrategyAgent'],
        }

        base_agents = agent_suggestions.get(cluster.pattern_type, ['ResearchAgent'])

        # Add topic-specific agents based on keywords
        keyword_agents = {
            'crypto': 'SmartContractAuditorAgent',
            'blockchain': 'SmartContractAuditorAgent',
            'stock': 'StockAnalystAgent',
            'marketing': 'MarketingAgent',
            'seo': 'SEOOptimizerAgent',
            'code': 'FullStackDeveloperAgent',
            'python': 'FullStackDeveloperAgent',
            'legal': 'LegalDocDrafterAgent',
        }

        for kw in cluster.keywords:
            kw_lower = kw.lower()
            for trigger, agent in keyword_agents.items():
                if trigger in kw_lower and agent not in base_agents:
                    base_agents.append(agent)
                    break

        return base_agents[:4]  # Max 4 agents

    def _suggest_conversation_type(self, cluster: SignalCluster) -> str:
        """Suggest conversation type based on cluster."""
        type_mapping = {
            'demand_spike': 'analytical',
            'trend_emergence': 'analytical',
            'sentiment_shift': 'debate',
            'opportunity_window': 'planning',
            'knowledge_gap': 'analytical',
            'skill_demand': 'planning',
            'content_gap': 'creative',
        }

        return type_mapping.get(cluster.pattern_type, 'analytical')
