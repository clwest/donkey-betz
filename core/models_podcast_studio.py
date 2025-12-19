"""
AI Podcast Studio Models - Session 496

Models for multi-agent AI podcast generation where agents research,
debate, and create audio content with different voices.

The system orchestrates:
1. PodcastShow - A podcast series configuration
2. PodcastEpisode - Individual episodes with scripts and audio
3. PodcastDebate - The multi-agent debate that forms each episode
4. PodcastParticipant - Reusable debate personas with voice configs
"""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class PodcastShow(models.Model):
    """
    A podcast show configuration - like a content channel for podcasts.

    Example: "AI Debates Weekly" - a show where AI agents debate tech topics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='podcast_shows')

    # Show Identity
    name = models.CharField(max_length=200)  # "AI Debates Weekly"
    description = models.TextField(blank=True)
    topic_domain = models.TextField(blank=True)  # "AI, technology, startups, ethics"
    target_audience = models.CharField(max_length=200, blank=True)

    # Format Configuration
    FORMAT_CHOICES = [
        ('debate', 'Debate - Two sides argue'),
        ('roundtable', 'Roundtable - Multiple perspectives'),
        ('interview', 'Interview - Host interviews expert'),
        ('monologue', 'Monologue - Single speaker deep dive'),
    ]
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='debate')
    participant_count = models.IntegerField(default=3)  # 2-4 participants
    episode_duration_minutes = models.IntegerField(default=10)  # Target duration

    # Voice Configuration
    host_voice_id = models.CharField(max_length=100, default='Antoni')  # ElevenLabs voice
    participant_voices = models.JSONField(default=list)  # [{role: voice_id}, ...]

    # Generation Settings
    generate_audio = models.BooleanField(default=True)
    include_intro_music = models.BooleanField(default=True)
    include_outro_music = models.BooleanField(default=True)

    # Stats
    episode_count = models.IntegerField(default=0)
    total_listens = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Podcast Show'
        verbose_name_plural = 'Podcast Shows'

    def __str__(self):
        return f"{self.name} ({self.format})"


class PodcastDebate(models.Model):
    """
    Records the multi-agent debate that forms the basis of a podcast episode.

    Each debate has:
    - A topic question ("Should AI be regulated?")
    - Multiple participants with assigned perspectives
    - Independent research results per participant
    - Structured arguments and rebuttals
    - A complete debate transcript
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Topic
    topic = models.CharField(max_length=200)  # Short topic
    topic_question = models.TextField()  # Full debate question
    topic_context = models.TextField(blank=True)  # Additional context/research

    # Participants
    # Format: [{agent_name, role, voice_id, perspective}]
    participants = models.JSONField(default=list)

    # Research Phase - each agent's independent research
    # Format: {agent_name: {sources: [], findings: [], key_points: []}}
    research_results = models.JSONField(default=dict)

    # Argument Phase - structured arguments per participant
    # Format: {agent_name: {position, main_arguments: [], evidence: [], rebuttals: []}}
    arguments = models.JSONField(default=dict)

    # Debate Transcript - the actual back-and-forth
    # Format: [{speaker, role, text, timestamp_seconds}]
    debate_transcript = models.JSONField(default=list)

    # Outcome
    consensus = models.TextField(blank=True)  # If any consensus reached
    key_takeaways = models.JSONField(default=list)  # Main points from debate
    winner = models.CharField(max_length=100, blank=True)  # Optional: who "won"

    # Timing
    debate_duration_seconds = models.IntegerField(null=True)

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('researching', 'Researching'),
        ('debating', 'Debating'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Podcast Debate'
        verbose_name_plural = 'Podcast Debates'

    def __str__(self):
        return f"Debate: {self.topic} ({self.status})"

    def add_transcript_entry(self, speaker: str, role: str, text: str, timestamp: float = None):
        """Add an entry to the debate transcript."""
        entry = {
            'speaker': speaker,
            'role': role,
            'text': text,
            'timestamp_seconds': timestamp or len(self.debate_transcript) * 30  # Estimate
        }
        self.debate_transcript.append(entry)
        self.save(update_fields=['debate_transcript'])


class PodcastEpisode(models.Model):
    """
    A single podcast episode with debate content and optional audio.

    Each episode goes through stages:
    1. researching - Agents research their positions
    2. debating - Agents engage in structured debate
    3. scripting - Debate transformed into podcast script
    4. recording - TTS generates audio for each speaker
    5. complete - Final audio assembled
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    show = models.ForeignKey(PodcastShow, on_delete=models.CASCADE, related_name='episodes', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='podcast_episodes')

    # Episode Info
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    episode_number = models.IntegerField(default=1)

    # The underlying debate
    debate = models.OneToOneField(PodcastDebate, on_delete=models.SET_NULL, null=True, related_name='episode')

    # Generated Script
    script = models.TextField(blank=True)  # Full podcast script
    # Format: [{speaker, voice_id, text, segment_type}]
    script_segments = models.JSONField(default=list)
    show_notes = models.TextField(blank=True)

    # Audio (if generated)
    audio_file = models.FileField(upload_to='podcasts/audio/', null=True, blank=True)
    audio_url = models.URLField(blank=True)
    audio_duration_seconds = models.IntegerField(null=True)

    # Individual audio segments before concatenation
    # Format: [{segment_id, speaker, audio_url, duration_seconds}]
    audio_segments = models.JSONField(default=list)

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('researching', 'Researching Positions'),
        ('debating', 'Agents Debating'),
        ('scripting', 'Generating Script'),
        ('recording', 'Recording Audio'),
        ('assembling', 'Assembling Audio'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    error_message = models.TextField(blank=True)
    progress_percent = models.IntegerField(default=0)

    # Generation config used
    generation_config = models.JSONField(default=dict)  # Store the config used

    # Stats
    listen_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Podcast Episode'
        verbose_name_plural = 'Podcast Episodes'

    def __str__(self):
        return f"#{self.episode_number}: {self.title} ({self.status})"

    def update_status(self, status: str, progress: int = None, error: str = None):
        """Update episode status and progress."""
        self.status = status
        if progress is not None:
            self.progress_percent = progress
        if error:
            self.error_message = error
        if status == 'complete':
            self.published_at = timezone.now()
            self.progress_percent = 100
        self.save(update_fields=['status', 'progress_percent', 'error_message', 'published_at'])


class PodcastParticipant(models.Model):
    """
    A reusable participant persona for podcasts.

    Personas can be reused across episodes for consistency:
    - "Dr. Tech Optimist" - always argues for technology
    - "The Skeptic" - always challenges assumptions
    - "Data Dan" - always brings statistics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='podcast_participants')

    # Identity
    name = models.CharField(max_length=100)  # "Dr. Tech Optimist"
    avatar_url = models.URLField(blank=True)  # Optional avatar

    # Role
    ROLE_CHOICES = [
        ('host', 'Host/Moderator'),
        ('advocate', 'Advocate (argues FOR)'),
        ('skeptic', 'Skeptic (argues AGAINST)'),
        ('analyst', 'Analyst (data-driven neutral)'),
        ('expert', 'Expert (domain knowledge)'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Personality for GPT
    personality = models.TextField()  # Detailed personality description
    speaking_style = models.CharField(max_length=200)  # "formal", "casual", "passionate"
    expertise_areas = models.JSONField(default=list)  # ["AI", "economics", "ethics"]

    # Voice Configuration
    VOICE_CHOICES = [
        ('Rachel', 'Rachel - Warm, enthusiastic'),
        ('Drew', 'Drew - Confident, clear'),
        ('Clyde', 'Clyde - Authoritative, deep'),
        ('Paul', 'Paul - Calm, conversational'),
        ('Aria', 'Aria - Expressive, dynamic'),
        ('Domi', 'Domi - Strong, assertive'),
        ('Dave', 'Dave - Friendly, approachable'),
        ('Antoni', 'Antoni - Warm narrator'),
        ('Sarah', 'Sarah - Soft, thoughtful'),
        ('Josh', 'Josh - Energetic, young'),
        ('Bella', 'Bella - Gentle, soothing'),
        ('Charlotte', 'Charlotte - Professional, elegant'),
    ]
    voice_id = models.CharField(max_length=100, choices=VOICE_CHOICES, default='Antoni')

    # Agent Mapping - which agent powers this persona
    agent_class = models.CharField(max_length=100, default='DebateAdvocateAgent')

    # Usage stats
    episodes_participated = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Podcast Participant'
        verbose_name_plural = 'Podcast Participants'

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"


# Default participants to create for new users
DEFAULT_PARTICIPANTS = [
    {
        'name': 'Alex the Advocate',
        'role': 'advocate',
        'personality': 'Optimistic and enthusiastic about new ideas. Finds the silver lining in every technology and trend. Uses compelling narratives and success stories to make points.',
        'speaking_style': 'enthusiastic, uses metaphors, builds momentum',
        'voice_id': 'Rachel',
        'agent_class': 'DebateAdvocateAgent',
    },
    {
        'name': 'Sam the Skeptic',
        'role': 'skeptic',
        'personality': 'Critical thinker who challenges assumptions. Not negative, but rigorous. Asks tough questions and demands evidence. Plays devil\'s advocate effectively.',
        'speaking_style': 'measured, probing, uses rhetorical questions',
        'voice_id': 'Clyde',
        'agent_class': 'DebateSkepticAgent',
    },
    {
        'name': 'Dana the Data Analyst',
        'role': 'analyst',
        'personality': 'Neutral and data-driven. Cites statistics, studies, and research. Balances both sides with evidence. Helps find common ground.',
        'speaking_style': 'precise, references sources, objective',
        'voice_id': 'Paul',
        'agent_class': 'PerformanceAnalystAgent',
    },
    {
        'name': 'Morgan the Moderator',
        'role': 'host',
        'personality': 'Warm and engaging podcast host. Asks great follow-up questions. Ensures fair time distribution. Summarizes key points clearly.',
        'speaking_style': 'conversational, curious, summarizes well',
        'voice_id': 'Antoni',
        'agent_class': 'ModeratorAgent',
    },
]
