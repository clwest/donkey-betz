"""
Vector Embeddings and RAG System

Comprehensive RAG (Retrieval-Augmented Generation) system with vector embeddings,
semantic search, and knowledge retrieval capabilities.
"""

import os
import json
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

import numpy as np
from django.conf import settings
from django.core.cache import cache
from asgiref.sync import sync_to_async

from .models import Document, DocumentEmbedding, KnowledgeBase, EmbeddingModel

logger = logging.getLogger(__name__)

# Import embedding libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import importlib.util
    HAS_SENTENCE_TRANSFORMERS = importlib.util.find_spec('sentence_transformers') is not None
except Exception:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import cohere
    HAS_COHERE = True
except ImportError:
    HAS_COHERE = False


@dataclass
class SearchResult:
    """Result from semantic search"""
    document_id: str
    chunk_index: int
    chunk_text: str
    similarity_score: float
    document_title: str
    document_type: str
    metadata: Dict[str, Any] = None
    context_before: str = ""
    context_after: str = ""


@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    success: bool
    embedding: List[float] = None
    dimension: int = 0
    processing_time_ms: int = 0
    cost: float = 0.0
    error_message: str = ""
    model_used: str = ""


class BaseEmbeddingProvider(ABC):
    """Base class for embedding providers"""
    
    def __init__(self):
        self.model_name = ""
        self.dimension = 0
        self.cost_per_token = 0.0
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> EmbeddingResult:
        """Generate embedding for text"""
        pass
    
    @abstractmethod
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate similarity between two embeddings"""
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: 1 token ≈ 0.75 words
        return max(1, int(len(text.split()) * 0.75))


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        super().__init__()
        
        if not HAS_OPENAI:
            raise ImportError("OpenAI library not installed")
        
        self.model_name = model
        self.client = openai.OpenAI(api_key=settings.AI_PROVIDERS.get('OPENAI_API_KEY'))
        
        # Model configurations
        model_configs = {
            "text-embedding-3-small": {"dimension": 1536, "cost": 0.00002},
            "text-embedding-3-large": {"dimension": 3072, "cost": 0.00013},
            "text-embedding-ada-002": {"dimension": 1536, "cost": 0.00010},
        }
        
        config = model_configs.get(model, {"dimension": 1536, "cost": 0.00010})
        self.dimension = config["dimension"]
        self.cost_per_token = config["cost"]
    
    async def generate_embedding(self, text: str) -> EmbeddingResult:
        """Generate embedding using OpenAI API"""
        try:
            import time
            start_time = time.time()
            
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            embedding = response.data[0].embedding
            tokens_used = response.usage.total_tokens
            cost = tokens_used * self.cost_per_token
            
            return EmbeddingResult(
                success=True,
                embedding=embedding,
                dimension=len(embedding),
                processing_time_ms=processing_time,
                cost=cost,
                model_used=self.model_name
            )
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {str(e)}")
            return EmbeddingResult(
                success=False,
                error_message=str(e),
                model_used=self.model_name
            )
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity"""
        import numpy as np
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Sentence Transformer embedding provider (local)"""
    
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        super().__init__()

        if not HAS_SENTENCE_TRANSFORMERS:
            raise ImportError("sentence-transformers library not installed")

        self.model_name = model
        self._model = None
        self.dimension = None
        self.cost_per_token = 0.0  # Local model, no API cost

    def _get_model(self):
        """Lazy-load the SentenceTransformer model on first use."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self.dimension = self._model.get_sentence_embedding_dimension()
        return self._model

    async def generate_embedding(self, text: str) -> EmbeddingResult:
        """Generate embedding using Sentence Transformers"""
        try:
            import time
            start_time = time.time()

            embedding = self._get_model().encode(text, convert_to_tensor=False)
            processing_time = int((time.time() - start_time) * 1000)
            
            return EmbeddingResult(
                success=True,
                embedding=embedding.tolist(),
                dimension=len(embedding),
                processing_time_ms=processing_time,
                cost=0.0,
                model_used=self.model_name
            )
            
        except Exception as e:
            logger.error(f"Sentence Transformer embedding generation failed: {str(e)}")
            return EmbeddingResult(
                success=False,
                error_message=str(e),
                model_used=self.model_name
            )
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity"""
        import numpy as np
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class CohereEmbeddingProvider(BaseEmbeddingProvider):
    """Cohere embedding provider"""
    
    def __init__(self, model: str = "embed-english-v3.0"):
        super().__init__()
        
        if not HAS_COHERE:
            raise ImportError("cohere library not installed")
        
        self.model_name = model
        self.client = cohere.Client(api_key=settings.AI_PROVIDERS.get('COHERE_API_KEY'))
        
        # Model configurations
        model_configs = {
            "embed-english-v3.0": {"dimension": 1024, "cost": 0.0001},
            "embed-multilingual-v3.0": {"dimension": 1024, "cost": 0.0001},
        }
        
        config = model_configs.get(model, {"dimension": 1024, "cost": 0.0001})
        self.dimension = config["dimension"]
        self.cost_per_token = config["cost"]
    
    async def generate_embedding(self, text: str) -> EmbeddingResult:
        """Generate embedding using Cohere API"""
        try:
            import time
            start_time = time.time()
            
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
                input_type="search_document"
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            embedding = response.embeddings[0]
            
            # Estimate cost (Cohere doesn't provide token count in response)
            estimated_tokens = self.estimate_tokens(text)
            cost = estimated_tokens * self.cost_per_token
            
            return EmbeddingResult(
                success=True,
                embedding=embedding,
                dimension=len(embedding),
                processing_time_ms=processing_time,
                cost=cost,
                model_used=self.model_name
            )
            
        except Exception as e:
            logger.error(f"Cohere embedding generation failed: {str(e)}")
            return EmbeddingResult(
                success=False,
                error_message=str(e),
                model_used=self.model_name
            )
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity"""
        import numpy as np
        
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class EmbeddingManager:
    """Manages embedding providers and operations"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available embedding providers"""
        # OpenAI providers
        if HAS_OPENAI and settings.AI_PROVIDERS.get('OPENAI_API_KEY'):
            self.providers[EmbeddingModel.OPENAI_SMALL] = OpenAIEmbeddingProvider(
                "text-embedding-3-small"
            )
            self.providers[EmbeddingModel.OPENAI_LARGE] = OpenAIEmbeddingProvider(
                "text-embedding-3-large"
            )
            self.providers[EmbeddingModel.OPENAI_ADA] = OpenAIEmbeddingProvider(
                "text-embedding-ada-002"
            )
        
        # Sentence Transformer provider (Session 733: Wrap in try/except to prevent errors from blocking OpenAI)
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.providers[EmbeddingModel.SENTENCE_TRANSFORMER] = SentenceTransformerProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize SentenceTransformerProvider: {e}. Local embeddings unavailable.")
        
        # Cohere provider
        if HAS_COHERE and settings.AI_PROVIDERS.get('COHERE_API_KEY'):
            self.providers[EmbeddingModel.COHERE] = CohereEmbeddingProvider()
    
    def get_provider(self, model: EmbeddingModel) -> Optional[BaseEmbeddingProvider]:
        """Get embedding provider for model"""
        return self.providers.get(model)
    
    def get_available_models(self) -> List[EmbeddingModel]:
        """Get list of available embedding models"""
        return list(self.providers.keys())
    
    async def generate_embedding(self, text: str, model: EmbeddingModel) -> EmbeddingResult:
        """Generate embedding for text using specified model"""
        provider = self.get_provider(model)
        if not provider:
            return EmbeddingResult(
                success=False,
                error_message=f"Provider not available for model: {model}",
                model_used=str(model)
            )
        
        return await provider.generate_embedding(text)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float], 
                           model: EmbeddingModel) -> float:
        """Calculate similarity between embeddings"""
        provider = self.get_provider(model)
        if not provider:
            return 0.0
        
        return provider.calculate_similarity(embedding1, embedding2)


class TextSplitter:
    """Split text into chunks for embedding"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        if not text.strip():
            return []
        
        chunks = []
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_chunk = ""
        current_size = 0
        chunk_index = 0
        
        for paragraph in paragraphs:
            paragraph_size = len(paragraph)
            
            # If paragraph alone exceeds chunk size, split it
            if paragraph_size > self.chunk_size:
                # Save current chunk if not empty
                if current_chunk.strip():
                    chunks.append(self._create_chunk(
                        current_chunk, chunk_index, metadata
                    ))
                    chunk_index += 1
                    current_chunk = ""
                    current_size = 0
                
                # Split large paragraph
                sub_chunks = self._split_large_paragraph(paragraph)
                for sub_chunk in sub_chunks:
                    chunks.append(self._create_chunk(
                        sub_chunk, chunk_index, metadata
                    ))
                    chunk_index += 1
            
            # If adding paragraph exceeds chunk size, save current chunk
            elif current_size + paragraph_size > self.chunk_size and current_chunk:
                chunks.append(self._create_chunk(
                    current_chunk, chunk_index, metadata
                ))
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + paragraph
                current_size = len(current_chunk)
            
            # Add paragraph to current chunk
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                current_size += paragraph_size
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(self._create_chunk(
                current_chunk, chunk_index, metadata
            ))
        
        return chunks
    
    def _create_chunk(self, text: str, index: int, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create chunk dictionary"""
        return {
            'text': text.strip(),
            'index': index,
            'size': len(text),
            'metadata': metadata or {}
        }
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Split a large paragraph into smaller chunks"""
        sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap = self._get_overlap_text(current_chunk)
                current_chunk = overlap + sentence + "."
            else:
                if current_chunk:
                    current_chunk += sentence + "."
                else:
                    current_chunk = sentence + "."
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from end of chunk"""
        if len(text) <= self.chunk_overlap:
            return text + " "
        
        # Get last chunk_overlap characters, but try to break at word boundary
        overlap = text[-self.chunk_overlap:]
        space_index = overlap.find(' ')
        
        if space_index > 0:
            overlap = overlap[space_index:].strip() + " "
        
        return overlap


class VideoTranscriptSplitter:
    """Split Whisper verbose_json segments into chunks with timestamp metadata."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_segments(
        self, segments: List[Dict[str, Any]], metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Split Whisper segments into chunks preserving start/end timestamps.

        Each segment dict is expected to have 'text', 'start', and 'end' keys
        (standard Whisper verbose_json output).

        Returns list of dicts with keys: text, index, size, metadata.
        metadata includes start_ms and end_ms (integer milliseconds).
        """
        if not segments:
            return []

        chunks: List[Dict[str, Any]] = []
        current_text = ""
        current_start: float = segments[0].get("start", 0)
        current_end: float = 0
        chunk_index = 0
        base_meta = metadata or {}

        for seg in segments:
            seg_text = seg.get("text", "").strip()
            if not seg_text:
                continue

            seg_start = seg.get("start", 0)
            seg_end = seg.get("end", seg_start)

            candidate = (current_text + " " + seg_text).strip() if current_text else seg_text

            if len(candidate) > self.chunk_size and current_text:
                # Flush current chunk
                chunk_meta = {
                    **base_meta,
                    "start_ms": int(current_start * 1000),
                    "end_ms": int(current_end * 1000),
                }
                chunks.append({
                    "text": current_text.strip(),
                    "index": chunk_index,
                    "size": len(current_text),
                    "metadata": chunk_meta,
                })
                chunk_index += 1

                # Start new chunk (overlap: carry last segment text)
                current_text = seg_text
                current_start = seg_start
            else:
                current_text = candidate

            current_end = seg_end

        # Flush remaining
        if current_text.strip():
            chunk_meta = {
                **base_meta,
                "start_ms": int(current_start * 1000),
                "end_ms": int(current_end * 1000),
            }
            chunks.append({
                "text": current_text.strip(),
                "index": chunk_index,
                "size": len(current_text),
                "metadata": chunk_meta,
            })

        return chunks


class RAGSystem:
    """Retrieval-Augmented Generation system"""
    
    def __init__(self):
        self.embedding_manager = EmbeddingManager()
        self.text_splitter = TextSplitter()
    
    async def process_document_for_rag(self, document: Document, 
                                     embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL,
                                     chunk_size: int = 1000,
                                     chunk_overlap: int = 200) -> bool:
        """Process document and create embeddings for RAG"""
        try:
            # Get document content
            content = document.get_content()
            if not content.strip():
                logger.warning(f"Document {document.id} has no content to process")
                return False
            
            # Update document status (Session 733: Use sync_to_async for ORM calls)
            document.status = 'processing'
            await sync_to_async(document.save)()
            
            # Split text into chunks
            splitter = TextSplitter(chunk_size, chunk_overlap)
            chunks = splitter.split_text(content, {
                'document_id': str(document.id),
                'document_title': document.title,
                'document_type': document.document_type,
            })
            
            # Generate embeddings for each chunk
            provider = self.embedding_manager.get_provider(embedding_model)
            if not provider:
                raise ValueError(f"No provider available for model: {embedding_model}")
            
            total_cost = 0.0
            successful_chunks = 0
            
            for i, chunk_data in enumerate(chunks):
                try:
                    # Generate embedding
                    result = await self.embedding_manager.generate_embedding(
                        chunk_data['text'], embedding_model
                    )
                    
                    if result.success:
                        # Create DocumentEmbedding (Session 733: Use sync_to_async)
                        embedding_obj = await sync_to_async(DocumentEmbedding.objects.create)(
                            document=document,
                            embedding_model=embedding_model,
                            chunk_index=i,
                            chunk_text=chunk_data['text'],
                            chunk_size=chunk_data['size'],
                            overlap_size=chunk_overlap if i > 0 else 0,
                            embedding_vector=result.embedding,
                            embedding_dimension=result.dimension,
                            processing_time_ms=result.processing_time_ms,
                            embedding_cost=result.cost,
                            metadata=chunk_data['metadata']
                        )
                        
                        total_cost += result.cost
                        successful_chunks += 1
                        
                        logger.debug(f"Created embedding for chunk {i} of document {document.id}")
                    
                    else:
                        logger.error(f"Failed to generate embedding for chunk {i}: {result.error_message}")
                
                except Exception as e:
                    logger.error(f"Error processing chunk {i} of document {document.id}: {str(e)}")
                    continue
            
            # Update document status (Session 733: Use sync_to_async for ORM calls)
            if successful_chunks > 0:
                document.status = 'processed'
                document.add_processing_log(
                    step='embedding_generation',
                    status='success',
                    details={
                        'chunks_processed': successful_chunks,
                        'total_chunks': len(chunks),
                        'total_cost': total_cost,
                        'embedding_model': str(embedding_model)
                    }
                )
            else:
                document.status = 'failed'
                document.error_message = "Failed to generate any embeddings"

            await sync_to_async(document.save)()

            return successful_chunks > 0

        except Exception as e:
            logger.error(f"Error processing document {document.id} for RAG: {str(e)}")
            document.status = 'failed'
            document.error_message = str(e)
            await sync_to_async(document.save)()
            return False

    def process_document_for_rag_sync(self, document: Document,
                                      embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL,
                                      chunk_size: int = 1000,
                                      chunk_overlap: int = 200) -> bool:
        """
        Synchronous version of process_document_for_rag for use in Celery tasks.
        Session 733: Added to avoid nested async/sync recursion issues.
        """
        try:
            # Get document content
            content = document.get_content()
            if not content or not content.strip():
                logger.warning(f"Document {document.id} has no content to process")
                return False

            # Update document status
            document.status = 'processing'
            document.save()

            # Split text into chunks
            splitter = TextSplitter(chunk_size, chunk_overlap)
            chunks = splitter.split_text(content, {
                'document_id': str(document.id),
                'document_title': document.title,
                'document_type': document.document_type,
            })

            # Get provider
            provider = self.embedding_manager.get_provider(embedding_model)
            if not provider:
                raise ValueError(f"No provider available for model: {embedding_model}")

            total_cost = 0.0
            successful_chunks = 0

            for i, chunk_data in enumerate(chunks):
                try:
                    # Generate embedding synchronously (OpenAI client is sync)
                    result = self._generate_embedding_sync(provider, chunk_data['text'])

                    if result.success:
                        # Create DocumentEmbedding
                        DocumentEmbedding.objects.create(
                            document=document,
                            embedding_model=embedding_model,
                            chunk_index=i,
                            chunk_text=chunk_data['text'],
                            chunk_size=chunk_data['size'],
                            overlap_size=chunk_overlap if i > 0 else 0,
                            embedding_vector=result.embedding,
                            embedding_dimension=result.dimension,
                            processing_time_ms=result.processing_time_ms,
                            embedding_cost=result.cost,
                            metadata=chunk_data['metadata']
                        )

                        total_cost += result.cost
                        successful_chunks += 1
                        logger.debug(f"Created embedding for chunk {i} of document {document.id}")
                    else:
                        logger.error(f"Failed to generate embedding for chunk {i}: {result.error_message}")

                except Exception as e:
                    logger.error(f"Error processing chunk {i} of document {document.id}: {str(e)}")
                    continue

            # Update document status
            if successful_chunks > 0:
                document.status = 'processed'
                document.add_processing_log(
                    step='embedding_generation',
                    status='success',
                    details={
                        'chunks_processed': successful_chunks,
                        'total_chunks': len(chunks),
                        'total_cost': total_cost,
                        'embedding_model': str(embedding_model)
                    }
                )
            else:
                document.status = 'failed'
                document.error_message = "Failed to generate any embeddings"

            document.save()
            return successful_chunks > 0

        except Exception as e:
            logger.error(f"Error processing document {document.id} for RAG: {str(e)}")
            document.status = 'failed'
            document.error_message = str(e)
            document.save()
            return False

    def _generate_embedding_sync(self, provider, text: str) -> EmbeddingResult:
        """Synchronously generate embedding using a provider."""
        try:
            import time
            start_time = time.time()

            if hasattr(provider, 'client') and hasattr(provider.client, 'embeddings'):
                # OpenAI-style provider
                response = provider.client.embeddings.create(
                    input=text,
                    model=provider.model_name
                )
                processing_time = int((time.time() - start_time) * 1000)
                embedding = response.data[0].embedding
                tokens_used = response.usage.total_tokens
                cost = tokens_used * provider.cost_per_token

                return EmbeddingResult(
                    success=True,
                    embedding=embedding,
                    dimension=len(embedding),
                    processing_time_ms=processing_time,
                    cost=cost,
                    model_used=provider.model_name
                )
            elif hasattr(provider, 'model') and hasattr(provider.model, 'encode'):
                # Sentence Transformer provider
                embedding = provider.model.encode(text, convert_to_tensor=False)
                processing_time = int((time.time() - start_time) * 1000)

                return EmbeddingResult(
                    success=True,
                    embedding=embedding.tolist(),
                    dimension=len(embedding),
                    processing_time_ms=processing_time,
                    cost=0.0,
                    model_used=provider.model_name
                )
            else:
                return EmbeddingResult(
                    success=False,
                    error_message="Unknown provider type",
                    model_used="unknown"
                )

        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return EmbeddingResult(
                success=False,
                error_message=str(e),
                model_used=getattr(provider, 'model_name', 'unknown')
            )

    async def semantic_search(self, query: str, 
                            knowledge_base: KnowledgeBase = None,
                            embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL,
                            limit: int = 10,
                            similarity_threshold: float = 0.7) -> List[SearchResult]:
        """Perform semantic search across document embeddings"""
        try:
            # Generate query embedding
            query_result = await self.embedding_manager.generate_embedding(query, embedding_model)
            if not query_result.success:
                logger.error(f"Failed to generate query embedding: {query_result.error_message}")
                return []
            
            query_embedding = query_result.embedding
            
            # Get relevant document embeddings
            embeddings_query = DocumentEmbedding.objects.filter(
                embedding_model=embedding_model
            )
            
            if knowledge_base:
                # Filter by knowledge base
                kb_documents = knowledge_base.get_documents()
                embeddings_query = embeddings_query.filter(document__in=kb_documents)
            
            embeddings = embeddings_query.select_related('document')[:1000]  # Limit for performance
            
            # Calculate similarities
            results = []
            provider = self.embedding_manager.get_provider(embedding_model)
            
            if not provider:
                return []
            
            for embedding in embeddings:
                try:
                    similarity = provider.calculate_similarity(
                        query_embedding, embedding.embedding_vector
                    )
                    
                    if similarity >= similarity_threshold:
                        results.append(SearchResult(
                            document_id=str(embedding.document.id),
                            chunk_index=embedding.chunk_index,
                            chunk_text=embedding.chunk_text,
                            similarity_score=similarity,
                            document_title=embedding.document.title,
                            document_type=embedding.document.document_type,
                            metadata=embedding.metadata,
                            context_before=embedding.context_before,
                            context_after=embedding.context_after
                        ))
                
                except Exception as e:
                    logger.error(f"Error calculating similarity for embedding {embedding.id}: {str(e)}")
                    continue
            
            # Sort by similarity score and return top results
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []
    
    def get_context_for_generation(self, search_results: List[SearchResult], 
                                 max_context_length: int = 4000) -> str:
        """Extract context text from search results for content generation"""
        if not search_results:
            return ""
        
        context_parts = []
        current_length = 0
        
        for result in search_results:
            # Format context chunk
            chunk_text = f"[Source: {result.document_title}]\n{result.chunk_text}\n"
            
            if current_length + len(chunk_text) > max_context_length:
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n---\n".join(context_parts)
    
    async def retrieve_and_generate(self, query: str, 
                                  generation_prompt: str,
                                  knowledge_base: KnowledgeBase = None,
                                  embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL,
                                  max_results: int = 5,
                                  max_context_length: int = 4000) -> Dict[str, Any]:
        """Complete RAG workflow: retrieve relevant context and prepare for generation"""
        # Perform semantic search
        search_results = await self.semantic_search(
            query=query,
            knowledge_base=knowledge_base,
            embedding_model=embedding_model,
            limit=max_results
        )
        
        # Extract context
        context = self.get_context_for_generation(search_results, max_context_length)
        
        # Prepare generation context
        rag_context = {
            'query': query,
            'context': context,
            'search_results': [
                {
                    'document_title': result.document_title,
                    'similarity_score': result.similarity_score,
                    'chunk_preview': result.chunk_text[:200] + "..." if len(result.chunk_text) > 200 else result.chunk_text
                }
                for result in search_results
            ],
            'context_length': len(context),
            'num_sources': len(search_results)
        }
        
        return rag_context


# Global RAG system instance — lazy to avoid loading ML models at import time
_rag_system = None


def _get_rag_system():
    global _rag_system
    if _rag_system is None:
        _rag_system = RAGSystem()
    return _rag_system


class _LazyRAGSystem:
    """Proxy that defers RAGSystem() construction until first attribute access."""

    def __getattr__(self, name):
        return getattr(_get_rag_system(), name)


rag_system = _LazyRAGSystem()