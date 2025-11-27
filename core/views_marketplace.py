"""
Workflow Marketplace API Endpoints
===================================

Session 219 Phase D: API endpoints for workflow marketplace.

Endpoints:
- GET /api/marketplace/workflows/ - Browse all published workflows
- GET /api/marketplace/workflows/featured/ - Get featured workflows
- GET /api/marketplace/workflows/trending/ - Get trending workflows
- GET /api/marketplace/workflows/{id}/ - Get workflow details
- POST /api/marketplace/workflows/{id}/install/ - Install workflow to my collection
- POST /api/marketplace/publish/ - Publish a workflow
- POST /api/marketplace/reviews/ - Add review
- GET /api/marketplace/reviews/{workflow_id}/ - Get reviews for workflow
- GET /api/marketplace/my-published/ - Get my published workflows
- GET /api/marketplace/my-installed/ - Get my installed workflows
- GET /api/marketplace/stats/ - Get marketplace stats
"""

import json
import logging
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.utils.text import slugify

from core.models_unified_system import (
    CustomWorkflow,
    CustomWorkflowStep,
    PublishedWorkflow,
    WorkflowReview,
    WorkflowInstallation
)

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@login_required
def browse_workflows(request):
    """
    Browse all published workflows.

    GET /api/marketplace/workflows/

    Query params:
    - category: Filter by category
    - search: Search in title/description
    - sort: Sort by (popular, recent, rating)
    - page: Page number
    - limit: Results per page
    """
    try:
        category = request.GET.get('category')
        search = request.GET.get('search')
        sort = request.GET.get('sort', 'popular')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))

        # Base query - only approved workflows
        workflows = PublishedWorkflow.objects.filter(status='approved')

        # Apply filters
        if category:
            workflows = workflows.filter(category=category)

        if search:
            workflows = workflows.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__contains=[search])
            )

        # Apply sorting
        if sort == 'popular':
            workflows = workflows.order_by('-download_count', '-view_count')
        elif sort == 'recent':
            workflows = workflows.order_by('-published_at')
        elif sort == 'rating':
            workflows = workflows.order_by('-average_rating', '-review_count')
        else:
            workflows = workflows.order_by('-is_featured', '-download_count')

        # Pagination
        total = workflows.count()
        offset = (page - 1) * limit
        workflows = workflows[offset:offset + limit]

        # Serialize
        results = []
        for w in workflows:
            results.append({
                'id': str(w.id),
                'title': w.title,
                'short_description': w.short_description or w.description[:150] + '...',
                'category': w.category,
                'category_display': dict(PublishedWorkflow.CATEGORY_CHOICES).get(w.category, w.category),
                'tags': w.tags,
                'preview_image': w.preview_image,
                'download_count': w.download_count,
                'average_rating': round(w.average_rating, 1),
                'review_count': w.review_count,
                'is_featured': w.is_featured,
                'is_free': w.is_free,
                'author': {
                    'id': w.author.id,
                    'username': w.author.username
                },
                'published_at': w.published_at.isoformat()
            })

        return JsonResponse({
            'success': True,
            'workflows': results,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })

    except Exception as e:
        logger.error(f"Error browsing workflows: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def featured_workflows(request):
    """
    Get featured workflows.

    GET /api/marketplace/workflows/featured/
    """
    try:
        workflows = PublishedWorkflow.objects.filter(
            status='approved',
            is_featured=True
        ).order_by('-download_count')[:10]

        results = [{
            'id': str(w.id),
            'title': w.title,
            'short_description': w.short_description or w.description[:100],
            'category': w.category,
            'preview_image': w.preview_image,
            'download_count': w.download_count,
            'average_rating': round(w.average_rating, 1),
            'author': {
                'username': w.author.username
            }
        } for w in workflows]

        return JsonResponse({
            'success': True,
            'workflows': results
        })

    except Exception as e:
        logger.error(f"Error getting featured workflows: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def trending_workflows(request):
    """
    Get trending workflows (most downloads recently).

    GET /api/marketplace/workflows/trending/
    """
    try:
        # Trending = most downloaded in last 7 days (approximated by recent + popular)
        workflows = PublishedWorkflow.objects.filter(
            status='approved'
        ).order_by('-download_count', '-view_count')[:10]

        results = [{
            'id': str(w.id),
            'title': w.title,
            'short_description': w.short_description or w.description[:100],
            'category': w.category,
            'preview_image': w.preview_image,
            'download_count': w.download_count,
            'average_rating': round(w.average_rating, 1),
            'author': {
                'username': w.author.username
            }
        } for w in workflows]

        return JsonResponse({
            'success': True,
            'workflows': results
        })

    except Exception as e:
        logger.error(f"Error getting trending workflows: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def workflow_details(request, workflow_id: str):
    """
    Get workflow details.

    GET /api/marketplace/workflows/{workflow_id}/
    """
    try:
        workflow = PublishedWorkflow.objects.get(id=workflow_id, status='approved')

        # Increment view count
        workflow.increment_view()

        # Get workflow steps
        steps = []
        if workflow.workflow:
            for step in workflow.workflow.steps.all().order_by('order'):
                steps.append({
                    'order': step.order,
                    'name': step.name,
                    'agent': step.agent,
                    'description': step.description
                })

        # Check if user has installed
        is_installed = WorkflowInstallation.objects.filter(
            published_workflow=workflow,
            user=request.user
        ).exists()

        # Check if user has reviewed
        user_review = None
        try:
            review = WorkflowReview.objects.get(
                published_workflow=workflow,
                user=request.user
            )
            user_review = {
                'rating': review.rating,
                'review_text': review.review_text,
                'created_at': review.created_at.isoformat()
            }
        except WorkflowReview.DoesNotExist:
            pass

        return JsonResponse({
            'success': True,
            'workflow': {
                'id': str(workflow.id),
                'title': workflow.title,
                'description': workflow.description,
                'short_description': workflow.short_description,
                'category': workflow.category,
                'category_display': dict(PublishedWorkflow.CATEGORY_CHOICES).get(workflow.category),
                'tags': workflow.tags,
                'preview_image': workflow.preview_image,
                'preview_images': workflow.preview_images,
                'download_count': workflow.download_count,
                'view_count': workflow.view_count,
                'average_rating': round(workflow.average_rating, 1),
                'review_count': workflow.review_count,
                'is_featured': workflow.is_featured,
                'is_free': workflow.is_free,
                'price': float(workflow.price),
                'author': {
                    'id': workflow.author.id,
                    'username': workflow.author.username
                },
                'steps': steps,
                'step_count': len(steps),
                'published_at': workflow.published_at.isoformat(),
                'is_installed': is_installed,
                'user_review': user_review
            }
        })

    except PublishedWorkflow.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting workflow details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def install_workflow(request, workflow_id: str):
    """
    Install a workflow to user's collection.

    POST /api/marketplace/workflows/{workflow_id}/install/
    """
    try:
        published_workflow = PublishedWorkflow.objects.get(id=workflow_id, status='approved')

        # Check if already installed
        existing = WorkflowInstallation.objects.filter(
            published_workflow=published_workflow,
            user=request.user
        ).first()

        if existing:
            return JsonResponse({
                'success': True,
                'message': 'Workflow already installed',
                'workflow_id': str(existing.installed_workflow.id) if existing.installed_workflow else None
            })

        # Clone the workflow
        original = published_workflow.workflow
        cloned = CustomWorkflow.objects.create(
            created_by=request.user,
            name=f"{original.name} (from Marketplace)",
            slug=slugify(f"{original.name}-{request.user.id}-{timezone.now().strftime('%Y%m%d')}"),
            description=original.description,
            content_type=original.content_type,
            category=original.category,
            config=original.config,
            status='active'
        )

        # Clone steps
        for step in original.steps.all():
            CustomWorkflowStep.objects.create(
                workflow=cloned,
                order=step.order,
                name=step.name,
                description=step.description,
                agent=step.agent,
                config=step.config,
                condition=step.condition,
                is_required=step.is_required,
                retry_count=step.retry_count
            )

        # Record installation
        installation = WorkflowInstallation.objects.create(
            published_workflow=published_workflow,
            user=request.user,
            installed_workflow=cloned
        )

        # Increment download count
        published_workflow.increment_download()

        return JsonResponse({
            'success': True,
            'message': 'Workflow installed successfully',
            'workflow_id': str(cloned.id),
            'installation_id': str(installation.id)
        })

    except PublishedWorkflow.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error installing workflow: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def publish_workflow(request):
    """
    Publish a workflow to the marketplace.

    POST /api/marketplace/publish/

    Body:
    {
        "workflow_id": "uuid",
        "title": "My Awesome Workflow",
        "description": "Full description...",
        "short_description": "Brief summary",
        "category": "image_generation",
        "tags": ["logo", "branding"],
        "preview_image": "https://..."
    }
    """
    try:
        body = json.loads(request.body)

        workflow_id = body.get('workflow_id')
        if not workflow_id:
            return JsonResponse({
                'success': False,
                'error': 'workflow_id is required'
            }, status=400)

        # Get the workflow and verify ownership
        workflow = CustomWorkflow.objects.get(
            id=workflow_id,
            created_by=request.user
        )

        # Check if already published
        if hasattr(workflow, 'publication'):
            return JsonResponse({
                'success': False,
                'error': 'Workflow is already published'
            }, status=400)

        # Create publication
        publication = PublishedWorkflow.objects.create(
            workflow=workflow,
            author=request.user,
            title=body.get('title', workflow.name),
            description=body.get('description', workflow.description),
            short_description=body.get('short_description', ''),
            category=body.get('category', 'other'),
            tags=body.get('tags', []),
            preview_image=body.get('preview_image', ''),
            preview_images=body.get('preview_images', [])
        )

        # Mark workflow as public
        workflow.is_public = True
        workflow.save(update_fields=['is_public'])

        return JsonResponse({
            'success': True,
            'publication_id': str(publication.id),
            'message': 'Workflow published successfully'
        })

    except CustomWorkflow.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Workflow not found or you do not own it'
        }, status=404)
    except Exception as e:
        logger.error(f"Error publishing workflow: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
@login_required
def add_review(request):
    """
    Add a review to a published workflow.

    POST /api/marketplace/reviews/

    Body:
    {
        "workflow_id": "uuid",
        "rating": 5,
        "review_text": "Great workflow!"
    }
    """
    try:
        body = json.loads(request.body)

        workflow_id = body.get('workflow_id')
        rating = body.get('rating')

        if not workflow_id or not rating:
            return JsonResponse({
                'success': False,
                'error': 'workflow_id and rating are required'
            }, status=400)

        if not (1 <= rating <= 5):
            return JsonResponse({
                'success': False,
                'error': 'Rating must be between 1 and 5'
            }, status=400)

        published_workflow = PublishedWorkflow.objects.get(id=workflow_id)

        # Check if user has installed (verified purchase)
        is_verified = WorkflowInstallation.objects.filter(
            published_workflow=published_workflow,
            user=request.user
        ).exists()

        # Create or update review
        review, created = WorkflowReview.objects.update_or_create(
            published_workflow=published_workflow,
            user=request.user,
            defaults={
                'rating': rating,
                'review_text': body.get('review_text', ''),
                'is_verified_purchase': is_verified
            }
        )

        return JsonResponse({
            'success': True,
            'review_id': str(review.id),
            'message': 'Review added' if created else 'Review updated',
            'is_verified': is_verified
        })

    except PublishedWorkflow.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Workflow not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error adding review: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_reviews(request, workflow_id: str):
    """
    Get reviews for a workflow.

    GET /api/marketplace/reviews/{workflow_id}/
    """
    try:
        reviews = WorkflowReview.objects.filter(
            published_workflow_id=workflow_id
        ).order_by('-helpful_count', '-created_at')[:50]

        results = [{
            'id': str(r.id),
            'rating': r.rating,
            'review_text': r.review_text,
            'helpful_count': r.helpful_count,
            'is_verified_purchase': r.is_verified_purchase,
            'user': {
                'username': r.user.username
            },
            'created_at': r.created_at.isoformat()
        } for r in reviews]

        return JsonResponse({
            'success': True,
            'reviews': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Error getting reviews: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def my_published_workflows(request):
    """
    Get workflows I have published.

    GET /api/marketplace/my-published/
    """
    try:
        publications = PublishedWorkflow.objects.filter(
            author=request.user
        ).order_by('-published_at')

        results = [{
            'id': str(p.id),
            'title': p.title,
            'category': p.category,
            'status': p.status,
            'download_count': p.download_count,
            'average_rating': round(p.average_rating, 1),
            'review_count': p.review_count,
            'published_at': p.published_at.isoformat()
        } for p in publications]

        return JsonResponse({
            'success': True,
            'publications': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Error getting my published workflows: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def my_installed_workflows(request):
    """
    Get workflows I have installed.

    GET /api/marketplace/my-installed/
    """
    try:
        installations = WorkflowInstallation.objects.filter(
            user=request.user
        ).select_related('published_workflow', 'installed_workflow').order_by('-installed_at')

        results = [{
            'id': str(i.id),
            'published_workflow': {
                'id': str(i.published_workflow.id),
                'title': i.published_workflow.title,
                'author': i.published_workflow.author.username
            } if i.published_workflow else None,
            'installed_workflow_id': str(i.installed_workflow.id) if i.installed_workflow else None,
            'times_executed': i.times_executed,
            'last_executed': i.last_executed.isoformat() if i.last_executed else None,
            'installed_at': i.installed_at.isoformat()
        } for i in installations]

        return JsonResponse({
            'success': True,
            'installations': results,
            'count': len(results)
        })

    except Exception as e:
        logger.error(f"Error getting my installed workflows: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def marketplace_stats(request):
    """
    Get marketplace statistics.

    GET /api/marketplace/stats/
    """
    try:
        total_workflows = PublishedWorkflow.objects.filter(status='approved').count()
        total_downloads = PublishedWorkflow.objects.filter(status='approved').aggregate(
            total=Count('download_count')
        )['total'] or 0

        # Category breakdown
        categories = PublishedWorkflow.objects.filter(status='approved').values(
            'category'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        category_stats = {
            c['category']: c['count'] for c in categories
        }

        # Top authors
        top_authors = PublishedWorkflow.objects.filter(status='approved').values(
            'author__username'
        ).annotate(
            workflow_count=Count('id'),
            total_downloads=Count('download_count')
        ).order_by('-workflow_count')[:5]

        return JsonResponse({
            'success': True,
            'stats': {
                'total_workflows': total_workflows,
                'total_downloads': total_downloads,
                'categories': category_stats,
                'top_authors': list(top_authors)
            }
        })

    except Exception as e:
        logger.error(f"Error getting marketplace stats: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def get_categories(request):
    """
    Get available categories.

    GET /api/marketplace/categories/
    """
    try:
        categories = [
            {'value': value, 'label': label}
            for value, label in PublishedWorkflow.CATEGORY_CHOICES
        ]

        return JsonResponse({
            'success': True,
            'categories': categories
        })

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
