"""
Session 403: Legal Case Files API Endpoints
Pro Se Legal Assistant - Document Upload and Analysis

This module provides API endpoints for managing legal case documents,
including upload, analysis, and integration with the LegalDocDrafterAgent.
"""

import logging

from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
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
@permission_classes([AllowAny])  # Session 688: Allow public access for React frontend
def list_legal_case_files(request):
    """
    List all legal case files for the current user.
    Returns documents from the LegalDocument model.
    """
    user = request.user

    # Session 688: Return empty for anonymous users
    if not user.is_authenticated:
        return Response({'documents': [], 'stats': {'total': 0, 'court_orders': 0, 'motions': 0, 'evidence': 0}})

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
        # Session 405: Only run full analysis on denied motions, not court orders
        analysis = None
        logger.info(f"[SESSION 404] Analyze requested: {analyze}, document_type: {document_type}")

        # Court orders should NOT go through the motion analysis pipeline
        if document_type == 'court_order':
            logger.info(f"[SESSION 405] Court order uploaded - storing for future reference, not analyzing as motion")
            analysis = {
                'summary': '✅ Court Order Uploaded Successfully',
                'full_analysis': (
                    "## ✅ COURT ORDER SAVED\n\n"
                    f"**Document:** {uploaded_file.name}\n\n"
                    "This court order has been saved to your case files and will be used for:\n\n"
                    "- **Conflict Detection** - When you upload a motion, we'll check if your requests conflict with this order\n"
                    "- **Reference** - You can view this document anytime in your case files\n"
                    "- **Exhibit Attachment** - Include this as an exhibit when filing modification motions\n\n"
                    "---\n\n"
                    "### Next Steps\n\n"
                    "1. Upload your **motion** to get analysis and rewrite assistance\n"
                    "2. The system will automatically check your motion against this court order\n"
                    "3. Any conflicts will be flagged with recommendations\n"
                ),
                'document_stored': True,
            }
        elif analyze:
            try:
                logger.info(f"[SESSION 404] Starting analysis for document {doc.id}...")
                analysis = analyze_legal_document(doc, context, request=request)
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

        # Perform analysis - Session 406: Pass request for CaseProfile lookup
        analysis = analyze_legal_document(doc, additional_context, request=request)

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
        except Exception:
            return file_content.decode('latin-1', errors='ignore')

    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        raise Exception(f"Could not extract text from document: {str(e)}")


def analyze_legal_document(doc, additional_context: str = '', request=None) -> dict:
    """
    Analyze a legal document using the LegalDocDrafterAgent.

    Session 404: Now routes through the LegalDocDrafterAgent to use the
    denied motion pipeline and motion rewriting tools.

    Session 405: Now fetches uploaded court orders to pass as context for
    conflict detection (Enhancement #4).

    Session 406: Now accepts request to pass active_case_id for CaseProfile lookup.

    Returns structured analysis with summary, issues, recommendations, and forms.
    """
    logger.info(f"[SESSION 404] analyze_legal_document called for doc: {doc.id}, type: {doc.document_type}")

    try:
        from core.agents.legal import LegalDocDrafterAgent
        from core.models_unified_system import LegalDocument

        # =====================================================================
        # Session 405: Fetch uploaded court orders for conflict analysis
        # =====================================================================
        existing_order_text = ''
        existing_order_summary = ''
        uploaded_document_types = []

        try:
            # Get all court orders uploaded by this user
            court_orders = LegalDocument.objects.filter(
                user=doc.user,
                document_type='court_order'
            ).order_by('-created_at')[:5]  # Get up to 5 most recent orders

            if court_orders.exists():
                # Combine court order text (limit to prevent token overflow)
                order_texts = []
                for order in court_orders:
                    if order.content:
                        order_texts.append(f"--- Court Order: {order.title} ---\n{order.content[:5000]}")
                        uploaded_document_types.append('court_order')

                existing_order_text = '\n\n'.join(order_texts)[:15000]  # Cap total length
                logger.info(f"[SESSION 405] Found {court_orders.count()} court orders, total text length: {len(existing_order_text)}")
            else:
                logger.info("[SESSION 405] No court orders found for user")

            # Also check for any other uploaded documents to track types
            other_docs = LegalDocument.objects.filter(user=doc.user).exclude(id=doc.id).values_list('document_type', flat=True).distinct()
            uploaded_document_types.extend(list(other_docs))

        except Exception as e:
            logger.warning(f"[SESSION 405] Error fetching court orders: {e}")

        # Build task string that triggers the denied motion pipeline
        doc_type_label = LEGAL_DOCUMENT_TYPES.get(doc.document_type, doc.document_type)
        logger.info(f"[SESSION 404] Document type label: {doc_type_label}")

        # Construct task that will trigger denied motion mode if appropriate
        if doc.document_type == 'denied_motion':
            task = f"My motion was denied. Please analyze this denied motion and help me rewrite it correctly."
        else:
            task = f"Please analyze this {doc_type_label} and provide guidance."

        logger.info(f"[SESSION 404] Task constructed: {task}")

        # Session 406: Get active_case_id from session if request is available
        active_case_id = None
        if request and hasattr(request, 'session'):
            active_case_id = request.session.get('active_case_id')
            logger.info(f"[SESSION 406] Got active_case_id from session: {active_case_id}")

        # Build context with the document content
        context = {
            'document_type': doc.document_type,
            'motion_content': doc.content[:15000],  # Limit content length
            'analyzing_document': True,
            'case_file_id': str(doc.id),
            'additional_context': additional_context,
            'case_details': {
                'document_title': doc.title,
            },
            # Session 405: Add court order context for conflict detection
            'existing_order_text': existing_order_text,
            'existing_order_summary': existing_order_summary,
            'uploaded_document_types': uploaded_document_types,
            # Session 406: Pass active case ID for CaseProfile lookup
            'active_case_id': active_case_id,
            'request': request,  # Pass full request for session access
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
            response_data = {
                'summary': 'Document analyzed using Legal Assistant pipeline.',
                'full_analysis': result.message,
                'pipeline_used': result.data.get('type', 'standard'),
                'tools_called': result.data.get('tools_called', []),
            }
            # Session 407: Include document bundle if available for downloads
            if result.data.get('document_bundle'):
                response_data['document_bundle'] = result.data.get('document_bundle')
                logger.info(f"[SESSION 407] Document bundle included with {len(result.data['document_bundle'].get('sections', []))} sections")
            return response_data
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


# =============================================================================
# Session 407: Export Legal Document Section
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_legal_section(request):
    """
    Export a specific section from a legal document analysis as downloadable file.

    POST body:
    {
        "section_id": "motion_core",      # Required - ID of the section to export
        "format": "docx",                  # Optional - docx (default), md, txt
        "content": "...",                  # Required - The section content
        "label": "Verified Motion"         # Optional - For filename
    }

    Returns: File download response
    """
    from django.http import HttpResponse

    try:
        data = request.data
        section_id = data.get('section_id')
        export_format = data.get('format', 'docx').lower()
        content = data.get('content', '')
        label = data.get('label', section_id or 'document')

        if not section_id or not content:
            return Response({
                'success': False,
                'error': 'Missing required fields: section_id and content'
            }, status=400)

        # Sanitize filename
        safe_label = "".join(c for c in label if c.isalnum() or c in ' -_').strip()
        safe_label = safe_label.replace(' ', '_')[:50]  # Max 50 chars

        # Import the document bundle helpers
        from core.agents.legal.document_bundle import (
            DocumentSection,
            generate_docx_from_section,
            generate_txt_from_section,
            generate_md_from_section,
            generate_pdf_from_section
        )

        # Create a section object
        section = DocumentSection(
            id=section_id,
            label=label,
            role='exported',
            format='markdown',
            content=content
        )

        # Generate the file based on format
        if export_format == 'docx':
            file_bytes = generate_docx_from_section(section)
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            filename = f'{safe_label}.docx'
        elif export_format == 'pdf':
            file_bytes = generate_pdf_from_section(section)
            content_type = 'application/pdf'
            filename = f'{safe_label}.pdf'
        elif export_format == 'txt':
            file_bytes = generate_txt_from_section(section)
            content_type = 'text/plain'
            filename = f'{safe_label}.txt'
        elif export_format == 'md':
            file_bytes = generate_md_from_section(section)
            content_type = 'text/markdown'
            filename = f'{safe_label}.md'
        else:
            return Response({
                'success': False,
                'error': f'Unsupported format: {export_format}. Use docx, pdf, md, or txt.'
            }, status=400)

        # Create response with file download
        response = HttpResponse(file_bytes, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(file_bytes)

        logger.info(f"[Session 407] Exported section '{section_id}' as {export_format} ({len(file_bytes)} bytes)")
        return response

    except Exception as e:
        logger.error(f"[Session 407] Export error: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 408: Litigation Document Management APIs
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_litigation_documents(request, case_profile_id):
    """
    List all litigation documents for a case, organized by category.

    Session 410: Added query parameter filtering:
    - ?party=petitioner|respondent|court|third_party
    - ?role=motion|response|reply|order|exhibit|other
    - ?category=court_order|motion|response|evidence|court_rule
    """
    user = request.user

    try:
        from core.models_legal import CaseProfile, LitigationDocument

        # Verify user owns this case
        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id, user=user)
        except CaseProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Case profile not found'
            }, status=404)

        # Get documents by category
        documents = LitigationDocument.objects.filter(case_profile=case_profile)

        # Session 410: Apply filters from query params
        party_filter = request.query_params.get('party')
        role_filter = request.query_params.get('role')
        category_filter = request.query_params.get('category')

        if party_filter:
            documents = documents.filter(filing_party=party_filter)
        if role_filter:
            documents = documents.filter(litigation_role=role_filter)
        if category_filter:
            documents = documents.filter(category=category_filter)

        # Organize by category
        categories = {
            'court_order': {'label': 'Court Orders', 'documents': []},
            'motion': {'label': 'Motions', 'documents': []},
            'response': {'label': 'Responses/Replies', 'documents': []},
            'evidence': {'label': 'Evidence', 'documents': []},
            'court_rule': {'label': 'Court Rules', 'documents': []},
        }

        for doc in documents:
            doc_data = {
                'id': str(doc.id),
                'title': doc.title,
                'document_type': doc.document_type,
                'document_type_display': doc.get_document_type_display(),
                'filing_party': doc.filing_party,
                'filing_party_display': doc.get_filing_party_display(),
                # Session 410: Add litigation_role for thread tracking
                'litigation_role': doc.litigation_role,
                'litigation_role_display': doc.get_litigation_role_display(),
                'status': doc.status,
                'document_date': str(doc.document_date) if doc.document_date else None,
                'filed_date': str(doc.filed_date) if doc.filed_date else None,
                'deadline_date': str(doc.deadline_date) if doc.deadline_date else None,
                'word_count': len(doc.extracted_text.split()) if doc.extracted_text else 0,
                'uploaded_at': doc.uploaded_at.isoformat(),
                'responds_to': str(doc.responds_to_id) if doc.responds_to_id else None,
                'has_responses': doc.responses.exists(),
                # Session 410: Include thread info
                'response_count': doc.responses.count(),
            }

            if doc.category in categories:
                categories[doc.category]['documents'].append(doc_data)

        # Calculate stats
        stats = {
            'total': documents.count(),
            'court_orders': len(categories['court_order']['documents']),
            'motions': len(categories['motion']['documents']),
            'responses': len(categories['response']['documents']),
            'evidence': len(categories['evidence']['documents']),
            'pending_responses': documents.filter(
                category='motion',
                filing_party='respondent',
                status__in=['uploaded', 'analyzed']
            ).count(),
        }

        return Response({
            'success': True,
            'case_number': case_profile.case_number,
            'categories': categories,
            'stats': stats,
        })

    except Exception as e:
        logger.error(f"[Session 408] Error listing litigation documents: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_litigation_document(request, case_profile_id):
    """
    Upload a document to the litigation brain.
    Automatically processes, classifies, and indexes the document.
    """
    logger.info(f"upload_litigation_document called: case_profile_id={case_profile_id}")
    user = request.user

    try:
        from core.models_legal import CaseProfile
        from core.services.litigation_brain import get_document_ingestor

        # Verify user owns this case
        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id, user=user)
        except CaseProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Case profile not found'
            }, status=404)

        # Get file
        uploaded_file = request.FILES.get('file')
        logger.debug(f"uploaded_file: {uploaded_file}")
        if not uploaded_file:
            logger.warning("No file in request.FILES")
            return Response({
                'success': False,
                'error': 'No file provided'
            }, status=400)

        # Validate file type
        filename = uploaded_file.name.lower()
        logger.debug(f"filename: {filename}, size: {uploaded_file.size}")
        if not any(filename.endswith(ext) for ext in ['.pdf', '.txt', '.doc', '.docx', '.png', '.jpg', '.jpeg']):
            logger.warning(f"Invalid file type: {filename}")
            return Response({
                'success': False,
                'error': 'Invalid file type. Supported: PDF, TXT, DOC, DOCX, PNG, JPG'
            }, status=400)

        # Get classification info from form data
        category = request.POST.get('category')
        document_type = request.POST.get('document_type')
        filing_party = request.POST.get('filing_party')
        litigation_role = request.POST.get('litigation_role')  # Session 410
        document_date = request.POST.get('document_date')
        filed_date = request.POST.get('filed_date')
        responds_to_id = request.POST.get('responds_to')
        notes = request.POST.get('notes', '')
        logger.debug(f"category={category}, document_type={document_type}, filing_party={filing_party}, litigation_role={litigation_role}")

        # Process the document
        ingestor = get_document_ingestor()
        logger.debug("Calling ingestor.process_document...")
        result = ingestor.process_document(
            case_profile_id=case_profile.id,
            file_content=uploaded_file.read(),
            filename=uploaded_file.name,
            user_category=category,
            user_document_type=document_type,
            filing_party=filing_party,
            litigation_role=litigation_role,  # Session 410
            document_date=document_date,
            filed_date=filed_date,
            responds_to_id=responds_to_id if responds_to_id else None,
            notes=notes,
        )

        return Response(result)

    except Exception as e:
        logger.error(f"[Session 408] Error uploading litigation document: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_case_knowledge_graph(request, case_profile_id):
    """
    Get the case knowledge graph (case_context.json equivalent).
    """
    user = request.user

    try:
        from core.models_legal import CaseProfile, CaseKnowledgeGraph
        from core.services.litigation_brain import get_context_builder

        # Verify user owns this case
        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id, user=user)
        except CaseProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Case profile not found'
            }, status=404)

        # Get or build knowledge graph
        try:
            kg = CaseKnowledgeGraph.objects.get(case_profile=case_profile)
            if kg.rebuild_needed:
                builder = get_context_builder()
                builder.rebuild_knowledge_graph(case_profile.id)
                kg.refresh_from_db()
        except CaseKnowledgeGraph.DoesNotExist:
            builder = get_context_builder()
            builder.rebuild_knowledge_graph(case_profile.id)
            kg = CaseKnowledgeGraph.objects.get(case_profile=case_profile)

        return Response({
            'success': True,
            'knowledge_graph': kg.to_json(),
        })

    except Exception as e:
        logger.error(f"[Session 408] Error getting knowledge graph: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rebuild_knowledge_graph(request, case_profile_id):
    """
    Force rebuild of the case knowledge graph.
    """
    user = request.user

    try:
        from core.models_legal import CaseProfile
        from core.services.litigation_brain import get_context_builder

        # Verify user owns this case
        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id, user=user)
        except CaseProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Case profile not found'
            }, status=404)

        builder = get_context_builder()
        result = builder.rebuild_knowledge_graph(case_profile.id)

        return Response(result)

    except Exception as e:
        logger.error(f"[Session 408] Error rebuilding knowledge graph: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_response_to_filing(request, document_id):
    """
    Generate a response to an opposing party's filing.
    """
    user = request.user

    try:
        from core.models_legal import LitigationDocument
        from core.services.litigation_brain import get_response_writer

        doc = LitigationDocument.objects.filter(
            id=document_id,
            case_profile__user=user,
        ).first()
        if not doc:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=404)

        writer = get_response_writer()
        result = writer.generate_response(doc)

        return Response(result)

    except Exception as e:
        logger.error(f"[Session 408] Error generating response: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_generated_responses(request, case_profile_id):
    """
    List all generated responses for a case.
    """
    user = request.user

    try:
        from core.models_legal import CaseProfile, GeneratedResponse

        # Verify user owns this case
        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id, user=user)
        except CaseProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Case profile not found'
            }, status=404)

        responses = GeneratedResponse.objects.filter(case_profile=case_profile)

        data = []
        for r in responses:
            data.append({
                'id': str(r.id),
                'responds_to': {
                    'id': str(r.responds_to.id),
                    'title': r.responds_to.title,
                },
                'status': r.status,
                'exhibits_count': len(r.exhibits),
                'created_at': r.created_at.isoformat(),
                'updated_at': r.updated_at.isoformat(),
            })

        return Response({
            'success': True,
            'responses': data,
            'count': len(data),
        })

    except Exception as e:
        logger.error(f"[Session 408] Error listing responses: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_generated_response(request, response_id):
    """
    Get a specific generated response with all components.
    """
    user = request.user

    try:
        from core.models_legal import GeneratedResponse

        r = GeneratedResponse.objects.filter(
            id=response_id,
            case_profile__user=user,
        ).first()
        if not r:
            return Response({
                'success': False,
                'error': 'Response not found'
            }, status=404)

        return Response({
            'success': True,
            'response': {
                'id': str(r.id),
                'responds_to': {
                    'id': str(r.responds_to.id),
                    'title': r.responds_to.title,
                },
                'response_content': r.response_content,
                'factual_corrections': r.factual_corrections,
                'legal_standard': r.legal_standard,
                'argument': r.argument,
                'relief_requested': r.relief_requested,
                'full_document': r.full_document,
                'proposed_order': r.proposed_order,
                'exhibits': r.exhibits,
                'status': r.status,
                'created_at': r.created_at.isoformat(),
            }
        })

    except Exception as e:
        logger.error(f"[Session 408] Error getting response: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_filing_package(request, response_id):
    """
    Create a filing package (ZIP with all documents) for a response.
    """
    user = request.user

    try:
        from core.models_legal import GeneratedResponse
        from core.services.litigation_brain import get_filing_packager

        r = GeneratedResponse.objects.filter(
            id=response_id,
            case_profile__user=user,
        ).first()
        if not r:
            return Response({
                'success': False,
                'error': 'Response not found'
            }, status=404)

        # Get requested formats
        formats = request.data.get('formats', ['docx', 'txt'])

        packager = get_filing_packager()
        result = packager.create_filing_package(r, formats=formats)

        if not result.get('success'):
            return Response(result, status=500)

        # Return package info (files would be downloaded separately)
        return Response({
            'success': True,
            'package': {
                'response_id': result['response_id'],
                'documents_count': len(result['documents']),
                'files': [
                    {'name': f['name'], 'document_type': f['document_type']}
                    for f in result['files']
                ],
            }
        })

    except Exception as e:
        logger.error(f"[Session 408] Error creating filing package: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 410: Document Thread APIs
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_threads(request, case_profile_id):
    """
    Session 410: Get all document threads for a case.
    Returns Motion → Response → Reply chains grouped together.
    """
    user = request.user

    try:
        from core.models_legal import CaseProfile, LitigationDocument

        # Verify user owns this case
        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id, user=user)
        except CaseProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Case profile not found'
            }, status=404)

        # Get all root motions (motions that don't respond to anything)
        root_motions = LitigationDocument.objects.filter(
            case_profile=case_profile,
            litigation_role='motion',
            responds_to__isnull=True
        ).order_by('-filed_date', '-document_date', '-uploaded_at')

        threads = []
        for motion in root_motions:
            thread = {
                'id': str(motion.id),
                'title': motion.title,
                'chain': []
            }

            # Add the motion as first item
            thread['chain'].append({
                'id': str(motion.id),
                'title': motion.title,
                'litigation_role': 'motion',
                'litigation_role_display': motion.get_litigation_role_display(),
                'filing_party': motion.filing_party,
                'filing_party_display': motion.get_filing_party_display(),
                'filed_date': str(motion.filed_date) if motion.filed_date else None,
                'status': motion.status,
            })

            # Find response to this motion
            response = motion.responses.filter(litigation_role='response').first()
            if response:
                thread['chain'].append({
                    'id': str(response.id),
                    'title': response.title,
                    'litigation_role': 'response',
                    'litigation_role_display': response.get_litigation_role_display(),
                    'filing_party': response.filing_party,
                    'filing_party_display': response.get_filing_party_display(),
                    'filed_date': str(response.filed_date) if response.filed_date else None,
                    'status': response.status,
                })

                # Find reply to the response
                reply = response.responses.filter(litigation_role='reply').first()
                if reply:
                    thread['chain'].append({
                        'id': str(reply.id),
                        'title': reply.title,
                        'litigation_role': 'reply',
                        'litigation_role_display': reply.get_litigation_role_display(),
                        'filing_party': reply.filing_party,
                        'filing_party_display': reply.get_filing_party_display(),
                        'filed_date': str(reply.filed_date) if reply.filed_date else None,
                        'status': reply.status,
                    })

            # Find any court orders related to this motion
            orders = motion.responses.filter(litigation_role='order')
            for order in orders:
                thread['chain'].append({
                    'id': str(order.id),
                    'title': order.title,
                    'litigation_role': 'order',
                    'litigation_role_display': order.get_litigation_role_display(),
                    'filing_party': 'court',
                    'filing_party_display': 'Court',
                    'filed_date': str(order.filed_date) if order.filed_date else None,
                    'status': order.status,
                })

            thread['document_count'] = len(thread['chain'])
            thread['needs_response'] = (
                len(thread['chain']) == 1 and
                motion.filing_party == 'respondent'
            )
            thread['needs_reply'] = (
                len(thread['chain']) == 2 and
                response and response.filing_party == 'respondent' and
                motion.filing_party == 'petitioner'
            )

            threads.append(thread)

        return Response({
            'success': True,
            'threads': threads,
            'count': len(threads),
        })

    except Exception as e:
        logger.error(f"[Session 410] Error getting document threads: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_thread(request, document_id):
    """
    Session 410: Get the document thread for a specific document.
    Returns the full Motion → Response → Reply chain this document belongs to.
    """
    user = request.user

    try:
        from core.models_legal import LitigationDocument

        doc = LitigationDocument.objects.filter(
            id=document_id,
            case_profile__user=user,
        ).first()
        if not doc:
            return Response({
                'success': False,
                'error': 'Document not found'
            }, status=404)

        # Use model method to get thread
        thread_data = doc.get_document_thread()
        chain = doc.get_thread_chain()

        result_chain = []
        for item in chain:
            result_chain.append({
                'id': str(item.id),
                'title': item.title,
                'litigation_role': item.litigation_role,
                'litigation_role_display': item.get_litigation_role_display(),
                'filing_party': item.filing_party,
                'filing_party_display': item.get_filing_party_display(),
                'filed_date': str(item.filed_date) if item.filed_date else None,
                'document_date': str(item.document_date) if item.document_date else None,
                'status': item.status,
                'word_count': len(item.extracted_text.split()) if item.extracted_text else 0,
            })

        return Response({
            'success': True,
            'document_id': str(doc.id),
            'thread': {
                'chain': result_chain,
                'motion_id': str(thread_data['motion'].id) if thread_data['motion'] else None,
                'response_id': str(thread_data['response'].id) if thread_data['response'] else None,
                'reply_id': str(thread_data['reply'].id) if thread_data['reply'] else None,
            }
        })

    except Exception as e:
        logger.error(f"[Session 410] Error getting document thread: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_documents_needing_response(request, case_profile_id):
    """
    Session 410: Get documents from opposing party that need a response.
    Returns motions/filings from respondent that user hasn't responded to yet.
    """
    user = request.user

    try:
        from core.models_legal import CaseProfile, LitigationDocument

        # Verify user owns this case
        try:
            case_profile = CaseProfile.objects.get(id=case_profile_id, user=user)
        except CaseProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Case profile not found'
            }, status=404)

        # Get motions from respondent that don't have a response from petitioner
        respondent_motions = LitigationDocument.objects.filter(
            case_profile=case_profile,
            filing_party='respondent',
            litigation_role='motion',
        )

        needs_response = []
        for motion in respondent_motions:
            # Check if petitioner has responded
            has_response = motion.responses.filter(
                filing_party='petitioner',
                litigation_role='response'
            ).exists()

            if not has_response:
                needs_response.append({
                    'id': str(motion.id),
                    'title': motion.title,
                    'document_type': motion.document_type,
                    'document_type_display': motion.get_document_type_display(),
                    'filed_date': str(motion.filed_date) if motion.filed_date else None,
                    'deadline_date': str(motion.deadline_date) if motion.deadline_date else None,
                    'word_count': len(motion.extracted_text.split()) if motion.extracted_text else 0,
                    'status': motion.status,
                })

        # Also get responses from respondent that need a reply
        respondent_responses = LitigationDocument.objects.filter(
            case_profile=case_profile,
            filing_party='respondent',
            litigation_role='response',
        )

        needs_reply = []
        for response in respondent_responses:
            # Check if petitioner has replied
            has_reply = response.responses.filter(
                filing_party='petitioner',
                litigation_role='reply'
            ).exists()

            # Only suggest reply if the original motion was from petitioner
            if not has_reply and response.responds_to and response.responds_to.filing_party == 'petitioner':
                needs_reply.append({
                    'id': str(response.id),
                    'title': response.title,
                    'responds_to_title': response.responds_to.title if response.responds_to else None,
                    'filed_date': str(response.filed_date) if response.filed_date else None,
                    'deadline_date': str(response.deadline_date) if response.deadline_date else None,
                    'word_count': len(response.extracted_text.split()) if response.extracted_text else 0,
                    'status': response.status,
                })

        return Response({
            'success': True,
            'needs_response': needs_response,
            'needs_reply': needs_reply,
            'total_action_items': len(needs_response) + len(needs_reply),
        })

    except Exception as e:
        logger.error(f"[Session 410] Error getting documents needing response: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_types(request):
    """
    Get all available document types and categories.
    Session 410: Added litigation_roles for thread tracking.
    """
    from core.models_legal import LitigationDocument

    return Response({
        'success': True,
        'categories': dict(LitigationDocument.CATEGORY_CHOICES),
        'document_types': {
            'court_order': dict(LitigationDocument.COURT_ORDER_TYPES),
            'motion': dict(LitigationDocument.MOTION_TYPES),
            'response': dict(LitigationDocument.RESPONSE_TYPES),
            'evidence': dict(LitigationDocument.EVIDENCE_TYPES),
            'court_rule': dict(LitigationDocument.COURT_RULE_TYPES),
        },
        'filing_parties': dict(LitigationDocument.FILING_PARTY_CHOICES),
        # Session 410: Add litigation roles for Motion → Response → Reply chain
        'litigation_roles': dict(LitigationDocument.LITIGATION_ROLE_CHOICES),
    })


# =============================================================================
# S2803 Phase 3.0 — Legal Document Drafting Dispatch + Live Status
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def draft_legal_document(request):
    """Dispatch a legal-document drafting task with disclaimer enforcement.

    Body: {task_description: str, disclaimer_acknowledged: bool}
    Returns: {task_id, dispatch_log_id} on success; 400 on missing disclaimer.
    """
    from core.services.fleet_pa_chat_audit import _client_ip_from_request
    from core.services.legal_dispatch import DisclaimerRequired, dispatch_legal_draft

    task_description = (request.data.get('task_description') or '').strip()
    disclaimer_acknowledged = bool(request.data.get('disclaimer_acknowledged'))

    if not task_description:
        return Response(
            {'success': False, 'error': 'task_description is required'},
            status=400,
        )

    try:
        result = dispatch_legal_draft(
            user=request.user,
            task_description=task_description,
            disclaimer_acknowledged=disclaimer_acknowledged,
            ip_address=_client_ip_from_request(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            client_session_pin='',  # UI dispatches have no PA pin
            context={},
        )
    except DisclaimerRequired as exc:
        return Response(
            {'success': False, 'error': str(exc), 'error_code': 'disclaimer_required'},
            status=400,
        )

    if result.get('success') is False:
        return Response(result, status=503)

    return Response({'success': True, **result})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def draft_legal_document_status(request, task_id):
    """Poll dispatch + Celery status for a legal drafting task.

    Scoped to the requesting user — a task_id belonging to another user
    returns 404 (no leaked existence check).
    """
    from core.models_legal_audit import LegalDocumentDispatchLog

    dispatch_log = LegalDocumentDispatchLog.objects.filter(
        task_id=task_id,
        user=request.user,
    ).first()
    if not dispatch_log:
        return Response(
            {'success': False, 'error': 'Task not found'},
            status=404,
        )

    # DB status is the source of truth for terminal states (updated by the
    # drafting task on completion/failure). Derive live-Celery state for the
    # in-flight case (dispatched → pending/started).
    payload = {
        'success': True,
        'task_id': task_id,
        'status': dispatch_log.status,
        'dispatched_at': dispatch_log.dispatched_at.isoformat(),
        'completed_at': (
            dispatch_log.completed_at.isoformat() if dispatch_log.completed_at else None
        ),
        'error_message': dispatch_log.error_message or None,
        'document_id': (
            str(dispatch_log.resulting_document_id)
            if dispatch_log.resulting_document_id else None
        ),
    }

    if dispatch_log.status == 'dispatched':
        # Task hasn't reached postrun yet — check Celery for finer-grained state.
        try:
            from core.celery import app as celery_app
            result = celery_app.AsyncResult(task_id)
            payload['celery_state'] = result.state  # PENDING / STARTED / etc.
        except Exception as exc:
            logger.debug(f"[LEGAL_DRAFT_STATUS] Celery state read failed: {exc}")
            payload['celery_state'] = 'unknown'

    return Response(payload)


# =============================================================================
# S2808 Phase 4a — Form-selection intelligence
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_legal_form(request):
    """Recommend a Colorado JDF form for a plain-English situation description.

    Body: {situation: str, case_type?: str}
    Returns the LegalDocDrafterAgent._recommend_form envelope:
        {success, situation, top_match, alternates, confidence,
         clarifying_questions, disclaimer}
    """
    from core.agents.legal.legal_doc_drafter_agent import LegalDocDrafterAgent

    situation = (request.data.get('situation') or '').strip()
    if not situation:
        return Response(
            {'success': False, 'error': 'situation is required'},
            status=400,
        )

    case_type = (request.data.get('case_type') or '').strip() or None

    # Build a lightweight agent instance. `_recommend_form` is a pure
    # rule-based method — no LLM, no DB writes, no case binding needed.
    agent = LegalDocDrafterAgent.__new__(LegalDocDrafterAgent)
    agent.user = request.user
    agent.name = 'LegalDocDrafterAgent'
    agent.agent_name = 'LegalDocDrafterAgent'

    result = agent._recommend_form(
        situation=situation,
        context={'case_type': case_type} if case_type else None,
    )
    if result.get('success') is False:
        return Response(result, status=400)
    return Response(result)
