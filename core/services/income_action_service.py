"""
Income Action Service - Bridge from Spider Data to Income
=========================================================

Session 388: Simple, practical service to:
1. Save interesting opportunities from spider data
2. Track application status
3. Generate application materials (cover letter/proposal)
4. Record outcomes for learning

This is the missing "action layer" between data collection and revenue.
"""

import logging
from typing import Dict, List
from datetime import datetime, timezone
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


class IncomeActionService:
    """
    Service to turn spider-discovered opportunities into actionable income.

    Flow:
    1. User sees opportunity in UI (from spider data)
    2. User clicks "Save & Apply"
    3. System saves to SavedOpportunity model
    4. System generates application materials
    5. User applies externally
    6. User records outcome (got job, rejected, no response)
    7. System learns from outcomes
    """

    def __init__(self):
        self.gpt_client = None

    def _get_gpt_client(self):
        """Lazy-load GPT client"""
        if self.gpt_client is None:
            try:
                self.gpt_client = get_openai_client()
            except Exception as e:
                logger.error(f"Failed to initialize GPT client: {e}")
        return self.gpt_client

    def save_opportunity(self, user, opportunity_data: Dict) -> Dict:
        """
        Save an opportunity from spider data for tracking.

        Args:
            user: The user saving the opportunity
            opportunity_data: Dict with title, url, source, description, etc.

        Returns:
            Dict with saved opportunity ID and status
        """
        from core.models_unified_system import SavedOpportunity

        try:
            # Check for duplicates
            existing = SavedOpportunity.objects.filter(
                user=user,
                source_url=opportunity_data.get('url', '')
            ).first()

            if existing:
                return {
                    'success': True,
                    'message': 'Opportunity already saved',
                    'opportunity_id': str(existing.id),
                    'is_duplicate': True
                }

            # Create new saved opportunity
            saved = SavedOpportunity.objects.create(
                user=user,
                title=opportunity_data.get('title', 'Untitled')[:200],
                source_url=opportunity_data.get('url', ''),
                source_platform=opportunity_data.get('source', 'unknown'),
                description=opportunity_data.get('description', '')[:2000],
                salary_info=opportunity_data.get('salary', ''),
                company_name=opportunity_data.get('company', ''),
                location=opportunity_data.get('location', 'Remote'),
                category=opportunity_data.get('category', 'general'),
                raw_data=opportunity_data,
                status='saved'
            )

            logger.info(f"Saved opportunity {saved.id} for user {user.id}")

            return {
                'success': True,
                'message': 'Opportunity saved!',
                'opportunity_id': str(saved.id),
                'is_duplicate': False
            }

        except Exception as e:
            logger.error(f"Error saving opportunity: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_user_profile(self, user) -> Dict:
        """Fetch user's ExtendedUserProfile from database and format for cover letter generation."""
        try:
            from core.models import ExtendedUserProfile
            profile = ExtendedUserProfile.objects.filter(user=user).first()

            if not profile:
                return None

            # Extract skill names from the JSON structure
            skills = []
            if profile.skills:
                for skill in profile.skills:
                    if isinstance(skill, dict):
                        skills.append(skill.get('name', ''))
                    elif isinstance(skill, str):
                        skills.append(skill)

            # Format work history summary
            work_summary = ""
            if profile.work_history:
                recent_jobs = profile.work_history[:3]  # Last 3 jobs
                for job in recent_jobs:
                    if isinstance(job, dict):
                        work_summary += f"- {job.get('title', '')} at {job.get('company', '')} ({job.get('duration', '')})\n"

            return {
                'full_name': profile.full_name or user.get_full_name() or user.username,
                'skills': skills,
                'experience_years': profile.years_experience,
                'current_title': profile.current_title,
                'location': profile.location,
                'remote_preference': profile.remote_preference,
                'work_history': work_summary,
                'portfolio_url': profile.portfolio_url,
                'linkedin_url': profile.linkedin_url,
                'github_username': profile.github_username,
                'profile_completeness': profile.profile_completeness,
            }
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return None

    def generate_application(self, opportunity_id: str, user_profile: Dict = None) -> Dict:
        """
        Generate application materials (cover letter/proposal) for an opportunity.

        Args:
            opportunity_id: ID of the saved opportunity
            user_profile: Optional user profile override. If not provided, fetches from database.

        Returns:
            Dict with generated application materials
        """
        from core.models_unified_system import SavedOpportunity

        try:
            opportunity = SavedOpportunity.objects.get(id=opportunity_id)
        except SavedOpportunity.DoesNotExist:
            return {'success': False, 'error': 'Opportunity not found'}

        client = self._get_gpt_client()
        if not client:
            return {'success': False, 'error': 'GPT client not available'}

        # If no profile passed in, fetch from database
        if not user_profile:
            user_profile = self._get_user_profile(opportunity.user)

        # Build context
        job_context = f"""
Title: {opportunity.title}
Company: {opportunity.company_name or 'Not specified'}
Location: {opportunity.location}
Description: {opportunity.description[:1000]}
Source: {opportunity.source_platform}
"""

        # Build user profile context - now much richer!
        profile_context = ""
        if user_profile:
            skills_str = ', '.join(user_profile.get('skills', [])) if user_profile.get('skills') else 'Not specified'
            profile_context = f"""
Name: {user_profile.get('full_name', 'Not specified')}
Current Role: {user_profile.get('current_title', 'Not specified')}
Skills: {skills_str}
Experience: {user_profile.get('experience_years', 0)} years
Location: {user_profile.get('location', 'Not specified')}
Remote Preference: {user_profile.get('remote_preference', 'flexible')}

Recent Experience:
{user_profile.get('work_history', 'Not specified')}

Portfolio: {user_profile.get('portfolio_url', 'Not provided')}
LinkedIn: {user_profile.get('linkedin_url', 'Not provided')}
GitHub: {user_profile.get('github_username', 'Not provided')}
"""
        else:
            profile_context = "Professional seeking remote work opportunities."

        try:
            # Generate cover letter/proposal
            # Note: gpt-5-mini needs reasoning_effort and high max_completion_tokens
            # since reasoning tokens come from the same budget
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert at writing compelling job applications and proposals.
Write concise, professional, and personalized application materials.
Focus on demonstrating relevant skills and enthusiasm.
Keep the tone confident but not arrogant."""
                    },
                    {
                        "role": "user",
                        "content": f"""Write a brief cover letter/proposal for this opportunity:

{job_context}

About the applicant:
{profile_context}

Requirements:
1. Keep it under 200 words
2. Be specific to the job
3. Highlight relevant skills
4. End with a clear call to action
5. Professional but personable tone"""
                    }
                ],
                max_completion_tokens=2000,  # High enough for reasoning + output
                reasoning_effort="low"  # Keep reasoning minimal for simple task
            )

            cover_letter = response.choices[0].message.content

            # Update opportunity with generated materials
            opportunity.application_materials = {
                'cover_letter': cover_letter,
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            opportunity.status = 'materials_ready'
            opportunity.save()

            return {
                'success': True,
                'cover_letter': cover_letter,
                'opportunity_id': str(opportunity.id)
            }

        except Exception as e:
            logger.error(f"Error generating application: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def update_status(self, opportunity_id: str, new_status: str, notes: str = None) -> Dict:
        """
        Update the status of a saved opportunity.

        Statuses:
        - saved: Just saved, no action taken
        - materials_ready: Application materials generated
        - applied: User has applied
        - interview: Got an interview
        - accepted: Got the job/gig
        - rejected: Was rejected
        - no_response: No response after reasonable time
        - withdrawn: User withdrew application
        """
        from core.models_unified_system import SavedOpportunity

        valid_statuses = [
            'saved', 'materials_ready', 'applied', 'interview',
            'accepted', 'rejected', 'no_response', 'withdrawn'
        ]

        if new_status not in valid_statuses:
            return {
                'success': False,
                'error': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
            }

        try:
            opportunity = SavedOpportunity.objects.get(id=opportunity_id)
            old_status = opportunity.status
            opportunity.status = new_status

            if notes:
                if not opportunity.notes:
                    opportunity.notes = ""
                opportunity.notes += f"\n[{datetime.now(timezone.utc).isoformat()}] {notes}"

            # Track timeline
            if new_status == 'applied':
                opportunity.applied_at = datetime.now(timezone.utc)
            elif new_status in ['accepted', 'rejected', 'no_response']:
                opportunity.resolved_at = datetime.now(timezone.utc)
                # Record outcome for learning
                self._record_outcome(opportunity, new_status)

            opportunity.save()

            return {
                'success': True,
                'message': f'Status updated from {old_status} to {new_status}',
                'opportunity_id': str(opportunity.id)
            }

        except SavedOpportunity.DoesNotExist:
            return {'success': False, 'error': 'Opportunity not found'}
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return {'success': False, 'error': str(e)}

    def _record_outcome(self, opportunity, outcome: str):
        """Record outcome for the learning system using LearningPattern"""
        from core.models_unified_system import LearningPattern

        try:
            # Calculate confidence based on outcome
            confidence = 1.0 if outcome == 'accepted' else 0.5 if outcome == 'rejected' else 0.3

            # Calculate days to outcome
            days_to_outcome = None
            if opportunity.applied_at and opportunity.resolved_at:
                days_to_outcome = (opportunity.resolved_at - opportunity.applied_at).days

            # Record as a learning pattern
            LearningPattern.objects.create(
                user=opportunity.user,
                pattern_type='application_outcome',
                description=f"Application to {opportunity.title} ({opportunity.source_platform}): {outcome}",
                confidence=confidence,
                pattern_data={
                    'opportunity_id': str(opportunity.id),
                    'opportunity_title': opportunity.title,
                    'platform': opportunity.source_platform,
                    'category': opportunity.category,
                    'outcome': outcome,
                    'days_to_outcome': days_to_outcome,
                    'company': opportunity.company_name,
                    'location': opportunity.location,
                }
            )

            logger.info(f"Recorded learning pattern: {outcome} for {opportunity.title}")

        except Exception as e:
            logger.error(f"Error recording outcome: {e}")

    def get_user_opportunities(self, user, status: str = None, limit: int = 50) -> List[Dict]:
        """
        Get saved opportunities for a user.

        Args:
            user: The user
            status: Optional status filter
            limit: Max results

        Returns:
            List of opportunity dicts
        """
        from core.models_unified_system import SavedOpportunity

        queryset = SavedOpportunity.objects.filter(user=user)

        if status:
            queryset = queryset.filter(status=status)

        queryset = queryset.order_by('-created_at')[:limit]

        return [
            {
                'id': str(opp.id),
                'title': opp.title,
                'source_url': opp.source_url,
                'source_platform': opp.source_platform,
                'company_name': opp.company_name,
                'location': opp.location,
                'status': opp.status,
                'has_materials': bool(opp.application_materials),
                'created_at': opp.created_at.isoformat() if opp.created_at else None,
                'applied_at': opp.applied_at.isoformat() if opp.applied_at else None,
            }
            for opp in queryset
        ]

    def get_statistics(self, user) -> Dict:
        """Get application statistics for a user"""
        from core.models_unified_system import SavedOpportunity
        from django.db.models import Count

        stats = SavedOpportunity.objects.filter(user=user).values('status').annotate(
            count=Count('id')
        )

        status_counts = {s['status']: s['count'] for s in stats}

        total = sum(status_counts.values())
        applied = status_counts.get('applied', 0) + status_counts.get('interview', 0) + \
                  status_counts.get('accepted', 0) + status_counts.get('rejected', 0) + \
                  status_counts.get('no_response', 0)
        accepted = status_counts.get('accepted', 0)

        success_rate = (accepted / applied * 100) if applied > 0 else 0

        return {
            'total_saved': total,
            'total_applied': applied,
            'total_accepted': accepted,
            'success_rate': round(success_rate, 1),
            'by_status': status_counts
        }


# Singleton accessor
_service_instance = None

def get_income_action_service() -> IncomeActionService:
    """Get singleton instance of IncomeActionService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = IncomeActionService()
    return _service_instance
