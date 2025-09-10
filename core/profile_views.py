"""
Profile management views including avatar upload functionality.
"""

import os
import uuid
from PIL import Image
from io import BytesIO
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import hashlib


# Create media directories if they don't exist
AVATAR_DIR = os.path.join(settings.MEDIA_ROOT if hasattr(settings, 'MEDIA_ROOT') else 'media', 'avatars')
if not os.path.exists(AVATAR_DIR):
    os.makedirs(AVATAR_DIR, exist_ok=True)


@api_view(['POST'])
@permission_classes([AllowAny])  # Using AllowAny for dev, should be IsAuthenticated in production
@parser_classes([MultiPartParser, FormParser])
def upload_avatar_view(request):
    """
    Upload a new avatar image for the user.
    """
    if 'avatar' not in request.FILES:
        return Response(
            {'error': 'No avatar file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    avatar_file = request.FILES['avatar']
    
    # Validate file size (max 5MB)
    if avatar_file.size > 5 * 1024 * 1024:
        return Response(
            {'error': 'File size must be less than 5MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if avatar_file.content_type not in allowed_types:
        return Response(
            {'error': 'Invalid file type. Allowed types: JPEG, PNG, GIF, WebP'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Open and validate image
        img = Image.open(avatar_file)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize image to a reasonable size (500x500 max)
        max_size = (500, 500)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Generate unique filename
        user_id = request.user.id if request.user.is_authenticated else 'demo'
        file_ext = os.path.splitext(avatar_file.name)[1] or '.jpg'
        filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}{file_ext}"
        filepath = os.path.join(AVATAR_DIR, filename)
        
        # Save the image
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)
        
        # Save to storage
        path = default_storage.save(f'avatars/{filename}', ContentFile(output.read()))
        
        # Build the URL
        if hasattr(settings, 'MEDIA_URL'):
            avatar_url = f"{settings.MEDIA_URL}{path}"
        else:
            # For development, return a direct path
            avatar_url = f"/media/{path}"
        
        # In production, you would update the user's profile here
        # For now, just return the URL
        
        return Response({
            'message': 'Avatar uploaded successfully',
            'avatar_url': avatar_url,
            'filename': filename
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to process image: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([AllowAny])  # Should be IsAuthenticated in production
def delete_avatar_view(request):
    """
    Delete the user's avatar and revert to default.
    """
    try:
        # In production, you would delete the actual file here
        # For now, just return success
        
        # Generate default avatar URL (using dicebear or similar)
        username = request.user.username if request.user.is_authenticated else 'demo'
        default_avatar = f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}"
        
        return Response({
            'message': 'Avatar deleted successfully',
            'avatar_url': default_avatar
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to delete avatar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([AllowAny])  # Should be IsAuthenticated in production
def update_profile_view(request):
    """
    Update user profile information.
    """
    try:
        # Extract update data
        update_data = request.data
        
        # In production, you would validate and update the actual user profile here
        # For now, just acknowledge the update
        
        # Fields that can be updated
        allowed_fields = [
            'first_name', 'last_name', 'email', 'bio', 'display_name',
            'occupation', 'location', 'preferred_ai_model', 
            'default_content_tone', 'auto_save', 'dark_mode',
            'email_notifications', 'default_citation_style',
            'preferred_book_length', 'research_topics'
        ]
        
        # Filter to only allowed fields
        filtered_data = {
            key: value for key, value in update_data.items() 
            if key in allowed_fields
        }
        
        # In production, save to database
        # For now, just return success
        
        return Response({
            'message': 'Profile updated successfully',
            'updated_fields': list(filtered_data.keys())
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to update profile: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])  # Should be IsAuthenticated in production
def generate_avatar_view(request):
    """
    Generate a new random avatar using an avatar service.
    """
    try:
        # Get parameters
        style = request.data.get('style', 'avataaars')
        seed = request.data.get('seed', uuid.uuid4().hex[:8])
        
        # Available styles for dicebear
        available_styles = [
            'avataaars', 'bottts', 'identicon', 'initials',
            'micah', 'miniavs', 'pixel-art', 'shapes'
        ]
        
        if style not in available_styles:
            style = 'avataaars'
        
        # Generate avatar URL
        avatar_url = f"https://api.dicebear.com/7.x/{style}/svg?seed={seed}"
        
        return Response({
            'message': 'Avatar generated successfully',
            'avatar_url': avatar_url,
            'style': style,
            'seed': seed
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate avatar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )