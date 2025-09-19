"""
Personal Assistant Interview System
===================================

A conversational onboarding system that builds comprehensive user profiles through
intelligent, adaptive interviews. Transforms anonymous users into fully understood
individuals with clear goals and capabilities.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class InterviewPhase(Enum):
    """Interview phases for structured conversation flow"""
    INTRODUCTION = "introduction"
    SKILLS_DISCOVERY = "skills_discovery"
    EXPERIENCE_DEEP_DIVE = "experience_deep_dive"
    GOALS_PREFERENCES = "goals_preferences"
    HIDDEN_TALENTS = "hidden_talents"
    VERIFICATION = "verification"
    COMPLETE = "complete"


class SkillCategory(Enum):
    """Skill categories for organized discovery"""
    TECHNICAL = "technical"
    CREATIVE = "creative"
    BUSINESS = "business"
    COMMUNICATION = "communication"
    ANALYTICAL = "analytical"
    LEADERSHIP = "leadership"


class CommitmentLevel(Enum):
    """User commitment levels for opportunity matching"""
    EXPLORING = "exploring"
    SERIOUS = "serious"
    VERY_SERIOUS = "very_serious"
    JUST_BROWSING = "just_browsing"


@dataclass
class InterviewState:
    """Current state of the interview process"""
    phase: InterviewPhase
    current_question_id: str
    responses: Dict[str, Any]
    profile_data: Dict[str, Any]
    insights: List[str]
    completion_percentage: float
    started_at: datetime
    last_activity: datetime
    topics_covered: List[str] = None  # Track what we've asked about

    def __post_init__(self):
        if self.topics_covered is None:
            self.topics_covered = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'phase': self.phase.value,
            'current_question_id': self.current_question_id,
            'responses': self.responses,
            'profile_data': self.profile_data,
            'insights': self.insights,
            'completion_percentage': self.completion_percentage,
            'started_at': self.started_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'topics_covered': self.topics_covered
        }


@dataclass
class Question:
    """Interview question structure"""
    id: str
    phase: InterviewPhase
    text: str
    input_type: str  # 'text', 'multiple_choice', 'multi_select', 'scale', 'yes_no'
    options: Optional[List[str]] = None
    required: bool = True
    follow_up_questions: Optional[List[str]] = None
    ai_analysis_prompt: Optional[str] = None


class PersonalAssistantInterviewer:
    """
    Conversational interview system that builds comprehensive user profiles
    through intelligent, adaptive conversations with real AI personality.
    """

    def __init__(self):
        self.questions = self._initialize_questions()
        self.skill_keywords = self._initialize_skill_keywords()
        self.active_interviews: Dict[str, InterviewState] = {}
        self.conversation_context: Dict[str, List[Dict]] = {}  # Store conversation history
        self.llm_enforcer = None  # Will be initialized when needed
        self._initialize_ai_system()

    def _initialize_ai_system(self):
        """Initialize the AI system for conversational interviews"""
        try:
            from core.llm_enforcer import LLMEnforcer
            self.llm_enforcer = LLMEnforcer()
            logger.info("✅ AI system initialized for conversational interviews")

            # Test if AI is actually working
            test_result = self.llm_enforcer.enforce_real_ai(
                prompt="Say 'Hello, I'm ready to help with interviews!'",
                context="Test prompt",
                agent_name="InterviewAssistant",
                task_type="test",
                max_tokens=20,
                temperature=0.5
            )

            if test_result.get('success'):
                logger.info(f"✅ AI system test successful: {test_result.get('response', '')[:50]}")
            else:
                logger.warning(f"⚠️ AI system test failed: {test_result.get('error', 'Unknown error')}")
                self.llm_enforcer = None

        except Exception as e:
            logger.warning(f"⚠️ Could not initialize AI system: {e}")
            self.llm_enforcer = None

    def _generate_conversational_question(self, state: InterviewState, context: Dict[str, Any]) -> str:
        """Generate a natural, conversational question based on context and previous responses"""

        # TEMPORARILY DISABLED: Force use of smart fallback questions
        # The AI is generating repetitive name questions
        return self._get_next_predefined_question(state)

        if not self.llm_enforcer:
            # Fallback to predefined questions if AI not available
            return self._get_next_predefined_question(state)

        try:
            # Build conversation context
            conversation_history = self.conversation_context.get(state.profile_data.get('user_id', 'unknown'), [])

            # Create AI prompt for natural conversation
            system_prompt = f"""You are a warm, friendly Personal AI Assistant conducting an onboarding interview.
Your personality traits:
- Empathetic and encouraging
- Professional yet conversational
- Genuinely interested in helping the user succeed
- Natural conversationalist (not robotic)

Current interview phase: {state.phase.value}
User's name: {state.profile_data.get('name') or 'Not provided yet'}
Progress: {state.completion_percentage:.0f}% complete

Previous conversation:
{self._format_conversation_history(conversation_history[-3:])}

User profile so far:
- Name: {state.profile_data.get('name') or 'Not provided yet'}
- Situation: {state.profile_data.get('current_situation', 'Not specified')}
- Available hours: {state.profile_data.get('available_hours', 'Not specified')}
- Skills mentioned: {', '.join(state.profile_data.get('skills', {}).get('all', [])) or 'None yet'}
- Goals: {state.profile_data.get('goals', {}).get('monthly_income', 'Not specified')}

Topics we've already covered: {', '.join(state.topics_covered) if state.topics_covered else 'None'}

Based on the conversation flow and what we know so far, generate the NEXT natural question to continue building their profile.
Make it conversational and personalized. Reference what they just told you. Show genuine interest.

Important:
1. NEVER ask about topics we've already covered: {', '.join(state.topics_covered) if state.topics_covered else 'None'}
2. Don't ask about things already answered (especially their name if already provided)
3. Make smooth transitions between topics
4. Use their name occasionally (only if we have it: {state.profile_data.get('name', '')})
5. Keep questions concise but warm
6. If they seem enthusiastic, match their energy
7. If they're brief, be respectful of their time

Generate only the question text, nothing else."""

            # Determine what type of information we need next
            next_info_needed = self._determine_next_info_needed(state)

            prompt = f"Generate a natural question to learn about their {next_info_needed}. Make it conversational and build on what they just said."

            # Get AI response
            result = self.llm_enforcer.enforce_real_ai(
                prompt=prompt,
                context=system_prompt,
                agent_name="InterviewAssistant",
                task_type="conversation",
                max_tokens=150,
                temperature=0.8
            )

            if result['success']:
                return result['response']
            else:
                return self._get_next_predefined_question(state)

        except Exception as e:
            logger.error(f"Error generating conversational question: {e}")
            return self._get_next_predefined_question(state)

    def _generate_ai_response_to_answer(self, user_response: str, state: InterviewState) -> str:
        """Generate a natural AI response acknowledging the user's answer"""

        if not self.llm_enforcer:
            # Simple acknowledgment if AI not available
            return self._get_simple_acknowledgment(user_response)

        try:
            system_prompt = f"""You are a warm, friendly Personal AI Assistant.
Acknowledge what the user just told you in a natural, encouraging way.
Be brief (1-2 sentences max) but genuine.
User's name: {state.profile_data.get('name', 'there')}

Their response: {user_response}

Generate a brief, natural acknowledgment that:
1. Shows you understood them
2. Is encouraging/positive
3. Smoothly transitions to the next question
4. Uses their name occasionally

Keep it conversational, not robotic. Be genuinely interested."""

            result = self.llm_enforcer.enforce_real_ai(
                prompt="Generate a brief acknowledgment",
                context=system_prompt,
                agent_name="InterviewAssistant",
                task_type="acknowledgment",
                max_tokens=50,
                temperature=0.7
            )

            if result['success']:
                return result['response']
            else:
                return self._get_simple_acknowledgment(user_response)

        except Exception as e:
            logger.error(f"Error generating AI acknowledgment: {e}")
            return self._get_simple_acknowledgment(user_response)

    def _get_simple_acknowledgment(self, response: str) -> str:
        """Smart acknowledgments based on response content (no AI required)"""
        response_lower = response.lower()

        # Check for specific keywords and respond appropriately
        if "ai" in response_lower and ("collaboration" in response_lower or "mentor" in response_lower or "co-worker" in response_lower):
            return "That's fascinating! Your perspective on AI as a collaborative partner rather than just a tool really resonates. This kind of human-AI synergy is exactly what makes projects successful."

        elif "not correct" in response_lower or "wrong" in response_lower or "no that" in response_lower:
            return "I apologize for the confusion! Let me understand better - please tell me your actual name and how you'd like to be addressed."

        elif "project" in response_lower and "working" in response_lower:
            return "That sounds like an exciting project! The fact that you see AI as a true collaborator shows deep understanding of its potential."

        elif len(response) < 10:
            # Short response - likely just a name or simple answer
            return f"Thanks, {response}! That's perfect."

        elif "experience" in response_lower or "years" in response_lower:
            return "Wow, that's impressive experience! Your background will definitely open up some great opportunities."

        elif "skill" in response_lower or "good at" in response_lower:
            return "Excellent! Those are valuable skills that are in high demand right now."

        else:
            # Default varied responses
            acknowledgments = [
                "That's really interesting! Tell me more.",
                "Thanks for sharing that! This helps me understand you better.",
                "Great insight! I can see how that shapes your perspective.",
                "Fascinating! Your experience is quite unique.",
                "Perfect! This gives me a much clearer picture of who you are."
            ]
            import random
            return random.choice(acknowledgments)

    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for AI context"""
        if not history:
            return "No previous conversation"

        formatted = []
        for entry in history:
            formatted.append(f"Assistant: {entry.get('assistant', '')}")
            formatted.append(f"User: {entry.get('user', '')}")

        return "\n".join(formatted)

    def _determine_next_info_needed(self, state: InterviewState) -> str:
        """Determine what information we need to gather next"""
        profile = state.profile_data
        name = profile.get('name', '')

        # Skip name if we have it (and it's not a mistaken extraction)
        if not name or name.lower() in ['there', 'hi', 'hello', 'hey']:
            return "name and how they'd like to be addressed"
        elif 'professional_situation' not in state.topics_covered:
            return "current professional situation"
        elif 'time_availability' not in state.topics_covered:
            return "time availability for additional work"
        elif not profile.get('available_hours'):
            return "time availability for additional work"
        elif not profile.get('skills', {}).get('technical'):
            return "technical skills and expertise"
        elif not profile.get('skills', {}).get('strongest_skill'):
            return "strongest skill with a specific example"
        elif not profile.get('experience', {}).get('background'):
            return "professional background and experience"
        elif not profile.get('goals', {}).get('monthly_income'):
            return "income goals and financial targets"
        elif not profile.get('goals', {}).get('work_preferences'):
            return "work preferences and ideal opportunities"
        elif not profile.get('hidden_talents'):
            return "unique abilities or hidden talents"
        elif not profile.get('commitment_level'):
            return "commitment level and readiness to start"
        else:
            return "any final thoughts or questions"

    def _get_next_predefined_question(self, state: InterviewState) -> str:
        """Smart conversational questions without AI (fallback)"""
        profile = state.profile_data
        name = profile.get('name', '')

        # Generate contextual questions based on what we know
        if not name or name == 'there' or name.lower() in ['hi', 'hello', 'hey']:
            return "Let's start with the basics - what's your name? How would you like me to address you?"

        # If we have a name but nothing else, move straight to important stuff
        elif name and 'professional_situation' not in state.topics_covered:
            state.topics_covered.append('professional_situation')
            return f"Great, {name}! Let's dive right in. Tell me about your current professional situation - are you working, studying, building something, or exploring new opportunities?"

        elif 'professional_situation' in state.topics_covered and 'time_availability' not in state.topics_covered:
            state.topics_covered.append('time_availability')
            return f"Thanks for sharing that, {name}! Now, how much time could you realistically dedicate to earning additional income each week?"

        elif 'time_availability' in state.topics_covered and 'skills' not in state.topics_covered:
            state.topics_covered.append('skills')
            return f"Perfect, {name}! Now I'd love to learn about your skills and expertise. What would you say you're really good at? What comes naturally to you?"

        elif not profile.get('skills', {}).get('technical') and not profile.get('skills', {}).get('strongest_skill'):
            return f"Now {name}, I'd love to learn about your skills and expertise. What would you say you're really good at? What comes naturally to you?"

        elif not profile.get('experience', {}).get('background'):
            return f"That's a great skill set, {name}! Can you tell me more about your professional background? Any specific projects or achievements you're proud of?"

        elif not profile.get('goals', {}).get('monthly_income'):
            return f"Based on what you've told me, {name}, you have some great opportunities ahead! What kind of monthly income are you hoping to generate?"

        elif not profile.get('goals', {}).get('work_preferences'):
            return f"Perfect! Now {name}, what type of work environment do you prefer? Remote, flexible hours, project-based, or something else?"

        elif not profile.get('hidden_talents'):
            return f"{name}, here's something fun - what do people often ask you for help with? Sometimes our hidden talents are things we don't even realize are special!"

        elif not profile.get('commitment_level'):
            return f"We're almost done, {name}! One last question - how serious are you about generating income in the next 30 days? Just exploring or ready to dive in?"

        else:
            return f"Thanks for sharing all of this, {name}! Is there anything else you'd like me to know about your goals or preferences?"

    def _initialize_questions(self) -> Dict[str, Question]:
        """Initialize the question bank for all interview phases"""
        questions = {}

        # INTRODUCTION PHASE
        questions['intro_welcome'] = Question(
            id='intro_welcome',
            phase=InterviewPhase.INTRODUCTION,
            text="Hi! I'm your personal AI assistant. Let's build your profile together so I can find the perfect income opportunities for you. This personalized interview takes about 10 minutes. Ready to get started?",
            input_type='yes_no',
            required=True
        )

        questions['intro_name'] = Question(
            id='intro_name',
            phase=InterviewPhase.INTRODUCTION,
            text="Wonderful! First, what should I call you? (Your first name or preferred nickname)",
            input_type='text',
            required=True
        )

        questions['intro_situation'] = Question(
            id='intro_situation',
            phase=InterviewPhase.INTRODUCTION,
            text="Thanks! Now, tell me about your current professional situation - what best describes where you're at right now?",
            input_type='multiple_choice',
            options=[
                "Employed - looking for more income",
                "Unemployed - need income ASAP",
                "Student - want part-time work",
                "Entrepreneur - scaling my business",
                "Retired - exploring opportunities",
                "Other"
            ],
            required=True
        )

        questions['intro_availability'] = Question(
            id='intro_availability',
            phase=InterviewPhase.INTRODUCTION,
            text="Perfect! How much time could you realistically dedicate to earning additional income each week?",
            input_type='multiple_choice',
            options=[
                "1-5 hours (side hustle)",
                "10-20 hours (part-time)",
                "20-40 hours (serious commitment)",
                "40+ hours (full-time)"
            ],
            required=True
        )

        # SKILLS DISCOVERY PHASE
        questions['skills_intro'] = Question(
            id='skills_intro',
            phase=InterviewPhase.SKILLS_DISCOVERY,
            text="Excellent! Now let's explore your skills and talents. I'll ask about different areas to build a complete picture of your capabilities. Ready?",
            input_type='text',
            required=False
        )

        questions['skills_technical'] = Question(
            id='skills_technical',
            phase=InterviewPhase.SKILLS_DISCOVERY,
            text="Let's start with technical skills - do any of these resonate with you? (Select all that apply)",
            input_type='multi_select',
            options=[
                "Python/Programming",
                "Web Development (HTML/CSS/JS)",
                "Data Analysis/Excel",
                "AI/Machine Learning",
                "No-code tools (Zapier, Bubble)",
                "Database/SQL",
                "Cloud platforms (AWS/Google)",
                "Mobile app development",
                "None of these"
            ]
        )

        questions['skills_creative'] = Question(
            id='skills_creative',
            phase=InterviewPhase.SKILLS_DISCOVERY,
            text="Great! Now, how about creative and content skills? Which of these do you have experience with?",
            input_type='multi_select',
            options=[
                "Writing/Content Creation",
                "Design/Graphics (Photoshop/Canva)",
                "Video/Audio Editing",
                "Music/Audio Production",
                "Photography",
                "Social Media Management",
                "Copywriting/Marketing",
                "Animation/Motion Graphics",
                "None of these"
            ]
        )

        questions['skills_business'] = Question(
            id='skills_business',
            phase=InterviewPhase.SKILLS_DISCOVERY,
            text="Wonderful! What about business and professional skills? Have you worked in any of these areas?",
            input_type='multi_select',
            options=[
                "Sales/Business Development",
                "Marketing/Advertising",
                "Project Management",
                "Customer Service/Support",
                "Finance/Accounting",
                "Operations/Logistics",
                "HR/Recruiting",
                "Consulting/Coaching",
                "None of these"
            ]
        )

        questions['skills_strongest'] = Question(
            id='skills_strongest',
            phase=InterviewPhase.SKILLS_DISCOVERY,
            text="Now I'd love to hear from you directly - what would you say is your strongest skill or talent? What comes naturally to you that others often struggle with?",
            input_type='text',
            required=True,
            ai_analysis_prompt="Extract specific skills, experience level, and confidence indicators from this response."
        )

        questions['skills_example'] = Question(
            id='skills_example',
            phase=InterviewPhase.SKILLS_DISCOVERY,
            text="Can you give me a specific example of how you've used this skill? Any achievements or projects you're proud of?",
            input_type='text',
            required=True,
            ai_analysis_prompt="Identify concrete examples, quantifiable results, and transferable skills from this response."
        )

        # EXPERIENCE DEEP DIVE PHASE
        questions['exp_background'] = Question(
            id='exp_background',
            phase=InterviewPhase.EXPERIENCE_DEEP_DIVE,
            text="What's your professional background? Tell me about your work experience or education.",
            input_type='text',
            required=True,
            ai_analysis_prompt="Extract years of experience, industries, roles, companies, and career transitions."
        )

        questions['exp_transition'] = Question(
            id='exp_transition',
            phase=InterviewPhase.EXPERIENCE_DEEP_DIVE,
            text="What motivated any major career changes or what drives you professionally?",
            input_type='text',
            ai_analysis_prompt="Identify motivations, values, and what they want to avoid in work."
        )

        questions['exp_achievements'] = Question(
            id='exp_achievements',
            phase=InterviewPhase.EXPERIENCE_DEEP_DIVE,
            text="What's your biggest professional achievement or project you've completed recently?",
            input_type='text',
            ai_analysis_prompt="Extract quantifiable achievements and demonstrated capabilities."
        )

        questions['exp_learning'] = Question(
            id='exp_learning',
            phase=InterviewPhase.EXPERIENCE_DEEP_DIVE,
            text="Have you completed any courses, certifications, or self-directed learning recently?",
            input_type='text',
            ai_analysis_prompt="Identify learning style, self-direction, and growth mindset indicators."
        )

        # GOALS & PREFERENCES PHASE
        questions['goals_income'] = Question(
            id='goals_income',
            phase=InterviewPhase.GOALS_PREFERENCES,
            text="What's your income goal for the next 30 days?",
            input_type='multiple_choice',
            options=[
                "$500 - Just testing the waters",
                "$1,000 - $2,500 - Solid side income",
                "$2,500 - $5,000 - Replace part-time job",
                "$5,000+ - Full income replacement"
            ],
            required=True
        )

        questions['goals_work_type'] = Question(
            id='goals_work_type',
            phase=InterviewPhase.GOALS_PREFERENCES,
            text="What type of work do you prefer?",
            input_type='multi_select',
            options=[
                "Project-based (clear deliverables)",
                "Ongoing clients (recurring revenue)",
                "Product sales (build once, sell many)",
                "Service delivery (hourly/consulting)",
                "Passive income (investments/automation)",
                "Remote work only",
                "Flexible schedule"
            ]
        )

        questions['goals_avoid'] = Question(
            id='goals_avoid',
            phase=InterviewPhase.GOALS_PREFERENCES,
            text="What would you absolutely NOT want to do? Any deal-breakers?",
            input_type='text',
            required=True,
            ai_analysis_prompt="Extract negative preferences and constraints for opportunity filtering."
        )

        questions['goals_preferences'] = Question(
            id='goals_preferences',
            phase=InterviewPhase.GOALS_PREFERENCES,
            text="Any other preferences? (remote only, specific industries, work schedule, etc.)",
            input_type='text',
            ai_analysis_prompt="Extract additional constraints and preferences."
        )

        # HIDDEN TALENTS PHASE
        questions['talents_hobbies'] = Question(
            id='talents_hobbies',
            phase=InterviewPhase.HIDDEN_TALENTS,
            text="What do you enjoy doing in your free time? Any hobbies or interests?",
            input_type='text',
            ai_analysis_prompt="Identify monetizable hobbies and hidden talents."
        )

        questions['talents_natural'] = Question(
            id='talents_natural',
            phase=InterviewPhase.HIDDEN_TALENTS,
            text="What do people often ask you for help with? What comes naturally to you?",
            input_type='text',
            ai_analysis_prompt="Extract natural strengths and skills others recognize."
        )

        questions['talents_passionate'] = Question(
            id='talents_passionate',
            phase=InterviewPhase.HIDDEN_TALENTS,
            text="If money wasn't a factor, what would you spend your time doing?",
            input_type='text',
            ai_analysis_prompt="Identify passion projects and intrinsic motivations."
        )

        # VERIFICATION PHASE
        questions['verify_assets'] = Question(
            id='verify_assets',
            phase=InterviewPhase.VERIFICATION,
            text="Do you have any of these ready to showcase your skills?",
            input_type='multi_select',
            options=[
                "Professional portfolio/website",
                "LinkedIn profile (updated)",
                "Resume/CV",
                "GitHub/Code samples",
                "Client testimonials",
                "Work samples/demos",
                "None yet (that's ok!)"
            ]
        )

        questions['verify_commitment'] = Question(
            id='verify_commitment',
            phase=InterviewPhase.VERIFICATION,
            text="How serious are you about generating income in the next 30 days?",
            input_type='multiple_choice',
            options=[
                "Very serious - I'll work on this daily",
                "Serious - I'll dedicate real time to this",
                "Exploring - Want to see what's possible",
                "Just browsing"
            ],
            required=True
        )

        questions['verify_auto_apply'] = Question(
            id='verify_auto_apply',
            phase=InterviewPhase.VERIFICATION,
            text="Would you like me to actively apply to opportunities on your behalf?",
            input_type='multiple_choice',
            options=[
                "Yes - Apply automatically to good matches",
                "Yes - But ask me first",
                "No - Just show me opportunities"
            ]
        )

        return questions

    @database_sync_to_async
    def _get_user_by_id(self, user_id: str):
        """Get user object from database by ID"""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.filter(id=user_id).first()
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    def _initialize_skill_keywords(self) -> Dict[str, List[str]]:
        """Initialize skill detection keywords for AI analysis"""
        return {
            'technical': [
                'python', 'javascript', 'react', 'node.js', 'sql', 'api', 'database',
                'machine learning', 'ai', 'data analysis', 'excel', 'programming',
                'web development', 'mobile app', 'cloud', 'aws', 'automation'
            ],
            'creative': [
                'design', 'photoshop', 'canva', 'video editing', 'content creation',
                'writing', 'copywriting', 'social media', 'photography', 'graphics',
                'branding', 'marketing', 'animation', 'audio'
            ],
            'business': [
                'sales', 'business development', 'project management', 'operations',
                'finance', 'accounting', 'consulting', 'strategy', 'leadership',
                'team management', 'customer service', 'recruitment'
            ],
            'communication': [
                'presentation', 'public speaking', 'negotiation', 'teaching',
                'training', 'customer support', 'relationship building'
            ]
        }

    async def start_interview(self, user_id: str, quick_start: bool = False) -> Dict[str, Any]:
        """Start a new interview for the user"""
        logger.info(f"Starting {'quick' if quick_start else 'full'} interview for user {user_id}")

        # Try to get user's name from database
        user_name = ''
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = await self._get_user_by_id(user_id)
            if user:
                # Get name from user account
                if user.first_name:
                    user_name = user.first_name
                elif hasattr(user, 'username'):
                    user_name = user.username
                logger.info(f"Found user name from account: {user_name}")
        except Exception as e:
            logger.warning(f"Could not get user name from database: {e}")

        # Initialize interview state
        state = InterviewState(
            phase=InterviewPhase.INTRODUCTION,
            current_question_id='intro_welcome',
            responses={},
            profile_data={
                'user_id': user_id,
                'name': user_name,  # Pre-populate with user's name from account!
                'interview_type': 'quick' if quick_start else 'full',
                'skills': {cat.value: [] for cat in SkillCategory},
                'experience': {},
                'goals': {},
                'preferences': {},
                'hidden_talents': [],
                'commitment_level': None,
                'ai_insights': []
            },
            insights=[],
            completion_percentage=0.0,
            started_at=datetime.now(),
            last_activity=datetime.now(),
            topics_covered=[]  # Initialize empty topics covered list
        )

        self.active_interviews[user_id] = state

        # Get first question - customize if we have their name
        first_question = self._get_next_question(state)

        # If we have the user's name, personalize the welcome
        if user_name:
            if first_question.get('id') == 'intro_welcome':
                first_question['text'] = f"Hi {user_name}! I'm your personal AI assistant. Let's build on your profile so I can find the perfect income opportunities for you. This interview takes about 10 minutes. Ready to dive in?"

        return {
            'success': True,
            'interview_started': True,
            'interview_type': 'quick' if quick_start else 'full',
            'estimated_time': '2 minutes' if quick_start else '8-10 minutes',
            'question': first_question,
            'state': state.to_dict(),
            'has_user_name': bool(user_name)  # Let frontend know we have their name
        }

    async def process_response(self, user_id: str, response: Any) -> Dict[str, Any]:
        """Process a user response and get the next question in a conversational way"""
        if user_id not in self.active_interviews:
            return {'error': 'No active interview found'}

        state = self.active_interviews[user_id]
        state.last_activity = datetime.now()

        # Store the response
        current_question = self.questions.get(state.current_question_id)
        if current_question:
            state.responses[state.current_question_id] = response

        # Store in conversation history for AI context
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = []

        self.conversation_context[user_id].append({
            'user': str(response),
            'timestamp': datetime.now().isoformat()
        })

        # Generate AI acknowledgment of their response
        acknowledgment = self._generate_ai_response_to_answer(str(response), state)

        # Process response with AI if needed
        if current_question and current_question.ai_analysis_prompt:
            insights = await self._analyze_response_with_ai(
                response,
                current_question.ai_analysis_prompt
            )
            state.insights.extend(insights)

        # Extract profile data from response
        if current_question:
            await self._extract_profile_data(state, current_question, response)
            # Track what we've covered
            if 'professional situation' in current_question.text.lower():
                state.topics_covered.append('professional_situation')
            elif 'time' in current_question.text.lower() and 'dedicate' in current_question.text.lower():
                state.topics_covered.append('time_availability')
            elif 'skills' in current_question.text.lower() or 'good at' in current_question.text.lower():
                state.topics_covered.append('skills')
            elif 'background' in current_question.text.lower() or 'experience' in current_question.text.lower():
                state.topics_covered.append('background')

        # IMPORTANT: Update the current question ID to advance the interview
        # Get next question to update state
        next_q = self._get_next_question(state)
        if next_q and 'id' in next_q:
            state.current_question_id = next_q['id']

        # Update completion percentage
        state.completion_percentage = self._calculate_completion(state)

        # Check if interview is complete
        if state.phase == InterviewPhase.COMPLETE:
            profile = await self._build_final_profile(state)
            return {
                'success': True,
                'interview_complete': True,
                'profile': profile,
                'acknowledgment': acknowledgment,
                'final_message': f"Fantastic, {state.profile_data.get('name', 'there')}! I've learned so much about you. Based on everything you've shared, I've built a comprehensive profile that will help me find the perfect opportunities for you. Your profile strength score is {profile.get('profile_strength_score', 0)}%!",
                'state': state.to_dict()
            }

        # Generate next conversational question
        next_question_text = self._generate_conversational_question(state, {'previous_response': response})

        # Store AI's question in conversation history
        self.conversation_context[user_id].append({
            'assistant': next_question_text,
            'timestamp': datetime.now().isoformat()
        })

        # Get structured question data for frontend
        next_question_data = self._get_next_question_structured(state)
        next_question_data['text'] = next_question_text  # Override with conversational text

        return {
            'success': True,
            'response_processed': True,
            'acknowledgment': acknowledgment,
            'question': next_question_data,
            'insights': state.insights[-3:] if state.insights else [],
            'conversation_style': True,  # Flag to indicate conversational mode
            'state': state.to_dict()
        }

    def _get_next_question_structured(self, state: InterviewState) -> Dict[str, Any]:
        """Get structured question data for the next question"""
        # This provides the structured data (input type, options, etc.)
        # while the actual text will be generated conversationally
        phase = state.phase

        # Determine what info we need next
        next_info = self._determine_next_info_needed(state)

        # Map to appropriate input type
        input_type = 'text'  # Default
        options = None

        if 'income' in next_info or 'financial' in next_info:
            input_type = 'multiple_choice'
            options = [
                "Less than $1,000/month",
                "$1,000 - $2,500/month",
                "$2,500 - $5,000/month",
                "$5,000+/month",
                "Just exploring"
            ]
        elif 'commitment' in next_info:
            input_type = 'multiple_choice'
            options = [
                "Very serious - I'll work on this daily",
                "Serious - I'll dedicate real time",
                "Exploring - Want to see what's possible",
                "Just browsing"
            ]
        elif 'time availability' in next_info:
            input_type = 'multiple_choice'
            options = [
                "1-5 hours/week",
                "10-20 hours/week",
                "20-40 hours/week",
                "40+ hours/week"
            ]
        elif 'work preferences' in next_info:
            input_type = 'multi_select'
            options = [
                "Remote work only",
                "Flexible schedule",
                "Project-based",
                "Ongoing clients",
                "Passive income",
                "Service delivery"
            ]

        return {
            'id': f"dynamic_{datetime.now().timestamp()}",
            'phase': phase.value,
            'text': '',  # Will be overridden with conversational text
            'input_type': input_type,
            'options': options,
            'required': True,
            'progress': state.completion_percentage
        }

    def _get_next_question(self, state: InterviewState) -> Dict[str, Any]:
        """Get the next question based on current state (fallback for non-AI mode)"""
        phase = state.phase
        responses = state.responses

        # Introduction phase flow
        if phase == InterviewPhase.INTRODUCTION:
            if 'intro_welcome' not in responses:
                question_id = 'intro_welcome'
            elif 'intro_name' not in responses and not state.profile_data.get('name'):
                # Only ask for name if we don't already have it
                question_id = 'intro_name'
            elif 'intro_situation' not in responses:
                question_id = 'intro_situation'
            elif 'intro_availability' not in responses:
                question_id = 'intro_availability'
            else:
                # Move to skills discovery
                state.phase = InterviewPhase.SKILLS_DISCOVERY
                question_id = 'skills_intro'

        # Skills discovery flow
        elif phase == InterviewPhase.SKILLS_DISCOVERY:
            if 'skills_intro' not in responses:
                question_id = 'skills_intro'
            elif 'skills_technical' not in responses:
                question_id = 'skills_technical'
            elif 'skills_creative' not in responses:
                question_id = 'skills_creative'
            elif 'skills_business' not in responses:
                question_id = 'skills_business'
            elif 'skills_strongest' not in responses:
                question_id = 'skills_strongest'
            elif 'skills_example' not in responses:
                question_id = 'skills_example'
            else:
                # Move to experience deep dive
                state.phase = InterviewPhase.EXPERIENCE_DEEP_DIVE
                question_id = 'exp_background'

        # Experience deep dive flow
        elif phase == InterviewPhase.EXPERIENCE_DEEP_DIVE:
            if 'exp_background' not in responses:
                question_id = 'exp_background'
            elif 'exp_transition' not in responses:
                question_id = 'exp_transition'
            elif 'exp_achievements' not in responses:
                question_id = 'exp_achievements'
            elif 'exp_learning' not in responses:
                question_id = 'exp_learning'
            else:
                # Move to goals & preferences
                state.phase = InterviewPhase.GOALS_PREFERENCES
                question_id = 'goals_income'

        # Goals & preferences flow
        elif phase == InterviewPhase.GOALS_PREFERENCES:
            if 'goals_income' not in responses:
                question_id = 'goals_income'
            elif 'goals_work_type' not in responses:
                question_id = 'goals_work_type'
            elif 'goals_avoid' not in responses:
                question_id = 'goals_avoid'
            elif 'goals_preferences' not in responses:
                question_id = 'goals_preferences'
            else:
                # Move to hidden talents
                state.phase = InterviewPhase.HIDDEN_TALENTS
                question_id = 'talents_hobbies'

        # Hidden talents flow
        elif phase == InterviewPhase.HIDDEN_TALENTS:
            if 'talents_hobbies' not in responses:
                question_id = 'talents_hobbies'
            elif 'talents_natural' not in responses:
                question_id = 'talents_natural'
            elif 'talents_passionate' not in responses:
                question_id = 'talents_passionate'
            else:
                # Move to verification
                state.phase = InterviewPhase.VERIFICATION
                question_id = 'verify_assets'

        # Verification flow
        elif phase == InterviewPhase.VERIFICATION:
            if 'verify_assets' not in responses:
                question_id = 'verify_assets'
            elif 'verify_commitment' not in responses:
                question_id = 'verify_commitment'
            elif 'verify_auto_apply' not in responses:
                question_id = 'verify_auto_apply'
            else:
                # Interview complete
                state.phase = InterviewPhase.COMPLETE
                return {'complete': True}

        else:
            # Interview complete
            state.phase = InterviewPhase.COMPLETE
            return {'complete': True}

        # Update current question
        state.current_question_id = question_id
        question = self.questions[question_id]

        return {
            'id': question.id,
            'phase': question.phase.value,
            'text': question.text,
            'input_type': question.input_type,
            'options': question.options,
            'required': question.required,
            'progress': self._calculate_completion(state)
        }

    async def _extract_profile_data(self, state: InterviewState, question: Question, response: Any):
        """Extract profile data from user response"""
        profile = state.profile_data

        # Extract based on question ID
        # Always extract current_situation from intro_situation response or any question about professional situation
        if question.id == 'intro_situation' or 'professional situation' in question.text.lower():
            profile['current_situation'] = str(response)
        elif 'time' in question.text.lower() and 'dedicate' in question.text.lower():
            profile['available_hours'] = str(response)
        # Special case: if user gives name in response to welcome, extract it
        elif question.id == 'intro_welcome':
            response_str = str(response).strip().lower()
            # Check if user provided a name instead of just yes/no
            if 'is fine' in response_str or 'call me' in response_str or ',' in response_str:
                # Extract name from responses like "Chris is fine" or "Chris, is fine"
                name_part = str(response).split(',')[0].split(' is ')[0].strip()
                if name_part and name_part.lower() not in ['yes', 'no', 'yeah', 'nope', 'sure']:
                    profile['name'] = name_part.title()
                    logger.info(f"Extracted name '{name_part}' from welcome response")

        elif question.id == 'intro_name':
            # Smart name extraction - avoid common greetings
            name = str(response).strip()

            # Check if response contains common greeting phrases
            greetings_to_ignore = ['hi there', 'hello there', 'hey there', 'hi!', 'hello!', 'hey!']
            name_lower = name.lower()

            # If the response is just a greeting, don't save it as name
            if name_lower in greetings_to_ignore:
                logger.warning(f"Ignoring greeting '{name}' as name")
                profile['name'] = ''
            # Also check if "there" appears to be incorrectly extracted
            elif name.lower() == 'there':
                logger.warning("'there' detected as name - likely extraction error")
                profile['name'] = ''
            # Valid name
            else:
                # Remove any "Hi, I'm" or "My name is" prefixes
                for prefix in ['hi, i\'m ', 'hello, i\'m ', 'my name is ', 'i\'m ', 'call me ']:
                    if name_lower.startswith(prefix):
                        name = name[len(prefix):].strip()
                        break

                # Capitalize properly
                profile['name'] = name.title() if name else ''

        elif question.id == 'intro_situation':
            profile['current_situation'] = response

        elif question.id == 'intro_availability':
            # Extract hours from response
            if '1-5' in response:
                profile['available_hours'] = 3
            elif '10-20' in response:
                profile['available_hours'] = 15
            elif '20-40' in response:
                profile['available_hours'] = 30
            elif '40+' in response:
                profile['available_hours'] = 50

        elif question.id.startswith('skills_'):
            if question.id == 'skills_technical':
                profile['skills']['technical'] = response if isinstance(response, list) else [response]
            elif question.id == 'skills_creative':
                profile['skills']['creative'] = response if isinstance(response, list) else [response]
            elif question.id == 'skills_business':
                profile['skills']['business'] = response if isinstance(response, list) else [response]
            elif question.id == 'skills_strongest':
                profile['strongest_skill'] = response
            elif question.id == 'skills_example':
                profile['skill_example'] = response

        elif question.id.startswith('exp_'):
            if question.id == 'exp_background':
                profile['experience']['background'] = response
            elif question.id == 'exp_transition':
                profile['experience']['motivation'] = response
            elif question.id == 'exp_achievements':
                profile['experience']['achievements'] = response
            elif question.id == 'exp_learning':
                profile['experience']['learning'] = response

        elif question.id.startswith('goals_'):
            if question.id == 'goals_income':
                # Extract income goal
                if '$500' in response:
                    profile['goals']['monthly_income'] = 500
                elif '$1,000' in response:
                    profile['goals']['monthly_income'] = 1750
                elif '$2,500' in response:
                    profile['goals']['monthly_income'] = 3750
                elif '$5,000+' in response:
                    profile['goals']['monthly_income'] = 7500
            elif question.id == 'goals_work_type':
                profile['goals']['work_preferences'] = response if isinstance(response, list) else [response]
            elif question.id == 'goals_avoid':
                profile['goals']['avoid'] = response
            elif question.id == 'goals_preferences':
                profile['goals']['other_preferences'] = response

        elif question.id.startswith('talents_'):
            if question.id == 'talents_hobbies':
                profile['hidden_talents'].append({'type': 'hobbies', 'description': response})
            elif question.id == 'talents_natural':
                profile['hidden_talents'].append({'type': 'natural_strengths', 'description': response})
            elif question.id == 'talents_passionate':
                profile['hidden_talents'].append({'type': 'passions', 'description': response})

        elif question.id.startswith('verify_'):
            if question.id == 'verify_assets':
                profile['assets'] = response if isinstance(response, list) else [response]
            elif question.id == 'verify_commitment':
                if 'Very serious' in response:
                    profile['commitment_level'] = CommitmentLevel.VERY_SERIOUS.value
                elif 'Serious' in response:
                    profile['commitment_level'] = CommitmentLevel.SERIOUS.value
                elif 'Exploring' in response:
                    profile['commitment_level'] = CommitmentLevel.EXPLORING.value
                else:
                    profile['commitment_level'] = CommitmentLevel.JUST_BROWSING.value
            elif question.id == 'verify_auto_apply':
                profile['auto_apply_preference'] = response

    async def _analyze_response_with_ai(self, response: str, analysis_prompt: str) -> List[str]:
        """Use AI to analyze user response and extract insights"""
        # Placeholder for AI analysis - would integrate with actual AI service
        insights = []

        # Simple keyword-based analysis for now
        response_lower = response.lower()

        # Detect technical skills
        tech_skills = []
        for skill in self.skill_keywords['technical']:
            if skill in response_lower:
                tech_skills.append(skill)
        if tech_skills:
            insights.append(f"Technical skills detected: {', '.join(tech_skills)}")

        # Detect business experience
        business_terms = []
        for term in self.skill_keywords['business']:
            if term in response_lower:
                business_terms.append(term)
        if business_terms:
            insights.append(f"Business experience: {', '.join(business_terms)}")

        # Detect confidence levels
        confidence_words = ['expert', 'proficient', 'experienced', 'years', 'professional']
        if any(word in response_lower for word in confidence_words):
            insights.append("High confidence/experience level detected")

        # Detect quantifiable achievements
        numbers = ['$', '%', 'million', 'thousand', 'increased', 'improved', 'reduced']
        if any(word in response_lower for word in numbers):
            insights.append("Quantifiable achievements mentioned")

        return insights

    def _calculate_completion(self, state: InterviewState) -> float:
        """Calculate interview completion percentage"""
        total_questions = len(self.questions)
        answered_questions = len(state.responses)
        return min(100.0, (answered_questions / total_questions) * 100)

    async def _build_final_profile(self, state: InterviewState) -> Dict[str, Any]:
        """Build the final comprehensive user profile"""
        profile_data = state.profile_data

        # Compile all skills
        all_skills = []
        for category, skills in profile_data['skills'].items():
            all_skills.extend(skills)

        # Remove 'None of these' entries
        all_skills = [skill for skill in all_skills if skill != 'None of these']

        # Calculate profile strength score
        strength_score = self._calculate_profile_strength(state)

        # Generate recommendations
        recommendations = self._generate_recommendations(state)

        final_profile = {
            'user_id': profile_data['user_id'],
            'interview_completed_at': datetime.now().isoformat(),
            'interview_type': profile_data['interview_type'],

            # Basic info
            'name': profile_data.get('name', ''),
            'current_situation': profile_data.get('current_situation', ''),
            'available_hours_per_week': profile_data.get('available_hours', 0),

            # Skills
            'skills_by_category': profile_data['skills'],
            'all_skills': all_skills,
            'strongest_skill': profile_data.get('strongest_skill', ''),
            'skill_example': profile_data.get('skill_example', ''),

            # Experience
            'professional_background': profile_data.get('experience', {}).get('background', ''),
            'career_motivation': profile_data.get('experience', {}).get('motivation', ''),
            'achievements': profile_data.get('experience', {}).get('achievements', ''),
            'learning_activity': profile_data.get('experience', {}).get('learning', ''),

            # Goals
            'monthly_income_goal': profile_data.get('goals', {}).get('monthly_income', 0),
            'work_preferences': profile_data.get('goals', {}).get('work_preferences', []),
            'things_to_avoid': profile_data.get('goals', {}).get('avoid', ''),
            'other_preferences': profile_data.get('goals', {}).get('other_preferences', ''),

            # Hidden talents
            'hidden_talents': profile_data.get('hidden_talents', []),

            # Verification
            'available_assets': profile_data.get('assets', []),
            'commitment_level': profile_data.get('commitment_level', ''),
            'auto_apply_preference': profile_data.get('auto_apply_preference', ''),

            # AI insights
            'ai_insights': state.insights,
            'profile_strength_score': strength_score,
            'recommendations': recommendations,

            # Metadata
            'completion_percentage': state.completion_percentage,
            'total_responses': len(state.responses),
            'interview_duration_minutes': (datetime.now() - state.started_at).total_seconds() / 60
        }

        return final_profile

    def _calculate_profile_strength(self, state: InterviewState) -> float:
        """Calculate overall profile strength score (0-100)"""
        score = 0

        # Skills diversity (20 points max)
        skill_count = sum(len(skills) for skills in state.profile_data['skills'].values())
        score += min(20, skill_count * 2)

        # Experience depth (20 points max)
        if state.profile_data.get('experience', {}).get('background'):
            score += 10
        if state.profile_data.get('experience', {}).get('achievements'):
            score += 10

        # Clear goals (20 points max)
        if state.profile_data.get('goals', {}).get('monthly_income', 0) > 0:
            score += 10
        if state.profile_data.get('goals', {}).get('work_preferences'):
            score += 10

        # Commitment level (20 points max)
        commitment = state.profile_data.get('commitment_level', '')
        if commitment == CommitmentLevel.VERY_SERIOUS.value:
            score += 20
        elif commitment == CommitmentLevel.SERIOUS.value:
            score += 15
        elif commitment == CommitmentLevel.EXPLORING.value:
            score += 10

        # Available assets (10 points max)
        assets = state.profile_data.get('assets', [])
        if any('portfolio' in str(asset).lower() or 'linkedin' in str(asset).lower() for asset in assets):
            score += 5
        if any('resume' in str(asset).lower() or 'github' in str(asset).lower() for asset in assets):
            score += 5

        # AI insights (10 points max)
        score += min(10, len(state.insights))

        return min(100.0, score)

    def _generate_recommendations(self, state: InterviewState) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on profile"""
        recommendations = []

        profile = state.profile_data
        skills = profile['skills']
        goals = profile.get('goals', {})

        # Technical skill recommendations
        if skills['technical']:
            recommendations.append({
                'category': 'technical_opportunities',
                'title': 'Leverage Your Technical Skills',
                'description': 'Your technical background opens doors to high-paying freelance and remote opportunities.',
                'specific_actions': [
                    'Create profiles on Upwork and Toptal',
                    'Build a portfolio showcasing your best work',
                    'Consider AI/automation consulting services'
                ],
                'income_potential': '$3,000-$8,000/month'
            })

        # Creative skill recommendations
        if skills['creative']:
            recommendations.append({
                'category': 'creative_opportunities',
                'title': 'Monetize Your Creative Talents',
                'description': 'Creative skills are in high demand for digital marketing and content creation.',
                'specific_actions': [
                    'Offer social media management services',
                    'Create digital products and templates',
                    'Build a creative services agency'
                ],
                'income_potential': '$1,500-$5,000/month'
            })

        # Business experience recommendations
        if skills['business']:
            recommendations.append({
                'category': 'business_opportunities',
                'title': 'Scale Your Business Experience',
                'description': 'Your business background is perfect for consulting and B2B services.',
                'specific_actions': [
                    'Start business consulting services',
                    'Offer project management for startups',
                    'Create business development partnerships'
                ],
                'income_potential': '$2,000-$10,000/month'
            })

        # Commitment-based recommendations
        commitment = profile.get('commitment_level', '')
        if commitment == CommitmentLevel.VERY_SERIOUS.value:
            recommendations.append({
                'category': 'high_commitment',
                'title': 'High-Impact Opportunities for Serious Commitment',
                'description': 'Since you are very serious, consider opportunities with higher complexity but greater rewards.',
                'specific_actions': [
                    'Launch a full service business',
                    'Build and scale digital products',
                    'Develop recurring revenue streams'
                ],
                'income_potential': '$5,000-$15,000/month'
            })

        return recommendations

    async def get_interview_status(self, user_id: str) -> Dict[str, Any]:
        """Get current interview status for a user"""
        if user_id not in self.active_interviews:
            return {'active': False, 'message': 'No active interview'}

        state = self.active_interviews[user_id]
        return {
            'active': True,
            'state': state.to_dict(),
            'next_question': self._get_next_question(state) if state.phase != InterviewPhase.COMPLETE else None
        }

    async def resume_interview(self, user_id: str) -> Dict[str, Any]:
        """Resume an existing interview"""
        if user_id not in self.active_interviews:
            return {'error': 'No interview to resume'}

        state = self.active_interviews[user_id]

        # Check if interview expired (older than 24 hours)
        if datetime.now() - state.last_activity > timedelta(hours=24):
            del self.active_interviews[user_id]
            return {'error': 'Interview expired, please start a new one'}

        next_question = self._get_next_question(state)

        return {
            'success': True,
            'resumed': True,
            'question': next_question,
            'state': state.to_dict()
        }

    def cleanup_expired_interviews(self):
        """Clean up expired interviews (call periodically)"""
        expired_users = []
        cutoff_time = datetime.now() - timedelta(hours=24)

        for user_id, state in self.active_interviews.items():
            if state.last_activity < cutoff_time:
                expired_users.append(user_id)

        for user_id in expired_users:
            del self.active_interviews[user_id]

        logger.info(f"Cleaned up {len(expired_users)} expired interviews")


# Global interview service instance
personal_assistant_interviewer = PersonalAssistantInterviewer()