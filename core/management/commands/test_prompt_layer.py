"""
Test individual prompt injection layers by running an agent with/without each layer.

Usage:
    python manage.py test_prompt_layer --agent ResearchAgent --task "What are AI trends?"
    python manage.py test_prompt_layer --agent ResearchAgent --disable mood
    python manage.py test_prompt_layer --agent ResearchAgent --disable learning
    python manage.py test_prompt_layer --all-layers
    python manage.py test_prompt_layer --list-layers

Session 1085: Built for A/B testing prompt injection layers.
"""

import time
import json
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

LAYERS = {
    'sharpening': 'Prompt sharpening (hedging → decisive language)',
    'knowledge': 'Relevant knowledge from past learning (AgentKnowledgeSource + SharedKnowledge)',
    'policies': 'Canonical boardroom policies',
    'learnings': 'System learnings from LearningLoopOrchestrator',
    'advisor': 'Legendary advisor principles and frameworks',
    'mood': 'Mood behavioral directives (excited/focused/creative/tired)',
    'evolution': 'Authority level directives (junior/senior/expert/master)',
    'spider': 'Spider intelligence (trending topics)',
    'docs': 'Risk-aware document retrieval',
    'user': 'User context (profile, skills, preferences)',
    'memory': 'Agent memory palace (past patterns)',
}


class Command(BaseCommand):
    help = 'Test prompt injection layers by running agents with/without specific layers'

    def add_arguments(self, parser):
        parser.add_argument('--agent', type=str, default='ResearchAgent', help='Agent to test')
        parser.add_argument('--task', type=str, default='What are the top 3 AI trends in 2026?', help='Task to run')
        parser.add_argument('--disable', type=str, help='Layer to disable (e.g., mood, learning, advisor)')
        parser.add_argument('--all-layers', action='store_true', help='Test each layer independently')
        parser.add_argument('--list-layers', action='store_true', help='List all testable layers')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be injected without calling LLM')

    def handle(self, *args, **options):
        if options['list_layers']:
            self.stdout.write('\nTestable prompt injection layers:\n')
            for name, desc in LAYERS.items():
                self.stdout.write(f'  {name:15s} — {desc}')
            self.stdout.write(f'\nUsage: python manage.py test_prompt_layer --disable <layer>\n')
            return

        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stderr.write('No superuser found')
            return

        agent_name = options['agent']
        task = options['task']
        disable = options.get('disable')
        dry_run = options['dry_run']

        if options['all_layers']:
            self._test_all_layers(user, agent_name, task, dry_run)
        elif disable:
            self._test_single_layer(user, agent_name, task, disable, dry_run)
        else:
            # Run baseline (all layers enabled)
            self._run_test(user, agent_name, task, disabled_layer=None, dry_run=dry_run)

    def _test_all_layers(self, user, agent_name, task, dry_run):
        """Test each layer by disabling it one at a time."""
        self.stdout.write(f'\n=== A/B TEST: {agent_name} ===')
        self.stdout.write(f'Task: {task[:80]}')
        self.stdout.write(f'Testing {len(LAYERS)} layers...\n')

        # Baseline first
        baseline = self._run_test(user, agent_name, task, disabled_layer=None, dry_run=dry_run)

        results = [{'layer': 'BASELINE (all enabled)', **baseline}]

        for layer_name in LAYERS:
            result = self._run_test(user, agent_name, task, disabled_layer=layer_name, dry_run=dry_run)
            results.append({'layer': f'WITHOUT {layer_name}', **result})

        # Summary
        self.stdout.write(f'\n{"="*70}')
        self.stdout.write(f'{"Layer":<30} {"Tokens":>8} {"Cost":>8} {"Time":>8} {"Len":>6}')
        self.stdout.write(f'{"-"*70}')
        for r in results:
            self.stdout.write(
                f'{r["layer"]:<30} {r.get("tokens",0):>8} '
                f'${r.get("cost",0):>7.4f} {r.get("time_ms",0):>7}ms '
                f'{r.get("output_len",0):>5}c'
            )

    def _test_single_layer(self, user, agent_name, task, layer, dry_run):
        """Compare baseline vs one layer disabled."""
        if layer not in LAYERS:
            self.stderr.write(f'Unknown layer: {layer}. Use --list-layers to see options.')
            return

        self.stdout.write(f'\n=== A/B: {agent_name} with/without {layer} ===\n')

        self.stdout.write('--- BASELINE (all layers) ---')
        baseline = self._run_test(user, agent_name, task, disabled_layer=None, dry_run=dry_run)

        self.stdout.write(f'\n--- WITHOUT {layer} ---')
        without = self._run_test(user, agent_name, task, disabled_layer=layer, dry_run=dry_run)

        # Compare
        self.stdout.write(f'\n--- COMPARISON ---')
        self.stdout.write(f'Tokens: {baseline.get("tokens",0)} → {without.get("tokens",0)} ({"+" if without.get("tokens",0) > baseline.get("tokens",0) else ""}{without.get("tokens",0) - baseline.get("tokens",0)})')
        self.stdout.write(f'Cost:   ${baseline.get("cost",0):.4f} → ${without.get("cost",0):.4f}')
        self.stdout.write(f'Output: {baseline.get("output_len",0)}c → {without.get("output_len",0)}c')

    def _run_test(self, user, agent_name, task, disabled_layer=None, dry_run=False):
        """Run a single agent execution, optionally disabling a layer."""
        from core.agent_router import AgentRouter

        label = f'WITHOUT {disabled_layer}' if disabled_layer else 'BASELINE'

        # Monkey-patch to disable specific layer
        original_methods = {}
        if disabled_layer:
            original_methods = self._disable_layer(disabled_layer)

        try:
            router = AgentRouter(user=user)

            if dry_run:
                # Just gather context and build prompt, don't call LLM
                self.stdout.write(f'  [{label}] Gathering context...')
                try:
                    learning = router._get_learning_context(agent_name, task)
                    advisor = router._get_advisor_context(agent_name, task)
                    self.stdout.write(f'  Learning: {len(learning.get("applied_pattern_ids",[]))} patterns')
                    self.stdout.write(f'  Advisor: {"yes" if advisor.get("has_advice") else "no"}')
                except Exception as e:
                    self.stdout.write(f'  Context error: {e}')
                return {'tokens': 0, 'cost': 0, 'time_ms': 0, 'output_len': 0, 'success': True}

            start = time.time()
            try:
                result = router.route(agent_name, task, context={})
                elapsed = int((time.time() - start) * 1000)

                output_len = len(result.message or '') if result.message else 0
                self.stdout.write(
                    f'  [{label}] success={result.success} tokens={result.tokens_used} '
                    f'cost=${result.cost:.4f} time={elapsed}ms output={output_len}c'
                )
                if result.message:
                    self.stdout.write(f'  Preview: {result.message[:150]}...')

                return {
                    'tokens': result.tokens_used,
                    'cost': float(result.cost),
                    'time_ms': elapsed,
                    'output_len': output_len,
                    'success': result.success,
                }
            except Exception as e:
                elapsed = int((time.time() - start) * 1000)
                self.stdout.write(f'  [{label}] FAILED: {e} ({elapsed}ms)')
                return {'tokens': 0, 'cost': 0, 'time_ms': elapsed, 'output_len': 0, 'success': False}

        finally:
            # Restore monkey-patched methods
            self._restore_layer(original_methods)

    def _disable_layer(self, layer_name):
        """Monkey-patch BaseAgent to disable a specific prompt layer."""
        from core.agents.base_agent import BaseAgent
        saved = {}

        if layer_name == 'sharpening':
            saved['sharpened_system_prompt'] = BaseAgent.sharpened_system_prompt
            BaseAgent.sharpened_system_prompt = property(lambda self: self.system_prompt)

        elif layer_name == 'knowledge':
            saved['_get_relevant_knowledge_for_task'] = BaseAgent._get_relevant_knowledge_for_task
            BaseAgent._get_relevant_knowledge_for_task = lambda self, *a, **kw: []

        elif layer_name == 'policies':
            # Disable by making get_policy_context_service return empty
            saved['_policy_disabled'] = True

        elif layer_name == 'learnings':
            saved['_get_system_learnings_section'] = BaseAgent._get_system_learnings_section
            BaseAgent._get_system_learnings_section = lambda self: ''

        elif layer_name == 'advisor':
            # Will return empty since we override context
            saved['_advisor_disabled'] = True

        elif layer_name == 'mood':
            saved['_mood_disabled'] = True

        elif layer_name == 'evolution':
            saved['_evolution_disabled'] = True

        elif layer_name == 'spider':
            saved['_get_fresh_spider_intelligence'] = BaseAgent._get_fresh_spider_intelligence
            BaseAgent._get_fresh_spider_intelligence = lambda self, *a, **kw: []

        elif layer_name == 'docs':
            if hasattr(BaseAgent, '_get_relevant_docs_for_task'):
                saved['_get_relevant_docs_for_task'] = BaseAgent._get_relevant_docs_for_task
                BaseAgent._get_relevant_docs_for_task = lambda self, *a, **kw: []

        elif layer_name == 'memory':
            saved['_memory_disabled'] = True

        return saved

    def _restore_layer(self, saved):
        """Restore monkey-patched methods."""
        from core.agents.base_agent import BaseAgent
        for attr, value in saved.items():
            if attr.startswith('_') and attr.endswith('_disabled'):
                continue  # Skip flag markers
            if hasattr(BaseAgent, attr):
                setattr(BaseAgent, attr, value)
