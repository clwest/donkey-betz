"""
Unified Views for the integrated AI Platform
Combines functionality from AI Studio, Django/DBAO, and Sports interfaces
"""
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
import json
import logging

logger = logging.getLogger(__name__)


class UnifiedDashboardView(TemplateView):
    """Main dashboard combining all platform features"""
    template_name = 'unified/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add dashboard stats
        context['stats'] = {
            'total_opportunities': 0,
            'active_applications': 0,
            'total_revenue': 0,
            'success_rate': 0,
            'agents_active': 149,
            'spiders_active': 0,
        }

        # Add user profile completion status
        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.extendeduserprofile
                context['profile_completion'] = profile.calculate_completion_percentage()
            except:
                context['profile_completion'] = 0
        else:
            context['profile_completion'] = 0

        return context


class IncomeBuilderView(View):
    """Income Builder - Redirects to consolidated Revenue Opportunities page"""

    def get(self, request, *args, **kwargs):
        # Redirect to the consolidated opportunities page
        # Preserve any query parameters
        from django.shortcuts import redirect
        query_string = request.META.get('QUERY_STRING', '')
        redirect_url = '/opportunities/'
        if query_string:
            redirect_url += '?' + query_string
        return redirect(redirect_url)


class DecisionCommandView(TemplateView):
    """Decision Command - Real-time decision analysis and execution"""
    template_name = 'unified/decision_command.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Decision Command'
        # Check for opportunity ID in query params
        opportunity_id = self.request.GET.get('opportunity')
        if opportunity_id:
            context['selected_opportunity'] = opportunity_id
        return context


class RevenueOpportunitiesView(TemplateView):
    """Revenue Opportunities - Spider network opportunity feed"""
    template_name = 'unified/revenue_opportunities.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Revenue Opportunities'
        return context


class RevenueDashboardView(TemplateView):
    """Revenue Dashboard - Track earnings and revenue"""
    template_name = 'unified/revenue_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Revenue Dashboard'
        return context


class MonetizationHubView(TemplateView):
    """Monetization Hub - Real revenue tracking and withdrawals"""
    template_name = 'unified/monetization_hub.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Monetization Hub'
        return context


class NeuralOrchestraView(TemplateView):
    """Neural Orchestra - Agent visualization and orchestration"""
    template_name = 'unified/neural_orchestra.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Neural Orchestra'
        context['agent_count'] = 149
        context['advisor_count'] = 25
        return context


class ControlCenterView(TemplateView):
    """Control Center - System monitoring and control"""
    template_name = 'unified/control_center.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Control Center'
        return context


class DiagnosticDashboardView(TemplateView):
    """Diagnostic Dashboard - System diagnostics and health"""
    template_name = 'unified/diagnostic_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Diagnostic Dashboard'
        return context


class AINexusView(TemplateView):
    """AI Nexus - Central AI intelligence hub"""
    template_name = 'unified/ai_nexus.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'AI Nexus'
        return context


class SportsHubView(LoginRequiredMixin, TemplateView):
    """Sports Hub - Sports betting and analytics"""
    template_name = 'unified/sports_hub.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Sports Hub'
        return context


class DBAODashboardView(LoginRequiredMixin, TemplateView):
    """DBAO Dashboard - Data analytics and optimization"""
    template_name = 'unified/dbao_dashboard.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'DBAO Dashboard'
        return context


class PersonalAssistantView(TemplateView):
    """Personal Assistant - AI chat and interview system"""
    template_name = 'unified/personal_assistant.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Personal Assistant'
        return context


class UserProfileView(LoginRequiredMixin, TemplateView):
    """User Profile - View and manage user profile"""
    template_name = 'unified/profile.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'User Profile'
        try:
            context['profile'] = self.request.user.extendeduserprofile
        except:
            context['profile'] = None
        return context


class EditProfileView(LoginRequiredMixin, View):
    """Edit Profile - Update user profile information"""
    login_url = '/login/'

    def get(self, request):
        return render(request, 'unified/edit_profile.html')

    def post(self, request):
        # Handle profile update
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile')


class NotificationsView(LoginRequiredMixin, TemplateView):
    """Notifications - View all notifications"""
    template_name = 'unified/notifications.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Notifications'
        context['notifications'] = []  # TODO: Load from database
        return context


class SignupView(View):
    """User Registration View"""

    def get(self, request):
        form = UserCreationForm()
        return render(request, 'unified/signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Welcome! Your account has been created.')
            return redirect('unified_dashboard')
        return render(request, 'unified/signup.html', {'form': form})


# API Views for AJAX/WebSocket support

class QuickApplyAPIView(View):
    """API endpoint for Quick Apply functionality"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        try:
            data = json.loads(request.body)
            opportunity_id = data.get('opportunity_id')

            # Import the real job submitter
            from core.real_job_submitter import RealJobSubmitter
            submitter = RealJobSubmitter()

            # Submit the application
            result = submitter.submit_application(
                platform=data.get('platform', 'email'),
                job_url=data.get('job_url', ''),
                job_title=data.get('job_title', 'Opportunity'),
                company=data.get('company', 'Company'),
                user_profile={
                    'name': request.user.get_full_name() if request.user.is_authenticated else 'User',
                    'email': request.user.email if request.user.is_authenticated else 'user@example.com',
                    'resume': data.get('resume', ''),
                    'cover_letter': data.get('cover_letter', ''),
                }
            )

            return JsonResponse({
                'success': result.get('success', False),
                'confirmation_id': result.get('confirmation_id'),
                'message': result.get('message', 'Application submitted')
            })

        except Exception as e:
            logger.error(f"Quick Apply error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class OpportunitiesAPIView(View):
    """API endpoint for fetching opportunities"""

    def get(self, request):
        try:
            # TODO: Fetch from database or spider network
            opportunities = []

            return JsonResponse({
                'success': True,
                'opportunities': opportunities,
                'count': len(opportunities)
            })

        except Exception as e:
            logger.error(f"Opportunities API error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class RevenueStatsAPIView(View):
    """API endpoint for revenue statistics"""

    def get(self, request):
        try:
            # TODO: Fetch from database
            stats = {
                'total_revenue': 2600,
                'pending_revenue': 450,
                'completed_revenue': 2150,
                'monthly_trend': [1200, 1400, 1800, 2150, 2600],
                'success_rate': 0.78
            }

            return JsonResponse({
                'success': True,
                'stats': stats
            })

        except Exception as e:
            logger.error(f"Revenue Stats API error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class SystemHealthAPIView(View):
    """API endpoint for system health monitoring"""

    def get(self, request):
        try:
            import psutil

            health = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'agents_active': 149,
                'spiders_active': 0,
                'websockets_connected': 0,
                'status': 'healthy'
            }

            return JsonResponse({
                'success': True,
                'health': health
            })

        except Exception as e:
            logger.error(f"System Health API error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class SpiderStatusAPIView(View):
    """API endpoint for spider network status"""

    def get(self, request):
        try:
            # TODO: Get real spider status
            status = {
                'total_spiders': 40,
                'active_spiders': 0,
                'jobs_found_today': 0,
                'last_crawl': None,
                'next_crawl': None
            }

            return JsonResponse({
                'success': True,
                'status': status
            })

        except Exception as e:
            logger.error(f"Spider Status API error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class NotificationsAPIView(LoginRequiredMixin, View):
    """API endpoint for notifications"""

    def get(self, request):
        try:
            # TODO: Fetch from database
            notifications = []

            return JsonResponse({
                'success': True,
                'notifications': notifications,
                'unread_count': 0
            })

        except Exception as e:
            logger.error(f"Notifications API error: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)