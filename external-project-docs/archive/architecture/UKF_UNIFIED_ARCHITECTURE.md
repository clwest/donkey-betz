# UKF Unified Architecture Design
**Consolidating Universal Knowledge Format into Django Backend**

## 🎯 Architecture Overview

The unified system will consolidate all UKF components into the Django backend, creating a single source of truth that provides:

1. **Unified Search** - Conversations + Documents in one interface
2. **Rich Metadata** - Temporal tracking, entities, relationships
3. **Django Integration** - Proper models, migrations, management commands
4. **Real Data** - Migrated from existing 2,201 processed markdown files
5. **Performance** - Optimized database with proper indexing

## 📁 Proposed Directory Structure

```
backend/
├── ukf_system/                           # 🆕 New Django App
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                         # Django models for all UKF data
│   ├── admin.py                          # Admin interface for UKF content
│   ├── urls.py                           # UKF-specific endpoints
│   ├── views.py                          # API views for UKF search
│   │
│   ├── services/                         # Core business logic
│   │   ├── __init__.py
│   │   ├── markdown_processor.py         # Process raw markdown files
│   │   ├── embedding_service.py          # Generate embeddings with Phase 8 integration
│   │   ├── import_service.py             # Bulk import utilities
│   │   ├── search_service.py             # Unified search across all content
│   │   ├── metadata_extractor.py         # Extract entities, topics, sentiment
│   │   ├── relationship_detector.py      # Find cross-references between content
│   │   └── temporal_analyzer.py          # Track idea evolution over time
│   │
│   ├── management/
│   │   └── commands/
│   │       ├── import_markdown_files.py  # Import markdown files with metadata
│   │       ├── migrate_ukf_database.py   # Import from existing SQLite
│   │       ├── rebuild_ukf_index.py      # Rebuild search indexes
│   │       ├── analyze_content.py        # Run metadata extraction
│   │       └── export_ukf_data.py        # Export in UKF format
│   │
│   ├── migrations/                       # Django database migrations
│   │   └── 0001_initial.py
│   │
│   ├── templates/ukf_system/             # Admin templates
│   │   ├── document_detail.html
│   │   └── search_results.html
│   │
│   └── tests/                            # Test suite
│       ├── test_models.py
│       ├── test_services.py
│       ├── test_import.py
│       └── test_search.py
│
├── ai_partner/                           # 🔄 Enhanced Integration
│   └── memory_services/
│       ├── unified_memory_search.py     # 🆕 Search across all content types
│       ├── ukf_memory_service.py        # 🔄 Enhanced to use real UKF data
│       └── content_aware_embedding_service.py  # 🔄 Extended for documents
│
└── ukf_integration/                      # 🔄 Simplified Bridge
    ├── bridge.py                        # 🔄 Simplified - delegates to ukf_system
    └── legacy_views.py                  # Backward compatibility
```

## 🗄️ Django Models Design

### Core Document Model

```python
class MarkdownDocument(models.Model):
    """Represents a markdown file in the knowledge base"""
    
    # Identity & Ownership
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # File Metadata (from location #1 schema)
    file_path = models.CharField(max_length=500, unique=True)
    file_name = models.CharField(max_length=255)
    relative_path = models.CharField(max_length=500)
    project_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  # notes/projects/qa/rants
    
    # Content
    title = models.CharField(max_length=255)
    raw_content = models.TextField()
    processed_content = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    key_points = models.JSONField(default=list)
    word_count = models.IntegerField(default=0)
    line_count = models.IntegerField(default=0)
    
    # Timestamps
    file_created_date = models.DateTimeField(null=True, blank=True)
    file_modified_date = models.DateTimeField(null=True, blank=True)
    discovered_date = models.DateTimeField(auto_now_add=True)
    last_accessed_date = models.DateTimeField(null=True, blank=True)
    imported_date = models.DateTimeField(auto_now_add=True)
    
    # File Integrity
    content_hash = models.CharField(max_length=64)  # SHA256
    file_size = models.IntegerField()
    
    # Classification (from location #2 UKF format)
    primary_type = models.CharField(max_length=50, choices=[
        ('documentation', 'Documentation'),
        ('idea', 'Idea'),
        ('solution', 'Solution'),
        ('question', 'Question'),
        ('research', 'Research'),
        ('experiment', 'Experiment'),
        ('rant', 'Rant'),
    ])
    categories = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    importance = models.CharField(max_length=20, choices=[
        ('critical', 'Critical'),
        ('high', 'High'),
        ('normal', 'Normal'),
        ('low', 'Low'),
    ], default='normal')
    
    # Enhanced Metadata (Phase 8 integration)
    topics = models.JSONField(default=list)
    entities_people = models.JSONField(default=list)
    entities_technologies = models.JSONField(default=list)
    entities_concepts = models.JSONField(default=list)
    mentioned_projects = models.JSONField(default=list)
    
    # Quality & Context Scores
    importance_score = models.FloatField(default=0.5)
    clarity_score = models.FloatField(null=True, blank=True)
    completeness_score = models.FloatField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)
    
    # Emotional Context (from location #1)
    emotional_context = models.CharField(max_length=50, choices=[
        ('frustrated', 'Frustrated'),
        ('excited', 'Excited'),
        ('confused', 'Confused'),
        ('breakthrough', 'Breakthrough'),
        ('stuck', 'Stuck'),
        ('neutral', 'Neutral'),
    ], default='neutral')
    
    # Status & Workflow
    is_archived = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], default='pending')
    processing_error = models.TextField(blank=True)
    
    # Access Metrics
    times_accessed = models.IntegerField(default=0)
    usefulness_score = models.FloatField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['project_name']),
            models.Index(fields=['file_modified_date']),
            models.Index(fields=['importance', 'quality_score']),
            models.Index(fields=['processing_status']),
        ]
        unique_together = ['user', 'file_path']
    
    def __str__(self):
        return f"{self.title} ({self.project_name})"


class MarkdownEmbedding(models.Model):
    """Embeddings for markdown content chunks - parallel to ConversationEmbedding"""
    
    # Core Relations
    document = models.ForeignKey(MarkdownDocument, on_delete=models.CASCADE, related_name='embeddings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Denormalized for performance
    
    # Chunk Information
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    chunk_type = models.CharField(max_length=20, choices=[
        ('title', 'Title'),
        ('summary', 'Summary'),
        ('content', 'Content'),
        ('code', 'Code Block'),
        ('list', 'List'),
        ('quote', 'Quote'),
    ], default='content')
    
    # Embedding Data
    embedding = VectorField(dimensions=1536)  # OpenAI embedding
    embedding_model = models.CharField(max_length=100, default='text-embedding-3-large')
    embedding_date = models.DateTimeField(auto_now_add=True)
    
    # Phase 8 Content Analysis Integration
    content_type = models.CharField(max_length=20, choices=[
        ('prose', 'Prose'),
        ('code', 'Code'),
        ('mixed', 'Mixed'),
        ('reference', 'Reference'),
    ], null=True, blank=True)
    prose_percentage = models.FloatField(null=True, blank=True)
    code_percentage = models.FloatField(null=True, blank=True)
    code_blocks = models.JSONField(default=list, blank=True)
    is_reference_dump = models.BooleanField(default=False)
    has_code_explanation = models.BooleanField(default=False)
    primary_content = models.TextField(null=True, blank=True)
    
    # Importance & Quality
    importance_score = models.FloatField(default=0.5)
    content_importance_score = models.FloatField(null=True, blank=True)
    semantic_cluster_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Metadata (compatible with ConversationEmbedding)
    topics = models.JSONField(default=list)
    entities = models.JSONField(default=list)
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    mentioned_people = models.JSONField(default=list)
    mentioned_projects = models.JSONField(default=list)
    mentioned_technologies = models.JSONField(default=list)
    
    # Content Flags
    has_code_snippets = models.BooleanField(default=False)
    has_urls = models.BooleanField(default=False)
    has_action_items = models.BooleanField(default=False)
    has_questions = models.BooleanField(default=False)
    has_decisions = models.BooleanField(default=False)
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    document_timestamp = models.DateTimeField()  # When the document was created
    
    class Meta:
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['importance_score']),
            models.Index(fields=['document_timestamp']),
            models.Index(fields=['is_reference_dump']),
            models.Index(fields=['has_code_explanation']),
        ]
        unique_together = ['document', 'chunk_index']


class DocumentIdea(models.Model):
    """Ideas extracted from documents - from location #1 schema"""
    
    document = models.ForeignKey(MarkdownDocument, on_delete=models.CASCADE, related_name='ideas')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Idea Content
    concept = models.CharField(max_length=500)
    description = models.TextField()
    context = models.TextField(blank=True)  # Surrounding text
    line_number = models.IntegerField(null=True, blank=True)
    
    # Idea Classification
    idea_type = models.CharField(max_length=20, choices=[
        ('initial', 'Initial'),
        ('evolution', 'Evolution'),
        ('refinement', 'Refinement'),
        ('abandonment', 'Abandonment'),
    ], default='initial')
    
    confidence_level = models.CharField(max_length=20, choices=[
        ('experimental', 'Experimental'),
        ('confident', 'Confident'),
        ('proven', 'Proven'),
        ('failed', 'Failed'),
    ], default='experimental')
    
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('implemented', 'Implemented'),
        ('abandoned', 'Abandoned'),
        ('superseded', 'Superseded'),
    ], default='active')
    
    # Temporal Tracking
    date_proposed = models.DateTimeField()
    date_updated = models.DateTimeField(auto_now=True)
    
    # Evolution Chain
    parent_idea = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    
    # Success Tracking
    success_indicators = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['concept']),
            models.Index(fields=['date_proposed']),
            models.Index(fields=['parent_idea']),
        ]


class DocumentSolution(models.Model):
    """Solutions and problem-solving patterns from documents"""
    
    document = models.ForeignKey(MarkdownDocument, on_delete=models.CASCADE, related_name='solutions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    related_idea = models.ForeignKey(DocumentIdea, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Problem & Solution
    problem_description = models.TextField()
    solution_approach = models.TextField()
    outcome = models.TextField(blank=True)
    
    outcome_type = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('failure', 'Failure'),
        ('unknown', 'Unknown'),
    ], default='unknown')
    
    # Technical Details
    technologies_used = models.JSONField(default=list)
    lessons_learned = models.TextField(blank=True)
    reproducible = models.BooleanField(default=True)
    
    # Timestamps
    date_attempted = models.DateTimeField()
    date_resolved = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'outcome_type']),
            models.Index(fields=['date_attempted']),
        ]


class DocumentRelationship(models.Model):
    """Cross-references and relationships between documents"""
    
    source_document = models.ForeignKey(MarkdownDocument, on_delete=models.CASCADE, related_name='outgoing_relationships')
    target_document = models.ForeignKey(MarkdownDocument, on_delete=models.CASCADE, related_name='incoming_relationships')
    
    relationship_type = models.CharField(max_length=20, choices=[
        ('similar_idea', 'Similar Idea'),
        ('builds_on', 'Builds On'),
        ('contradicts', 'Contradicts'),
        ('implements', 'Implements'),
        ('mentions', 'Mentions'),
        ('evolves_from', 'Evolves From'),
    ])
    
    context = models.TextField(blank=True)
    confidence_score = models.FloatField(default=1.0)
    discovered_date = models.DateTimeField(auto_now_add=True)
    
    # Auto-detection metadata
    auto_detected = models.BooleanField(default=True)
    detection_method = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['source_document', 'target_document', 'relationship_type']
        indexes = [
            models.Index(fields=['relationship_type']),
            models.Index(fields=['confidence_score']),
        ]
```

## 🔧 Service Architecture

### Unified Search Service

```python
class UnifiedKnowledgeSearch:
    """Single interface for searching across all content types"""
    
    def __init__(self):
        self.conversation_search = EnhancedMemorySearch()
        self.document_search = DocumentSearchService()
        self.content_processor = IntelligentContentProcessor()  # Phase 8 integration
    
    def search(
        self,
        user_id: int,
        query: str,
        content_types: List[str] = ['conversations', 'documents'],
        include_code: bool = None,  # Phase 8 content awareness
        time_window_days: int = None,
        limit: int = 20
    ) -> UnifiedSearchResults:
        """Universal search across all knowledge types"""
        
        # Detect query intent (Phase 8)
        is_code_query = self._detect_code_intent(query)
        if include_code is None:
            include_code = is_code_query
        
        results = []
        
        # Search conversations if requested
        if 'conversations' in content_types:
            conv_results = self.conversation_search.search_with_content_awareness(
                user_id=user_id,
                query=query,
                include_code=include_code
            )
            results.extend(self._format_conversation_results(conv_results))
        
        # Search documents if requested  
        if 'documents' in content_types:
            doc_results = self.document_search.search_documents(
                user_id=user_id,
                query=query,
                include_code=include_code
            )
            results.extend(self._format_document_results(doc_results))
        
        # Rank combined results
        ranked_results = self._rank_combined_results(results, query)
        
        return UnifiedSearchResults(
            results=ranked_results[:limit],
            total_conversations=sum(1 for r in results if r.type == 'conversation'),
            total_documents=sum(1 for r in results if r.type == 'document'),
            search_strategy={
                'query': query,
                'content_types': content_types,
                'include_code': include_code,
                'is_code_query': is_code_query
            }
        )
```

### Import Service Architecture

```python
class MarkdownImportService:
    """Import and process markdown files with rich metadata extraction"""
    
    def __init__(self):
        self.content_processor = IntelligentContentProcessor()  # Phase 8
        self.chunking_service = IntelligentChunkingService()    # Phase 8  
        self.metadata_extractor = CompleteMetadataExtractor()
        self.embedding_service = ContentAwareEmbeddingService()
    
    def import_directory(
        self, 
        directory_path: str, 
        user: User,
        category: str = None,
        project_name: str = None,
        dry_run: bool = False
    ) -> ImportResults:
        """Import all markdown files from a directory"""
        
        # 1. Discovery phase
        markdown_files = self._discover_markdown_files(directory_path)
        
        # 2. Processing phase  
        results = ImportResults()
        
        for file_path in markdown_files:
            try:
                # Process single file
                document = self._process_markdown_file(
                    file_path=file_path,
                    user=user,
                    category=category or self._auto_detect_category(file_path),
                    project_name=project_name or self._extract_project_name(file_path),
                    dry_run=dry_run
                )
                
                if document:
                    results.successful.append(document)
                    
            except Exception as e:
                results.failed.append({
                    'file_path': file_path,
                    'error': str(e)
                })
        
        return results
    
    def _process_markdown_file(self, file_path: str, user: User, category: str, project_name: str, dry_run: bool) -> MarkdownDocument:
        """Process a single markdown file with full metadata extraction"""
        
        # 1. Read and parse file
        content = self._read_markdown_file(file_path)
        file_stats = self._get_file_stats(file_path)
        
        # 2. Extract metadata using Phase 8 content analysis
        content_analysis = self.content_processor.process_content(content)
        metadata = self.metadata_extractor.extract_all_metadata(content, file_path)
        
        # 3. Create document record
        if not dry_run:
            document = MarkdownDocument.objects.create(
                user=user,
                file_path=file_path,
                file_name=file_stats['name'],
                project_name=project_name,
                category=category,
                title=metadata['title'],
                raw_content=content,
                processed_content=content_analysis.get('prose_content', content),
                summary=metadata['summary'],
                content_hash=file_stats['hash'],
                file_size=file_stats['size'],
                file_created_date=file_stats['created'],
                file_modified_date=file_stats['modified'],
                # ... all metadata fields
            )
            
            # 4. Create embeddings with Phase 8 content awareness
            self._create_embeddings(document, content_analysis)
            
            # 5. Extract ideas and solutions
            self._extract_ideas(document, content)
            self._extract_solutions(document, content)
            
            return document
        
        return None  # Dry run
```

## 🔗 Integration Points

### Phase 8 Content Analysis Integration

The new system will leverage the existing Phase 8 intelligent content processing:

```python
# Enhanced embedding service for documents
class DocumentEmbeddingService(ContentAwareEmbeddingPipeline):
    """Extends Phase 8 pipeline for markdown documents"""
    
    async def process_document(self, document: MarkdownDocument) -> List[MarkdownEmbedding]:
        """Process document using Phase 8 content-aware chunking"""
        
        # Use Phase 8 intelligent chunking
        chunks = self.chunking_service.create_chunks(
            document.processed_content,
            conversation_metadata={
                'document_type': document.category,
                'project_name': document.project_name,
                'file_path': document.file_path
            }
        )
        
        # Generate embeddings with content analysis
        embeddings = []
        for chunk in chunks:
            embedding_obj = MarkdownEmbedding.objects.create(
                document=document,
                user=document.user,
                chunk_text=chunk['text'],
                chunk_index=chunk['index'],
                content_type=chunk['content_type'],
                prose_percentage=chunk.get('analysis_metadata', {}).get('prose_percentage'),
                code_percentage=chunk.get('analysis_metadata', {}).get('code_percentage'),
                # ... all Phase 8 fields
            )
            embeddings.append(embedding_obj)
        
        return embeddings
```

### Memory Service Enhancement

```python
class UnifiedMemoryService:
    """Enhanced memory service that searches both conversations and documents"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.unified_search = UnifiedKnowledgeSearch()
    
    async def find_relevant_context(
        self,
        query: str,
        include_conversations: bool = True,
        include_documents: bool = True,
        limit: int = 10
    ) -> List[MemoryContext]:
        """Find relevant context from all knowledge sources"""
        
        content_types = []
        if include_conversations:
            content_types.append('conversations')
        if include_documents:
            content_types.append('documents')
        
        results = self.unified_search.search(
            user_id=self.user_id,
            query=query,
            content_types=content_types,
            limit=limit
        )
        
        # Convert to MemoryContext for backward compatibility
        memory_contexts = []
        for result in results.results:
            context = MemoryContext(
                content=result.content,
                conversation_id=result.source_id,
                relevance_score=result.relevance_score,
                metadata={
                    'source_type': result.type,  # 'conversation' or 'document'
                    'title': result.title,
                    'project': result.project_name,
                    'categories': result.categories,
                    'content_type': result.content_type,  # Phase 8
                },
                timestamp=result.timestamp
            )
            memory_contexts.append(context)
        
        return memory_contexts
```

## 📊 Migration Strategy

### Data Migration from Location #1

```python
class UKFDataMigrator:
    """Migrate data from existing UKF SQLite database to Django"""
    
    def migrate_all_data(self, ukf_db_path: str, user: User) -> MigrationResults:
        """Migrate all data from UKF SQLite to Django models"""
        
        conn = sqlite3.connect(ukf_db_path)
        
        # 1. Migrate files -> MarkdownDocument
        files_migrated = self._migrate_files(conn, user)
        
        # 2. Migrate file_content -> enhanced MarkdownDocument
        content_migrated = self._migrate_content(conn)
        
        # 3. Migrate ideas -> DocumentIdea
        ideas_migrated = self._migrate_ideas(conn, user)
        
        # 4. Migrate solutions -> DocumentSolution  
        solutions_migrated = self._migrate_solutions(conn, user)
        
        # 5. Migrate cross_references -> DocumentRelationship
        relationships_migrated = self._migrate_relationships(conn)
        
        # 6. Generate embeddings for all migrated content
        embeddings_created = self._generate_embeddings_for_migrated_content(user)
        
        return MigrationResults(
            files=files_migrated,
            ideas=ideas_migrated,
            solutions=solutions_migrated,
            relationships=relationships_migrated,
            embeddings=embeddings_created
        )
```

## 🎯 Success Criteria

### Technical Goals
- ✅ Single Django app containing all UKF functionality
- ✅ All 2,201 markdown files accessible via Django models
- ✅ Phase 8 content analysis applied to documents
- ✅ Unified search returning both conversations and documents
- ✅ Rich metadata preserved (ideas, solutions, relationships)
- ✅ Performance optimized with proper indexing

### User Experience Goals
- ✅ One search interface finds everything
- ✅ Context-aware results (prose vs code)
- ✅ Temporal tracking shows idea evolution
- ✅ Cross-references between conversations and documents
- ✅ Fast response times (<100ms for typical queries)

### Integration Goals
- ✅ Backward compatibility with existing memory services
- ✅ Agent integration works seamlessly
- ✅ Memory Palace integration enhanced
- ✅ No disruption to current conversation functionality

This unified architecture consolidates the best components from all three UKF locations while leveraging the Phase 8 content analysis system we just implemented. The result will be a comprehensive knowledge system with both conversations and documents searchable through a single, intelligent interface.

Ready to proceed to Phase 3: Create Django Models? 🚀