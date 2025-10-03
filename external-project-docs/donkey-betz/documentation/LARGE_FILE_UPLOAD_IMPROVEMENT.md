# Large File Upload Architecture Improvements

## Current Issues with 100MB+ Files
1. **Synchronous Processing**: Backend processes each conversation sequentially
2. **No Progress Feedback**: User sees "uploading" but no real progress after upload
3. **Timeout Risk**: Frontend connection may timeout during processing
4. **Memory Usage**: Entire file loaded into memory at once
5. **No Resume**: If it fails, must start over from beginning

## Proposed Production Architecture

### Option 1: Background Processing with Celery (Recommended)
```python
# 1. Upload endpoint receives file
def import_chatgpt_conversations(request):
    file = request.FILES['file']
    
    # Save file to temporary storage
    temp_path = save_to_temp(file)
    
    # Create import job record
    import_job = ChatGPTImportJob.objects.create(
        user=request.user,
        file_path=temp_path,
        status='pending',
        total_conversations=0,
        processed_conversations=0
    )
    
    # Queue for background processing
    process_chatgpt_import.delay(import_job.id)
    
    # Return immediately with job ID
    return Response({
        'import_job_id': import_job.id,
        'status': 'processing',
        'message': 'Import started, check status for progress'
    })

# 2. Celery task processes in background
@shared_task
def process_chatgpt_import(job_id):
    job = ChatGPTImportJob.objects.get(id=job_id)
    
    # Stream parse the JSON file
    for conversation in stream_json_file(job.file_path):
        process_conversation(conversation)
        
        # Update progress
        job.processed_conversations += 1
        job.progress = (job.processed_conversations / job.total_conversations) * 100
        job.save()
        
        # Send WebSocket update
        send_progress_update(job.user_id, job.progress)
```

### Option 2: Chunked Upload with Streaming
```javascript
// Frontend chunks large file
async function uploadLargeFile(file) {
    const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks
    const chunks = Math.ceil(file.size / CHUNK_SIZE);
    
    // Initialize upload session
    const session = await api.post('/api/upload/init', {
        filename: file.name,
        size: file.size,
        chunks: chunks
    });
    
    // Upload chunks with progress
    for (let i = 0; i < chunks; i++) {
        const chunk = file.slice(i * CHUNK_SIZE, (i + 1) * CHUNK_SIZE);
        
        await api.post(`/api/upload/chunk/${session.id}`, chunk, {
            headers: {
                'X-Chunk-Index': i,
                'X-Total-Chunks': chunks
            },
            onUploadProgress: (e) => {
                const overallProgress = ((i * CHUNK_SIZE + e.loaded) / file.size) * 100;
                setProgress(overallProgress);
            }
        });
    }
    
    // Trigger processing after all chunks uploaded
    return api.post(`/api/upload/process/${session.id}`);
}
```

### Option 3: Direct S3/Cloud Upload
```javascript
// Get presigned URL from backend
const { uploadUrl, importId } = await api.get('/api/chatgpt/get-upload-url');

// Upload directly to S3
await axios.put(uploadUrl, file, {
    headers: { 'Content-Type': file.type },
    onUploadProgress: updateProgress
});

// Trigger processing
await api.post('/api/chatgpt/process-from-s3', { importId });
```

## WebSocket Progress Updates
```python
# consumers.py
class ImportProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.room_group_name = f'import_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def import_progress(self, event):
        await self.send(text_data=json.dumps({
            'type': 'import_progress',
            'progress': event['progress'],
            'processed': event['processed'],
            'total': event['total'],
            'status': event['status']
        }))
```

## Frontend Progress Display
```tsx
const ImportProgress: React.FC = () => {
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState('');
    
    useEffect(() => {
        const ws = new WebSocket(`ws://localhost:8001/ws/import-progress/`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setProgress(data.progress);
            setStatus(`Processing conversation ${data.processed}/${data.total}`);
        };
        
        return () => ws.close();
    }, []);
    
    return (
        <div>
            <ProgressBar value={progress} />
            <p>{status}</p>
        </div>
    );
};
```

## Database Schema for Import Jobs
```python
class ChatGPTImportJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ])
    total_conversations = models.IntegerField(default=0)
    processed_conversations = models.IntegerField(default=0)
    successful_imports = models.IntegerField(default=0)
    failed_imports = models.IntegerField(default=0)
    memories_created = models.IntegerField(default=0)
    progress = models.FloatField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def estimated_time_remaining(self):
        if self.processed_conversations == 0:
            return None
        elapsed = timezone.now() - self.started_at
        rate = self.processed_conversations / elapsed.total_seconds()
        remaining = self.total_conversations - self.processed_conversations
        return timedelta(seconds=remaining / rate)
```

## Benefits of Improved Architecture
1. **Non-blocking**: User can navigate away and come back
2. **Progress Tracking**: Real-time updates via WebSocket
3. **Resumable**: Can retry failed imports from where they left off
4. **Scalable**: Can process multiple imports in parallel
5. **Memory Efficient**: Streams file instead of loading all at once
6. **Better UX**: Shows time estimates, progress, and detailed status

## Implementation Priority
1. **Phase 1**: Add Celery background processing (1-2 days)
2. **Phase 2**: Add WebSocket progress updates (1 day)
3. **Phase 3**: Implement chunked upload (2-3 days)
4. **Phase 4**: Add S3/cloud storage option (1-2 days)

## Quick Win for Now
At minimum, we should:
1. Move processing to Celery task
2. Return job ID immediately
3. Add status endpoint to check progress
4. Show "processing in background" message

This would prevent timeouts and improve UX significantly even without full WebSocket integration.