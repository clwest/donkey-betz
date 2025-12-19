# AI Podcast Studio - Implementation Plan

**Session:** 496
**Status:** Planning Complete
**Concept:** Multi-agent AI podcast where agents research, debate, and generate audio content

---

## The Vision

Imagine this: You give a topic like "Should AI replace human jobs?" and the system:

1. **Assigns Perspectives** - 3 AI agents take positions (Advocate, Skeptic, Analyst)
2. **Independent Research** - Each agent uses spiders to research their position
3. **Structured Debate** - Agents argue back and forth with evidence
4. **Script Generation** - A polished podcast script emerges from the debate
5. **Audio Production** - Different ElevenLabs voices for each speaker
6. **Final Episode** - A complete, ready-to-publish podcast!

---

## Architecture Overview

```
User Request: "Debate: Should AI be regulated?"
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│            PodcastDebateCoordinator                     │
│  (Orchestrates the entire podcast creation process)     │
└─────────────────────────────────────────────────────────┘
         │
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ DebateAdvocate  │ │  DebateSkeptic  │ │ PerformanceAnal │
│    Agent        │ │     Agent       │ │     yst         │
│ (Argues FOR)    │ │ (Argues AGAINST)│ │ (Data-driven)   │
│ Voice: Rachel   │ │ Voice: Clyde    │ │ Voice: Paul     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│              ResearchAgent (Spider Network)             │
│  Each agent researches independently using 72 spiders   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                  ModeratorAgent                         │
│  Hosts the discussion, asks questions, manages flow     │
│  Voice: Antoni                                          │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│               ContentWriterAgent                        │
│  Transforms debate into polished podcast_script         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│            PodcastAudioService (ElevenLabs)             │
│  Generates audio for each speaker, concatenates         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
    🎙️ Complete Podcast Episode
```

---

## Existing Components to Reuse

| Component | Location | How to Reuse |
|-----------|----------|--------------|
| `TopicMinerAgent` | `core/agents/content/topic_miner_agent.py` | Base for DebateAdvocateAgent |
| `ContrarianAgent` | `core/agents/content/contrarian_agent.py` | Base for DebateSkepticAgent |
| `PerformanceAnalystAgent` | `core/agents/content/performance_analyst_agent.py` | Use directly as neutral analyst |
| `ContentWriterAgent` | `core/agents/content_writer_agent.py` | Has `podcast_script` type already! |
| `AudioAgent` | `core/agents/audio_agent.py` | ElevenLabs integration |
| `ResearchAgent` | `core/agents/research_agent.py` | Spider + web research |
| `ContentDebate` model | `core/models_autonomous_studio.py` | Pattern for PodcastDebate |
| ElevenLabs provider | `content/elevenlabs_provider.py` | 12 voices available |

---

## New Components to Create

### 1. Database Models (`core/models_podcast_studio.py`)

```python
class PodcastShow(models.Model):
    """A podcast show configuration."""
    name = CharField(max_length=200)  # "AI Debates Weekly"
    topic_domain = TextField()  # "AI, technology, startups"
    format = CharField(choices=['debate', 'roundtable', 'interview'])
    participant_count = IntegerField(default=3)
    host_voice_id = CharField(max_length=100)
    participant_voices = JSONField(default=list)
    generate_audio = BooleanField(default=True)

class PodcastEpisode(models.Model):
    """A single podcast episode."""
    show = ForeignKey(PodcastShow)
    title = CharField(max_length=200)
    topic = CharField(max_length=200)
    episode_number = IntegerField()
    script = TextField()
    script_segments = JSONField(default=list)
    audio_url = URLField(blank=True)
    status = CharField(choices=['researching', 'debating', 'scripting', 'recording', 'complete'])

class PodcastDebate(models.Model):
    """Records the multi-agent debate."""
    topic = CharField(max_length=200)
    topic_question = TextField()  # "Should AI be regulated?"
    participants = JSONField()  # [{agent, role, voice_id}]
    research_results = JSONField()  # Per-agent findings
    arguments = JSONField()  # {agent: {position, points, evidence}}
    debate_transcript = JSONField()  # [{speaker, text, timestamp}]
```

### 2. New Agents (`core/agents/podcast/`)

| Agent | Purpose |
|-------|---------|
| `PodcastDebateCoordinator` | Main orchestrator - assigns roles, manages flow |
| `DebateAdvocateAgent` | Argues FOR the topic with evidence |
| `DebateSkepticAgent` | Argues AGAINST, challenges assumptions |
| `ModeratorAgent` | Hosts, asks questions, summarizes |

### 3. Services

| Service | Purpose |
|---------|---------|
| `PodcastAudioService` | Multi-voice TTS + audio concatenation |
| `PodcastScriptGenerator` | Debate-to-script transformation |

---

## API Endpoints

```python
# Podcast Show Management
POST   /api/podcast/shows/create/          # Create new show
GET    /api/podcast/shows/                 # List shows
GET    /api/podcast/shows/<id>/            # Show details

# Episode Generation
POST   /api/podcast/generate/              # Generate new episode
GET    /api/podcast/generate/<job_id>/status/  # Check progress
GET    /api/podcast/episodes/              # List episodes
GET    /api/podcast/episodes/<id>/         # Episode details
GET    /api/podcast/episodes/<id>/script/  # Get script
GET    /api/podcast/episodes/<id>/audio/   # Get audio

# Debate Details
GET    /api/podcast/debates/<id>/          # Debate record
GET    /api/podcast/debates/<id>/transcript/  # Full transcript
```

### Generate Episode Request

```json
POST /api/podcast/generate/
{
    "topic": "Should AI replace human jobs?",
    "format": "debate",
    "participants": 3,
    "generate_audio": true,
    "voices": {
        "host": "Antoni",
        "advocate": "Rachel",
        "skeptic": "Clyde",
        "analyst": "Paul"
    },
    "duration_target": 10
}
```

---

## Discord Commands

```
/podcast-create <topic> [format] [participants]
  - Generate a new AI podcast episode
  - Format: debate, roundtable, interview
  - Participants: 2-4

/podcast-status <job_id>
  - Check generation progress

/podcast-list
  - List your podcast episodes

/podcast-play [episode_id]
  - Play podcast in voice channel

/podcast-debate <episode_id>
  - View the agent debate transcript
```

---

## Celery Tasks

```python
# Main generation pipeline
@shared_task
def generate_podcast_episode_task(topic, format, participants, voices, user_id):
    """Full podcast generation pipeline."""

# Sub-tasks
@shared_task
def research_debate_position_task(topic, perspective, agent_name):
    """Single agent researches their position."""

@shared_task
def generate_podcast_audio_task(script_segments, voice_config, episode_id):
    """Generate TTS for each speaker."""

@shared_task
def concatenate_podcast_audio_task(audio_segments, episode_id):
    """Combine audio into final episode."""
```

---

## Implementation Phases

### Phase 1: Foundation (1 session)
- [ ] Create `core/models_podcast_studio.py`
- [ ] Migration `0101_podcast_studio_models.py`
- [ ] Basic API endpoints
- [ ] Register in admin

### Phase 2: Debate System (1-2 sessions)
- [ ] Create `core/agents/podcast/` directory
- [ ] Implement `PodcastDebateCoordinator`
- [ ] Implement `DebateAdvocateAgent` (extends TopicMinerAgent)
- [ ] Implement `DebateSkepticAgent` (extends ContrarianAgent)
- [ ] Implement `ModeratorAgent`
- [ ] Add to `AgentRouter`

### Phase 3: Script Generation (1 session)
- [ ] Create debate-to-script templates
- [ ] Extend `ContentWriterAgent` for debate scripts
- [ ] Test full debate → script pipeline

### Phase 4: Audio Generation (1 session)
- [ ] Create `PodcastAudioService`
- [ ] Multi-voice segment generation
- [ ] Audio concatenation with ffmpeg
- [ ] Integration with VoiceProfile marketplace

### Phase 5: Async Pipeline (1 session)
- [ ] Celery tasks for generation pipeline
- [ ] Job status tracking
- [ ] Add to Celery Beat

### Phase 6: Discord Integration (1 session)
- [ ] Create `PodcastCog`
- [ ] Implement all `/podcast-*` commands
- [ ] Voice channel playback

### Phase 7: Frontend (Optional, 1-2 sessions)
- [ ] Podcast Studio tab in AI Studio
- [ ] Episode player component
- [ ] Debate visualization

---

## Voice Assignments (ElevenLabs)

| Role | Voice | Character |
|------|-------|-----------|
| Host/Moderator | Antoni | Warm, professional narrator |
| Advocate (FOR) | Rachel | Enthusiastic, optimistic |
| Skeptic (AGAINST) | Clyde | Authoritative, critical |
| Analyst (NEUTRAL) | Paul | Calm, data-driven |
| Expert Guest | Drew | Confident, knowledgeable |

---

## Example Output

### Debate Transcript (Internal)
```
ModeratorAgent: Welcome to AI Debates! Today's topic: Should AI replace human jobs?
DebateAdvocateAgent: AI will CREATE more jobs than it eliminates. History shows...
DebateSkepticAgent: That's naive optimism. The IMF predicts 40% of jobs affected...
PerformanceAnalystAgent: The data shows mixed results. In manufacturing...
ModeratorAgent: Interesting point. Rachel, how do you respond to the IMF data?
...
```

### Podcast Script (Output)
```
[INTRO MUSIC - 5 seconds]

ANTONI (Host): Welcome to AI Debates, the podcast where artificial minds
argue the issues that matter. I'm your host, and today we're tackling
a question on everyone's mind: Should AI replace human jobs?

Joining me are three perspectives...

[SEGMENT 1: Opening Statements]

RACHEL (Advocate): Thanks for having me! I firmly believe AI will
CREATE more opportunities than it eliminates...

CLYDE (Skeptic): I appreciate the optimism, but let's look at the facts...
```

---

## Why This is Exciting

1. **Novel Content Creation** - AI-generated podcasts with actual debates
2. **Multi-Agent Collaboration** - Agents work together with different roles
3. **Real Research** - Each position is backed by spider data
4. **Full Audio** - Ready-to-publish content with professional voices
5. **Autonomous** - Set a topic, get a complete episode
6. **Extensible** - Add new debate formats, voices, styles

---

## Dependencies

- ElevenLabs API (existing)
- ffmpeg for audio concatenation
- Existing agent infrastructure
- Spider network for research

---

**Ready to build the future of AI-generated podcasts!** 🎙️
