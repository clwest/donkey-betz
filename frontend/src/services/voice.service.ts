import { apiClient } from './api.config';

export interface VoiceGenerationRequest {
  text: string;
  voice?: string;
  stability?: number;
  similarity_boost?: number;
  model_id?: string;
  style?: 'professional' | 'conversational' | 'narrative' | 'news' | 'audiobook';
}

export interface VoiceResponse {
  success: boolean;
  audio_url?: string;
  duration?: number;
  error?: string;
}

export interface Voice {
  voice_id: string;
  name: string;
  preview_url?: string;
  category?: string;
  description?: string;
  accent?: string;
  age?: string;
  gender?: string;
  use_case?: string;
}

export const voiceService = {
  // Generate voice/narration from text
  async generateVoice(request: VoiceGenerationRequest): Promise<VoiceResponse> {
    const { data } = await apiClient.post('/api/v1/voice/generate/', request);
    return data;
  },

  // Get available voices
  async getVoices(): Promise<Voice[]> {
    const { data } = await apiClient.get('/api/v1/voice/voices/');
    return data.voices || [];
  },

  // Generate voiceover for video
  async generateVideoNarration(params: {
    script: string;
    video_id?: string;
    voice?: string;
    style?: string;
  }): Promise<VoiceResponse> {
    const { data } = await apiClient.post('/api/v1/voice/video-narration/', params);
    return data;
  },

  // Transcribe audio to text
  async transcribeAudio(audioFile: File, format = 'transcribe') {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('format', format);
    
    const { data } = await apiClient.post('/api/v1/voice/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};