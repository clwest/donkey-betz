"""
Mythology detection and prevention services for unified-donkey-betz.
"""

import re
import logging
from typing import Dict, List, Any
from django.db import transaction
from django.utils import timezone

from .models import (
    MythologyEvent, MythPattern, MythologyGuard, 
    MythologyAlert
)

logger = logging.getLogger(__name__)


class MythologyDetectionService:
    """Service for detecting mythology patterns in text."""
    
    # Known mythology patterns from the review
    MYTHOLOGY_PATTERNS = {
        'numeric_inflation': r'\b\d{3,}\s*(deployments?|instances?|users?|systems?|agents?|embeddings?)\b',
        'false_authority': r'(studies show|experts confirm|research proves|scientists agree)',
        'context_loss': r'(we have|our system|the platform) (successfully|always|never)',
        'capability_exaggeration': r'(can do anything|unlimited|infinite|perfect|complete[ly]?)',
        'temporal_distortion': r'(has been|have been) .{0,20}(years?|months?|decades?)',
        'false_claims': r'(fitness dashboard|dart|flutter|main_navigation|dashboard_page)',
        'unverified_stats': r'(\d+%?\s*(success|accuracy|improvement|performance))',
        'false_technology': r'(dart|flutter|swift|kotlin|react native)',
        '350_deployments': r'350\s*deployments?',
    }
    
    # Anti-mythology instruction to inject
    ANTI_MYTHOLOGY_INSTRUCTION = """
IMPORTANT: Base all responses on verified data only. Follow these guidelines:
- Only cite specific, verifiable numbers with sources
- Avoid generalizations without data backing
- Preserve full context when summarizing
- Acknowledge uncertainties and limitations
- Do not create fictional statistics or capabilities
- If unsure about specifics, say so explicitly
- This system is a Django/React platform for AI content generation and sports analytics
"""
    
    def __init__(self):
        self._load_patterns()
    
    def _load_patterns(self):
        """Load active patterns from database."""
        try:
            db_patterns = MythPattern.objects.filter(is_active=True)
            for pattern in db_patterns:
                if pattern.regex_pattern:
                    self.MYTHOLOGY_PATTERNS[pattern.pattern_type] = pattern.regex_pattern
        except Exception as e:
            logger.debug(f"Could not load patterns from DB: {e}")
    
    def detect_mythologies(self, text: str, source_type: str = None) -> Dict[str, Any]:
        """
        Detect mythology patterns in text.
        
        Args:
            text: Text to analyze
            source_type: Type of source (conversation, embedding, etc.)
            
        Returns:
            Dictionary with detection results
        """
        patterns_found = []
        matches = {}
        risk_score = 0.0
        
        # Check each pattern
        for pattern_name, pattern_regex in self.MYTHOLOGY_PATTERNS.items():
            try:
                found_matches = re.findall(pattern_regex, text, re.IGNORECASE)
                if found_matches:
                    patterns_found.append(pattern_name)
                    matches[pattern_name] = found_matches[:5]  # Limit to 5 examples
                    
                    # Update pattern statistics
                    self._update_pattern_stats(pattern_name)
                    
                    # Add to risk score
                    risk_score += self._get_pattern_weight(pattern_name)
                    
            except Exception as e:
                logger.error(f"Error checking pattern {pattern_name}: {e}")
        
        # Check for specific known myths
        known_myths = self._check_known_myths(text)
        if known_myths:
            patterns_found.extend(known_myths)
            risk_score += len(known_myths) * 0.2
        
        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)
        
        return {
            'detected': len(patterns_found) > 0,
            'patterns_found': patterns_found,
            'matches': matches,
            'risk_score': risk_score,
            'severity': self._get_severity(risk_score),
            'source_type': source_type
        }
    
    def _check_known_myths(self, text: str) -> List[str]:
        """Check for specific known mythology instances."""
        known_myths = []
        
        # The infamous "350 deployments" myth
        if '350' in text and 'deployment' in text.lower():
            known_myths.append('350_deployments_myth')
        
        # Fitness dashboard false claim
        if 'fitness' in text.lower() and 'dashboard' in text.lower():
            known_myths.append('fitness_dashboard_myth')
        
        # Dart/Flutter false technology
        if 'dart' in text.lower() or 'flutter' in text.lower():
            known_myths.append('dart_flutter_myth')
        
        return known_myths
    
    def _get_pattern_weight(self, pattern_name: str) -> float:
        """Get risk weight for a pattern."""
        weights = {
            'numeric_inflation': 0.3,
            'false_authority': 0.2,
            'context_loss': 0.25,
            'capability_exaggeration': 0.35,
            'temporal_distortion': 0.2,
            'false_claims': 0.4,
            'unverified_stats': 0.25,
            'false_technology': 0.35,
            '350_deployments': 0.5,
            '350_deployments_myth': 0.8,
            'fitness_dashboard_myth': 0.7,
            'dart_flutter_myth': 0.6,
        }
        return weights.get(pattern_name, 0.1)
    
    def _get_severity(self, risk_score: float) -> str:
        """Get severity level from risk score."""
        if risk_score >= 0.7:
            return 'critical'
        elif risk_score >= 0.5:
            return 'high'
        elif risk_score >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _update_pattern_stats(self, pattern_name: str):
        """Update pattern statistics in database."""
        try:
            pattern, created = MythPattern.objects.get_or_create(
                pattern_type=pattern_name,
                defaults={
                    'description': f'Auto-detected pattern: {pattern_name}',
                    'regex_pattern': self.MYTHOLOGY_PATTERNS.get(pattern_name, ''),
                    'severity_weight': self._get_pattern_weight(pattern_name)
                }
            )
            pattern.frequency_count += 1
            pattern.last_seen = timezone.now()
            pattern.save(update_fields=['frequency_count', 'last_seen'])
        except Exception as e:
            logger.debug(f"Could not update pattern stats: {e}")
    
    @transaction.atomic
    def record_mythology_event(
        self, 
        content: str, 
        detection_result: Dict[str, Any],
        user=None,
        source_id=None,
        was_prevented=False
    ) -> MythologyEvent:
        """Record a mythology event in the database."""
        event = MythologyEvent.objects.create(
            event_type='detection' if not was_prevented else 'prevention',
            original_content=content[:2000],  # Limit content size
            mutation_type=self._get_primary_mutation_type(detection_result['patterns_found']),
            source_type=detection_result.get('source_type', 'unknown'),
            source_id=str(source_id) if source_id else '',
            user=user,
            confidence_score=detection_result['risk_score'],
            risk_level=detection_result['risk_score'],
            patterns_detected=detection_result['patterns_found'],
            was_prevented=was_prevented,
            metadata=detection_result.get('matches', {})
        )
        
        # Create alert if severity is high
        if detection_result['severity'] in ['high', 'critical']:
            self._create_alert(event, detection_result)
        
        return event
    
    def _get_primary_mutation_type(self, patterns: List[str]) -> str:
        """Get the primary mutation type from patterns."""
        mutation_map = {
            'numeric_inflation': 'inflation',
            'false_authority': 'false_claim',
            'context_loss': 'context_loss',
            'capability_exaggeration': 'capability_exaggeration',
            'temporal_distortion': 'semantic_drift',
            'false_claims': 'false_claim',
            'unverified_stats': 'inflation',
            'false_technology': 'false_claim',
        }
        
        for pattern in patterns:
            if pattern in mutation_map:
                return mutation_map[pattern]
        
        return 'semantic_drift'
    
    def _create_alert(self, event: MythologyEvent, detection_result: Dict[str, Any]):
        """Create an alert for high-risk mythology."""
        MythologyAlert.objects.create(
            alert_type='pattern_detected',
            severity=detection_result['severity'],
            title=f"High-risk mythology detected: {', '.join(detection_result['patterns_found'][:3])}",
            description=f"Detected {len(detection_result['patterns_found'])} mythology patterns with risk score {detection_result['risk_score']:.2f}",
            mythology_event=event,
            data=detection_result
        )


class MythologyPreventionService:
    """Service for preventing mythology in prompts and responses."""
    
    def __init__(self):
        self.detection_service = MythologyDetectionService()
        self._load_guards()
    
    def _load_guards(self):
        """Load active guards from database."""
        try:
            self.guards = list(MythologyGuard.objects.filter(is_active=True).order_by('-priority'))
        except:
            self.guards = []
    
    def guard_prompt(self, prompt: str, user=None) -> Dict[str, Any]:
        """
        Apply mythology guards to a prompt before sending to AI.
        
        Args:
            prompt: Original prompt
            user: User making the request
            
        Returns:
            Dictionary with guarded prompt and metadata
        """
        # Detect mythologies
        detection_result = self.detection_service.detect_mythologies(prompt, 'prompt')
        
        guarded_prompt = prompt
        guards_applied = []
        
        # If mythology detected, apply guards
        if detection_result['risk_score'] > 0.3:
            # Record the detection
            self.detection_service.record_mythology_event(
                prompt, detection_result, user=user, was_prevented=False
            )
            
            # Apply instruction guard
            guarded_prompt = self._inject_anti_mythology_instructions(prompt)
            guards_applied.append('anti_mythology_instructions')
            
            # Apply strong guards for high risk
            if detection_result['risk_score'] > 0.6:
                guarded_prompt = self._apply_strong_guards(guarded_prompt)
                guards_applied.append('strong_guards')
        
        return {
            'prompt': guarded_prompt,
            'original_prompt': prompt,
            'mythology_detected': detection_result['detected'],
            'risk_score': detection_result['risk_score'],
            'patterns_found': detection_result['patterns_found'],
            'guards_applied': guards_applied
        }
    
    def validate_response(self, response: str, original_prompt: str, user=None) -> Dict[str, Any]:
        """
        Validate a response for mythology after generation.
        
        Args:
            response: Generated response
            original_prompt: The prompt that generated it
            user: User who made the request
            
        Returns:
            Dictionary with validation results
        """
        # Detect mythologies in response
        detection_result = self.detection_service.detect_mythologies(response, 'response')
        
        # Check for context loss
        context_loss = self._check_context_loss(original_prompt, response)
        
        # Record mythology events for risk > 0.3 (matches detection threshold)
        if detection_result['risk_score'] > 0.3:
            # Record the mythology event
            self.detection_service.record_mythology_event(
                response, detection_result, user=user, was_prevented=False
            )
        
        # Suggest corrections if needed for higher risk
        corrections = []
        if detection_result['risk_score'] > 0.5:
            corrections = self._suggest_corrections(response, detection_result)
        
        return {
            'valid': detection_result['risk_score'] < 0.3,
            'mythology_risk': detection_result['risk_score'],
            'patterns_found': detection_result['patterns_found'],
            'context_loss_ratio': context_loss,
            'corrections': corrections,
            'needs_regeneration': detection_result['risk_score'] > 0.7
        }
    
    def _inject_anti_mythology_instructions(self, prompt: str) -> str:
        """Inject anti-mythology instructions into prompt."""
        if 'verified data only' in prompt.lower():
            return prompt
        
        return f"{prompt}\n\n{MythologyDetectionService.ANTI_MYTHOLOGY_INSTRUCTION}"
    
    def _apply_strong_guards(self, prompt: str) -> str:
        """Apply strong mythology prevention guards."""
        strong_guard = """
CRITICAL MYTHOLOGY PREVENTION:
- Every number must have a source
- No capabilities without documentation
- Explicitly state when information is uncertain
- Use phrases like "approximately", "reported", "according to"
- Never invent statistics or metrics
- This is a Django/React platform, not Flutter/Dart
- Do not reference "350 deployments" or fitness features
"""
        return f"{prompt}\n\n{strong_guard}"
    
    def _check_context_loss(self, prompt: str, response: str) -> float:
        """Check for context loss between prompt and response."""
        prompt_terms = set(re.findall(r'\b\w{4,}\b', prompt.lower()))
        response_terms = set(re.findall(r'\b\w{4,}\b', response.lower()))
        
        if not prompt_terms:
            return 0.0
        
        retained = len(prompt_terms & response_terms)
        loss_ratio = 1 - (retained / len(prompt_terms))
        
        return loss_ratio
    
    def _suggest_corrections(self, text: str, detection_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest corrections for detected mythology."""
        corrections = []
        
        # Numeric inflation corrections
        if 'numeric_inflation' in detection_result['patterns_found']:
            for match in detection_result.get('matches', {}).get('numeric_inflation', []):
                corrections.append({
                    'pattern': match,
                    'suggestion': f"approximately {match} (unverified)",
                    'type': 'numeric_qualification'
                })
        
        # False technology corrections
        if 'false_technology' in detection_result['patterns_found'] or 'dart_flutter_myth' in detection_result['patterns_found']:
            corrections.append({
                'pattern': 'Dart/Flutter references',
                'suggestion': 'Django/React/TypeScript',
                'type': 'technology_correction'
            })
        
        # False claims corrections
        if 'fitness_dashboard_myth' in detection_result['patterns_found']:
            corrections.append({
                'pattern': 'fitness dashboard',
                'suggestion': 'AI content generation and sports analytics platform',
                'type': 'purpose_correction'
            })
        
        return corrections


class HallucinationFlaggingService:
    """Service for flagging and managing hallucinations for review."""
    
    def __init__(self):
        self.detection_service = MythologyDetectionService()
    
    def flag_blocked_content(self, original_prompt: str, blocked_content: str, 
                           detection_result: Dict[str, Any], user=None, 
                           session_id: str = None) -> 'FlaggedHallucination':
        """
        Flag content that was blocked for containing hallucinations.
        
        Args:
            original_prompt: The original user prompt
            blocked_content: The content that was blocked
            detection_result: Results from mythology detection
            user: User who submitted the prompt
            session_id: Session identifier
            
        Returns:
            FlaggedHallucination object
        """
        from .models import FlaggedHallucination
        
        # Determine priority based on risk score
        priority = self._calculate_priority(detection_result['risk_score'])
        
        # Create flagged hallucination record
        flagged = FlaggedHallucination.objects.create(
            flagged_type='blocked_content',
            original_prompt=original_prompt,
            flagged_content=blocked_content,
            patterns_detected=detection_result.get('patterns_found', []),
            risk_score=detection_result.get('risk_score', 0.0),
            confidence_score=detection_result.get('confidence_score', 0.0),
            detection_method=f"mythology_patterns_{len(detection_result.get('patterns_found', []))}_detected",
            priority=priority,
            requires_immediate_attention=priority in ['high', 'critical'],
            user=user,
            session_id=session_id or '',
            metadata={
                'detection_timestamp': timezone.now().isoformat(),
                'patterns_detail': detection_result.get('matches', {}),
                'severity': detection_result.get('severity', 'medium')
            }
        )
        
        # Create real-time alert for high priority items
        if priority in ['high', 'critical']:
            self._create_immediate_alert(flagged)
        
        # Trigger auto-verification for medium+ priority
        if priority in ['medium', 'high', 'critical']:
            self._schedule_auto_verification(flagged)
        
        return flagged
    
    def flag_suspicious_response(self, original_prompt: str, response: str,
                               risk_score: float, patterns: List[str], 
                               user=None, session_id: str = None) -> 'FlaggedHallucination':
        """
        Flag a response that appears suspicious but wasn't blocked.
        
        Args:
            original_prompt: The original user prompt
            response: The suspicious response
            risk_score: Calculated risk score
            patterns: Detected patterns
            user: User who received the response
            session_id: Session identifier
            
        Returns:
            FlaggedHallucination object
        """
        from .models import FlaggedHallucination
        
        priority = self._calculate_priority(risk_score)
        
        flagged = FlaggedHallucination.objects.create(
            flagged_type='suspicious_response',
            original_prompt=original_prompt,
            flagged_content=response,
            patterns_detected=patterns,
            risk_score=risk_score,
            detection_method="response_validation",
            priority=priority,
            requires_immediate_attention=risk_score > 0.8,
            user=user,
            session_id=session_id or '',
            metadata={
                'detection_timestamp': timezone.now().isoformat(),
                'risk_threshold_exceeded': risk_score > 0.5,
                'auto_flagged': True
            }
        )
        
        # Auto-verify high-risk items
        if risk_score > 0.7:
            self._schedule_auto_verification(flagged)
        
        return flagged
    
    def flag_user_reported(self, original_prompt: str, reported_content: str,
                          user_notes: str, user=None, session_id: str = None) -> 'FlaggedHallucination':
        """
        Flag content reported by user as potentially incorrect.
        
        Args:
            original_prompt: The original prompt
            reported_content: Content user reported as problematic
            user_notes: User's explanation of the issue
            user: User reporting the issue
            session_id: Session identifier
            
        Returns:
            FlaggedHallucination object
        """
        from .models import FlaggedHallucination
        
        # Run detection on reported content
        detection_result = self.detection_service.detect_mythologies(reported_content, 'user_report')
        
        flagged = FlaggedHallucination.objects.create(
            flagged_type='user_reported',
            original_prompt=original_prompt,
            flagged_content=reported_content,
            patterns_detected=detection_result.get('patterns_found', []),
            risk_score=detection_result.get('risk_score', 0.0),
            detection_method="user_report",
            priority='high',  # User reports get high priority
            requires_immediate_attention=True,
            user=user,
            session_id=session_id or '',
            verification_notes=user_notes,
            metadata={
                'user_report_timestamp': timezone.now().isoformat(),
                'user_notes': user_notes,
                'auto_detection_result': detection_result
            }
        )
        
        # Always auto-verify user reports
        self._schedule_auto_verification(flagged)
        
        return flagged
    
    def get_pending_reviews(self, limit: int = 50) -> List['FlaggedHallucination']:
        """Get pending hallucinations that need review."""
        from .models import FlaggedHallucination
        
        return list(
            FlaggedHallucination.objects
            .filter(verification_status='pending')
            .order_by('-requires_immediate_attention', '-priority', '-flagged_at')[:limit]
        )
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for the hallucination review dashboard."""
        from .models import FlaggedHallucination
        from django.db.models import Count, Q
        from datetime import timedelta
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        stats = FlaggedHallucination.objects.aggregate(
            total_flagged=Count('id'),
            pending_review=Count('id', filter=Q(verification_status='pending')),
            high_priority=Count('id', filter=Q(priority__in=['high', 'critical'])),
            needs_attention=Count('id', filter=Q(requires_immediate_attention=True)),
            last_24h=Count('id', filter=Q(flagged_at__gte=last_24h)),
            last_7d=Count('id', filter=Q(flagged_at__gte=last_7d)),
            verified_hallucinations=Count('id', filter=Q(verification_status='verified_hallucination')),
            false_positives=Count('id', filter=Q(verification_status='false_positive'))
        )
        
        # Calculate rates
        if stats['total_flagged'] > 0:
            stats['false_positive_rate'] = stats['false_positives'] / stats['total_flagged']
            stats['confirmation_rate'] = stats['verified_hallucinations'] / stats['total_flagged']
        else:
            stats['false_positive_rate'] = 0.0
            stats['confirmation_rate'] = 0.0
        
        return stats
    
    def _calculate_priority(self, risk_score: float) -> str:
        """Calculate priority level based on risk score."""
        if risk_score >= 0.9:
            return 'critical'
        elif risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _create_immediate_alert(self, flagged: 'FlaggedHallucination'):
        """Create immediate alert for high-priority flagged content."""
        from .models import MythologyAlert
        
        MythologyAlert.objects.create(
            alert_type='new_myth',
            severity=flagged.priority,
            title=f"High-priority hallucination flagged: {flagged.get_flagged_type_display()}",
            description=f"Risk score: {flagged.risk_score:.2f}, Patterns: {', '.join(flagged.patterns_detected[:3])}",
            data={
                'flagged_hallucination_id': str(flagged.id),
                'patterns': flagged.patterns_detected,
                'risk_score': flagged.risk_score,
                'requires_review': True
            }
        )
    
    def _schedule_auto_verification(self, flagged: 'FlaggedHallucination'):
        """Schedule automatic verification by a second agent."""
        # This will be implemented when we create the verification agent
        flagged.auto_verification_attempted = False
        flagged.save()


class HallucinationVerificationService:
    """Service for auto-verifying flagged hallucinations using a second agent."""
    
    def __init__(self):
        self.flagging_service = HallucinationFlaggingService()
    
    def verify_flagged_content(self, flagged_id: str) -> Dict[str, Any]:
        """
        Use a second agent to verify if flagged content is actually a hallucination.
        
        Args:
            flagged_id: ID of the flagged hallucination
            
        Returns:
            Verification result dictionary
        """
        from .models import FlaggedHallucination
        
        try:
            flagged = FlaggedHallucination.objects.get(id=flagged_id)
        except FlaggedHallucination.DoesNotExist:
            return {'success': False, 'error': 'Flagged content not found'}
        
        # Prepare verification prompt
        verification_prompt = self._build_verification_prompt(flagged)
        
        # Use AI to verify content
        verification_result = self._execute_verification(verification_prompt, flagged)
        
        # Update flagged record with verification results
        self._update_verification_results(flagged, verification_result)
        
        return verification_result
    
    def _build_verification_prompt(self, flagged: 'FlaggedHallucination') -> str:
        """Build prompt for verification agent."""
        return f"""
HALLUCINATION VERIFICATION TASK

You are a secondary verification agent. Your job is to analyze content that was flagged as a potential hallucination and determine if the flagging was correct.

ORIGINAL PROMPT:
{flagged.original_prompt}

FLAGGED CONTENT:
{flagged.flagged_content}

DETECTED PATTERNS:
{', '.join(flagged.patterns_detected)}

RISK SCORE: {flagged.risk_score}

VERIFICATION INSTRUCTIONS:
1. Analyze the flagged content for factual accuracy
2. Check if the content contains unverified claims, false statistics, or capability exaggerations
3. Determine if the flagging was justified
4. Provide a confidence score (0.0-1.0) for your assessment

RESPOND WITH JSON:
{{
    "is_hallucination": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "explanation of your assessment",
    "specific_issues": ["list of specific problems found"],
    "verdict": "verified_hallucination" | "verified_safe" | "needs_human_review"
}}

Be thorough and objective in your analysis.
"""
    
    def _execute_verification(self, prompt: str, flagged: 'FlaggedHallucination') -> Dict[str, Any]:
        """Execute verification using AI provider."""
        try:
            from content.ai_providers import AIProviderManager
            import json
            
            ai_manager = AIProviderManager()
            available_providers = ai_manager.get_available_providers()
            
            if not available_providers:
                return {
                    'success': False,
                    'error': 'No AI providers available for verification',
                    'verdict': 'needs_human_review'
                }
            
            # Use different provider than original if possible
            provider = 'anthropic' if 'anthropic' in available_providers else available_providers[0]
            model = 'claude-3-haiku-20240307' if provider == 'anthropic' else 'default'
            
            result = ai_manager.generate_content(
                provider=provider,
                model=model,
                system_prompt="You are a hallucination verification agent. Analyze content objectively and respond with valid JSON only.",
                user_prompt=prompt,
                config={'max_tokens': 800, 'temperature': 0.1}
            )
            
            if result.success and result.content:
                # Parse JSON response
                verification_data = json.loads(result.content.strip())
                
                return {
                    'success': True,
                    'verification_data': verification_data,
                    'agent_used': f"{provider}:{model}",
                    'verdict': verification_data.get('verdict', 'needs_human_review')
                }
            else:
                return {
                    'success': False,
                    'error': result.error_message if hasattr(result, 'error_message') else 'Verification failed',
                    'verdict': 'needs_human_review'
                }
                
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': 'Invalid JSON response from verification agent',
                'verdict': 'needs_human_review'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Verification error: {str(e)}',
                'verdict': 'needs_human_review'
            }
    
    def _update_verification_results(self, flagged: 'FlaggedHallucination', result: Dict[str, Any]):
        """Update flagged record with verification results."""
        flagged.auto_verification_attempted = True
        flagged.auto_verification_result = result
        
        if result['success']:
            flagged.auto_verification_agent = result.get('agent_used', 'unknown')
            flagged.verification_status = result.get('verdict', 'needs_human_review')
            
            if result.get('verification_data'):
                data = result['verification_data']
                flagged.confidence_score = data.get('confidence', 0.0)
                flagged.verification_notes = data.get('reasoning', '')
        else:
            flagged.verification_status = 'needs_human_review'
            flagged.verification_notes = f"Auto-verification failed: {result.get('error', 'Unknown error')}"
        
        flagged.save()