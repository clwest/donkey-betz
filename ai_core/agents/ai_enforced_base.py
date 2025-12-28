"""
AI Enforced Base Agent - Base class that FORCES all agents to use real AI
"""

import os
import sys
import logging
from typing import Dict, Any, List
from abc import ABC, abstractmethod

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.llm_enforcer import get_llm_enforcer
from core.agent_context_middleware import UserContextualAgent
from core.models import EnhancedUserProfile, UserMemoryContext
from core.unified_memory_manager import get_memory_manager

logger = logging.getLogger(__name__)


class AIEnforcedAgent(UserContextualAgent, ABC):
    """
    Base class for all agents that MUST use real AI and user context.

    Any agent that generates text MUST inherit from this class
    to ensure it uses real LLM APIs, not fake responses, and has
    access to personalized user context.
    """

    def __init__(self, agent_name: str = None, user=None):
        """Initialize the AI-enforced agent with user context and enhanced profile"""
        # Initialize user context first
        UserContextualAgent.__init__(self, user=user)

        self.agent_name = agent_name or self.__class__.__name__
        self.enforcer = get_llm_enforcer()
        self.ai_calls_made = 0
        self.ai_tokens_used = 0
        self.ai_cost = 0.0
        self.enhanced_profile = None

        # Initialize UnifiedMemoryManager for this agent
        self.memory_manager = get_memory_manager(user) if user else None

        # Load Enhanced Profile if user is provided
        if user:
            try:
                self.enhanced_profile = EnhancedUserProfile.objects.get(user=user)
                logger.info(f"📊 Loaded Enhanced Profile for {user.username} (completeness: {self.enhanced_profile.calculate_completeness()}%)")
            except EnhancedUserProfile.DoesNotExist:
                # Create enhanced profile if it doesn't exist
                self.enhanced_profile = EnhancedUserProfile.objects.create(user=user)
                logger.info(f"📊 Created new Enhanced Profile for {user.username}")
            except Exception as e:
                logger.warning(f"Could not load Enhanced Profile: {e}")

        logger.info(f"🔒 Initialized AI-Enforced Agent: {self.agent_name}")
        if user:
            logger.info(f"👤 Agent has user context for: {user.username}")

    def generate_ai_text(self,
                         prompt: str,
                         context: str = "",
                         task_type: str = "general",
                         max_tokens: int = 500,
                         temperature: float = 0.7,
                         use_claude: bool = False,
                         personalize: bool = True) -> str:
        """
        ENFORCED method to generate text using real AI with user personalization.

        This is the ONLY way agents should generate text.

        Args:
            prompt: The prompt for the AI
            context: Additional context
            task_type: Type of task (cover_letter, content, analysis, etc.)
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0-1)
            use_claude: Use Claude instead of GPT
            personalize: Whether to add user context to the prompt

        Returns:
            The generated text from real AI

        Raises:
            Exception if no LLM is available
        """
        # Personalize the prompt if requested and user context is available
        if personalize and (self.user_context or self.enhanced_profile):
            prompt = self.get_enhanced_personalized_prompt(prompt)
            logger.info(f"🎯 Personalized prompt for {self.user_context.get('username', 'Unknown User') if self.user_context else 'User'}")

        result = self.enforcer.enforce_real_ai(
            prompt=prompt,
            context=context,
            agent_name=self.agent_name,
            task_type=task_type,
            max_tokens=max_tokens,
            temperature=temperature,
            use_claude=use_claude
        )

        if result['success']:
            # Track usage
            self.ai_calls_made += 1
            self.ai_tokens_used += result.get('tokens', 0)
            self.ai_cost += result.get('cost', 0)

            logger.info(f"✅ {self.agent_name} generated {result.get('tokens', 0)} tokens via {result['provider']}/{result['model']}")
            return result['response']
        else:
            error_msg = f"Failed to generate AI text: {result.get('error', 'Unknown error')}"
            logger.error(f"❌ {self.agent_name}: {error_msg}")
            raise Exception(error_msg)

    def store_agent_memory(self, memory_type: str, content: str, importance: int = 5, **metadata) -> Any:
        """
        Store agent memory using UnifiedMemoryManager.

        Args:
            memory_type: Type of memory (agent_action, agent_learning, etc.)
            content: Memory content
            importance: Importance level 1-10
            **metadata: Additional metadata

        Returns:
            Created memory instance
        """
        if not self.memory_manager or not self.user:
            logger.warning(f"⚠️ {self.agent_name}: Cannot store memory without user context")
            return None

        return self.memory_manager.store_memory(
            user=self.user,
            source=f"agent:{self.agent_name}",
            memory_type=memory_type,
            content=content,
            importance=importance,
            **metadata
        )

    def get_assistant_context(self) -> Dict[str, Any]:
        """
        Get Personal Assistant context for this agent.

        Returns:
            Dictionary with assistant insights
        """
        if not self.memory_manager or not self.user:
            logger.warning(f"⚠️ {self.agent_name}: Cannot get assistant context without user")
            return {}

        return self.memory_manager.get_assistant_context_for_agents(self.user)

    def get_other_agent_activities(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get activities from other agents for coordination.

        Args:
            limit: Maximum results

        Returns:
            List of agent activities
        """
        if not self.memory_manager or not self.user:
            return []

        # Get all agent activities
        activities = self.memory_manager.get_agent_activities(self.user, limit=limit * 2)

        # Filter out this agent's own activities
        return [a for a in activities if self.agent_name not in a.get('source', '')][:limit]

    def share_with_agents(self, content: str, target_agents: List[str], importance: int = 7):
        """
        Share memory with specific agents.

        Args:
            content: Content to share
            target_agents: List of agent names to share with
            importance: Importance level
        """
        if not self.memory_manager or not self.user:
            logger.warning(f"⚠️ {self.agent_name}: Cannot share without user context")
            return

        # Create the memory first
        memory = self.store_agent_memory(
            'agent_learning',
            content,
            importance=importance
        )

        if memory:
            # Share with other agents
            self.memory_manager.share_memory_between_agents(
                memory=memory,
                from_agent=self.agent_name,
                to_agents=target_agents
            )
            logger.info(f"📤 {self.agent_name} shared memory with {', '.join(target_agents)}")

    def get_ai_usage_stats(self) -> Dict[str, Any]:
        """Get AI usage statistics for this agent"""
        return {
            'agent_name': self.agent_name,
            'calls_made': self.ai_calls_made,
            'tokens_used': self.ai_tokens_used,
            'total_cost': f"${self.ai_cost:.4f}"
        }

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Abstract method that each agent must implement.

        This is where the agent's main logic goes.
        MUST use generate_ai_text() for any text generation!
        """

    def verify_ai_usage(self) -> bool:
        """Verify that this agent has actually used AI"""
        if self.ai_calls_made == 0:
            logger.warning(f"⚠️ {self.agent_name} has not made any AI calls!")
            return False

        logger.info(f"✅ {self.agent_name} has made {self.ai_calls_made} real AI calls")
        return True

    def get_enhanced_personalized_prompt(self, base_prompt: str) -> str:
        """
        Enhance prompt with both user context and Enhanced Profile data.

        Combines traditional user context with rich profile information
        for maximum personalization.
        """
        # Start with base context from parent class
        try:
            prompt = super().get_personalized_prompt(base_prompt)
        except (AttributeError, TypeError):
            prompt = base_prompt

        # Add Enhanced Profile data if available
        if self.enhanced_profile:
            profile_context = []

            # Add primary role and goals
            if self.enhanced_profile.primary_role:
                profile_context.append(f"Role: {self.enhanced_profile.primary_role}")

            if self.enhanced_profile.long_term_goals:
                goals = self.enhanced_profile.long_term_goals[:2]  # Top 2 goals
                profile_context.append(f"Goals: {'; '.join(goals)}")

            # Add skills
            if self.enhanced_profile.core_competencies:
                # Get top 5 skills sorted by proficiency level
                top_skills = sorted(self.enhanced_profile.core_competencies.items(), key=lambda x: x[1], reverse=True)[:5]
                skill_names = [skill[0] for skill in top_skills]
                profile_context.append(f"Skills: {', '.join(skill_names)}")

            # Add current projects
            if self.enhanced_profile.current_projects:
                projects = self.enhanced_profile.current_projects[:2]
                profile_context.append(f"Projects: {'; '.join(projects)}")

            # Add communication preferences
            if self.enhanced_profile.communication_style:
                profile_context.append(f"Communication Style: {self.enhanced_profile.communication_style}")

            if self.enhanced_profile.decision_framework:
                profile_context.append(f"Decision Framework: {self.enhanced_profile.decision_framework}")

            # Add work schedule
            if self.enhanced_profile.work_schedule:
                profile_context.append(f"Work Schedule: Available")

            # Build enhanced context
            if profile_context:
                enhanced_addition = f"""

Enhanced User Profile:
{chr(10).join(f'- {item}' for item in profile_context)}

Tailor your response to align with this user's specific profile, goals, and preferences.
"""
                prompt += enhanced_addition

                # Store that we used the profile
                if hasattr(self, 'user'):
                    try:
                        UserMemoryContext.objects.create(
                            user=self.user,
                            profile=self.enhanced_profile,
                            memory_type='agent_usage',
                            content=f"Agent {self.agent_name} used enhanced profile",
                            importance=3,
                            context_metadata={'agent': self.agent_name}
                        )
                    except Exception as e:
                        logger.debug(f"Could not store memory: {e}")

        return prompt


class AIEnforcedContentAgent(AIEnforcedAgent):
    """Specialized base for content-generating agents"""

    def generate_blog_post(self, topic: str, keywords: list, word_count: int = 800) -> str:
        """Generate a blog post using REAL AI"""
        context = f"Topic: {topic}\nKeywords: {', '.join(keywords)}\nTarget word count: {word_count}"

        prompt = f"""
Write a high-quality, engaging blog post about {topic}.

Requirements:
- Include these keywords naturally: {', '.join(keywords)}
- Around {word_count} words
- SEO-optimized with proper headings
- Engaging introduction and conclusion
- Informative and valuable content
- Professional tone but conversational
"""

        return self.generate_ai_text(
            prompt=prompt,
            context=context,
            task_type="content",
            max_tokens=word_count * 2,
            temperature=0.8
        )

    def generate_product_description(self, product_name: str, features: list, price: float) -> str:
        """Generate product description using REAL AI"""
        context = f"Product: {product_name}\nFeatures: {', '.join(features)}\nPrice: ${price}"

        prompt = """
Create a compelling product description that sells.

Requirements:
- Highlight key benefits
- Create emotional appeal
- Include a call to action
- Be concise but persuasive
- Focus on value, not just features
"""

        return self.generate_ai_text(
            prompt=prompt,
            context=context,
            task_type="content",
            max_tokens=300,
            temperature=0.9
        )


class AIEnforcedApplicationAgent(AIEnforcedAgent):
    """Specialized base for job application agents with user context"""

    def generate_cover_letter(self, job_info: Dict[str, Any], applicant_info: Dict[str, Any] = None) -> str:
        """Generate cover letter using REAL AI and user context"""

        # Use user context if available, otherwise fall back to provided applicant_info
        if self.user_context:
            prof = self.user_context.get('professional_profile', {})
            skills = self.user_context.get('skills', {})
            background = self.user_context.get('background', {})

            context = f"""
Job: {job_info.get('title')} at {job_info.get('company')}
Description: {job_info.get('description', '')[:500]}
Salary: {job_info.get('salary_min', 'N/A')} - {job_info.get('salary_max', 'N/A')}
Location: {job_info.get('location', 'N/A')}
Remote: {job_info.get('remote', False)}

Applicant Profile:
- Name: {prof.get('full_name')}
- Current Title: {prof.get('current_title')}
- Experience: {prof.get('years_experience', 0)} years ({prof.get('experience_level', 'entry')} level)
- Top Skills: {', '.join(skill.get('name', '') for skill in skills.get('top_skills', [])[:5])}
- Recent Work: {background.get('work_history', [{}])[0].get('company', 'Unknown') if background.get('work_history') else 'No work history'}
- Education: {background.get('education', [{}])[0].get('degree', 'Unknown') if background.get('education') else 'No education data'}
- Portfolio: {prof.get('portfolio_url', 'Not provided')}
- GitHub: {prof.get('github_username', 'Not provided')}
"""
        else:
            # Fallback to provided applicant info
            context = f"""
Job: {job_info.get('title')} at {job_info.get('company')}
Description: {job_info.get('description', '')[:500]}
Applicant: {applicant_info.get('name') if applicant_info else 'Unknown'}
Skills: {', '.join(applicant_info.get('skills', [])[:5]) if applicant_info else 'None provided'}
Experience: {applicant_info.get('years_experience', 0) if applicant_info else 0} years
"""

        prompt = """
Write a personalized, compelling cover letter for this specific job application.

Requirements:
- Address the specific role and company by name
- Highlight relevant experience and skills that match the job requirements
- Show genuine enthusiasm and cultural fit
- Professional but authentic and engaging tone
- Include specific achievements and quantifiable results when possible
- Strong opening hook and persuasive closing with call to action
- Customize for the company's industry and culture
- Demonstrate knowledge of the company's mission/values
- Keep to 3-4 paragraphs, approximately 300-400 words

Make this cover letter stand out by showing how the candidate's unique background
specifically solves the company's needs mentioned in the job description.
"""

        return self.generate_ai_text(
            prompt=prompt,
            context=context,
            task_type="cover_letter",
            max_tokens=600,
            temperature=0.8,
            personalize=True
        )

    def generate_linkedin_message(self, recruiter_name: str, company: str, job_title: str) -> str:
        """Generate LinkedIn outreach message using user context"""
        context = f"""
Recruiter: {recruiter_name}
Company: {company}
Position: {job_title}
"""

        prompt = """
Write a professional LinkedIn message to reach out about a job opportunity.

Requirements:
- Personal but professional tone
- Brief and respectful of their time
- Show genuine interest in the role and company
- Highlight 1-2 key qualifications
- Include a clear call to action
- Keep under 150 words
- Avoid being pushy or desperate
"""

        return self.generate_ai_text(
            prompt=prompt,
            context=context,
            task_type="outreach",
            max_tokens=200,
            temperature=0.7,
            personalize=True
        )

    def analyze_job_fit(self, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well a job fits the user's profile"""
        if not self.user_context:
            return {'fit_score': 0, 'analysis': 'No user context available'}

        fit_score = self.calculate_opportunity_fit(job_info)

        # Generate detailed analysis
        prompt = f"""
Analyze how well this job opportunity matches the user's profile and provide detailed feedback.

Job Details:
- Title: {job_info.get('title')}
- Company: {job_info.get('company')}
- Required Skills: {', '.join(job_info.get('required_skills', []))}
- Salary: {job_info.get('salary_min', 'N/A')} - {job_info.get('salary_max', 'N/A')}
- Location: {job_info.get('location', 'N/A')}
- Experience Required: {job_info.get('min_experience', 0)}-{job_info.get('max_experience', 999)} years

Provide analysis on:
1. Skills alignment (what matches, what's missing)
2. Experience level fit
3. Salary/compensation alignment
4. Location/remote work compatibility
5. Growth potential for this candidate
6. Specific recommendations for improving candidacy

Be honest about gaps but also highlight strengths.
"""

        analysis = self.generate_ai_text(
            prompt=prompt,
            task_type="analysis",
            max_tokens=500,
            temperature=0.6,
            personalize=True
        )

        return {
            'fit_score': round(fit_score, 1),
            'analysis': analysis,
            'recommended': fit_score >= 70,
            'skills_match': self._analyze_skills_match(job_info),
            'salary_match': self._analyze_salary_match(job_info)
        }

    def _analyze_skills_match(self, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skills match in detail"""
        if not self.user_context:
            return {'matching': [], 'missing': [], 'match_percentage': 0}

        user_skills = set(self.user_context.get('skills', {}).get('skills_list', []))
        required_skills = set(job_info.get('required_skills', []))
        preferred_skills = set(job_info.get('preferred_skills', []))

        matching_required = list(required_skills & user_skills)
        missing_required = list(required_skills - user_skills)
        matching_preferred = list(preferred_skills & user_skills)

        match_percentage = 0
        if required_skills:
            match_percentage = (len(matching_required) / len(required_skills)) * 100

        return {
            'matching_required': matching_required,
            'missing_required': missing_required,
            'matching_preferred': matching_preferred,
            'match_percentage': round(match_percentage, 1)
        }

    def _analyze_salary_match(self, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze salary compatibility"""
        if not self.user_context:
            return {'compatible': False, 'reason': 'No salary data'}

        salary_range = self.user_context.get('professional_profile', {}).get('salary_range', {})
        user_min = salary_range.get('min', 0)
        user_max = salary_range.get('max', 0)

        job_min = job_info.get('salary_min', 0)
        job_max = job_info.get('salary_max', 0)

        if not user_min and not user_max:
            return {'compatible': True, 'reason': 'No salary preferences set'}

        if not job_min and not job_max:
            return {'compatible': True, 'reason': 'Job salary not specified'}

        # Check if ranges overlap
        if job_max >= user_min and job_min <= user_max:
            return {'compatible': True, 'reason': 'Salary ranges overlap'}
        elif job_max < user_min:
            return {'compatible': False, 'reason': f'Job max (${job_max:,}) below user minimum (${user_min:,})'}
        else:
            return {'compatible': True, 'reason': 'Within acceptable range'}

    def generate_follow_up_email(self, job_title: str, company: str, days_since_applied: int) -> str:
        """Generate follow-up email using REAL AI"""
        context = f"Job: {job_title}\nCompany: {company}\nDays since application: {days_since_applied}"

        prompt = """
Write a professional follow-up email for a job application.

Requirements:
- Polite and professional
- Brief and to the point
- Express continued interest
- Add value (not just asking for status)
- Appropriate for the time frame
"""

        return self.generate_ai_text(
            prompt=prompt,
            context=context,
            task_type="general",
            max_tokens=200,
            temperature=0.7
        )


# Example of how to convert an existing agent
class ExampleConvertedAgent(AIEnforcedAgent):
    """Example of an agent converted to use enforced AI"""

    async def execute(self, task: str) -> Dict[str, Any]:
        """Execute the agent's task using REAL AI"""

        # Instead of returning hardcoded text...
        # OLD: response = "This is a fake response"

        # Use the enforced AI method:
        response = self.generate_ai_text(
            prompt=f"Complete this task: {task}",
            task_type="general"
        )

        return {
            'success': True,
            'response': response,
            'agent': self.agent_name,
            'stats': self.get_ai_usage_stats()
        }


def convert_agent_to_ai_enforced(agent_class):
    """
    Decorator to convert any agent class to use enforced AI

    Usage:
    @convert_agent_to_ai_enforced
    class MyAgent:
        def generate_text(self):
            # Will be intercepted and forced to use real AI
            return "fake text"
    """

    # Create a new class that inherits from both
    class EnforcedAgent(AIEnforcedAgent, agent_class):
        def __init__(self, *args, **kwargs):
            AIEnforcedAgent.__init__(self, agent_name=agent_class.__name__)
            agent_class.__init__(self, *args, **kwargs)

        # Override any text generation methods
        def __getattribute__(self, name):
            attr = object.__getattribute__(self, name)

            # Intercept methods that might generate text
            if callable(attr) and any(keyword in name.lower() for keyword in
                                     ['generate', 'create', 'write', 'compose']):
                def enforced_method(*args, **kwargs):
                    # Log the interception
                    logger.warning(f"🔒 Intercepted {name} - forcing real AI usage")

                    # Generate prompt from method name and args
                    prompt = f"Method {name} called with args: {args[:2] if args else 'none'}"

                    # Use real AI
                    return self.generate_ai_text(
                        prompt=prompt,
                        task_type="general"
                    )

                return enforced_method

            return attr

    return EnforcedAgent


# Audit function to check all agents
def audit_agent_ai_usage(agent_instance: AIEnforcedAgent) -> Dict[str, Any]:
    """
    Audit an agent to verify it's using real AI

    Args:
        agent_instance: Instance of an AI-enforced agent

    Returns:
        Audit report
    """
    report = {
        'agent_name': agent_instance.agent_name,
        'is_ai_enforced': isinstance(agent_instance, AIEnforcedAgent),
        'ai_calls_made': agent_instance.ai_calls_made if hasattr(agent_instance, 'ai_calls_made') else 0,
        'uses_real_ai': False,
        'recommendations': []
    }

    if report['is_ai_enforced']:
        report['uses_real_ai'] = agent_instance.verify_ai_usage()

        if not report['uses_real_ai']:
            report['recommendations'].append("Agent is AI-enforced but hasn't made any calls")
            report['recommendations'].append("Check that execute() method uses generate_ai_text()")
    else:
        report['recommendations'].append("CRITICAL: Agent does not inherit from AIEnforcedAgent")
        report['recommendations'].append("Convert agent to use AIEnforcedAgent base class")

    return report


if __name__ == "__main__":
    # Test the enforced agent
    import asyncio

    async def test_enforced_agent():
        agent = ExampleConvertedAgent("TestAgent")

        result = await agent.execute("Write a haiku about AI")

        print(f"Result: {result}")
        print(f"Stats: {agent.get_ai_usage_stats()}")
        print(f"Verified: {agent.verify_ai_usage()}")

    asyncio.run(test_enforced_agent())