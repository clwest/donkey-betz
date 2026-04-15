#!/usr/bin/env python3
"""
Real Job Executor - Creates unique content based on actual job requirements
"""

import os
import sys
import django
import redis
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Setup Django environment
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import logging
from ai_core.agents.agent_llm_integration import agent_llm_integration

logger = logging.getLogger(__name__)

# Redis URL for production compatibility
_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')


class RealJobExecutor:
    """
    Executes real freelance jobs based on actual requirements.

    All LLM calls route through ``agent_llm_integration.generate_for_agent``;
    the raw OpenAI client previously held in ``self.client`` was dead code
    (assigned but never read) and was removed in Session 1086 Tier 4 PR 2.
    """

    def __init__(self):
        self.redis_client = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

    async def execute_job(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a job based on its actual requirements

        Args:
            opportunity: The job opportunity from the spider

        Returns:
            Dictionary with execution results and deliverable info
        """
        try:
            logger.info(f"🎯 Executing real job: {opportunity.get('title', 'Unknown')}")

            # Analyze job requirements
            job_type = self._analyze_job_type(opportunity)

            # Execute based on job type
            if job_type == 'content_writing':
                return await self._execute_content_job(opportunity)
            elif job_type == 'code_development':
                return await self._execute_coding_job(opportunity)
            elif job_type == 'data_analysis':
                return await self._execute_data_job(opportunity)
            elif job_type == 'design':
                return await self._execute_design_job(opportunity)
            else:
                return await self._execute_general_job(opportunity)

        except Exception as e:
            logger.error(f"Error executing job: {e}")
            return None

    def _analyze_job_type(self, opportunity: Dict[str, Any]) -> str:
        """Analyze job to determine type"""
        title = opportunity.get('title', '').lower()
        description = opportunity.get('description', '').lower()
        skills = [skill.lower() for skill in opportunity.get('skills_required', [])]

        # Check for content writing
        content_keywords = ['content', 'writing', 'blog', 'article', 'copywriting', 'seo']
        if any(keyword in title or keyword in description for keyword in content_keywords):
            return 'content_writing'

        # Check for coding/development
        code_keywords = ['python', 'javascript', 'react', 'node', 'api', 'development', 'programming']
        if any(keyword in title or keyword in description or keyword in skills for keyword in code_keywords):
            return 'code_development'

        # Check for data analysis
        data_keywords = ['data', 'analysis', 'pandas', 'visualization', 'dashboard', 'analytics']
        if any(keyword in title or keyword in description or keyword in skills for keyword in data_keywords):
            return 'data_analysis'

        # Check for design
        design_keywords = ['design', 'ui', 'ux', 'frontend', 'graphic', 'visual']
        if any(keyword in title or keyword in description or keyword in skills for keyword in design_keywords):
            return 'design'

        return 'general'

    async def _execute_content_job(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content writing job"""
        title = opportunity.get('title', 'Content Project')
        description = opportunity.get('description', '')

        # Create specific prompt based on job requirements
        prompt = f"""
        Write content for this specific freelance job:

        Job Title: {title}
        Job Description: {description}

        Requirements:
        - Create content that directly addresses the job requirements
        - Use professional, engaging tone
        - Include specific details mentioned in the job description
        - Make it ready for client delivery
        - Target 500-800 words

        Write original content that fulfills this specific job's needs.
        """

        try:
            result = await agent_llm_integration.generate_for_agent(
                agent_name="JobExecutor",
                prompt=f"You are a professional content writer working on this specific job: {title}\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="low",
                verbosity="medium",
                max_output_tokens=1200
            )

            if not result['success']:
                logger.error(f"LLM error in content job: {result.get('error')}")
                return None

            content = result['response']

            # Save unique file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            job_id = opportunity.get('job_id', 'unknown')
            filename = f"real_job_deliverables/content_{job_id}_{timestamp}.md"
            os.makedirs('real_job_deliverables', exist_ok=True)

            with open(filename, 'w') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**Generated for job: {job_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n\n")
                f.write(content)

            logger.info(f"✅ Created content deliverable: {filename}")

            return {
                'type': 'content_writing',
                'filename': filename,
                'content': content,
                'job_title': title,
                'created_at': datetime.now().isoformat(),
                'deliverable_id': f"content_{job_id}_{timestamp}",
                'size': len(content)
            }

        except Exception as e:
            logger.error(f"Error creating content: {e}")
            return None

    async def _execute_coding_job(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding/development job"""
        title = opportunity.get('title', 'Development Project')
        description = opportunity.get('description', '')
        skills = opportunity.get('skills_required', [])

        prompt = f"""
        Create code for this specific development job:

        Job Title: {title}
        Description: {description}
        Required Skills: {', '.join(skills)}

        Requirements:
        - Write production-ready code that addresses the specific requirements
        - Include proper error handling and documentation
        - Use the technologies mentioned in the job description
        - Make it client-ready and functional
        - Include comments explaining the code

        Generate code that solves this specific project's requirements.
        """

        try:
            result = await agent_llm_integration.generate_for_agent(
                agent_name="JobExecutor",
                prompt=f"You are an expert developer working on: {title}\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="low",
                verbosity="medium",
                max_output_tokens=1200
            )

            if not result['success']:
                logger.error(f"LLM error in coding job: {result.get('error')}")
                return None

            code_content = result['response']

            # Clean up code formatting
            if "```python" in code_content:
                code_content = code_content.split("```python")[1].split("```")[0].strip()
            elif "```javascript" in code_content:
                code_content = code_content.split("```javascript")[1].split("```")[0].strip()
            elif "```" in code_content:
                code_content = code_content.split("```")[1].strip()

            # Determine file extension
            extension = '.py'
            if any(lang in skills for lang in ['javascript', 'js', 'react', 'node']):
                extension = '.js'
            elif any(lang in skills for lang in ['html', 'css', 'frontend']):
                extension = '.html'

            # Save unique file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            job_id = opportunity.get('job_id', 'unknown')
            filename = f"real_job_deliverables/code_{job_id}_{timestamp}{extension}"

            with open(filename, 'w') as f:
                f.write(f"#!/usr/bin/env python\n" if extension == '.py' else "")
                f.write(f'"""\n{title}\n')
                f.write(f"Generated for job: {job_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f'"""\n\n')
                f.write(code_content)

            logger.info(f"✅ Created code deliverable: {filename}")

            return {
                'type': 'code_development',
                'filename': filename,
                'content': code_content,
                'job_title': title,
                'language': extension,
                'created_at': datetime.now().isoformat(),
                'deliverable_id': f"code_{job_id}_{timestamp}",
                'size': len(code_content)
            }

        except Exception as e:
            logger.error(f"Error creating code: {e}")
            return None

    async def _execute_data_job(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis job"""
        title = opportunity.get('title', 'Data Analysis Project')
        description = opportunity.get('description', '')

        prompt = f"""
        Create a data analysis solution for this specific job:

        Job Title: {title}
        Description: {description}

        Requirements:
        - Create Python code that addresses the specific data requirements mentioned
        - Include data visualization appropriate to the job
        - Add analysis and insights relevant to the job description
        - Make it production-ready with proper documentation
        - Include sample data handling if needed

        Generate a complete data analysis solution for this specific project.
        """

        try:
            result = await agent_llm_integration.generate_for_agent(
                agent_name="JobExecutor",
                prompt=f"You are a data analyst working on: {title}\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="low",
                verbosity="medium",
                max_output_tokens=1200
            )

            if not result['success']:
                logger.error(f"LLM error in data job: {result.get('error')}")
                return None

            code_content = result['response']

            # Clean up code formatting
            if "```python" in code_content:
                code_content = code_content.split("```python")[1].split("```")[0].strip()
            elif "```" in code_content:
                code_content = code_content.split("```")[1].strip()

            # Save unique file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            job_id = opportunity.get('job_id', 'unknown')
            filename = f"real_job_deliverables/analysis_{job_id}_{timestamp}.py"

            with open(filename, 'w') as f:
                f.write(f"#!/usr/bin/env python\n")
                f.write(f'"""\n{title}\n')
                f.write(f"Data Analysis for job: {job_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f'"""\n\n')
                f.write(code_content)

            logger.info(f"✅ Created data analysis deliverable: {filename}")

            return {
                'type': 'data_analysis',
                'filename': filename,
                'content': code_content,
                'job_title': title,
                'created_at': datetime.now().isoformat(),
                'deliverable_id': f"analysis_{job_id}_{timestamp}",
                'size': len(code_content)
            }

        except Exception as e:
            logger.error(f"Error creating data analysis: {e}")
            return None

    async def _execute_design_job(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute design job (creates specification/requirements)"""
        title = opportunity.get('title', 'Design Project')
        description = opportunity.get('description', '')

        prompt = f"""
        Create design specifications for this specific job:

        Job Title: {title}
        Description: {description}

        Requirements:
        - Create detailed design specifications addressing the job requirements
        - Include layout descriptions, color schemes, typography
        - Provide wireframes in text format
        - Include user experience considerations
        - Make it client-ready with clear deliverables

        Generate comprehensive design documentation for this specific project.
        """

        try:
            result = await agent_llm_integration.generate_for_agent(
                agent_name="JobExecutor",
                prompt=f"You are a UX/UI designer working on: {title}\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="low",
                verbosity="medium",
                max_output_tokens=1200
            )

            if not result['success']:
                logger.error(f"LLM error in design job: {result.get('error')}")
                return None

            design_content = result['response']

            # Save unique file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            job_id = opportunity.get('job_id', 'unknown')
            filename = f"real_job_deliverables/design_{job_id}_{timestamp}.md"

            with open(filename, 'w') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**Design Specifications for job: {job_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n\n")
                f.write(design_content)

            logger.info(f"✅ Created design deliverable: {filename}")

            return {
                'type': 'design',
                'filename': filename,
                'content': design_content,
                'job_title': title,
                'created_at': datetime.now().isoformat(),
                'deliverable_id': f"design_{job_id}_{timestamp}",
                'size': len(design_content)
            }

        except Exception as e:
            logger.error(f"Error creating design: {e}")
            return None

    async def _execute_general_job(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute general job type"""
        title = opportunity.get('title', 'General Project')
        description = opportunity.get('description', '')

        prompt = f"""
        Create deliverable for this specific job:

        Job Title: {title}
        Description: {description}

        Requirements:
        - Analyze the job requirements and create appropriate deliverable
        - Address the specific needs mentioned in the description
        - Make it professional and client-ready
        - Provide actionable, valuable content

        Generate a solution that fulfills this specific job's requirements.
        """

        try:
            result = await agent_llm_integration.generate_for_agent(
                agent_name="JobExecutor",
                prompt=f"You are a freelancer working on: {title}\n\n{prompt}",
                model="gpt-5-mini",
                reasoning_effort="low",
                verbosity="medium",
                max_output_tokens=1200
            )

            if not result['success']:
                logger.error(f"LLM error in general job: {result.get('error')}")
                return None

            content = result['response']

            # Save unique file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            job_id = opportunity.get('job_id', 'unknown')
            filename = f"real_job_deliverables/general_{job_id}_{timestamp}.md"

            with open(filename, 'w') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**Deliverable for job: {job_id} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n\n")
                f.write(content)

            logger.info(f"✅ Created general deliverable: {filename}")

            return {
                'type': 'general',
                'filename': filename,
                'content': content,
                'job_title': title,
                'created_at': datetime.now().isoformat(),
                'deliverable_id': f"general_{job_id}_{timestamp}",
                'size': len(content)
            }

        except Exception as e:
            logger.error(f"Error creating general deliverable: {e}")
            return None


def execute_freelance_jobs():
    """Execute all available freelance jobs"""
    executor = RealJobExecutor()
    r = redis.Redis.from_url(_REDIS_URL, decode_responses=True)

    # Get opportunities from Redis
    opp_keys = r.keys('freelance:opportunity:*')

    if not opp_keys:
        print("❌ No opportunities found in Redis")
        return

    print(f"🎯 Found {len(opp_keys)} opportunities to execute")

    for key in opp_keys[:3]:  # Execute first 3 jobs
        try:
            data = r.get(key)
            if data:
                opportunity = json.loads(data)
                print(f"\n🚀 Executing: {opportunity.get('title', 'Unknown Job')}")

                result = executor.execute_job(opportunity)
                if result:
                    print(f"✅ Created: {result['filename']}")
                    print(f"📊 Type: {result['type']}")
                    print(f"📄 Size: {result['size']} characters")
                else:
                    print("❌ Execution failed")

        except Exception as e:
            print(f"❌ Error processing {key}: {e}")

    print(f"\n✨ Job execution complete! Check the 'real_job_deliverables' folder")


if __name__ == "__main__":
    execute_freelance_jobs()