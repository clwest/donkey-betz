"""
Watermark Service - Steganography for Creator Attribution
==========================================================

Session 295: Creator Watermarks using LSB Steganography

This service embeds invisible watermarks into generated images,
allowing creators to prove ownership even when images are shared
without attribution.

Technique: LSB (Least Significant Bit) steganography
- Embeds data in the least significant bits of pixel values
- Visually imperceptible changes
- Survives most image operations (not heavy compression)

Usage:
    from core.services.watermark_service import WatermarkService

    service = WatermarkService()

    # Embed watermark
    watermarked_bytes = service.embed_watermark(
        image_bytes=original_bytes,
        creator_id="user-uuid",
        provenance_id="provenance-uuid"
    )

    # Extract watermark
    watermark_data = service.extract_watermark(watermarked_bytes)
    # Returns: {'creator_id': '...', 'provenance_id': '...', 'timestamp': '...'}

    # Verify ownership
    is_owner = service.verify_ownership(image_bytes, claimed_creator_id)
"""

import io
import json
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


# Magic bytes to identify our watermarks
WATERMARK_MAGIC = b"DKAI"  # Donkey King AI
WATERMARK_VERSION = 1


@dataclass
class WatermarkResult:
    """Result from watermark operations."""
    success: bool
    image_bytes: Optional[bytes] = None
    watermark_data: Optional[Dict] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'watermark_data': self.watermark_data,
            'error': self.error,
        }


class WatermarkService:
    """
    Steganography service for embedding invisible creator watermarks.

    Uses LSB (Least Significant Bit) technique to hide data in images
    without visible changes.
    """

    def __init__(self):
        self.magic = WATERMARK_MAGIC
        self.version = WATERMARK_VERSION

    def embed_watermark(
        self,
        image_bytes: bytes,
        creator_id: str,
        provenance_id: str,
        metadata: Optional[Dict] = None
    ) -> WatermarkResult:
        """
        Embed invisible watermark into image.

        Args:
            image_bytes: Original image bytes
            creator_id: UUID of the creator
            provenance_id: UUID of the provenance record
            metadata: Optional additional metadata

        Returns:
            WatermarkResult with watermarked image bytes
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if necessary (steganography needs consistent channels)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Create watermark payload
            payload = self._create_payload(creator_id, provenance_id, metadata)

            # Convert payload to binary
            binary_data = self._to_binary(payload)

            # Check if image can hold the data
            max_bytes = (image.width * image.height * 3) // 8
            if len(payload) > max_bytes:
                return WatermarkResult(
                    success=False,
                    error=f"Image too small. Max payload: {max_bytes} bytes, needed: {len(payload)} bytes"
                )

            # Embed data using LSB
            watermarked_image = self._embed_lsb(image, binary_data)

            # Convert back to bytes
            output = io.BytesIO()
            watermarked_image.save(output, format='PNG')  # PNG is lossless
            watermarked_bytes = output.getvalue()

            logger.info(f"Watermark embedded: creator={creator_id[:8]}..., provenance={provenance_id[:8]}...")

            return WatermarkResult(
                success=True,
                image_bytes=watermarked_bytes,
                watermark_data={
                    'creator_id': creator_id,
                    'provenance_id': provenance_id,
                    'embedded_at': datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Error embedding watermark: {e}")
            return WatermarkResult(success=False, error=str(e))

    def extract_watermark(self, image_bytes: bytes) -> WatermarkResult:
        """
        Extract watermark data from image.

        Args:
            image_bytes: Potentially watermarked image bytes

        Returns:
            WatermarkResult with extracted watermark data or None if not found
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_bytes))

            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Extract binary data from LSB
            binary_data = self._extract_lsb(image)

            # Try to decode payload
            payload = self._from_binary(binary_data)

            if payload is None:
                return WatermarkResult(
                    success=False,
                    error="No valid watermark found"
                )

            # Parse payload
            watermark_data = self._parse_payload(payload)

            if watermark_data is None:
                return WatermarkResult(
                    success=False,
                    error="Invalid watermark format"
                )

            logger.info(f"Watermark extracted: creator={watermark_data.get('creator_id', 'unknown')[:8]}...")

            return WatermarkResult(
                success=True,
                watermark_data=watermark_data
            )

        except Exception as e:
            logger.error(f"Error extracting watermark: {e}")
            return WatermarkResult(success=False, error=str(e))

    def verify_ownership(
        self,
        image_bytes: bytes,
        claimed_creator_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Verify claimed ownership matches embedded watermark.

        Args:
            image_bytes: Image to verify
            claimed_creator_id: UUID of claimed creator

        Returns:
            Tuple of (is_owner, watermark_data)
        """
        result = self.extract_watermark(image_bytes)

        if not result.success or not result.watermark_data:
            return False, None

        embedded_creator = result.watermark_data.get('creator_id', '')
        is_owner = embedded_creator == claimed_creator_id

        if is_owner:
            logger.info(f"Ownership verified for creator {claimed_creator_id[:8]}...")
        else:
            logger.warning(
                f"Ownership mismatch: claimed={claimed_creator_id[:8]}..., "
                f"embedded={embedded_creator[:8]}..."
            )

        return is_owner, result.watermark_data

    def _create_payload(
        self,
        creator_id: str,
        provenance_id: str,
        metadata: Optional[Dict] = None
    ) -> bytes:
        """Create watermark payload with magic bytes and checksum."""
        data = {
            'v': self.version,
            'c': creator_id,
            'p': provenance_id,
            't': datetime.utcnow().isoformat(),
        }

        if metadata:
            data['m'] = metadata

        # Convert to JSON and encode
        json_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')

        # Add checksum
        checksum = hashlib.md5(json_bytes).digest()[:4]  # 4 bytes for checksum

        # Format: MAGIC (4) + VERSION (1) + LENGTH (4) + DATA (N) + CHECKSUM (4)
        length = len(json_bytes).to_bytes(4, 'big')
        payload = self.magic + bytes([self.version]) + length + json_bytes + checksum

        return payload

    def _parse_payload(self, payload: bytes) -> Optional[Dict]:
        """Parse and validate watermark payload."""
        try:
            # Check magic bytes
            if not payload.startswith(self.magic):
                return None

            # Check version
            version = payload[4]
            if version != self.version:
                logger.warning(f"Watermark version mismatch: expected {self.version}, got {version}")

            # Get length
            length = int.from_bytes(payload[5:9], 'big')

            # Extract data and checksum
            json_bytes = payload[9:9+length]
            stored_checksum = payload[9+length:9+length+4]

            # Verify checksum
            calculated_checksum = hashlib.md5(json_bytes).digest()[:4]
            if stored_checksum != calculated_checksum:
                logger.warning("Watermark checksum mismatch")
                return None

            # Parse JSON
            data = json.loads(json_bytes.decode('utf-8'))

            return {
                'version': data.get('v'),
                'creator_id': data.get('c'),
                'provenance_id': data.get('p'),
                'timestamp': data.get('t'),
                'metadata': data.get('m'),
            }

        except Exception as e:
            logger.error(f"Error parsing watermark payload: {e}")
            return None

    def _to_binary(self, data: bytes) -> str:
        """Convert bytes to binary string."""
        return ''.join(format(byte, '08b') for byte in data)

    def _from_binary(self, binary: str) -> Optional[bytes]:
        """Convert binary string back to bytes."""
        try:
            # Read in 8-bit chunks
            bytes_list = []
            for i in range(0, len(binary), 8):
                byte_str = binary[i:i+8]
                if len(byte_str) == 8:
                    bytes_list.append(int(byte_str, 2))

            result = bytes(bytes_list)

            # Check for magic bytes to know where payload ends
            if self.magic in result:
                start = result.index(self.magic)
                # Find payload length
                if start + 9 <= len(result):
                    length = int.from_bytes(result[start+5:start+9], 'big')
                    end = start + 9 + length + 4  # header + data + checksum
                    return result[start:end]

            return None

        except Exception as e:
            logger.error(f"Error converting binary to bytes: {e}")
            return None

    def _embed_lsb(self, image: Image.Image, binary_data: str) -> Image.Image:
        """Embed binary data into image using LSB technique."""
        # Convert to numpy array for faster manipulation
        pixels = np.array(image, dtype=np.uint8)

        # Flatten to 1D array of pixel values
        flat = pixels.flatten()

        # Add terminator to mark end of data
        binary_data = binary_data + '1111111111111110'  # End marker

        # Embed each bit in LSB
        for i, bit in enumerate(binary_data):
            if i >= len(flat):
                break
            # Clear LSB and set new bit
            flat[i] = (flat[i] & 0xFE) | int(bit)

        # Reshape back to image dimensions
        watermarked = flat.reshape(pixels.shape)

        return Image.fromarray(watermarked, mode='RGB')

    def _extract_lsb(self, image: Image.Image, max_bits: int = 100000) -> str:
        """Extract LSB data from image."""
        # Convert to numpy array
        pixels = np.array(image, dtype=np.uint8)

        # Flatten to 1D array
        flat = pixels.flatten()

        # Extract LSB from each pixel value
        binary_data = ''
        for i in range(min(len(flat), max_bits)):
            binary_data += str(flat[i] & 1)

            # Check for end marker every 16 bits
            if i >= 15 and i % 8 == 7:
                if binary_data[-16:] == '1111111111111110':
                    binary_data = binary_data[:-16]  # Remove end marker
                    break

        return binary_data


# Convenience functions
def embed_creator_watermark(
    image_bytes: bytes,
    creator_id: str,
    provenance_id: str
) -> bytes:
    """
    Quick function to embed watermark and return watermarked bytes.

    Returns original bytes if embedding fails.
    """
    service = WatermarkService()
    result = service.embed_watermark(image_bytes, creator_id, provenance_id)

    if result.success and result.image_bytes:
        return result.image_bytes
    else:
        logger.warning(f"Watermark embedding failed: {result.error}")
        return image_bytes


def verify_creator_ownership(
    image_bytes: bytes,
    claimed_creator_id: str
) -> bool:
    """Quick function to verify ownership claim."""
    service = WatermarkService()
    is_owner, _ = service.verify_ownership(image_bytes, claimed_creator_id)
    return is_owner
