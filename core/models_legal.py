"""
Legal Case Management Models

Session 406: Case Intake Form for Legal Assistant
These models store case profiles so the Legal Assistant has full context
before analyzing any motions.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class CaseProfile(models.Model):
    """
    Main case record linking all parties, attorneys, and documents.
    Users fill this out ONCE when setting up their case.
    """
    CASE_TYPE_CHOICES = [
        ('divorce', 'Divorce'),
        ('custody', 'Child Custody'),
        ('modification', 'Modification'),
        ('enforcement', 'Enforcement'),
        ('paternity', 'Paternity'),
        ('protection_order', 'Protection Order'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('pending', 'Pending'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='case_profiles'
    )

    # Case identification
    case_number = models.CharField(max_length=50, help_text="Court case number (e.g., 2025DR576)")
    case_type = models.CharField(max_length=30, choices=CASE_TYPE_CHOICES, default='custody')
    case_title = models.CharField(max_length=200, blank=True, help_text="Optional case title")

    # Court information
    county = models.CharField(max_length=100)
    state = models.CharField(max_length=50, default='Colorado')
    district = models.CharField(max_length=50, blank=True, help_text="Judicial district")
    division = models.CharField(max_length=10, blank=True)
    courtroom = models.CharField(max_length=10, blank=True)
    court_address = models.TextField(blank=True)

    # Case dates
    filing_date = models.DateField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Notes
    notes = models.TextField(blank=True, help_text="Any additional case notes")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Case Profile'
        verbose_name_plural = 'Case Profiles'

    def __str__(self):
        return f"{self.case_number} - {self.get_case_type_display()}"

    @property
    def document_count(self):
        """S2805 Phase 3.1 P1: live count of linked LegalDocument rows.

        No denormalization — matches the read-side pattern. Replaces
        the LegalCase.document_count integer field that the legal
        drafter agent used to maintain by hand.
        """
        return self.legal_documents.count()

    @property
    def research_result_count(self):
        """S2807 Phase 3.1 P1.b: live count of linked LegalResearchResult rows.

        No denormalization — matches the read-side pattern. Replaces
        the LegalCase.research_count integer field that the legal
        drafter agent used to maintain by hand.
        """
        return self.legal_research_results.count()

    @property
    def petitioner(self):
        """Get the petitioner party for this case."""
        return self.parties.filter(party_type='petitioner').first()

    @property
    def respondent(self):
        """Get the respondent party for this case."""
        return self.parties.filter(party_type='respondent').first()

    def get_conferral_recipient(self):
        """
        Get the appropriate recipient for conferral emails.
        Returns opposing counsel if represented, otherwise the respondent.
        """
        respondent = self.respondent
        if respondent and not respondent.is_pro_se:
            attorney = respondent.attorneys.first()
            if attorney:
                return {
                    'name': attorney.full_name,
                    'first_name': attorney.first_name,
                    'email': attorney.email,
                    'address': attorney.get_full_address(),
                    'firm': attorney.firm_name,
                    'is_attorney': True
                }
        if respondent:
            return {
                'name': respondent.full_name,
                'first_name': respondent.first_name,
                'email': respondent.email,
                'address': respondent.get_full_address(),
                'is_attorney': False
            }
        return None


class Party(models.Model):
    """
    Represents a party to the case (Petitioner or Respondent).
    """
    PARTY_TYPE_CHOICES = [
        ('petitioner', 'Petitioner'),
        ('respondent', 'Respondent'),
        ('intervenor', 'Intervenor'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.ForeignKey(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='parties'
    )

    party_type = models.CharField(max_length=20, choices=PARTY_TYPE_CHOICES)

    # Name
    full_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # Contact information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    # Representation status
    is_pro_se = models.BooleanField(default=True, help_text="True if self-represented")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['party_type', 'full_name']
        verbose_name = 'Party'
        verbose_name_plural = 'Parties'

    def __str__(self):
        return f"{self.full_name} ({self.get_party_type_display()})"

    def save(self, *args, **kwargs):
        # Auto-extract first name if not provided
        if self.full_name and not self.first_name:
            parts = self.full_name.split()
            if parts:
                self.first_name = parts[0]
        super().save(*args, **kwargs)

    @property
    def attorney(self):
        """Get the primary attorney for this party."""
        return self.attorneys.first()

    def get_full_address(self):
        """Return formatted full address."""
        parts = [self.address]
        if self.city or self.state or self.zip_code:
            city_state_zip = ', '.join(filter(None, [self.city, self.state]))
            if self.zip_code:
                city_state_zip += f' {self.zip_code}'
            parts.append(city_state_zip)
        return '\n'.join(filter(None, parts))


class Attorney(models.Model):
    """
    Represents legal counsel for a party.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        related_name='attorneys'
    )

    # Name
    full_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)

    # Firm information
    firm_name = models.CharField(max_length=200, blank=True)

    # Contact information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    # Bar information
    bar_number = models.CharField(max_length=50, blank=True, help_text="Attorney registration number")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Attorney'
        verbose_name_plural = 'Attorneys'

    def __str__(self):
        if self.firm_name:
            return f"{self.full_name} ({self.firm_name})"
        return self.full_name

    def save(self, *args, **kwargs):
        # Auto-extract first name if not provided
        if self.full_name and not self.first_name:
            parts = self.full_name.split()
            if parts:
                self.first_name = parts[0]
        super().save(*args, **kwargs)

    def get_full_address(self):
        """Return formatted full address."""
        parts = []
        if self.firm_name:
            parts.append(self.firm_name)
        if self.address:
            parts.append(self.address)
        if self.city or self.state or self.zip_code:
            city_state_zip = ', '.join(filter(None, [self.city, self.state]))
            if self.zip_code:
                city_state_zip += f' {self.zip_code}'
            parts.append(city_state_zip)
        return '\n'.join(parts)


class Child(models.Model):
    """
    For family law cases involving minor children.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.ForeignKey(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='children'
    )

    # Name
    full_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100, blank=True)

    # Date of birth
    date_of_birth = models.DateField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_of_birth']
        verbose_name = 'Child'
        verbose_name_plural = 'Children'

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        # Auto-extract first name if not provided
        if self.full_name and not self.first_name:
            parts = self.full_name.split()
            if parts:
                self.first_name = parts[0]
        super().save(*args, **kwargs)

    @property
    def age(self):
        """Calculate current age."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class CaseDocument(models.Model):
    """
    Court orders and other documents associated with a case.
    """
    DOCUMENT_TYPE_CHOICES = [
        ('temporary_orders', 'Temporary Orders'),
        ('permanent_orders', 'Permanent Orders'),
        ('separation_agreement', 'Separation Agreement'),
        ('parenting_plan', 'Parenting Plan'),
        ('support_order', 'Support Order'),
        ('protection_order', 'Protection Order'),
        ('motion', 'Motion'),
        ('response', 'Response'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.ForeignKey(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=300)

    # File
    file = models.FileField(upload_to='legal_documents/', null=True, blank=True)

    # Dates
    entered_date = models.DateField(null=True, blank=True, help_text="Date order was entered by court")

    # Extracted content
    extracted_text = models.TextField(blank=True, help_text="OCR/extracted text from document")

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-entered_date', '-uploaded_at']
        verbose_name = 'Case Document'
        verbose_name_plural = 'Case Documents'

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"


# =============================================================================
# Session 408: Multi-Document Litigation Management System
# =============================================================================

class LitigationDocument(models.Model):
    """
    Session 408: Enhanced document model for litigation management.
    Organizes documents into categories matching the Legal Document Brain.

    Categories:
    1. Court Orders (temporary, prior parenting, status quo, restrictions, emergency)
    2. Motions (filed by user, filed by opposing party, pending)
    3. Responses/Replies (responses, exhibits, affidavits)
    4. Evidence (messages, call logs, calendars, photos, transcripts, notes)
    5. Court Rules (CRCP, JDF forms, local standards, division requirements)
    """

    # Category 1: Court Orders
    COURT_ORDER_TYPES = [
        ('temporary_orders', 'Temporary Orders'),
        ('prior_parenting', 'Prior Parenting Orders'),
        ('status_quo', 'Status Quo Orders'),
        ('restriction', 'Restrictions'),
        ('emergency_ruling', 'Emergency Ruling'),
        ('permanent_orders', 'Permanent Orders'),
        ('separation_agreement', 'Separation Agreement'),
        ('parenting_plan', 'Parenting Plan'),
        ('support_order', 'Support Order'),
        ('protection_order', 'Protection Order'),
    ]

    # Category 2: Motions
    MOTION_TYPES = [
        ('my_motion', 'Motion I Filed'),
        ('opposing_motion', 'Motion Filed by Opposing Party'),
        ('pending_motion', 'Pending Motion'),
    ]

    # Category 3: Responses/Replies
    RESPONSE_TYPES = [
        ('response', 'Response to Motion'),
        ('reply', 'Reply'),
        ('exhibit_attachment', 'Exhibit Attachment'),
        ('affidavit', 'Affidavit'),
    ]

    # Category 4: Evidence
    EVIDENCE_TYPES = [
        ('messages', 'Messages/Texts'),
        ('call_logs', 'Call Logs'),
        ('calendar', 'Calendar/Schedule'),
        ('photos', 'Photos'),
        ('transcript', 'Transcript'),
        ('notes', 'Notes'),
        ('email_evidence', 'Email Evidence'),
        ('financial_record', 'Financial Record'),
        ('school_record', 'School Record'),
        ('medical_record', 'Medical Record'),
    ]

    # Category 5: Court Rules
    COURT_RULE_TYPES = [
        ('crcp', 'C.R.C.P. Rule'),
        ('jdf_form', 'JDF Form'),
        ('local_standard', 'Local Practice Standard'),
        ('division_requirement', 'Division-Specific Requirement'),
    ]

    CATEGORY_CHOICES = [
        ('court_order', 'Court Orders'),
        ('motion', 'Motions'),
        ('response', 'Responses/Replies'),
        ('evidence', 'Evidence'),
        ('court_rule', 'Court Rules'),
    ]

    # Combine all document types
    DOCUMENT_TYPE_CHOICES = (
        COURT_ORDER_TYPES + MOTION_TYPES + RESPONSE_TYPES +
        EVIDENCE_TYPES + COURT_RULE_TYPES
    )

    FILING_PARTY_CHOICES = [
        ('petitioner', 'Petitioner (Me)'),
        ('respondent', 'Respondent (Opposing Party)'),
        ('court', 'Court'),
        ('third_party', 'Third Party'),
    ]

    # Session 410: Litigation role - where does this fit in motion/response/reply chain
    LITIGATION_ROLE_CHOICES = [
        ('motion', 'Motion'),
        ('response', 'Response'),
        ('reply', 'Reply'),
        ('order', 'Court Order'),
        ('exhibit', 'Exhibit'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('analyzed', 'Analyzed'),
        ('linked', 'Linked to Case'),
        ('responded', 'Response Generated'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.ForeignKey(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='litigation_documents'
    )

    # Document classification
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    filing_party = models.CharField(
        max_length=20,
        choices=FILING_PARTY_CHOICES,
        default='petitioner'
    )
    # Session 410: Litigation role - where does this fit in motion/response/reply chain
    litigation_role = models.CharField(
        max_length=20,
        choices=LITIGATION_ROLE_CHOICES,
        default='other',
        help_text="Role in litigation chain: motion, response, reply, order"
    )

    # Document info
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    # File storage
    file = models.FileField(upload_to='litigation_documents/', null=True, blank=True)
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(default=0)

    # Extracted content
    extracted_text = models.TextField(blank=True)

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')

    # Key dates
    document_date = models.DateField(null=True, blank=True, help_text="Date on document")
    filed_date = models.DateField(null=True, blank=True, help_text="Date filed with court")
    deadline_date = models.DateField(null=True, blank=True, help_text="Response deadline")

    # Linkage fields - which motion this responds to
    responds_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responses'
    )

    # Extracted metadata (populated by LegalContextBuilder)
    extracted_metadata = models.JSONField(
        default=dict,
        help_text="Extracted: parties, dates, allegations, claims, relief requested"
    )

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-filed_date', '-document_date', '-uploaded_at']
        verbose_name = 'Litigation Document'
        verbose_name_plural = 'Litigation Documents'
        indexes = [
            models.Index(fields=['case_profile', 'category']),
            models.Index(fields=['case_profile', 'document_type']),
            models.Index(fields=['case_profile', 'filing_party']),
            models.Index(fields=['case_profile', 'litigation_role']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    def get_document_thread(self):
        """
        Session 410: Get the full document thread this filing belongs to.
        Returns: {'motion': doc, 'response': doc, 'reply': doc} chain
        """
        thread = {'motion': None, 'response': None, 'reply': None}

        # Find the root motion
        current = self
        while current.responds_to:
            current = current.responds_to

        # Build thread from root
        if current.litigation_role == 'motion':
            thread['motion'] = current
            # Find response
            response = current.responses.filter(litigation_role='response').first()
            if response:
                thread['response'] = response
                # Find reply
                reply = response.responses.filter(litigation_role='reply').first()
                if reply:
                    thread['reply'] = reply

        return thread

    def get_thread_chain(self):
        """
        Session 410: Get ordered list of documents in this thread.
        Returns list of docs in order: [motion, response, reply, ...]
        """
        chain = []
        thread = self.get_document_thread()

        if thread['motion']:
            chain.append(thread['motion'])
        if thread['response']:
            chain.append(thread['response'])
        if thread['reply']:
            chain.append(thread['reply'])

        return chain


class CaseKnowledgeGraph(models.Model):
    """
    Session 408: Knowledge graph for a case - the "case_context.json" equivalent.
    Stores extracted information from all documents to build case understanding.

    This is rebuilt/updated each time a new document is ingested.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.OneToOneField(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='knowledge_graph'
    )

    # Parties extracted from documents
    parties = models.JSONField(
        default=dict,
        help_text="All parties mentioned: {name: {role, mentions, documents}}"
    )

    # Timeline of events
    timeline = models.JSONField(
        default=list,
        help_text="Chronological events: [{date, event, source_document, category}]"
    )

    # All allegations across documents
    allegations = models.JSONField(
        default=dict,
        help_text="Allegations by party: {party: [{allegation, document, date, contradicts}]}"
    )

    # Legal issues identified
    legal_issues = models.JSONField(
        default=list,
        help_text="List of legal issues: [{issue, related_documents, status}]"
    )

    # Claims made
    claims = models.JSONField(
        default=dict,
        help_text="Claims by party: {party: [{claim, document, evidence}]}"
    )

    # Relief requested
    relief_requested = models.JSONField(
        default=dict,
        help_text="Relief by motion: {motion_id: [{relief_type, specifics}]}"
    )

    # Evidence referenced
    evidence_referenced = models.JSONField(
        default=dict,
        help_text="Evidence items: {evidence_id: {type, description, supports, contradicts}}"
    )

    # Contradictions found
    contradictions = models.JSONField(
        default=list,
        help_text="Cross-document contradictions: [{doc1, claim1, doc2, claim2, analysis}]"
    )

    # Procedural posture
    procedural_posture = models.JSONField(
        default=dict,
        help_text="Current procedural state: {pending_motions, deadlines, next_hearing}"
    )

    # Response deadlines
    deadlines = models.JSONField(
        default=list,
        help_text="Upcoming deadlines: [{date, motion, type, days_remaining}]"
    )

    # Court requirements (local rules, division specific)
    court_requirements = models.JSONField(
        default=dict,
        help_text="Court-specific requirements: {rule: requirement}"
    )

    # Unaddressed issues
    unaddressed_issues = models.JSONField(
        default=list,
        help_text="Issues not yet responded to: [{issue, source_document}]"
    )

    # Misinformation flags
    misinformation = models.JSONField(
        default=list,
        help_text="Potential misinformation: [{claim, document, contradicting_evidence}]"
    )

    # Summary statistics
    stats = models.JSONField(
        default=dict,
        help_text="Stats: {total_documents, pending_responses, contradictions_found}"
    )

    # Last rebuild timestamp
    last_rebuilt = models.DateTimeField(auto_now=True)
    rebuild_needed = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Case Knowledge Graph'
        verbose_name_plural = 'Case Knowledge Graphs'

    def __str__(self):
        return f"Knowledge Graph: {self.case_profile.case_number}"

    def to_json(self):
        """Export as case_context.json format."""
        return {
            'case_number': self.case_profile.case_number,
            'case_type': self.case_profile.case_type,
            'county': self.case_profile.county,
            'state': self.case_profile.state,
            'parties': self.parties,
            'timeline': self.timeline,
            'allegations': self.allegations,
            'legal_issues': self.legal_issues,
            'claims': self.claims,
            'relief_requested': self.relief_requested,
            'evidence_referenced': self.evidence_referenced,
            'contradictions': self.contradictions,
            'procedural_posture': self.procedural_posture,
            'deadlines': self.deadlines,
            'court_requirements': self.court_requirements,
            'unaddressed_issues': self.unaddressed_issues,
            'misinformation': self.misinformation,
            'stats': self.stats,
            'last_updated': self.last_rebuilt.isoformat() if self.last_rebuilt else None,
        }


class DocumentRelationship(models.Model):
    """
    Session 408: Links documents to each other to track motion/response chains.
    """

    RELATIONSHIP_TYPES = [
        ('responds_to', 'Responds To'),
        ('reply_to', 'Reply To'),
        ('exhibit_for', 'Exhibit For'),
        ('supersedes', 'Supersedes'),
        ('references', 'References'),
        ('contradicts', 'Contradicts'),
        ('supports', 'Supports'),
        ('amends', 'Amends'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    source_document = models.ForeignKey(
        LitigationDocument,
        on_delete=models.CASCADE,
        related_name='outgoing_relationships'
    )
    target_document = models.ForeignKey(
        LitigationDocument,
        on_delete=models.CASCADE,
        related_name='incoming_relationships'
    )

    relationship_type = models.CharField(max_length=30, choices=RELATIONSHIP_TYPES)

    # Additional context
    description = models.TextField(blank=True)
    confidence = models.FloatField(default=1.0, help_text="0-1 confidence score")
    auto_detected = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['source_document', 'target_document', 'relationship_type']
        verbose_name = 'Document Relationship'
        verbose_name_plural = 'Document Relationships'

    def __str__(self):
        return f"{self.source_document.title} {self.get_relationship_type_display()} {self.target_document.title}"


class GeneratedResponse(models.Model):
    """
    Session 408: Stores auto-generated responses to opposing filings.
    """

    RESPONSE_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('filed', 'Filed'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.ForeignKey(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='generated_responses'
    )

    # The document being responded to
    responds_to = models.ForeignKey(
        LitigationDocument,
        on_delete=models.CASCADE,
        related_name='auto_responses'
    )

    # Response components
    response_content = models.TextField(help_text="Main response (Admit/Deny/Insufficient)")
    factual_corrections = models.TextField(blank=True)
    legal_standard = models.TextField(blank=True)
    argument = models.TextField(blank=True)
    relief_requested = models.TextField(blank=True)

    # Full assembled document
    full_document = models.TextField(blank=True)

    # Proposed order
    proposed_order = models.TextField(blank=True)

    # Exhibits referenced
    exhibits = models.JSONField(default=list)

    # Status
    status = models.CharField(max_length=20, choices=RESPONSE_STATUS_CHOICES, default='draft')

    # Generation metadata
    generation_context = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Generated Response'
        verbose_name_plural = 'Generated Responses'

    def __str__(self):
        return f"Response to: {self.responds_to.title}"


class ExhibitList(models.Model):
    """
    Session 408: Auto-generated exhibit list for a case or filing.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.ForeignKey(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='exhibit_lists'
    )

    # Optional: linked to specific motion/response
    for_document = models.ForeignKey(
        LitigationDocument,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exhibit_lists'
    )

    title = models.CharField(max_length=300, default='Exhibit List')

    # Exhibits in order
    exhibits = models.JSONField(
        default=list,
        help_text="[{number, letter, title, document_id, description, page_count}]"
    )

    # Full formatted exhibit list
    formatted_content = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exhibit List'
        verbose_name_plural = 'Exhibit Lists'

    def __str__(self):
        return f"{self.title} - {self.case_profile.case_number}"


class CaseMemorandum(models.Model):
    """
    Session 408: High-level case summary for user and court.
    Auto-generated from knowledge graph.
    """

    MEMO_TYPE_CHOICES = [
        ('case_summary', 'Case Summary'),
        ('status_report', 'Status Report'),
        ('trial_brief', 'Trial Brief'),
        ('settlement_summary', 'Settlement Summary'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_profile = models.ForeignKey(
        CaseProfile,
        on_delete=models.CASCADE,
        related_name='memoranda'
    )

    memo_type = models.CharField(max_length=30, choices=MEMO_TYPE_CHOICES, default='case_summary')
    title = models.CharField(max_length=300)

    # Content sections
    executive_summary = models.TextField(blank=True)
    procedural_history = models.TextField(blank=True)
    factual_background = models.TextField(blank=True)
    issues_presented = models.TextField(blank=True)
    analysis = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)

    # Full document
    full_content = models.TextField(blank=True)

    # Source documents used
    source_documents = models.ManyToManyField(LitigationDocument, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Case Memorandum'
        verbose_name_plural = 'Case Memoranda'

    def __str__(self):
        return f"{self.title} - {self.case_profile.case_number}"
