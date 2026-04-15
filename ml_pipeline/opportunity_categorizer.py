"""
ML-Powered Opportunity Categorizer
Automatically categorizes and enriches opportunities for frontend display
"""

import logging
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

logger = logging.getLogger(__name__)


class OpportunityCategorizationSystem:
    """
    ML-powered system to categorize and enrich opportunities for frontend display
    """

    def __init__(self):
        """Initialize the categorization system"""

        # Define our income categories with detailed subcategories
        self.category_definitions = {
            'freelance_work': {
                'display_name': 'Freelance & Contract',
                'icon': '💼',
                'color': '#3B82F6',
                'subcategories': {
                    'writing': {'name': 'Content Writing', 'keywords': ['writing', 'content', 'blog', 'article', 'copywriting']},
                    'programming': {'name': 'Programming', 'keywords': ['python', 'javascript', 'react', 'development', 'coding']},
                    'design': {'name': 'Design & Creative', 'keywords': ['design', 'graphic', 'ui', 'ux', 'creative']},
                    'marketing': {'name': 'Digital Marketing', 'keywords': ['marketing', 'seo', 'social media', 'advertising']},
                    'consulting': {'name': 'Consulting', 'keywords': ['consulting', 'strategy', 'business', 'advisory']}
                }
            },
            'full_time_jobs': {
                'display_name': 'Full-Time Jobs',
                'icon': '🏢',
                'color': '#10B981',
                'subcategories': {
                    'tech': {'name': 'Technology', 'keywords': ['engineer', 'developer', 'software', 'tech', 'programming']},
                    'remote': {'name': 'Remote Work', 'keywords': ['remote', 'work from home', 'distributed', 'anywhere']},
                    'management': {'name': 'Management', 'keywords': ['manager', 'director', 'lead', 'supervisor']},
                    'sales': {'name': 'Sales & Business', 'keywords': ['sales', 'business development', 'account manager']},
                    'healthcare': {'name': 'Healthcare', 'keywords': ['healthcare', 'medical', 'nurse', 'doctor']}
                }
            },
            'e_commerce': {
                'display_name': 'E-Commerce & Selling',
                'icon': '🛒',
                'color': '#F59E0B',
                'subcategories': {
                    'amazon_fba': {'name': 'Amazon FBA', 'keywords': ['amazon', 'fba', 'fulfillment', 'selling']},
                    'dropshipping': {'name': 'Dropshipping', 'keywords': ['dropshipping', 'shopify', 'ecommerce', 'online store']},
                    'handmade': {'name': 'Handmade & Crafts', 'keywords': ['etsy', 'handmade', 'crafts', 'artisan']},
                    'print_on_demand': {'name': 'Print on Demand', 'keywords': ['print on demand', 'pod', 'tshirt', 'designs']},
                    'marketplace': {'name': 'Marketplace Selling', 'keywords': ['ebay', 'facebook marketplace', 'reselling']}
                }
            },
            'digital_services': {
                'display_name': 'Digital Services',
                'icon': '💻',
                'color': '#8B5CF6',
                'subcategories': {
                    'coaching': {'name': 'Online Coaching', 'keywords': ['coaching', 'life coach', 'business coach', 'mentoring']},
                    'tutoring': {'name': 'Online Tutoring', 'keywords': ['tutoring', 'teaching', 'education', 'instructor']},
                    'virtual_assistant': {'name': 'Virtual Assistant', 'keywords': ['virtual assistant', 'va', 'administrative', 'support']},
                    'course_creation': {'name': 'Course Creation', 'keywords': ['course', 'udemy', 'teachable', 'online learning']},
                    'saas': {'name': 'SaaS & Apps', 'keywords': ['saas', 'software', 'app', 'subscription']}
                }
            },
            'real_estate': {
                'display_name': 'Real Estate',
                'icon': '🏠',
                'color': '#EF4444',
                'subcategories': {
                    'rental_property': {'name': 'Rental Properties', 'keywords': ['rental', 'landlord', 'investment property', 'cash flow']},
                    'airbnb': {'name': 'Short-Term Rentals', 'keywords': ['airbnb', 'short term rental', 'vacation rental', 'hosting']},
                    'wholesaling': {'name': 'Wholesaling', 'keywords': ['wholesaling', 'assignment', 'distressed property', 'rehab']},
                    'flipping': {'name': 'House Flipping', 'keywords': ['flipping', 'renovation', 'fix and flip', 'remodel']},
                    'commercial': {'name': 'Commercial RE', 'keywords': ['commercial', 'office', 'retail', 'warehouse']}
                }
            },
            'content_creation': {
                'display_name': 'Content & Media',
                'icon': '📺',
                'color': '#F97316',
                'subcategories': {
                    'youtube': {'name': 'YouTube', 'keywords': ['youtube', 'video', 'subscriber', 'monetization']},
                    'blogging': {'name': 'Blogging', 'keywords': ['blog', 'wordpress', 'writing', 'affiliate']},
                    'podcasting': {'name': 'Podcasting', 'keywords': ['podcast', 'audio', 'spotify', 'interviewing']},
                    'social_media': {'name': 'Social Media', 'keywords': ['instagram', 'tiktok', 'twitter', 'influencer']},
                    'photography': {'name': 'Photography', 'keywords': ['photography', 'stock photos', 'wedding', 'portrait']}
                }
            },
            'investing_trading': {
                'display_name': 'Investing & Trading',
                'icon': '📈',
                'color': '#06B6D4',
                'subcategories': {
                    'stocks': {'name': 'Stock Trading', 'keywords': ['stocks', 'equity', 'trading', 'nasdaq']},
                    'crypto': {'name': 'Cryptocurrency', 'keywords': ['crypto', 'bitcoin', 'ethereum', 'blockchain']},
                    'forex': {'name': 'Forex Trading', 'keywords': ['forex', 'currency', 'fx', 'pairs']},
                    'options': {'name': 'Options Trading', 'keywords': ['options', 'calls', 'puts', 'derivatives']},
                    'commodities': {'name': 'Commodities', 'keywords': ['gold', 'oil', 'commodities', 'futures']}
                }
            },
            'local_services': {
                'display_name': 'Local Services',
                'icon': '🔧',
                'color': '#84CC16',
                'subcategories': {
                    'home_services': {'name': 'Home Services', 'keywords': ['cleaning', 'landscaping', 'handyman', 'maintenance']},
                    'delivery': {'name': 'Delivery & Transport', 'keywords': ['uber', 'doordash', 'delivery', 'driving']},
                    'fitness': {'name': 'Fitness & Health', 'keywords': ['personal trainer', 'yoga', 'fitness', 'wellness']},
                    'events': {'name': 'Events & Entertainment', 'keywords': ['dj', 'photography', 'catering', 'events']},
                    'pet_services': {'name': 'Pet Services', 'keywords': ['dog walking', 'pet sitting', 'grooming', 'veterinary']}
                }
            }
        }

        # Initialize ML models
        self.categorizer_model = None
        self.subcategory_models = {}
        self.tfidf_vectorizer = None

        # Load or create models
        self._initialize_models()

        logger.info(f"🏷️ Opportunity Categorization System initialized")
        logger.info(f"📊 Categories: {len(self.category_definitions)}")
        logger.info(f"🎯 Subcategories: {sum(len(cat['subcategories']) for cat in self.category_definitions.values())}")

    def _initialize_models(self):
        """Initialize or load ML models for categorization"""
        try:
            # Try to load existing models
            model_path = "ml_models/categorizer.pkl"
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.categorizer_model = model_data['model']
                    self.tfidf_vectorizer = model_data['vectorizer']
                logger.info("✅ Loaded existing categorization model")
            else:
                # Create and train new model with synthetic data
                self._train_categorization_model()

        except Exception as e:
            logger.warning(f"Could not load models: {e}")
            self._train_categorization_model()

    def _train_categorization_model(self):
        """Train categorization model with synthetic training data"""
        logger.info("🎓 Training categorization model with synthetic data")

        # Generate training data
        training_texts = []
        training_labels = []

        for category, config in self.category_definitions.items():
            # Generate synthetic examples for each category
            category_examples = self._generate_category_examples(category, config)
            training_texts.extend(category_examples)
            training_labels.extend([category] * len(category_examples))

        # Create and train pipeline
        self.categorizer_model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, stop_words='english')),
            ('classifier', MultinomialNB())
        ])

        self.categorizer_model.fit(training_texts, training_labels)
        self.tfidf_vectorizer = self.categorizer_model.named_steps['tfidf']

        # Save model
        os.makedirs("ml_models", exist_ok=True)
        with open("ml_models/categorizer.pkl", 'wb') as f:
            pickle.dump({
                'model': self.categorizer_model,
                'vectorizer': self.tfidf_vectorizer
            }, f)

        logger.info("✅ Categorization model trained and saved")

    def _generate_category_examples(self, category: str, config: Dict) -> List[str]:
        """Generate synthetic training examples for a category"""
        examples = []

        # Base examples
        base_templates = [
            "{keyword} opportunity available",
            "Looking for {keyword} professional",
            "Hiring {keyword} expert",
            "{keyword} position open",
            "Seeking {keyword} specialist",
            "{keyword} work available",
            "Join our {keyword} team",
            "{keyword} freelancer needed"
        ]

        # Generate examples for main category
        category_keywords = [config['display_name'].lower()]

        # Add subcategory keywords
        for subcat_config in config['subcategories'].values():
            category_keywords.extend(subcat_config['keywords'])

        # Create examples
        for keyword in category_keywords[:10]:  # Limit to prevent too much data
            for template in base_templates[:3]:  # Use subset of templates
                examples.append(template.format(keyword=keyword))

        return examples

    async def categorize_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize and enrich a single opportunity

        Args:
            opportunity: Raw opportunity data

        Returns:
            Enriched opportunity with category information
        """
        try:
            # Extract text for categorization
            text_content = self._extract_text_content(opportunity)

            # Get main category
            main_category = self._predict_main_category(text_content)
            category_config = self.category_definitions[main_category]

            # Get subcategory
            subcategory = self._predict_subcategory(text_content, main_category)

            # Calculate confidence scores
            confidence = self._calculate_confidence(text_content, main_category)

            # Extract financial information
            financial_info = self._extract_financial_info(opportunity)

            # Assess opportunity quality
            quality_score = self._assess_opportunity_quality(opportunity, main_category)

            # Create enriched opportunity
            enriched_opportunity = {
                **opportunity,
                'category': {
                    'main': main_category,
                    'display_name': category_config['display_name'],
                    'icon': category_config['icon'],
                    'color': category_config['color'],
                    'subcategory': subcategory,
                    'confidence': confidence
                },
                'financial': financial_info,
                'quality': quality_score,
                'enrichment': {
                    'processed_at': datetime.now().isoformat(),
                    'ml_version': '1.0.0',
                    'tags': self._generate_tags(text_content, main_category),
                    'difficulty_level': self._assess_difficulty(opportunity, main_category),
                    'time_commitment': self._assess_time_commitment(opportunity, main_category),
                    'skill_requirements': self._extract_skill_requirements(text_content)
                }
            }

            return enriched_opportunity

        except Exception as e:
            logger.error(f"Error categorizing opportunity: {e}")
            # Return original opportunity with default category
            return {
                **opportunity,
                'category': {
                    'main': 'freelance_work',
                    'display_name': 'Uncategorized',
                    'icon': '❓',
                    'color': '#6B7280',
                    'subcategory': 'general',
                    'confidence': 0.1
                },
                'error': str(e)
            }

    def _extract_text_content(self, opportunity: Dict[str, Any]) -> str:
        """Extract relevant text content for categorization"""
        text_parts = []

        # Get title
        if 'title' in opportunity:
            text_parts.append(str(opportunity['title']))

        # Get description
        if 'description' in opportunity:
            text_parts.append(str(opportunity['description']))

        # Get tags
        if 'tags' in opportunity and isinstance(opportunity['tags'], list):
            text_parts.extend(opportunity['tags'])

        # Get company info
        if 'company' in opportunity:
            text_parts.append(str(opportunity['company']))

        return ' '.join(text_parts).lower()

    def _predict_main_category(self, text_content: str) -> str:
        """Predict main category using ML model"""
        try:
            if self.categorizer_model:
                prediction = self.categorizer_model.predict([text_content])[0]
                return prediction
        except Exception as e:
            logger.warning(f"ML prediction failed: {e}")

        # Fallback to keyword matching
        return self._keyword_based_categorization(text_content)

    def _keyword_based_categorization(self, text_content: str) -> str:
        """Fallback keyword-based categorization"""
        category_scores = {}

        for category, config in self.category_definitions.items():
            score = 0

            # Check subcategory keywords
            for subcat_config in config['subcategories'].values():
                for keyword in subcat_config['keywords']:
                    if keyword.lower() in text_content:
                        score += 1

            category_scores[category] = score

        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)

        return 'freelance_work'  # Default category

    def _predict_subcategory(self, text_content: str, main_category: str) -> str:
        """Predict subcategory within main category"""
        category_config = self.category_definitions[main_category]
        subcategory_scores = {}

        for subcat_key, subcat_config in category_config['subcategories'].items():
            score = 0
            for keyword in subcat_config['keywords']:
                if keyword.lower() in text_content:
                    score += 1
            subcategory_scores[subcat_key] = score

        if subcategory_scores:
            return max(subcategory_scores, key=subcategory_scores.get)

        # Return first subcategory as default
        return list(category_config['subcategories'].keys())[0]

    def _calculate_confidence(self, text_content: str, predicted_category: str) -> float:
        """Calculate confidence score for categorization"""
        try:
            if self.categorizer_model:
                probabilities = self.categorizer_model.predict_proba([text_content])[0]
                categories = self.categorizer_model.classes_
                category_index = list(categories).index(predicted_category)
                return float(probabilities[category_index])
        except:
            pass

        # Fallback confidence based on keyword matches
        category_config = self.category_definitions[predicted_category]
        matches = 0
        total_keywords = 0

        for subcat_config in category_config['subcategories'].values():
            total_keywords += len(subcat_config['keywords'])
            for keyword in subcat_config['keywords']:
                if keyword.lower() in text_content:
                    matches += 1

        return min(0.9, max(0.1, matches / max(total_keywords, 1)))

    def _extract_financial_info(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize financial information"""
        financial_info = {
            'budget_min': None,
            'budget_max': None,
            'currency': 'USD',
            'payment_type': 'unknown',  # hourly, fixed, salary, commission
            'payment_frequency': 'unknown'  # once, weekly, monthly, annually
        }

        # Check various budget/salary fields
        budget_fields = ['budget', 'salary', 'price', 'rate', 'pay']
        budget_text = ''

        for field in budget_fields:
            if field in opportunity and opportunity[field]:
                budget_text += str(opportunity[field]) + ' '

        if budget_text:
            # Extract numbers and payment info
            amounts = self._extract_amounts(budget_text)
            payment_info = self._extract_payment_info(budget_text)

            if amounts:
                financial_info['budget_min'] = min(amounts)
                financial_info['budget_max'] = max(amounts)

            financial_info.update(payment_info)

        return financial_info

    def _extract_amounts(self, text: str) -> List[float]:
        """Extract monetary amounts from text"""
        # Find patterns like $1000, $1,000, $1K, $1.5K, etc.
        patterns = [
            r'\$[\d,]+(?:\.\d{2})?',  # $1,000.00
            r'\$\d+\.?\d*[kK]',       # $1K, $1.5K
            r'\d+[kK]',               # 50K
            r'\d+,\d+',               # 1,000
            r'\d+'                    # 1000
        ]

        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = self._parse_amount(match)
                if amount and amount > 0:
                    amounts.append(amount)

        return amounts

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float"""
        try:
            # Clean the string
            clean_str = amount_str.replace('$', '').replace(',', '')

            # Handle K notation
            if clean_str.lower().endswith('k'):
                return float(clean_str[:-1]) * 1000

            return float(clean_str)
        except Exception as _e:
            logger.warning(
                "opportunity_categorizer._parse_amount: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _extract_payment_info(self, text: str) -> Dict[str, str]:
        """Extract payment type and frequency information"""
        payment_info = {}

        text_lower = text.lower()

        # Payment type
        if any(word in text_lower for word in ['hour', 'hr', '/hr']):
            payment_info['payment_type'] = 'hourly'
        elif any(word in text_lower for word in ['fixed', 'project', 'one-time']):
            payment_info['payment_type'] = 'fixed'
        elif any(word in text_lower for word in ['salary', 'annual', 'yearly']):
            payment_info['payment_type'] = 'salary'
        elif any(word in text_lower for word in ['commission', '%', 'percent']):
            payment_info['payment_type'] = 'commission'

        # Payment frequency
        if any(word in text_lower for word in ['month', 'monthly']):
            payment_info['payment_frequency'] = 'monthly'
        elif any(word in text_lower for word in ['week', 'weekly']):
            payment_info['payment_frequency'] = 'weekly'
        elif any(word in text_lower for word in ['year', 'annual', 'yearly']):
            payment_info['payment_frequency'] = 'annually'
        elif any(word in text_lower for word in ['daily', 'day']):
            payment_info['payment_frequency'] = 'daily'

        return payment_info

    def _assess_opportunity_quality(self, opportunity: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Assess the quality and attractiveness of an opportunity"""
        quality_factors = {
            'budget_attractiveness': 0.5,
            'description_quality': 0.5,
            'company_reputation': 0.5,
            'requirements_clarity': 0.5,
            'overall_score': 0.5
        }

        # Assess budget attractiveness
        financial_info = self._extract_financial_info(opportunity)
        if financial_info['budget_min']:
            quality_factors['budget_attractiveness'] = self._score_budget(
                financial_info['budget_min'], category
            )

        # Assess description quality
        description = opportunity.get('description', '')
        if description:
            quality_factors['description_quality'] = min(1.0, len(description) / 500)

        # Calculate overall score
        quality_factors['overall_score'] = sum(quality_factors.values()) / len(quality_factors)

        return quality_factors

    def _score_budget(self, budget: float, category: str) -> float:
        """Score budget attractiveness for category"""
        # Category-specific budget thresholds
        budget_thresholds = {
            'freelance_work': {'low': 500, 'good': 2000, 'excellent': 5000},
            'full_time_jobs': {'low': 40000, 'good': 70000, 'excellent': 120000},
            'e_commerce': {'low': 1000, 'good': 5000, 'excellent': 20000},
            'digital_services': {'low': 500, 'good': 3000, 'excellent': 10000},
            'real_estate': {'low': 10000, 'good': 50000, 'excellent': 200000}
        }

        thresholds = budget_thresholds.get(category, budget_thresholds['freelance_work'])

        if budget >= thresholds['excellent']:
            return 1.0
        elif budget >= thresholds['good']:
            return 0.8
        elif budget >= thresholds['low']:
            return 0.6
        else:
            return 0.3

    def _generate_tags(self, text_content: str, category: str) -> List[str]:
        """Generate relevant tags for the opportunity"""
        tags = []

        # Add category-specific tags
        category_config = self.category_definitions[category]
        for subcat_config in category_config['subcategories'].values():
            for keyword in subcat_config['keywords']:
                if keyword.lower() in text_content:
                    tags.append(keyword.title())

        # Add common skill tags
        skill_keywords = [
            'python', 'javascript', 'react', 'design', 'marketing',
            'writing', 'seo', 'social media', 'consulting', 'remote'
        ]

        for skill in skill_keywords:
            if skill.lower() in text_content:
                tags.append(skill.title())

        return list(set(tags))[:10]  # Limit to 10 unique tags

    def _assess_difficulty(self, opportunity: Dict[str, Any], category: str) -> str:
        """Assess difficulty level of opportunity"""
        text_content = self._extract_text_content(opportunity)

        # Check for difficulty indicators
        if any(word in text_content for word in ['senior', 'expert', 'advanced', 'lead']):
            return 'advanced'
        elif any(word in text_content for word in ['junior', 'entry', 'beginner', 'intern']):
            return 'beginner'
        else:
            return 'intermediate'

    def _assess_time_commitment(self, opportunity: Dict[str, Any], category: str) -> str:
        """Assess time commitment required"""
        text_content = self._extract_text_content(opportunity)

        # Check for time indicators
        if any(word in text_content for word in ['full-time', 'full time', '40 hours']):
            return 'full_time'
        elif any(word in text_content for word in ['part-time', 'part time', 'flexible']):
            return 'part_time'
        elif any(word in text_content for word in ['project', 'contract', 'one-time']):
            return 'project_based'
        else:
            return 'flexible'

    def _extract_skill_requirements(self, text_content: str) -> List[str]:
        """Extract skill requirements from opportunity text"""
        common_skills = [
            'python', 'javascript', 'react', 'vue', 'angular', 'node.js',
            'django', 'flask', 'sql', 'postgresql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'git',
            'photoshop', 'illustrator', 'figma', 'sketch',
            'seo', 'google ads', 'facebook ads', 'analytics',
            'excel', 'powerpoint', 'word', 'salesforce'
        ]

        found_skills = []
        for skill in common_skills:
            if skill.lower() in text_content:
                found_skills.append(skill)

        return found_skills

    async def categorize_batch(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize a batch of opportunities

        Args:
            opportunities: List of raw opportunities

        Returns:
            List of categorized and enriched opportunities
        """
        categorized_opportunities = []

        for opportunity in opportunities:
            categorized = await self.categorize_opportunity(opportunity)
            categorized_opportunities.append(categorized)

        logger.info(f"📊 Categorized {len(categorized_opportunities)} opportunities")

        return categorized_opportunities

    def get_category_summary(self, categorized_opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for categorized opportunities"""
        summary = {
            'total_opportunities': len(categorized_opportunities),
            'categories': {},
            'financial_summary': {},
            'quality_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }

        for opp in categorized_opportunities:
            category = opp.get('category', {}).get('main', 'unknown')

            # Count by category
            if category not in summary['categories']:
                summary['categories'][category] = {
                    'count': 0,
                    'display_name': opp.get('category', {}).get('display_name', category),
                    'icon': opp.get('category', {}).get('icon', '❓'),
                    'subcategories': {}
                }

            summary['categories'][category]['count'] += 1

            # Count subcategories
            subcategory = opp.get('category', {}).get('subcategory', 'general')
            if subcategory not in summary['categories'][category]['subcategories']:
                summary['categories'][category]['subcategories'][subcategory] = 0
            summary['categories'][category]['subcategories'][subcategory] += 1

            # Quality distribution
            quality_score = opp.get('quality', {}).get('overall_score', 0.5)
            if quality_score >= 0.7:
                summary['quality_distribution']['high'] += 1
            elif quality_score >= 0.4:
                summary['quality_distribution']['medium'] += 1
            else:
                summary['quality_distribution']['low'] += 1

        return summary


# Singleton instance
_categorizer_instance = None

def get_opportunity_categorizer() -> OpportunityCategorizationSystem:
    """Get or create opportunity categorizer singleton"""
    global _categorizer_instance
    if _categorizer_instance is None:
        _categorizer_instance = OpportunityCategorizationSystem()
    return _categorizer_instance