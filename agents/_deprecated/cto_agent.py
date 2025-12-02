"""
CTO Agent - Session 98 (Read-Only Phase 1)
===========================================

The CTO Agent is a specialized agent that understands the entire codebase,
can analyze architecture, and coordinate with other agents.

**Phase 1: Read-Only Analysis & Planning**
- ✅ Codebase mapping and understanding
- ✅ Feature analysis and recommendations
- ✅ Agent coordination
- ✅ Documentation analysis
- ❌ NO file writes or destructive operations yet

Philosophy: Deep system understanding → Intelligent recommendations → Safe planning

Features:
- Complete codebase understanding (all files, all relationships)
- Code analysis and quality assessment
- Safe planning for implementations (no execution yet)
- Documentation analysis (read-only)
- Agent coordination for complex tasks

Example Usage:
    cto_agent = CTOAgent(user=request.user)

    # Analyze feature
    analysis = cto_agent.analyze_feature("AI Assistant voice commands")

    # Plan implementation (returns plan, doesn't execute)
    plan = cto_agent.implement_feature(
        description="Add rate limiting to all API endpoints",
        approach="decorator_pattern"
    )

    # Analyze documentation (read-only)
    doc_analysis = cto_agent.sync_documentation(scope="all_agents")

    # Coordinate agents
    result = cto_agent.coordinate_agents(
        task="Create complete brand package",
        required_agents=["CreativeDirectorAgent", "BrandStyleAgent"]
    )
"""

from __future__ import annotations

import os
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from openai import OpenAI

from agents.models import UnifiedAgentTemplate, AgentExecution, AgentSpecialization
from intelligence.shared_memory import AgentMemoryInterface

logger = logging.getLogger(__name__)
User = get_user_model()


class CTOAgent:
    """
    CTO Agent - Deep codebase understanding and planning (Read-Only Phase 1)

    Phase 1 Capabilities:
    - Analyze features and architecture
    - Plan implementations (without executing)
    - Coordinate with other agents
    - Analyze documentation gaps

    Phase 2 (Future):
    - Execute safe code changes
    - Update documentation automatically
    - Refactor code with approval
    """

    def __init__(self, user: Optional[User] = None):
        """
        Initialize CTO Agent.

        Args:
            user: User who initiated the agent (optional)
        """
        self.user = user
        self.agent_name = 'CTOAgent'

        # Initialize OpenAI client for reasoning
        self.client = OpenAI()

        # Initialize memory interface for knowledge storage
        self.memory = AgentMemoryInterface(agent_id='cto_agent')

        # Get or create agent template
        self.template = self._get_or_create_template()

        # Cache codebase structure on initialization
        self.codebase_map = self._build_codebase_map()

        logger.info(f"🏗️ CTO Agent initialized (READ-ONLY MODE) for user: {user.username if user else 'system'}")

    def _get_or_create_template(self) -> UnifiedAgentTemplate:
        """Get or create CTOAgent template in database"""
        try:
            agent = UnifiedAgentTemplate.objects.get(name=self.agent_name)
            logger.debug(f"Using existing CTOAgent template: {agent.id}")
            return agent

        except UnifiedAgentTemplate.DoesNotExist:
            # Create new CTOAgent template
            agent = UnifiedAgentTemplate.objects.create(
                name=self.agent_name,
                display_name='CTO Agent (System Architect)',
                description=(
                    'Deep codebase understanding agent that analyzes architecture, '
                    'plans implementations, and coordinates platform evolution. '
                    'Phase 1: Read-only analysis and planning.'
                ),
                specialization=AgentSpecialization.TECHNICAL,
                capabilities=[
                    'codebase_analysis',
                    'architectural_planning',
                    'documentation_analysis',
                    'agent_coordination',
                    'implementation_planning'
                ],
                routing_keywords=[
                    'cto', 'architecture', 'codebase', 'analyze', 'plan',
                    'technical', 'system', 'infrastructure', 'review',
                    'code review', 'analyze docs', 'coordinate'
                ],
                required_tools=[
                    'file_read', 'code_analysis', 'gpt-5-mini',
                    'agent_query_protocol', 'memory_interface'
                ],
                system_prompt=(
                    "You are the CTO Agent (Phase 1: Read-Only Analysis). You have deep understanding of the "
                    "Unified Donkey Betz Platform codebase. You know:\n"
                    "- All 34 AI features and their implementations\n"
                    "- Complete agent ecosystem (10 creative workflow agents + infrastructure)\n"
                    "- All 6 external API integrations (Stability AI, Runway ML, ElevenLabs, Replicate, OpenAI, DaVinci)\n"
                    "- Database schema and models\n"
                    "- Architecture patterns and conventions\n\n"
                    "Phase 1 Capabilities:\n"
                    "- Analyze code quality and architecture (READ-ONLY)\n"
                    "- Plan implementations (PLANNING ONLY - no execution)\n"
                    "- Analyze documentation gaps (READ-ONLY)\n"
                    "- Coordinate with other agents for complex tasks\n\n"
                    "You DO NOT:\n"
                    "- Write or modify files (Phase 2)\n"
                    "- Execute code changes (Phase 2)\n"
                    "- Make destructive changes (Phase 2)\n\n"
                    "You prioritize:\n"
                    "- Safety (analysis only, no changes)\n"
                    "- Quality (maintain 99.9% reality score)\n"
                    "- Clarity (detailed plans and recommendations)\n"
                    "- Coordination (work with other agents)"
                ),
                llm_provider='openai',
                llm_model='gpt-5-mini',
                llm_config={
                    'reasoning_effort': 'high',  # Maximum reasoning for CTO decisions
                    'max_completion_tokens': 4000
                },
                tool_integrations={
                    'file_operations': {
                        'enabled': True,
                        'read': True,       # Can read files
                        'analyze': True,    # Can analyze code
                        'write': False,     # Phase 2
                        'edit': False       # Phase 2
                    },
                    'database_access': {
                        'enabled': True,
                        'schema_query': True,
                        'read_models': True,
                        'modify_schema': False  # Phase 2
                    },
                    'agent_coordination': {
                        'enabled': True,
                        'can_query_agents': True,
                        'can_coordinate': True
                    }
                },
                is_active=True,
                metadata={
                    'phase': 'read_only_analysis',
                    'codebase_scope': 'full',
                    'knowledge_domains': [
                        'stability_ai', 'runway_ml', 'elevenlabs',
                        'replicate', 'openai', 'davinci_resolve',
                        'agent_system', 'database', 'frontend'
                    ],
                    'created_by': 'session_98',
                    'version': '1.0.0-readonly'
                }
            )

            logger.info(f"✅ Created new CTOAgent template (READ-ONLY): {agent.id}")
            return agent

    def _build_codebase_map(self) -> Dict[str, Any]:
        """
        Build complete map of codebase structure.

        This is a READ-ONLY operation that scans the codebase and creates
        an index of all files, directories, and key components.
        """
        try:
            base_path = Path(settings.BASE_DIR)

            codebase_map = {
                'base_path': str(base_path),
                'directories': {},
                'file_count': 0,
                'key_files': [],
                'total_lines': 0,
                'last_scanned': datetime.now().isoformat()
            }

            # Map key directories
            key_dirs = [
                'ai_core', 'content', 'core', 'agents',
                'intelligence', 'docs', 'scripts'
            ]

            for dir_name in key_dirs:
                dir_path = base_path / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    # Count Python files
                    py_files = list(dir_path.rglob('*.py'))

                    # Get file info (first 100 files to avoid overwhelming)
                    file_list = []
                    for f in py_files[:100]:
                        try:
                            stats = f.stat()
                            file_list.append({
                                'path': str(f.relative_to(base_path)),
                                'size': stats.st_size,
                                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                            })
                        except Exception as e:
                            logger.warning(f"Could not stat {f}: {e}")

                    codebase_map['directories'][dir_name] = {
                        'path': str(dir_path),
                        'file_count': len(py_files),
                        'files': file_list
                    }
                    codebase_map['file_count'] += len(py_files)

            # Identify key files (always include these in analysis)
            key_files = [
                'core/views_image.py',           # AI Assistant integration (5800+ lines)
                'content/image_generation.py',   # Stability AI (2000+ lines)
                'content/video_provider.py',     # Runway ML (1500+ lines)
                'content/elevenlabs_provider.py', # ElevenLabs audio
                'agents/models.py',              # Agent system models
                'ai_core/templates/ai_image_studio.html', # Frontend
                'agents/video_agent.py',         # Video agent
                'agents/audio_agent.py',         # Audio agent
                'intelligence/agent_query_protocol.py', # Agent communication
                'CLAUDE.md',                     # Main documentation
                '00-START-NEXT-SESSION.md'       # Current priorities
            ]

            for file_path in key_files:
                full_path = base_path / file_path
                if full_path.exists():
                    try:
                        stats = full_path.stat()
                        # Count lines
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                        except:
                            lines = 0

                        codebase_map['key_files'].append({
                            'path': file_path,
                            'size': stats.st_size,
                            'lines': lines,
                            'exists': True,
                            'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
                        })
                        codebase_map['total_lines'] += lines
                    except Exception as e:
                        logger.warning(f"Could not analyze {file_path}: {e}")
                        codebase_map['key_files'].append({
                            'path': file_path,
                            'exists': False,
                            'error': str(e)
                        })

            logger.info(
                f"📊 Codebase map built: {codebase_map['file_count']} Python files, "
                f"{codebase_map['total_lines']} lines in key files"
            )

            # Store codebase map in memory
            self.memory.remember(
                'codebase_map',
                codebase_map
            )

            return codebase_map

        except Exception as e:
            logger.error(f"❌ Error building codebase map: {e}", exc_info=True)
            return {
                'error': str(e),
                'directories': {},
                'file_count': 0,
                'key_files': []
            }

    def analyze_feature(self, feature_name: str, scope: str = "feature") -> Dict[str, Any]:
        """
        Analyze a feature across the entire codebase.

        READ-ONLY operation that uses GPT-5-mini to deeply analyze a feature,
        its implementation, dependencies, and potential improvements.

        Args:
            feature_name: Name of feature to analyze
            scope: Scope of analysis ('feature', 'integration', 'agent', 'full_system')

        Returns:
            Complete analysis with files, dependencies, and recommendations
        """
        logger.info(f"🔍 Analyzing feature: {feature_name} (scope: {scope})")

        try:
            # Build context about the codebase
            context = self._build_analysis_context(feature_name, scope)

            # Use GPT-5-mini for deep reasoning
            analysis_prompt = f"""
Analyze the '{feature_name}' feature in the Unified Donkey Betz Platform.

Context about the platform:
- 34 AI features across 6 API integrations (Stability AI, Runway ML, ElevenLabs, Replicate, OpenAI, DaVinci)
- 10-agent creative workflow ecosystem with Redis-based communication
- Django backend + vanilla JavaScript frontend
- 99.9% reality score, 93% launch readiness

Codebase structure:
{json.dumps(self.codebase_map['directories'], indent=2)}

Key files ({len(self.codebase_map['key_files'])} files):
{json.dumps([f['path'] for f in self.codebase_map['key_files']], indent=2)}

Analysis scope: {scope}

Provide a comprehensive analysis including:

1. **Implementation Overview**
   - Which files implement this feature?
   - How is it structured?
   - What patterns are used?

2. **Dependencies & Integrations**
   - What APIs or services does it depend on?
   - Which other features does it integrate with?
   - Which agents are involved (if any)?

3. **Current Status**
   - Is it working, broken, or incomplete?
   - What's the quality of the implementation?
   - Any known issues or technical debt?

4. **Potential Improvements**
   - What could be optimized?
   - What features could be added?
   - What refactoring would help?

5. **Risk Areas**
   - Security concerns?
   - Performance bottlenecks?
   - Maintenance challenges?

6. **Recommendations**
   - Priority improvements (high/medium/low)
   - Quick wins vs long-term projects
   - Specific action items

Be specific, technical, and actionable. Reference actual file paths and line numbers when possible.
"""

            # Session 313: Use GPT-5-mini with Responses API
            full_input = f"{self.template.system_prompt}\n\n{analysis_prompt}"

            response = self.client.responses.create(
                model="gpt-5-mini",
                input=full_input,
                reasoning={"effort": "high"},
                text={"verbosity": "medium"},
                max_output_tokens=3000
            )

            analysis_text = response.output_text

            # Store analysis in memory
            analysis_data = {
                'feature_name': feature_name,
                'scope': scope,
                'analysis': analysis_text,
                'analyzed_at': datetime.now().isoformat(),
                'analyzed_by': self.user.username if self.user else 'system',
                'codebase_snapshot': {
                    'file_count': self.codebase_map['file_count'],
                    'key_files': len(self.codebase_map['key_files'])
                }
            }

            memory_key = f"feature_analysis_{feature_name.lower().replace(' ', '_')}"
            self.memory.remember(
                memory_key,
                analysis_data
            )

            logger.info(f"✅ Analysis complete for: {feature_name}")

            return {
                'feature_name': feature_name,
                'scope': scope,
                'analysis': analysis_text,
                'status': 'complete',
                'analyzed_at': analysis_data['analyzed_at']
            }

        except Exception as e:
            logger.error(f"❌ Feature analysis failed: {e}", exc_info=True)
            return {
                'feature_name': feature_name,
                'status': 'failed',
                'error': str(e)
            }

    def _build_analysis_context(self, feature_name: str, scope: str) -> Dict[str, Any]:
        """Build context for feature analysis"""
        # This is a helper that could be expanded to search specific files
        # For now, returns basic codebase info
        return {
            'codebase_map': self.codebase_map,
            'feature_name': feature_name,
            'scope': scope
        }

    def implement_feature(
        self,
        description: str,
        approach: str,
        files_to_modify: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Plan a feature implementation.

        **PHASE 1: PLANNING ONLY - NO EXECUTION**

        This method creates a detailed implementation plan but does NOT
        execute any code changes. It returns a plan that a human can review
        and approve before execution in Phase 2.

        Args:
            description: What to implement
            approach: How to implement (e.g., 'decorator_pattern', 'new_agent')
            files_to_modify: Optional list of files to modify

        Returns:
            Implementation plan (NO EXECUTION)
        """
        logger.info(f"📋 Planning implementation: {description}")
        logger.info(f"⚠️ PHASE 1: PLANNING ONLY - NO FILES WILL BE MODIFIED")

        try:
            # Create execution record (for planning)
            execution = AgentExecution.objects.create(
                template=self.template,
                user=self.user,
                task_description=f"[PLAN ONLY] {description}",
                status='running',
                input_data={
                    'description': description,
                    'approach': approach,
                    'files_to_modify': files_to_modify,
                    'phase': 'planning_only'
                }
            )

            # Use GPT-5-mini to create implementation plan
            planning_prompt = f"""
Create a detailed implementation plan for: {description}

Approach: {approach}
Suggested files to modify: {files_to_modify or 'TBD'}

Platform context:
- Django backend with 34 AI features
- 10-agent creative workflow system
- Redis for state management, PostgreSQL for data
- Production-ready with 99.9% reality score

Create a comprehensive plan including:

1. **Files to Modify**
   - Exact file paths
   - What changes in each file
   - Line number estimates if possible

2. **Code Changes Required**
   - Specific functions/classes to add or modify
   - Code snippets or pseudocode
   - Import statements needed

3. **Testing Strategy**
   - What tests should be added
   - How to verify the implementation works
   - Edge cases to consider

4. **Documentation Updates**
   - Which docs need updating
   - What information to add
   - Examples to include

5. **Risks & Considerations**
   - What could go wrong
   - Dependencies to be aware of
   - Performance implications

6. **Step-by-Step Implementation**
   - Ordered list of steps
   - Estimated time for each step
   - Checkpoints for verification

⚠️ IMPORTANT: This is a PLAN ONLY. No files will be modified yet.
The plan should be detailed enough that a developer can execute it safely.
"""

            # Session 313: Use GPT-5-mini with Responses API
            system_prompt = self.template.system_prompt + "\n\nYou are creating an implementation PLAN. Be thorough and specific."
            full_input = f"{system_prompt}\n\n{planning_prompt}"

            response = self.client.responses.create(
                model="gpt-5-mini",
                input=full_input,
                reasoning={"effort": "high"},
                text={"verbosity": "medium"},
                max_output_tokens=3500
            )

            implementation_plan = response.output_text

            # Store plan in memory
            plan_data = {
                'description': description,
                'approach': approach,
                'plan': implementation_plan,
                'created_at': datetime.now().isoformat(),
                'created_by': self.user.username if self.user else 'system',
                'execution_id': execution.id,
                'phase': 'planning_only',
                'files_to_modify': files_to_modify
            }

            # Store plan in memory
            memory_key = f"implementation_plan_{execution.id}"
            self.memory.remember(memory_key, plan_data)

            # Update execution record
            execution.status = 'completed'
            execution.result_data = {
                'plan': implementation_plan,
                'status': 'plan_created',
                'phase': 'planning_only',
                'note': 'No files were modified. This is a plan only.'
            }
            execution.save()

            logger.info(f"✅ Implementation plan created: {execution.id}")

            return {
                'execution_id': execution.id,
                'plan': implementation_plan,
                'status': 'plan_created',
                'phase': 'planning_only',
                'note': '⚠️ This is a PLAN ONLY. No files were modified.',
                'next_step': 'Review plan, then execute in Phase 2 (with approval)'
            }

        except Exception as e:
            logger.error(f"❌ Implementation planning failed: {e}", exc_info=True)
            if 'execution' in locals():
                execution.status = 'failed'
                execution.error_message = str(e)
                execution.save()

            return {
                'status': 'failed',
                'error': str(e),
                'phase': 'planning_only'
            }

    def sync_documentation(
        self,
        scope: str = 'changed_files'
    ) -> Dict[str, Any]:
        """
        Analyze documentation and identify gaps.

        **PHASE 1: ANALYSIS ONLY - NO WRITES**

        This method analyzes documentation and identifies what's outdated
        or missing, but does NOT modify any files. It returns recommendations
        for documentation updates.

        Args:
            scope: 'changed_files', 'all_agents', 'all_features', or 'full'

        Returns:
            Documentation analysis and recommendations (NO MODIFICATIONS)
        """
        logger.info(f"📝 Analyzing documentation: {scope}")
        logger.info(f"⚠️ PHASE 1: ANALYSIS ONLY - NO FILES WILL BE MODIFIED")

        try:
            # Analyze current documentation state
            doc_analysis_prompt = f"""
Analyze the documentation state for the Unified Donkey Betz Platform.

Scope: {scope}

Platform state:
- 34 AI features (13 Stability AI, 5 Runway ML, 2 ElevenLabs, 3 Character Training, 5 OpenAI, 6 UI/System)
- 10 active creative workflow agents
- 6 external API integrations
- 99.9% reality score, 93% launch readiness

Key documentation files in codebase:
{json.dumps([f['path'] for f in self.codebase_map['key_files'] if 'md' in f['path'].lower()], indent=2)}

Documentation directories:
- docs/features/ - Feature-specific documentation
- docs/apis/ - API integration documentation
- docs/agents/ - Agent system documentation
- docs/architecture/ - System architecture
- docs/sessions/ - Session notes

Analyze:

1. **Current Documentation Coverage**
   - What's well documented?
   - What's missing documentation?
   - What's outdated?

2. **Documentation Quality**
   - Are examples up-to-date?
   - Are API references accurate?
   - Are there dead links or references?

3. **Gaps & Missing Docs**
   - Features without documentation
   - Agents without documentation
   - APIs without documentation

4. **Recommendations**
   - High priority docs to create/update
   - Medium priority improvements
   - Nice-to-have additions

5. **Documentation Update Plan**
   - Which files need updating
   - What information to add
   - Suggested structure for new docs

⚠️ IMPORTANT: This is ANALYSIS ONLY. No files will be modified.
Provide specific file paths and content recommendations.
"""

            # Session 313: Use GPT-5-mini with Responses API
            system_prompt = "You are a technical documentation expert analyzing documentation coverage and quality."
            full_input = f"{system_prompt}\n\n{doc_analysis_prompt}"

            response = self.client.responses.create(
                model="gpt-5-mini",
                input=full_input,
                reasoning={"effort": "medium"},
                text={"verbosity": "medium"},
                max_output_tokens=3000
            )

            doc_analysis = response.output_text

            # Store analysis in memory
            analysis_data = {
                'scope': scope,
                'analysis': doc_analysis,
                'analyzed_at': datetime.now().isoformat(),
                'analyzed_by': self.user.username if self.user else 'system',
                'phase': 'analysis_only'
            }

            # Store analysis in memory
            memory_key = f"documentation_analysis_{scope}"
            self.memory.remember(memory_key, analysis_data)

            logger.info(f"✅ Documentation analysis complete: {scope}")

            return {
                'scope': scope,
                'analysis': doc_analysis,
                'status': 'complete',
                'phase': 'analysis_only',
                'note': '⚠️ This is ANALYSIS ONLY. No files were modified.',
                'next_step': 'Review recommendations, then update docs in Phase 2'
            }

        except Exception as e:
            logger.error(f"❌ Documentation analysis failed: {e}", exc_info=True)
            return {
                'scope': scope,
                'status': 'failed',
                'error': str(e),
                'phase': 'analysis_only'
            }

    def coordinate_agents(
        self,
        task: str,
        required_agents: List[str]
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents to accomplish a complex task.

        This uses the Agent Query Protocol to communicate with other agents
        and synthesize their contributions into a unified solution.

        Args:
            task: Task description
            required_agents: List of agent names to coordinate

        Returns:
            Coordination results and synthesized solution
        """
        logger.info(f"🎯 Coordinating agents for: {task}")
        logger.info(f"Required agents: {', '.join(required_agents)}")

        try:
            # For Phase 1, we'll create a coordination plan
            # In Phase 2, we can actually query the agents via AgentQueryProtocol

            coordination_prompt = f"""
Create a coordination plan for the following task:

Task: {task}

Required agents: {', '.join(required_agents)}

Available agents in the ecosystem:
- WorkflowCoordinatorAgent: Master orchestrator for complete workflows
- CreativeDirectorAgent: Multi-option generation with learning
- TemplateManagerAgent: Save and reuse templates
- BrandStyleAgent: FLUX LoRA brand training
- VersionControlAgent: Generation history tracking
- EditingOrchestratorAgent: Multi-step image editing
- IterationAgent: Intelligent refinement
- ReferenceLibraryAgent: Reference management
- AudioAgent: Audio generation (ElevenLabs)
- VideoAgent: Video editing (DaVinci/ffmpeg)

Create a coordination plan including:

1. **Agent Responsibilities**
   - What each agent will contribute
   - Order of execution
   - Dependencies between agents

2. **Data Flow**
   - What data passes between agents
   - How results are combined
   - Where intermediate results are stored

3. **Expected Outcomes**
   - What the final deliverable will be
   - Success criteria
   - Validation steps

4. **Execution Steps**
   - Step-by-step workflow
   - Agent interactions at each step
   - Checkpoints for verification

5. **Integration Points**
   - How agent outputs combine
   - Conflict resolution if needed
   - Final synthesis approach

Be specific about agent capabilities and realistic about what each can deliver.
"""

            # Session 313: Use GPT-5-mini with Responses API
            full_input = f"{self.template.system_prompt}\n\n{coordination_prompt}"

            response = self.client.responses.create(
                model="gpt-5-mini",
                input=full_input,
                reasoning={"effort": "high"},
                text={"verbosity": "medium"},
                max_output_tokens=2500
            )

            coordination_plan = response.output_text

            # Store coordination plan
            plan_data = {
                'task': task,
                'required_agents': required_agents,
                'coordination_plan': coordination_plan,
                'created_at': datetime.now().isoformat(),
                'created_by': self.user.username if self.user else 'system',
                'phase': 'planning'
            }

            # Store coordination plan in memory
            task_id = task.lower().replace(' ', '_')[:50]
            memory_key = f"agent_coordination_{task_id}"
            self.memory.remember(memory_key, plan_data)

            logger.info(f"✅ Agent coordination plan created: {task}")

            return {
                'task': task,
                'required_agents': required_agents,
                'coordination_plan': coordination_plan,
                'status': 'plan_created',
                'phase': 'planning',
                'note': 'Phase 1: Coordination plan created. Phase 2 will execute actual agent queries.',
                'next_step': 'Review plan, then execute coordination in Phase 2'
            }

        except Exception as e:
            logger.error(f"❌ Agent coordination failed: {e}", exc_info=True)
            return {
                'task': task,
                'status': 'failed',
                'error': str(e)
            }
