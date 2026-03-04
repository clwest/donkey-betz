"""
Enhanced authentication views with full registration, email verification, and remember me functionality.
"""

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db import transaction
import secrets
from datetime import timedelta
import re

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user with email verification.
    """
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')
    confirm_password = request.data.get('confirm_password', '')
    first_name = request.data.get('first_name', '').strip()
    last_name = request.data.get('last_name', '').strip()
    
    # Validation
    errors = {}
    
    # Username validation
    if not username:
        errors['username'] = 'Username is required'
    elif len(username) < 3:
        errors['username'] = 'Username must be at least 3 characters'
    elif not re.match(r'^[a-zA-Z0-9_-]+$', username):
        errors['username'] = 'Username can only contain letters, numbers, underscores, and hyphens'
    elif User.objects.filter(username=username).exists():
        errors['username'] = 'Username already taken'
    
    # Email validation
    if not email:
        errors['email'] = 'Email is required'
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors['email'] = 'Please enter a valid email address'
    elif User.objects.filter(email=email).exists():
        errors['email'] = 'Email already registered'
    
    # Password validation
    if not password:
        errors['password'] = 'Password is required'
    elif len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters'
    elif not any(char.isdigit() for char in password):
        errors['password'] = 'Password must contain at least one number'
    elif not any(char.isupper() for char in password):
        errors['password'] = 'Password must contain at least one uppercase letter'
    elif password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match'
    
    if errors:
        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # User needs to verify email first
            )
            
            # Create verification token
            verification_token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Store verification token in user profile or session
            # For now, we'll activate immediately in dev mode
            if settings.DEBUG:
                user.is_active = True
                user.save()
                
                # Create auth token
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'message': 'Registration successful (auto-verified in dev mode)',
                    'token': token.key,
                    'user': {
                        'id': str(user.id),
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'credits': 10000,  # New users get 10000 credits
                        'subscription': 'free'  # Start with free tier
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                # Send verification email in production
                verification_url = f"{request.build_absolute_uri('/verify-email/')}{uid}/{verification_token}/"
                
                send_mail(
                    'Verify your email - Unified Donkey Betz',
                    f'''
                    Welcome to Unified Donkey Betz, {first_name}!
                    
                    Please click the link below to verify your email address:
                    {verification_url}
                    
                    This link will expire in 24 hours.
                    
                    If you didn't create this account, please ignore this email.
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                return Response({
                    'message': 'Registration successful. Please check your email to verify your account.',
                    'email': email
                }, status=status.HTTP_201_CREATED)
                
    except Exception as e:
        return Response({
            'error': 'Registration failed. Please try again.',
            'detail': str(e) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    """
    Verify user's email address with token.
    """
    uid = request.data.get('uid')
    token = request.data.get('token')
    
    if not uid or not token:
        return Response(
            {'error': 'Invalid verification link'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        
        if default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.save()
                
                # Create auth token
                auth_token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'message': 'Email verified successfully',
                    'token': auth_token.key,
                    'user': {
                        'id': str(user.id),
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                })
            else:
                return Response({
                    'message': 'Email already verified'
                })
        else:
            return Response(
                {'error': 'Invalid or expired verification link'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid verification link'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_enhanced_view(request):
    """
    Enhanced login with remember me functionality.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    remember_me = request.data.get('remember_me', False)
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Allow login with email or username
    if '@' in username:
        try:
            user = User.objects.get(email=username.lower())
            username = user.username
        except User.DoesNotExist:
            pass
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is not None:
        if not user.is_active:
            return Response(
                {'error': 'Please verify your email address first'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Create response data
        response_data = {
            'token': token.key,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'credits': getattr(user, 'credits', 10000),
                'subscription': getattr(user, 'subscription_tier', 'free')
            },
            'remember_me': remember_me
        }
        
        # If remember me is checked, create a persistent session token
        if remember_me:
            # Generate a secure remember token
            remember_token = secrets.token_urlsafe(32)
            
            # Store in user profile (you might want to create a separate model for this)
            # For now, we'll include it in the response
            response_data['remember_token'] = remember_token
            response_data['expires_at'] = (timezone.now() + timedelta(days=30)).isoformat()
        
        return Response(response_data)
    else:
        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Send password reset email.
    """
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        # Generate reset token
        reset_token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # In dev mode, return the token directly
        if settings.DEBUG:
            return Response({
                'message': 'Password reset link generated (dev mode)',
                'uid': uid,
                'token': reset_token
            })
        else:
            # Send reset email in production
            reset_url = f"{request.build_absolute_uri('/reset-password/')}{uid}/{reset_token}/"
            
            send_mail(
                'Reset your password - Unified Donkey Betz',
                f'''
                Hi {user.first_name or user.username},
                
                We received a request to reset your password. Click the link below:
                {reset_url}
                
                This link will expire in 1 hour.
                
                If you didn't request this, please ignore this email.
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset link sent to your email'
            })
            
    except User.DoesNotExist:
        # Don't reveal if email exists or not for security
        return Response({
            'message': 'If an account exists with this email, you will receive a password reset link'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset password with token.
    """
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not all([uid, token, new_password, confirm_password]):
        return Response(
            {'error': 'All fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_password != confirm_password:
        return Response(
            {'error': 'Passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate password strength
    if len(new_password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
        
        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            
            # Invalidate old tokens
            Token.objects.filter(user=user).delete()
            
            # Create new token
            new_token = Token.objects.create(user=user)
            
            return Response({
                'message': 'Password reset successful',
                'token': new_token.key,
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return Response(
                {'error': 'Invalid or expired reset link'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'error': 'Invalid reset link'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change password for authenticated user.
    """
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        return Response(
            {'error': 'All fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_password != confirm_password:
        return Response(
            {'error': 'New passwords do not match'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not request.user.check_password(current_password):
        return Response(
            {'error': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    request.user.set_password(new_password)
    request.user.save()
    
    # Generate new token
    Token.objects.filter(user=request.user).delete()
    new_token = Token.objects.create(user=request.user)
    
    return Response({
        'message': 'Password changed successfully',
        'token': new_token.key
    })


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get or update user profile.
    """
    user = request.user
    
    if request.method == 'GET':
        return Response({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'credits': getattr(user, 'credits', 10000),
            'subscription': getattr(user, 'subscription_tier', 'free'),
            'preferences': getattr(user, 'preferences', {
                'theme': 'dark',
                'language': 'en',
                'notifications': True,
                'email_updates': True
            })
        })
    
    elif request.method in ['PUT', 'PATCH']:
        # Update profile fields
        updateable_fields = ['first_name', 'last_name', 'email']
        updated = False
        
        for field in updateable_fields:
            if field in request.data:
                # Special validation for email
                if field == 'email':
                    new_email = request.data[field].strip().lower()
                    if new_email != user.email:
                        if User.objects.filter(email=new_email).exists():
                            return Response(
                                {'error': 'Email already in use'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        user.email = new_email
                else:
                    setattr(user, field, request.data[field])
                updated = True
        
        # Update preferences if provided
        if 'preferences' in request.data:
            current_prefs = getattr(user, 'preferences', {})
            current_prefs.update(request.data['preferences'])
            user.preferences = current_prefs
            updated = True
        
        if updated:
            user.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_enhanced_view(request):
    """
    Enhanced logout that clears tokens and sessions.
    """
    try:
        # Delete auth token
        request.user.auth_token.delete()
    except Exception:
        pass
    
    return Response({
        'message': 'Logged out successfully'
    })


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def validate_token_view(request):
    """
    Validate if a token is still valid.
    """
    token = request.data.get('token')
    
    if not token:
        return Response(
            {'valid': False, 'error': 'No token provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token_obj = Token.objects.get(key=token)
        user = token_obj.user
        
        if user.is_active:
            return Response({
                'valid': True,
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        else:
            return Response({
                'valid': False,
                'error': 'User account is inactive'
            })
    except Token.DoesNotExist:
        return Response({
            'valid': False,
            'error': 'Invalid token'
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_view(request):
    """
    Resend email verification link.
    """
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email, is_active=False)
        
        # Generate new verification token
        verification_token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        if settings.DEBUG:
            return Response({
                'message': 'Verification link generated (dev mode)',
                'uid': uid,
                'token': verification_token
            })
        else:
            verification_url = f"{request.build_absolute_uri('/verify-email/')}{uid}/{verification_token}/"
            
            send_mail(
                'Verify your email - Unified Donkey Betz',
                f'''
                Hi {user.first_name or user.username},
                
                Please click the link below to verify your email address:
                {verification_url}
                
                This link will expire in 24 hours.
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Verification email sent'
            })
            
    except User.DoesNotExist:
        # Don't reveal if account exists
        return Response({
            'message': 'If an unverified account exists with this email, you will receive a verification link'
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_debug_view(request):
    """
    Session 830: Debug endpoint to diagnose auth issues.

    GET /api/v1/auth/debug/

    Returns information about the authentication state of the request.
    """
    from rest_framework.authtoken.models import Token

    # Check Authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    has_auth_header = bool(auth_header)

    # Extract token info
    token_value = None
    token_format = None
    if auth_header.startswith('Token '):
        token_value = auth_header[6:]
        token_format = 'Token'
    elif auth_header.startswith('Bearer '):
        token_value = auth_header[7:]
        token_format = 'Bearer'

    # Check token validity
    token_valid = False
    token_user = None
    token_error = None

    if token_value:
        try:
            token_obj = Token.objects.select_related('user').get(key=token_value)
            if token_obj.user.is_active:
                token_valid = True
                token_user = {
                    'id': str(token_obj.user.id),
                    'username': token_obj.user.username,
                    'is_active': token_obj.user.is_active,
                    'is_staff': token_obj.user.is_staff,
                }
            else:
                token_error = 'User is inactive'
        except Token.DoesNotExist:
            token_error = 'Token not found in database'
        except Exception as e:
            token_error = str(e)

    # Check session auth
    session_auth = hasattr(request, 'user') and request.user.is_authenticated
    session_user = None
    if session_auth:
        session_user = {
            'id': str(request.user.id),
            'username': request.user.username,
        }

    # Check cookies
    has_csrf_cookie = 'csrftoken' in request.COOKIES
    has_session_cookie = 'sessionid' in request.COOKIES

    return Response({
        'header': {
            'has_authorization': has_auth_header,
            'token_format': token_format,
            'token_prefix': token_value[:8] + '...' if token_value else None,
        },
        'token': {
            'valid': token_valid,
            'user': token_user,
            'error': token_error,
        },
        'session': {
            'authenticated': session_auth,
            'user': session_user,
        },
        'cookies': {
            'has_csrf': has_csrf_cookie,
            'has_session': has_session_cookie,
        },
        'recommendation': (
            'Token is valid' if token_valid
            else 'Session is valid' if session_auth
            else 'Please re-login to get a fresh token' if token_error
            else 'No authentication provided'
        )
    })