"""
Provenance URL Configuration
============================

Session 295: URL routing for provenance, audit, originality, and marketplace APIs.

Include in core/urls.py:
    path('api/provenance/', include('core.urls_provenance')),
"""

from django.urls import path
from core import views_provenance

app_name = 'provenance'

urlpatterns = [
    # ==========================================================================
    # Provenance endpoints
    # ==========================================================================
    path('create/', views_provenance.create_provenance, name='create'),
    path('<uuid:provenance_id>/', views_provenance.get_provenance, name='detail'),
    path('<uuid:provenance_id>/certificate/', views_provenance.get_certificate, name='certificate'),
    path('<uuid:provenance_id>/certificate/download/', views_provenance.download_certificate, name='certificate_download'),
    path('verify/', views_provenance.verify_provenance, name='verify'),
    path('similar/', views_provenance.find_similar, name='similar'),

    # ==========================================================================
    # Audit endpoints
    # ==========================================================================
    path('audit/prompt/', views_provenance.audit_prompt, name='audit_prompt'),
    path('audit/<uuid:provenance_id>/', views_provenance.get_audit, name='audit_detail'),
    path('audit/<uuid:audit_id>/transparency/', views_provenance.get_transparency_card, name='transparency'),

    # ==========================================================================
    # Originality endpoints
    # ==========================================================================
    path('originality/analyze/', views_provenance.analyze_originality, name='originality_analyze'),
    path('originality/<uuid:provenance_id>/', views_provenance.get_originality_score, name='originality_detail'),
    path('originality/alternatives/', views_provenance.get_alternative_prompts, name='originality_alternatives'),

    # ==========================================================================
    # Marketplace endpoints
    # ==========================================================================
    path('marketplace/fit/<uuid:provenance_id>/', views_provenance.get_market_fit, name='market_fit'),
    path('marketplace/platforms/<uuid:provenance_id>/', views_provenance.get_platform_suggestions, name='platforms'),
    path('marketplace/opportunities/', views_provenance.get_trending_opportunities, name='opportunities'),
    path('marketplace/hashtags/', views_provenance.generate_hashtags, name='hashtags'),

    # ==========================================================================
    # Watermark endpoints
    # ==========================================================================
    path('watermark/verify/', views_provenance.verify_watermark, name='watermark_verify'),
    path('watermark/extract/', views_provenance.extract_watermark, name='watermark_extract'),
]
