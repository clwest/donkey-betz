"""
API Configuration Settings
==========================
Centralized configuration for all API models and settings
Optimized for cost with gpt-4o-mini
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Settings - Using gpt-4o-mini for cost optimization
OPENAI_CONFIG = {
    'api_key': os.getenv('OPENAI_API_KEY'),
    'model': 'gpt-4o-mini',  # Cost-optimized model
    'temperature': 0.7,
    'max_tokens': 1000,
    'fallback_model': 'gpt-4o-mini',  # Even fallback uses mini
}

# Cost comparison (per 1M tokens as of 2024)
COST_COMPARISON = {
    'gpt-4o-mini': {
        'input': 0.15,   # $0.15 per 1M input tokens
        'output': 0.60,  # $0.60 per 1M output tokens
    },
    'gpt-3.5-turbo': {
        'input': 0.50,   # $0.50 per 1M input tokens
        'output': 1.50,  # $1.50 per 1M output tokens
    },
    'gpt-4': {
        'input': 30.00,  # $30 per 1M input tokens
        'output': 60.00, # $60 per 1M output tokens
    }
}

# Other API configurations
ANTHROPIC_CONFIG = {
    'api_key': os.getenv('ANTHROPIC_API_KEY'),
    'model': 'claude-3-haiku-20240307',  # Cost-optimized Claude model
    'max_tokens': 1000,
}

SERPER_CONFIG = {
    'api_key': os.getenv('SERPER_API_KEY'),
    'results_limit': 5,  # Limit results to control costs
}

NEWS_API_CONFIG = {
    'api_key': os.getenv('NEWS_API_KEY'),
    'page_size': 5,  # Limit articles to control response size
}

POLYGON_CONFIG = {
    'api_key': os.getenv('POLYGON_API_KEY'),
    'tier': 'basic',  # Use basic tier for cost optimization
}

def get_openai_client():
    """
    Get configured OpenAI client with cost-optimized settings
    """
    from openai import OpenAI
    return OpenAI(
        api_key=OPENAI_CONFIG['api_key'],
        timeout=30.0,  # 30 second timeout
        max_retries=2
    )

def get_model_for_task(task_type='general'):
    """
    Get the appropriate model based on task type
    All tasks use gpt-4o-mini for now (cost optimization)
    """
    model_mapping = {
        'general': 'gpt-4o-mini',
        'code_generation': 'gpt-4o-mini',
        'analysis': 'gpt-4o-mini',
        'creative': 'gpt-4o-mini',
        'translation': 'gpt-4o-mini',
    }
    return model_mapping.get(task_type, 'gpt-4o-mini')

def estimate_cost(input_tokens, output_tokens, model='gpt-4o-mini'):
    """
    Estimate the cost of an API call
    """
    if model not in COST_COMPARISON:
        model = 'gpt-4o-mini'

    costs = COST_COMPARISON[model]
    input_cost = (input_tokens / 1_000_000) * costs['input']
    output_cost = (output_tokens / 1_000_000) * costs['output']

    return {
        'model': model,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'input_cost': f"${input_cost:.6f}",
        'output_cost': f"${output_cost:.6f}",
        'total_cost': f"${input_cost + output_cost:.6f}"
    }

# Export configuration
__all__ = [
    'OPENAI_CONFIG',
    'ANTHROPIC_CONFIG',
    'SERPER_CONFIG',
    'NEWS_API_CONFIG',
    'POLYGON_CONFIG',
    'get_openai_client',
    'get_model_for_task',
    'estimate_cost',
    'COST_COMPARISON'
]