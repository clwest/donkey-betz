"""
Editor Agent - Session 864 Content Intelligence
================================================

Enhances content that has good quality and novelty but needs structural improvements.

This agent takes content marked as 'needs_enhancement' by the PublishGate and
improves its structure by adding:
- Engaging hooks/openings
- Better section headers
- Callouts and stat boxes
- Questions and engagement elements
- Better transitions between sections

Usage:
    from core.agents.editor_agent import EditorAgent

    agent = EditorAgent(user=request.user)
    result = agent.execute(
        task="Enhance blog structure",
        context={
            'blog_id': 'uuid-here',
            'focus_areas': ['hooks', 'headers', 'engagement']
        },
        scifi_context={},
        spider_context={}
    )
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig, OutputCategory, QualityTier

logger = logging.getLogger(__name__)


# Enhancement strategies
ENHANCEMENT_STRATEGIES = {
    'hooks': {
        'name': 'Opening Hooks',
        'description': 'Add compelling opening questions, statistics, or bold statements',
        'prompt_addition': '''
Add an attention-grabbing hook to the introduction. Options:
- Start with a provocative question
- Lead with a surprising statistic
- Open with a bold, contrarian statement
- Begin with a relatable scenario
'''
    },
    'headers': {
        'name': 'Section Headers',
        'description': 'Make section headers more engaging and varied',
        'prompt_addition': '''
Improve section headers to be:
- Action-oriented (start with verbs when possible)
- Benefit-focused (what will the reader learn?)
- Varied in structure (not all starting with the same word)
- Compelling enough to skim-read
'''
    },
    'engagement': {
        'name': 'Engagement Elements',
        'description': 'Add questions, stats, quotes, and callouts',
        'prompt_addition': '''
Add engagement elements throughout:
- Rhetorical questions that make readers think
- Key statistics or data points (with specific numbers)
- Relevant quotes (real or conceptual)
- Callout boxes for key takeaways
- Transition phrases between sections
'''
    },
    'structure': {
        'name': 'Content Structure',
        'description': 'Balance section lengths and improve flow',
        'prompt_addition': '''
Improve overall structure:
- Balance section lengths (none too short or too long)
- Add smooth transitions between sections
- Ensure logical flow from intro to conclusion
- Add a clear call-to-action at the end
'''
    },
    'conclusion': {
        'name': 'Strong Conclusion',
        'description': 'Create a memorable, actionable conclusion',
        'prompt_addition': '''
Strengthen the conclusion:
- Summarize key takeaways (3-5 bullet points)
- Include a clear call-to-action
- End with a memorable statement or question
- Connect back to the opening hook
'''
    }
}


class EditorAgent(BaseAgent):
    """
    Agent that enhances content structure for publishing readiness.

    Session 864: Created as part of Content Intelligence Layer improvements.
    Works with PublishGate to improve content marked as 'needs_enhancement'.
    """

    name = "EditorAgent"
    create_deliverable_on_schedule = True  # Fixed: was False (Session 1077), outputs were lost in AgentExecution
    description = "Enhances content structure, adds engagement elements, and polishes for publication"

    # Session 857: Output category configuration
    output_category = OutputCategory.CONTENT
    default_quality_tier = QualityTier.SILVER

    system_prompt = """You are an execution-focused product editor that ENFORCES INTENT.

You are NOT a grammar checker. You are a GATEKEEPER. Your job is to verify that the draft
actually delivers what the workspace brief asked for, and either FIX it or FAIL it.

## YOUR 5 NON-NEGOTIABLE CHECKS

### 1. TOPIC ALIGNMENT (MOST IMPORTANT)
Does EVERY section directly support the Topic/Focus from the brief?
- If a section drifts off-topic (e.g., brief says "AI agents for ops" but section covers "funding trends"), MARK IT FOR REMOVAL or REWRITE.
- Sections that are well-written but wrong for THIS article must be cut.

### 2. HOOK ENFORCEMENT
The brief's Distribution Hook must:
- Open the article (first paragraph)
- Be reinforced in at least 2 sections
- If the hook is missing or buried, REWRITE the intro to lead with it.

### 3. AUDIENCE ALIGNMENT
Every section must answer: "Would the target audience care about this?"
- If a section reads like an analyst report but the audience is solo devs → rewrite for operators
- If it reads like an investor memo but the audience is founders → make it actionable

### 4. ACTIONABILITY
Each section must include at least one CONCRETE takeaway the reader can act on.
- Not "consider your options" → instead "Set up X this week using Y"
- If a section is purely informational with no action → add one or flag for rewrite

### 5. EVIDENCE INTEGRITY
- Are claims tied to citations?
- Are there at least 2 real, cited examples?
- If claims are unsupported → flag them

## PASS / FAIL BEHAVIOR

After your 5 checks, give a verdict:

PASS (score >= 70): Polish the draft — improve hooks, headers, transitions, flow. Output the improved version.
FAIL (score < 70): Return a structured rejection with:
- Which checks failed
- Which sections to cut, rewrite, or add
- Specific instructions for the previous stage to fix

## OUTPUT FORMAT (JSON)

{
    "verdict": "PASS" or "FAIL",
    "score": 0-100,
    "checks": {
        "topic_alignment": {"pass": true/false, "issues": ["..."], "sections_to_cut": ["..."]},
        "hook_enforcement": {"pass": true/false, "issues": ["..."]},
        "audience_relevance": {"pass": true/false, "issues": ["..."]},
        "actionability": {"pass": true/false, "issues": ["..."]},
        "evidence_quality": {"pass": true/false, "issues": ["..."]}
    },
    "title": "Improved title",
    "intro": "Improved intro (hook-first)",
    "sections": [
        {"header": "...", "content": "..."}
    ],
    "conclusion": "Improved conclusion with CTA",
    "sections_removed": ["Section name — reason"],
    "sections_added": ["Section name — reason"],
    "changes_made": ["What changed and why"]
}

If verdict is FAIL, still include the checks and specific fix instructions but DO NOT produce
a full rewrite — that wastes tokens. Just explain what needs to change and who should fix it.

CRITICAL: Read the workspace brief (topic, audience, tone, hook) BEFORE reading the draft.
The brief is your rubric. The draft is what you're grading."""

    def __init__(self, user=None, **kwargs):
        """Initialize the EditorAgent."""
        super().__init__(user=user, **kwargs)
        self.enhancements_applied = []

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute content enhancement.

        Args:
            task: Enhancement task description
            context: Must include either 'blog_id' or 'content' dict
            scifi_context: Sci-fi context (optional)
            spider_context: Spider context (optional)

        Returns:
            AgentResult with enhanced content
        """
        start_time = time.time()

        try:
            # Get content to enhance
            blog = None
            content = context.get('content')
            blog_id = context.get('blog_id')

            if blog_id and not content:
                # Load from database
                from core.models_unified_system import SelfBlog
                try:
                    blog = SelfBlog.objects.get(id=blog_id)
                    content = {
                        'title': blog.title,
                        'intro': blog.intro,
                        'sections': blog.sections or [],
                        'conclusion': blog.conclusion,
                        'meta_description': blog.meta_description,
                    }
                except SelfBlog.DoesNotExist:
                    return AgentResult(
                        success=False,
                        message=f"Blog not found: {blog_id}",
                        error=f"Blog not found: {blog_id}",
                        agent_name=self.name,
                    )

            if not content:
                return AgentResult(
                    success=False,
                    message="No content provided. Include 'blog_id' or 'content' in context.",
                    error="No content provided. Include 'blog_id' or 'content' in context.",
                    agent_name=self.name,
                )

            # Determine focus areas
            focus_areas = context.get('focus_areas', ['hooks', 'headers', 'engagement', 'structure', 'conclusion'])

            # Get workspace brief — this is the rubric for the 5 quality checks
            workspace_brief = context.get('workspace_brief', {})
            if not isinstance(workspace_brief, dict):
                workspace_brief = {}

            # Build enhancement prompt with brief as rubric
            enhancement_prompt = self._build_enhancement_prompt(content, focus_areas, workspace_brief)

            # Call LLM for enhancement
            enhanced_content = self._enhance_with_llm(enhancement_prompt, content)

            if not enhanced_content:
                return AgentResult(
                    success=False,
                    message="Failed to enhance content (LLM returned unparseable response)",
                    error="Failed to enhance content",
                    agent_name=self.name,
                )

            # Optionally save back to blog
            if blog and context.get('save', False):
                self._save_enhanced_blog(blog, enhanced_content)

            execution_time = int((time.time() - start_time) * 1000)

            # Session 1006: Persist output to Deliverable
            self._save_to_deliverable(
                title=f"Edited Content: {content.get('title', task[:80])}",
                content=enhanced_content.get('enhanced_body', '') if isinstance(enhanced_content, dict) else str(enhanced_content),
                deliverable_type='edited_content',
                category='Content Editing',
                tags=['editing'] + focus_areas[:3],
                metadata={'task': task[:200], 'focus_areas': focus_areas, 'blog_id': str(blog_id) if blog_id else None},
            )

            return AgentResult(
                success=True,
                message=f"Enhanced content with focus on: {', '.join(focus_areas)}",
                data={
                    'enhanced_content': enhanced_content,
                    'original_title': content.get('title'),
                    'changes_made': enhanced_content.get('changes_made', []),
                    'focus_areas': focus_areas,
                    'blog_id': str(blog_id) if blog_id else None,
                    'saved': context.get('save', False),
                },
                agent_name=self.name,
                execution_time_ms=execution_time,
                output_category=OutputCategory.CONTENT.value,
                quality_tier=QualityTier.SILVER.value,
            )

        except Exception as e:
            logger.exception(f"EditorAgent error: {e}")
            return AgentResult(
                success=False,
                message=f"EditorAgent error: {e}",
                error=str(e),
                agent_name=self.name,
                execution_time_ms=int((time.time() - start_time) * 1000),
            )

    def _build_enhancement_prompt(self, content: Dict[str, Any], focus_areas: List[str], workspace_brief: Dict[str, Any] = None) -> str:
        """Build the enhancement prompt with the workspace brief as the rubric."""
        brief = workspace_brief or {}
        prompt_parts = []

        # THE RUBRIC — brief comes FIRST so the editor knows what to grade against
        if brief:
            prompt_parts.append("## WORKSPACE BRIEF (Your Rubric — grade the draft against this)\n")
            if brief.get('topic'):
                prompt_parts.append(f"**Topic/Focus:** {brief['topic']}\n")
            if brief.get('audience'):
                prompt_parts.append(f"**Target Audience:** {brief['audience']}\n")
            if brief.get('tone'):
                prompt_parts.append(f"**Tone:** {brief['tone']}\n")
            if brief.get('distribution_hook'):
                prompt_parts.append(f"**Distribution Hook (must appear in intro + 2 sections):** {brief['distribution_hook']}\n")
            if brief.get('focus_areas') and isinstance(brief['focus_areas'], list):
                prompt_parts.append(f"**Focus Areas:** {', '.join(brief['focus_areas'])}\n")
            if brief.get('notes'):
                prompt_parts.append(f"**Notes:** {brief['notes']}\n")
            prompt_parts.append("\n---\n\n")

        prompt_parts.append("## DRAFT TO REVIEW\n\n")

        # Handle content as either dict (structured) or string (plain text)
        if isinstance(content, dict):
            prompt_parts.append(f"Title: {content.get('title', 'Untitled')}\n\n")
            if content.get('intro'):
                prompt_parts.append(f"{content['intro']}\n\n")
            for section in content.get('sections', []):
                if isinstance(section, dict):
                    prompt_parts.append(f"### {section.get('header', section.get('heading', 'Section'))}\n")
                    prompt_parts.append(f"{section.get('content', section.get('body', ''))}\n\n")
                elif isinstance(section, str):
                    prompt_parts.append(f"{section}\n\n")
            if content.get('conclusion'):
                prompt_parts.append(f"Conclusion:\n{content['conclusion']}\n\n")
        elif isinstance(content, str):
            prompt_parts.append(f"{content}\n\n")

        prompt_parts.append("""
## YOUR TASK

Run your 5 non-negotiable checks against the brief above:
1. **Topic Alignment** — Does every section support the Topic/Focus? Cut off-topic sections.
2. **Hook Enforcement** — Is the Distribution Hook in the intro and reinforced in 2+ sections?
3. **Audience Relevance** — Would the target audience care about each section?
4. **Actionability** — Does each section have a concrete takeaway?
5. **Evidence Quality** — Are claims cited? At least 2 real examples?

Then give your verdict (PASS/FAIL) and return the JSON output.
If PASS: include the improved/polished content.
If FAIL: explain what needs to change and which stage should fix it.
""")

        return ''.join(prompt_parts)

    def _enhance_with_llm(self, prompt: str, original_content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call LLM to enhance content."""
        try:
            # Session 1033: Use LLMProviderRegistry (not nonexistent llm_service)
            from core.services.llm_provider_registry import LLMProviderRegistry, LLMRequest

            registry = LLMProviderRegistry()
            request = LLMRequest(
                prompt=prompt,
                system_prompt=self.system_prompt,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7,
            )

            response = registry.complete('openai', 'gpt-5.2', request)

            if not response.success:
                logger.error(f"LLM enhancement failed: {response.error}")
                return None

            response_text = response.content or ''

            # Extract JSON from response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()

            enhanced = json.loads(response_text)

            # Ensure required fields
            if 'title' not in enhanced:
                enhanced['title'] = original_content.get('title')
            if 'sections' not in enhanced:
                enhanced['sections'] = original_content.get('sections', [])
            if 'changes_made' not in enhanced:
                enhanced['changes_made'] = ['Content enhanced']

            return enhanced

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            return None

    def _save_enhanced_blog(self, blog, enhanced_content: Dict[str, Any]) -> None:
        """Save enhanced content back to blog."""
        try:
            if enhanced_content.get('title'):
                blog.title = enhanced_content['title']
            if enhanced_content.get('intro'):
                blog.intro = enhanced_content['intro']
            if enhanced_content.get('sections'):
                blog.sections = enhanced_content['sections']
            if enhanced_content.get('conclusion'):
                blog.conclusion = enhanced_content['conclusion']

            # Mark as pending review after enhancement
            blog.status = 'pending_review'

            # Add note about enhancement
            enhancement_note = f"Enhanced by EditorAgent on {datetime.now().isoformat()}"
            if enhanced_content.get('changes_made'):
                enhancement_note += f". Changes: {', '.join(enhanced_content['changes_made'][:5])}"

            if blog.gate_notes:
                blog.gate_notes += f"; {enhancement_note}"
            else:
                blog.gate_notes = enhancement_note

            blog.save()
            logger.info(f"Saved enhanced content to blog {blog.id}")

        except Exception as e:
            logger.error(f"Failed to save enhanced blog: {e}")
            raise


# Convenience function for batch enhancement
def enhance_blog(blog_id: str, focus_areas: List[str] = None, save: bool = False) -> AgentResult:
    """
    Enhance a blog by ID.

    Args:
        blog_id: UUID of the blog to enhance
        focus_areas: List of areas to focus on (default: all)
        save: Whether to save changes to database

    Returns:
        AgentResult with enhanced content
    """
    agent = EditorAgent()
    return agent.execute(
        task="Enhance blog structure",
        context={
            'blog_id': blog_id,
            'focus_areas': focus_areas or ['hooks', 'headers', 'engagement', 'structure', 'conclusion'],
            'save': save,
        },
        scifi_context={},
        spider_context={},
    )


def enhance_all_needing_enhancement(limit: int = 10, save: bool = False) -> List[Dict[str, Any]]:
    """
    Enhance all blogs marked as needs_enhancement.

    Args:
        limit: Maximum number of blogs to enhance
        save: Whether to save changes to database

    Returns:
        List of enhancement results
    """
    from core.models_unified_system import SelfBlog

    blogs = SelfBlog.objects.filter(status='needs_enhancement')[:limit]
    results = []

    agent = EditorAgent()

    for blog in blogs:
        result = agent.execute(
            task=f"Enhance blog: {blog.title[:50]}",
            context={
                'blog_id': str(blog.id),
                'save': save,
            },
            scifi_context={},
            spider_context={},
        )
        results.append({
            'blog_id': str(blog.id),
            'title': blog.title[:60],
            'success': result.success,
            'changes': result.data.get('changes_made', []) if result.success else [],
            'error': result.error,
        })

    return results
