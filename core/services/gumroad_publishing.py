"""
Gumroad Publishing Service

Handles the complete pipeline for publishing AI-generated content to Gumroad:
- Download images from various storage formats (data URI, local path, URL)
- Upload to Gumroad API with proper multipart file handling
- Create and track ContentDistribution records

Created: Session 487 - Golden Egg Strategy (Auto-Publishing)
"""

import base64
import os
import logging
import requests
from decimal import Decimal
from typing import Tuple, Optional
from django.conf import settings

from content.models import ImageHistory
from core.models_unified_system import ContentDistribution, UserPlatformAccount

logger = logging.getLogger(__name__)


class GumroadPublishingService:
    """
    Service for publishing AI-generated images to Gumroad for sale.

    Handles:
    - Image download from data URIs, local paths, or URLs
    - Gumroad API product creation with file uploads
    - ContentDistribution record management
    """

    GUMROAD_API_BASE = "https://api.gumroad.com/v2"

    def __init__(self, user):
        """
        Initialize with a user to get their Gumroad OAuth credentials.

        Args:
            user: Django User object
        """
        self.user = user
        self.account = self._get_gumroad_account()

    def _get_gumroad_account(self) -> Optional[UserPlatformAccount]:
        """Get the user's connected Gumroad account."""
        try:
            return UserPlatformAccount.objects.get(
                user=self.user,
                platform='gumroad',
                is_active=True
            )
        except UserPlatformAccount.DoesNotExist:
            return None

    def download_image(self, image: ImageHistory) -> Tuple[bytes, str, str]:
        """
        Download image data from various storage formats.

        Args:
            image: ImageHistory instance

        Returns:
            Tuple of (image_bytes, filename, mime_type)

        Handles three formats:
        1. Data URI: data:image/png;base64,...
        2. Local path: /media/generated_images/...
        3. URL: http://... or https://...
        """
        file_path = image.file_path

        if not file_path:
            raise ValueError(f"Image {image.id} has no file_path")

        # Format 1: Data URI (base64 encoded)
        if file_path.startswith('data:'):
            return self._download_from_data_uri(file_path, image)

        # Format 2: Local file path
        if not file_path.startswith('http'):
            return self._download_from_local(file_path, image)

        # Format 3: Remote URL
        return self._download_from_url(file_path, image)

    def _download_from_data_uri(self, data_uri: str, image: ImageHistory) -> Tuple[bytes, str, str]:
        """Extract image data from a data URI."""
        try:
            # Parse: data:image/png;base64,iVBORw0KGgo...
            header, data = data_uri.split(',', 1)

            # Extract MIME type: image/png
            mime_type = header.split(';')[0].split(':')[1]

            # Determine extension from MIME
            ext = mime_type.split('/')[-1]
            if ext == 'jpeg':
                ext = 'jpg'

            # Decode base64
            image_bytes = base64.b64decode(data)

            # Generate filename
            filename = image.filename or f"ai-generated-{image.id}.{ext}"
            if not filename.endswith(f'.{ext}'):
                filename = f"{filename}.{ext}"

            logger.info(f"Downloaded {len(image_bytes)} bytes from data URI for image {image.id}")
            return image_bytes, filename, mime_type

        except Exception as e:
            logger.error(f"Failed to parse data URI for image {image.id}: {e}")
            raise ValueError(f"Invalid data URI format: {e}")

    def _download_from_local(self, file_path: str, image: ImageHistory) -> Tuple[bytes, str, str]:
        """Read image from local filesystem."""
        # Handle paths with or without leading slash
        if file_path.startswith('/'):
            # Could be absolute or relative to MEDIA_ROOT
            if file_path.startswith('/media/'):
                # Relative to MEDIA_ROOT
                relative_path = file_path[7:]  # Strip '/media/'
                full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
            elif os.path.exists(file_path):
                # Absolute path exists
                full_path = file_path
            else:
                # Try as relative to MEDIA_ROOT
                full_path = os.path.join(settings.MEDIA_ROOT, file_path.lstrip('/'))
        else:
            # Relative path
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Image file not found: {full_path}")

        # Read file
        with open(full_path, 'rb') as f:
            image_bytes = f.read()

        # Determine MIME type from extension
        filename = os.path.basename(full_path)
        ext = os.path.splitext(filename)[1].lower().lstrip('.')

        mime_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp',
        }
        mime_type = mime_map.get(ext, 'image/png')

        logger.info(f"Read {len(image_bytes)} bytes from {full_path} for image {image.id}")
        return image_bytes, filename, mime_type

    def _download_from_url(self, url: str, image: ImageHistory) -> Tuple[bytes, str, str]:
        """Download image from a remote URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            image_bytes = response.content

            # Try to get MIME type from headers
            content_type = response.headers.get('content-type', 'image/png')
            mime_type = content_type.split(';')[0].strip()

            # Generate filename
            ext = mime_type.split('/')[-1]
            if ext == 'jpeg':
                ext = 'jpg'
            filename = image.filename or f"ai-generated-{image.id}.{ext}"

            logger.info(f"Downloaded {len(image_bytes)} bytes from {url} for image {image.id}")
            return image_bytes, filename, mime_type

        except requests.RequestException as e:
            logger.error(f"Failed to download image from {url}: {e}")
            raise ValueError(f"Failed to download image: {e}")

    def upload_to_gumroad(
        self,
        image: ImageHistory,
        title: str,
        price_cents: int,
        description: Optional[str] = None
    ) -> dict:
        """
        Upload an image to Gumroad as a new product.

        Args:
            image: ImageHistory instance
            title: Product title
            price_cents: Price in cents (e.g., 999 for $9.99)
            description: Optional product description

        Returns:
            Gumroad API response dict
        """
        if not self.account:
            raise ValueError("No Gumroad account connected. Please connect your Gumroad account first.")

        if not self.account.access_token:
            raise ValueError("Gumroad account has no access token. Please reconnect your account.")

        # Download the image
        image_bytes, filename, mime_type = self.download_image(image)

        # Build description
        if not description:
            prompt_preview = (image.prompt[:200] + '...') if len(image.prompt) > 200 else image.prompt
            description = f"AI-generated artwork.\n\nPrompt: {prompt_preview}"

            if image.model_used:
                description += f"\n\nGenerated with: {image.model_used}"

        # Prepare multipart upload
        files = {
            'preview': (filename, image_bytes, mime_type),
            'file': (filename, image_bytes, mime_type),
        }

        data = {
            'access_token': self.account.access_token,
            'name': title,
            'price': price_cents,
            'description': description,
        }

        # Make API request
        url = f"{self.GUMROAD_API_BASE}/products"

        logger.info(f"Uploading to Gumroad: {title} at ${price_cents/100:.2f}")

        try:
            response = requests.post(url, data=data, files=files, timeout=60)
            response.raise_for_status()
            result = response.json()

            if result.get('success'):
                logger.info(f"Successfully created Gumroad product: {result.get('product', {}).get('short_url')}")
            else:
                logger.error(f"Gumroad API error: {result}")

            return result

        except requests.RequestException as e:
            logger.error(f"Gumroad API request failed: {e}")
            raise ValueError(f"Failed to upload to Gumroad: {e}")

    def publish_image(
        self,
        image_id: int,
        title: Optional[str] = None,
        price: Decimal = Decimal('9.99'),
        description: Optional[str] = None
    ) -> ContentDistribution:
        """
        Main entry point: Publish an image to Gumroad and create a ContentDistribution record.

        Args:
            image_id: ID of the ImageHistory to publish
            title: Optional custom title (defaults to generated title)
            price: Price in USD (default $9.99)
            description: Optional custom description

        Returns:
            ContentDistribution record
        """
        # Get the image
        try:
            image = ImageHistory.objects.get(id=image_id, user=self.user)
        except ImageHistory.DoesNotExist:
            raise ValueError(f"Image {image_id} not found or not owned by user")

        # Generate title if not provided
        if not title:
            # Use prompt as title (truncated)
            if image.prompt:
                title = image.prompt[:50]
                if len(image.prompt) > 50:
                    title += '...'
            else:
                title = f"AI Artwork #{image.sequential_number or image.id}"

        # Convert price to cents
        price_cents = int(price * 100)

        # Upload to Gumroad
        result = self.upload_to_gumroad(image, title, price_cents, description)

        if not result.get('success'):
            error_msg = result.get('message', 'Unknown error')
            raise ValueError(f"Gumroad upload failed: {error_msg}")

        # Extract product info
        product = result.get('product', {})
        product_id = product.get('id')
        product_url = product.get('short_url')

        # Create ContentDistribution record
        distribution = ContentDistribution.objects.create(
            user=self.user,
            image_history=image,
            platform='gumroad',
            platform_account=self.account,
            title=title,
            description=description or '',
            price=price,
            platform_listing_id=product_id,
            platform_listing_url=product_url,
            status='published',
        )

        logger.info(f"Created ContentDistribution {distribution.id} for Gumroad product {product_id}")

        return distribution

    def get_product_stats(self, product_id: str) -> dict:
        """
        Get sales stats for a Gumroad product.

        Args:
            product_id: Gumroad product ID

        Returns:
            Product stats dict
        """
        if not self.account or not self.account.access_token:
            raise ValueError("No Gumroad account connected")

        url = f"{self.GUMROAD_API_BASE}/products/{product_id}"
        params = {'access_token': self.account.access_token}

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get product stats: {e}")
            raise ValueError(f"Failed to get product stats: {e}")
