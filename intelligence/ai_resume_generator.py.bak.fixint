"""
AI Resume Generator - Intelligent Resume Creation for AI Professionals
======================================================================

This module generates compelling, ATS-optimized resumes that highlight
AI expertise and capabilities. It creates resumes tailored to specific
job opportunities, emphasizing relevant AI skills and experience.

Key Features:
- Dynamic skill highlighting based on job requirements
- AI portfolio generation
- Quantifiable achievement generation
- ATS optimization
- Multiple format support (PDF, DOCX, TXT)
"""

import json
import random
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# Add path for core imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm_enforcer import get_llm_enforcer
from .ai_job_matcher import AIJobCategory


@dataclass
class AIResume:
    """Represents an AI-optimized resume"""

    name: str
    email: str
    phone: str
    location: str
    title: str
    summary: str
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    portfolio: List[Dict[str, Any]]
    achievements: List[str]
    languages: List[str]
    ai_tools: List[str]


class AIResumeGenerator:
    """
    Generates compelling AI-focused resumes tailored to specific opportunities
    """

    def __init__(self):
        # Core AI skills by category
        self.ai_skills = {
            AIJobCategory.CONTENT_WRITING: [
                "ChatGPT", "Claude", "SEO Writing", "Content Strategy",
                "Copywriting", "Blog Writing", "Technical Writing",
                "Content Marketing", "Jasper AI", "Copy.ai"
            ],
            AIJobCategory.DATA_ANALYSIS: [
                "Python", "Pandas", "NumPy", "Data Visualization",
                "SQL", "Excel", "Tableau", "Power BI", "Statistical Analysis",
                "Machine Learning", "ChatGPT Code Interpreter"
            ],
            AIJobCategory.CODE_GENERATION: [
                "Python", "JavaScript", "GitHub Copilot", "ChatGPT",
                "API Development", "Web Development", "Automation",
                "Testing", "Docker", "CI/CD", "Git"
            ],
            AIJobCategory.GRAPHIC_DESIGN: [
                "DALL-E", "Midjourney", "Stable Diffusion", "Photoshop",
                "Illustrator", "Canva", "Figma", "UI/UX Design",
                "Brand Design", "Creative Direction"
            ],
            AIJobCategory.PROMPT_ENGINEERING: [
                "Prompt Design", "ChatGPT", "Claude", "LLM Fine-tuning",
                "Prompt Testing", "AI Training", "Model Evaluation",
                "Natural Language Processing", "Conversational AI"
            ],
            AIJobCategory.VIRTUAL_ASSISTANT: [
                "Task Management", "Calendar Management", "Email Management",
                "Zapier", "Make.com", "ChatGPT", "Administrative Support",
                "Project Management", "Customer Service", "Research"
            ]
        }

        # Professional titles by category
        self.job_titles = {
            AIJobCategory.CONTENT_WRITING: [
                "AI Content Strategist",
                "Senior AI Content Writer",
                "AI-Powered Copywriter",
                "Content Marketing Specialist (AI-Enhanced)",
                "SEO Content Expert with AI Proficiency"
            ],
            AIJobCategory.DATA_ANALYSIS: [
                "AI Data Analyst",
                "Machine Learning Data Specialist",
                "Business Intelligence Analyst (AI-Powered)",
                "Data Science Consultant",
                "AI Analytics Expert"
            ],
            AIJobCategory.CODE_GENERATION: [
                "AI Software Developer",
                "Full-Stack Developer (AI-Enhanced)",
                "Automation Engineer",
                "AI Integration Specialist",
                "Python Developer with AI Expertise"
            ],
            AIJobCategory.PROMPT_ENGINEERING: [
                "Senior Prompt Engineer",
                "AI Conversation Designer",
                "LLM Specialist",
                "AI Training Expert",
                "Prompt Engineering Consultant"
            ]
        }

        # Achievement templates
        self.achievement_templates = [
            "Increased {metric} by {percentage}% using AI-powered {tool}",
            "Automated {process} saving {hours} hours weekly with {technology}",
            "Generated ${amount} in revenue through AI-enhanced {service}",
            "Completed {number}+ {deliverable} with {rating}% client satisfaction",
            "Reduced {metric} by {percentage}% implementing AI solutions",
            "Delivered {number} projects ahead of schedule using AI tools",
            "Trained AI models achieving {percentage}% accuracy in {task}",
            "Optimized {process} resulting in {percentage}% efficiency gain"
        ]

        # Certification options
        self.certifications = [
            "OpenAI API Certification",
            "Google AI/ML Professional Certificate",
            "DeepLearning.AI Specialization",
            "Microsoft Azure AI Fundamentals",
            "AWS Machine Learning Specialty",
            "Prompt Engineering Certification",
            "HuggingFace NLP Course",
            "Fast.ai Practical Deep Learning"
        ]

    def generate_resume(self,
                        user_profile: Dict[str, Any],
                        job_category: AIJobCategory,
                        job_requirements: Optional[List[str]] = None) -> AIResume:
        """
        Generate a tailored AI resume for a specific job category

        Args:
            user_profile: User's profile information
            job_category: The category of job to tailor for
            job_requirements: Specific requirements from the job posting

        Returns:
            AIResume object with all fields populated
        """

        # Extract user info or use defaults
        name = user_profile.get('name', 'Alex Johnson')
        email = user_profile.get('email', 'ai.professional@email.com')
        phone = user_profile.get('phone', '+1 (555) 123-4567')
        location = user_profile.get('location', 'Remote | Available Worldwide')

        # Generate professional title
        title = self._generate_title(job_category, user_profile)

        # Generate compelling summary
        summary = self._generate_summary(job_category, user_profile)

        # Generate skills based on category and requirements
        skills = self._generate_skills(job_category, job_requirements)

        # Generate experience
        experience = self._generate_experience(job_category, user_profile)

        # Generate education
        education = self._generate_education(user_profile)

        # Select certifications
        certs = self._select_certifications(job_category)

        # Generate portfolio
        portfolio = self._generate_portfolio(job_category)

        # Generate achievements
        achievements = self._generate_achievements(job_category)

        # Languages
        languages = user_profile.get('languages', ['English (Native)', 'Spanish (Conversational)'])

        # AI tools
        ai_tools = self.ai_skills.get(job_category, [])[:8]

        return AIResume(
            name=name,
            email=email,
            phone=phone,
            location=location,
            title=title,
            summary=summary,
            skills=skills,
            experience=experience,
            education=education,
            certifications=certs,
            portfolio=portfolio,
            achievements=achievements,
            languages=languages,
            ai_tools=ai_tools
        )

    def _generate_title(self, category: AIJobCategory, profile: Dict) -> str:
        """Generate professional title"""

        if profile.get('professional_title'):
            return profile['professional_title']

        titles = self.job_titles.get(category, ["AI Professional"])
        return random.choice(titles)

    def _generate_summary(self, category: AIJobCategory, profile: Dict) -> str:
        """Generate professional summary using REAL AI"""

        years = profile.get('years_experience', 5)

        # Use real AI to generate summary
        enforcer = get_llm_enforcer()

        # Extract profile information for context
        skills = profile.get('skills', [])
        experience = profile.get('professional_summary', '')

        prompt = f"""Generate a compelling professional summary for a resume.

Job Category: {category.value}
Years of Experience: {years}
Current Skills: {', '.join(skills[:10]) if skills else 'AI tools, automation, analysis'}
Background: {experience if experience else 'Professional with AI expertise'}

Requirements:
1. 3-4 sentences maximum
2. Highlight AI expertise relevant to {category.value}
3. Include quantifiable achievements (e.g., "increased efficiency by X%")
4. Professional tone, action-oriented language
5. Focus on value delivered to clients/employers

Generate ONLY the summary text, no labels or formatting."""

        try:
            result = enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name="AIResumeGenerator",
                task_type="resume_summary",
                max_tokens=200,
                temperature=0.7
            )
            return result['content'].strip()
        except Exception as e:
            # Fallback to template if AI fails
            print(f"Failed to generate AI summary: {e}")
            return f"AI Professional with {years}+ years of experience specializing in {category.value}."

    def _generate_skills(self, category: AIJobCategory, requirements: Optional[List[str]]) -> List[str]:
        """Generate relevant skills list"""

        # Start with category-specific skills
        skills = self.ai_skills.get(category, [])[:6]

        # Add general AI skills
        general_skills = [
            "Machine Learning", "Natural Language Processing",
            "API Integration", "Process Automation",
            "Project Management", "Agile Methodologies"
        ]

        skills.extend(random.sample(general_skills, 3))

        # Add any specific requirements
        if requirements:
            for req in requirements[:3]:
                if req not in skills:
                    skills.append(req)

        return skills[:12]  # Limit to 12 skills

    def _generate_experience(self, category: AIJobCategory, profile: Dict) -> List[Dict[str, Any]]:
        """Generate work experience entries"""

        experiences = []

        # Current/Recent position
        experiences.append({
            "title": self.job_titles.get(category, ["AI Specialist"])[0],
            "company": "Freelance / AI Consulting",
            "location": "Remote",
            "start_date": "2022",
            "end_date": "Present",
            "highlights": [
                f"Completed 100+ AI-powered projects with 5-star ratings",
                f"Generated ${random.randint(50, 200)}K in client revenue through AI solutions",
                f"Reduced project delivery time by {random.randint(40, 70)}% using AI tools",
                f"Built AI automation systems processing {random.randint(10, 50)}K+ data points daily"
            ]
        })

        # Previous position
        experiences.append({
            "title": f"{category.value.replace('_', ' ').title()} Specialist",
            "company": "TechCorp Solutions",
            "location": "Remote",
            "start_date": "2020",
            "end_date": "2022",
            "highlights": [
                f"Led AI transformation initiative improving efficiency by {random.randint(30, 60)}%",
                f"Trained team of {random.randint(5, 15)} on AI best practices",
                f"Implemented AI tools saving ${random.randint(100, 500)}K annually",
                f"Managed {random.randint(20, 50)} concurrent AI-enhanced projects"
            ]
        })

        return experiences

    def _generate_education(self, profile: Dict) -> List[Dict[str, Any]]:
        """Generate education entries"""

        education = profile.get('education', [])

        if not education:
            education = [{
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "State University",
                "year": "2018",
                "highlights": ["AI/ML Specialization", "Dean's List", "3.8 GPA"]
            }]

        return education

    def _select_certifications(self, category: AIJobCategory) -> List[str]:
        """Select relevant certifications"""

        # Always include some general AI certs
        certs = random.sample(self.certifications[:4], 2)

        # Add category-specific
        if category == AIJobCategory.PROMPT_ENGINEERING:
            certs.append("Prompt Engineering Certification")
        elif category == AIJobCategory.DATA_ANALYSIS:
            certs.append("Google Data Analytics Professional Certificate")
        elif category == AIJobCategory.CODE_GENERATION:
            certs.append("GitHub Copilot Certification")

        return certs[:4]

    def _generate_portfolio(self, category: AIJobCategory) -> List[Dict[str, Any]]:
        """Generate portfolio items"""

        portfolio = []

        if category == AIJobCategory.CONTENT_WRITING:
            portfolio.extend([
                {
                    "title": "AI-Generated Blog Series",
                    "description": "30-article series on emerging tech, 500K+ views",
                    "link": "portfolio.example.com/blog-series"
                },
                {
                    "title": "SEO Content Strategy",
                    "description": "Increased organic traffic by 300% in 6 months",
                    "link": "portfolio.example.com/seo-case-study"
                }
            ])
        elif category == AIJobCategory.CODE_GENERATION:
            portfolio.extend([
                {
                    "title": "AI-Powered Web Scraper",
                    "description": "Python tool processing 1M+ pages daily",
                    "link": "github.com/username/ai-scraper"
                },
                {
                    "title": "Chatbot Development",
                    "description": "Customer service bot handling 10K+ queries/month",
                    "link": "github.com/username/ai-chatbot"
                }
            ])
        elif category == AIJobCategory.DATA_ANALYSIS:
            portfolio.extend([
                {
                    "title": "Predictive Analytics Dashboard",
                    "description": "ML model with 94% accuracy in sales forecasting",
                    "link": "portfolio.example.com/analytics-dashboard"
                },
                {
                    "title": "Data Pipeline Automation",
                    "description": "ETL system processing 100GB+ daily",
                    "link": "github.com/username/data-pipeline"
                }
            ])

        return portfolio

    def _generate_achievements(self, category: AIJobCategory) -> List[str]:
        """Generate quantifiable achievements"""

        achievements = []

        for _ in range(4):
            template = random.choice(self.achievement_templates)

            # Fill in the template with relevant values
            achievement = template.format(
                metric=random.choice(['productivity', 'efficiency', 'revenue', 'engagement']),
                percentage=random.randint(30, 200),
                tool=random.choice(self.ai_skills.get(category, ['AI tools'])[:3]),
                process=random.choice(['content creation', 'data analysis', 'development', 'workflow']),
                hours=random.randint(10, 40),
                technology=random.choice(['AI automation', 'machine learning', 'NLP', 'ChatGPT']),
                amount=random.randint(10, 100) * 1000,
                service=random.choice(['consulting', 'development', 'analysis', 'content']),
                number=random.randint(50, 500),
                deliverable=random.choice(['projects', 'articles', 'reports', 'applications']),
                rating=random.randint(95, 100),
                task=random.choice(['classification', 'prediction', 'generation', 'analysis'])
            )

            achievements.append(achievement)

        return achievements

    def format_resume_text(self, resume: AIResume) -> str:
        """Format resume as plain text"""

        text = f"""
{resume.name}
{resume.title}
{resume.email} | {resume.phone} | {resume.location}

PROFESSIONAL SUMMARY
{resume.summary}

CORE SKILLS
{', '.join(resume.skills)}

AI TOOLS & TECHNOLOGIES
{', '.join(resume.ai_tools)}

PROFESSIONAL EXPERIENCE
"""

        for exp in resume.experience:
            text += f"\n{exp['title']}\n"
            text += f"{exp['company']} | {exp['location']} | {exp['start_date']} - {exp['end_date']}\n"
            for highlight in exp['highlights']:
                text += f"• {highlight}\n"

        text += "\nKEY ACHIEVEMENTS\n"
        for achievement in resume.achievements:
            text += f"• {achievement}\n"

        text += "\nEDUCATION\n"
        for edu in resume.education:
            text += f"{edu['degree']} in {edu['field']}\n"
            text += f"{edu['institution']}, {edu['year']}\n"

        text += "\nCERTIFICATIONS\n"
        for cert in resume.certifications:
            text += f"• {cert}\n"

        if resume.portfolio:
            text += "\nPORTFOLIO HIGHLIGHTS\n"
            for item in resume.portfolio:
                text += f"• {item['title']}: {item['description']}\n"

        text += f"\nLANGUAGES\n{', '.join(resume.languages)}\n"

        return text

    def generate_cover_letter(self, resume: AIResume, job_title: str, company: str = "your company") -> str:
        """Generate a matching cover letter using REAL AI"""

        # Use real AI to generate cover letter
        enforcer = get_llm_enforcer()

        prompt = f"""Write a compelling cover letter for a job application.

Job Title: {job_title}
Company: {company}
Applicant: {resume.name}
Professional Title: {resume.title}
Summary: {resume.summary}
Key Skills: {', '.join(resume.skills[:8])}
AI Tools: {', '.join(resume.ai_tools[:5])}
Recent Achievements:
{chr(10).join('- ' + a for a in resume.achievements[:2])}

Requirements:
1. Professional yet personable tone
2. 4-5 paragraphs maximum
3. Emphasize AI expertise and efficiency gains
4. Include specific achievements and quantifiable results
5. Express genuine enthusiasm for the role
6. End with a clear call to action

Format:
- Start with "Dear Hiring Manager,"
- End with contact information
- Professional sign-off

Generate the complete cover letter."""

        try:
            result = enforcer.enforce_real_ai(
                prompt=prompt,
                agent_name="AIResumeGenerator",
                task_type="cover_letter",
                max_tokens=500,
                temperature=0.8
            )

            # Add contact info at the end if not already included
            letter = result['content'].strip()
            if resume.email not in letter:
                letter += f"\n\n{resume.name}\n{resume.email}\n{resume.phone}"

            return letter

        except Exception as e:
            # Fallback to basic template if AI fails
            print(f"Failed to generate AI cover letter: {e}")
            letter = f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. As an {resume.title} with expertise in cutting-edge AI technologies, I am excited about the opportunity to bring my unique blend of technical skills and AI innovation to your team.

{resume.summary}

In my current role, I have:
{chr(10).join('• ' + h for h in resume.experience[0]['highlights'][:3])}

What sets me apart is my deep expertise in AI tools and technologies, including {', '.join(resume.ai_tools[:4])}. I've successfully leveraged these tools to deliver exceptional results quickly and efficiently, often exceeding client expectations while reducing project timelines by up to 70%.

My recent achievements include:
{chr(10).join('• ' + a for a in resume.achievements[:2])}

I am particularly drawn to this opportunity because it aligns perfectly with my expertise in AI-enhanced solutions. I am confident that my combination of technical skills, AI proficiency, and proven track record of delivering results will make me a valuable addition to your team.

I would welcome the opportunity to discuss how my AI expertise can contribute to {company}'s continued success. I am available for an interview at your earliest convenience and can start immediately.

Thank you for considering my application. I look forward to the possibility of contributing to your team's success.

Best regards,
{resume.name}
{resume.email}
{resume.phone}

Portfolio: Available upon request
LinkedIn: linkedin.com/in/{resume.name.lower().replace(' ', '-')}
"""
            return letter