"""
Data encryption service migrated from donkey_betz
Handles encryption/decryption of sensitive data including embeddings
"""

from cryptography.fernet import Fernet
from django.conf import settings
import json
import logging
import os
from uuid import UUID

logger = logging.getLogger(__name__)


class UUIDEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID objects"""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


class EncryptionService:
    """Handle encryption/decryption of sensitive data"""
    
    def __init__(self):
        # Try to get encryption key from environment or settings
        encryption_key = os.environ.get('ENCRYPTION_KEY') or getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not encryption_key:
            logger.warning("No ENCRYPTION_KEY found - encryption service disabled")
            self.cipher = None
        else:
            try:
                self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            except Exception as e:
                logger.error(f"Failed to initialize cipher with primary key: {e}")
                self.cipher = None
        
        # Support backup key for migration (from donkey_betz)
        self.backup_cipher = None
        backup_key = os.environ.get('ENCRYPTION_KEY_BACKUP') or getattr(settings, 'ENCRYPTION_KEY_BACKUP', None)
        
        if backup_key:
            try:
                self.backup_cipher = Fernet(backup_key.encode() if isinstance(backup_key, str) else backup_key)
                logger.info("Backup encryption key loaded for migration support")
            except Exception as e:
                logger.error(f"Failed to initialize backup cipher: {e}")
    
    def encrypt(self, plaintext):
        """Encrypt text data"""
        # Handle None separately from empty string
        if plaintext is None:
            return None
        
        if not self.cipher:
            logger.warning("Encryption requested but no cipher available")
            return plaintext
            
        # Convert to string and encrypt (including empty strings)
        plaintext = str(plaintext)
        try:
            return self.cipher.encrypt(plaintext.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return plaintext  # Return unencrypted as fallback
    
    def decrypt(self, ciphertext):
        """Decrypt text data with automatic fallback to backup key"""
        # Handle None and empty string
        if ciphertext is None:
            return None
        if ciphertext == '':
            return ''
        
        # Check if it looks encrypted (Fernet tokens start with gAAAAA)
        if not isinstance(ciphertext, str) or not ciphertext.startswith('gAAAAA'):
            # Not encrypted, return as-is
            return ciphertext
        
        # Try primary cipher first
        if self.cipher:
            try:
                return self.cipher.decrypt(ciphertext.encode()).decode()
            except Exception as e:
                logger.warning(f"Primary key decryption failed: {e}")
        
        # Try backup cipher for migration
        if self.backup_cipher:
            try:
                decrypted = self.backup_cipher.decrypt(ciphertext.encode()).decode()
                logger.debug("Successfully decrypted with backup key")
                return decrypted
            except Exception as e:
                logger.warning(f"Backup key decryption failed: {e}")
        
        # If both failed, log error and return empty string
        logger.error(f"Failed to decrypt data with both primary and backup keys")
        return ""  # Return empty string for failed decryption
    
    def encrypt_json(self, data):
        """Encrypt JSON data"""
        if not data:
            return None
        
        if not self.cipher:
            # No encryption available, store as JSON string
            try:
                return json.dumps(data, cls=UUIDEncoder)
            except Exception as e:
                logger.error(f"JSON serialization failed: {e}")
                return None
        
        try:
            json_str = json.dumps(data, cls=UUIDEncoder)
            return self.encrypt(json_str)
        except Exception as e:
            logger.error(f"JSON encryption failed: {e}")
            # Try without encryption as fallback
            return json.dumps(data, cls=UUIDEncoder)
    
    def decrypt_json(self, ciphertext):
        """Decrypt JSON data"""
        if not ciphertext:
            return None
        
        try:
            # Check if it's already JSON (unencrypted)
            if isinstance(ciphertext, str):
                if ciphertext.startswith('gAAAAA'):
                    # It's encrypted, decrypt it
                    json_str = self.decrypt(ciphertext)
                    return json.loads(json_str) if json_str else None
                else:
                    # Try to parse as JSON directly
                    try:
                        return json.loads(ciphertext)
                    except json.JSONDecodeError:
                        # Not valid JSON, return empty list/dict
                        logger.debug("Invalid JSON in unencrypted field, returning empty value")
                        return [] if ciphertext.strip().startswith('[') else {}
            elif isinstance(ciphertext, (list, dict)):
                # Already a Python object
                return ciphertext
            else:
                return None
        except Exception as e:
            logger.error(f"JSON decryption failed: {e}")
            # Return safe default instead of raising
            return []
    
    def can_decrypt(self, ciphertext):
        """Check if we can decrypt this ciphertext"""
        if not ciphertext or not isinstance(ciphertext, str):
            return False
        
        if not ciphertext.startswith('gAAAAA'):
            return True  # Not encrypted, can return as-is
        
        # Try to decrypt with available keys
        if self.cipher:
            try:
                self.cipher.decrypt(ciphertext.encode())
                return True
            except Exception as _e:
                logger.warning(
                    "encryption_service.can_decrypt: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        
        if self.backup_cipher:
            try:
                self.backup_cipher.decrypt(ciphertext.encode())
                return True
            except Exception as _e:
                logger.warning(
                    "encryption_service.can_decrypt: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        
        return False


# Global encryption service instance
_encryption_service = None

def get_encryption_service():
    """Get or create encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def decrypt_content(encrypted_text):
    """Convenience function to decrypt content"""
    if not encrypted_text:
        return ""
    
    service = get_encryption_service()
    return service.decrypt(encrypted_text)


def encrypt_content(plaintext):
    """Convenience function to encrypt content"""
    if plaintext is None:
        return None
    
    service = get_encryption_service()
    return service.encrypt(plaintext)