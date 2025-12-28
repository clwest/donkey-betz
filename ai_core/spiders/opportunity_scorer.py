"""
Opportunity Scoring System
Phase 5: Activate Money-Making Pipeline

This module analyzes and scores opportunities collected by spiders to
identify the most profitable and suitable prospects for applications.
"""

import logging
import asyncio
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass, field
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


@dataclass
class OpportunityScore:
    """Scored opportunity with detailed metrics"""
    opportunity_id: str
    source_spider: str
    original_data: Dict
    scores: Dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0
    rank: int = 0
    recommendation: str = "review"  # "apply", "skip", "review"
    confidence: float = 0.0
    estimated_revenue: float = 0.0
    time_investment: int = 0  # hours
    success_probability: float = 0.0
    competition_level: str = "medium"  # "low", "medium", "high"
    skill_match: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


class OpportunityScorer:
    """
    Advanced opportunity scoring system that evaluates prospects
    across multiple dimensions to maximize revenue potential.
    """

    def __init__(self, user_profile: Dict = None):
        self.user_profile = user_profile or self._default_user_profile()

        # Scoring weights (can be tuned based on results)
        self.scoring_weights = {
            'profit_potential': 0.30,
            'success_probability': 0.25,
            'time_investment': 0.20,
            'skill_match': 0.15,
            'competition_level': 0.10
        }

        # Revenue estimation models
        self.revenue_models = {
            'job': self._estimate_job_revenue,
            'freelance': self._estimate_freelance_revenue,
            'business': self._estimate_business_revenue,
            'financial': self._estimate_financial_revenue,
            'real_estate': self._estimate_real_estate_revenue
        }

        # Skills vectorizer for matching
        self.skills_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

        # Historical performance data
        self.historical_scores = []
        self.performance_metrics = {
            'applications_sent': 0,
            'responses_received': 0,
            'revenue_generated': 0.0,
            'average_score_threshold': 0.7
        }

        logger.info("🎯 Opportunity Scorer initialized with advanced ML scoring")

    def _default_user_profile(self) -> Dict:
        """Default user profile for opportunity matching"""
        return {
            'skills': [
                'python', 'javascript', 'machine learning', 'ai', 'data analysis',
                'web development', 'automation', 'django', 'react', 'sql',
                'content writing', 'seo', 'marketing', 'business analysis'
            ],
            'experience_years': 8,
            'hourly_rate_target': 150,
            'preferred_types': ['job', 'freelance', 'business'],
            'availability_hours_per_week': 40,
            'location': 'remote',
            'industries': ['technology', 'finance', 'healthcare', 'e-commerce']
        }

    async def score_opportunity(self, opportunity: Dict, user_profile: Dict = None) -> OpportunityScore:
        """
        Score a single opportunity across all dimensions

        Args:
            opportunity: Raw opportunity data from spider

        Returns:
            Scored opportunity with detailed metrics
        """
        try:
            # Extract opportunity metadata
            opp_id = opportunity.get('id', f"opp_{datetime.now().timestamp()}")
            spider_type = opportunity.get('spider_type', 'unknown')

            # Initialize score object
            scored_opp = OpportunityScore(
                opportunity_id=opp_id,
                source_spider=spider_type,
                original_data=opportunity
            )

            # Calculate individual scores
            scored_opp.scores['profit_potential'] = await self._score_profit_potential(opportunity)
            scored_opp.scores['success_probability'] = await self._score_success_probability(opportunity)
            scored_opp.scores['time_investment'] = await self._score_time_investment(opportunity)
            scored_opp.scores['skill_match'] = await self._score_skill_match(opportunity)
            scored_opp.scores['competition_level'] = await self._score_competition_level(opportunity)

            # Calculate weighted total score
            total_score = 0.0
            for metric, score in scored_opp.scores.items():
                weight = self.scoring_weights.get(metric, 0.0)
                total_score += score * weight

            scored_opp.total_score = total_score
            scored_opp.confidence = self._calculate_confidence(scored_opp.scores)

            # Estimate specific metrics
            scored_opp.estimated_revenue = await self._estimate_revenue(opportunity)
            scored_opp.time_investment = self._estimate_time_investment(opportunity)
            scored_opp.success_probability = scored_opp.scores['success_probability']
            scored_opp.competition_level = self._categorize_competition(
                scored_opp.scores['competition_level']
            )
            scored_opp.skill_match = scored_opp.scores['skill_match']

            # Generate recommendation
            scored_opp.recommendation = self._generate_recommendation(scored_opp)

            logger.debug(f"🎯 Scored opportunity {opp_id}: {total_score:.2f}")

            return scored_opp

        except Exception as e:
            logger.error(f"❌ Error scoring opportunity: {e}")
            # Return minimal score on error
            return OpportunityScore(
                opportunity_id=opportunity.get('id', 'error'),
                source_spider=opportunity.get('spider_type', 'unknown'),
                original_data=opportunity,
                total_score=0.0
            )

    async def _score_profit_potential(self, opportunity: Dict) -> float:
        """Score profit potential (0.0 to 1.0)"""
        try:
            # Extract monetary indicators
            salary = self._extract_monetary_value(opportunity, ['salary', 'budget', 'price', 'value'])

            if not salary:
                return 0.3  # Default score if no monetary value found

            # Normalize against target rate
            target_rate = self.user_profile['hourly_rate_target']
            estimated_hours = self._estimate_hours_from_opportunity(opportunity)

            if estimated_hours > 0:
                effective_hourly = salary / estimated_hours
                profit_score = min(1.0, effective_hourly / (target_rate * 1.5))
            else:
                # For fixed-price opportunities
                profit_score = min(1.0, salary / 100000)  # Normalize to $100k max

            return max(0.0, profit_score)

        except Exception as e:
            logger.warning(f"⚠️ Profit scoring error: {e}")
            return 0.3

    async def _score_success_probability(self, opportunity: Dict) -> float:
        """Score success probability based on requirements match"""
        try:
            # Analyze requirements vs skills
            requirements = self._extract_requirements(opportunity)
            skills_match = await self._calculate_skills_overlap(requirements)

            # Experience level match
            exp_required = self._extract_experience_requirement(opportunity)
            exp_match = min(1.0, self.user_profile['experience_years'] / max(exp_required, 1))

            # Location compatibility
            location_score = self._score_location_match(opportunity)

            # Competition analysis (inverse relationship)
            competition = await self._analyze_competition_level(opportunity)
            competition_score = 1.0 - (competition / 10.0)  # Lower competition = higher success

            # Weighted average
            success_prob = (
                skills_match * 0.4 +
                exp_match * 0.3 +
                location_score * 0.2 +
                competition_score * 0.1
            )

            return max(0.0, min(1.0, success_prob))

        except Exception as e:
            logger.warning(f"⚠️ Success probability scoring error: {e}")
            return 0.5

    async def _score_time_investment(self, opportunity: Dict) -> float:
        """Score time investment (higher score = less time needed)"""
        try:
            estimated_hours = self._estimate_hours_from_opportunity(opportunity)

            # Prefer opportunities with reasonable time commitments
            if estimated_hours <= 10:  # Quick wins
                return 1.0
            elif estimated_hours <= 40:  # Week-long projects
                return 0.8
            elif estimated_hours <= 160:  # Month-long projects
                return 0.6
            elif estimated_hours <= 400:  # Quarter-long projects
                return 0.4
            else:  # Long-term commitments
                return 0.2

        except Exception as e:
            logger.warning(f"⚠️ Time investment scoring error: {e}")
            return 0.5

    async def _score_skill_match(self, opportunity: Dict) -> float:
        """Score how well opportunity matches user skills"""
        try:
            requirements = self._extract_requirements(opportunity)
            return await self._calculate_skills_overlap(requirements)

        except Exception as e:
            logger.warning(f"⚠️ Skill match scoring error: {e}")
            return 0.5

    async def _score_competition_level(self, opportunity: Dict) -> float:
        """Score competition level (higher score = less competition)"""
        try:
            competition_level = await self._analyze_competition_level(opportunity)

            # Convert to 0-1 score (inverse of competition)
            # 1-2 competitors = 1.0, 10+ competitors = 0.1
            if competition_level <= 2:
                return 1.0
            elif competition_level <= 5:
                return 0.8
            elif competition_level <= 10:
                return 0.6
            elif competition_level <= 20:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.warning(f"⚠️ Competition scoring error: {e}")
            return 0.5

    def _extract_monetary_value(self, opportunity: Dict, fields: List[str]) -> float:
        """Extract monetary value from opportunity"""
        for field in fields:
            value = opportunity.get(field)
            if value:
                # Handle string values like "$50,000", "$50-75K", etc.
                if isinstance(value, str):
                    # Extract numbers from string
                    numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', value.replace('$', '').replace('k', '000').replace('K', '000'))
                    if numbers:
                        return float(numbers[0].replace(',', ''))
                elif isinstance(value, (int, float)):
                    return float(value)

        return 0.0

    def _estimate_hours_from_opportunity(self, opportunity: Dict) -> int:
        """Estimate hours needed for opportunity"""
        # Look for explicit time indicators
        duration_indicators = ['duration', 'timeline', 'deadline', 'hours', 'days', 'weeks']

        for field in duration_indicators:
            value = opportunity.get(field, '').lower()
            if 'hour' in value:
                hours = re.search(r'(\d+)', value)
                if hours:
                    return int(hours.group(1))
            elif 'day' in value:
                days = re.search(r'(\d+)', value)
                if days:
                    return int(days.group(1)) * 8
            elif 'week' in value:
                weeks = re.search(r'(\d+)', value)
                if weeks:
                    return int(weeks.group(1)) * 40

        # Estimate based on opportunity type and complexity
        opp_type = opportunity.get('type', 'unknown')
        description = str(opportunity.get('description', '')).lower()

        if opp_type == 'job':
            return 2000  # Full-time position (50 weeks * 40 hours)
        elif 'quick' in description or 'simple' in description:
            return 5
        elif 'complex' in description or 'enterprise' in description:
            return 200
        else:
            return 40  # Default to 1 week

    def _extract_requirements(self, opportunity: Dict) -> str:
        """Extract skill requirements from opportunity"""
        requirement_fields = ['requirements', 'skills', 'description', 'qualifications']

        requirements = []
        for field in requirement_fields:
            value = opportunity.get(field, '')
            if value:
                requirements.append(str(value))

        return ' '.join(requirements)

    async def _calculate_skills_overlap(self, requirements: str) -> float:
        """Calculate overlap between user skills and requirements"""
        try:
            if not requirements:
                return 0.5

            # Create skill vectors
            user_skills_text = ' '.join(self.user_profile['skills'])
            texts = [user_skills_text, requirements.lower()]

            # Calculate TF-IDF similarity
            tfidf_matrix = self.skills_vectorizer.fit_transform(texts)
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            # Also check for direct skill matches
            direct_matches = 0
            for skill in self.user_profile['skills']:
                if skill.lower() in requirements.lower():
                    direct_matches += 1

            direct_match_score = min(1.0, direct_matches / 5.0)  # Normalize to 5 skills

            # Combine scores
            final_score = (similarity_score * 0.7) + (direct_match_score * 0.3)

            return max(0.0, min(1.0, final_score))

        except Exception as e:
            logger.warning(f"⚠️ Skills overlap calculation error: {e}")
            return 0.5

    def _extract_experience_requirement(self, opportunity: Dict) -> int:
        """Extract experience requirement in years"""
        text = str(opportunity.get('description', '') + ' ' + opportunity.get('requirements', '')).lower()

        # Look for experience patterns
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:in|with)',
            r'minimum\s*(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?'
        ]

        for pattern in exp_patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))

        # Default based on seniority level
        if any(level in text for level in ['senior', 'lead', 'principal', 'architect']):
            return 5
        elif any(level in text for level in ['mid-level', 'intermediate']):
            return 3
        elif any(level in text for level in ['junior', 'entry']):
            return 1

        return 2  # Default

    def _score_location_match(self, opportunity: Dict) -> float:
        """Score location compatibility"""
        location = str(opportunity.get('location', '')).lower()
        user_location = self.user_profile.get('location', '').lower()

        if 'remote' in location or 'anywhere' in location:
            return 1.0
        elif user_location in location or location in user_location:
            return 0.8
        elif any(word in location for word in ['hybrid', 'flexible']):
            return 0.6
        else:
            return 0.3  # Location mismatch

    async def _analyze_competition_level(self, opportunity: Dict) -> int:
        """Analyze competition level (number of competitors)"""
        # Look for competition indicators
        description = str(opportunity.get('description', '')).lower()

        if 'urgent' in description or 'asap' in description:
            return 2  # Urgent projects have less competition
        elif 'popular' in description or 'many applicants' in description:
            return 15  # Popular projects have high competition
        elif 'niche' in description or 'specialized' in description:
            return 3  # Specialized projects have low competition

        # Estimate based on opportunity type and salary
        salary = self._extract_monetary_value(opportunity, ['salary', 'budget'])

        if salary > 150000:
            return 8  # High-pay attracts competition
        elif salary > 75000:
            return 12  # Medium-high competition
        elif salary > 30000:
            return 15  # High competition
        else:
            return 5  # Low-pay has less competition

    async def _estimate_revenue(self, opportunity: Dict) -> float:
        """Estimate potential revenue from opportunity"""
        opp_type = opportunity.get('type', 'unknown')

        if opp_type in self.revenue_models:
            return await self.revenue_models[opp_type](opportunity)
        else:
            return self._extract_monetary_value(opportunity, ['salary', 'budget', 'value'])

    async def _estimate_job_revenue(self, opportunity: Dict) -> float:
        """Estimate revenue from job opportunities"""
        salary = self._extract_monetary_value(opportunity, ['salary', 'annual_salary'])

        if salary:
            # Assume 1-year commitment
            return salary
        else:
            # Estimate based on experience and role
            hourly_rate = self.user_profile['hourly_rate_target']
            hours_per_year = 2080  # 40 hours/week * 52 weeks
            return hourly_rate * hours_per_year

    async def _estimate_freelance_revenue(self, opportunity: Dict) -> float:
        """Estimate revenue from freelance opportunities"""
        budget = self._extract_monetary_value(opportunity, ['budget', 'project_value'])

        if budget:
            return budget
        else:
            # Estimate based on time investment
            hours = self._estimate_hours_from_opportunity(opportunity)
            hourly_rate = self.user_profile['hourly_rate_target']
            return hours * hourly_rate

    async def _estimate_business_revenue(self, opportunity: Dict) -> float:
        """Estimate revenue from business opportunities"""
        # Business opportunities might have equity, revenue share, etc.
        direct_value = self._extract_monetary_value(opportunity, ['funding', 'revenue', 'value'])

        if direct_value:
            return direct_value * 0.1  # Assume 10% stake/share
        else:
            return 50000  # Conservative estimate

    async def _estimate_financial_revenue(self, opportunity: Dict) -> float:
        """Estimate revenue from financial opportunities"""
        investment = self._extract_monetary_value(opportunity, ['price', 'investment', 'cost'])

        if investment:
            # Assume 20% annual return
            return investment * 0.20
        else:
            return 5000  # Small investment return

    async def _estimate_real_estate_revenue(self, opportunity: Dict) -> float:
        """Estimate revenue from real estate opportunities"""
        property_value = self._extract_monetary_value(opportunity, ['price', 'rent', 'value'])

        if property_value:
            # Assume rental yield or appreciation
            return property_value * 0.08  # 8% annual return
        else:
            return 10000  # Conservative estimate

    def _estimate_time_investment(self, opportunity: Dict) -> int:
        """Estimate time investment in hours"""
        return self._estimate_hours_from_opportunity(opportunity)

    def _categorize_competition(self, competition_score: float) -> str:
        """Categorize competition level"""
        if competition_score >= 0.8:
            return "low"
        elif competition_score >= 0.5:
            return "medium"
        else:
            return "high"

    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate confidence in the scoring"""
        if not scores:
            return 0.0

        # Confidence based on variance of scores
        score_values = list(scores.values())
        mean_score = sum(score_values) / len(score_values)
        variance = sum((x - mean_score) ** 2 for x in score_values) / len(score_values)

        # Lower variance = higher confidence
        confidence = 1.0 - min(1.0, variance * 2)
        return max(0.1, confidence)

    def _generate_recommendation(self, scored_opp: OpportunityScore) -> str:
        """Generate recommendation based on scores"""
        total_score = scored_opp.total_score
        confidence = scored_opp.confidence

        if total_score >= 0.8 and confidence >= 0.7:
            return "apply"
        elif total_score >= 0.6 and confidence >= 0.5:
            return "review"
        else:
            return "skip"

    async def score_batch(self, opportunities: List[Dict]) -> List[OpportunityScore]:
        """Score a batch of opportunities"""
        logger.info(f"🎯 Scoring batch of {len(opportunities)} opportunities")

        # Score all opportunities concurrently
        scoring_tasks = []
        for opp in opportunities:
            task = asyncio.create_task(self.score_opportunity(opp))
            scoring_tasks.append(task)

        scored_opportunities = await asyncio.gather(*scoring_tasks)

        # Sort by total score (descending)
        scored_opportunities.sort(key=lambda x: x.total_score, reverse=True)

        # Assign ranks
        for i, scored_opp in enumerate(scored_opportunities, 1):
            scored_opp.rank = i

        # Store for performance tracking
        self.historical_scores.extend(scored_opportunities)

        logger.info(f"✅ Batch scoring complete. Top score: {scored_opportunities[0].total_score:.2f}")

        return scored_opportunities

    def get_top_opportunities(self, scored_opportunities: List[OpportunityScore],
                            limit: int = 10, min_score: float = 0.6) -> List[OpportunityScore]:
        """Get top opportunities above threshold"""
        filtered = [opp for opp in scored_opportunities
                   if opp.total_score >= min_score]

        return filtered[:limit]

    def get_scoring_analytics(self) -> Dict:
        """Get analytics on scoring performance"""
        if not self.historical_scores:
            return {'message': 'No scoring history available'}

        scores = [opp.total_score for opp in self.historical_scores]

        return {
            'total_scored': len(self.historical_scores),
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'high_score_count': len([s for s in scores if s >= 0.8]),
            'apply_recommendations': len([opp for opp in self.historical_scores if opp.recommendation == 'apply']),
            'skip_recommendations': len([opp for opp in self.historical_scores if opp.recommendation == 'skip']),
            'estimated_total_revenue': sum(opp.estimated_revenue for opp in self.historical_scores)
        }

    async def score_opportunities(self, opportunities: List[Dict], user_profile: Dict = None) -> List[Dict]:
        """Score multiple opportunities and return score data"""
        scored_results = []

        for opportunity in opportunities:
            try:
                scored_opp = await self.score_opportunity(opportunity, user_profile)

                # Convert to dict format expected by auto_apply
                score_data = {
                    'total_score': scored_opp.total_score,
                    'score_breakdown': scored_opp.scores,
                    'skill_match_details': {'skill_match': scored_opp.skill_match},
                    'revenue_estimate': scored_opp.estimated_revenue,
                    'time_investment': scored_opp.time_investment,
                    'success_probability': scored_opp.success_probability,
                    'recommendation': scored_opp.recommendation
                }

                scored_results.append(score_data)

            except Exception as e:
                logger.error(f"❌ Error scoring opportunity {opportunity.get('id', 'unknown')}: {e}")
                # Add default score for failed opportunities
                scored_results.append({
                    'total_score': 0.0,
                    'score_breakdown': {},
                    'skill_match_details': {},
                    'revenue_estimate': 0.0,
                    'time_investment': 0,
                    'success_probability': 0.0,
                    'recommendation': 'skip'
                })

        return scored_results


# Singleton instance
opportunity_scorer = OpportunityScorer()


# Public API functions
async def score_opportunity(opportunity: Dict) -> OpportunityScore:
    """Score a single opportunity"""
    return await opportunity_scorer.score_opportunity(opportunity)


async def score_opportunities(opportunities: List[Dict]) -> List[OpportunityScore]:
    """Score multiple opportunities"""
    return await opportunity_scorer.score_batch(opportunities)


def get_top_opportunities(scored_opportunities: List[OpportunityScore],
                         limit: int = 10) -> List[OpportunityScore]:
    """Get top-scoring opportunities"""
    return opportunity_scorer.get_top_opportunities(scored_opportunities, limit)


def get_scoring_stats() -> Dict:
    """Get scoring analytics"""
    return opportunity_scorer.get_scoring_analytics()