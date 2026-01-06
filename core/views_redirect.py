"""
Redirect views for legacy Django template URLs to React frontend.

Session 688: Full UI deprecation - React becomes the only UI.
All legacy Django template URLs now redirect to React routes.
"""

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


# Mapping of legacy Django paths to React routes
REACT_ROUTE_MAP = {
    # Main studio pages -> /content
    'ai-studio': '/content',
    'ai-production-hub': '/content',
    'content-studio': '/content',

    # Dashboard pages -> /dashboard
    'ai-nexus': '/dashboard',
    'income-builder': '/dashboard',
    'dashboard': '/dashboard',
    'income': '/dashboard',
    'opportunities': '/dashboard',

    # Intelligence pages -> /intelligence
    'command': '/intelligence',
    'decisions': '/intelligence',
    'control': '/intelligence',

    # Agent pages -> /agents
    'neural-orchestra': '/agents',
    'visualization': '/agents',
    'learning': '/agents',

    # Betting pages -> /betting
    'sports': '/betting',
    'dbao': '/betting',

    # Portfolio pages -> /portfolio
    'revenue': '/portfolio',
    'monetization': '/portfolio',

    # Admin pages -> /admin
    'diagnostics': '/admin',

    # Direct mappings
    'assistant': '/assistant',
    'profile': '/profile',
    'settings': '/settings',
}


def create_redirect_view(react_path, require_login=True):
    """
    Factory function to create redirect views for legacy URLs.

    Args:
        react_path: The React route to redirect to
        require_login: Whether to require authentication (default True)

    Returns:
        A view function that redirects to the React route
    """
    def view(request, *args, **kwargs):
        return redirect(react_path)

    if require_login:
        return login_required(view)
    return view


# Pre-created redirect views for common routes
# These can be imported directly in urls.py

# Studio redirects
ai_studio_redirect = create_redirect_view('/content')
ai_production_hub_redirect = create_redirect_view('/content')
content_studio_redirect = create_redirect_view('/content')

# Dashboard redirects
ai_nexus_redirect = create_redirect_view('/dashboard')
income_builder_redirect = create_redirect_view('/dashboard')
dashboard_redirect = create_redirect_view('/dashboard')
opportunities_redirect = create_redirect_view('/dashboard')

# Intelligence redirects
command_redirect = create_redirect_view('/intelligence')
decisions_redirect = create_redirect_view('/intelligence')
control_redirect = create_redirect_view('/intelligence')

# Agent redirects
neural_orchestra_redirect = create_redirect_view('/agents')
visualization_redirect = create_redirect_view('/agents')
learning_redirect = create_redirect_view('/agents')

# Betting redirects
sports_redirect = create_redirect_view('/betting')
dbao_redirect = create_redirect_view('/betting')

# Portfolio redirects
revenue_redirect = create_redirect_view('/portfolio')
monetization_redirect = create_redirect_view('/portfolio')

# Admin redirects
diagnostics_redirect = create_redirect_view('/admin')

# Other redirects
assistant_redirect = create_redirect_view('/assistant')
profile_redirect = create_redirect_view('/profile')
settings_redirect = create_redirect_view('/settings')

# Login redirect (public)
login_redirect = create_redirect_view('/login', require_login=False)


def legacy_url_redirect(request, path=''):
    """
    Generic redirect handler for any unmapped legacy URL.
    Redirects to dashboard by default.
    """
    # Try to find a matching route
    path_key = path.strip('/').split('/')[0] if path else ''
    react_route = REACT_ROUTE_MAP.get(path_key, '/dashboard')
    return redirect(react_route)
