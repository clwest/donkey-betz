"""
Legal Case Management API Views

Session 406: Case Intake Form for Legal Assistant
REST API endpoints for managing case profiles, parties, attorneys, and documents.
"""

import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json

from .models_legal import CaseProfile, Party, Attorney, Child, CaseDocument

logger = logging.getLogger(__name__)


def get_current_user(request):
    """Get the current user, handling both authenticated and anonymous users."""
    if request.user.is_authenticated:
        return request.user
    return None


# =============================================================================
# Case Profile Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def case_profiles_list(request):
    """
    GET: List all case profiles for the current user
    POST: Create a new case profile
    """
    user = get_current_user(request)

    if request.method == "GET":
        if not user:
            # Return empty list for anonymous users
            return JsonResponse({'success': True, 'cases': [], 'count': 0})

        cases = CaseProfile.objects.filter(user=user).order_by('-updated_at')
        case_list = []
        for case in cases:
            petitioner = case.petitioner
            respondent = case.respondent
            case_list.append({
                'id': str(case.id),
                'case_number': case.case_number,
                'case_type': case.case_type,
                'case_type_display': case.get_case_type_display(),
                'case_title': case.case_title,
                'county': case.county,
                'state': case.state,
                'status': case.status,
                'status_display': case.get_status_display(),
                'petitioner_name': petitioner.full_name if petitioner else '',
                'respondent_name': respondent.full_name if respondent else '',
                'children_count': case.children.count(),
                'documents_count': case.documents.count(),
                'created_at': case.created_at.isoformat(),
                'updated_at': case.updated_at.isoformat(),
            })

        return JsonResponse({'success': True, 'cases': case_list, 'count': len(case_list)})

    elif request.method == "POST":
        if not user:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Create the case profile
        case = CaseProfile.objects.create(
            user=user,
            case_number=data.get('case_number', ''),
            case_type=data.get('case_type', 'custody'),
            case_title=data.get('case_title', ''),
            county=data.get('county', ''),
            state=data.get('state', 'Colorado'),
            district=data.get('district', ''),
            division=data.get('division', ''),
            courtroom=data.get('courtroom', ''),
            court_address=data.get('court_address', ''),
            filing_date=data.get('filing_date') or None,
            status=data.get('status', 'active'),
            notes=data.get('notes', ''),
        )

        # Create petitioner if provided
        petitioner_data = data.get('petitioner')
        if petitioner_data:
            Party.objects.create(
                case_profile=case,
                party_type='petitioner',
                full_name=petitioner_data.get('full_name', ''),
                address=petitioner_data.get('address', ''),
                city=petitioner_data.get('city', ''),
                state=petitioner_data.get('state', ''),
                zip_code=petitioner_data.get('zip_code', ''),
                phone=petitioner_data.get('phone', ''),
                email=petitioner_data.get('email', ''),
                is_pro_se=petitioner_data.get('is_pro_se', True),
            )

            # Create petitioner's attorney if not pro se
            petitioner_attorney = petitioner_data.get('attorney')
            if petitioner_attorney and not petitioner_data.get('is_pro_se', True):
                petitioner_party = case.petitioner
                if petitioner_party:
                    Attorney.objects.create(
                        party=petitioner_party,
                        full_name=petitioner_attorney.get('full_name', ''),
                        firm_name=petitioner_attorney.get('firm_name', ''),
                        address=petitioner_attorney.get('address', ''),
                        city=petitioner_attorney.get('city', ''),
                        state=petitioner_attorney.get('state', ''),
                        zip_code=petitioner_attorney.get('zip_code', ''),
                        phone=petitioner_attorney.get('phone', ''),
                        email=petitioner_attorney.get('email', ''),
                        bar_number=petitioner_attorney.get('bar_number', ''),
                    )

        # Create respondent if provided
        respondent_data = data.get('respondent')
        if respondent_data:
            respondent_party = Party.objects.create(
                case_profile=case,
                party_type='respondent',
                full_name=respondent_data.get('full_name', ''),
                address=respondent_data.get('address', ''),
                city=respondent_data.get('city', ''),
                state=respondent_data.get('state', ''),
                zip_code=respondent_data.get('zip_code', ''),
                phone=respondent_data.get('phone', ''),
                email=respondent_data.get('email', ''),
                is_pro_se=respondent_data.get('is_pro_se', True),
            )

            # Create respondent's attorney if not pro se
            respondent_attorney = respondent_data.get('attorney')
            if respondent_attorney and not respondent_data.get('is_pro_se', True):
                Attorney.objects.create(
                    party=respondent_party,
                    full_name=respondent_attorney.get('full_name', ''),
                    firm_name=respondent_attorney.get('firm_name', ''),
                    address=respondent_attorney.get('address', ''),
                    city=respondent_attorney.get('city', ''),
                    state=respondent_attorney.get('state', ''),
                    zip_code=respondent_attorney.get('zip_code', ''),
                    phone=respondent_attorney.get('phone', ''),
                    email=respondent_attorney.get('email', ''),
                    bar_number=respondent_attorney.get('bar_number', ''),
                )

        # Create children if provided
        children_data = data.get('children', [])
        for child_data in children_data:
            Child.objects.create(
                case_profile=case,
                full_name=child_data.get('full_name', ''),
                date_of_birth=child_data.get('date_of_birth') or None,
            )

        logger.info(f"Created case profile {case.case_number} for user {user.username}")

        return JsonResponse({
            'success': True,
            'case_id': str(case.id),
            'case_number': case.case_number,
            'message': f'Case {case.case_number} created successfully'
        }, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def case_profile_detail(request, case_id):
    """
    GET: Get full details of a case profile
    PUT: Update a case profile
    DELETE: Delete a case profile
    """
    user = get_current_user(request)

    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    case = get_object_or_404(CaseProfile, id=case_id, user=user)

    if request.method == "GET":
        petitioner = case.petitioner
        respondent = case.respondent

        # Build petitioner data
        petitioner_data = None
        if petitioner:
            petitioner_attorney = petitioner.attorney
            petitioner_data = {
                'id': str(petitioner.id),
                'full_name': petitioner.full_name,
                'first_name': petitioner.first_name,
                'address': petitioner.address,
                'city': petitioner.city,
                'state': petitioner.state,
                'zip_code': petitioner.zip_code,
                'phone': petitioner.phone,
                'email': petitioner.email,
                'is_pro_se': petitioner.is_pro_se,
                'attorney': {
                    'id': str(petitioner_attorney.id),
                    'full_name': petitioner_attorney.full_name,
                    'first_name': petitioner_attorney.first_name,
                    'firm_name': petitioner_attorney.firm_name,
                    'address': petitioner_attorney.address,
                    'city': petitioner_attorney.city,
                    'state': petitioner_attorney.state,
                    'zip_code': petitioner_attorney.zip_code,
                    'phone': petitioner_attorney.phone,
                    'email': petitioner_attorney.email,
                    'bar_number': petitioner_attorney.bar_number,
                } if petitioner_attorney else None
            }

        # Build respondent data
        respondent_data = None
        if respondent:
            respondent_attorney = respondent.attorney
            respondent_data = {
                'id': str(respondent.id),
                'full_name': respondent.full_name,
                'first_name': respondent.first_name,
                'address': respondent.address,
                'city': respondent.city,
                'state': respondent.state,
                'zip_code': respondent.zip_code,
                'phone': respondent.phone,
                'email': respondent.email,
                'is_pro_se': respondent.is_pro_se,
                'attorney': {
                    'id': str(respondent_attorney.id),
                    'full_name': respondent_attorney.full_name,
                    'first_name': respondent_attorney.first_name,
                    'firm_name': respondent_attorney.firm_name,
                    'address': respondent_attorney.address,
                    'city': respondent_attorney.city,
                    'state': respondent_attorney.state,
                    'zip_code': respondent_attorney.zip_code,
                    'phone': respondent_attorney.phone,
                    'email': respondent_attorney.email,
                    'bar_number': respondent_attorney.bar_number,
                } if respondent_attorney else None
            }

        # Build children data
        children_data = []
        for child in case.children.all():
            children_data.append({
                'id': str(child.id),
                'full_name': child.full_name,
                'first_name': child.first_name,
                'date_of_birth': child.date_of_birth.isoformat() if child.date_of_birth else None,
                'age': child.age,
            })

        # Build documents data
        documents_data = []
        for doc in case.documents.all():
            documents_data.append({
                'id': str(doc.id),
                'document_type': doc.document_type,
                'document_type_display': doc.get_document_type_display(),
                'title': doc.title,
                'entered_date': doc.entered_date.isoformat() if doc.entered_date else None,
                'file_url': doc.file.url if doc.file else None,
                'uploaded_at': doc.uploaded_at.isoformat(),
            })

        return JsonResponse({
            'id': str(case.id),
            'case_number': case.case_number,
            'case_type': case.case_type,
            'case_type_display': case.get_case_type_display(),
            'case_title': case.case_title,
            'county': case.county,
            'state': case.state,
            'district': case.district,
            'division': case.division,
            'courtroom': case.courtroom,
            'court_address': case.court_address,
            'filing_date': case.filing_date.isoformat() if case.filing_date else None,
            'status': case.status,
            'status_display': case.get_status_display(),
            'notes': case.notes,
            'petitioner': petitioner_data,
            'respondent': respondent_data,
            'children': children_data,
            'documents': documents_data,
            'created_at': case.created_at.isoformat(),
            'updated_at': case.updated_at.isoformat(),
        })

    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Update case fields
        for field in ['case_number', 'case_type', 'case_title', 'county', 'state',
                      'district', 'division', 'courtroom', 'court_address', 'status', 'notes']:
            if field in data:
                setattr(case, field, data[field])

        if 'filing_date' in data:
            case.filing_date = data['filing_date'] or None

        case.save()

        # Update petitioner if provided
        petitioner_data = data.get('petitioner')
        if petitioner_data:
            petitioner = case.petitioner
            if petitioner:
                for field in ['full_name', 'address', 'city', 'state', 'zip_code', 'phone', 'email', 'is_pro_se']:
                    if field in petitioner_data:
                        setattr(petitioner, field, petitioner_data[field])
                petitioner.save()

                # Update attorney
                attorney_data = petitioner_data.get('attorney')
                if attorney_data and not petitioner.is_pro_se:
                    attorney = petitioner.attorney
                    if attorney:
                        for field in ['full_name', 'firm_name', 'address', 'city', 'state', 'zip_code', 'phone', 'email', 'bar_number']:
                            if field in attorney_data:
                                setattr(attorney, field, attorney_data[field])
                        attorney.save()
                    else:
                        # Create attorney
                        Attorney.objects.create(party=petitioner, **attorney_data)

        # Update respondent if provided
        respondent_data = data.get('respondent')
        if respondent_data:
            respondent = case.respondent
            if respondent:
                for field in ['full_name', 'address', 'city', 'state', 'zip_code', 'phone', 'email', 'is_pro_se']:
                    if field in respondent_data:
                        setattr(respondent, field, respondent_data[field])
                respondent.save()

                # Update attorney
                attorney_data = respondent_data.get('attorney')
                if attorney_data and not respondent.is_pro_se:
                    attorney = respondent.attorney
                    if attorney:
                        for field in ['full_name', 'firm_name', 'address', 'city', 'state', 'zip_code', 'phone', 'email', 'bar_number']:
                            if field in attorney_data:
                                setattr(attorney, field, attorney_data[field])
                        attorney.save()
                    else:
                        # Create attorney
                        Attorney.objects.create(party=respondent, **attorney_data)

        logger.info(f"Updated case profile {case.case_number}")

        return JsonResponse({
            'success': True,
            'case_id': str(case.id),
            'case_number': case.case_number,
            'message': f'Case {case.case_number} updated successfully'
        })

    elif request.method == "DELETE":
        case_number = case.case_number
        case.delete()

        logger.info(f"Deleted case profile {case_number}")

        return JsonResponse({
            'success': True,
            'message': f'Case {case_number} deleted successfully'
        })


# =============================================================================
# Child Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def add_child(request, case_id):
    """Add a child to a case profile."""
    user = get_current_user(request)

    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    case = get_object_or_404(CaseProfile, id=case_id, user=user)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    child = Child.objects.create(
        case_profile=case,
        full_name=data.get('full_name', ''),
        date_of_birth=data.get('date_of_birth') or None,
    )

    return JsonResponse({
        'success': True,
        'child_id': str(child.id),
        'message': f'Child {child.full_name} added to case'
    }, status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_child(request, case_id, child_id):
    """Delete a child from a case profile."""
    user = get_current_user(request)

    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    case = get_object_or_404(CaseProfile, id=case_id, user=user)
    child = get_object_or_404(Child, id=child_id, case_profile=case)

    child_name = child.full_name
    child.delete()

    return JsonResponse({
        'success': True,
        'message': f'Child {child_name} removed from case'
    })


# =============================================================================
# Document Endpoints
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def add_document(request, case_id):
    """Add a document to a case profile."""
    user = get_current_user(request)

    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    case = get_object_or_404(CaseProfile, id=case_id, user=user)

    # Handle form data (file upload)
    document_type = request.POST.get('document_type', 'other')
    title = request.POST.get('title', '')
    entered_date = request.POST.get('entered_date') or None
    notes = request.POST.get('notes', '')
    file = request.FILES.get('file')

    doc = CaseDocument.objects.create(
        case_profile=case,
        document_type=document_type,
        title=title,
        entered_date=entered_date,
        notes=notes,
        file=file,
    )

    return JsonResponse({
        'success': True,
        'document_id': str(doc.id),
        'message': f'Document "{doc.title}" added to case'
    }, status=201)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_document(request, case_id, document_id):
    """Delete a document from a case profile."""
    user = get_current_user(request)

    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    case = get_object_or_404(CaseProfile, id=case_id, user=user)
    doc = get_object_or_404(CaseDocument, id=document_id, case_profile=case)

    doc_title = doc.title
    doc.delete()

    return JsonResponse({
        'success': True,
        'message': f'Document "{doc_title}" removed from case'
    })


# =============================================================================
# Helper Endpoint - Get Case Context for Motion Analysis
# =============================================================================

@csrf_exempt
@require_http_methods(["GET"])
def get_case_context(request, case_id):
    """
    Get case context formatted for motion analysis pipeline.
    This is what the Legal Assistant uses to populate conferral emails, etc.
    """
    user = get_current_user(request)

    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    case = get_object_or_404(CaseProfile, id=case_id, user=user)

    petitioner = case.petitioner
    respondent = case.respondent

    # Build context dict that matches what _extract_case_metadata returns
    context = {
        'case_number': case.case_number,
        'county': case.county,
        'state': case.state,
        'division': case.division,
        'courtroom': case.courtroom,
        'court_address': case.court_address,
        'petitioner_name': petitioner.full_name if petitioner else '',
        'petitioner_first_name': petitioner.first_name if petitioner else '',
        'petitioner_address': petitioner.get_full_address() if petitioner else '',
        'petitioner_email': petitioner.email if petitioner else '',
        'petitioner_is_pro_se': petitioner.is_pro_se if petitioner else True,
        'respondent_name': respondent.full_name if respondent else '',
        'respondent_first_name': respondent.first_name if respondent else '',
        'respondent_address': respondent.get_full_address() if respondent else '',
        'respondent_email': respondent.email if respondent else '',
        'respondent_is_pro_se': respondent.is_pro_se if respondent else True,
    }

    # Add respondent's counsel info if represented
    if respondent and not respondent.is_pro_se:
        attorney = respondent.attorney
        if attorney:
            context['respondent_counsel'] = attorney.full_name
            context['respondent_counsel_first_name'] = attorney.first_name
            context['respondent_counsel_email'] = attorney.email
            context['respondent_counsel_firm'] = attorney.firm_name
            context['respondent_counsel_address'] = attorney.get_full_address()

    # Add petitioner's counsel info if represented
    if petitioner and not petitioner.is_pro_se:
        attorney = petitioner.attorney
        if attorney:
            context['petitioner_counsel'] = attorney.full_name
            context['petitioner_counsel_email'] = attorney.email

    # Add children info
    children = []
    for child in case.children.all():
        children.append({
            'name': child.full_name,
            'first_name': child.first_name,
            'age': child.age,
        })
    context['children'] = children

    # Get conferral recipient (who to send conferral email to)
    conferral_recipient = case.get_conferral_recipient()
    if conferral_recipient:
        context['conferral_recipient_name'] = conferral_recipient['name']
        context['conferral_recipient_first_name'] = conferral_recipient['first_name']
        context['conferral_recipient_email'] = conferral_recipient['email']
        context['conferral_recipient_is_attorney'] = conferral_recipient['is_attorney']

    return JsonResponse(context)


# =============================================================================
# Active Case Selection
# =============================================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def active_case(request):
    """
    GET: Get the user's currently selected active case
    POST: Set the active case for the user
    """
    user = get_current_user(request)

    if not user:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    if request.method == "GET":
        # Get active case from user preferences or session
        active_case_id = request.session.get('active_case_id')
        if active_case_id:
            try:
                case = CaseProfile.objects.get(id=active_case_id, user=user)
                return JsonResponse({
                    'has_active_case': True,
                    'case_id': str(case.id),
                    'case_number': case.case_number,
                    'case_type': case.case_type,
                })
            except CaseProfile.DoesNotExist:
                pass

        return JsonResponse({'has_active_case': False})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        case_id = data.get('case_id')
        if case_id:
            case = get_object_or_404(CaseProfile, id=case_id, user=user)
            request.session['active_case_id'] = str(case.id)

            return JsonResponse({
                'success': True,
                'case_id': str(case.id),
                'case_number': case.case_number,
                'message': f'Active case set to {case.case_number}'
            })
        else:
            # Clear active case
            request.session.pop('active_case_id', None)
            return JsonResponse({
                'success': True,
                'message': 'Active case cleared'
            })
