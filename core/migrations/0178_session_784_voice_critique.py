"""
Session 784: Voice Critique System

Adds voice quality scoring fields to ChannelEpisode:
- intent_type: Content intent classification (visionary, technical_deep_dive, etc.)
- distinctiveness_score: How unique is the voice (0-100)
- specificity_score: Concrete examples vs generic statements (0-100)
- opinion_strength_score: Takes a stance vs hedges everything (0-100)
- generic_flag: Boolean flag for "sounds like every other AI blog"
- voice_critique_completed: Has VoiceCriticAgent scored this episode?

These fields support the "Voice Critic, not Voice Editor" pattern:
- Score content without editing it
- Store scores as metadata for learning
- System learns taste over time
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0177_spider_data_annotation'),
    ]

    operations = [
        # Add intent_type field
        migrations.AddField(
            model_name='channelepisode',
            name='intent_type',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Content intent: visionary, technical_deep_dive, operator_diary, contrarian_take, postmortem, behind_the_scenes',
                max_length=30,
            ),
        ),
        # Add distinctiveness_score field
        migrations.AddField(
            model_name='channelepisode',
            name='distinctiveness_score',
            field=models.IntegerField(
                default=0,
                help_text='Voice distinctiveness score (0-100): Could this have been written by anyone?',
            ),
        ),
        # Add specificity_score field
        migrations.AddField(
            model_name='channelepisode',
            name='specificity_score',
            field=models.IntegerField(
                default=0,
                help_text='Specificity score (0-100): Does it use concrete examples vs. generic statements?',
            ),
        ),
        # Add opinion_strength_score field
        migrations.AddField(
            model_name='channelepisode',
            name='opinion_strength_score',
            field=models.IntegerField(
                default=0,
                help_text='Opinion strength score (0-100): Does it take a real stance or hedge everything?',
            ),
        ),
        # Add generic_flag field
        migrations.AddField(
            model_name='channelepisode',
            name='generic_flag',
            field=models.BooleanField(
                default=False,
                help_text="True if content reads like 'every other AI blog' - buzzwords, corporate speak, lack of personality",
            ),
        ),
        # Add voice_critique_completed field
        migrations.AddField(
            model_name='channelepisode',
            name='voice_critique_completed',
            field=models.BooleanField(
                default=False,
                help_text='Whether VoiceCriticAgent has scored this episode',
            ),
        ),
        # Add index for intent_type
        migrations.AddIndex(
            model_name='channelepisode',
            index=models.Index(fields=['intent_type'], name='channel_epi_intent__f8e4c3_idx'),
        ),
        # Add index for voice_critique_completed
        migrations.AddIndex(
            model_name='channelepisode',
            index=models.Index(fields=['voice_critique_completed'], name='channel_epi_voice_c_a1b2c3_idx'),
        ),
    ]
