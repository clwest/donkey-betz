import { apiClient } from './apiClient';
import { VoiceRecording, TranscriptionRequest, TranscriptionResponse, PaginatedResponse, ListParams } from '../types/api';

class VoiceService {
  // === VOICE TRANSCRIPTION ===

  // Transcribe audio file
  async transcribeAudio(
    audioFile: any, 
    options?: Partial<TranscriptionRequest>,
    onProgress?: (progress: number) => void
  ): Promise<TranscriptionResponse> {
    return await apiClient.uploadFile(
      '/voice/transcribe/',
      audioFile,
      'audio_file',
      {
        output_type: options?.output_type || 'transcript',
        speaker_diarization: options?.speaker_diarization || false,
      },
      onProgress
    );
  }

  // Process voice command (for voice-controlled content creation)
  async processVoiceCommand(audioFile: any): Promise<{
    command: string;
    parameters?: Record<string, any>;
    confidence: number;
    action: string;
  }> {
    return await apiClient.uploadFile(
      '/voice/command/',
      audioFile,
      'audio_file'
    );
  }

  // Get voice history/recordings
  async getVoiceHistory(params?: ListParams): Promise<PaginatedResponse<VoiceRecording>> {
    return await apiClient.get('/voice/history/', { params });
  }

  // Format transcript text (cleanup, punctuation, etc.)
  async formatTranscriptText(text: string, format?: 'clean' | 'paragraphs' | 'bullets'): Promise<{
    formatted_text: string;
    original_text: string;
    changes_made: string[];
  }> {
    return await apiClient.post('/voice/format-text/', { 
      text, 
      format: format || 'clean' 
    });
  }

  // === TEXT-TO-SPEECH (ELEVENLABS INTEGRATION) ===

  // Get available voices
  async getVoices(): Promise<{
    id: string;
    name: string;
    category: string;
    description: string;
    preview_url?: string;
    labels?: Record<string, string>;
  }[]> {
    return await apiClient.get('/voice/voices/');
  }

  // Get recommended voices for content type
  async getRecommendedVoices(contentType?: string): Promise<{
    voice_id: string;
    name: string;
    reason: string;
    preview_url?: string;
  }[]> {
    return await apiClient.get('/voice/recommended/', {
      params: { content_type: contentType }
    });
  }

  // Generate speech from text
  async generateSpeech(
    text: string,
    voiceId: string,
    options?: {
      stability?: number;
      similarity_boost?: number;
      style?: number;
      use_speaker_boost?: boolean;
    }
  ): Promise<{
    audio_url: string;
    duration: number;
    character_count: number;
    voice_id: string;
  }> {
    return await apiClient.post('/voice/generate/', {
      text,
      voice_id: voiceId,
      ...options,
    });
  }

  // Generate video narration
  async generateVideoNarration(
    script: string,
    voiceId: string,
    options?: {
      segments?: { text: string; timestamp: number }[];
      background_music?: boolean;
      volume_level?: number;
    }
  ): Promise<{
    narration_url: string;
    segments: { audio_url: string; start_time: number; duration: number }[];
    total_duration: number;
  }> {
    return await apiClient.post('/voice/video-narration/', {
      script,
      voice_id: voiceId,
      ...options,
    });
  }

  // Batch generate speech for multiple texts
  async batchGenerateSpeech(
    requests: {
      text: string;
      voice_id: string;
      filename?: string;
    }[],
    options?: {
      stability?: number;
      similarity_boost?: number;
      zip_output?: boolean;
    }
  ): Promise<{
    results: { filename: string; audio_url: string; duration: number }[];
    zip_url?: string;
    total_duration: number;
  }> {
    return await apiClient.post('/voice/batch/', {
      requests,
      ...options,
    });
  }

  // Check TTS API status
  async checkTTSStatus(): Promise<{
    available: boolean;
    character_limit: number;
    characters_used: number;
    reset_date: string;
  }> {
    return await apiClient.get('/voice/status/');
  }

  // === VOICE RECORDING MANAGEMENT ===

  // Get voice recording detail
  async getVoiceRecording(id: number): Promise<VoiceRecording> {
    return await apiClient.get(`/voice/recordings/${id}/`);
  }

  // Delete voice recording
  async deleteVoiceRecording(id: number): Promise<void> {
    await apiClient.delete(`/voice/recordings/${id}/`);
  }

  // Update voice recording metadata
  async updateVoiceRecording(id: number, updates: {
    title?: string;
    tags?: string[];
    notes?: string;
  }): Promise<VoiceRecording> {
    return await apiClient.patch(`/voice/recordings/${id}/`, updates);
  }

  // === VOICE-TO-CONTENT WORKFLOWS ===

  // Convert voice to blog post
  async voiceToBlog(
    audioFile: any,
    options?: {
      title?: string;
      style?: string;
      target_audience?: string;
      include_images?: boolean;
    }
  ): Promise<{
    transcript: string;
    blog_post: any;
    suggestions: string[];
  }> {
    return await apiClient.uploadFile(
      '/voice/to-blog/',
      audioFile,
      'audio_file',
      options
    );
  }

  // Convert voice to social media posts
  async voiceToSocial(
    audioFile: any,
    options?: {
      platforms?: string[];
      max_posts?: number;
      include_hashtags?: boolean;
    }
  ): Promise<{
    transcript: string;
    social_posts: any[];
    hashtags: string[];
  }> {
    return await apiClient.uploadFile(
      '/voice/to-social/',
      audioFile,
      'audio_file',
      options
    );
  }

  // Convert voice to summary
  async voiceToSummary(
    audioFile: any,
    options?: {
      summary_type?: 'brief' | 'detailed' | 'action_items';
      format?: 'paragraph' | 'bullets' | 'numbered';
    }
  ): Promise<{
    transcript: string;
    summary: string;
    key_points: string[];
    action_items?: string[];
  }> {
    return await apiClient.uploadFile(
      '/voice/to-summary/',
      audioFile,
      'audio_file',
      options
    );
  }

  // === VOICE ANALYTICS ===

  // Get voice usage statistics
  async getVoiceStats(): Promise<{
    total_recordings: number;
    total_duration: number;
    total_transcriptions: number;
    total_tts_characters: number;
    most_used_voices: { voice_id: string; name: string; usage_count: number }[];
    recent_activity: any[];
  }> {
    return await apiClient.get('/voice/stats/');
  }

  // Get transcript analysis
  async analyzeTranscript(transcriptId: number): Promise<{
    word_count: number;
    speaking_rate: number;
    sentiment: string;
    key_topics: string[];
    readability_score: number;
    suggestions: string[];
  }> {
    return await apiClient.get(`/voice/recordings/${transcriptId}/analyze/`);
  }
}

export const voiceService = new VoiceService();
export default voiceService;