"""
Discord Training Data Spider
=============================

Session 420: Collects Discord conversation data for agent training.

Sources:
1. HuggingFace Discord datasets (breadlicker45/discord-chat, etc.)
2. LMSYS Chat Arena conversations (human-AI interactions)
3. UltraChat dialogues (filtered high-quality)

This spider fetches pre-collected Discord and chat data that can be used
to train agents on conversational patterns, Q&A, and community interactions.
"""

import aiohttp
import asyncio
import json
import os
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from ..base_spider import BaseIntelligenceSpider, SpiderTarget, IntelligenceData


class DiscordTrainingSpider(BaseIntelligenceSpider):
    """
    Spider for collecting Discord training data from public datasets.

    Unlike the regular Discord spider (which requires bot access to servers),
    this spider pulls from pre-collected, publicly available datasets that
    are legal and ToS-compliant to use for training.
    """

    # HuggingFace dataset endpoints
    # Note: Some datasets require HUGGINGFACE_TOKEN for access
    HUGGINGFACE_DATASETS = {
        # ============================================================
        # TIER 1: BEST PUBLIC DATASETS (No auth required, high quality)
        # ============================================================
        'openassistant': {
            'repo': 'OpenAssistant/oasst1',
            'description': 'OpenAssistant conversations - high quality human-AI dialogue',
            'type': 'ai_chat',
        },
        'dolly': {
            'repo': 'databricks/databricks-dolly-15k',
            'description': 'Databricks Dolly - 15K human-written instructions',
            'type': 'instruction',
        },
        'alpaca': {
            'repo': 'tatsu-lab/alpaca',
            'description': 'Stanford Alpaca - instruction tuning dataset',
            'type': 'instruction',
        },
        'no_robots': {
            'repo': 'HuggingFaceH4/no_robots',
            'description': 'No Robots - 10K human-written, zero AI slop',
            'type': 'instruction',
        },
        'slimorca': {
            'repo': 'Open-Orca/SlimOrca',
            'description': 'SlimOrca - 518K cleaned reasoning conversations',
            'type': 'reasoning',
        },
        'capybara': {
            'repo': 'LDJnr/Capybara',
            'description': 'Capybara - 16K multi-turn conversations',
            'type': 'conversation',
        },
        # ============================================================
        # TIER 2: GOOD PUBLIC DATASETS
        # ============================================================
        'topical_chat': {
            'repo': 'Conversational-Reasoning/Topical-Chat',
            'description': 'Topical conversations with knowledge grounding',
            'type': 'conversation',
        },
        # ============================================================
        # TIER 3: GATED DATASETS (Require HUGGINGFACE_TOKEN + terms acceptance)
        # Now unlocked - Session 420!
        # ============================================================
        'lmsys_chat': {
            'repo': 'lmsys/lmsys-chat-1m',
            'description': '1M real conversations with LLMs - UNLOCKED!',
            'type': 'ai_chat',
        },
        'ultrachat': {
            'repo': 'HuggingFaceH4/ultrachat_200k',
            'description': 'High-quality filtered dialogues',
            'type': 'ai_chat',
        },
        # ============================================================
        # REMOVED DATASETS (404 errors - Session 420 cleanup)
        # - wizard_vicuna: cognitivecomputations/wizard_vicuna_70k_unfiltered
        # - openhermes: teknium/OpenHermes-2.5
        # - evol_instruct: WizardLM/WizardLM_evol_instruct_V2_196k
        # - airoboros: jondurbin/airoboros-2.2.1
        # - chatbot_arena: lmsys/chatbot_arena_conversations
        # ============================================================
    }

    # Keywords that indicate high-quality training data
    QUALITY_KEYWORDS = [
        # Technical discussions
        'api', 'code', 'python', 'javascript', 'tutorial', 'documentation',
        'error', 'solution', 'fixed', 'working', 'example',
        # AI-specific
        'model', 'training', 'inference', 'prompt', 'llm', 'gpt', 'claude',
        'openai', 'anthropic', 'huggingface', 'fine-tune', 'embedding',
        # Problem-solving
        'how to', 'help with', 'anyone know', 'figured out', 'solved',
        'the trick is', 'what worked for me', 'best practice',
        # Creative
        'workflow', 'pipeline', 'automation', 'integration', 'project',
    ]

    # Topics to filter for
    RELEVANT_TOPICS = [
        'ai', 'machine learning', 'programming', 'development', 'tech',
        'creative', 'design', 'business', 'startup', 'productivity',
    ]

    def __init__(self, spider_id: str = 'discord_training', targets: List[SpiderTarget] = None,
                 subscribers: List[str] = None, redis_config: Dict[str, Any] = None):
        super().__init__(
            spider_id=spider_id,
            targets=targets or [],
            subscribers=subscribers or [],
            redis_config=redis_config or {}
        )
        # Try multiple env var names for HuggingFace token
        self.hf_token = os.getenv('HUGGING_FACE_API') or os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN', '')
        self.base_url = "https://datasets-server.huggingface.co"

    async def fetch_data(self, target: SpiderTarget) -> Optional[Dict[str, Any]]:
        """Fetch training data from HuggingFace datasets"""
        all_conversations = []

        try:
            headers = {}
            if self.hf_token:
                headers['Authorization'] = f'Bearer {self.hf_token}'

            async with aiohttp.ClientSession(headers=headers) as session:
                # Fetch from each dataset
                for dataset_key, dataset_info in self.HUGGINGFACE_DATASETS.items():
                    try:
                        conversations = await self._fetch_dataset(
                            session,
                            dataset_info['repo'],
                            dataset_info['type']
                        )
                        if conversations:
                            all_conversations.extend(conversations)
                            self.logger.info(f"Fetched {len(conversations)} from {dataset_key}")

                        # Rate limiting
                        await asyncio.sleep(1)

                    except Exception as e:
                        self.logger.warning(f"Error fetching {dataset_key}: {e}")
                        continue

            return {
                'conversations': all_conversations,
                'source': 'huggingface_datasets',
                'datasets_queried': list(self.HUGGINGFACE_DATASETS.keys()),
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error in fetch_data: {e}")
            return None

    async def _fetch_dataset(self, session: aiohttp.ClientSession, repo: str,
                            data_type: str) -> List[Dict[str, Any]]:
        """Fetch samples from a HuggingFace dataset"""
        conversations = []

        try:
            # Get dataset info first
            info_url = f"{self.base_url}/info?dataset={repo}"

            async with session.get(info_url, timeout=30) as response:
                if response.status != 200:
                    self.logger.warning(f"Dataset {repo} returned {response.status}")
                    return []

                info = await response.json()

            # Get first rows (samples)
            # HuggingFace datasets API allows fetching rows
            rows_url = f"{self.base_url}/rows?dataset={repo}&config=default&split=train&offset=0&length=100"

            async with session.get(rows_url, timeout=30) as response:
                if response.status != 200:
                    # Try without config
                    rows_url = f"{self.base_url}/first-rows?dataset={repo}&split=train"
                    async with session.get(rows_url, timeout=30) as retry_response:
                        if retry_response.status != 200:
                            return []
                        data = await retry_response.json()
                else:
                    data = await response.json()

            # Extract conversations from rows
            rows = data.get('rows', data.get('features', []))

            for row in rows[:100]:  # Limit to 100 per dataset
                row_data = row.get('row', row)

                # Different datasets have different formats
                conversation = self._extract_conversation(row_data, data_type, repo)
                if conversation:
                    conversations.append(conversation)

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout fetching {repo}")
        except Exception as e:
            self.logger.warning(f"Error fetching {repo}: {e}")

        return conversations

    def _extract_conversation(self, row: Dict, data_type: str, repo: str) -> Optional[Dict[str, Any]]:
        """Extract conversation from dataset row based on format"""
        try:
            conversation = {
                'source_dataset': repo,
                'data_type': data_type,
                'messages': [],
                'quality_score': 0.5,
                'topics': [],
            }

            # Handle different dataset formats
            if 'messages' in row:
                # Standard messages format
                conversation['messages'] = row['messages']
            elif 'conversation' in row:
                # Conversation format
                conversation['messages'] = row['conversation']
            elif 'content' in row:
                # Single message format
                conversation['messages'] = [{'role': 'user', 'content': row['content']}]
                if 'response' in row:
                    conversation['messages'].append({'role': 'assistant', 'content': row['response']})
            elif 'text' in row:
                # Text format
                conversation['messages'] = [{'role': 'user', 'content': row['text']}]
            elif 'prompt' in row:
                # Prompt/completion format
                conversation['messages'] = [{'role': 'user', 'content': row['prompt']}]
                if 'completion' in row:
                    conversation['messages'].append({'role': 'assistant', 'content': row['completion']})
            else:
                # Try to extract any text-like field
                for key in ['input', 'question', 'query']:
                    if key in row:
                        conversation['messages'] = [{'role': 'user', 'content': row[key]}]
                        break

            if not conversation['messages']:
                return None

            # Calculate quality score based on content
            conversation['quality_score'] = self._calculate_quality(conversation['messages'])

            # Extract topics
            conversation['topics'] = self._extract_topics(conversation['messages'])

            # Only return if quality is acceptable AND it's actual text content
            if conversation['quality_score'] >= 0.3:
                # Final check: reject if it's mostly URLs
                full_text = ' '.join(
                    m.get('content', '') if isinstance(m, dict) else str(m)
                    for m in conversation['messages']
                )
                # Skip if starts with URL or is mostly URL
                if full_text.strip().startswith('http') or full_text.count('http') > len(full_text) / 100:
                    return None
                return conversation

            return None

        except Exception as e:
            self.logger.debug(f"Error extracting conversation: {e}")
            return None

    def _calculate_quality(self, messages: List[Dict]) -> float:
        """Calculate quality score for a conversation"""
        score = 0.5  # Base score

        full_text = ' '.join(
            m.get('content', '') if isinstance(m, dict) else str(m)
            for m in messages
        ).lower()

        # Penalize URLs/image links (not useful for training)
        url_count = full_text.count('http://') + full_text.count('https://') + full_text.count('.gif') + full_text.count('.png') + full_text.count('.jpg')
        if url_count > 2:
            score -= 0.3

        # Penalize very short messages (likely just links or emojis)
        if len(full_text) < 50:
            score -= 0.4

        # Boost for quality keywords
        keyword_matches = sum(1 for kw in self.QUALITY_KEYWORDS if kw in full_text)
        score += min(0.3, keyword_matches * 0.05)

        # Boost for longer conversations (more context)
        if len(messages) >= 4:
            score += 0.1
        if len(messages) >= 8:
            score += 0.1

        # Boost for message length (substantial content)
        avg_length = sum(len(m.get('content', '')) if isinstance(m, dict) else len(str(m)) for m in messages) / max(1, len(messages))
        if avg_length > 100:
            score += 0.1
        if avg_length > 200:
            score += 0.1

        # Penalize very short or empty
        if avg_length < 20:
            score -= 0.3

        # Boost for question/answer patterns (useful for training)
        if '?' in full_text and len(messages) >= 2:
            score += 0.15

        return min(1.0, max(0.0, score))

    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """Extract relevant topics from conversation"""
        topics = []

        full_text = ' '.join(
            m.get('content', '') if isinstance(m, dict) else str(m)
            for m in messages
        ).lower()

        # Check for topic keywords
        topic_keywords = {
            'ai': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning'],
            'programming': ['code', 'programming', 'python', 'javascript', 'api', 'function'],
            'creative': ['design', 'creative', 'art', 'image', 'video', 'content'],
            'business': ['business', 'startup', 'revenue', 'customer', 'market'],
            'tech': ['technology', 'software', 'development', 'engineer', 'system'],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in full_text for kw in keywords):
                topics.append(topic)

        return topics

    async def process_data(self, raw_data: Dict[str, Any], target: SpiderTarget) -> Optional[IntelligenceData]:
        """Process fetched data into intelligence format"""
        try:
            conversations = raw_data.get('conversations', [])

            if not conversations:
                self.logger.warning("No conversations found in raw data")
                return None

            # Filter for quality and relevance
            high_quality = [c for c in conversations if c.get('quality_score', 0) >= 0.6]
            medium_quality = [c for c in conversations if 0.4 <= c.get('quality_score', 0) < 0.6]

            # Categorize by topic
            by_topic = {}
            for conv in conversations:
                for topic in conv.get('topics', ['general']):
                    if topic not in by_topic:
                        by_topic[topic] = []
                    by_topic[topic].append(conv)

            # Create training-ready format
            training_data = {
                'high_quality_conversations': high_quality[:50],
                'medium_quality_conversations': medium_quality[:50],
                'by_topic': {k: v[:20] for k, v in by_topic.items()},
                'statistics': {
                    'total_conversations': len(conversations),
                    'high_quality_count': len(high_quality),
                    'medium_quality_count': len(medium_quality),
                    'topics_found': list(by_topic.keys()),
                    'avg_quality_score': sum(c.get('quality_score', 0) for c in conversations) / max(1, len(conversations)),
                },
                'sample_formats': self._get_sample_formats(high_quality[:5]),
            }

            quality_score = min(1.0, len(high_quality) / 20 + 0.3)

            return IntelligenceData(
                spider_id=self.spider_id,
                source_url='huggingface.co/datasets',
                data_type='training_data',
                content=training_data,
                metadata={
                    'total_conversations': len(conversations),
                    'high_quality': len(high_quality),
                    'topics': list(by_topic.keys()),
                    'datasets_used': raw_data.get('datasets_queried', []),
                },
                quality_score=quality_score,
                timestamp=datetime.now(timezone.utc),
                relevance_tags=['training', 'conversations', 'discord', 'chat', 'ai'],
                target_agents=[
                    'personal_assistant_agent',
                    'creative_director_agent',
                    'content_strategy_agent',
                    'research_agent',
                ],
                target_advisors=['training_advisor', 'learning_advisor']
            )

        except Exception as e:
            self.logger.error(f"Error processing training data: {e}")
            return None

    def _get_sample_formats(self, conversations: List[Dict]) -> List[Dict]:
        """Get sample conversations in various training formats"""
        samples = []

        for conv in conversations:
            messages = conv.get('messages', [])
            if not messages:
                continue

            # Format 1: ChatML format
            chatml = []
            for msg in messages:
                if isinstance(msg, dict):
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                else:
                    role = 'user'
                    content = str(msg)
                chatml.append(f"<|im_start|>{role}\n{content}<|im_end|>")

            # Format 2: Instruction format
            instruction_format = {
                'instruction': messages[0].get('content', '') if isinstance(messages[0], dict) else str(messages[0]),
                'response': messages[-1].get('content', '') if len(messages) > 1 and isinstance(messages[-1], dict) else '',
            }

            samples.append({
                'original': conv,
                'chatml': '\n'.join(chatml),
                'instruction_format': instruction_format,
                'quality_score': conv.get('quality_score', 0),
            })

        return samples

    def get_required_fields(self) -> List[str]:
        return ['messages']

    def get_relevance_keywords(self) -> List[str]:
        return ['training', 'conversation', 'discord', 'chat', 'dialogue', 'ai']


# Convenience function to run spider manually
async def fetch_training_data():
    """Fetch training data - can be called from management commands"""
    spider = DiscordTrainingSpider()

    target = SpiderTarget(
        url='https://huggingface.co/datasets',
    )

    raw_data = await spider.fetch_data(target)
    if raw_data:
        result = await spider.process_data(raw_data, target)
        return result
    return None
