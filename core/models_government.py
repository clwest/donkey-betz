"""
Government & Legislation Models

Dedicated models for congress members, bills, roll call votes, and vote positions.
Designed for RAG search over legislation and representative accountability.
"""

import hashlib
from django.db import models

try:
    from pgvector.django import VectorField
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    VectorField = None

EMBEDDING_DIM = 1536


class CongressMember(models.Model):
    """Federal congress member (Representative or Senator)."""
    bioguide_id = models.CharField(max_length=20, unique=True, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    party = models.CharField(max_length=50)
    chamber = models.CharField(max_length=20)  # senate, house
    state = models.CharField(max_length=2)
    district = models.IntegerField(null=True, blank=True)  # null for senators
    in_office = models.BooleanField(default=True)
    profile_url = models.URLField(blank=True)
    photo_url = models.URLField(blank=True)
    terms = models.JSONField(default=list)  # historical terms served
    committees = models.JSONField(default=list)  # current committee assignments
    leadership_role = models.CharField(max_length=200, blank=True)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['state', 'last_name']
        indexes = [
            models.Index(fields=['state', 'chamber']),
            models.Index(fields=['party']),
            models.Index(fields=['in_office']),
        ]

    def __str__(self):
        dist = f"-{self.district}" if self.district else ""
        return f"{self.first_name} {self.last_name} ({self.party[0]}-{self.state}{dist})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Bill(models.Model):
    """Federal or state legislation bill."""
    bill_uid = models.CharField(max_length=80, unique=True, db_index=True)
    jurisdiction = models.CharField(max_length=20, default='federal')  # federal, state
    state = models.CharField(max_length=2, blank=True)  # only for state bills
    congress = models.IntegerField(null=True, blank=True)
    bill_type = models.CharField(max_length=10, blank=True)  # HR, S, HJRES, etc.
    bill_number = models.IntegerField(null=True, blank=True)
    title = models.TextField()
    short_title = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    plain_summary = models.TextField(blank=True)
    summary_source = models.CharField(max_length=30, blank=True)  # congressgov, llm, none
    status = models.CharField(max_length=50, blank=True)
    status_date = models.DateField(null=True, blank=True)
    introduced_date = models.DateField(null=True, blank=True)
    chamber = models.CharField(max_length=20, blank=True)
    sponsors = models.ManyToManyField(CongressMember, related_name='sponsored_bills', blank=True)
    sponsor_names = models.JSONField(default=list)  # cached sponsor info from source
    committee = models.CharField(max_length=200, blank=True)
    topics = models.JSONField(default=list)
    full_text_url = models.URLField(blank=True)
    congress_gov_url = models.URLField(blank=True)
    legiscan_url = models.URLField(blank=True)
    legiscan_bill_id = models.IntegerField(null=True, blank=True, db_index=True)
    source = models.CharField(max_length=20, blank=True)
    last_action = models.TextField(blank=True)
    last_action_date = models.DateField(null=True, blank=True)

    # Embedding / RAG
    embedding_text = models.TextField(blank=True)
    if HAS_PGVECTOR:
        embedding = VectorField(dimensions=EMBEDDING_DIM, null=True, blank=True)
    else:
        embedding = models.BinaryField(null=True, blank=True)
    content_hash = models.CharField(max_length=64, blank=True, db_index=True)

    # Provenance
    source_urls = models.JSONField(default=list)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['congress', 'bill_type', 'bill_number']),
            models.Index(fields=['jurisdiction', 'state']),
            models.Index(fields=['status']),
            models.Index(fields=['-updated_at']),
        ]

    def __str__(self):
        return f"{self.bill_type}{self.bill_number} - {self.short_title or self.title[:80]}"

    def build_embedding_text(self):
        """Build deterministic text for embedding from bill fields."""
        parts = []
        if self.bill_type and self.bill_number:
            parts.append(f"{self.bill_type} {self.bill_number}")
        if self.congress:
            parts.append(f"({self.congress}th Congress)")
        if self.title:
            parts.append(self.title)
        if self.short_title and self.short_title != self.title:
            parts.append(self.short_title)
        if self.plain_summary:
            parts.append(self.plain_summary)
        elif self.description:
            parts.append(self.description)
        if self.status:
            parts.append(f"Status: {self.status}")
        if self.topics:
            parts.append(f"Topics: {', '.join(sorted(self.topics[:10]))}")
        if self.sponsor_names:
            names = [s.get('name', '') for s in self.sponsor_names[:5] if isinstance(s, dict)]
            if names:
                parts.append(f"Sponsors: {', '.join(names)}")
        if self.last_action:
            parts.append(f"Latest: {self.last_action}")
        self.embedding_text = ' | '.join(parts)
        return self.embedding_text

    def compute_content_hash(self):
        """Hash embedding_text for change detection."""
        if not self.embedding_text:
            self.build_embedding_text()
        normalized = ' '.join(self.embedding_text.split())
        self.content_hash = hashlib.sha256(normalized.encode()).hexdigest()
        return self.content_hash


class BillChunk(models.Model):
    """Chunked bill text for fine-grained RAG retrieval."""
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    heading = models.CharField(max_length=300, blank=True)
    text = models.TextField()
    content_hash = models.CharField(max_length=64, blank=True)
    if HAS_PGVECTOR:
        embedding = VectorField(dimensions=EMBEDDING_DIM, null=True, blank=True)
    else:
        embedding = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        unique_together = [('bill', 'chunk_index')]
        ordering = ['bill', 'chunk_index']

    def __str__(self):
        return f"{self.bill.bill_uid} chunk {self.chunk_index}"


class RollCallVote(models.Model):
    """A roll call vote in Congress."""
    congress = models.IntegerField()
    chamber = models.CharField(max_length=20)
    roll_number = models.IntegerField()
    session = models.IntegerField(default=1)
    date = models.DateField()
    question = models.TextField()
    description = models.TextField(blank=True)
    result = models.CharField(max_length=50)
    bill = models.ForeignKey(Bill, null=True, blank=True, on_delete=models.SET_NULL, related_name='roll_calls')
    yea_count = models.IntegerField(default=0)
    nay_count = models.IntegerField(default=0)
    not_voting_count = models.IntegerField(default=0)
    present_count = models.IntegerField(default=0)
    source_url = models.URLField(blank=True)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        unique_together = ['congress', 'chamber', 'roll_number', 'session']
        ordering = ['-date', '-roll_number']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['bill']),
        ]

    def __str__(self):
        return f"Roll {self.roll_number} ({self.chamber}, {self.congress}th) - {self.result}"


class VotePosition(models.Model):
    """How a specific member voted on a specific roll call."""
    POSITION_CHOICES = [
        ('Yea', 'Yea'),
        ('Nay', 'Nay'),
        ('Present', 'Present'),
        ('Not Voting', 'Not Voting'),
    ]
    roll_call = models.ForeignKey(RollCallVote, on_delete=models.CASCADE, related_name='positions')
    member = models.ForeignKey(CongressMember, on_delete=models.CASCADE, related_name='votes')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)

    class Meta:
        app_label = 'core'
        unique_together = ['roll_call', 'member']
        indexes = [
            models.Index(fields=['member', 'position']),
        ]

    def __str__(self):
        return f"{self.member} - {self.position} on Roll {self.roll_call.roll_number}"
