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

    # Workspace linkage
    workspace = models.ForeignKey(
        'core.ProjectWorkspace', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='podcast_shows', db_index=True,
    )

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

    # Session 862: Content Flow Traceability
    initiative = models.ForeignKey(
        'core.Initiative',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='podcast_episodes',
        help_text="Session 862: Initiative this podcast belongs to"
    )
    dream = models.ForeignKey(
        'core.AgentDream',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='podcast_episodes',
        help_text="Session 862: Dream that originated this podcast"
    )
    initiative_stage = models.ForeignKey(
        'core.InitiativeStage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='podcast_episodes',
        help_text="Session 862: Initiative stage this podcast fulfills"
    )

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

    # TTS Cost Tracking (Session 770)
    tts_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    tts_cost_breakdown = models.JSONField(default=dict)  # {elevenlabs: 0.XX, characters: 1234}

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


class PodcastStyleProfile(models.Model):
    """
    Session 890: Style profile for podcast episodes.

    Based on ChatGPT feedback - tracks quality metrics for podcasts similar
    to how VoiceCriticAgent scores blogs. Enables the system to learn and
    improve podcast quality over time.

    Key metrics:
    - Humor: Percentage of content that includes wit/levity
    - Technical depth: How detailed/advanced the technical content is
    - Story density: How many concrete stories/examples are included
    - Authority score: How confident and stance-taking the content is
    - Platform mentions: References to Donkey Betz features
    - Generic flag: Whether content sounds like "every other AI podcast"
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to episode
    episode = models.OneToOneField(
        PodcastEpisode,
        on_delete=models.CASCADE,
        related_name='style_profile'
    )

    # Voice Quality Scores (0-100)
    distinctiveness_score = models.IntegerField(
        default=0,
        help_text="0-100: Could this be anyone, or is it unique?"
    )
    specificity_score = models.IntegerField(
        default=0,
        help_text="0-100: Concrete examples vs generic statements"
    )
    opinion_strength_score = models.IntegerField(
        default=0,
        help_text="0-100: Takes real stance vs hedges everything"
    )

    # Podcast-Specific Metrics (0-100)
    humor_percent = models.IntegerField(
        default=0,
        help_text="0-100: How much wit/levity is in the content"
    )
    technical_depth = models.IntegerField(
        default=0,
        help_text="0-100: How detailed/advanced the technical content"
    )
    story_density = models.IntegerField(
        default=0,
        help_text="0-100: How many concrete stories/examples included"
    )
    authority_score = models.IntegerField(
        default=0,
        help_text="0-100: Confident, stance-taking content"
    )

    # Platform Integration
    platform_mentions = models.IntegerField(
        default=0,
        help_text="Count of Donkey Betz feature references"
    )
    war_stories_count = models.IntegerField(
        default=0,
        help_text="Count of real system incidents/timestamps mentioned"
    )

    # Flags
    generic_flag = models.BooleanField(
        default=False,
        help_text="True if content sounds like every other AI podcast"
    )
    has_concrete_examples = models.BooleanField(
        default=False,
        help_text="True if content includes specific data/timestamps"
    )
    host_has_pov = models.BooleanField(
        default=False,
        help_text="True if host takes stances instead of just moderating"
    )

    # Intent Classification
    INTENT_CHOICES = [
        ('visionary', 'Visionary - Future predictions'),
        ('technical_deep_dive', 'Technical Deep-Dive'),
        ('operator_diary', 'Operator Diary - Real experience'),
        ('contrarian_take', 'Contrarian Take'),
        ('postmortem', 'Postmortem - Lessons learned'),
        ('behind_the_scenes', 'Behind the Scenes'),
    ]
    intent_type = models.CharField(
        max_length=50,
        choices=INTENT_CHOICES,
        default='visionary'
    )
    intent_confidence = models.FloatField(default=0.5)

    # Analysis Details
    generic_phrases_found = models.JSONField(
        default=list,
        help_text="List of generic phrases detected in the script"
    )
    hedging_phrases_found = models.JSONField(
        default=list,
        help_text="List of hedging phrases detected"
    )
    specific_examples = models.JSONField(
        default=list,
        help_text="List of specific examples/stories extracted"
    )

    # Overall Score (composite of all metrics)
    overall_quality_score = models.IntegerField(
        default=0,
        help_text="0-100: Weighted average of all quality metrics"
    )

    # Analysis metadata
    analyzed_at = models.DateTimeField(auto_now_add=True)
    analyzer_version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Version of the analysis algorithm"
    )

    class Meta:
        ordering = ['-analyzed_at']
        verbose_name = 'Podcast Style Profile'
        verbose_name_plural = 'Podcast Style Profiles'

    def __str__(self):
        return f"Style Profile: {self.episode.title} (Q:{self.overall_quality_score})"

    def calculate_overall_score(self):
        """
        Calculate weighted overall quality score.

        Weights based on ChatGPT feedback priorities:
        - Specificity (stories/examples): 25%
        - Authority (stance-taking): 20%
        - Distinctiveness (unique voice): 20%
        - Story density: 15%
        - Technical depth: 10%
        - Humor: 10%
        """
        weights = {
            'specificity_score': 0.25,
            'authority_score': 0.20,
            'distinctiveness_score': 0.20,
            'story_density': 0.15,
            'technical_depth': 0.10,
            'humor_percent': 0.10,
        }

        total = sum(
            getattr(self, attr, 0) * weight
            for attr, weight in weights.items()
        )

        # Penalties
        if self.generic_flag:
            total *= 0.7  # 30% penalty for generic content
        if not self.has_concrete_examples:
            total *= 0.85  # 15% penalty for no examples
        if not self.host_has_pov:
            total *= 0.9  # 10% penalty for bland host

        # Bonuses
        if self.war_stories_count >= 1:
            total *= 1.1  # 10% bonus for system stories
        if self.platform_mentions >= 1:
            total *= 1.05  # 5% bonus for platform integration

        self.overall_quality_score = min(100, int(total))
        return self.overall_quality_score

    def save(self, *args, **kwargs):
        """Calculate overall score before saving."""
        self.calculate_overall_score()
        super().save(*args, **kwargs)
