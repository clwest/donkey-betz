#!/usr/bin/env python3
"""
Test AI Job Application System
==============================
Demonstrates the complete flow from job discovery to application submission
with AI-generated resumes and proposals.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from intelligence.ai_job_matcher import AIJobMatcher, AIJobCategory
from intelligence.ai_resume_generator import AIResumeGenerator


def test_ai_job_system():
    """Test the complete AI job application system"""

    print("🤖 AI JOB APPLICATION SYSTEM TEST")
    print("="*60)

    # Sample job opportunities (these would come from spiders)
    job_opportunities = [
        {
            "id": "job_001",
            "title": "AI Content Writer Needed for Tech Blog",
            "description": """
            We need an experienced content writer to create blog posts about AI and machine learning.
            Requirements:
            - Write 5 articles per week (1500 words each)
            - SEO optimization required
            - Must be familiar with ChatGPT and other AI tools
            - Quick turnaround time (24-48 hours)
            - Bulk work available for the right candidate

            Budget: $50-100 per article
            This is ongoing work with potential for long-term collaboration.
            """,
            "skills": ["Content Writing", "SEO", "AI Tools", "Blog Writing"],
            "budget": 75,
            "client_history": {
                "hire_rate": 85,
                "payment_verified": True,
                "review_score": 4.8
            },
            "proposal_count": 3
        },
        {
            "id": "job_002",
            "title": "Python Developer for Data Analysis Automation",
            "description": """
            Looking for Python developer to automate our data analysis workflows.
            Must have experience with:
            - Pandas and NumPy for data processing
            - Creating automated reports
            - API integration
            - Using AI tools like ChatGPT for code generation

            This is a one-time project with possibility of ongoing work.
            Budget: $500-1000
            Timeline: 1 week
            """,
            "skills": ["Python", "Data Analysis", "Automation", "APIs"],
            "budget": 750,
            "client_history": {
                "hire_rate": 70,
                "payment_verified": True,
                "review_score": 4.5
            },
            "proposal_count": 8
        },
        {
            "id": "job_003",
            "title": "Virtual Assistant with AI Skills",
            "description": """
            Seeking a virtual assistant who can leverage AI tools for efficiency.
            Tasks include:
            - Email management and drafting
            - Calendar scheduling
            - Research and data entry
            - Social media management
            - Must be proficient with ChatGPT, Zapier, and automation tools

            Part-time position, 20 hours/week
            Rate: $15-25/hour
            Remote work, flexible hours
            """,
            "skills": ["Virtual Assistant", "ChatGPT", "Zapier", "Email Management"],
            "budget": 20,
            "client_history": {
                "hire_rate": 90,
                "payment_verified": True,
                "review_score": 4.9
            },
            "proposal_count": 12
        },
        {
            "id": "job_004",
            "title": "Prompt Engineer for AI Chatbot Development",
            "description": """
            We're building a customer service chatbot and need a prompt engineering expert.

            Requirements:
            - Design and optimize prompts for ChatGPT/Claude
            - Create conversation flows
            - Test and iterate on prompt performance
            - Document prompt templates
            - Experience with LLMs required

            Project duration: 2-3 weeks
            Budget: $2000-3000
            Urgent - need to start ASAP
            """,
            "skills": ["Prompt Engineering", "ChatGPT", "LLM", "Chatbot Development"],
            "budget": 2500,
            "client_history": {
                "hire_rate": 75,
                "payment_verified": True,
                "review_score": 4.7
            },
            "proposal_count": 5
        }
    ]

    # Initialize AI systems
    job_matcher = AIJobMatcher()
    resume_generator = AIResumeGenerator()

    # User profile (this would come from the database)
    user_profile = {
        "name": "Chris Johnson",
        "email": "chris.ai.pro@gmail.com",
        "phone": "+1 (555) 987-6543",
        "location": "Remote | USA",
        "years_experience": 3,
        "languages": ["English (Native)", "Spanish (Intermediate)"]
    }

    print("\n📋 Analyzing Job Opportunities...")
    print("-"*40)

    # Analyze and rank opportunities
    matches = job_matcher.rank_opportunities(job_opportunities)

    print(f"Found {len(matches)} suitable AI job opportunities\n")

    # Display top matches
    for i, match in enumerate(matches[:3], 1):
        print(f"\n🎯 Match #{i}: {match.title}")
        print(f"   Category: {match.category.value}")
        print(f"   AI Score: {match.ai_score:.2%}")
        print(f"   Success Probability: {match.success_probability:.2%}")
        print(f"   Budget: ${match.budget}")
        print(f"   Time Estimate: {match.estimated_completion_time} hours")
        print(f"   AI Tools: {', '.join(match.ai_tools_applicable[:3])}")

    # Select the best match
    best_match = matches[0]

    print("\n" + "="*60)
    print(f"✅ SELECTED: {best_match.title}")
    print("="*60)

    print(f"\n📝 Recommended Approach:")
    print(f"{best_match.recommended_approach}")

    print(f"\n🛠️ Applicable AI Tools:")
    for tool in best_match.ai_tools_applicable:
        print(f"   • {tool}")

    # Generate tailored resume
    print("\n📄 Generating AI-Optimized Resume...")
    print("-"*40)

    resume = resume_generator.generate_resume(
        user_profile,
        best_match.category,
        best_match.required_skills
    )

    print(f"Name: {resume.name}")
    print(f"Title: {resume.title}")
    print(f"Location: {resume.location}")
    print(f"\nCore Skills: {', '.join(resume.skills[:6])}")
    print(f"AI Tools: {', '.join(resume.ai_tools[:4])}")
    print(f"Certifications: {len(resume.certifications)} relevant certifications")
    print(f"Achievements: {len(resume.achievements)} quantifiable achievements")

    # Generate proposal
    print("\n💌 Generating Proposal...")
    print("-"*40)

    proposal = job_matcher.generate_proposal_template(best_match)
    print(proposal[:500] + "...")  # Show first 500 chars

    # Generate cover letter
    print("\n📨 Generating Cover Letter...")
    print("-"*40)

    cover_letter = resume_generator.generate_cover_letter(
        resume,
        best_match.title,
        "Your Company"
    )
    print(cover_letter[:500] + "...")  # Show first 500 chars

    # Save outputs
    print("\n💾 Saving Application Materials...")
    print("-"*40)

    # Save resume
    resume_path = f"ai_resume_{best_match.job_id}.txt"
    with open(resume_path, 'w') as f:
        f.write(resume_generator.format_resume_text(resume))
    print(f"✅ Resume saved to: {resume_path}")

    # Save proposal
    proposal_path = f"ai_proposal_{best_match.job_id}.txt"
    with open(proposal_path, 'w') as f:
        f.write(proposal)
    print(f"✅ Proposal saved to: {proposal_path}")

    # Save cover letter
    cover_path = f"ai_cover_letter_{best_match.job_id}.txt"
    with open(cover_path, 'w') as f:
        f.write(cover_letter)
    print(f"✅ Cover letter saved to: {cover_path}")

    print("\n" + "="*60)
    print("🎉 AI JOB APPLICATION SYSTEM TEST COMPLETE!")
    print("="*60)

    print(f"""
📊 SUMMARY:
   • Analyzed {len(job_opportunities)} job opportunities
   • Identified {len(matches)} AI-suitable matches
   • Selected best match with {best_match.ai_score:.0%} AI suitability
   • Generated tailored resume highlighting {len(resume.ai_tools)} AI tools
   • Created personalized proposal and cover letter
   • All materials optimized for ATS and AI keywords

🚀 NEXT STEPS:
   1. Review generated materials
   2. Customize proposal with specific examples
   3. Submit application through platform
   4. Track response rate for optimization

💡 KEY INSIGHT:
   This job has {best_match.success_probability:.0%} success probability
   with only {best_match.estimated_completion_time} hours estimated work time.
   Perfect for AI-assisted completion!
""")

    return best_match, resume, proposal


if __name__ == "__main__":
    # Run the test
    match, resume, proposal = test_ai_job_system()

    print("\n🔄 System is ready to process real job opportunities from spiders!")
    print("   Connect this to your spider data for automatic job applications.")