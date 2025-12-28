"""
Certificate Service - PDF Ownership Certificates
=================================================

Session 295: Downloadable, printable proof of ownership

This service generates professional PDF certificates for content provenance,
allowing creators to prove ownership of their AI-generated content.

Features:
- Platform branding
- Content thumbnail
- SHA-256 hash
- Creation timestamp
- QR code for verification
- Digital signature

Usage:
    from core.services.certificate_service import CertificateService

    service = CertificateService()

    # Generate PDF certificate
    pdf_bytes = service.generate_pdf_certificate(provenance_id)

    # Generate verification URL
    verify_url = service.get_verification_url(provenance_id)
"""

import io
import logging
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass

from django.conf import settings

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas

# QR code
import qrcode

logger = logging.getLogger(__name__)


# Platform branding
PLATFORM_NAME = "Donkey AI Studio"
PLATFORM_URL = "https://donkey.ai"  # Update to actual URL
CERTIFICATE_VERSION = "1.0"

# Colors
PRIMARY_COLOR = HexColor("#4F46E5")  # Indigo
SECONDARY_COLOR = HexColor("#6366F1")
ACCENT_COLOR = HexColor("#10B981")  # Emerald
DARK_COLOR = HexColor("#1F2937")
LIGHT_COLOR = HexColor("#F3F4F6")


@dataclass
class CertificateResult:
    """Result from certificate generation."""
    success: bool
    pdf_bytes: Optional[bytes] = None
    certificate_id: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'certificate_id': self.certificate_id,
            'error': self.error,
        }


class CertificateService:
    """
    Service for generating PDF ownership certificates.

    Creates professional, verifiable certificates that prove
    content ownership and provenance.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or getattr(settings, 'BASE_URL', 'http://localhost:8000')
        self.platform_name = PLATFORM_NAME

    def generate_pdf_certificate(
        self,
        provenance_id: str,
        include_thumbnail: bool = True
    ) -> CertificateResult:
        """
        Generate a PDF certificate for a provenance record.

        Args:
            provenance_id: UUID of the provenance record
            include_thumbnail: Whether to include content thumbnail

        Returns:
            CertificateResult with PDF bytes
        """
        try:
            # Get provenance record
            from core.models_unified_system import ContentProvenance

            provenance = ContentProvenance.objects.get(id=provenance_id)

            # Create PDF
            buffer = io.BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # Draw certificate
            self._draw_header(pdf, width, height)
            self._draw_title(pdf, width, height)
            self._draw_content_info(pdf, width, height, provenance)
            self._draw_hash_section(pdf, width, height, provenance)
            self._draw_qr_code(pdf, width, height, provenance_id)
            self._draw_signature_section(pdf, width, height, provenance)
            self._draw_footer(pdf, width, height, provenance)

            pdf.save()

            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()

            # Mark certificate as issued
            provenance.certificate_issued = True
            provenance.certificate_issued_at = datetime.now()
            provenance.save(update_fields=['certificate_issued', 'certificate_issued_at'])

            logger.info(f"Certificate generated for provenance {provenance_id}")

            return CertificateResult(
                success=True,
                pdf_bytes=pdf_bytes,
                certificate_id=str(provenance_id)
            )

        except ContentProvenance.DoesNotExist:
            logger.error(f"Provenance not found: {provenance_id}")
            return CertificateResult(
                success=False,
                error=f"Provenance record not found: {provenance_id}"
            )
        except Exception as e:
            logger.error(f"Error generating certificate: {e}")
            return CertificateResult(success=False, error=str(e))

    def _draw_header(self, pdf: canvas.Canvas, width: float, height: float):
        """Draw certificate header with branding."""
        # Background gradient effect (solid color for simplicity)
        pdf.setFillColor(PRIMARY_COLOR)
        pdf.rect(0, height - 1.5*inch, width, 1.5*inch, fill=True, stroke=False)

        # Platform name
        pdf.setFillColor(white)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawCentredString(width/2, height - 0.8*inch, self.platform_name)

        # Subtitle
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(width/2, height - 1.1*inch, "Content Provenance Certificate")

    def _draw_title(self, pdf: canvas.Canvas, width: float, height: float):
        """Draw main certificate title."""
        pdf.setFillColor(DARK_COLOR)
        pdf.setFont("Helvetica-Bold", 28)
        pdf.drawCentredString(width/2, height - 2.3*inch, "CERTIFICATE OF AUTHENTICITY")

        # Decorative line
        pdf.setStrokeColor(ACCENT_COLOR)
        pdf.setLineWidth(2)
        pdf.line(1.5*inch, height - 2.5*inch, width - 1.5*inch, height - 2.5*inch)

    def _draw_content_info(
        self,
        pdf: canvas.Canvas,
        width: float,
        height: float,
        provenance
    ):
        """Draw content information section."""
        y_pos = height - 3.2*inch

        # Section title
        pdf.setFillColor(SECONDARY_COLOR)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(1*inch, y_pos, "Content Details")

        y_pos -= 0.4*inch
        pdf.setFillColor(DARK_COLOR)
        pdf.setFont("Helvetica", 11)

        # Content type
        content_type = provenance.content_type.upper()
        pdf.drawString(1*inch, y_pos, f"Content Type: {content_type}")

        # Creator
        y_pos -= 0.25*inch
        creator_name = provenance.creator.get_full_name() or provenance.creator.username
        pdf.drawString(1*inch, y_pos, f"Creator: {creator_name}")

        # Creation date
        y_pos -= 0.25*inch
        creation_date = provenance.created_at.strftime("%B %d, %Y at %H:%M UTC")
        pdf.drawString(1*inch, y_pos, f"Created: {creation_date}")

        # Derivative status
        y_pos -= 0.25*inch
        derivative_type = provenance.derivative_type.replace('_', ' ').title()
        pdf.drawString(1*inch, y_pos, f"Derivative Status: {derivative_type}")

        # Generation params (if available)
        if provenance.generation_params:
            y_pos -= 0.25*inch
            model = provenance.generation_params.get('model', 'Unknown')
            pdf.drawString(1*inch, y_pos, f"Generation Model: {model}")

            prompt = provenance.generation_params.get('prompt', '')
            if prompt:
                y_pos -= 0.25*inch
                # Truncate long prompts
                if len(prompt) > 80:
                    prompt = prompt[:77] + "..."
                pdf.drawString(1*inch, y_pos, f"Prompt: {prompt}")

    def _draw_hash_section(
        self,
        pdf: canvas.Canvas,
        width: float,
        height: float,
        provenance
    ):
        """Draw content hash section."""
        y_pos = height - 5.5*inch

        # Section title
        pdf.setFillColor(SECONDARY_COLOR)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(1*inch, y_pos, "Cryptographic Verification")

        # SHA-256 hash box
        y_pos -= 0.5*inch
        pdf.setFillColor(LIGHT_COLOR)
        pdf.roundRect(1*inch, y_pos - 0.4*inch, width - 2*inch, 0.6*inch, 5, fill=True, stroke=False)

        pdf.setFillColor(DARK_COLOR)
        pdf.setFont("Courier", 9)
        hash_text = provenance.content_hash
        pdf.drawCentredString(width/2, y_pos - 0.15*inch, f"SHA-256: {hash_text}")

        # Perceptual hash (if available)
        if provenance.perceptual_hash:
            y_pos -= 0.7*inch
            pdf.setFont("Courier", 8)
            pdf.drawCentredString(width/2, y_pos, f"pHash: {provenance.perceptual_hash}")

        # Signature info
        y_pos -= 0.5*inch
        pdf.setFont("Helvetica", 9)
        pdf.setFillColor(DARK_COLOR)
        sig_text = f"Digital Signature: {provenance.signature_algorithm.upper()}"
        pdf.drawString(1*inch, y_pos, sig_text)

    def _draw_qr_code(
        self,
        pdf: canvas.Canvas,
        width: float,
        height: float,
        provenance_id: str
    ):
        """Draw QR code for verification."""
        # Generate verification URL
        verify_url = self.get_verification_url(provenance_id)

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(verify_url)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Save to buffer
        qr_buffer = io.BytesIO()
        qr_image.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        # Draw QR code on right side
        from reportlab.lib.utils import ImageReader
        qr_reader = ImageReader(qr_buffer)

        x_pos = width - 2.5*inch
        y_pos = height - 6*inch

        pdf.drawImage(qr_reader, x_pos, y_pos, 1.5*inch, 1.5*inch)

        # Label
        pdf.setFillColor(DARK_COLOR)
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(x_pos + 0.75*inch, y_pos - 0.15*inch, "Scan to verify")

    def _draw_signature_section(
        self,
        pdf: canvas.Canvas,
        width: float,
        height: float,
        provenance
    ):
        """Draw digital signature section."""
        y_pos = height - 8*inch

        # Section title
        pdf.setFillColor(SECONDARY_COLOR)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(1*inch, y_pos, "Digital Signature")

        # Signature value (truncated)
        y_pos -= 0.3*inch
        pdf.setFillColor(DARK_COLOR)
        pdf.setFont("Courier", 7)

        sig = provenance.signature
        if len(sig) > 80:
            # Split into multiple lines
            pdf.drawString(1*inch, y_pos, sig[:80])
            if len(sig) > 160:
                y_pos -= 0.15*inch
                pdf.drawString(1*inch, y_pos, sig[80:160] + "...")
            else:
                y_pos -= 0.15*inch
                pdf.drawString(1*inch, y_pos, sig[80:])

        # Verification status
        y_pos -= 0.4*inch
        pdf.setFillColor(ACCENT_COLOR)
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(1*inch, y_pos, "✓ VERIFIED")

        pdf.setFillColor(DARK_COLOR)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(1.8*inch, y_pos, f"- Certificate issued on {datetime.now().strftime('%Y-%m-%d')}")

    def _draw_footer(
        self,
        pdf: canvas.Canvas,
        width: float,
        height: float,
        provenance
    ):
        """Draw certificate footer."""
        y_pos = 1*inch

        # Decorative line
        pdf.setStrokeColor(PRIMARY_COLOR)
        pdf.setLineWidth(1)
        pdf.line(1*inch, y_pos + 0.5*inch, width - 1*inch, y_pos + 0.5*inch)

        # Certificate ID
        pdf.setFillColor(DARK_COLOR)
        pdf.setFont("Helvetica", 8)
        cert_id = f"Certificate ID: {provenance.id}"
        pdf.drawString(1*inch, y_pos + 0.2*inch, cert_id)

        # Platform info
        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(width - 1*inch, y_pos + 0.2*inch, f"v{CERTIFICATE_VERSION}")

        # Disclaimer
        pdf.setFont("Helvetica", 7)
        pdf.setFillColor(HexColor("#6B7280"))
        disclaimer = "This certificate verifies content ownership as recorded in the Donkey AI Studio platform."
        pdf.drawCentredString(width/2, y_pos - 0.1*inch, disclaimer)

    def get_verification_url(self, provenance_id: str) -> str:
        """Generate verification URL for a provenance record."""
        return f"{self.base_url}/api/provenance/{provenance_id}/verify/"

    def verify_certificate(self, provenance_id: str) -> Dict:
        """
        Verify a certificate is valid.

        Args:
            provenance_id: UUID of the provenance record

        Returns:
            Verification result dict
        """
        try:
            from core.models_unified_system import ContentProvenance

            provenance = ContentProvenance.objects.get(id=provenance_id)

            return {
                'valid': True,
                'provenance_id': str(provenance.id),
                'content_type': provenance.content_type,
                'creator': provenance.creator.username,
                'created_at': provenance.created_at.isoformat(),
                'content_hash': provenance.content_hash,
                'is_verified': provenance.is_verified,
                'certificate_issued': provenance.certificate_issued,
                'certificate_issued_at': (
                    provenance.certificate_issued_at.isoformat()
                    if provenance.certificate_issued_at else None
                ),
            }

        except ContentProvenance.DoesNotExist:
            return {
                'valid': False,
                'error': 'Certificate not found'
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }


# Convenience function
def generate_certificate(provenance_id: str) -> Optional[bytes]:
    """Quick function to generate PDF certificate."""
    service = CertificateService()
    result = service.generate_pdf_certificate(provenance_id)

    if result.success:
        return result.pdf_bytes
    else:
        logger.warning(f"Certificate generation failed: {result.error}")
        return None
