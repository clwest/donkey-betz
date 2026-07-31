"""
Unified Authentication Middleware
Ensures consistent token validation and security policies across all API endpoints
"""

import logging
from typing import Optional
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs

# T-ENVELOPE-2-DEPRECATION Batch 2 (S3007, ADR-0007 §4.3): error responses
# migrated from Family B (api_unauthorized/api_forbidden/api_error) to
# Family E via emit_error_envelope() helper (safety-contract §3.1). Existing
# f-string operator logs preserved for username/path context; the helper
# emits the structured envelope_emit warning with reason_code + support_code
# + hint. S3009 B1: all 10 sites now use the helper (0 raw-pattern sites).
from core.security.error_envelope import emit_error_envelope
from functools import wraps

logger = logging.getLogger(__name__)


class TokenValidationInfrastructureError(Exception):
    """Raised by `validate_token` when the auth backend (Postgres/Redis/cache)
    is unreachable during token lookup.

    Session 1171 #4: the previous implementation swallowed all non-
    `Token.DoesNotExist` exceptions in `validate_token` and returned None,
    producing false 401 'Invalid authentication token' responses during
    Postgres pressure events. This typed exception lets callers
    distinguish 'no such token' (401) from 'backend down' (503).
    """


def token_auth_required(view_func):
    """
    Decorator that ensures Token authentication for API views.

    Works for paths in PUBLIC_PATHS that bypass the middleware.
    Supports both session auth and Token auth.

    Usage:
        @token_auth_required
        def my_view(request):
            # request.user is guaranteed to be authenticated
            ...

    Session 891: Created to provide consistent Token auth across all API endpoints.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if already authenticated via session
        if hasattr(request, 'user') and request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        # Try Token auth
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
                    return view_func(request, *args, **kwargs)
            except Token.DoesNotExist:
                pass
        elif auth_header.startswith('Bearer '):
            token_key = auth_header.split(' ', 1)[1]
            try:
                token = Token.objects.select_related('user').get(key=token_key)
                if token.user.is_active:
                    request.user = token.user
                    return view_func(request, *args, **kwargs)
            except Token.DoesNotExist:
                pass

        # No valid auth found
        return emit_error_envelope(
            reason_code='not_authenticated',
            request=request,
            hint={'source': 'decorator_missing_token'},
        )

    # S3018 route-decorator invariant marker (Rigby T0 SIGN §2 recommendation):
    # marker + unwrap traversal is more robust than __wrapped__-only detection.
    # The invariant test (tests/security/test_public_paths_gate_invariant_s3018.py)
    # walks __wrapped__ chains looking for this attribute to classify views under
    # a PUBLIC_PATHS bare-prefix as gated.
    _wrapped_view._auth_gate = 'token_required'  # type: ignore[attr-defined]

    return _wrapped_view
User = get_user_model()


class UnifiedTokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Unified token authentication middleware for HTTP requests
    Provides consistent token validation across all API endpoints
    """
    
    # Session 528: SECURITY HARDENING - Reduced PUBLIC_PATHS to truly public endpoints only
    # Previously 48 paths were exempt from auth - now only essential endpoints are public
    # All other /api/ endpoints now require session auth OR token auth
    PUBLIC_PATHS = [
        # Health & Status (truly public)
        '/api/v1/health/',  # Health check endpoint
        '/health/',  # Health check
        '/api/app/manifest/',  # Deploy verification (returns minimal payload when unauthed)

        # Authentication endpoints (must be public to allow login/register)
        '/api/v1/auth/login/',  # Login endpoint
        '/api/v1/auth/register/',  # Registration endpoint
        '/api/v1/auth/validate-token/',  # Token validation (mobile hydration)
        '/api/v1/auth/forgot-password/',  # Password reset request
        '/api/v1/auth/reset-password/',  # Password reset confirmation
        '/api/v1/auth/debug/',  # Session 830: Auth debugging endpoint
        '/api-auth/',  # DRF browsable API auth

        # Webhooks with their own verification (use secrets/signatures)
        '/api/discord/verify-link-code/',  # Discord bot verification (uses bot_secret)
        '/api/stripe/webhook/',  # Stripe webhook (uses signature verification)
        # Session 1249 P2(a): db_health_tool prod RPC. View enforces
        # service-token auth via PA_DB_HEALTH_RPC_TOKEN env var; unset
        # token returns 404 (endpoint disabled). NOT user-bound.
        '/api/db-health-rpc/',

        # Django admin (has its own auth)
        '/admin/',

        # Public statistics (intentionally anonymous)
        '/api/public-stats/',  # Explicitly public stats

        # Session 538: Intelligence APIs (read-only, non-sensitive, used by UI Command Center)
        '/api/spider-intelligence/dashboard-stats/',  # Spider statistics
        '/api/spider-intelligence/detail/',  # Spider detail panel
        '/api/agent-intelligence/detail/',  # Agent detail panel
        '/api/situation-intelligence/detail/',  # Situation detail panel
        '/api/intelligence/cross-references/',  # Cross-reference mappings
        '/api/autonomous/situations/',  # Situations list for Command Center
        '/api/autonomous/trigger-events/',  # Trigger events for Command Center
        # S3052 PR 4: '/api/agents/' removed from PUBLIC_PATHS — now operator-only
        # via @require_operator_role on all_agents_list (Gap 6). Removing here
        # allows UnifiedTokenAuthenticationMiddleware to resolve token headers so
        # operator token callers reach the view; without this, PUBLIC_PATHS
        # short-circuits token resolution and the decorator sees AnonymousUser.
        '/api/agent-conversations/',  # Session 564: Conversations sub-tab
        '/api/conversation-contract/',  # Session 717: Conversation Contract Analytics
        '/api/agent-dreams/',  # Session 564: Dreams sub-tab
        '/api/boardroom/',  # Session 564: Boardroom sub-tab
        '/api/pilot-gates/',  # Session 590: Pilot Readiness Gates
        '/api/pilots/',  # Session 690: Pilot Implementation Pipeline
        '/api/pilot-experiments/',  # Session 692: Pilot Experiments for Command Center
        '/api/celery/',  # Session 660: Celery Task Monitor
        '/api/icc/',  # Session 660: ICC Health Dashboard
        '/api/artifacts/',  # Session 564: Artifacts sub-tab
        '/api/agent-learning/',  # Session 564: Learning activity
        '/api/recent-activity/',  # Session 614: Recent Activity panel
        '/api/experiment-recommendations/',  # Session 615: Experiment Recommendations

        # Session 542: Research Demo APIs (read-only visualization for research presentations)
        '/api/v1/research/network-graph/',  # D3.js graph data
        '/api/v1/research/live-feed/',  # Learning event feed
        '/api/v1/research/stats/',  # Pipeline statistics
        '/api/v1/research/mythology-gate/',  # Quarantine visualization
        # Session 543: Self-Blog APIs
        '/api/v1/research/self-blog/',  # Get latest self-blog
        '/api/v1/research/self-blog/generate/',  # Generate new self-blog
        '/api/v1/research/self-blog/task/',  # Check task status (prefix match)
        # Session 588: System Insights API
        '/api/v1/research/system-insights/',  # System insights from ThinkingAgent
        # Session 622: Deliverables API
        '/api/v1/research/deliverables/',  # Synthesized deliverables from research pipeline
        # Session 622: Document Registry / Initiatives API
        '/api/v1/initiatives/',  # View initiatives and their stages
        '/api/v1/initiatives/populate/',  # Auto-populate from deliverables
        # Session 912: Initiative Action Items API (non-versioned)
        # S3015 hotfix: `/api/initiatives/` moved to OPTIONAL_AUTH_PATHS below so
        # Token-authenticated callers get their scoped results. Bare-prefix PUBLIC
        # meant every /api/initiatives/* request was treated anonymous, causing
        # `scope_queryset_initiative` to return .none() for Token-auth browsers.
        '/api/action-items/',  # Bulk action item operations

        # Session 544: Autonomous Reasoning Engine APIs
        '/api/v1/reasoning/thoughts/',  # View thought records
        '/api/v1/reasoning/actions/',  # View autonomous actions
        '/api/v1/reasoning/trigger/',  # Trigger thinking cycle
        '/api/v1/reasoning/task/',  # Check task status
        '/api/v1/reasoning/config/',  # View/update config
        '/api/v1/reasoning/dashboard/',  # Dashboard data

        # Session 546: Concern Tracking APIs
        '/api/v1/reasoning/concerns/',  # Concern dashboard

        # Session 558: Prediction Markets & Sports Odds API (read-only for Command Center)
        '/api/prediction-markets/',  # Kalshi prediction market data
        '/api/sports-odds/',  # The Odds API sports betting data

        # Session 559: Betting Dashboard APIs (read-only for web UI)
        '/api/v1/betting/arbitrage/',  # Arbitrage scanning
        '/api/v1/sports/live-odds/',  # Live sports odds
        '/api/v1/sports/live-odds-scores/',  # Session 563: Live odds with ESPN scores
        '/api/v1/sports/events/',  # Session 563: Player props (matches /events/{id}/props/)
        '/api/v1/odds/bankroll/',  # Bankroll stats (read-only)
        # Session 560: Futures odds
        '/api/v1/betting/futures/',  # Championship futures
        # Session 561: Line Movement Charts
        '/api/v1/betting/line-movement/',  # Line movement data
        '/api/v1/betting/movers/',  # Games with significant movement
        # Session 562: Push Notifications (public key is public, subscribe needs to work for anon)
        '/api/v1/push/vapid-key/',  # VAPID public key for subscription
        '/api/v1/push/subscribe/',  # Allow anonymous subscriptions
        '/api/v1/push/unsubscribe/',  # Allow anonymous unsubscribe

        # Session 563: Bet Tracking (allow anonymous for demo mode)
        '/api/v1/betting/place/',  # Place bets
        '/api/v1/betting/wagers/',  # View wagers
        '/api/v1/betting/stats/',  # View stats
        '/api/v1/betting/recent/',  # Recent activity

        # Session 641: Agent Performance Dashboard APIs
        '/api/agent-analytics/',  # All agent analytics endpoints
        '/api/system-health/',  # System health check
        '/api/system/demo-status/',  # Session 1090: Demo mode banner
        '/api/agents/test/',  # Test agent execution

        # Session 761: Agent Monitoring Dashboard APIs
        '/api/v1/agents/monitoring/',  # Monitoring dashboard, alerts, agent detail

        # Session 642: Celery Monitoring
        '/api/celery/',  # Celery status endpoint

        # Session 687: Dashboard APIs (read-only stats for React frontend)
        '/api/ecosystem/stats/',  # Ecosystem statistics
        '/api/ecosystem/live-feed/',  # Live activity feed
        '/api/dashboard/stats/',  # Dashboard statistics
        '/api/v1/intelligence/spider-status/',  # Spider status
        '/api/spider-intelligence/report/',  # Daily spider report

        # Session 688: Agents Page APIs (read-only for React frontend)
        '/api/v1/agents/comprehensive/',  # Agent list with categories
        '/api/v1/agents/list/',  # Basic agent list
        '/api/v1/agents/health/',  # Agent health status
        '/api/recent-activity/',  # Recent system activity feed
        '/api/agent-learning/',  # Learning activity feed

        # Session 688: Intelligence Page APIs (read-only for React frontend)
        '/api/v1/intelligence/skynet/status/',  # Skynet intelligence status
        '/api/v1/intelligence/opportunities/',  # Opportunities list
        '/api/v1/intelligence/predictions/',  # AI predictions
        '/api/pilots/',  # Pilots dashboard and list
        '/api/experiments/',  # Experiments list
        '/api/opportunities/',  # Session 688: Opportunities list and detail

        # Session 688: Betting Page APIs (read-only for React frontend)
        '/api/v1/betting/stats/',  # Betting statistics
        '/api/v1/betting/wagers/',  # User wagers
        '/api/v1/betting/arbitrage/',  # Arbitrage opportunities
        '/api/v1/sports/live-odds',  # Live odds
        '/api/v1/odds/bankroll/',  # Bankroll management
        '/api/v1/odds/markets/',  # Betting markets

        # Session 688: Content Page APIs (read-only for React frontend)
        '/api/v1/gallery/',  # Gallery endpoints
        '/api/content-calendar/',  # Content calendar
        '/api/content-channels/',  # Session 741: Content channels (autonomous content studio)
        '/api/creative-projects/',  # Creative projects
        '/api/v1/content/templates/',  # Content templates

        # Session 688: Legal Page APIs (read-only for React frontend)
        '/api/legal/case-files/',  # Legal documents
        '/api/legal/cases/',  # Legal cases
        '/api/legal/active-case/',  # Active case

        # Session 688: Podcast Page APIs (read-only for React frontend)
        '/api/podcasts/',  # Podcast endpoints

        # Session 688: Portfolio Page APIs (read-only for React frontend)
        '/api/distribution/',  # Distribution endpoints (stats, platforms, accounts, content)

        # Session 688: Admin Page APIs (read-only for React frontend)
        '/api/spider-health/',  # Spider health summary and executions

        # Session 699: LLM Routing APIs (read-only for React frontend)
        '/api/v1/llm-routing/status/',  # LLM routing system status
        '/api/v1/llm-routing/providers/',  # LLM providers list
        '/api/v1/llm-routing/models/',  # LLM models list
        '/api/v1/llm-routing/agent-configs/',  # Agent-to-model mappings
        '/api/v1/llm-routing/logs/',  # LLM call logs
        '/api/v1/llm-routing/cost-analytics/',  # Cost analytics

        # Session 702: HEART Service APIs (read-only health monitoring for React frontend)
        '/api/heart/pulse/',  # Run full health check
        '/api/heart/status/',  # Get cached system vitals
        '/api/heart/history/',  # Heartbeat history
        '/api/heart/component/',  # Component status detail
        '/api/heart/alive/',  # Quick alive check

        # Session 702: LUNGS Service APIs (read-only resource monitoring for React frontend)
        '/api/lungs/breathe/',  # Run full breathing check
        '/api/lungs/status/',  # Get cached respiratory status
        '/api/lungs/oxygen/',  # Oxygen levels (budget usage)
        '/api/lungs/budgets/',  # List all budgets
        '/api/lungs/forecast/',  # Spending forecast
        '/api/lungs/can-breathe/',  # Check if API call is allowed
        '/api/lungs/alive/',  # Quick alive check

        # Session 703: CIRCULATORY System APIs (read-only data flow monitoring for React frontend)
        '/api/circulatory/circulate/',  # Run full circulation check
        '/api/circulatory/status/',  # Get cached flow status
        '/api/circulatory/routes/',  # List all monitored routes
        '/api/circulatory/bottlenecks/',  # Get current bottlenecks
        '/api/circulatory/velocity/',  # Get flow velocity metrics
        '/api/circulatory/history/',  # Get circulation pulse history
        '/api/circulatory/is-flowing/',  # Quick alive check

        # Session 704: SPINE System APIs (read-only API router monitoring for React frontend)
        '/api/spine/align/',  # Run full alignment check
        '/api/spine/status/',  # Get cached spine status
        '/api/spine/patterns/',  # List all route patterns
        '/api/spine/metrics/',  # Get metrics for a pattern
        '/api/spine/history/',  # Get alignment history
        '/api/spine/can-route/',  # Check if path can be routed
        '/api/spine/is-aligned/',  # Quick health check
        '/api/spine/categories/',  # Get category breakdown

        # Session 705: IMMUNE System APIs (security monitoring for React frontend)
        '/api/immune/scan/',  # Run full immune scan
        '/api/immune/status/',  # Get cached immune status
        '/api/immune/patterns/',  # List threat patterns
        '/api/immune/threats/',  # Get recent threat events
        '/api/immune/quarantine/',  # Get quarantine list
        '/api/immune/is-healthy/',  # Quick health check
        '/api/immune/categories/',  # Get category breakdown

        # Session 706: DIGESTIVE System APIs (data ingestion monitoring for React frontend)
        '/api/digestive/digest/',  # Run full digestion check
        '/api/digestive/status/',  # Get cached digestion status
        '/api/digestive/routes/',  # List ingestion routes
        '/api/digestive/bottlenecks/',  # Get current bottlenecks
        '/api/digestive/metabolism/',  # Get throughput metrics
        '/api/digestive/history/',  # Get digestion pulse history
        '/api/digestive/is-digesting/',  # Quick alive check

        # Session 707: MUSCULAR System APIs (agent execution monitoring for React frontend)
        '/api/muscular/flex/',  # Run full muscular check
        '/api/muscular/status/',  # Get cached muscular status
        '/api/muscular/groups/',  # List muscle groups
        '/api/muscular/weak/',  # Get weak muscles
        '/api/muscular/overworked/',  # Get overworked muscles
        '/api/muscular/history/',  # Get muscular pulse history
        '/api/muscular/is-strong/',  # Quick alive check

        # Session 721: BRAIN System APIs (cognitive processing for React frontend)
        '/api/brain/status/',  # Get cached brain status
        '/api/brain/think/',  # Run brain check
        '/api/brain/vitals/',  # Get brain vitals
        '/api/brain/history/',  # Get brain pulse history
        '/api/brain/is-thinking/',  # Quick alive check

        # Session 723: SKIN System APIs (project workspace health for React frontend)
        '/api/skin/status/',  # Get cached skin status
        '/api/skin/feel/',  # Run skin check
        '/api/skin/vitals/',  # Get skin vitals
        '/api/skin/history/',  # Get skin pulse history
        '/api/skin/is-healthy/',  # Quick alive check
        '/api/skin/workspaces/',  # Get workspace summaries

        # Session 724: NERVOUS System APIs (WebSocket communication health)
        '/api/nervous/status/',  # Get cached nervous status
        '/api/nervous/feel/',  # Run nervous check
        '/api/nervous/vitals/',  # Get nervous vitals
        '/api/nervous/history/',  # Get nervous pulse history
        '/api/nervous/is-responsive/',  # Quick alive check
        '/api/nervous/consumers/',  # Get WebSocket consumers summary

        # Session 710: BODY UNIFIED - Body Health Dashboard API
        '/api/body/vitals/',  # All systems health
        '/api/body/alerts/',  # Active alerts
        '/api/body/history/',  # Historical data
        '/api/body/summary/',  # Compact summary

        # Session 711: Body Coordination API
        '/api/body/coordination/status/',  # Coordination status
        '/api/body/coordination/run/',  # Trigger coordination
        '/api/body/coordination/log/',  # Coordination log
        '/api/body/throttle/',  # Throttle status

        # Session 716: Memory Palace APIs (agent memory visualization for React frontend)
        '/api/memory-palace/',  # Memory palace overview
        '/api/memory-palace/agent/',  # Agent memories, rooms, summary
        '/api/memory-palace/memory/',  # Memory detail, connections
        '/api/memory-palace/room/',  # Room memories
        '/api/memory-palace/search/',  # Search memories
        '/api/memory-palace/create/',  # Create memory
        '/api/memory-palace/assign/',  # Assign to room
        '/api/memory-palace/connect/',  # Connect memories

        # Session 715: Hive Mind APIs (multi-agent collaboration for React frontend)
        '/api/hive-mind/',  # Hive mind sessions and operations

        # Session 716: Agent Evolution APIs (XP, Levels, Abilities for React frontend)
        '/api/agent-evolution/',  # Evolution overview, leaderboard, abilities, XP gains

        # Session 716: Agent Mood APIs (emotional state and personality for React frontend)
        '/api/agent-mood/',  # Mood overview, agent moods, rules, history

        # Session 716: Time Capsules APIs (agent messages to the future for React frontend)
        '/api/time-capsules/',  # Capsules overview, agent capsules, reveal, react

        # Session 716: Time Travel APIs (decision tracking and session replay for React frontend)
        '/api/time-travel/',  # Sessions, decisions, bookmarks, annotations, search

        # Session 716: Advisors APIs (famous figure consultations for React frontend)
        '/api/v1/advisors/',  # Advisor list, detail, consult
        '/api/v1/ecosystem/advisors/',  # Advisor network
        '/api/dashboard/advisors/',  # Dashboard insights from advisors

        # Session 716: Agent Relationships APIs (rivalries, alliances, bonds for React frontend)
        '/api/agent-relationships/',  # Relationships overview, agent relationships, alliances

        # Session 716: Neural Orchestra APIs (AI consciousness visualization for React frontend)
        '/api/neural-orchestra/',  # Health, ecosystem feed, agent stats, learning status/feed, debug

        # Session 718: Spider Integration Page APIs (spider network management for React frontend)
        '/api/spider-dashboard/',  # Spider network data, activity feed
        '/api/spider-intelligence/',  # Spider registry, feed, trends, knowledge, timeline, detail
        '/api/spider-feed/',  # Session 783: Spider News Feed (human-facing with agent annotations)
        '/api/docs/',  # Session 784: Documentation Index API

        # Session 718: Memory Clusters APIs (semantic memory grouping for Memory Palace)
        '/api/memory-clusters/',  # Overview, agent clusters, visualization, evolution, find-similar

        # Session 745: New Frontend Pages APIs (stubs for frontend-first development)
        '/api/collective/',  # Collective Intelligence dashboard
        '/api/stripe/',  # Billing and subscription (stubs)
        '/api/learning/',  # Learning journeys and templates
        '/api/autonomous/',  # Autonomous system status
        '/api/reasoning/',  # Reasoning engine dashboard (non-v1)
        '/api/analytics/',  # Analytics overview and reports

        # Session 782: Team Collaboration APIs (read-only for Collective Intelligence page)
        '/api/teams/',  # Agent teams list and management
        '/api/collaboration/history/',  # Collaboration history for Network tab
        '/api/agent-collab/messages/',  # Inter-agent messages for Messages tab

        # Session 815/819: Platform Command Center APIs (read-only for Workspace page)
        '/api/platform/mission/',  # Platform mission statement
        '/api/platform/metrics/',  # Platform metrics dashboard
        '/api/platform/governance/',  # Governance status
        '/api/platform/canon/',  # Canon browser
        '/api/platform/playbooks/',  # Playbooks list
        '/api/platform/audits/',  # System audits browser
        '/api/platform/doc-content/',  # Document content viewer
        # '/api/deliverables/' moved to OPTIONAL_AUTH_PATHS — needs user context when logged in

        # Session 824: Live Metrics (read-only, no auth needed)
        '/api/platform/live-metrics/',  # Real-time system metrics
        '/api/platform/remediation/',  # Remediation status (read-only)
        # NOTE: /api/platform/actions/ and /api/platform/triggers/ intentionally NOT in
        # PUBLIC_PATHS - their POST endpoints (run-now, toggle, run-remediation) require auth

        # Session 819: Audit Tracking System APIs (read-only endpoints)
        '/api/audit-tracking/findings/',  # Findings list and summary
        '/api/audit-tracking/reports/',  # Audit reports list

        # Session 830: Self-Healing Progress (read-only monitoring)
        '/api/self-healing/progress/',  # Live remediation progress

        # Session 842: Celery Debug & Cleanup (for production debugging)
        # S2788 Fold C: '/api/platform/celery-debug/' and
        # '/api/platform/cleanup-stale-executions/' removed — both are now
        # staff-only per S2772 N16 contract (leaked infra info / anon-reachable
        # POST mutation respectively).

        # Session 1069: Internal config snapshot (no secrets, for cross-service comparison)
        '/api/internal/config-snapshot/',

        # Session 893: Intel Page APIs (read-only for React frontend)
        '/api/v1/agents/unified-executions/',  # Agent execution history
        '/api/orchestrations/',  # Active orchestrations list
        '/api/v1/reasoning/gates/',  # Pilot readiness gates

        # Session 894: LLM Routing APIs (read-only for React frontend)
        '/api/llm-routing/status/',  # LLM routing status
        '/api/llm-routing/providers/',  # LLM providers list
        '/api/llm-routing/models/',  # LLM models list
        '/api/llm-routing/agent-configs/',  # Agent LLM configs
        '/api/llm-routing/logs/',  # LLM call logs
        '/api/llm-routing/cost-analytics/',  # LLM cost analytics

        # Session 894: Intel Page - Safety & Collective sub-tabs
        '/api/mythology/patterns/',  # Safety patterns
        '/api/mythology/guards/',  # Safety guards
        '/api/v1/collective/shared-knowledge/',  # Collective shared knowledge

        # Session 894: Dossiers tab (ConceptForge)
        '/api/conceptforge/runs/',  # ConceptForge runs list
        '/api/conceptforge/stats/',  # ConceptForge stats

        # Session 894: Knowledge/Learn tab (Learning Journeys)
        '/api/learning/journeys/',  # Learning journeys list
        '/api/learning/journeys/analytics/',  # Learning analytics
        '/api/learning/journeys/active/',  # Active journeys
        '/api/learning/achievements/',  # Achievements
        '/api/learning/templates/',  # Journey templates

        # Session 972: Page-view telemetry (fire-and-forget counters, non-sensitive)
        '/api/v1/telemetry/',  # Page view tracking

        # Session 987: Deliberation APIs (read-only for Orchestration Monitor tab)
        '/api/deliberation/',  # Deliberation sessions, turns, contracts, verification

        # VIP Magic Link Exchange (must be public — unauthenticated users redeem tokens)
        '/api/v1/vip-invites/exchange/',

        # Preview System: Public magic-link review portal
        '/api/review/',  # GET context + POST feedback (token-validated, not auth-validated)

        # BPaaS: Public schema + example (documentation/intake)
        '/api/bpaas/schema/',
        '/api/bpaas/example/',

        # Status overview (used by /demo page)
        '/api/status/overview/',

        # Newsletter signup (public landing page — Operator Edge)
        '/api/newsletter/',

        # S2990: drf-spectacular schema + Swagger UI + Redoc — dev docs, conventionally public.
        '/api/schema/',
    ]

    # Session 830: Exact match public paths (don't use prefix matching)
    # These specific endpoints are public, but their sub-paths require auth
    PUBLIC_PATHS_EXACT = [
        '/api/platform/triggers/',  # GET list is public, but /run-now/ and /toggle/ require auth
        '/api/home/purge-queue/',  # Session 1005: Uses secret-based auth (PURGE_SECRET)
    ]

    # Session 528: Paths that allow session auth but DON'T require it (optional auth)
    # These endpoints work for both authenticated and anonymous users
    # Anonymous users get limited/public data, authenticated users get full access
    OPTIONAL_AUTH_PATHS = [
        '/api/voice-marketplace/',  # Browse marketplace is public, purchasing requires auth
        '/api/monitoring/',  # Public monitoring dashboard for stress tests
        '/api/deliverables/',  # Deliverables: anonymous gets public, authed gets scoped by user/workspace
        # S3015 hotfix: initiatives list endpoint. Moved from PUBLIC_PATHS so Token-auth
        # browsers get their scoped results (scope_queryset_initiative returns .none()
        # for anon, so anonymous access is still safe). Fixes empty-Initiatives-tab
        # for token-auth-only browser sessions (no Django session cookie).
        '/api/initiatives/',
        # Session 1129 Move 2 — fleet artifact endpoints authenticate via
        # X-Fleet-Signature headers at the DRF layer, not via PA token /
        # session. This middleware would otherwise reject signed-but-
        # tokenless fleet requests before DRF auth ran.
        '/api/fleet/artifacts/',
        # Session 1129 Move 3 — fleet event SSE stream, same pattern.
        '/api/fleet/events/',
        # Session 1131 Phase 1 — fleet signal-cluster replay
        # (signal-studio only; app_slug allowlist enforced in the view).
        '/api/fleet/signals/',
        # Session 1138 — fleet paid-interest submission (Decision 13
        # demand-gate). Same fleet HMAC auth as artifacts/events.
        '/api/fleet/paid-interest/',
    ]
    
    # Paths that require staff privileges
    STAFF_REQUIRED_PATHS = [
        '/api/v1/admin/',
        '/api/v1/system/',
        '/api/v1/metrics/admin/',
    ]

    # Session 998: Paths blocked for read-only reviewers
    REVIEWER_BLOCKED_PATHS = [
        '/api/v1/spiders/create/', '/api/v1/spiders/execute/',
        '/api/v1/betting/execute/', '/api/v1/betting/place/',
        '/api/platform/actions/', '/api/platform/triggers/',
        '/api/v1/admin/',
        '/api/initiatives/create/', '/api/action-items/create/',
        '/api/v1/research/self-blog/publish/', '/api/content/publish/',
        '/api/podcasts/create/',
    ]

    # Session 998: Auth endpoints that reviewers can still use
    REVIEWER_ALLOWED_PATHS = [
        '/api/v1/auth/',
    ]
    
    def process_request(self, request):
        """Process incoming request for authentication"""
        # Skip non-API requests (let Django handle them)
        if not request.path.startswith('/api/') and not request.path.startswith('/admin/'):
            return None

        # Skip truly public paths (no auth required at all)
        if any(request.path.startswith(path) for path in self.PUBLIC_PATHS):
            return None

        # Session 830: Check exact match public paths (for endpoints where sub-paths need auth)
        if request.path in self.PUBLIC_PATHS_EXACT:
            return None

        # Session 528: Handle optional auth paths
        # These work for both auth and anon users - try to authenticate but don't require it
        is_optional_auth = any(request.path.startswith(path) for path in self.OPTIONAL_AUTH_PATHS)
        if is_optional_auth:
            # Try to authenticate, but don't fail if no auth provided
            if hasattr(request, 'user') and request.user.is_authenticated:
                return None  # Already authenticated via session
            token = self.extract_token(request)
            if token:
                try:
                    user = self.validate_token(token)
                except TokenValidationInfrastructureError:
                    # Optional-auth path: fail open. If auth backend is
                    # down we still allow the anon code path through;
                    # the strict path (below) is the one that 503s.
                    user = None
                if user:
                    request.user = user
            return None  # Allow through regardless

        # Session 452: Support DRF's force_authenticate() for testing
        # DRF's force_authenticate sets _force_auth_user on the request
        if hasattr(request, '_force_auth_user') and request._force_auth_user:
            request.user = request._force_auth_user
            logger.debug(f"DRF force_authenticate user {request.user.username} for {request.path}")
            return None

        # Check if user is already authenticated via session
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Session authentication is valid for API requests
            logger.debug(f"Session authenticated user {request.user.username} for {request.path}")

            # Check if staff access required
            if any(request.path.startswith(path) for path in self.STAFF_REQUIRED_PATHS):
                if not request.user.is_staff:
                    logger.warning(f"Staff access required for {request.path}, user: {request.user.username}")
                    return emit_error_envelope(
                        reason_code='permission_denied',
                        request=request,
                        hint={'source': 'session_staff_required', 'user': request.user.username},
                    )

            # Session 998: Block write paths for read-only reviewers
            if hasattr(request.user, 'is_reviewer') and request.user.is_reviewer:
                if any(request.path.startswith(p) for p in self.REVIEWER_BLOCKED_PATHS):
                    return emit_error_envelope(
                        reason_code='permission_denied',
                        request=request,
                        hint={'source': 'session_reviewer_blocked_path', 'user': request.user.username},
                    )
                # Block non-GET methods on /api/ paths (except auth endpoints)
                if (request.method not in ('GET', 'HEAD', 'OPTIONS')
                        and request.path.startswith('/api/')
                        and not any(request.path.startswith(p) for p in self.REVIEWER_ALLOWED_PATHS)):
                    return emit_error_envelope(
                        reason_code='permission_denied',
                        request=request,
                        hint={'source': 'session_reviewer_write_blocked', 'user': request.user.username, 'method': request.method},
                    )

            return None

        # Extract token from request
        token = self.extract_token(request)

        if not token:
            # No token and no session authentication
            logger.warning(f"No authentication provided for {request.path}")
            return emit_error_envelope(
                reason_code='not_authenticated',
                request=request,
                hint={'source': 'no_credentials'},
            )

        # Validate token and get user.
        # Session 1171 #4: separate "token not in DB" (→ 401) from "auth backend
        # unreachable" (→ 503). Before this fix, a Postgres OperationalError
        # (e.g., 'too many clients already') was swallowed in `validate_token`
        # and returned None — indistinguishable from a real Token.DoesNotExist
        # — producing a false 401 'Invalid authentication token'. Discovered
        # while debugging session 1171's ml-queue flood. See
        # docs/handoffs/SESSION_1171_ML_QUEUE_FLOOD_AND_AUTH_MIDDLEWARE.md.
        try:
            user = self.validate_token(token)
        except TokenValidationInfrastructureError as infra_exc:
            logger.error(
                "Auth backend unreachable while validating token for %s: %s",
                request.path, infra_exc,
            )
            # S1171 fix intent preserved: retryable=True + terminal_state=BUSY
            # (reason_code=busy) signals transient infrastructure failure,
            # NOT a bad-credentials 401. 'auth_backend_unavailable' identity
            # preserved in structured-log hint for operator diagnostics.
            return emit_error_envelope(
                reason_code='busy',
                request=request,
                hint={'source': 'auth_backend_unavailable', 'exc_type': type(infra_exc).__name__},
            )

        if not user:
            logger.warning(f"Invalid authentication token for {request.path}")
            return emit_error_envelope(
                reason_code='not_authenticated',
                request=request,
                hint={'source': 'invalid_token'},
            )

        # Check if staff access required
        if any(request.path.startswith(path) for path in self.STAFF_REQUIRED_PATHS):
            if not user.is_staff:
                logger.warning(f"Staff access required for {request.path}, user: {user.username}")
                return emit_error_envelope(
                    reason_code='permission_denied',
                    request=request,
                    hint={'source': 'token_staff_required', 'user': user.username},
                )

        # Session 998: Block write paths for read-only reviewers (token auth path)
        if hasattr(user, 'is_reviewer') and user.is_reviewer:
            if any(request.path.startswith(p) for p in self.REVIEWER_BLOCKED_PATHS):
                return emit_error_envelope(
                    reason_code='permission_denied',
                    request=request,
                    hint={'source': 'token_reviewer_blocked_path', 'user': user.username},
                )
            if (request.method not in ('GET', 'HEAD', 'OPTIONS')
                    and request.path.startswith('/api/')
                    and not any(request.path.startswith(p) for p in self.REVIEWER_ALLOWED_PATHS)):
                return emit_error_envelope(
                    reason_code='permission_denied',
                    request=request,
                    hint={'source': 'token_reviewer_write_blocked', 'user': user.username, 'method': request.method},
                )

        # Attach user to request
        request.user = user

        # Log successful authentication
        logger.debug(f"Authenticated user {user.username} for {request.path}")

        return None
    
    def extract_token(self, request) -> Optional[str]:
        """Extract authentication token from request"""
        # Try Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Token '):
            return auth_header.split(' ', 1)[1]
        elif auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]
        
        # Try custom header
        custom_token = request.META.get('HTTP_X_API_KEY')
        if custom_token:
            return custom_token
        
        # Try query parameter (less secure, only for development)
        if settings.DEBUG:
            return request.GET.get('token')
        
        return None
    
    def validate_token(self, token_value: str) -> Optional[User]:
        """Validate authentication token and return user.

        Session 1171 #4: distinguishes 'no such token' (return None → caller
        emits 401) from 'auth backend unreachable' (raise
        `TokenValidationInfrastructureError` → caller emits 503). The
        previous `except Exception: return None` swallowed Postgres
        OperationalError ('too many clients already') and produced false
        401 'Invalid authentication token' responses during DB pressure
        events. See SESSION_1171 handoff for the discovery incident.
        """
        try:
            token = Token.objects.select_related('user').get(key=token_value)

            # Check if user is active
            if not token.user.is_active:
                logger.warning(f"Token belongs to inactive user: {token.user.username}")
                return None

            return token.user

        except Token.DoesNotExist:
            return None
        except Exception as e:
            # Postgres / Redis / cache failures land here. Re-raise as a
            # typed infrastructure error so callers can return 503 instead
            # of misleading the client with a 401 "Invalid token" when the
            # token might be perfectly valid.
            logger.error(
                "Auth backend error while validating token: %s: %s",
                type(e).__name__, e,
            )
            raise TokenValidationInfrastructureError(str(e)) from e


class WebSocketAuthenticationMiddleware(BaseMiddleware):
    """
    WebSocket authentication middleware
    Ensures consistent authentication for WebSocket connections
    """
    
    async def __call__(self, scope, receive, send):
        """Authenticate WebSocket connection"""
        # Only process WebSocket connections
        if scope['type'] != 'websocket':
            return await super().__call__(scope, receive, send)
        
        # Extract token from query string or headers
        token = await self.extract_websocket_token(scope)
        
        # Validate token if provided
        if token:
            user = await self.validate_websocket_token(token)
            scope['user'] = user or AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        
        # Check if WebSocket authentication is required
        ws_auth_required = getattr(settings, 'REQUIRE_WEBSOCKET_AUTH', True)

        if ws_auth_required and isinstance(scope['user'], AnonymousUser):
            # Close connection with authentication error
            logger.warning("WebSocket connection rejected: authentication required")
            await send({
                'type': 'websocket.close',
                'code': 4001  # Custom close code for authentication required
            })
            return
        
        # Log successful WebSocket authentication
        if not isinstance(scope['user'], AnonymousUser):
            logger.debug(f"WebSocket authenticated: {scope['user'].username}")
        
        return await super().__call__(scope, receive, send)
    
    async def extract_websocket_token(self, scope) -> Optional[str]:
        """Extract authentication token from WebSocket scope"""
        # Try query string first
        query_string = scope.get('query_string', b'').decode('utf-8')
        if query_string:
            parsed_query = parse_qs(query_string)
            token = parsed_query.get('token', [None])[0]
            if token:
                return token
        
        # Try headers
        headers = dict(scope.get('headers', []))
        
        # Authorization header
        auth_header = headers.get(b'authorization', b'').decode('utf-8')
        if auth_header.startswith('Token '):
            return auth_header.split(' ', 1)[1]
        elif auth_header.startswith('Bearer '):
            return auth_header.split(' ', 1)[1]
        
        # Custom header
        custom_token = headers.get(b'x-api-key', b'').decode('utf-8')
        if custom_token:
            return custom_token
        
        return None
    
    @database_sync_to_async
    def validate_websocket_token(self, token_value: str) -> Optional[User]:
        """Validate WebSocket authentication token"""
        try:
            token = Token.objects.select_related('user').get(key=token_value)

            # Check if user is active
            if not token.user.is_active:
                return None

            return token.user

        except Token.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error validating WebSocket token: {str(e)}")
            return None



class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    Provides consistent security headers across the platform
    """
    
    def process_response(self, request, response):
        """Add security headers to response"""
        # Basic security headers for all responses
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Frame options (can be overridden by views if needed)
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'
        
        # HTTPS security headers for production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # API-specific headers
        if request.path.startswith('/api/'):
            response['X-API-Version'] = 'v1'
            response['X-Platform'] = 'Unified Donkey Betz'
        
        # CORS headers are handled by django-cors-headers middleware
        return response


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Enhanced rate limiting middleware
    Provides additional rate limiting beyond DRF throttling
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        self.rate_limits = {
            '/api/v1/auth/login/': (5, 300),  # 5 attempts per 5 minutes
            '/api/v1/auth/register/': (3, 3600),  # 3 attempts per hour
            '/api/v1/auth/forgot-password/': (3, 3600),  # 3 attempts per hour
        }
    
    def process_request(self, request):
        """Apply additional rate limiting"""
        # Skip if not an API request
        if not request.path.startswith('/api/'):
            return None
        
        # Check specific endpoint rate limits
        for endpoint, (limit, window) in self.rate_limits.items():
            if request.path == endpoint:
                client_ip = self.get_client_ip(request)
                
                # Check rate limit (implementation would use Redis/cache)
                if self.is_rate_limited(client_ip, endpoint, limit, window):
                    logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint}")
                    return emit_error_envelope(
                        reason_code='rate_limited',
                        request=request,
                        hint={
                            'source': 'rate_limit_exceeded',
                            'endpoint': endpoint,
                            'client_ip': client_ip,
                            'limit': limit,
                            'window_seconds': window,
                        },
                        retry_after_seconds=window,
                    )
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rate_limited(self, client_ip, endpoint, limit, window):
        """Check if client is rate limited using Django cache (Redis-backed)"""
        from django.core.cache import cache

        cache_key = f"rate_limit:{endpoint}:{client_ip}"

        # Get current count
        current_count = cache.get(cache_key, 0)

        if current_count >= limit:
            return True

        # Increment counter
        if current_count == 0:
            # First request in window
            cache.set(cache_key, 1, window)
        else:
            cache.incr(cache_key)

        return False


class APILoggingMiddleware(MiddlewareMixin):
    """
    Enhanced API request/response logging
    Provides consistent logging across all API endpoints
    """
    
    def process_request(self, request):
        """Log API request"""
        if request.path.startswith('/api/'):
            # Don't log sensitive endpoints in detail
            sensitive_paths = ['/api/v1/auth/login/', '/api/v1/auth/register/']
            
            if any(request.path.startswith(path) for path in sensitive_paths):
                logger.info(f"API Request: {request.method} {request.path} [SENSITIVE]")
            else:
                logger.debug(
                    f"API Request: {request.method} {request.path}",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'user': getattr(request, 'user', None),
                        'ip': self.get_client_ip(request)
                    }
                )
        
        return None
    
    def process_response(self, request, response):
        """Log API response"""
        if request.path.startswith('/api/'):
            logger.debug(
                f"API Response: {request.method} {request.path} -> {response.status_code}",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'user': getattr(request, 'user', None)
                }
            )
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip