"""
Session 136 Part 2: Cloud storage utilities for image persistence.

This module provides utilities for uploading images to Cloudinary for permanent storage,
preventing file loss issues when local files are deleted.

Key Features:
    - Upload images to Cloudinary with organized folder structure
    - Delete images from Cloudinary when needed
    - Automatic error handling and logging
    - Support for both upload and cleanup operations

Usage:
    from content.cloud_storage import CloudStorageManager

    # Upload an image
    result = CloudStorageManager.upload_image(
        file_path='/path/to/image.png',
        public_id='image_abc123',
        folder='ai-content-studio/images'
    )

    if result['success']:
        print(f"Uploaded to: {result['url']}")

    # Delete an image
    deleted = CloudStorageManager.delete_image('image_abc123')
"""

import os
import logging

logger = logging.getLogger(__name__)


class CloudStorageManager:
    """
    Manage cloud storage uploads for images.

    This class provides methods to upload and delete images from Cloudinary,
    ensuring permanent storage and preventing file loss issues.
    """

    @staticmethod
    def upload_image(file_path, public_id=None, folder="ai-content-studio"):
        """
        Upload image to Cloudinary for permanent storage.

        Args:
            file_path (str): Local file path to the image
            public_id (str, optional): Public ID for the image in Cloudinary.
                                      If not provided, Cloudinary generates one.
            folder (str): Cloudinary folder path. Default: "ai-content-studio"

        Returns:
            dict: Result dictionary with keys:
                - success (bool): Whether upload succeeded
                - url (str): Cloudinary URL if successful
                - public_id (str): Public ID in Cloudinary if successful
                - error (str): Error message if failed

        Example:
            >>> result = CloudStorageManager.upload_image(
            ...     file_path='/path/to/image.png',
            ...     public_id='image_123',
            ...     folder='ai-content-studio/images'
            ... )
            >>> if result['success']:
            ...     print(f"Image URL: {result['url']}")
        """
        try:
            # Check if Cloudinary is configured
            try:
                import cloudinary
                import cloudinary.uploader
            except ImportError:
                return {
                    'success': False,
                    'error': 'Cloudinary package not installed. Run: pip install cloudinary'
                }

            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File not found: {file_path}'
                }

            logger.info(f"📤 Uploading image to Cloudinary: {file_path}")

            # Upload to Cloudinary
            upload_params = {
                'folder': folder,
                'resource_type': 'image',
                'overwrite': False
            }

            if public_id:
                upload_params['public_id'] = public_id

            result = cloudinary.uploader.upload(file_path, **upload_params)

            logger.info(f"✅ Successfully uploaded to Cloudinary")
            logger.info(f"   URL: {result['secure_url']}")
            logger.info(f"   Public ID: {result['public_id']}")

            return {
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id']
            }

        except Exception as e:
            logger.error(f"❌ Cloudinary upload failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_image(public_id):
        """
        Delete image from Cloudinary.

        Args:
            public_id (str): The public ID of the image in Cloudinary

        Returns:
            bool: True if deletion succeeded, False otherwise

        Example:
            >>> deleted = CloudStorageManager.delete_image('image_123')
            >>> if deleted:
            ...     print("Image deleted successfully")
        """
        try:
            import cloudinary
            import cloudinary.uploader

            logger.info(f"🗑️  Deleting image from Cloudinary: {public_id}")

            result = cloudinary.uploader.destroy(public_id)

            if result.get('result') == 'ok':
                logger.info(f"✅ Successfully deleted from Cloudinary")
                return True
            else:
                logger.warning(f"⚠️  Cloudinary delete returned: {result}")
                return False

        except Exception as e:
            logger.error(f"❌ Cloudinary delete failed: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def is_configured():
        """
        Check if Cloudinary is properly configured.

        Returns:
            tuple: (bool, str) - (is_configured, message)

        Example:
            >>> configured, message = CloudStorageManager.is_configured()
            >>> if configured:
            ...     print("Cloudinary is ready!")
            ... else:
            ...     print(f"Setup needed: {message}")
        """
        try:
            import cloudinary

            config = cloudinary.config()

            if not config.cloud_name:
                return False, "CLOUDINARY_CLOUD_NAME not set in environment"

            if not config.api_key:
                return False, "CLOUDINARY_API_KEY not set in environment"

            if not config.api_secret:
                return False, "CLOUDINARY_API_SECRET not set in environment"

            return True, "Cloudinary is properly configured"

        except ImportError:
            return False, "Cloudinary package not installed. Run: pip install cloudinary"
        except Exception as e:
            return False, f"Configuration error: {str(e)}"
