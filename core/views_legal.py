"""
Session 403: Legal Case Files API Endpoints
Pro Se Legal Assistant - Document Upload and Analysis

This module provides API endpoints for managing legal case documents,
including upload, analysis, and integration with the LegalDocDrafterAgent.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


# =============================================================================
# Legal Case Files Document Types
# =============================================================================

LEGAL_DOCUMENT_TYPES = {
    'court_order': 'Court Order / Ruling',
    'denied_motion': 'Denied Motion',
    'motion': 'Filed Motion',
    'correspondence': 'Correspondence',
    'opposing_filing': 'Opposing Party Filing',
    'financial': 'Financial Document',
    'evidence': 'Evidence / Exhibit',
    'other': 'Other Legal Document',
}


# =============================================================================
# List Legal Case Files
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_legal_case_files(request):
    """
    List all legal case files for the current user.
    Returns documents from the LegalDocument model.
    """
    user = request.user

    try:
        from core.models_unified_system import LegalDocument

        documents = LegalDocument.objects.filter(user=user).order_by('-created_at')

        # Calculate stats
        total = documents.count()
        court_orders = documents.filter(document_type__in=['court_order', 'denied_motion']).count()
        motions = documents.filter(document_type__in=['motion', 'opposing_filing']).count()
        processed = documents.filter(status__in=['finalized', 'review']).count()

        # Serialize documents
        docs_data = []
        for doc in documents[:100]:  # Limit to 100 most recent
            docs_data.append({
                'id': str(doc.id),
                'title': doc.title,
                'document_type': doc.document_type,
                'status': doc.status,
                'word_count': len(doc.content.split()) if doc.content else 0,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
                'case_id': str(doc.case_id) if doc.case_id else None,
            })

        return Response({
            'success': True,
            'documents': docs_data,
            'stats': {
                'total': total,
                'court_orders': court_orders,
                'motions': motions,
                'processed': processed,
            }
        })

    except Exception as e:
        logger.error(f"Error listing legal case files: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Upload Legal Case File
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_legal_case_file(request):
    """
    Upload a legal document (PDF, TXT, DOC, DOCX).
    Processes the file, extracts text, and optionally analyzes it.
    """
    user = request.user
    logger.info(f"[SESSION 404] upload_legal_case_file called by user: {user.id}")

    try:
        # Get file from request
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({
                'success': False,
                'error': 'No file provided'
            }, status=400)

        # Get parameters
        document_type = request.POST.get('document_type', 'other')
        context = request.POST.get('context', '')
        analyze = request.POST.get('analyze', 'false').lower() == 'true'
        generate_embeddings = request.POST.get('generate_embeddings', 'true').lower() == 'true'

        logger.info(f"[SESSION 404] Upload params: document_type={document_type}, analyze={analyze}, context={context[:50] if context else 'none'}")

        # Validate file type
        filename = uploaded_file.name.lower()
        if not any(filename.endswith(ext) for ext in ['.pdf', '.txt', '.doc', '.docx']):
            return Response({
                'success': False,
                'error': 'Invalid file type. Supported: PDF, TXT, DOC, DOCX'
            }, status=400)

        # Check file size (10MB max)
        if uploaded_file.size > 10 * 1024 * 1024:
            return Response({
                'success': False,
                'error': 'File size exceeds 10MB limit'
            }, status=400)

        # Process the file to extract text
        file_content = uploaded_file.read()
        extracted_text = ''

        if filename.endswith('.pdf'):
            extracted_text = extract_pdf_text(file_content)
        elif filename.endswith('.txt'):
            extracted_text = file_content.decode('utf-8', errors='ignore')
        elif filename.endswith('.doc') or filename.endswith('.docx'):
            extracted_text = extract_docx_text(file_content, filename)

        if not extracted_text or len(extracted_text.strip()) < 50:
            return Response({
                'success': False,
                'error': 'Could not extract text from file. Please ensure the file contains readable text.'
            }, status=400)

        # Create LegalDocument record
        from core.models_unified_system import LegalDocument

        doc = LegalDocument.objects.create(
            user=user,
            document_type=document_type,
            title=uploaded_file.name,
            content=extracted_text,
            original_query=context,
            generation_context={
                'source': 'upload',
                'original_filename': uploaded_file.name,
                'file_size': uploaded_file.size,
                'user_context': context,
                'uploaded_at': timezone.now().isoformat(),
            },
            status='review',  # Uploaded docs start in review status
        )

        # Generate embeddings if requested
        if generate_embeddings:
            try:
                from core.tasks import generate_legal_document_embeddings
                generate_legal_document_embeddings.delay(str(doc.id))
            except Exception as e:
                logger.warning(f"Could not queue embedding generation: {e}")

        # Analyze document if requested
        analysis = None
        logger.info(f"[SESSION 404] Analyze requested: {analyze}, document_type: {document_type}")
        if analyze:
            try:
                logger.info(f"[SESSION 404] Starting analysis for document {doc.id}...")
                analysis = analyze_legal_document(doc, context)
                logger.info(f"[SESSION 404] Analysis complete. Has full_analysis: {bool(analysis.get('full_analysis') if analysis else False)}")
            except Exception as e:
                logger.error(f"[SESSION 404] Error analyzing document: {e}")
                import traceback
                traceback.print_exc()
                analysis = {
                    'summary': 'Document uploaded successfully.',
                    'issues': 'Analysis could not be completed at this time.',
                    'recommendations': 'Please review the document manually.',
                    'forms': 'Unable to determine relevant forms.'
                }

        logger.info(f"[SESSION 404] Returning response with analysis: {bool(analysis)}")
        return Response({
            'success': True,
            'document': {
                'id': str(doc.id),
                'title': doc.title,
                'document_type': doc.document_type,
                'status': doc.status,
                'word_count': len(extracted_text.split()),
                'created_at': doc.created_at.isoformat(),
            },
            'analysis': analysis
        })

    except Exception as e:
        logger.error(f"Error uploading legal case file: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Get Legal Case File Details
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_legal_case_file(request, document_id):
    """
    Get details of a specific legal case file.
    """
    user = request.user

    try:
        from core.models_unified_system import LegalDocument

        try:
            doc = LegalDocument.objects.get(id=document_id, user=user)
        except LegalDocument.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=404)

        return Response({
            'success': True,
            'document': {
                'id': str(doc.id),
                'title': doc.title,
                'document_type': doc.document_type,
                'content': doc.content,
                'original_query': doc.original_query,
                'generation_context': doc.generation_context,
                'status': doc.status,
                'version': doc.version,
                'word_count': len(doc.content.split()) if doc.content else 0,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
                'case_id': str(doc.case_id) if doc.case_id else None,
            }
        })

    except Exception as e:
        logger.error(f"Error getting legal case file: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Analyze Legal Case File
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_legal_case_file(request, document_id):
    """
    Analyze a legal case file using AI.
    Returns summary, issues, recommendations, and relevant forms.
    """
    user = request.user

    try:
        from core.models_unified_system import LegalDocument

        try:
            doc = LegalDocument.objects.get(id=document_id, user=user)
        except LegalDocument.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=404)

        # Get additional context from request
        data = request.data if hasattr(request, 'data') else {}
        additional_context = data.get('context', '')

        # Perform analysis
        analysis = analyze_legal_document(doc, additional_context)

        return Response({
            'success': True,
            'analysis': analysis,
            'document_id': str(doc.id),
        })

    except Exception as e:
        logger.error(f"Error analyzing legal case file: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Delete Legal Case File
# =============================================================================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_legal_case_file(request, document_id):
    """
    Delete a legal case file.
    """
    user = request.user

    try:
        from core.models_unified_system import LegalDocument

        try:
            doc = LegalDocument.objects.get(id=document_id, user=user)
        except LegalDocument.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=404)

        doc.delete()

        return Response({
            'success': True,
            'message': 'Document deleted successfully'
        })

    except Exception as e:
        logger.error(f"Error deleting legal case file: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Helper Functions
# =============================================================================

def extract_pdf_text(file_content: bytes) -> str:
    """Extract text from PDF file content."""
    try:
        import io
        from PyPDF2 import PdfReader

        pdf_file = io.BytesIO(file_content)
        reader = PdfReader(pdf_file)

        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return '\n\n'.join(text_parts)

    except ImportError:
        logger.error("PyPDF2 not installed")
        raise Exception("PDF processing not available. Please install PyPDF2.")
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise Exception(f"Could not extract text from PDF: {str(e)}")


def extract_docx_text(file_content: bytes, filename: str) -> str:
    """Extract text from DOC/DOCX file content."""
    try:
        import io

        # Try python-docx for .docx files
        if filename.endswith('.docx'):
            try:
                from docx import Document as DocxDocument
                docx_file = io.BytesIO(file_content)
                doc = DocxDocument(docx_file)
                return '\n\n'.join([para.text for para in doc.paragraphs if para.text])
            except ImportError:
                logger.warning("python-docx not installed, trying alternative")

        # Fallback: just try to decode as text
        try:
            return file_content.decode('utf-8', errors='ignore')
        except:
            return file_content.decode('latin-1', errors='ignore')

    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        raise Exception(f"Could not extract text from document: {str(e)}")


def analyze_legal_document(doc, additional_context: str = '') -> dict:
    """
    Analyze a legal document using the LegalDocDrafterAgent.

    Session 404: Now routes through the LegalDocDrafterAgent to use the
    denied motion pipeline and motion rewriting tools.

    Returns structured analysis with summary, issues, recommendations, and forms.
    """
    logger.info(f"[SESSION 404] analyze_legal_document called for doc: {doc.id}, type: {doc.document_type}")

    try:
        from core.agents.legal import LegalDocDrafterAgent

        # Build task string that triggers the denied motion pipeline
        doc_type_label = LEGAL_DOCUMENT_TYPES.get(doc.document_type, doc.document_type)
        logger.info(f"[SESSION 404] Document type label: {doc_type_label}")

        # Construct task that will trigger denied motion mode if appropriate
        if doc.document_type == 'denied_motion':
            task = f"My motion was denied. Please analyze this denied motion and help me rewrite it correctly."
        else:
            task = f"Please analyze this {doc_type_label} and provide guidance."

        logger.info(f"[SESSION 404] Task constructed: {task}")

        # Build context with the document content
        context = {
            'document_type': doc.document_type,
            'motion_content': doc.content[:15000],  # Limit content length
            'analyzing_document': True,
            'case_file_id': str(doc.id),
            'additional_context': additional_context,
            'case_details': {
                'document_title': doc.title,
            }
        }

        logger.info(f"[SESSION 404] Context built, motion_content length: {len(context['motion_content'])}")

        # Create agent and execute
        agent = LegalDocDrafterAgent(user=doc.user)
        logger.info(f"[SESSION 404] LegalDocDrafterAgent created, calling execute()...")

        result = agent.execute(
            task=task,
            context=context,
            scifi_context={},
            spider_context={}
        )

        logger.info(f"[SESSION 404] Agent execute() returned: success={result.success}, has_message={bool(result.message)}, data_type={result.data.get('type') if result.data else 'N/A'}")

        if result.success and result.message:
            logger.info(f"[SESSION 404] Returning full_analysis, message length: {len(result.message)}")
            # Return the full agent output
            return {
                'summary': 'Document analyzed using Legal Assistant pipeline.',
                'full_analysis': result.message,
                'pipeline_used': result.data.get('type', 'standard'),
                'tools_called': result.data.get('tools_called', []),
            }
        else:
            # Fallback if agent failed
            logger.warning(f"[SESSION 404] Agent failed or no message. Error: {result.error}")
            return {
                'summary': f'Document: {doc.title}',
                'issues': result.error if result.error else 'Analysis could not be completed.',
                'recommendations': 'Consider consulting with a licensed Colorado attorney.',
                'forms': 'Unable to determine relevant forms automatically.'
            }

    except Exception as e:
        logger.error(f"[SESSION 404] Exception in analyze_legal_document: {e}")
        import traceback
        traceback.print_exc()
        return {
            'summary': f'Document: {doc.title}',
            'issues': f'AI analysis error: {str(e)}',
            'recommendations': 'Consider consulting with a licensed Colorado attorney.',
            'forms': 'Unable to determine relevant forms automatically.'
        }
