# core/validation/__init__.py
"""
Section Validation Agents

Specialized agents for validating each major section of the platform.
Run these to verify endpoints, integrations, and data flows are working.

Usage:
    from core.validation import ImageValidationAgent, run_all_validations

    # Validate specific section
    validator = ImageValidationAgent()
    results = validator.validate_all()

    # Validate all sections
    report = run_all_validations()
"""

from .base import BaseValidationAgent
from .image_validator import ImageValidationAgent
from .video_validator import VideoValidationAgent
from .agent_validator import AgentOrchestrationValidator
from .spider_validator import SpiderValidationAgent

__all__ = [
    'BaseValidationAgent',
    'ImageValidationAgent',
    'VideoValidationAgent',
    'AgentOrchestrationValidator',
    'SpiderValidationAgent',
    'run_all_validations',
    'get_validator_for_section',
]

VALIDATORS = {
    'images': ImageValidationAgent,
    'videos': VideoValidationAgent,
    'agents': AgentOrchestrationValidator,
    'spiders': SpiderValidationAgent,
}


def get_validator_for_section(section: str):
    """Get the validator class for a specific section."""
    return VALIDATORS.get(section)


def run_all_validations(user=None) -> dict:
    """Run all section validations and return combined report."""
    results = {
        'overall_status': 'healthy',
        'sections': {},
        'summary': {
            'total': 0,
            'passed': 0,
            'failed': 0,
        }
    }

    for section_name, validator_class in VALIDATORS.items():
        try:
            validator = validator_class(user=user)
            section_result = validator.validate_all()
            results['sections'][section_name] = section_result

            # Count checks
            for check in section_result.get('checks', []):
                results['summary']['total'] += 1
                if check.get('pass'):
                    results['summary']['passed'] += 1
                else:
                    results['summary']['failed'] += 1
                    results['overall_status'] = 'degraded'

        except Exception as e:
            results['sections'][section_name] = {
                'status': 'error',
                'error': str(e)
            }
            results['overall_status'] = 'degraded'

    return results
