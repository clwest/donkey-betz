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
                    'is_attorney': True
                }
        if respondent:
            return {
                'name': respondent.full_name,
                'first_name': respondent.first_name,
                'email': respondent.email,
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
