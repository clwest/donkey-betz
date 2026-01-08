"""
Mythology Validator - Reality Enforcement System

This module prevents AI agents from making unrealistic promises or claims.
It validates agent outputs against reality constraints before returning to users.

Session 728: Connected to mythology/ database models for persistent tracking.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Session 728: Database persistence service (lazy-loaded)
_detection_service = None

def get_detection_service():
    """Lazy-load the MythologyDetectionService to avoid circular imports."""
    global _detection_service
    if _detection_service is None:
        try:
            from mythology.services import MythologyDetectionService
            _detection_service = MythologyDetectionService()
        except Exception as e:
            logger.debug(f"Could not load MythologyDetectionService: {e}")
    return _detection_service


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
        r'(?:5|10|20)\s+years?\s+(?:of\s+)?(?:development|work|building)',  # Exaggerated timelines
        r'decades?\s+of\s+(?:development|work)',  # Decade claims
    ]

    # Legal/medical myths
    DANGEROUS_MYTHS = [
        r'(?:cure|heal|fix).*(?:disease|illness|condition)',  # Medical claims
        r'(?:legal|financial)\s+advice',  # Unlicensed advice
        r'guaranteed\s+(?:approval|acceptance|qualification)',  # Guaranteed approvals
    ]

    # Session 354: Spider data validation - catches unrealistic claims from web sources
    SPIDER_DATA_MYTHS = [
        r'(\d{2,})\s*%\s+(?:of|market|growth|increase)',  # Exaggerated percentages (99% market share)
        r'(?:every|all)\s+(?:business|company|startup)\s+(?:uses?|needs?)',  # Universal claims
        r'(?:million|billion)s?\s+(?:users?|customers?)\s+(?:in|within)\s+(?:\d+\s+)?(?:days?|weeks?|months?)',  # Unrealistic user growth
        r'(?:dominate|dominates?|dominated?)\s+(?:the\s+)?(?:market|industry)',  # Domination claims
        r'(?:no\s+)?competition',  # No competition claims
        r'(?:first|only)\s+(?:ever|in the world|of its kind)',  # Unique claims
        r'(?:viral|virality)\s+(?:guaranteed|certain)',  # Viral guarantees
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

        # Session 354: Check for spider data myths (from web sources)
        for pattern in self.SPIDER_DATA_MYTHS:
            if re.search(pattern, output_str, re.IGNORECASE):
                violations.append({
                    'type': 'spider_data_myth',
                    'pattern': pattern,
                    'severity': 'medium'
                })

        if violations:
            self.validation_stats['violations_found'] += len(violations)
            # Session 728: Pass output for database persistence
            self.log_violation(agent_name, violations, output=output_str)

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
            ],
            # Session 354: Spider data myth corrections
            'spider_data_myth': [
                (r'(\d{2,})\s*%\s+(?:of|market)', 'significant market share'),
                (r'(?:every|all)\s+(?:business|company|startup)\s+(?:uses?|needs?)', 'many businesses use'),
                (r'(?:million|billion)s?\s+(?:users?|customers?)\s+(?:in|within)', 'rapid user growth'),
                (r'(?:dominate|dominates?|dominated?)\s+(?:the\s+)?(?:market|industry)', 'has strong market presence'),
                (r'(?:no\s+)?competition', 'limited direct competition'),
                (r'(?:first|only)\s+(?:ever|in the world|of its kind)', 'innovative'),
                (r'(?:viral|virality)\s+(?:guaranteed|certain)', 'viral potential'),
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

    def log_violation(self, agent_name: str, violations: List[Dict], output: str = None, user=None):
        """
        Log violations for monitoring and persist to database.

        Session 728: Now persists to mythology/ database models.
        """
        # In-memory logging
        self.violation_log.append({
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'violations': violations,
            'count': len(violations)
        })

        logger.warning(f"🚨 Mythology violations detected in {agent_name}: {len(violations)} issues")

        # Session 728: Persist to database
        self._persist_to_database(agent_name, violations, output, user)

    def _persist_to_database(self, agent_name: str, violations: List[Dict], output: str = None, user=None):
        """
        Persist violations to mythology database models.

        Session 728: Connects validator to mythology/ app for tracking.
        """
        try:
            detection_service = get_detection_service()
            if not detection_service:
                return

            # Calculate risk score based on violations
            risk_score = 0.0
            severity_weights = {'critical': 0.4, 'high': 0.3, 'medium': 0.2, 'low': 0.1}
            for v in violations:
                risk_score += severity_weights.get(v.get('severity', 'medium'), 0.2)
            risk_score = min(risk_score, 1.0)

            # Determine overall severity
            severities = [v.get('severity', 'medium') for v in violations]
            if 'critical' in severities:
                overall_severity = 'critical'
            elif 'high' in severities:
                overall_severity = 'high'
            elif 'medium' in severities:
                overall_severity = 'medium'
            else:
                overall_severity = 'low'

            # Build detection result format expected by record_mythology_event
            detection_result = {
                'detected': True,
                'patterns_found': [v.get('type', 'unknown') for v in violations],
                'matches': {v.get('type', 'unknown'): [v.get('pattern', '')] for v in violations},
                'risk_score': risk_score,
                'severity': overall_severity,
                'source_type': 'agent'
            }

            # Record to MythologyEvent
            detection_service.record_mythology_event(
                content=output or 'No output captured',
                detection_result=detection_result,
                user=user,
                source_id=agent_name,
                was_prevented=True  # We corrected the output
            )

            logger.info(f"📝 Mythology event recorded for {agent_name} (risk: {risk_score:.2f})")

            # For high/critical violations, also create a FlaggedHallucination
            if overall_severity in ['high', 'critical']:
                self._create_flagged_hallucination(agent_name, violations, output, user, detection_result)

        except Exception as e:
            logger.debug(f"Could not persist mythology event: {e}")

    def _create_flagged_hallucination(
        self,
        agent_name: str,
        violations: List[Dict],
        output: str,
        user,
        detection_result: Dict
    ):
        """
        Create a FlaggedHallucination record for high-severity violations.

        Session 728: Enables human review of serious mythology violations.
        """
        try:
            from mythology.models import FlaggedHallucination

            FlaggedHallucination.objects.create(
                flagged_type='auto_detected',
                original_prompt=f"Agent: {agent_name}",
                flagged_content=output[:2000] if output else 'No content',
                context=f"Violations: {[v.get('type') for v in violations]}",
                patterns_detected=detection_result['patterns_found'],
                risk_score=detection_result['risk_score'],
                confidence_score=0.8,  # High confidence from pattern matching
                detection_method='mythology_validator',
                verification_status='pending',
                priority=detection_result['severity'],
                requires_immediate_attention=detection_result['severity'] == 'critical',
                metadata={
                    'agent_name': agent_name,
                    'violations': violations,
                    'validator_version': 'v2_session_728'
                }
            )
            logger.info(f"🚩 FlaggedHallucination created for {agent_name}")
        except Exception as e:
            logger.debug(f"Could not create FlaggedHallucination: {e}")

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
            self.DANGEROUS_MYTHS +
            self.SPIDER_DATA_MYTHS  # Session 354: Include spider data myths
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