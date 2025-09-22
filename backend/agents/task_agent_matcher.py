"""
Task-Agent Matching System
==========================

Intelligent system that matches freelance job requirements to the most suitable
agents from the 152 available agents, considering skills, complexity, and experience.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import difflib

logger = logging.getLogger(__name__)


@dataclass
class AgentSkillProfile:
    """Profile of an agent's capabilities"""
    agent_name: str
    primary_skills: List[str]
    secondary_skills: List[str]
    complexity_rating: int  # 1-10, higher = more complex tasks
    experience_level: str  # 'junior', 'mid', 'senior', 'expert'
    specializations: List[str]
    avg_completion_time: float  # hours per task
    success_rate: float  # 0-1
    preferred_task_types: List[str]


@dataclass
class TaskRequirements:
    """Requirements extracted from a freelance job"""
    job_id: str
    title: str
    description: str
    skills_required: List[str]
    complexity_estimate: int  # 1-10
    budget: float
    deadline_days: int
    task_type: str  # 'content', 'development', 'design', 'analysis', etc.
    estimated_hours: float


@dataclass
class AgentMatch:
    """A matched agent for a task"""
    agent_name: str
    match_score: float  # 0-1
    skill_match_score: float
    complexity_match_score: float
    availability_score: float
    reasons: List[str]
    estimated_completion_time: float
    confidence_level: str


class TaskAgentMatcher:
    """
    Matches freelance tasks to the most suitable agents from the 152 available agents.
    """

    def __init__(self):
        """Initialize the Task-Agent Matcher"""
        self.agent_profiles = self._initialize_agent_profiles()
        self.task_type_keywords = self._initialize_task_type_keywords()
        self.skill_synonyms = self._initialize_skill_synonyms()

        logger.info(f"🧠 TaskAgentMatcher initialized with {len(self.agent_profiles)} agent profiles")

    def _initialize_agent_profiles(self) -> Dict[str, AgentSkillProfile]:
        """Initialize profiles for all 152 agents"""
        profiles = {}

        # Content Creation Agents
        profiles['real_content_creator'] = AgentSkillProfile(
            agent_name='real_content_creator',
            primary_skills=['content writing', 'copywriting', 'blog writing', 'SEO writing'],
            secondary_skills=['research', 'editing', 'proofreading', 'marketing'],
            complexity_rating=7,
            experience_level='senior',
            specializations=['blog posts', 'articles', 'marketing copy', 'web content'],
            avg_completion_time=2.5,
            success_rate=0.95,
            preferred_task_types=['content', 'writing', 'marketing']
        )

        profiles['seo_optimizer_agent'] = AgentSkillProfile(
            agent_name='seo_optimizer_agent',
            primary_skills=['SEO', 'keyword research', 'content optimization', 'technical SEO'],
            secondary_skills=['analytics', 'content writing', 'link building'],
            complexity_rating=8,
            experience_level='expert',
            specializations=['on-page SEO', 'keyword strategy', 'content optimization'],
            avg_completion_time=3.0,
            success_rate=0.92,
            preferred_task_types=['seo', 'optimization', 'analysis']
        )

        # Development Agents
        profiles['code_generator_agent'] = AgentSkillProfile(
            agent_name='code_generator_agent',
            primary_skills=['Python', 'JavaScript', 'Node.js', 'React', 'Django'],
            secondary_skills=['database design', 'API development', 'testing'],
            complexity_rating=9,
            experience_level='expert',
            specializations=['full-stack development', 'API creation', 'automation'],
            avg_completion_time=8.0,
            success_rate=0.88,
            preferred_task_types=['development', 'programming', 'automation']
        )

        profiles['api_builder_agent'] = AgentSkillProfile(
            agent_name='api_builder_agent',
            primary_skills=['REST API', 'Node.js', 'Express', 'MongoDB', 'PostgreSQL'],
            secondary_skills=['authentication', 'documentation', 'testing'],
            complexity_rating=8,
            experience_level='senior',
            specializations=['API development', 'backend systems', 'database integration'],
            avg_completion_time=6.0,
            success_rate=0.90,
            preferred_task_types=['api', 'backend', 'development']
        )

        profiles['web_developer_agent'] = AgentSkillProfile(
            agent_name='web_developer_agent',
            primary_skills=['HTML', 'CSS', 'JavaScript', 'React', 'Vue.js'],
            secondary_skills=['responsive design', 'UI/UX', 'performance optimization'],
            complexity_rating=7,
            experience_level='senior',
            specializations=['frontend development', 'responsive design', 'SPA development'],
            avg_completion_time=5.0,
            success_rate=0.91,
            preferred_task_types=['frontend', 'web development', 'ui']
        )

        # Design Agents
        profiles['ui_designer_agent'] = AgentSkillProfile(
            agent_name='ui_designer_agent',
            primary_skills=['UI design', 'UX design', 'Figma', 'Adobe XD', 'Sketch'],
            secondary_skills=['prototyping', 'user research', 'wireframing'],
            complexity_rating=7,
            experience_level='senior',
            specializations=['interface design', 'user experience', 'mobile design'],
            avg_completion_time=4.0,
            success_rate=0.89,
            preferred_task_types=['design', 'ui', 'ux', 'prototype']
        )

        profiles['graphic_designer_agent'] = AgentSkillProfile(
            agent_name='graphic_designer_agent',
            primary_skills=['graphic design', 'Adobe Photoshop', 'Illustrator', 'branding'],
            secondary_skills=['typography', 'layout design', 'print design'],
            complexity_rating=6,
            experience_level='mid',
            specializations=['logo design', 'marketing materials', 'brand identity'],
            avg_completion_time=3.5,
            success_rate=0.87,
            preferred_task_types=['design', 'graphics', 'branding', 'logo']
        )

        # Analysis & Research Agents
        profiles['data_analyst_agent'] = AgentSkillProfile(
            agent_name='data_analyst_agent',
            primary_skills=['data analysis', 'Python', 'SQL', 'Excel', 'Tableau'],
            secondary_skills=['statistics', 'visualization', 'reporting'],
            complexity_rating=8,
            experience_level='senior',
            specializations=['business intelligence', 'data visualization', 'statistical analysis'],
            avg_completion_time=6.0,
            success_rate=0.93,
            preferred_task_types=['analysis', 'data', 'research', 'reporting']
        )

        profiles['market_researcher_agent'] = AgentSkillProfile(
            agent_name='market_researcher_agent',
            primary_skills=['market research', 'competitive analysis', 'survey design'],
            secondary_skills=['data collection', 'report writing', 'presentation'],
            complexity_rating=7,
            experience_level='senior',
            specializations=['market analysis', 'competitor research', 'industry reports'],
            avg_completion_time=8.0,
            success_rate=0.90,
            preferred_task_types=['research', 'analysis', 'market study']
        )

        # Business & Strategy Agents
        profiles['business_strategist_agent'] = AgentSkillProfile(
            agent_name='business_strategist_agent',
            primary_skills=['business strategy', 'planning', 'consulting', 'analysis'],
            secondary_skills=['financial modeling', 'market analysis', 'presentation'],
            complexity_rating=9,
            experience_level='expert',
            specializations=['strategic planning', 'business development', 'growth strategy'],
            avg_completion_time=10.0,
            success_rate=0.91,
            preferred_task_types=['strategy', 'consulting', 'planning', 'business']
        )

        profiles['project_manager_agent'] = AgentSkillProfile(
            agent_name='project_manager_agent',
            primary_skills=['project management', 'planning', 'coordination', 'communication'],
            secondary_skills=['risk management', 'budgeting', 'team management'],
            complexity_rating=8,
            experience_level='senior',
            specializations=['agile management', 'resource planning', 'stakeholder communication'],
            avg_completion_time=5.0,
            success_rate=0.94,
            preferred_task_types=['management', 'coordination', 'planning']
        )

        # Marketing & Social Media Agents
        profiles['social_media_agent'] = AgentSkillProfile(
            agent_name='social_media_agent',
            primary_skills=['social media marketing', 'content creation', 'community management'],
            secondary_skills=['analytics', 'advertising', 'influencer outreach'],
            complexity_rating=6,
            experience_level='mid',
            specializations=['Instagram', 'LinkedIn', 'Twitter', 'Facebook marketing'],
            avg_completion_time=3.0,
            success_rate=0.86,
            preferred_task_types=['social media', 'marketing', 'content']
        )

        profiles['digital_marketer_agent'] = AgentSkillProfile(
            agent_name='digital_marketer_agent',
            primary_skills=['digital marketing', 'PPC', 'email marketing', 'conversion optimization'],
            secondary_skills=['analytics', 'A/B testing', 'lead generation'],
            complexity_rating=7,
            experience_level='senior',
            specializations=['Google Ads', 'Facebook Ads', 'email campaigns', 'landing pages'],
            avg_completion_time=4.0,
            success_rate=0.88,
            preferred_task_types=['marketing', 'advertising', 'campaigns']
        )

        # Technical Writing & Documentation
        profiles['technical_writer_agent'] = AgentSkillProfile(
            agent_name='technical_writer_agent',
            primary_skills=['technical writing', 'documentation', 'API documentation'],
            secondary_skills=['software knowledge', 'editing', 'user guides'],
            complexity_rating=7,
            experience_level='senior',
            specializations=['API docs', 'user manuals', 'technical guides'],
            avg_completion_time=4.0,
            success_rate=0.92,
            preferred_task_types=['documentation', 'technical writing', 'guides']
        )

        # Add more agent profiles to reach 152 total...
        # For now, we'll add some generic agents to represent the full roster

        for i in range(15, 152):
            agent_name = f"specialist_agent_{i:03d}"
            profiles[agent_name] = AgentSkillProfile(
                agent_name=agent_name,
                primary_skills=['general tasks', 'research', 'analysis'],
                secondary_skills=['communication', 'problem solving'],
                complexity_rating=5,
                experience_level='mid',
                specializations=['general purpose', 'flexible tasks'],
                avg_completion_time=4.0,
                success_rate=0.80,
                preferred_task_types=['general', 'research', 'support']
            )

        return profiles

    def _initialize_task_type_keywords(self) -> Dict[str, List[str]]:
        """Initialize keywords for different task types"""
        return {
            'content': ['writing', 'blog', 'article', 'copy', 'content', 'editorial', 'ghostwriting'],
            'development': ['code', 'programming', 'development', 'software', 'app', 'website', 'system'],
            'design': ['design', 'ui', 'ux', 'graphic', 'logo', 'branding', 'visual', 'mockup'],
            'marketing': ['marketing', 'promotion', 'advertising', 'campaign', 'social media', 'seo'],
            'analysis': ['analysis', 'research', 'data', 'report', 'study', 'investigation', 'audit'],
            'translation': ['translation', 'translate', 'language', 'localization', 'multilingual'],
            'video': ['video', 'animation', 'editing', 'motion graphics', 'youtube', 'multimedia'],
            'audio': ['audio', 'podcast', 'voice', 'music', 'sound', 'recording', 'editing']
        }

    def _initialize_skill_synonyms(self) -> Dict[str, List[str]]:
        """Initialize skill synonyms for better matching"""
        return {
            'javascript': ['js', 'ecmascript', 'node.js', 'nodejs'],
            'python': ['py', 'django', 'flask', 'fastapi'],
            'css': ['styling', 'sass', 'scss', 'less', 'stylesheets'],
            'react': ['reactjs', 'react.js', 'jsx'],
            'vue': ['vuejs', 'vue.js'],
            'angular': ['angularjs', 'angular.js'],
            'seo': ['search engine optimization', 'organic search', 'search optimization'],
            'ui/ux': ['user interface', 'user experience', 'interface design', 'experience design'],
            'api': ['rest api', 'restful', 'web service', 'microservice'],
            'database': ['db', 'sql', 'mysql', 'postgresql', 'mongodb', 'nosql'],
            'marketing': ['digital marketing', 'online marketing', 'internet marketing'],
            'content writing': ['copywriting', 'blog writing', 'article writing', 'content creation']
        }

    def extract_task_requirements(self, opportunity: Dict[str, Any]) -> TaskRequirements:
        """Extract structured requirements from a freelance opportunity"""
        try:
            title = opportunity.get('title', '')
            description = opportunity.get('description', '')
            skills_required = opportunity.get('skills_required', [])
            budget = float(opportunity.get('budget', 0))

            # Estimate complexity based on budget, skills, and description
            complexity = self._estimate_complexity(title, description, skills_required, budget)

            # Determine task type
            task_type = self._determine_task_type(title, description, skills_required)

            # Estimate deadline
            deadline_days = self._estimate_deadline(opportunity.get('deadline', ''), complexity)

            # Estimate hours
            estimated_hours = self._estimate_hours(complexity, budget, task_type)

            return TaskRequirements(
                job_id=opportunity.get('job_id', 'unknown'),
                title=title,
                description=description,
                skills_required=skills_required,
                complexity_estimate=complexity,
                budget=budget,
                deadline_days=deadline_days,
                task_type=task_type,
                estimated_hours=estimated_hours
            )

        except Exception as e:
            logger.error(f"Error extracting task requirements: {e}")
            # Return minimal requirements
            return TaskRequirements(
                job_id=opportunity.get('job_id', 'unknown'),
                title=opportunity.get('title', 'Unknown Task'),
                description=opportunity.get('description', ''),
                skills_required=opportunity.get('skills_required', []),
                complexity_estimate=5,
                budget=float(opportunity.get('budget', 0)),
                deadline_days=7,
                task_type='general',
                estimated_hours=8.0
            )

    def _estimate_complexity(self, title: str, description: str, skills: List[str], budget: float) -> int:
        """Estimate task complexity (1-10)"""
        complexity = 5  # Base complexity

        combined_text = f"{title} {description}".lower()

        # Budget indicators
        if budget > 2000:
            complexity += 2
        elif budget > 1000:
            complexity += 1
        elif budget < 200:
            complexity -= 1

        # Skill count indicators
        if len(skills) > 5:
            complexity += 1
        elif len(skills) > 3:
            complexity += 0.5

        # Complexity keywords
        high_complexity_words = [
            'complex', 'advanced', 'enterprise', 'scalable', 'architecture',
            'integration', 'machine learning', 'ai', 'algorithms', 'optimization'
        ]

        low_complexity_words = [
            'simple', 'basic', 'beginner', 'easy', 'straightforward', 'quick'
        ]

        for word in high_complexity_words:
            if word in combined_text:
                complexity += 0.5

        for word in low_complexity_words:
            if word in combined_text:
                complexity -= 0.5

        return max(1, min(10, int(complexity)))

    def _determine_task_type(self, title: str, description: str, skills: List[str]) -> str:
        """Determine the primary task type"""
        combined_text = f"{title} {description} {' '.join(skills)}".lower()

        type_scores = {}

        for task_type, keywords in self.task_type_keywords.items():
            score = 0
            for keyword in keywords:
                score += combined_text.count(keyword)
            type_scores[task_type] = score

        # Return the type with highest score, or 'general' if no clear winner
        if type_scores and max(type_scores.values()) > 0:
            return max(type_scores, key=type_scores.get)

        return 'general'

    def _estimate_deadline(self, deadline_str: str, complexity: int) -> int:
        """Estimate deadline in days"""
        if deadline_str:
            try:
                # Try to parse deadline - simplified for now
                return 7  # Default to 7 days
            except:
                pass

        # Estimate based on complexity
        base_days = {
            1: 1, 2: 2, 3: 3, 4: 5, 5: 7,
            6: 10, 7: 14, 8: 21, 9: 30, 10: 45
        }

        return base_days.get(complexity, 7)

    def _estimate_hours(self, complexity: int, budget: float, task_type: str) -> float:
        """Estimate required hours"""
        base_hours = complexity * 2  # Base: 2 hours per complexity point

        # Adjust by task type
        type_multipliers = {
            'development': 1.5,
            'design': 1.2,
            'analysis': 1.3,
            'content': 0.8,
            'marketing': 1.0,
            'general': 1.0
        }

        multiplier = type_multipliers.get(task_type, 1.0)
        estimated_hours = base_hours * multiplier

        # Consider budget constraints
        if budget > 0:
            # Assume $50/hour average rate
            max_hours_by_budget = budget / 50
            estimated_hours = min(estimated_hours, max_hours_by_budget)

        return max(1.0, estimated_hours)

    def find_best_agents(self, task_requirements: TaskRequirements, top_n: int = 3) -> List[AgentMatch]:
        """Find the best agents for a given task"""
        try:
            logger.info(f"🔍 Finding best agents for task: {task_requirements.title}")

            agent_matches = []

            for agent_name, profile in self.agent_profiles.items():
                match = self._calculate_agent_match(task_requirements, profile)
                if match.match_score > 0.1:  # Only include agents with reasonable match
                    agent_matches.append(match)

            # Sort by match score and return top N
            agent_matches.sort(key=lambda x: x.match_score, reverse=True)

            top_matches = agent_matches[:top_n]

            logger.info(f"✅ Found {len(top_matches)} suitable agents")
            for match in top_matches:
                logger.info(f"   {match.agent_name}: {match.match_score:.2f} score")

            return top_matches

        except Exception as e:
            logger.error(f"Error finding best agents: {e}")
            return []

    def _calculate_agent_match(self, task: TaskRequirements, profile: AgentSkillProfile) -> AgentMatch:
        """Calculate how well an agent matches a task"""

        # 1. Skill Match Score (40% weight)
        skill_score = self._calculate_skill_match(task.skills_required, profile)

        # 2. Complexity Match Score (25% weight)
        complexity_score = self._calculate_complexity_match(task.complexity_estimate, profile)

        # 3. Task Type Match Score (20% weight)
        task_type_score = self._calculate_task_type_match(task.task_type, profile)

        # 4. Availability/Efficiency Score (15% weight)
        availability_score = self._calculate_availability_score(task.estimated_hours, profile)

        # Calculate weighted total score
        match_score = (
            skill_score * 0.40 +
            complexity_score * 0.25 +
            task_type_score * 0.20 +
            availability_score * 0.15
        )

        # Generate reasons for the match
        reasons = self._generate_match_reasons(task, profile, skill_score, complexity_score)

        # Determine confidence level
        confidence_level = self._determine_confidence_level(match_score)

        # Estimate completion time
        estimated_time = self._estimate_agent_completion_time(task, profile)

        return AgentMatch(
            agent_name=profile.agent_name,
            match_score=match_score,
            skill_match_score=skill_score,
            complexity_match_score=complexity_score,
            availability_score=availability_score,
            reasons=reasons,
            estimated_completion_time=estimated_time,
            confidence_level=confidence_level
        )

    def _calculate_skill_match(self, required_skills: List[str], profile: AgentSkillProfile) -> float:
        """Calculate skill match score"""
        if not required_skills:
            return 0.5  # Neutral score if no specific skills required

        total_score = 0
        skill_count = len(required_skills)

        for required_skill in required_skills:
            required_skill_lower = required_skill.lower()
            best_match_score = 0

            # Check primary skills (full weight)
            for primary_skill in profile.primary_skills:
                similarity = self._calculate_skill_similarity(required_skill_lower, primary_skill.lower())
                best_match_score = max(best_match_score, similarity * 1.0)

            # Check secondary skills (half weight)
            for secondary_skill in profile.secondary_skills:
                similarity = self._calculate_skill_similarity(required_skill_lower, secondary_skill.lower())
                best_match_score = max(best_match_score, similarity * 0.5)

            total_score += best_match_score

        return min(1.0, total_score / skill_count)

    def _calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills"""
        # Exact match
        if skill1 == skill2:
            return 1.0

        # Check synonyms
        for main_skill, synonyms in self.skill_synonyms.items():
            if skill1 in synonyms and skill2 in synonyms:
                return 0.9
            if (skill1 == main_skill and skill2 in synonyms) or (skill2 == main_skill and skill1 in synonyms):
                return 0.9

        # Substring match
        if skill1 in skill2 or skill2 in skill1:
            return 0.7

        # Use difflib for fuzzy matching
        similarity = difflib.SequenceMatcher(None, skill1, skill2).ratio()
        return similarity if similarity > 0.6 else 0

    def _calculate_complexity_match(self, task_complexity: int, profile: AgentSkillProfile) -> float:
        """Calculate how well agent's complexity rating matches task complexity"""
        complexity_diff = abs(task_complexity - profile.complexity_rating)

        if complexity_diff == 0:
            return 1.0
        elif complexity_diff == 1:
            return 0.8
        elif complexity_diff == 2:
            return 0.6
        elif complexity_diff == 3:
            return 0.4
        else:
            return 0.2

    def _calculate_task_type_match(self, task_type: str, profile: AgentSkillProfile) -> float:
        """Calculate task type match score"""
        if task_type in profile.preferred_task_types:
            return 1.0

        # Check if task type appears in specializations
        for specialization in profile.specializations:
            if task_type.lower() in specialization.lower():
                return 0.8

        return 0.3  # Default score for general compatibility

    def _calculate_availability_score(self, required_hours: float, profile: AgentSkillProfile) -> float:
        """Calculate availability/efficiency score"""
        # Favor agents with completion times close to required hours
        time_ratio = required_hours / profile.avg_completion_time

        if 0.8 <= time_ratio <= 1.2:  # Sweet spot
            return 1.0
        elif 0.5 <= time_ratio <= 2.0:  # Reasonable range
            return 0.8
        else:
            return 0.5

    def _generate_match_reasons(self, task: TaskRequirements, profile: AgentSkillProfile,
                              skill_score: float, complexity_score: float) -> List[str]:
        """Generate human-readable reasons for the match"""
        reasons = []

        if skill_score > 0.8:
            reasons.append(f"Excellent skill match ({skill_score:.1%})")
        elif skill_score > 0.6:
            reasons.append(f"Good skill alignment ({skill_score:.1%})")

        if complexity_score > 0.8:
            reasons.append("Perfect complexity level match")
        elif complexity_score > 0.6:
            reasons.append("Good complexity level fit")

        if profile.success_rate > 0.9:
            reasons.append(f"High success rate ({profile.success_rate:.1%})")

        if profile.experience_level in ['senior', 'expert']:
            reasons.append(f"{profile.experience_level.title()} level experience")

        # Check for specific skill matches
        for required_skill in task.skills_required:
            for primary_skill in profile.primary_skills:
                if required_skill.lower() in primary_skill.lower():
                    reasons.append(f"Specializes in {primary_skill}")
                    break

        return reasons[:3]  # Limit to top 3 reasons

    def _determine_confidence_level(self, match_score: float) -> str:
        """Determine confidence level based on match score"""
        if match_score >= 0.8:
            return "high"
        elif match_score >= 0.6:
            return "medium"
        else:
            return "low"

    def _estimate_agent_completion_time(self, task: TaskRequirements, profile: AgentSkillProfile) -> float:
        """Estimate how long this agent would take to complete the task"""
        base_time = task.estimated_hours

        # Adjust based on agent's average completion time and skill match
        agent_efficiency = profile.avg_completion_time / 5.0  # Normalize around 5 hours

        # Agents with better skill matches work faster
        skill_match = self._calculate_skill_match(task.skills_required, profile)
        efficiency_bonus = 1 - (skill_match * 0.2)  # Up to 20% faster for perfect skill match

        estimated_time = base_time * agent_efficiency * efficiency_bonus

        return max(1.0, estimated_time)

    def get_agent_recommendations(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent recommendations for a freelance opportunity"""
        try:
            # Extract task requirements
            task_requirements = self.extract_task_requirements(opportunity)

            # Find best agents
            best_agents = self.find_best_agents(task_requirements, top_n=5)

            # Prepare recommendation response
            recommendations = {
                'task_analysis': {
                    'complexity': task_requirements.complexity_estimate,
                    'task_type': task_requirements.task_type,
                    'estimated_hours': task_requirements.estimated_hours,
                    'skills_required': task_requirements.skills_required
                },
                'recommended_agents': [],
                'primary_agent': None,
                'backup_agents': [],
                'execution_plan': None
            }

            if best_agents:
                # Primary agent (best match)
                primary = best_agents[0]
                recommendations['primary_agent'] = {
                    'agent_name': primary.agent_name,
                    'match_score': primary.match_score,
                    'confidence_level': primary.confidence_level,
                    'estimated_completion_time': primary.estimated_completion_time,
                    'reasons': primary.reasons
                }

                # Backup agents
                recommendations['backup_agents'] = [
                    {
                        'agent_name': agent.agent_name,
                        'match_score': agent.match_score,
                        'confidence_level': agent.confidence_level,
                        'reasons': agent.reasons[:2]  # Fewer reasons for backup
                    }
                    for agent in best_agents[1:4]
                ]

                # All recommendations
                recommendations['recommended_agents'] = [
                    {
                        'agent_name': agent.agent_name,
                        'match_score': agent.match_score,
                        'confidence_level': agent.confidence_level,
                        'estimated_hours': agent.estimated_completion_time,
                        'skill_match': agent.skill_match_score,
                        'reasons': agent.reasons
                    }
                    for agent in best_agents
                ]

                # Create execution plan
                recommendations['execution_plan'] = self._create_execution_plan(
                    task_requirements, primary
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error getting agent recommendations: {e}")
            return {
                'error': str(e),
                'recommended_agents': [],
                'primary_agent': None
            }

    def _create_execution_plan(self, task: TaskRequirements, primary_agent: AgentMatch) -> Dict[str, Any]:
        """Create an execution plan for the task"""
        return {
            'phases': [
                {
                    'phase': 'preparation',
                    'duration_hours': 0.5,
                    'description': 'Analyze requirements and setup workspace'
                },
                {
                    'phase': 'execution',
                    'duration_hours': primary_agent.estimated_completion_time * 0.8,
                    'description': 'Main task execution'
                },
                {
                    'phase': 'review_delivery',
                    'duration_hours': primary_agent.estimated_completion_time * 0.2,
                    'description': 'Quality review and delivery preparation'
                }
            ],
            'total_estimated_hours': primary_agent.estimated_completion_time,
            'milestones': [
                'Requirements analysis complete',
                'First draft/prototype ready',
                'Final deliverable completed',
                'Quality check passed'
            ],
            'success_probability': primary_agent.match_score
        }


# Global matcher instance
_task_agent_matcher = None

def get_task_agent_matcher() -> TaskAgentMatcher:
    """Get the global task-agent matcher instance"""
    global _task_agent_matcher
    if _task_agent_matcher is None:
        _task_agent_matcher = TaskAgentMatcher()
    return _task_agent_matcher