"""Session 1092: BaseAgent._render_agent_output_markdown regression tests.

Locks in the shared content renderer that replaces the
"content=result.message → fails 300-char gate → no Deliverable saved"
pattern across 10 previously-broken agents (video, audio, image editing,
3D, character training, trained creation, voice critic, code generator,
code review, content strategy).
"""

from django.test import SimpleTestCase

from core.agents.base_agent import BaseAgent


class _BareAgent(BaseAgent):
    """Minimal concrete BaseAgent subclass for helper-method tests."""

    name = "TestAgent"
    system_prompt = "test"

    def execute(self, task, context, scifi_context=None, spider_context=None):
        raise NotImplementedError('Not used in renderer tests')


class TestRenderAgentOutputMarkdown(SimpleTestCase):

    def setUp(self):
        # BaseAgent's __init__ hits user resolution and several services we
        # don't need for pure-Python renderer testing. Build an instance
        # without running __init__, then call the unbound method bound to it.
        self.agent = _BareAgent.__new__(_BareAgent)
        self.render = self.agent._render_agent_output_markdown

    def test_passes_300_char_gate_with_realistic_media_input(self):
        """The canary v5 scenario: media agent with short summary + tool_calls
        + extra artifact metadata must render >300 chars."""
        output = self.render(
            task="Generate a 15-second promo video for a sports betting app",
            summary="Video generation started: 15s video from prompt 'sports betting app promo...'",
            tool_calls=[
                {'tool': 'generate_video', 'arguments': {'prompt': 'sports app promo', 'duration': 15}},
            ],
            extra={'tool_used': 'generate_video', 'duration': 15, 'artifact_id': 'vid_abc123'},
        )
        self.assertGreater(
            len(output), 300,
            f'Rendered output too short ({len(output)} chars) — would fail '
            f'DeliverableFactory gate:\n{output}',
        )
        self.assertIn('# Generate a 15-second promo video', output)
        self.assertIn('Video generation started', output)  # summary preserved
        self.assertIn('generate_video', output)  # tool call rendered
        self.assertIn('artifact_id', output)  # extra rendered

    def test_sections_with_list_of_dicts_render_as_subheadings(self):
        """Used by ContentStrategyAgent shim — list of recommendation dicts
        should render as H3 subsections with bullet details."""
        output = self.render(
            task="Design content pillars",
            summary="Generated 2 recommendations",
            sections=[{
                'heading': 'Recommendations',
                'content': [
                    {'title': 'Sharp Action', 'description': 'Daily smart money', 'priority': 'high'},
                    {'title': 'Line Movement', 'description': 'Weekly breakdowns', 'priority': 'medium'},
                ],
            }],
        )
        self.assertIn('## Recommendations', output)
        self.assertIn('### 1. Sharp Action', output)
        self.assertIn('### 2. Line Movement', output)
        self.assertIn('- **description**: Daily smart money', output)
        self.assertIn('- **priority**: medium', output)

    def test_empty_inputs_fall_back_to_task_section(self):
        """Defensive case: no summary/tool_calls/sections/extra should still
        produce a non-empty doc including the task text."""
        output = self.render(task="Do something")
        self.assertIn('# Do something', output)
        self.assertIn('## Task', output)
        self.assertIn('Do something', output)

    def test_tool_calls_without_summary_still_render(self):
        """Agents that don't have a status message but do have tool trail."""
        output = self.render(
            task="Apply three photo edits",
            tool_calls=[
                {'tool': 'upscale', 'arguments': {'image_id': 'img_1', 'scale': 2}},
                {'tool': 'remove_bg', 'arguments': {'image_id': 'img_1'}},
                {'tool': 'add_variation', 'arguments': {'image_id': 'img_1', 'count': 3}},
            ],
        )
        self.assertIn('## Tool calls made', output)
        self.assertIn('upscale', output)
        self.assertIn('remove_bg', output)
        self.assertIn('add_variation', output)

    def test_title_prefix_is_applied(self):
        output = self.render(
            task="Q4 review",
            title_prefix='Strategy:',
        )
        self.assertIn('# Strategy: Q4 review', output)

    def test_handles_non_dict_items_in_sections_list(self):
        """Strings mixed in with dicts shouldn't crash."""
        output = self.render(
            task="Mixed content",
            sections=[{
                'heading': 'Mixed',
                'content': ['first bullet', {'title': 'Second', 'note': 'n/a'}, 'third bullet'],
            }],
        )
        self.assertIn('1. first bullet', output)
        self.assertIn('### 2. Second', output)
        self.assertIn('3. third bullet', output)
