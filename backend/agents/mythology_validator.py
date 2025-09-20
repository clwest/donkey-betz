"""
Mythology Validator - Reality Enforcement System

This module prevents AI agents from making unrealistic promises or claims.
It validates agent outputs against reality constraints before returning to users.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MythologyValidator:
    """
    Validates agent outputs to prevent unrealistic promises.
    Enforces reality constraints on AI-generated content.
    """

    # Unrealistic financial promises
    FINANCIAL_MYTHS = [
        r'\$[\d,]+\s*(?:per|a|in)\s*(?:day|hour|minute)',  # Unrealistic earnings
        r'guaranteed\s+(?:income|profit|return)',  # Guaranteed returns
        r'risk[- ]free\s+(?:investment|income|money)',  # Risk-free claims
        r'(?:earn|make)\s+\$?[\d,]+k?\s+(?:overnight|instantly|immediately)',  # Instant wealth
        r'(?:10x|100x|1000x)\s+your\s+(?:money|investment)',  # Unrealistic multipliers
        r'passive\s+income.*\$[\d,]+.*(?:day|week)',  # Unrealistic passive income
    ]

    # Impossible technical claims
    TECHNICAL_MYTHS = [
        r'100%\s+(?:accurate|success|uptime)',  # Perfect accuracy
        r'never\s+(?:fail|break|crash)',  # Impossible reliability
        r'(?:instant|immediate)\s+(?:deployment|scaling|migration)',  # Instant complex tasks
        r'no\s+(?:bugs|errors|issues|maintenance)',  # Perfect software
        r'unlimited\s+(?:scaling|storage|processing)',  # Unlimited resources
    ]

    # Unrealistic time promises
    TIME_MYTHS = [
        r'(?:build|create|develop).*(?:seconds|minute)',  # Instant development
        r'(?:learn|master).*(?:hours?|days?)\b',  # Instant expertise
        r'(?:immediate|instant)\s+(?:results|success|profitability)',  # Instant success
    ]

    # Legal/medical myths
    DANGEROUS_MYTHS = [
        r'(?:cure|heal|fix).*(?:disease|illness|condition)',  # Medical claims
        r'(?:legal|financial)\s+advice',  # Unlicensed advice
        r'guaranteed\s+(?:approval|acceptance|qualification)',  # Guaranteed approvals
    ]

    def __init__(self):
        """Initialize the validator with myth patterns"""
        self.violation_log = []
        self.validation_stats = {
            'total_checks': 0,
            'violations_found': 0,
            'corrections_made': 0
        }

    def validate_output(self, agent_name: str, output: Any) -> Dict[str, Any]:
        """
        Validate agent output for unrealistic promises.

        Args:
            agent_name: Name of the agent
            output: The output to validate

        Returns:
            Dict with validation results and corrected output
        """
        self.validation_stats['total_checks'] += 1

        # Convert output to string for analysis
        output_str = str(output) if not isinstance(output, str) else output

        violations = []

        # Check for financial myths
        for pattern in self.FINANCIAL_MYTHS:
            if re.search(pattern, output_str, re.IGNORECASE):
                violations.append({
                    'type': 'financial_myth',
                    'pattern': pattern,
                    'severity': 'high'
                })

        # Check for technical myths
        for pattern in self.TECHNICAL_MYTHS:
            if re.search(pattern, output_str, re.IGNORECASE):
                violations.append({
                    'type': 'technical_myth',
                    'pattern': pattern,
                    'severity': 'medium'
                })

        # Check for time myths
        for pattern in self.TIME_MYTHS:
            if re.search(pattern, output_str, re.IGNORECASE):
                violations.append({
                    'type': 'time_myth',
                    'pattern': pattern,
                    'severity': 'medium'
                })

        # Check for dangerous myths
        for pattern in self.DANGEROUS_MYTHS:
            if re.search(pattern, output_str, re.IGNORECASE):
                violations.append({
                    'type': 'dangerous_myth',
                    'pattern': pattern,
                    'severity': 'critical'
                })

        if violations:
            self.validation_stats['violations_found'] += len(violations)
            self.log_violation(agent_name, violations)

            # Correct the output
            corrected_output = self.correct_output(output, violations)

            return {
                'valid': False,
                'violations': violations,
                'original_output': output,
                'corrected_output': corrected_output,
                'warning': self.generate_warning(violations)
            }

        return {
            'valid': True,
            'output': output,
            'message': 'Output validated - no unrealistic promises detected'
        }

    def correct_output(self, output: Any, violations: List[Dict]) -> Any:
        """
        Correct unrealistic claims in output.

        Args:
            output: Original output
            violations: List of violations found

        Returns:
            Corrected output
        """
        if not isinstance(output, (str, dict)):
            return output

        output_str = str(output) if not isinstance(output, str) else output
        corrected = output_str

        # Apply corrections based on violation type
        corrections = {
            'financial_myth': [
                (r'\$[\d,]+\s*(?:per|a|in)\s*(?:day|hour|minute)', 'potential earnings vary'),
                (r'guaranteed\s+(?:income|profit|return)', 'potential income'),
                (r'risk[- ]free', 'low-risk'),
            ],
            'technical_myth': [
                (r'100%\s+(?:accurate|success|uptime)', 'highly reliable'),
                (r'never\s+(?:fail|break|crash)', 'rarely fails'),
                (r'unlimited\s+', 'scalable '),
            ],
            'time_myth': [
                (r'(?:instant|immediate)\s+', ''),
                (r'in\s+(?:seconds|minute)', 'quickly'),
            ],
            'dangerous_myth': [
                (r'(?:cure|heal|fix).*(?:disease|illness|condition)', 'may help with symptoms'),
                (r'guaranteed\s+', 'potential '),
            ]
        }

        for violation in violations:
            vtype = violation['type']
            if vtype in corrections:
                for pattern, replacement in corrections[vtype]:
                    corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

        self.validation_stats['corrections_made'] += 1

        # Return in original format
        if isinstance(output, dict):
            return {'corrected': True, 'content': corrected}
        return corrected

    def generate_warning(self, violations: List[Dict]) -> str:
        """Generate user-friendly warning about violations"""
        severity_counts = {}
        for v in violations:
            severity = v['severity']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        warning = "⚠️ Reality check: This output contained "

        if 'critical' in severity_counts:
            warning += f"{severity_counts['critical']} critical issues. "
        if 'high' in severity_counts:
            warning += f"{severity_counts['high']} unrealistic promises. "
        if 'medium' in severity_counts:
            warning += f"{severity_counts['medium']} exaggerated claims. "

        warning += "The output has been adjusted to be more realistic."
        return warning

    def log_violation(self, agent_name: str, violations: List[Dict]):
        """Log violations for monitoring"""
        self.violation_log.append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'violations': violations,
            'count': len(violations)
        })

        logger.warning(f"🚨 Mythology violations detected in {agent_name}: {len(violations)} issues")

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            **self.validation_stats,
            'recent_violations': self.violation_log[-10:],
            'violation_rate': (
                self.validation_stats['violations_found'] /
                max(self.validation_stats['total_checks'], 1)
            ) * 100
        }

    def is_realistic(self, claim: str) -> bool:
        """Quick check if a single claim is realistic"""
        all_patterns = (
            self.FINANCIAL_MYTHS +
            self.TECHNICAL_MYTHS +
            self.TIME_MYTHS +
            self.DANGEROUS_MYTHS
        )

        for pattern in all_patterns:
            if re.search(pattern, claim, re.IGNORECASE):
                return False
        return True


class MythologyEnforcer:
    """
    Enforces mythology validation across all agent executions.
    Integrates with the agent execution pipeline.
    """

    def __init__(self):
        self.validator = MythologyValidator()
        self.enforcement_enabled = True
        logger.info("🛡️ Mythology Enforcer initialized - protecting against unrealistic promises")

    def enforce(self, agent_name: str, result: Any) -> Dict[str, Any]:
        """
        Enforce validation on agent result.

        Args:
            agent_name: Name of the agent
            result: Agent execution result

        Returns:
            Validated and potentially corrected result
        """
        if not self.enforcement_enabled:
            return {'original': result, 'validated': False}

        # Validate the output
        validation = self.validator.validate_output(agent_name, result)

        if not validation['valid']:
            logger.warning(f"🚫 Mythology enforcement triggered for {agent_name}")

            # Return corrected version with metadata
            return {
                'result': validation['corrected_output'],
                'mythology_corrected': True,
                'violations': len(validation['violations']),
                'warning': validation['warning'],
                'original_flagged': True
            }

        return {
            'result': result,
            'mythology_validated': True,
            'clean': True
        }

    def set_enforcement(self, enabled: bool):
        """Enable or disable enforcement"""
        self.enforcement_enabled = enabled
        status = "enabled" if enabled else "disabled"
        logger.info(f"🛡️ Mythology enforcement {status}")

    def get_report(self) -> Dict[str, Any]:
        """Get enforcement report"""
        return {
            'enabled': self.enforcement_enabled,
            'stats': self.validator.get_stats(),
            'health': 'active' if self.enforcement_enabled else 'disabled'
        }


# Global enforcer instance
mythology_enforcer = MythologyEnforcer()


# Decorator for automatic validation
def validate_mythology(func):
    """Decorator to automatically validate function outputs"""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        agent_name = func.__qualname__ if hasattr(func, '__qualname__') else func.__name__
        validated = mythology_enforcer.enforce(agent_name, result)
        return validated.get('result', result)
    return wrapper