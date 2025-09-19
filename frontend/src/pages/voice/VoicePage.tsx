import { useState, useEffect, useRef } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { voiceService } from '../../services/voice.service';
import { toast } from 'react-hot-toast';
import { 
  MicrophoneIcon, 
  StopIcon, 
  PlayIcon, 
  PauseIcon,
  CloudArrowUpIcon,
  DocumentTextIcon,
  ClockIcon,
  SpeakerWaveIcon,
  TrashIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';

interface VoiceRecording {
  id: string;
  transcript: string;
  audio_url?: string;
  duration?: number;
  created_at: string;
  format?: string;
  speaker_labels?: any[];
}

export function VoicePage() {
  const [recordings, setRecordings] = useState<VoiceRecording[]>([]);
  const [loading, setLoading] = useState(true);
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [expandedRecording, setExpandedRecording] = useState<string | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadRecordings();
  }, []);

  const loadRecordings = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/voice/history/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'e7d2ae96885384ad8c66cfcd094f4f193629f227'}`
        }
      });
      const data = await response.json();
      
      if (data.recordings) {
        // Sort by newest first
        const sorted = data.recordings.sort((a: any, b: any) => 
          new Date(b.created_at || b.timestamp).getTime() - new Date(a.created_at || a.timestamp).getTime()
        );
        setRecordings(sorted);
      }
    } catch (error) {
      console.error('Failed to load recordings:', error);
      toast.error('Failed to load voice recordings');
    } finally {
      setLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
      };

      mediaRecorder.start();
      setRecording(true);
      toast.success('Recording started');
    } catch (error) {
      toast.error('Failed to access microphone');
      console.error(error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setRecording(false);
      toast.success('Recording stopped');
    }
  };

  const processRecording = async () => {
    if (!audioUrl && !selectedFile) {
      toast.error('No recording or file to process');
      return;
    }

    try {
      setProcessing(true);
      
      let audioFile: File;
      if (selectedFile) {
        audioFile = selectedFile;
      } else if (audioUrl) {
        const response = await fetch(audioUrl);
        const blob = await response.blob();
        audioFile = new File([blob], 'recording.webm', { type: 'audio/webm' });
      } else {
        throw new Error('No audio to process');
      }

      const result = await voiceService.transcribeAudio(audioFile);
      
      if (result.success) {
        toast.success('Transcription complete!');
        loadRecordings(); // Reload to show new transcription
        
        // Clear the recording
        setAudioUrl(null);
        setSelectedFile(null);
      } else {
        toast.error(result.error || 'Transcription failed');
      }
    } catch (error) {
      console.error('Processing error:', error);
      toast.error('Failed to process audio');
    } finally {
      setProcessing(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Check file type
      const validTypes = ['audio/mp3', 'audio/wav', 'audio/m4a', 'audio/webm', 'audio/ogg'];
      if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a|webm|ogg)$/i)) {
        toast.error('Please select a valid audio file (MP3, WAV, M4A, WebM, OGG)');
        return;
      }
      
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      toast.success(`Selected: ${file.name}`);
    }
  };

  const playAudio = (url: string, id: string) => {
    if (playingId === id) {
      // Pause if already playing
      if (audioRef.current) {
        audioRef.current.pause();
      }
      setPlayingId(null);
    } else {
      // Play new audio
      if (audioRef.current) {
        audioRef.current.pause();
      }
      
      audioRef.current = new Audio(url);
      audioRef.current.play();
      setPlayingId(id);
      
      audioRef.current.onended = () => {
        setPlayingId(null);
      };
    }
  };

  const deleteRecording = async (id: string) => {
    if (!confirm('Are you sure you want to delete this recording?')) {
      return;
    }
    
    try {
      // For now, just remove from local state
      // TODO: Add backend delete endpoint
      setRecordings(recordings.filter(r => r.id !== id));
      toast.success('Recording deleted');
    } catch (error) {
      toast.error('Failed to delete recording');
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Voice Studio</h1>
        <p className="text-muted-foreground mt-1">Record, transcribe, and manage voice content</p>
      </div>

      {/* Recording Controls */}
      <Card>
        <h2 className="text-xl font-semibold text-foreground mb-4">New Recording</h2>
        
        <div className="space-y-4">
          {/* Recording Buttons */}
          <div className="flex flex-wrap gap-3">
            {!recording ? (
              <Button onClick={startRecording} variant="primary">
                <MicrophoneIcon className="h-4 w-4" />
                Start Recording
              </Button>
            ) : (
              <Button onClick={stopRecording} variant="secondary">
                <StopIcon className="h-4 w-4" />
                Stop Recording
              </Button>
            )}
            
            <Button
              variant="secondary"
              onClick={() => fileInputRef.current?.click()}
            >
              <CloudArrowUpIcon className="h-4 w-4" />
              Upload Audio File
            </Button>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Audio Preview */}
          {audioUrl && (
            <div className="bg-card rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <SpeakerWaveIcon className="h-5 w-5 text-primary-400" />
                  <span className="text-sm text-muted-foreground">
                    {selectedFile ? selectedFile.name : 'New Recording'}
                  </span>
                </div>
                <audio controls src={audioUrl} className="max-w-xs" />
              </div>
              
              <div className="mt-3 flex gap-2">
                <Button
                  onClick={processRecording}
                  disabled={processing}
                  size="sm"
                >
                  {processing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <DocumentTextIcon className="h-4 w-4" />
                      Transcribe
                    </>
                  )}
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setAudioUrl(null);
                    setSelectedFile(null);
                  }}
                >
                  Clear
                </Button>
              </div>
            </div>
          )}

          {/* Recording Status */}
          {recording && (
            <div className="flex items-center gap-2 text-red-500">
              <div className="w-3 h-3 bg-red-400 rounded-full animate-pulse" />
              <span className="text-sm">Recording in progress...</span>
            </div>
          )}
        </div>
      </Card>

      {/* Recordings List */}
      <div>
        <h2 className="text-xl font-semibold text-foreground mb-4">
          Voice Recordings ({recordings.length})
        </h2>

        {recordings.length === 0 ? (
          <Card>
            <div className="text-center py-8">
              <MicrophoneIcon className="h-12 w-12 text-gray-600 mx-auto mb-3" />
              <p className="text-muted-foreground">No recordings yet</p>
              <p className="text-sm text-muted-foreground mt-1">
                Start recording or upload an audio file to get started
              </p>
            </div>
          </Card>
        ) : (
          <div className="space-y-3">
            {recordings.map((recording) => (
              <Card key={recording.id} hover>
                <div className="space-y-3">
                  {/* Recording Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className="p-2 bg-primary-500/10 rounded-lg">
                        <MicrophoneIcon className="h-5 w-5 text-primary-400" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-foreground">
                            Recording #{recording.id.slice(-6)}
                          </span>
                          {recording.duration && (
                            <span className="text-xs text-muted-foreground">
                              {formatDuration(recording.duration)}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <ClockIcon className="h-3 w-3" />
                            {formatDate(recording.created_at || recording.timestamp)}
                          </span>
                          {recording.format && (
                            <span>{recording.format}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {recording.audio_url && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => playAudio(recording.audio_url!, recording.id)}
                        >
                          {playingId === recording.id ? (
                            <PauseIcon className="h-4 w-4" />
                          ) : (
                            <PlayIcon className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                      
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setExpandedRecording(
                          expandedRecording === recording.id ? null : recording.id
                        )}
                      >
                        <DocumentTextIcon className="h-4 w-4" />
                        {expandedRecording === recording.id ? 'Hide' : 'View'} Transcript
                      </Button>
                      
                      {recording.audio_url && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => {
                            const a = document.createElement('a');
                            a.href = recording.audio_url!;
                            a.download = `recording-${recording.id}.wav`;
                            a.click();
                          }}
                        >
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        </Button>
                      )}
                      
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => deleteRecording(recording.id)}
                        className="text-red-500 hover:text-red-300"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Transcript */}
                  {expandedRecording === recording.id && (
                    <div className="bg-card rounded-lg p-4">
                      <h4 className="text-sm font-medium text-muted-foreground mb-2">Transcript</h4>
                      <div className="text-sm text-muted-foreground whitespace-pre-wrap">
                        {recording.transcript || 'No transcript available'}
                      </div>
                      
                      {recording.speaker_labels && recording.speaker_labels.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-border">
                          <h4 className="text-sm font-medium text-muted-foreground mb-2">
                            Speaker Breakdown
                          </h4>
                          {recording.speaker_labels.map((speaker: any, idx: number) => (
                            <div key={idx} className="mb-2">
                              <span className="text-xs text-primary-400">
                                {speaker.speaker}:
                              </span>
                              <p className="text-sm text-muted-foreground ml-4">
                                {speaker.text}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      <div className="mt-4 flex gap-2">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => {
                            navigator.clipboard.writeText(recording.transcript);
                            toast.success('Transcript copied to clipboard');
                          }}
                        >
                          Copy Transcript
                        </Button>
                        
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => {
                            // TODO: Generate content from transcript
                            toast.info('Content generation coming soon!');
                          }}
                        >
                          Generate Content
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}