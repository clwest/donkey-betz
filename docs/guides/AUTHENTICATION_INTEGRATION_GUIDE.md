# 🔐 Authentication Integration Guide

**Purpose**: Ensure authentication is properly integrated into every layer of the new UI
**Status**: 📋 Reference Guide
**Last Updated**: October 2, 2025

---

## 🎯 Authentication Goals

### Core Principles:
1. **Authenticated by Default** - Every page requires login unless explicitly public
2. **User Context Everywhere** - User data available in all templates and JavaScript
3. **WebSocket Security** - All WebSocket connections authenticated
4. **CSRF Protection** - All POST requests protected
5. **Session Management** - Proper session handling and expiry

### What We're Preventing:
- ❌ Anonymous access to user data
- ❌ WebSocket connections without authentication
- ❌ Mixed authentication states
- ❌ CSRF vulnerabilities
- ❌ Session hijacking
- ❌ User data leakage

---

## 🏗️ Authentication Architecture

### 4-Layer Authentication:

```
┌─────────────────────────────────────┐
│  Layer 1: Django View Authentication│  ← LoginRequiredMixin
├─────────────────────────────────────┤
│  Layer 2: WebSocket Authentication  │  ← scope["user"] check
├─────────────────────────────────────┤
│  Layer 3: Template Context          │  ← User data in context
├─────────────────────────────────────┤
│  Layer 4: Frontend JavaScript       │  ← User ID & CSRF token
└─────────────────────────────────────┘
```

---

## 📝 Layer 1: Django View Authentication

### Base Authenticated View

Create in `core/views_unified_v2.py`:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from core.models_unified_system import Agent, Advisor, AgentExecution, SpiderData
from intelligence.models import OpportunityTracking
import logging

logger = logging.getLogger(__name__)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AuthenticatedView(LoginRequiredMixin, TemplateView):
    """
    Base view that requires authentication and provides user context
    to all templates.

    All new views should inherit from this class.
    """
    login_url = '/login/'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ALWAYS include user data
        context['user_data'] = self.get_user_data()

        # ALWAYS include CSRF token
        context['csrf_token'] = self.request.META.get('CSRF_COOKIE', '')

        return context

    def get_user_data(self):
        """
        Get comprehensive user data for templates and JavaScript.
        This runs on EVERY page load.
        """
        user = self.request.user

        # Get user stats
        stats = self.get_user_stats(user)

        # Get user learning
        learning = self.get_user_learning(user)

        # Get user profile
        profile = self.get_user_profile(user)

        return {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name() or user.username,
            'stats': stats,
            'learning': learning,
            'profile': profile,
        }

    def get_user_stats(self, user):
        """Get user statistics"""
        from django.db.models import Count, Sum

        try:
            stats = {
                'agents_total': Agent.objects.count(),
                'advisors_total': Advisor.objects.count(),
                'executions_total': AgentExecution.objects.filter(user=user).count(),
                'executions_today': AgentExecution.objects.filter(
                    user=user,
                    created_at__date=timezone.now().date()
                ).count(),
                'opportunities_total': OpportunityTracking.objects.count(),
                'spider_data_items': SpiderData.objects.count(),
                'learning_records': self.get_learning_count(user),
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {}

    def get_user_learning(self, user):
        """Get user learning summary"""
        try:
            from core.models_unified_system import UserAgentLearning

            learning_records = UserAgentLearning.objects.filter(user=user)

            if not learning_records.exists():
                return {
                    'total_records': 0,
                    'avg_confidence': 0,
                    'top_agents': [],
                }

            # Calculate average confidence
            avg_confidence = learning_records.aggregate(
                Avg('confidence_score')
            )['confidence_score__avg'] or 0

            # Get top 3 agents by confidence
            top_agents = learning_records.values('agent_name').annotate(
                avg_conf=Avg('confidence_score')
            ).order_by('-avg_conf')[:3]

            return {
                'total_records': learning_records.count(),
                'avg_confidence': round(avg_confidence, 2),
                'top_agents': list(top_agents),
            }
        except Exception as e:
            logger.error(f"Error getting user learning: {e}")
            return {'total_records': 0, 'avg_confidence': 0, 'top_agents': []}

    def get_user_profile(self, user):
        """Get user profile data"""
        try:
            profile = user.extendeduserprofile
            return {
                'has_profile': True,
                'completion': profile.calculate_completion_percentage(),
                'skills': profile.skills or [],
                'goals': profile.goals or [],
            }
        except:
            return {
                'has_profile': False,
                'completion': 0,
                'skills': [],
                'goals': [],
            }

    def get_learning_count(self, user):
        """Get learning record count"""
        try:
            from core.models_unified_system import UserAgentLearning
            return UserAgentLearning.objects.filter(user=user).count()
        except:
            return 0


class DashboardView(AuthenticatedView):
    """Main dashboard - inherits authentication"""
    template_name = 'unified_v2/dashboard.html'


class PersonalAssistantView(AuthenticatedView):
    """Personal Assistant - inherits authentication"""
    template_name = 'unified_v2/personal_assistant.html'


class AgentMarketplaceView(AuthenticatedView):
    """Agent Marketplace - inherits authentication"""
    template_name = 'unified_v2/agent_marketplace.html'


class AdvisorCouncilView(AuthenticatedView):
    """Advisor Council - inherits authentication"""
    template_name = 'unified_v2/advisor_council.html'


class IntelligenceHubView(AuthenticatedView):
    """Intelligence Hub - inherits authentication"""
    template_name = 'unified_v2/intelligence_hub.html'
```

### Authentication Decorator for API Views

```python
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json


@login_required
def api_execute_agent(request):
    """API endpoint to execute an agent"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body or b"{}"))
        agent_name = data.get('agent_name')

        # User is available as request.user (guaranteed by @login_required)
        user = request.user

        # Execute agent
        from ai_core.agents.universal_agent_loader import UniversalAgentLoader
        loader = UniversalAgentLoader()
        result = loader.execute_agent(agent_name, user=user)

        return JsonResponse({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"Error executing agent: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_list_agents(request):
    """API endpoint to list agents"""
    try:
        user = request.user
        agents = Agent.objects.all()

        agent_list = [{
            'id': str(agent.id),
            'name': agent.name,
            'description': agent.description,
            'category': agent.category.name if agent.category else 'Uncategorized',
        } for agent in agents]

        return JsonResponse({
            'agents': agent_list,
            'total': len(agent_list)
        })
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return JsonResponse({'error': str(e)}, status=500)
```

---

## 🔌 Layer 2: WebSocket Authentication

### Base Authenticated Consumer

Create in `core/consumers_unified.py`:

```python
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AuthenticatedConsumer(AsyncWebsocketConsumer):
    """
    Base WebSocket consumer with authentication built-in.
    All WebSocket consumers should inherit from this class.
    """

    async def connect(self):
        """
        Handle WebSocket connection with authentication check
        """
        # Get user from scope (provided by Django Channels auth middleware)
        user = self.scope.get("user")

        # REJECT if not authenticated
        if not user or not user.is_authenticated:
            logger.warning(f"Unauthenticated WebSocket connection attempt")
            await self.close(code=4001)  # Custom code: Unauthorized
            return

        # Store user
        self.user = user
        self.user_id = str(user.id)

        logger.info(f"✅ User {user.username} connected to WebSocket: {self.__class__.__name__}")

        # Join user-specific group (for targeted messages)
        await self.channel_layer.group_add(
            f"user_{self.user_id}",
            self.channel_name
        )

        # Accept connection
        await self.accept()

        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected successfully',
            'user': {
                'id': self.user_id,
                'username': user.username,
            },
            'timestamp': timezone.now().isoformat()
        }))

        # Send initial data (override in subclasses)
        await self.send_initial_data()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection
        """
        # Leave user group
        if hasattr(self, 'user_id'):
            await self.channel_layer.group_discard(
                f"user_{self.user_id}",
                self.channel_name
            )
            logger.info(f"❌ User {self.user.username} disconnected from WebSocket")

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages
        Override in subclasses to handle specific message types
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # Verify user is still authenticated
            if not self.user or not self.user.is_authenticated:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Authentication required'
                }))
                await self.close(code=4001)
                return

            # Route to handler
            handler = getattr(self, f'handle_{message_type}', None)
            if handler:
                await handler(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_data(self):
        """
        Send initial data after connection
        Override in subclasses
        """
        pass

    # Helper to send messages from other parts of the system
    async def send_message(self, event):
        """Send message to this WebSocket"""
        await self.send(text_data=json.dumps(event))


class DashboardConsumer(AuthenticatedConsumer):
    """WebSocket consumer for dashboard real-time updates"""

    async def send_initial_data(self):
        """Send initial dashboard data"""
        stats = await self.get_user_stats()

        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }))

    @database_sync_to_async
    def get_user_stats(self):
        """Get user statistics"""
        from core.models_unified_system import Agent, Advisor, AgentExecution
        from intelligence.models import OpportunityTracking

        return {
            'agents_total': Agent.objects.count(),
            'advisors_total': Advisor.objects.count(),
            'executions_total': AgentExecution.objects.filter(user=self.user).count(),
            'opportunities_total': OpportunityTracking.objects.count(),
        }

    async def handle_refresh_stats(self, data):
        """Handle refresh stats request"""
        stats = await self.get_user_stats()

        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }))
```

### Django Channels Authentication Middleware

Ensure `core/routing.py` uses authentication middleware:

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import core.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(  # ← This adds user to scope
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
```

---

## 📄 Layer 3: Template Context

### Base Template with User Context

Create `core/templates/unified_v2/base.html`:

```html
{% load static %}
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <title>{% block title %}AI Platform{% endblock %}</title>

    <!-- Tailwind CSS CDN (replace with local in production) -->
    <script src="https://cdn.tailwindcss.com"></script>

    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-900 text-white">

    <!-- User Context (Available to ALL JavaScript) -->
    <script>
        // User data available globally
        window.USER_DATA = {
            id: "{{ user_data.id }}",
            username: "{{ user_data.username }}",
            email: "{{ user_data.email }}",
            full_name: "{{ user_data.full_name }}",
            stats: {
                agents_total: {{ user_data.stats.agents_total|default:0 }},
                advisors_total: {{ user_data.stats.advisors_total|default:0 }},
                executions_total: {{ user_data.stats.executions_total|default:0 }},
                executions_today: {{ user_data.stats.executions_today|default:0 }},
                opportunities_total: {{ user_data.stats.opportunities_total|default:0 }},
                spider_data_items: {{ user_data.stats.spider_data_items|default:0 }},
                learning_records: {{ user_data.stats.learning_records|default:0 }},
            },
            learning: {
                total_records: {{ user_data.learning.total_records|default:0 }},
                avg_confidence: {{ user_data.learning.avg_confidence|default:0 }},
            },
            profile: {
                has_profile: {{ user_data.profile.has_profile|yesno:"true,false" }},
                completion: {{ user_data.profile.completion|default:0 }},
            }
        };

        // CSRF token for all AJAX requests
        window.CSRF_TOKEN = "{{ csrf_token }}";

        // Helper function to include CSRF in fetch requests
        window.fetchWithAuth = function(url, options = {}) {
            options.headers = options.headers || {};
            options.headers['X-CSRFToken'] = window.CSRF_TOKEN;
            options.credentials = 'same-origin';
            return fetch(url, options);
        };
    </script>

    <!-- Navigation -->
    <nav class="bg-gray-800 border-b border-gray-700">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex">
                    <!-- Logo -->
                    <div class="flex-shrink-0 flex items-center">
                        <h1 class="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                            AI Platform
                        </h1>
                    </div>

                    <!-- Navigation Links -->
                    <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                        <a href="{% url 'dashboard' %}" class="nav-link">Dashboard</a>
                        <a href="{% url 'personal_assistant' %}" class="nav-link">Assistant</a>
                        <a href="{% url 'agent_marketplace' %}" class="nav-link">Agents</a>
                        <a href="{% url 'advisor_council' %}" class="nav-link">Advisors</a>
                        <a href="{% url 'intelligence_hub' %}" class="nav-link">Intelligence</a>
                    </div>
                </div>

                <!-- User Menu -->
                <div class="flex items-center">
                    <div class="ml-3 relative">
                        <div class="flex items-center space-x-4">
                            <!-- User Stats Badge -->
                            <div class="text-sm text-gray-400">
                                <span class="font-semibold text-cyan-400">{{ user_data.stats.executions_today }}</span> executions today
                            </div>

                            <!-- User Dropdown -->
                            <div class="flex items-center space-x-2">
                                <span class="text-sm">{{ user_data.full_name }}</span>
                                <img class="h-8 w-8 rounded-full bg-gray-700" src="https://ui-avatars.com/api/?name={{ user_data.username }}&background=6366f1&color=fff" alt="{{ user_data.username }}">
                            </div>

                            <!-- Logout -->
                            <a href="{% url 'logout' %}" class="text-sm text-gray-400 hover:text-white">
                                Logout
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {% block content %}{% endblock %}
    </main>

    <!-- WebSocket Manager (Available to all pages) -->
    <script src="{% static 'js/auth.js' %}"></script>
    <script src="{% static 'js/websocket.js' %}"></script>

    {% block extra_js %}{% endblock %}

    <style>
        .nav-link {
            @apply border-transparent text-gray-300 hover:border-cyan-400 hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium;
        }
    </style>
</body>
</html>
```

---

## 💻 Layer 4: Frontend JavaScript

### Authentication Utilities

Create `core/static/js/auth.js`:

```javascript
/**
 * Authentication utilities for frontend
 * Provides helpers for authenticated requests
 */

class AuthManager {
    constructor() {
        this.userData = window.USER_DATA || null;
        this.csrfToken = window.CSRF_TOKEN || '';

        if (!this.userData) {
            console.warn('⚠️ User data not found. User may not be authenticated.');
        } else {
            console.log(`✅ Authenticated as: ${this.userData.username}`);
        }
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return this.userData && this.userData.id;
    }

    /**
     * Get user ID
     */
    getUserId() {
        return this.userData ? this.userData.id : null;
    }

    /**
     * Get username
     */
    getUsername() {
        return this.userData ? this.userData.username : null;
    }

    /**
     * Get user stats
     */
    getUserStats() {
        return this.userData ? this.userData.stats : {};
    }

    /**
     * Get CSRF token
     */
    getCsrfToken() {
        return this.csrfToken;
    }

    /**
     * Make authenticated fetch request
     */
    async fetch(url, options = {}) {
        // Add CSRF token to headers
        options.headers = options.headers || {};
        options.headers['X-CSRFToken'] = this.csrfToken;

        // Include credentials
        options.credentials = 'same-origin';

        try {
            const response = await fetch(url, options);

            // Check for authentication errors
            if (response.status === 401 || response.status === 403) {
                console.error('❌ Authentication error');
                // Redirect to login
                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                return null;
            }

            return response;
        } catch (error) {
            console.error('Request error:', error);
            throw error;
        }
    }

    /**
     * Make authenticated POST request
     */
    async post(url, data) {
        return this.fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
    }

    /**
     * Make authenticated GET request
     */
    async get(url) {
        return this.fetch(url, {
            method: 'GET',
        });
    }
}

// Create global auth manager instance
window.authManager = new AuthManager();
```

### Authenticated WebSocket Manager

Create `core/static/js/websocket.js`:

```javascript
/**
 * Authenticated WebSocket Manager
 * Handles WebSocket connections with automatic authentication
 */

class AuthenticatedWebSocket {
    constructor(endpoint) {
        this.endpoint = endpoint;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.handlers = {};
        this.isConnected = false;

        // Check authentication
        if (!window.authManager || !window.authManager.isAuthenticated()) {
            console.error('❌ User not authenticated. Cannot create WebSocket.');
            return;
        }

        this.connect();
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}/ws/${this.endpoint}/`;

        console.log(`🔌 Connecting to WebSocket: ${url}`);

        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log(`✅ WebSocket connected: ${this.endpoint}`);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.onOpen();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log(`❌ WebSocket disconnected: ${this.endpoint}`);
            this.isConnected = false;

            // Check if it was an authentication error
            if (event.code === 4001) {
                console.error('Authentication failed. Redirecting to login...');
                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                return;
            }

            this.onClose();
            this.reconnect();
        };

        this.ws.onerror = (error) => {
            console.error(`WebSocket error:`, error);
            this.onError(error);
        };
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not connected. Message not sent:', data);
        }
    }

    on(messageType, handler) {
        this.handlers[messageType] = handler;
    }

    handleMessage(data) {
        const handler = this.handlers[data.type];
        if (handler) {
            handler(data);
        } else {
            console.log('Unhandled message type:', data.type, data);
        }
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(
                this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
                30000
            );

            console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

            setTimeout(() => this.connect(), delay);
        } else {
            console.error('❌ Max reconnection attempts reached. Please refresh the page.');
        }
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }

    // Override these in subclasses
    onOpen() {}
    onClose() {}
    onError(error) {}
}

// Make available globally
window.AuthenticatedWebSocket = AuthenticatedWebSocket;
```

---

## ✅ Authentication Checklist

### Pre-Implementation:
- [ ] Review Django authentication settings
- [ ] Verify CSRF middleware is enabled
- [ ] Verify session middleware is enabled
- [ ] Verify Django Channels authentication middleware
- [ ] Test login/logout flow

### During Implementation:
- [ ] All views inherit from `AuthenticatedView`
- [ ] All API endpoints use `@login_required` decorator
- [ ] All WebSocket consumers inherit from `AuthenticatedConsumer`
- [ ] All templates extend `base.html` (includes user context)
- [ ] All JavaScript uses `authManager` for requests
- [ ] All WebSocket connections use `AuthenticatedWebSocket`

### Post-Implementation Testing:
- [ ] Try accessing pages without logging in → redirects to login
- [ ] Try connecting WebSocket without auth → connection refused
- [ ] Try API endpoints without auth → 401/403 error
- [ ] Verify CSRF protection on POST requests
- [ ] Test session expiry handling
- [ ] Test logout functionality

---

## 🧪 Testing Authentication

### Manual Tests:

#### Test 1: View Authentication
```bash
# Open browser in incognito mode
# Try to access: http://localhost:8000/
# Expected: Redirect to /login/?next=/
```

#### Test 2: WebSocket Authentication
```javascript
// Open browser console (logged out)
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/');
// Expected: Connection closes with code 4001
```

#### Test 3: API Authentication
```javascript
// Open browser console (logged out)
fetch('/api/agents/list/')
    .then(r => console.log(r.status));
// Expected: 302 (redirect) or 401/403
```

#### Test 4: CSRF Protection
```javascript
// Open browser console (logged in)
fetch('/api/agents/execute/', {
    method: 'POST',
    body: JSON.stringify({agent_name: 'test'})
})
.then(r => console.log(r.status));
// Expected: 403 Forbidden (no CSRF token)

// With CSRF token
window.authManager.post('/api/agents/execute/', {agent_name: 'test'})
    .then(r => console.log(r.status));
// Expected: 200 OK (or appropriate response)
```

---

## 🚨 Common Authentication Issues & Solutions

### Issue 1: WebSocket Connects But No User Data
**Symptom**: WebSocket connects but `scope["user"]` is AnonymousUser

**Solution**:
```python
# Ensure AuthMiddlewareStack in routing.py
application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(  # ← Must be here
        URLRouter(websocket_urlpatterns)
    ),
})
```

### Issue 2: CSRF Token Missing
**Symptom**: POST requests fail with 403 Forbidden

**Solution**:
```python
# Add to base view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class AuthenticatedView(LoginRequiredMixin, TemplateView):
    ...
```

### Issue 3: Session Expires, User Not Redirected
**Symptom**: User stays on page but requests fail

**Solution**:
```javascript
// In auth.js, check response status
if (response.status === 401 || response.status === 403) {
    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
}
```

### Issue 4: User Data Not in Template Context
**Symptom**: Template shows `{{ user_data.username }}` as blank

**Solution**:
```python
# Ensure view calls get_context_data and includes user_data
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['user_data'] = self.get_user_data()  # ← Must be here
    return context
```

---

## 📚 Related Documentation

- Django Authentication: https://docs.djangoproject.com/en/4.2/topics/auth/
- Django Channels Authentication: https://channels.readthedocs.io/en/stable/topics/authentication.html
- CSRF Protection: https://docs.djangoproject.com/en/4.2/ref/csrf/

---

## 🎯 Summary

**4 Layers of Authentication:**
1. ✅ Django views require login
2. ✅ WebSocket connections check user
3. ✅ Templates receive user context
4. ✅ JavaScript has user data & CSRF token

**Every Component Authenticated:**
- Views → `LoginRequiredMixin` or `@login_required`
- WebSockets → `AuthenticatedConsumer` base class
- Templates → User context in every page
- JavaScript → `authManager` for all requests

**Result:** Zero authentication issues! 🎉

---

**Status**: 📋 REFERENCE GUIDE COMPLETE

**Next**: Start implementing Phase 1 with this authentication architecture!
