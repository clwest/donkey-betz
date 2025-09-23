#!/usr/bin/env python
"""
Hallucination Event Publisher
==============================
Publishes hallucination detection events to Redis for real-time display
"""

import json
import redis
from datetime import datetime
from typing import Dict, Any, List


class HallucinationPublisher:
    """
    Publishes hallucination events for real-time monitoring
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=2,
            decode_responses=True
        )

    def publish_hallucination_blocked(self, agent_name: str, original_text: str,
                                     patterns: List[str], risk_score: float,
                                     corrected_text: str = None, severity: str = "medium"):
        """
        Publish a hallucination blocking event

        Args:
            agent_name: Name of the agent that generated the hallucination
            original_text: The original hallucinated text
            patterns: List of mythology patterns detected
            risk_score: Risk score (0.0 to 1.0)
            corrected_text: The corrected version (if available)
            severity: Severity level (low, medium, high, critical)
        """
        event_data = {
            'agent': agent_name,
            'original_text': original_text[:500],  # Limit length
            'patterns': patterns,
            'risk_score': risk_score,
            'corrected_text': corrected_text[:500] if corrected_text else None,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }

        # Publish to Redis channel
        self.redis_client.publish('hallucination_events', json.dumps(event_data))

        # Also store in recent history
        history_key = 'hallucination_history'
        self.redis_client.lpush(history_key, json.dumps(event_data))
        self.redis_client.ltrim(history_key, 0, 99)  # Keep last 100

        # Update statistics
        self.redis_client.hincrby('hallucination_stats', 'total_blocked', 1)
        if corrected_text:
            self.redis_client.hincrby('hallucination_stats', 'total_corrected', 1)

        print(f"🚫 Hallucination blocked from {agent_name}: {patterns}")

    def get_recent_hallucinations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent hallucination events

        Args:
            limit: Number of recent events to retrieve

        Returns:
            List of hallucination events
        """
        history_key = 'hallucination_history'
        events = self.redis_client.lrange(history_key, 0, limit - 1)

        return [json.loads(event) for event in events]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get hallucination statistics

        Returns:
            Dictionary with statistics
        """
        stats = self.redis_client.hgetall('hallucination_stats')

        return {
            'total_blocked': int(stats.get('total_blocked', 0)),
            'total_corrected': int(stats.get('total_corrected', 0)),
            'prevention_rate': self._calculate_prevention_rate(stats)
        }

    def _calculate_prevention_rate(self, stats: Dict) -> float:
        """Calculate the prevention rate"""
        total_blocked = int(stats.get('total_blocked', 0))
        total_checked = int(stats.get('total_checked', 1))

        if total_checked == 0:
            return 0.0

        return (total_blocked / total_checked) * 100


# Global publisher instance
hallucination_publisher = HallucinationPublisher()


def test_publisher():
    """Test the hallucination publisher"""
    print("Testing Hallucination Publisher...")

    publisher = HallucinationPublisher()

    # Test 1: Financial mythology
    publisher.publish_hallucination_blocked(
        agent_name="income_generator_001",
        original_text="This method guarantees $10000 per day income with zero risk",
        patterns=["financial_myth", "guaranteed_income", "zero_risk"],
        risk_score=0.95,
        corrected_text="This method may generate income with careful management",
        severity="high"
    )

    # Test 2: Technical mythology
    publisher.publish_hallucination_blocked(
        agent_name="tech_advisor_002",
        original_text="Our system achieves 100% accuracy and never fails",
        patterns=["technical_myth", "100_percent_accuracy", "never_fails"],
        risk_score=0.85,
        corrected_text="Our system achieves high reliability with robust error handling",
        severity="high"
    )

    # Test 3: Capability exaggeration
    publisher.publish_hallucination_blocked(
        agent_name="skill_builder_003",
        original_text="Learn programming instantly and become an expert in hours",
        patterns=["time_myth", "instant_expertise"],
        risk_score=0.7,
        corrected_text="Learn programming progressively with dedicated practice",
        severity="medium"
    )

    # Get recent events
    recent = publisher.get_recent_hallucinations(5)
    print(f"\nRecent hallucinations: {len(recent)} events")
    for event in recent:
        print(f"  - {event['agent']}: {event['patterns']}")

    # Get statistics
    stats = publisher.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total blocked: {stats['total_blocked']}")
    print(f"  Total corrected: {stats['total_corrected']}")
    print(f"  Prevention rate: {stats['prevention_rate']:.1f}%")


if __name__ == "__main__":
    test_publisher()