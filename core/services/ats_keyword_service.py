"""
ATS Keyword Service - Session 866
=================================

Extracts and maps keywords from job descriptions for ATS optimization.

This service provides:
1. Keyword extraction from job descriptions
2. ATS-friendly keyword mapping
3. Resume-to-job matching scores
4. Keyword suggestions for resume optimization

Usage:
    from core.services.ats_keyword_service import ats_keyword_service

    # Extract keywords from a job description
    keywords = ats_keyword_service.extract_keywords(job_description)

    # Score resume against job
    score = ats_keyword_service.score_resume_match(resume_text, job_description)

    # Get optimization suggestions
    suggestions = ats_keyword_service.get_optimization_suggestions(
        resume_text, job_description, user_profile
    )
"""

import re
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import Counter
from django.utils import timezone

logger = logging.getLogger(__name__)


class ATSKeywordService:
    """
    Service for ATS keyword extraction, mapping, and resume optimization.

    Session 866: Built from HiveMind brainstorm "Persona Synthesis Engine" proposal.
    """

    # Common ATS keyword categories
    KEYWORD_CATEGORIES = {
        'technical_skills': {
            'programming': [
                'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'golang',
                'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql',
                'html', 'css', 'sass', 'less', 'graphql', 'rest', 'api', 'sdk'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'next.js', 'nuxt', 'django', 'flask', 'fastapi',
                'spring', 'node.js', 'express', 'rails', 'laravel', '.net', 'asp.net',
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy'
            ],
            'databases': [
                'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb',
                'cassandra', 'oracle', 'sql server', 'sqlite', 'neo4j', 'firebase'
            ],
            'cloud_devops': [
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
                'terraform', 'ansible', 'jenkins', 'github actions', 'gitlab ci',
                'circleci', 'travis', 'helm', 'prometheus', 'grafana', 'datadog'
            ],
            'ai_ml': [
                'machine learning', 'deep learning', 'nlp', 'natural language processing',
                'computer vision', 'neural networks', 'llm', 'gpt', 'bert', 'transformers',
                'rag', 'embeddings', 'fine-tuning', 'reinforcement learning', 'mlops'
            ]
        },
        'soft_skills': [
            'leadership', 'communication', 'teamwork', 'collaboration', 'problem-solving',
            'critical thinking', 'time management', 'adaptability', 'creativity',
            'attention to detail', 'analytical', 'strategic thinking', 'mentoring',
            'project management', 'stakeholder management', 'cross-functional'
        ],
        'certifications': [
            'aws certified', 'azure certified', 'gcp certified', 'pmp', 'scrum master',
            'cissp', 'ceh', 'comptia', 'cisco', 'oracle certified', 'salesforce',
            'google analytics', 'hubspot', 'agile', 'six sigma', 'itil'
        ],
        'experience_levels': [
            'entry-level', 'junior', 'mid-level', 'senior', 'lead', 'principal',
            'staff', 'architect', 'director', 'vp', 'executive', 'c-level'
        ],
        'education': [
            'bachelor', 'master', 'phd', 'mba', 'bootcamp', 'certification',
            'computer science', 'engineering', 'mathematics', 'statistics',
            'data science', 'information technology', 'business administration'
        ],
        'action_verbs': [
            'developed', 'implemented', 'designed', 'architected', 'led', 'managed',
            'built', 'created', 'optimized', 'improved', 'reduced', 'increased',
            'launched', 'delivered', 'collaborated', 'mentored', 'automated',
            'streamlined', 'transformed', 'scaled', 'integrated', 'migrated'
        ]
    }

    # ATS-friendly keyword variations (canonical -> variations)
    KEYWORD_VARIATIONS = {
        'javascript': ['js', 'ecmascript', 'es6', 'es2015'],
        'typescript': ['ts'],
        'python': ['py', 'python3'],
        'kubernetes': ['k8s', 'kube'],
        'amazon web services': ['aws'],
        'google cloud platform': ['gcp', 'google cloud'],
        'microsoft azure': ['azure'],
        'machine learning': ['ml'],
        'artificial intelligence': ['ai'],
        'natural language processing': ['nlp'],
        'continuous integration': ['ci'],
        'continuous deployment': ['cd'],
        'ci/cd': ['cicd', 'ci-cd', 'continuous integration/continuous deployment'],
        'user experience': ['ux'],
        'user interface': ['ui'],
        'application programming interface': ['api'],
        'software development kit': ['sdk'],
        'object-oriented programming': ['oop'],
        'test-driven development': ['tdd'],
        'behavior-driven development': ['bdd'],
    }

    # Industry-specific keyword sets
    INDUSTRY_KEYWORDS = {
        'fintech': [
            'fintech', 'payments', 'banking', 'trading', 'blockchain', 'cryptocurrency',
            'compliance', 'kyc', 'aml', 'regulatory', 'risk management', 'portfolio'
        ],
        'healthcare': [
            'healthcare', 'hipaa', 'ehr', 'medical', 'clinical', 'patient', 'telehealth',
            'health tech', 'fda', 'regulatory', 'life sciences', 'pharmaceutical'
        ],
        'ecommerce': [
            'ecommerce', 'e-commerce', 'retail', 'marketplace', 'inventory', 'fulfillment',
            'shopify', 'magento', 'woocommerce', 'conversion', 'cart', 'checkout'
        ],
        'saas': [
            'saas', 'b2b', 'b2c', 'subscription', 'mrr', 'arr', 'churn', 'retention',
            'onboarding', 'customer success', 'product-led', 'self-serve'
        ],
        'ai_ml': [
            'ai', 'ml', 'deep learning', 'neural networks', 'nlp', 'computer vision',
            'data science', 'mlops', 'model training', 'inference', 'llm', 'gpt'
        ]
    }

    def __init__(self):
        self._llm_client = None
        # Build reverse variation map for normalization
        self._variation_to_canonical = {}
        for canonical, variations in self.KEYWORD_VARIATIONS.items():
            for var in variations:
                self._variation_to_canonical[var.lower()] = canonical.lower()

    @property
    def llm_client(self):
        """Lazy load LLM client for advanced extraction."""
        if self._llm_client is None:
            try:
                from core.llm_enforcer import LLMEnforcer
                self._llm_client = LLMEnforcer()
            except Exception as e:
                logger.warning(f"Could not load LLM client: {e}")
        return self._llm_client

    def extract_keywords(
        self,
        text: str,
        use_llm: bool = False,
        include_scores: bool = True
    ) -> Dict[str, Any]:
        """
        Extract ATS-relevant keywords from text (job description or resume).

        Args:
            text: The text to extract keywords from
            use_llm: Whether to use LLM for enhanced extraction
            include_scores: Whether to include relevance scores

        Returns:
            Dict with categorized keywords and metadata
        """
        if not text:
            return {'keywords': {}, 'total_count': 0}

        text_lower = text.lower()
        results = {
            'keywords': {},
            'raw_matches': [],
            'normalized': [],
            'categories': {},
            'total_count': 0,
            'extraction_method': 'rule_based'
        }

        # Extract technical skills
        tech_keywords = self._extract_technical_keywords(text_lower)
        results['categories']['technical_skills'] = tech_keywords

        # Extract soft skills
        soft_keywords = self._extract_category_keywords(
            text_lower, self.KEYWORD_CATEGORIES['soft_skills']
        )
        results['categories']['soft_skills'] = soft_keywords

        # Extract certifications
        cert_keywords = self._extract_category_keywords(
            text_lower, self.KEYWORD_CATEGORIES['certifications']
        )
        results['categories']['certifications'] = cert_keywords

        # Extract experience level indicators
        exp_keywords = self._extract_category_keywords(
            text_lower, self.KEYWORD_CATEGORIES['experience_levels']
        )
        results['categories']['experience_level'] = exp_keywords

        # Extract action verbs (important for ATS)
        action_keywords = self._extract_category_keywords(
            text_lower, self.KEYWORD_CATEGORIES['action_verbs']
        )
        results['categories']['action_verbs'] = action_keywords

        # Detect industry
        detected_industry = self._detect_industry(text_lower)
        results['detected_industry'] = detected_industry

        # Add industry-specific keywords if detected
        if detected_industry:
            industry_keywords = self._extract_category_keywords(
                text_lower, self.INDUSTRY_KEYWORDS.get(detected_industry, [])
            )
            results['categories']['industry_specific'] = industry_keywords

        # Aggregate all keywords
        all_keywords = []
        for category, keywords in results['categories'].items():
            all_keywords.extend(keywords)

        results['keywords'] = dict(Counter(all_keywords))
        results['total_count'] = len(all_keywords)

        # Normalize keywords to canonical forms
        results['normalized'] = self._normalize_keywords(list(results['keywords'].keys()))

        # Use LLM for enhanced extraction if requested
        if use_llm and self.llm_client:
            llm_keywords = self._extract_with_llm(text)
            if llm_keywords:
                results['llm_extracted'] = llm_keywords
                results['extraction_method'] = 'hybrid'
                # Merge LLM keywords
                for kw in llm_keywords:
                    if kw.lower() not in results['keywords']:
                        results['keywords'][kw.lower()] = 1
                        results['total_count'] += 1

        return results

    def _extract_technical_keywords(self, text: str) -> List[str]:
        """Extract technical skills from text."""
        found = []
        for subcategory, keywords in self.KEYWORD_CATEGORIES['technical_skills'].items():
            for keyword in keywords:
                # Use word boundary matching to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    found.append(keyword)
        return found

    def _extract_category_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Extract keywords from a specific category."""
        found = []
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                found.append(keyword)
        return found

    def _detect_industry(self, text: str) -> Optional[str]:
        """Detect the industry from job description text."""
        industry_scores = {}
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                industry_scores[industry] = score

        if industry_scores:
            return max(industry_scores, key=industry_scores.get)
        return None

    def _normalize_keywords(self, keywords: List[str]) -> List[str]:
        """Normalize keywords to canonical forms."""
        normalized = []
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in self._variation_to_canonical:
                normalized.append(self._variation_to_canonical[kw_lower])
            else:
                normalized.append(kw_lower)
        return list(set(normalized))

    def _extract_with_llm(self, text: str) -> List[str]:
        """Use LLM to extract additional keywords not caught by rules."""
        try:
            prompt = f"""Extract the key skills, technologies, and qualifications from this job description.
Return ONLY a JSON array of keywords, no explanation.

Text:
{text[:3000]}

Return format: ["keyword1", "keyword2", ...]"""

            response = self.llm_client.execute(
                prompt=prompt,
                model='gpt-5.2',
                max_tokens=500
            )

            if response and 'response' in response:
                import json
                # Try to parse as JSON array
                content = response['response'].strip()
                if content.startswith('['):
                    return json.loads(content)
        except Exception as e:
            logger.warning(f"LLM keyword extraction failed: {e}")

        return []

    def score_resume_match(
        self,
        resume_text: str,
        job_description: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Score how well a resume matches a job description.

        Args:
            resume_text: The resume text
            job_description: The job description text
            weights: Optional category weights for scoring

        Returns:
            Dict with overall score and category breakdowns
        """
        # Default weights
        if weights is None:
            weights = {
                'technical_skills': 0.40,
                'soft_skills': 0.15,
                'certifications': 0.15,
                'experience_level': 0.10,
                'action_verbs': 0.10,
                'industry_specific': 0.10
            }

        # Extract keywords from both
        job_keywords = self.extract_keywords(job_description)
        resume_keywords = self.extract_keywords(resume_text)

        # Calculate category scores
        category_scores = {}
        for category in weights.keys():
            job_cat_keywords = set(job_keywords['categories'].get(category, []))
            resume_cat_keywords = set(resume_keywords['categories'].get(category, []))

            if job_cat_keywords:
                matched = job_cat_keywords & resume_cat_keywords
                score = len(matched) / len(job_cat_keywords) * 100
            else:
                score = 100  # If job doesn't require this category, full score

            category_scores[category] = {
                'score': round(score, 1),
                'matched': list(job_cat_keywords & resume_cat_keywords),
                'missing': list(job_cat_keywords - resume_cat_keywords),
                'job_required': list(job_cat_keywords),
                'resume_has': list(resume_cat_keywords)
            }

        # Calculate weighted overall score
        overall_score = sum(
            category_scores[cat]['score'] * weight
            for cat, weight in weights.items()
            if cat in category_scores
        )

        # Get all missing keywords (prioritized)
        all_missing = []
        for cat in ['technical_skills', 'certifications', 'soft_skills']:
            if cat in category_scores:
                all_missing.extend(category_scores[cat]['missing'])

        return {
            'overall_score': round(overall_score, 1),
            'category_scores': category_scores,
            'missing_keywords': all_missing[:20],  # Top 20 missing
            'match_level': self._get_match_level(overall_score),
            'job_industry': job_keywords.get('detected_industry'),
            'resume_industry': resume_keywords.get('detected_industry'),
        }

    def _get_match_level(self, score: float) -> str:
        """Get human-readable match level from score."""
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'moderate'
        elif score >= 30:
            return 'low'
        else:
            return 'poor'

    def get_optimization_suggestions(
        self,
        resume_text: str,
        job_description: str,
        user_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get specific suggestions for optimizing a resume for a job.

        Args:
            resume_text: Current resume text
            job_description: Target job description
            user_skills: User's known skills (may not be on resume)

        Returns:
            Dict with prioritized suggestions
        """
        match_result = self.score_resume_match(resume_text, job_description)

        suggestions = {
            'priority_keywords_to_add': [],
            'keyword_placement_tips': [],
            'format_suggestions': [],
            'action_verb_suggestions': [],
            'overall_recommendations': []
        }

        # Priority keywords to add (from missing)
        missing = match_result['missing_keywords']

        # Check if user has skills that are missing from resume
        if user_skills:
            user_skills_lower = [s.lower() for s in user_skills]
            for kw in missing:
                if kw.lower() in user_skills_lower:
                    suggestions['priority_keywords_to_add'].append({
                        'keyword': kw,
                        'priority': 'high',
                        'reason': 'You have this skill but it\'s not on your resume'
                    })
                else:
                    suggestions['priority_keywords_to_add'].append({
                        'keyword': kw,
                        'priority': 'medium',
                        'reason': 'Required by job but not on your resume'
                    })
        else:
            for kw in missing[:10]:
                suggestions['priority_keywords_to_add'].append({
                    'keyword': kw,
                    'priority': 'medium',
                    'reason': 'Required by job but not on your resume'
                })

        # Keyword placement tips
        tech_missing = match_result['category_scores'].get('technical_skills', {}).get('missing', [])
        if tech_missing:
            suggestions['keyword_placement_tips'].append(
                f"Add technical skills ({', '.join(tech_missing[:5])}) to your Skills section"
            )

        soft_missing = match_result['category_scores'].get('soft_skills', {}).get('missing', [])
        if soft_missing:
            suggestions['keyword_placement_tips'].append(
                f"Demonstrate soft skills ({', '.join(soft_missing[:3])}) in your experience bullets"
            )

        # Action verb suggestions
        job_keywords = self.extract_keywords(job_description)
        job_actions = job_keywords['categories'].get('action_verbs', [])
        resume_keywords = self.extract_keywords(resume_text)
        resume_actions = resume_keywords['categories'].get('action_verbs', [])

        missing_actions = set(job_actions) - set(resume_actions)
        if missing_actions:
            suggestions['action_verb_suggestions'] = list(missing_actions)[:5]

        # Overall recommendations based on score
        score = match_result['overall_score']
        if score < 50:
            suggestions['overall_recommendations'].append(
                "Consider tailoring your resume more specifically for this role"
            )
        if match_result['job_industry'] and match_result['job_industry'] != match_result['resume_industry']:
            suggestions['overall_recommendations'].append(
                f"Add {match_result['job_industry']}-specific terminology to your resume"
            )

        suggestions['current_match_score'] = score
        suggestions['target_score'] = min(score + 20, 95)

        return suggestions

    def generate_ats_optimized_summary(
        self,
        user_profile: Dict[str, Any],
        job_description: str,
        style: str = 'professional'
    ) -> str:
        """
        Generate an ATS-optimized professional summary.

        Args:
            user_profile: User's profile data (skills, experience, etc.)
            job_description: Target job description
            style: Writing style ('professional', 'creative', 'technical')

        Returns:
            ATS-optimized summary text
        """
        job_keywords = self.extract_keywords(job_description)

        # Get top required keywords
        top_tech = job_keywords['categories'].get('technical_skills', [])[:5]
        top_soft = job_keywords['categories'].get('soft_skills', [])[:3]
        industry = job_keywords.get('detected_industry', '')

        # Build keyword-rich summary
        user_title = user_profile.get('title', 'Professional')
        years_exp = user_profile.get('years_experience', '')
        user_skills = user_profile.get('skills', [])

        # Match user skills with job requirements
        matched_skills = [s for s in user_skills if s.lower() in [t.lower() for t in top_tech]]

        if self.llm_client:
            try:
                prompt = f"""Write a 3-4 sentence professional summary for a {user_title} applying for a job.

The summary MUST include these keywords naturally: {', '.join(top_tech[:4])}
Also try to include: {', '.join(top_soft[:2])}

User background:
- Title: {user_title}
- Years of experience: {years_exp or 'Not specified'}
- Key skills: {', '.join(user_skills[:10])}
- Industry: {industry or 'Technology'}

Style: {style}
Write in first person, be specific, and include measurable achievements where possible.
Keep it under 75 words for ATS scannability."""

                response = self.llm_client.execute(
                    prompt=prompt,
                    model='gpt-5.2',
                    max_tokens=200
                )

                if response and 'response' in response:
                    return response['response'].strip()

            except Exception as e:
                logger.warning(f"LLM summary generation failed: {e}")

        # Fallback template-based summary
        skills_str = ', '.join(matched_skills[:4]) if matched_skills else ', '.join(top_tech[:4])
        exp_str = f"with {years_exp} years of experience " if years_exp else ""

        return f"{user_title} {exp_str}specializing in {skills_str}. " \
               f"Proven track record of delivering results through {top_soft[0] if top_soft else 'collaboration'} " \
               f"and technical excellence. Passionate about {industry or 'technology'} and continuous improvement."


# Singleton instance
ats_keyword_service = ATSKeywordService()


def get_ats_keyword_service() -> ATSKeywordService:
    """Get the singleton ATS keyword service instance."""
    return ats_keyword_service
