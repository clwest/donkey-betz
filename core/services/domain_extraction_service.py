"""
Domain Extraction Service
==========================

Session 350: Domain-Aware Spider Targeting

This service analyzes business ideas and extracts:
1. Primary domain (e.g., "fitness_coaching", "saas_tools", "ecommerce")
2. Domain tags for targeted spider queries
3. Suggested search queries for each domain

The goal is to transform generic spider queries into domain-specific ones:
    Before: "AI fitness app" → generic AI articles
    After:  "AI fitness app" → fitness, wearables, health_tech articles

Usage:
    from core.services.domain_extraction_service import DomainExtractionService

    service = DomainExtractionService()
    result = service.extract_domains("AI-powered fitness coaching app")
    # Returns: {
    #     'primary_domain': 'fitness_health',
    #     'domain_tags': ['fitness', 'ai', 'wearables', 'health_tech', 'coaching'],
    #     'spider_queries': ['AI fitness coach market', 'wearable fitness app competitors', ...],
    #     'spider_categories': ['tech', 'news', 'community'],
    #     'subreddits': ['fitness', 'loseit', 'quantifiedself', 'apple_watch']
    # }
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# Domain definitions with associated keywords, spider categories, and subreddits
DOMAIN_DEFINITIONS = {
    'fitness_health': {
        'keywords': ['fitness', 'workout', 'exercise', 'gym', 'health', 'wellness',
                     'nutrition', 'diet', 'weight loss', 'training', 'coaching',
                     'wearable', 'smartwatch', 'apple watch', 'fitbit', 'garmin'],
        'spider_categories': ['tech', 'news', 'community'],
        'subreddits': ['fitness', 'loseit', 'nutrition', 'bodyweightfitness',
                       'running', 'cycling', 'quantifiedself', 'apple_watch',
                       'fitbit', 'garmin', 'xxfitness', 'gainit'],
        'search_templates': [
            '{topic} market size',
            '{topic} app competitors',
            '{topic} startup funding',
            'best {topic} apps 2024',
            '{topic} user retention',
            '{topic} monetization strategies'
        ]
    },
    'saas_b2b': {
        'keywords': ['saas', 'b2b', 'enterprise', 'software', 'platform', 'tool',
                     'productivity', 'workflow', 'automation', 'integration', 'api'],
        'spider_categories': ['tech', 'news', 'jobs'],
        'subreddits': ['saas', 'startups', 'entrepreneur', 'smallbusiness',
                       'productivity', 'notion', 'asana', 'monday'],
        'search_templates': [
            '{topic} market analysis',
            '{topic} competitors comparison',
            '{topic} pricing models',
            'enterprise {topic} solutions',
            '{topic} integration requirements'
        ]
    },
    'ecommerce_retail': {
        'keywords': ['ecommerce', 'retail', 'shop', 'store', 'marketplace',
                     'selling', 'products', 'dropshipping', 'inventory', 'fulfillment'],
        'spider_categories': ['tech', 'news', 'financial'],
        'subreddits': ['ecommerce', 'shopify', 'amazon', 'dropship',
                       'smallbusiness', 'entrepreneur', 'flipping'],
        'search_templates': [
            '{topic} market trends',
            '{topic} platform comparison',
            '{topic} logistics solutions',
            '{topic} customer acquisition cost'
        ]
    },
    'fintech_finance': {
        'keywords': ['fintech', 'finance', 'banking', 'payment', 'investment',
                     'trading', 'crypto', 'blockchain', 'lending', 'insurance'],
        'spider_categories': ['tech', 'financial', 'news'],
        'subreddits': ['fintech', 'personalfinance', 'investing', 'cryptocurrency',
                       'stocks', 'financialindependence', 'banking'],
        'search_templates': [
            '{topic} regulatory landscape',
            '{topic} market size TAM',
            '{topic} competitors funding',
            '{topic} compliance requirements'
        ]
    },
    'edtech_learning': {
        'keywords': ['education', 'learning', 'course', 'training', 'tutoring',
                     'school', 'student', 'teacher', 'curriculum', 'certification'],
        'spider_categories': ['tech', 'news', 'community'],
        'subreddits': ['edtech', 'education', 'learnprogramming', 'languagelearning',
                       'udemy', 'coursera', 'teachers', 'homeschool'],
        'search_templates': [
            '{topic} platform market',
            '{topic} completion rates',
            '{topic} pricing strategies',
            'online {topic} competitors'
        ]
    },
    'food_restaurant': {
        'keywords': ['food', 'restaurant', 'dining', 'delivery', 'kitchen',
                     'chef', 'menu', 'catering', 'cafe', 'bar', 'cooking'],
        'spider_categories': ['news', 'community'],
        'subreddits': ['restaurant', 'KitchenConfidential', 'foodservice',
                       'restaurateur', 'smallbusiness', 'food', 'cooking'],
        'search_templates': [
            '{topic} industry trends',
            '{topic} startup costs',
            '{topic} franchise opportunities',
            '{topic} technology solutions'
        ]
    },
    'mental_health': {
        'keywords': ['mental health', 'therapy', 'counseling', 'meditation',
                     'anxiety', 'depression', 'mindfulness', 'wellness', 'stress'],
        'spider_categories': ['tech', 'news', 'community'],
        'subreddits': ['mentalhealth', 'anxiety', 'depression', 'meditation',
                       'therapy', 'selfimprovement', 'getmotivated'],
        'search_templates': [
            '{topic} app market size',
            '{topic} digital therapeutics',
            '{topic} regulatory requirements',
            '{topic} user engagement metrics'
        ]
    },
    'ai_ml': {
        'keywords': ['ai', 'artificial intelligence', 'machine learning', 'ml',
                     'neural network', 'deep learning', 'nlp', 'computer vision',
                     'generative ai', 'llm', 'chatbot', 'automation'],
        'spider_categories': ['tech', 'news', 'community'],
        'subreddits': ['MachineLearning', 'artificial', 'LocalLLaMA',
                       'ChatGPT', 'OpenAI', 'StableDiffusion', 'singularity'],
        'search_templates': [
            '{topic} market landscape',
            '{topic} startup funding 2024',
            '{topic} use cases enterprise',
            '{topic} competitors comparison'
        ]
    },
    'creator_economy': {
        'keywords': ['creator', 'content', 'influencer', 'youtube', 'tiktok',
                     'podcast', 'streaming', 'monetization', 'newsletter', 'substack'],
        'spider_categories': ['tech', 'news', 'creative', 'community'],
        'subreddits': ['youtube', 'Twitch', 'podcasting', 'NewTubers',
                       'ContentCreators', 'blogging', 'substack'],
        'search_templates': [
            '{topic} monetization strategies',
            '{topic} platform comparison',
            '{topic} creator tools market',
            '{topic} audience growth'
        ]
    },
    'real_estate': {
        'keywords': ['real estate', 'property', 'housing', 'rental', 'mortgage',
                     'landlord', 'tenant', 'proptech', 'commercial real estate'],
        'spider_categories': ['news', 'financial', 'community'],
        'subreddits': ['RealEstate', 'realestateinvesting', 'landlord',
                       'FirstTimeHomeBuyer', 'PropertyManagement', 'CommercialRealEstate'],
        'search_templates': [
            '{topic} market trends',
            '{topic} technology solutions',
            '{topic} investment strategies',
            'proptech {topic} startups'
        ]
    },
    'gaming_entertainment': {
        'keywords': ['gaming', 'game', 'esports', 'streaming', 'entertainment',
                     'mobile game', 'console', 'pc gaming', 'indie game'],
        'spider_categories': ['tech', 'news', 'community'],
        'subreddits': ['gaming', 'gamedev', 'IndieGaming', 'esports',
                       'MobileGaming', 'pcgaming', 'Games'],
        'search_templates': [
            '{topic} market size',
            '{topic} monetization models',
            '{topic} user acquisition',
            '{topic} platform requirements'
        ]
    },
    'travel_hospitality': {
        'keywords': ['travel', 'hotel', 'booking', 'tourism', 'vacation',
                     'airbnb', 'hospitality', 'flight', 'destination'],
        'spider_categories': ['news', 'community'],
        'subreddits': ['travel', 'solotravel', 'TravelHacks', 'digitalnomad',
                       'AirBnB', 'hotels', 'backpacking'],
        'search_templates': [
            '{topic} industry recovery',
            '{topic} booking platform comparison',
            '{topic} technology trends',
            '{topic} customer experience'
        ]
    },
    'general_startup': {
        'keywords': ['startup', 'business', 'venture', 'company', 'product'],
        'spider_categories': ['tech', 'news', 'financial', 'community'],
        'subreddits': ['startups', 'entrepreneur', 'smallbusiness',
                       'SideProject', 'business'],
        'search_templates': [
            '{topic} market opportunity',
            '{topic} competitive landscape',
            '{topic} business model',
            '{topic} go to market strategy'
        ]
    }
}


@dataclass
class DomainExtractionResult:
    """Result from domain extraction."""
    primary_domain: str
    domain_tags: List[str]
    spider_queries: List[str]
    spider_categories: List[str]
    subreddits: List[str]
    confidence: float
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            'primary_domain': self.primary_domain,
            'domain_tags': self.domain_tags,
            'spider_queries': self.spider_queries,
            'spider_categories': self.spider_categories,
            'subreddits': self.subreddits,
            'confidence': self.confidence,
            'reasoning': self.reasoning
        }


class DomainExtractionService:
    """
    Service for extracting domain information from business ideas.

    Uses a combination of keyword matching and GPT analysis to:
    1. Identify the primary business domain
    2. Extract relevant tags for spider targeting
    3. Generate domain-specific search queries
    """

    def __init__(self):
        self.domains = DOMAIN_DEFINITIONS

    def extract_domains(self, business_idea: str, use_gpt: bool = True) -> DomainExtractionResult:
        """
        Extract domain information from a business idea.

        Args:
            business_idea: The business idea or project description
            use_gpt: Whether to use GPT for enhanced extraction (default True)

        Returns:
            DomainExtractionResult with domain info and spider targeting
        """
        # First, do keyword-based extraction for speed
        keyword_result = self._keyword_extraction(business_idea)

        # If GPT is enabled and we have a decent idea, enhance with GPT
        if use_gpt and len(business_idea) > 20:
            try:
                gpt_result = self._gpt_extraction(business_idea, keyword_result)
                return gpt_result
            except Exception as e:
                logger.warning(f"GPT extraction failed, using keyword extraction: {e}")
                return keyword_result

        return keyword_result

    def _keyword_extraction(self, business_idea: str) -> DomainExtractionResult:
        """
        Extract domains using keyword matching.

        Fast but less accurate than GPT extraction.
        """
        idea_lower = business_idea.lower()

        # Score each domain based on keyword matches
        domain_scores = {}
        for domain_name, domain_config in self.domains.items():
            score = 0
            matched_keywords = []
            for keyword in domain_config['keywords']:
                if keyword.lower() in idea_lower:
                    score += 1
                    matched_keywords.append(keyword)
            if score > 0:
                domain_scores[domain_name] = {
                    'score': score,
                    'keywords': matched_keywords
                }

        # Get the best matching domain
        if domain_scores:
            best_domain = max(domain_scores.items(), key=lambda x: x[1]['score'])
            primary_domain = best_domain[0]
            matched_keywords = best_domain[1]['keywords']
            confidence = min(best_domain[1]['score'] / 5, 1.0)  # Normalize to 0-1
        else:
            primary_domain = 'general_startup'
            matched_keywords = []
            confidence = 0.3

        domain_config = self.domains[primary_domain]

        # Generate spider queries
        spider_queries = self._generate_queries(business_idea, domain_config)

        # Extract topic for tags
        topic_words = self._extract_topic_words(business_idea)
        domain_tags = list(set(matched_keywords + topic_words))[:10]

        return DomainExtractionResult(
            primary_domain=primary_domain,
            domain_tags=domain_tags,
            spider_queries=spider_queries,
            spider_categories=domain_config['spider_categories'],
            subreddits=domain_config['subreddits'][:8],
            confidence=confidence,
            reasoning=f"Matched keywords: {', '.join(matched_keywords)}" if matched_keywords else "No specific domain keywords found, using general startup domain"
        )

    def _gpt_extraction(self, business_idea: str, keyword_result: DomainExtractionResult) -> DomainExtractionResult:
        """
        Use GPT for enhanced domain extraction.

        More accurate but slower than keyword extraction.
        """
        from openai import OpenAI
        client = OpenAI()

        domain_list = list(self.domains.keys())

        prompt = f"""Analyze this business idea and extract domain targeting information.

Business Idea: {business_idea}

Available domains: {', '.join(domain_list)}

Respond in JSON format:
{{
    "primary_domain": "<best matching domain from the list>",
    "domain_tags": ["<5-8 relevant tags for this specific business>"],
    "search_queries": ["<5-7 specific search queries to find market data, competitors, and customer insights>"],
    "subreddits": ["<5-8 relevant subreddits where target customers discuss this topic>"],
    "reasoning": "<one sentence explaining the domain choice>"
}}

IMPORTANT:
- domain_tags should be SPECIFIC to this business (e.g., for fitness app: "wearables", "fitness_tracking", "health_coaching")
- search_queries should find RELEVANT market data, not generic AI news
- subreddits should be where ACTUAL CUSTOMERS of this product would be

Example for "AI-powered fitness coaching app":
{{
    "primary_domain": "fitness_health",
    "domain_tags": ["fitness", "ai_coaching", "wearables", "health_tech", "personal_training", "wellness_app"],
    "search_queries": ["AI fitness coach market size 2024", "wearable fitness app competitors", "digital personal training startups", "fitness app retention rates", "health coaching app monetization"],
    "subreddits": ["fitness", "loseit", "quantifiedself", "apple_watch", "bodyweightfitness", "running"],
    "reasoning": "This is a fitness/health tech product combining AI with personal training"
}}"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=500
            # Note: gpt-5-mini reasoning models don't support temperature
        )

        result = json.loads(response.choices[0].message.content)

        # Validate and use the result
        primary_domain = result.get('primary_domain', 'general_startup')
        if primary_domain not in self.domains:
            primary_domain = 'general_startup'

        domain_config = self.domains[primary_domain]

        # Merge GPT subreddits with domain defaults
        gpt_subreddits = result.get('subreddits', [])
        all_subreddits = list(set(gpt_subreddits + domain_config['subreddits'][:4]))[:10]

        return DomainExtractionResult(
            primary_domain=primary_domain,
            domain_tags=result.get('domain_tags', keyword_result.domain_tags),
            spider_queries=result.get('search_queries', keyword_result.spider_queries),
            spider_categories=domain_config['spider_categories'],
            subreddits=all_subreddits,
            confidence=0.85,  # GPT extraction is more confident
            reasoning=result.get('reasoning', 'GPT-based domain extraction')
        )

    def _generate_queries(self, business_idea: str, domain_config: Dict) -> List[str]:
        """Generate search queries from templates."""
        # Extract the main topic from the business idea
        topic = self._extract_main_topic(business_idea)

        queries = []
        for template in domain_config.get('search_templates', []):
            query = template.format(topic=topic)
            queries.append(query)

        # Add a few general queries
        queries.append(f"{topic} startups 2024")
        queries.append(f"{topic} market trends")

        return queries[:7]

    def _extract_main_topic(self, business_idea: str) -> str:
        """Extract the main topic/product from the business idea."""
        # Remove common filler words and extract key concept
        filler_words = ['a', 'an', 'the', 'for', 'that', 'which', 'to', 'is', 'are',
                        'app', 'platform', 'tool', 'service', 'business', 'startup']

        words = business_idea.lower().split()
        topic_words = [w for w in words if w not in filler_words and len(w) > 2]

        # Return first 3-4 meaningful words
        return ' '.join(topic_words[:4])

    def _extract_topic_words(self, business_idea: str) -> List[str]:
        """Extract individual topic words as tags."""
        filler_words = ['a', 'an', 'the', 'for', 'that', 'which', 'to', 'is', 'are',
                        'app', 'platform', 'tool', 'service', 'business', 'startup',
                        'with', 'and', 'or', 'in', 'on', 'by', 'of', 'ai', 'powered']

        words = business_idea.lower().split()
        topic_words = [w.strip('.,!?-') for w in words
                       if w.strip('.,!?-') not in filler_words and len(w) > 2]

        return topic_words[:8]

    def get_domain_config(self, domain_name: str) -> Optional[Dict]:
        """Get configuration for a specific domain."""
        return self.domains.get(domain_name)

    def list_domains(self) -> List[str]:
        """List all available domains."""
        return list(self.domains.keys())


# Convenience function
def extract_domains(business_idea: str, use_gpt: bool = True) -> DomainExtractionResult:
    """Extract domain information from a business idea."""
    service = DomainExtractionService()
    return service.extract_domains(business_idea, use_gpt)


# Singleton instance
_domain_service = None

def get_domain_extraction_service() -> DomainExtractionService:
    """Get singleton instance of DomainExtractionService."""
    global _domain_service
    if _domain_service is None:
        _domain_service = DomainExtractionService()
    return _domain_service
