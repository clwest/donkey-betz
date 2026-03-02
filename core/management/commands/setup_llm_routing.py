"""
Session 697: Setup LLM Routing - Seed providers, models, and agent configs.

This command initializes the Enhanced Nervous System by populating:
1. LLM Providers (OpenAI, Anthropic, DeepSeek, Gemini, Ollama)
2. LLM Models (GPT-5 family, Claude, DeepSeek Coder, Gemini, etc.)
3. Agent LLM Configs (which model each agent should use)

Usage:
    python manage.py setup_llm_routing
    python manage.py setup_llm_routing --check  # Just check status
    python manage.py setup_llm_routing --clear  # Clear and re-seed
"""

import os
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models_llm_routing import (
    LLMProvider,
    LLMModel,
    AgentLLMConfig,
    DEFAULT_PROVIDERS,
    DEFAULT_MODELS,
    DEFAULT_AGENT_LLM_CONFIGS,
)


class Command(BaseCommand):
    help = 'Setup LLM routing with default providers, models, and agent configs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Only check current status, do not modify',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--mode',
            type=str,
            choices=['off', 'conservative', 'balanced', 'aggressive'],
            default=None,
            help='Set LLM routing tier mode (off|conservative|balanced|aggressive)',
        )

    def handle(self, *args, **options):
        if options['mode'] is not None:
            self.set_routing_mode(options['mode'])
            return

        if options['check']:
            self.check_status()
            return

        if options['clear']:
            self.clear_data()

        self.setup_providers()
        self.setup_models()
        self.setup_agent_configs()
        self.check_api_keys()

        self.stdout.write(self.style.SUCCESS('\n✅ LLM Routing setup complete!'))
        self.check_status()

    def check_status(self):
        """Display current status of LLM routing configuration"""
        self.stdout.write('\n=== LLM Routing Status ===\n')

        # Providers
        providers = LLMProvider.objects.all()
        self.stdout.write(f'Providers: {providers.count()}')
        for p in providers:
            status = '✅' if p.is_available else '⚠️'
            key_status = 'has key' if self._has_api_key(p.api_key_env_var) else 'no key'
            self.stdout.write(f'  {status} {p.name}: {key_status}')

        # Models
        models = LLMModel.objects.all()
        self.stdout.write(f'\nModels: {models.count()}')
        by_provider = {}
        for m in models:
            by_provider.setdefault(m.provider.name, []).append(m.model_id)
        for provider, model_list in by_provider.items():
            self.stdout.write(f'  {provider}: {", ".join(model_list)}')

        # Agent Configs
        configs = AgentLLMConfig.objects.filter(is_active=True)
        self.stdout.write(f'\nAgent Configs: {configs.count()}')
        by_model = {}
        for c in configs:
            model_name = c.primary_model.model_id if c.primary_model else 'none'
            by_model.setdefault(model_name, []).append(c.agent_name)
        for model, agents in list(by_model.items())[:5]:
            self.stdout.write(f'  {model}: {len(agents)} agents')

    def _has_api_key(self, env_var: str) -> bool:
        """Check if API key is configured"""
        if not env_var:
            return True  # No key needed (e.g., Ollama)
        key = os.getenv(env_var, '')
        return bool(key and key not in ['', 'your-key-here'])

    def clear_data(self):
        """Clear existing LLM routing data"""
        self.stdout.write('Clearing existing data...')
        AgentLLMConfig.objects.all().delete()
        LLMModel.objects.all().delete()
        LLMProvider.objects.all().delete()
        self.stdout.write(self.style.WARNING('  Cleared all LLM routing data'))

    @transaction.atomic
    def setup_providers(self):
        """Create LLM providers"""
        self.stdout.write('\nSetting up providers...')

        for provider_data in DEFAULT_PROVIDERS:
            provider, created = LLMProvider.objects.update_or_create(
                name=provider_data['name'],
                defaults={
                    'display_name': provider_data['display_name'],
                    'api_key_env_var': provider_data['api_key_env_var'],
                    'base_url': provider_data.get('base_url', ''),
                    'supports_tools': provider_data.get('supports_tools', True),
                    'supports_vision': provider_data.get('supports_vision', False),
                    'supports_streaming': provider_data.get('supports_streaming', True),
                    'is_active': True,
                    'is_available': self._has_api_key(provider_data['api_key_env_var']),
                }
            )
            action = 'Created' if created else 'Updated'
            status = '✅' if provider.is_available else '⚠️'
            self.stdout.write(f'  {status} {action} {provider.display_name}')

    @transaction.atomic
    def setup_models(self):
        """Create LLM models"""
        self.stdout.write('\nSetting up models...')

        for model_data in DEFAULT_MODELS:
            try:
                provider = LLMProvider.objects.get(name=model_data['provider'])

                model, created = LLMModel.objects.update_or_create(
                    provider=provider,
                    model_id=model_data['model_id'],
                    defaults={
                        'display_name': model_data['display_name'],
                        'category': model_data.get('category', 'general'),
                        'context_window': model_data.get('context_window', 128000),
                        'max_output_tokens': model_data.get('max_output_tokens', 4096),
                        'speed_rating': model_data.get('speed_rating', 5),
                        'quality_rating': model_data.get('quality_rating', 5),
                        'cost_per_1m_input': model_data.get('cost_per_1m_input', 0),
                        'cost_per_1m_output': model_data.get('cost_per_1m_output', 0),
                        'specializations': model_data.get('specializations', []),
                        'is_active': True,
                        'is_recommended': model_data.get('is_recommended', False),
                    }
                )
                action = 'Created' if created else 'Updated'
                self.stdout.write(f'  {action} {model.display_name}')

            except LLMProvider.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f'  Provider {model_data["provider"]} not found for model {model_data["model_id"]}'
                ))

    @transaction.atomic
    def setup_agent_configs(self):
        """Create agent LLM configurations"""
        self.stdout.write('\nSetting up agent configs...')

        for config_data in DEFAULT_AGENT_LLM_CONFIGS:
            try:
                # Parse primary model (format: "provider:model_id")
                primary_parts = config_data['primary'].split(':')
                primary_model = LLMModel.objects.filter(
                    provider__name=primary_parts[0],
                    model_id=primary_parts[1]
                ).first()

                # Parse fallback model
                fallback_parts = config_data['fallback'].split(':')
                fallback_model = LLMModel.objects.filter(
                    provider__name=fallback_parts[0],
                    model_id=fallback_parts[1]
                ).first()

                config, created = AgentLLMConfig.objects.update_or_create(
                    agent_name=config_data['agent_name'],
                    defaults={
                        'agent_category': config_data.get('agent_category', ''),
                        'primary_model': primary_model,
                        'fallback_model': fallback_model,
                        'temperature': 0.7,
                        'max_tokens': 2000,
                        'is_active': True,
                    }
                )
                action = 'Created' if created else 'Updated'
                primary_name = primary_model.model_id if primary_model else 'none'
                self.stdout.write(f'  {action} {config.agent_name} → {primary_name}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'  Failed to create config for {config_data["agent_name"]}: {e}'
                ))

    def set_routing_mode(self, mode: str):
        """Set the LLM routing tier mode via SystemConfiguration."""
        from core.models import SystemConfiguration
        obj, created = SystemConfiguration.objects.update_or_create(
            key='llm_routing_mode',
            defaults={
                'value': mode,
                'description': 'LLM routing tier mode: off|conservative|balanced|aggressive',
                'category': 'llm',
                'is_active': True,
            },
        )
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f"{action} llm_routing_mode = {mode}"))

    def check_api_keys(self):
        """Check and report on API key status"""
        self.stdout.write('\nAPI Key Status:')

        key_checks = [
            ('OPENAI_API_KEY', 'OpenAI'),
            ('ANTHROPIC_API_KEY', 'Anthropic'),
            ('DEEPSEEK_API_KEY', 'DeepSeek'),
            ('TOGETHER_AI_API_KEY', 'Together AI'),  # Session 697: Hosts DeepSeek, Llama, Mixtral
            ('GEMINI_API_KEY', 'Gemini'),
        ]

        for env_var, name in key_checks:
            if self._has_api_key(env_var):
                self.stdout.write(self.style.SUCCESS(f'  ✅ {name}: configured'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠️ {name}: not configured (set {env_var})'))

        # Ollama (no key needed)
        self.stdout.write(f'  ℹ️  Ollama: no API key needed (local)')
