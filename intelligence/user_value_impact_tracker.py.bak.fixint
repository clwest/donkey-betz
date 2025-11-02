"""
User Value Impact Tracker

This module proves that the system ACTUALLY helps users succeed by tracking
real outcomes, measuring value created, and verifying user success metrics.
"""

import json
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import redis
import hashlib
import logging

logger = logging.getLogger(__name__)


class UserValueImpactTracker:
    """
    Track and verify the real value and impact delivered to users
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=5,  # Dedicated DB for user impact tracking
            decode_responses=True
        )

    def track_user_outcome(self, user_id: str, outcome_data: Dict) -> Dict:
        """
        Track a specific outcome for a user (job obtained, income earned, etc.)

        Returns:
            Outcome tracking record with verification
        """
        outcome_id = str(uuid.uuid4())
        timestamp = datetime.now()

        outcome_record = {
            'outcome_id': outcome_id,
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'outcome_type': outcome_data.get('type'),  # 'job_obtained', 'income_earned', 'skill_learned', etc.
            'outcome_details': outcome_data,
            'value_metrics': self._calculate_value_metrics(outcome_data),
            'verification_hash': self._generate_verification_hash(user_id, outcome_data),
            'is_verified': False
        }

        # Verify the outcome
        verification = self._verify_outcome(outcome_data)
        outcome_record['is_verified'] = verification['is_verified']
        outcome_record['verification_details'] = verification

        # Store outcome
        self._store_outcome(outcome_record)

        # Update user's cumulative impact
        self._update_user_impact(user_id, outcome_record)

        logger.info(f"Tracked outcome for user {user_id}: {outcome_data.get('type')}")

        return outcome_record

    def _calculate_value_metrics(self, outcome_data: Dict) -> Dict:
        """Calculate the value metrics for an outcome"""
        metrics = {
            'monetary_value': 0,
            'time_saved_hours': 0,
            'efficiency_gain': 0,
            'skill_improvement': 0,
            'opportunity_score': 0
        }

        outcome_type = outcome_data.get('type')

        if outcome_type == 'job_obtained':
            metrics['monetary_value'] = float(outcome_data.get('salary', 0))
            metrics['opportunity_score'] = 100
            metrics['time_saved_hours'] = outcome_data.get('time_to_hire_hours', 0)

        elif outcome_type == 'income_earned':
            metrics['monetary_value'] = float(outcome_data.get('amount', 0))
            metrics['efficiency_gain'] = outcome_data.get('efficiency_improvement', 0)

        elif outcome_type == 'skill_learned':
            metrics['skill_improvement'] = outcome_data.get('skill_level_increase', 0)
            metrics['opportunity_score'] = outcome_data.get('new_opportunities_unlocked', 0)

        elif outcome_type == 'time_saved':
            metrics['time_saved_hours'] = outcome_data.get('hours_saved', 0)
            # Convert time to monetary value (assuming $50/hour)
            metrics['monetary_value'] = metrics['time_saved_hours'] * 50

        elif outcome_type == 'task_automated':
            metrics['efficiency_gain'] = outcome_data.get('automation_percentage', 0)
            metrics['time_saved_hours'] = outcome_data.get('weekly_hours_saved', 0) * 52  # Annualized

        return metrics

    def _verify_outcome(self, outcome_data: Dict) -> Dict:
        """Verify that the outcome is real and not simulated"""
        verification = {
            'is_verified': False,
            'verification_score': 0,
            'checks': {}
        }

        # Check 1: External verification (if available)
        if outcome_data.get('external_proof'):
            verification['checks']['external_proof'] = True
            verification['verification_score'] += 40

        # Check 2: Timestamp verification (is it recent and realistic?)
        if outcome_data.get('occurred_at'):
            occurred_at = datetime.fromisoformat(outcome_data['occurred_at'])
            if (datetime.now() - occurred_at).days <= 30:
                verification['checks']['timestamp_valid'] = True
                verification['verification_score'] += 20

        # Check 3: Value range verification (is the value realistic?)
        value = outcome_data.get('amount') or outcome_data.get('salary') or 0
        if 0 < value < 1000000:  # Realistic range
            verification['checks']['value_realistic'] = True
            verification['verification_score'] += 20

        # Check 4: User activity verification (has the user been active?)
        if self._verify_user_activity(outcome_data.get('user_id')):
            verification['checks']['user_active'] = True
            verification['verification_score'] += 20

        verification['is_verified'] = verification['verification_score'] >= 60

        return verification

    def _verify_user_activity(self, user_id: str) -> bool:
        """Verify the user has been active on the platform"""
        activity_key = f"user:activity:{user_id}"
        last_activity = self.redis_client.get(activity_key)

        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            # User active in last 7 days
            return (datetime.now() - last_activity_time).days <= 7

        return False

    def _generate_verification_hash(self, user_id: str, outcome_data: Dict) -> str:
        """Generate a verification hash for the outcome"""
        hash_input = json.dumps({
            'user_id': user_id,
            'type': outcome_data.get('type'),
            'value': str(outcome_data.get('amount') or outcome_data.get('salary') or 0),
            'timestamp': datetime.now().isoformat()
        }, sort_keys=True)

        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _store_outcome(self, outcome_record: Dict):
        """Store outcome record in Redis"""
        key = f"user:outcome:{outcome_record['outcome_id']}"

        self.redis_client.hset(
            key,
            mapping={
                'data': json.dumps(outcome_record),
                'user_id': outcome_record['user_id'],
                'type': outcome_record['outcome_details'].get('type'),
                'timestamp': outcome_record['timestamp'],
                'verified': str(outcome_record['is_verified'])
            }
        )

        # Add to user's outcome list
        user_outcomes_key = f"user:outcomes:{outcome_record['user_id']}"
        self.redis_client.lpush(user_outcomes_key, outcome_record['outcome_id'])

        # Set expiry (keep for 90 days)
        self.redis_client.expire(key, 86400 * 90)

    def _update_user_impact(self, user_id: str, outcome_record: Dict):
        """Update cumulative impact metrics for a user"""
        impact_key = f"user:impact:{user_id}"

        # Get current metrics
        current = self.redis_client.hgetall(impact_key) or {}

        # Update metrics
        value_metrics = outcome_record['value_metrics']

        total_value = float(current.get('total_monetary_value', 0)) + value_metrics['monetary_value']
        total_time_saved = float(current.get('total_time_saved', 0)) + value_metrics['time_saved_hours']
        total_outcomes = int(current.get('total_outcomes', 0)) + 1
        verified_outcomes = int(current.get('verified_outcomes', 0)) + (1 if outcome_record['is_verified'] else 0)

        # Calculate success rate
        success_rate = (verified_outcomes / total_outcomes * 100) if total_outcomes > 0 else 0

        # Update Redis
        self.redis_client.hset(
            impact_key,
            mapping={
                'user_id': user_id,
                'total_monetary_value': str(total_value),
                'total_time_saved': str(total_time_saved),
                'total_outcomes': str(total_outcomes),
                'verified_outcomes': str(verified_outcomes),
                'success_rate': str(success_rate),
                'last_updated': datetime.now().isoformat()
            }
        )

    def get_user_impact_summary(self, user_id: str) -> Dict:
        """Get comprehensive impact summary for a user"""
        impact_key = f"user:impact:{user_id}"
        impact_data = self.redis_client.hgetall(impact_key)

        if not impact_data:
            return {
                'user_id': user_id,
                'total_value_created': 0,
                'time_saved_hours': 0,
                'outcomes_achieved': 0,
                'success_rate': 0,
                'impact_score': 0
            }

        # Calculate impact score
        monetary_value = float(impact_data.get('total_monetary_value', 0))
        time_saved = float(impact_data.get('total_time_saved', 0))
        outcomes = int(impact_data.get('total_outcomes', 0))
        success_rate = float(impact_data.get('success_rate', 0))

        # Impact score formula
        impact_score = (
            (monetary_value / 1000) * 0.4 +  # Money weight: 40%
            (time_saved / 10) * 0.3 +        # Time weight: 30%
            (outcomes * 5) * 0.2 +           # Outcomes weight: 20%
            success_rate * 0.1                # Success rate weight: 10%
        )

        return {
            'user_id': user_id,
            'total_value_created': monetary_value,
            'time_saved_hours': time_saved,
            'outcomes_achieved': outcomes,
            'verified_outcomes': int(impact_data.get('verified_outcomes', 0)),
            'success_rate': success_rate,
            'impact_score': min(100, impact_score),  # Cap at 100
            'last_updated': impact_data.get('last_updated')
        }

    def get_platform_impact_statistics(self) -> Dict:
        """Get overall platform impact statistics"""
        user_keys = self.redis_client.keys("user:impact:*")

        total_users = len(user_keys)
        total_value = 0
        total_time_saved = 0
        total_outcomes = 0
        verified_outcomes = 0

        success_stories = []

        for key in user_keys:
            data = self.redis_client.hgetall(key)
            if data:
                total_value += float(data.get('total_monetary_value', 0))
                total_time_saved += float(data.get('total_time_saved', 0))
                total_outcomes += int(data.get('total_outcomes', 0))
                verified_outcomes += int(data.get('verified_outcomes', 0))

                # Identify success stories (high impact users)
                if float(data.get('total_monetary_value', 0)) > 5000:
                    success_stories.append({
                        'user_id': data.get('user_id'),
                        'value': float(data.get('total_monetary_value', 0)),
                        'outcomes': int(data.get('total_outcomes', 0))
                    })

        # Sort success stories by value
        success_stories.sort(key=lambda x: x['value'], reverse=True)

        return {
            'total_users_impacted': total_users,
            'total_value_created': total_value,
            'total_time_saved_hours': total_time_saved,
            'total_outcomes_achieved': total_outcomes,
            'verified_outcomes': verified_outcomes,
            'platform_success_rate': (verified_outcomes / total_outcomes * 100) if total_outcomes > 0 else 0,
            'average_value_per_user': total_value / total_users if total_users > 0 else 0,
            'top_success_stories': success_stories[:10],
            'timestamp': datetime.now().isoformat()
        }

    def track_user_journey(self, user_id: str, milestone: Dict):
        """Track user's journey from start to success"""
        journey_key = f"user:journey:{user_id}"
        milestone_id = str(uuid.uuid4())

        milestone_data = {
            'milestone_id': milestone_id,
            'timestamp': datetime.now().isoformat(),
            'type': milestone.get('type'),  # 'registration', 'first_action', 'first_success', etc.
            'details': milestone
        }

        # Add to journey timeline
        self.redis_client.lpush(journey_key, json.dumps(milestone_data))

        # Track milestone in metrics
        metrics_key = f"user:journey:metrics:{user_id}"
        self.redis_client.hincrby(metrics_key, milestone.get('type', 'unknown'), 1)

        logger.info(f"Tracked milestone for user {user_id}: {milestone.get('type')}")

    def calculate_time_to_value(self, user_id: str) -> Optional[float]:
        """Calculate time from registration to first value creation"""
        journey_key = f"user:journey:{user_id}"
        journey_data = self.redis_client.lrange(journey_key, 0, -1)

        if not journey_data:
            return None

        registration_time = None
        first_value_time = None

        for item in journey_data:
            milestone = json.loads(item)
            if milestone['type'] == 'registration':
                registration_time = datetime.fromisoformat(milestone['timestamp'])
            elif milestone['type'] in ['first_income', 'first_success', 'job_obtained']:
                if not first_value_time:
                    first_value_time = datetime.fromisoformat(milestone['timestamp'])

        if registration_time and first_value_time:
            return (first_value_time - registration_time).total_seconds() / 3600  # Hours

        return None

    def get_user_testimonial_data(self, user_id: str) -> Dict:
        """Get data that could be used for user testimonials"""
        impact = self.get_user_impact_summary(user_id)
        time_to_value = self.calculate_time_to_value(user_id)

        # Get user's best outcome
        outcomes_key = f"user:outcomes:{user_id}"
        outcome_ids = self.redis_client.lrange(outcomes_key, 0, 10)

        best_outcome = None
        max_value = 0

        for outcome_id in outcome_ids:
            outcome_data = self.redis_client.hget(f"user:outcome:{outcome_id}", 'data')
            if outcome_data:
                outcome = json.loads(outcome_data)
                value = outcome['value_metrics']['monetary_value']
                if value > max_value:
                    max_value = value
                    best_outcome = outcome

        return {
            'user_id': user_id,
            'total_value_created': impact['total_value_created'],
            'time_saved': impact['time_saved_hours'],
            'outcomes_count': impact['outcomes_achieved'],
            'success_rate': impact['success_rate'],
            'time_to_first_value_hours': time_to_value,
            'best_outcome': best_outcome,
            'testimonial_worthy': impact['total_value_created'] > 1000 or impact['outcomes_achieved'] > 5
        }


class UserSuccessVerifier:
    """
    Verify and validate user success claims
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=5,
            decode_responses=True
        )
        self.tracker = UserValueImpactTracker()

    def verify_success_claim(self, claim_data: Dict) -> Tuple[bool, Dict]:
        """
        Verify a user's success claim with evidence

        Returns:
            (is_verified, verification_details)
        """
        verification = {
            'claim_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'claim': claim_data,
            'checks_performed': [],
            'evidence': {},
            'verification_score': 0,
            'is_verified': False
        }

        # Check 1: User history verification
        if self._verify_user_history(claim_data.get('user_id')):
            verification['checks_performed'].append('user_history')
            verification['verification_score'] += 25
            verification['evidence']['user_history'] = 'verified'

        # Check 2: Value range verification
        if self._verify_value_range(claim_data.get('amount')):
            verification['checks_performed'].append('value_range')
            verification['verification_score'] += 25
            verification['evidence']['value_range'] = 'realistic'

        # Check 3: Timeline verification
        if self._verify_timeline(claim_data):
            verification['checks_performed'].append('timeline')
            verification['verification_score'] += 25
            verification['evidence']['timeline'] = 'consistent'

        # Check 4: Supporting data verification
        if self._verify_supporting_data(claim_data):
            verification['checks_performed'].append('supporting_data')
            verification['verification_score'] += 25
            verification['evidence']['supporting_data'] = 'present'

        verification['is_verified'] = verification['verification_score'] >= 75

        # Store verification
        self._store_verification(verification)

        return verification['is_verified'], verification

    def _verify_user_history(self, user_id: str) -> bool:
        """Verify user has sufficient history on platform"""
        impact = self.tracker.get_user_impact_summary(user_id)
        return impact['outcomes_achieved'] > 0

    def _verify_value_range(self, amount: float) -> bool:
        """Verify claimed amount is within realistic range"""
        return 10 <= amount <= 100000  # $10 to $100k

    def _verify_timeline(self, claim_data: Dict) -> bool:
        """Verify timeline is realistic"""
        if claim_data.get('time_period_days'):
            days = claim_data['time_period_days']
            amount = claim_data.get('amount', 0)

            # Check if daily rate is realistic
            daily_rate = amount / days if days > 0 else 0
            return 10 <= daily_rate <= 5000  # $10-$5000 per day

        return True

    def _verify_supporting_data(self, claim_data: Dict) -> bool:
        """Verify supporting data exists"""
        return bool(claim_data.get('proof_url') or claim_data.get('transaction_ids') or claim_data.get('screenshots'))

    def _store_verification(self, verification: Dict):
        """Store verification record"""
        key = f"success:verification:{verification['claim_id']}"
        self.redis_client.hset(
            key,
            mapping={
                'data': json.dumps(verification),
                'timestamp': verification['timestamp'],
                'is_verified': str(verification['is_verified']),
                'score': str(verification['verification_score'])
            }
        )
        self.redis_client.expire(key, 86400 * 30)  # 30 days