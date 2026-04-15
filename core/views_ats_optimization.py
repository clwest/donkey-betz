"""
ATS Optimization Views - Session 866
====================================

API endpoints for ATS keyword optimization and resume analysis.

Endpoints:
- POST /api/ats/analyze - Analyze resume against job description
- POST /api/ats/extract-keywords - Extract keywords from text
- POST /api/ats/optimize - Get optimization suggestions
- GET /api/ats/templates - List available persona templates
- POST /api/ats/generate-summary - Generate ATS-optimized summary
"""

import logging
import json
from typing import Dict, Any

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .services.ats_keyword_service import ats_keyword_service

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ATSAnalyzeView(View):
    """
    Analyze a resume against a job description.

    POST /api/ats/analyze
    Body: {
        "resume_text": "...",
        "job_description": "...",
        "include_suggestions": true
    }
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            resume_text = data.get('resume_text', '')
            job_description = data.get('job_description', '')
            include_suggestions = data.get('include_suggestions', True)

            if not resume_text:
                return JsonResponse({
                    'success': False,
                    'error': 'resume_text is required'
                }, status=400)

            if not job_description:
                return JsonResponse({
                    'success': False,
                    'error': 'job_description is required'
                }, status=400)

            # Score the match
            match_result = ats_keyword_service.score_resume_match(
                resume_text, job_description
            )

            response_data = {
                'success': True,
                'overall_score': match_result['overall_score'],
                'match_level': match_result['match_level'],
                'category_scores': match_result['category_scores'],
                'missing_keywords': match_result['missing_keywords'],
                'detected_industry': match_result.get('job_industry'),
            }

            # Add optimization suggestions if requested
            if include_suggestions:
                user_skills = []
                if request.user.is_authenticated:
                    try:
                        from .models import ExtendedUserProfile
                        profile = ExtendedUserProfile.objects.filter(user=request.user).first()
                        if profile and profile.skills:
                            user_skills = [s.get('name', '') for s in profile.skills]
                    except Exception as _e:
                        logger.warning(
                            "views_ats_optimization.post: swallowed (%s: %s) — degraded",
                            type(_e).__name__, _e,
                        )

                suggestions = ats_keyword_service.get_optimization_suggestions(
                    resume_text, job_description, user_skills
                )
                response_data['suggestions'] = suggestions

            # Log for conversion tracking (if user authenticated)
            if request.user.is_authenticated:
                self._log_analysis(request.user, match_result, data)

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"ATS analysis error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    def _log_analysis(self, user, match_result, data):
        """Log analysis for conversion tracking."""
        try:
            from .models_ats_optimization import ResumeOptimizationLog

            ResumeOptimizationLog.objects.create(
                user=user,
                job_title_target=data.get('job_title', ''),
                industry=match_result.get('job_industry', ''),
                initial_ats_score=match_result['overall_score'],
                missing_keywords_count=len(match_result['missing_keywords']),
                current_stage='analyzed'
            )
        except Exception as e:
            logger.warning(f"Failed to log analysis: {e}")


@method_decorator(csrf_exempt, name='dispatch')
class ATSExtractKeywordsView(View):
    """
    Extract keywords from text.

    POST /api/ats/extract-keywords
    Body: {
        "text": "...",
        "use_llm": false
    }
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            use_llm = data.get('use_llm', False)

            if not text:
                return JsonResponse({
                    'success': False,
                    'error': 'text is required'
                }, status=400)

            result = ats_keyword_service.extract_keywords(text, use_llm=use_llm)

            return JsonResponse({
                'success': True,
                'keywords': result['keywords'],
                'categories': result['categories'],
                'total_count': result['total_count'],
                'detected_industry': result.get('detected_industry'),
                'extraction_method': result['extraction_method']
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ATSOptimizeSuggestionsView(View):
    """
    Get optimization suggestions for a resume.

    POST /api/ats/optimize
    Body: {
        "resume_text": "...",
        "job_description": "...",
        "user_skills": ["python", "django", ...]  // optional
    }
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            resume_text = data.get('resume_text', '')
            job_description = data.get('job_description', '')
            user_skills = data.get('user_skills', [])

            if not resume_text or not job_description:
                return JsonResponse({
                    'success': False,
                    'error': 'resume_text and job_description are required'
                }, status=400)

            # Get user skills from profile if not provided
            if not user_skills and request.user.is_authenticated:
                try:
                    from .models import ExtendedUserProfile
                    profile = ExtendedUserProfile.objects.filter(user=request.user).first()
                    if profile and profile.skills:
                        user_skills = [s.get('name', '') for s in profile.skills]
                except Exception as _e:
                    logger.warning(
                        "views_ats_optimization.post: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            suggestions = ats_keyword_service.get_optimization_suggestions(
                resume_text, job_description, user_skills
            )

            return JsonResponse({
                'success': True,
                **suggestions
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"Optimization suggestions error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ATSTemplatesView(View):
    """
    List available persona resume templates.

    GET /api/ats/templates
    Query params:
        - industry: Filter by industry
        - experience_level: Filter by experience level
        - type: Filter by template type (free_guide, paid_basic, etc.)
    """

    def get(self, request):
        try:
            from .models_ats_optimization import PersonaResumeTemplate

            queryset = PersonaResumeTemplate.objects.filter(is_active=True)

            # Apply filters
            industry = request.GET.get('industry')
            if industry:
                queryset = queryset.filter(industry=industry)

            experience_level = request.GET.get('experience_level')
            if experience_level:
                queryset = queryset.filter(experience_level=experience_level)

            template_type = request.GET.get('type')
            if template_type:
                queryset = queryset.filter(template_type=template_type)

            templates = []
            for t in queryset[:50]:
                templates.append({
                    'id': str(t.id),
                    'name': t.name,
                    'slug': t.slug,
                    'description': t.description,
                    'industry': t.industry,
                    'experience_level': t.experience_level,
                    'target_roles': t.target_roles,
                    'template_type': t.template_type,
                    'price': t.get_price_display(),
                    'price_cents': t.price_cents,
                    'downloads': t.downloads,
                    'avg_score_improvement': t.avg_ats_score_improvement,
                })

            return JsonResponse({
                'success': True,
                'templates': templates,
                'count': len(templates),
                'industries': [c[0] for c in PersonaResumeTemplate.INDUSTRY_CHOICES],
                'experience_levels': [c[0] for c in PersonaResumeTemplate.EXPERIENCE_LEVEL_CHOICES],
            })

        except Exception as e:
            logger.error(f"Templates list error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ATSGenerateSummaryView(View):
    """
    Generate an ATS-optimized professional summary.

    POST /api/ats/generate-summary
    Body: {
        "job_description": "...",
        "user_profile": {...},  // or will use authenticated user's profile
        "style": "professional"  // professional, creative, technical
    }
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            job_description = data.get('job_description', '')
            style = data.get('style', 'professional')

            if not job_description:
                return JsonResponse({
                    'success': False,
                    'error': 'job_description is required'
                }, status=400)

            # Get user profile
            user_profile = data.get('user_profile', {})

            if not user_profile and request.user.is_authenticated:
                try:
                    from .models import ExtendedUserProfile
                    profile = ExtendedUserProfile.objects.filter(user=request.user).first()
                    if profile:
                        user_profile = {
                            'title': profile.professional_title or profile.current_role or 'Professional',
                            'years_experience': profile.years_experience,
                            'skills': [s.get('name', '') for s in (profile.skills or [])],
                            'industry': profile.industry,
                        }
                except Exception as _e:
                    logger.warning(
                        "views_ats_optimization.post: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            if not user_profile:
                user_profile = {
                    'title': 'Professional',
                    'years_experience': '',
                    'skills': [],
                }

            summary = ats_keyword_service.generate_ats_optimized_summary(
                user_profile, job_description, style
            )

            return JsonResponse({
                'success': True,
                'summary': summary,
                'style': style,
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON body'
            }, status=400)
        except Exception as e:
            logger.error(f"Summary generation error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator([csrf_exempt, login_required], name='dispatch')
class ATSConversionStatsView(View):
    """
    Get conversion statistics for ATS optimization (admin only).

    GET /api/ats/stats
    """

    def get(self, request):
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Admin access required'
            }, status=403)

        try:
            from .models_ats_optimization import ResumeOptimizationLog, ResumeRewriteOrder
            from django.db.models import Count, Avg, Sum

            # Funnel stats
            stage_counts = ResumeOptimizationLog.objects.values('current_stage').annotate(
                count=Count('id')
            )
            funnel = {s['current_stage']: s['count'] for s in stage_counts}

            # Revenue stats
            revenue_stats = ResumeRewriteOrder.objects.filter(
                status__in=['paid', 'completed']
            ).aggregate(
                total_revenue=Sum('price_cents'),
                total_orders=Count('id'),
                avg_order_value=Avg('price_cents')
            )

            # Score improvement stats
            score_stats = ResumeOptimizationLog.objects.filter(
                initial_ats_score__isnull=False,
                final_ats_score__isnull=False
            ).aggregate(
                avg_initial=Avg('initial_ats_score'),
                avg_final=Avg('final_ats_score'),
                count=Count('id')
            )

            # A/B test stats
            ab_stats = ResumeOptimizationLog.objects.exclude(
                ab_test_variant=''
            ).values('ab_test_variant', 'current_stage').annotate(
                count=Count('id')
            )

            return JsonResponse({
                'success': True,
                'funnel': funnel,
                'revenue': {
                    'total_cents': revenue_stats['total_revenue'] or 0,
                    'total_orders': revenue_stats['total_orders'] or 0,
                    'avg_order_cents': revenue_stats['avg_order_value'] or 0,
                },
                'score_improvement': {
                    'avg_initial': score_stats['avg_initial'] or 0,
                    'avg_final': score_stats['avg_final'] or 0,
                    'sample_size': score_stats['count'] or 0,
                },
                'ab_tests': list(ab_stats),
            })

        except Exception as e:
            logger.error(f"Stats error: {e}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
