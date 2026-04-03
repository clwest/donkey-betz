#!/usr/bin/env python3
"""
AI Project Builder
Simplified version for testing the AI opportunity pipeline

Session 306: Added learning infrastructure hooks for cross-agent knowledge sharing.
Session 728: Migrated from agents/ai_project_builder.py to core/services/ai_project_builder.py
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from core.llm_enforcer import get_llm_enforcer
from ai_core.spiders.ai_monetization_spider import research_ai_monetization_sync

logger = logging.getLogger(__name__)


class ProjectBuilderLearningMixin:
    """
    Learning infrastructure mixin for AIProjectBuilder.
    Session 306: Enables cross-agent knowledge sharing for project building.
    """

    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(None)
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                self._agent_model, _ = Agent.objects.get_or_create(
                    name='AIProjectBuilder',
                    defaults={
                        'agent_type': 'legacy',
                        'specialization': 'project_building',
                        'description': 'Builds AI projects from spider-discovered monetization strategies.',
                        'is_active': True,
                    }
                )
            except ImportError:
                logger.debug("Agent model not available")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = True
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type='build',
                query_text=task,
                execution_mode='agent',
                agents_used=['AIProjectBuilder'],
                response=str(result),
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', False),
                spider_data_used=spider_data_used,
                scifi_context_used=False,
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.warning(f"Failed to record learning outcome: {e}")
            return None

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the project build execution."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"Project Build: {task[:50]}...",
                content=str(result),
                memory_type=memory_type,
                valence="positive" if result.get('success') else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['project_building', 'ai_monetization', 'success' if result.get('success') else 'failure']
            )
            return memory
        except Exception as e:
            logger.warning(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """Share learned knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            type_mapping = {
                'project': 'tool_discovery',
                'monetization': 'market',
                'pattern': 'content_idea',
            }
            mapped_type = type_mapping.get(knowledge_type, 'tool_discovery')

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            logger.warning(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge from other agents."""
        try:
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                queryset = queryset.filter(knowledge_type=knowledge_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            return [
                {
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                }
                for ks in queryset.order_by('-confidence_score')[:10]
            ]
        except Exception as e:
            logger.warning(f"Failed to get shared knowledge: {e}")
            return []


class AIProjectBuilder(ProjectBuilderLearningMixin):
    """
    Simplified AI project builder for testing.

    Session 306: Added learning infrastructure for cross-agent knowledge sharing.
    """

    def __init__(self):
        self.llm_enforcer = get_llm_enforcer()
        self.project_workspace = Path("/Users/donkeyking/development/unified-donkey-betz/generated_projects")
        self.project_workspace.mkdir(exist_ok=True)
        # Initialize learning mixin attributes
        self._learning_loop = None
        self._memory_service = None
        self._agent_model = None

    def build_project(self, task: str, strategy: Dict = None) -> Dict[str, Any]:
        """
        Build an AI project based on task and strategy

        Args:
            task: Task description
            strategy: Optional strategy from spider research

        Returns:
            Build result with project details
        """
        try:
            logger.info(f"🚀 Building AI project: {task}")

            # If no strategy provided, research one
            if not strategy:
                strategies = research_ai_monetization_sync()
                if strategies:
                    strategy = strategies[0]  # Use first strategy
                else:
                    return {'success': False, 'error': 'No strategies found'}

            # Create project directory
            project_name = self._generate_project_name(strategy.get('title', 'ai_project'))
            project_path = self.project_workspace / project_name
            project_path.mkdir(exist_ok=True)

            logger.info(f"📁 Creating project at: {project_path}")

            # Determine project type
            strategy_type = strategy.get('strategy_type', 'ai_application')

            if strategy_type == 'content_generation':
                result = self._build_content_generator(project_path, strategy)
            elif strategy_type == 'ai_assistant':
                result = self._build_ai_assistant(project_path, strategy)
            else:
                result = self._build_generic_ai_app(project_path, strategy)

            if result['success']:
                result.update({
                    'strategy_used': strategy,
                    'estimated_revenue': strategy.get('potential_revenue', 'Unknown'),
                    'project_type': strategy_type,
                    'ready_to_launch': True
                })

                # Session 306: Learning Infrastructure Hooks
                self._record_learning_outcome(
                    result=result,
                    task=f"Build project: {task[:50]}",
                    context={
                        'project_type': strategy_type,
                        'strategy_title': strategy.get('title', ''),
                        'files_created': result.get('files_created', []),
                    },
                    spider_data_used=True
                )

                # Create memory for successful project builds
                self._create_execution_memory(
                    result=result,
                    task=f"Built {strategy_type} project",
                    memory_type="success",
                    importance=0.75  # High importance - successful project builds are valuable
                )

                # Share project building knowledge
                self._share_knowledge(
                    knowledge_type='project',
                    title=f"Successful {strategy_type} build: {strategy.get('title', 'project')[:40]}",
                    knowledge_value={
                        'project_type': strategy_type,
                        'files_created': result.get('files_created', []),
                        'monetization_ready': result.get('monetization_ready', False),
                        'estimated_revenue': strategy.get('potential_revenue', 'Unknown'),
                        'launch_command': result.get('launch_command', ''),
                    },
                    confidence=0.85
                )

            return result

        except Exception as e:
            logger.error(f"Failed to build project: {e}")
            # Session 306: Record failure for learning
            self._record_learning_outcome(
                result={'success': False, 'error': str(e)},
                task=f"Build project: {task[:50]} (failed)",
                context={'error': str(e)},
                spider_data_used=True
            )
            return {'success': False, 'error': str(e)}

    def _generate_project_name(self, title: str) -> str:
        """Generate project directory name"""
        import re
        name = re.sub(r'[^\w\s-]', '', title.lower())
        name = re.sub(r'[-\s]+', '_', name)
        return f"ai_project_{name}_{int(datetime.now().timestamp())}"

    def _build_content_generator(self, project_path: Path, strategy: Dict) -> Dict:
        """Build AI content generator"""
        try:
            # Create main application
            app_code = '''#!/usr/bin/env python3
"""
AI Content Generator
"""

import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

st.title('🖋️ AI Content Generator')

topic = st.text_input('Enter your topic:')
content_type = st.selectbox('Content Type', ['Blog Post', 'Social Media', 'Email'])

if st.button('Generate Content'):
    if topic and openai.api_key:
        try:
            response = openai.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "system", "content": "You are a professional content writer."},
                    {"role": "user", "content": f"Create a {content_type.lower()} about {topic}"}
                ],
                max_completion_tokens=500
            )

            content = response.choices[0].message.content
            st.write(content)

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning('Please enter a topic and configure OpenAI API key')

st.sidebar.write("💰 Revenue: $2,000-15,000/month")
'''
            (project_path / "content_generator.py").write_text(app_code)

            # Create requirements
            requirements = "streamlit==1.29.0\nopenai==1.52.0\npython-dotenv==1.0.0"
            (project_path / "requirements.txt").write_text(requirements)

            # Create README
            readme = f"""# {strategy.get('title', 'AI Content Generator')}

## Quick Start
1. `pip install -r requirements.txt`
2. Add OPENAI_API_KEY to .env file
3. `streamlit run content_generator.py`

## Revenue Potential
{strategy.get('potential_revenue', '$2,000-15,000/month')}

Generated by AI Project Builder
"""
            (project_path / "README.md").write_text(readme)

            return {
                'success': True,
                'project_path': str(project_path),
                'files_created': ['content_generator.py', 'requirements.txt', 'README.md'],
                'launch_command': 'streamlit run content_generator.py',
                'monetization_ready': True
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _build_ai_assistant(self, project_path: Path, strategy: Dict) -> Dict:
        """Build AI assistant"""
        try:
            # Create Flask API
            api_code = '''#!/usr/bin/env python3
"""
AI Assistant API
"""

from flask import Flask, request, jsonify
import openai
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message')

        response = openai.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": message}
            ],
            max_completion_tokens=300
        )

        return jsonify({
            'success': True,
            'reply': response.choices[0].message.content
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
            (project_path / "assistant_api.py").write_text(api_code)

            # Create requirements
            requirements = "flask==3.0.0\nopenai==1.52.0\npython-dotenv==1.0.0"
            (project_path / "requirements.txt").write_text(requirements)

            # Create README
            readme = f"""# {strategy.get('title', 'AI Assistant')}

## Quick Start
1. `pip install -r requirements.txt`
2. Add OPENAI_API_KEY to .env file
3. `python assistant_api.py`
4. POST to http://localhost:5000/chat

## Revenue Potential
{strategy.get('potential_revenue', '$3,000-25,000/month')}

Generated by AI Project Builder
"""
            (project_path / "README.md").write_text(readme)

            return {
                'success': True,
                'project_path': str(project_path),
                'files_created': ['assistant_api.py', 'requirements.txt', 'README.md'],
                'launch_command': 'python assistant_api.py',
                'monetization_ready': True
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _build_generic_ai_app(self, project_path: Path, strategy: Dict) -> Dict:
        """Build generic AI application"""
        try:
            # Create main app
            app_code = f'''#!/usr/bin/env python3
"""
{strategy.get('title', 'AI Application')}
"""

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def main():
    print("🤖 {strategy.get('title', 'AI Application')}")
    print("💰 Revenue Potential: {strategy.get('potential_revenue', 'Unknown')}")

    while True:
        user_input = input("\\nEnter your input (or 'quit'): ")
        if user_input.lower() == 'quit':
            break

        try:
            response = openai.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {{"role": "system", "content": "You are an AI assistant."}},
                    {{"role": "user", "content": user_input}}
                ],
                max_completion_tokens=300
            )

            print("\\nAI:", response.choices[0].message.content)

        except Exception as e:
            print(f"Error: {{e}}")

if __name__ == "__main__":
    main()
'''
            (project_path / "ai_app.py").write_text(app_code)

            # Create requirements
            requirements = "openai==1.52.0\npython-dotenv==1.0.0"
            (project_path / "requirements.txt").write_text(requirements)

            # Create README
            readme = f"""# {strategy.get('title', 'AI Application')}

## Quick Start
1. `pip install -r requirements.txt`
2. Add OPENAI_API_KEY to .env file
3. `python ai_app.py`

## Revenue Potential
{strategy.get('potential_revenue', 'Unknown')}

Generated by AI Project Builder
"""
            (project_path / "README.md").write_text(readme)

            return {
                'success': True,
                'project_path': str(project_path),
                'files_created': ['ai_app.py', 'requirements.txt', 'README.md'],
                'launch_command': 'python ai_app.py',
                'monetization_ready': True
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    # Test the builder
    builder = AIProjectBuilder()
    result = builder.build_project("build ai content generator")
    print(json.dumps(result, indent=2))