import { useState, useRef, useEffect } from 'react';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { 
  MicrophoneIcon, 
  CloudArrowUpIcon,
  PlayIcon,
  StopIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
  UserGroupIcon,
  CommandLineIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  NewspaperIcon,
  HashtagIcon,
  BookOpenIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'sonner';
import { contentService } from '../../../services/content.service';
import { useNavigate } from 'react-router-dom';

interface VoiceTranscript {
  id: string;
  transcript: string;
  format: 'transcribe' | 'conversation' | 'command';
  speakers?: string[];
  created_at: string;
}

interface AudioRecording {
  blob: Blob;
  url: string;
  duration: number;
}

export function VoiceStudio() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'transcribe' | 'conversation' | 'command'>('transcribe');
  const [isRecording, setIsRecording] = useState(false);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [recordedAudio, setRecordedAudio] = useState<AudioRecording | null>(null);
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [history, setHistory] = useState<VoiceTranscript[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [audioLevel, setAudioLevel] = useState(0);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isCreatingContent, setIsCreatingContent] = useState(false);
  
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioContext = useRef<AudioContext | null>(null);
  const analyser = useRef<AnalyserNode | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recordingInterval = useRef<number | null>(null);
  const animationFrame = useRef<number | undefined>(undefined);

  const modes = [
    { id: 'transcribe', name: 'Transcribe', icon: DocumentTextIcon, desc: 'Convert speech to text' },
    { id: 'conversation', name: 'Conversation', icon: UserGroupIcon, desc: 'Format with speakers' },
    { id: 'command', name: 'Command', icon: CommandLineIcon, desc: 'Process voice commands' },
  ] as const;

  // Get available audio devices
  useEffect(() => {
    async function getDevices() {
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
        const deviceList = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = deviceList.filter(device => device.kind === 'audioinput');
        setDevices(audioInputs);
        if (audioInputs.length > 0 && !selectedDeviceId) {
          setSelectedDeviceId(audioInputs[0].deviceId);
        }
      } catch (error) {
        console.error('Error getting audio devices:', error);
        toast.error('Failed to access microphone');
      }
    }
    getDevices();
  }, [selectedDeviceId]);

  // Audio level monitoring
  const updateAudioLevel = () => {
    if (analyser.current && isRecording) {
      const dataArray = new Uint8Array(analyser.current.frequencyBinCount);
      analyser.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
      setAudioLevel(Math.min(100, (average / 255) * 100));
      animationFrame.current = requestAnimationFrame(updateAudioLevel);
    }
  };

  const startRecording = async () => {
    try {
      const constraints = {
        audio: {
          deviceId: selectedDeviceId ? { exact: selectedDeviceId } : undefined,
          sampleRate: 44100,
          channelCount: 1,
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      // Setup audio analysis
      audioContext.current = new AudioContext();
      analyser.current = audioContext.current.createAnalyser();
      const source = audioContext.current.createMediaStreamSource(stream);
      source.connect(analyser.current);
      
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      const chunks: BlobPart[] = [];
      
      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const url = URL.createObjectURL(blob);
        const duration = recordingTime;
        
        setRecordedAudio({ blob, url, duration });
        stream.getTracks().forEach(track => track.stop());
        
        if (audioContext.current) {
          audioContext.current.close();
        }
      };

      mediaRecorder.current.start(100);
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start recording timer
      recordingInterval.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      // Start audio level monitoring
      updateAudioLevel();
      
      toast.success('Recording started');
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Failed to start recording');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && mediaRecorder.current.state === 'recording') {
      mediaRecorder.current.stop();
    }
    
    setIsRecording(false);
    setAudioLevel(0);
    
    if (recordingInterval.current) {
      clearInterval(recordingInterval.current);
    }
    
    if (animationFrame.current) {
      cancelAnimationFrame(animationFrame.current);
    }
    
    toast.success('Recording stopped');
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const validTypes = ['audio/mpeg', 'audio/wav', 'audio/m4a', 'audio/webm', 'audio/ogg'];
      if (validTypes.includes(file.type) || file.name.match(/\.(mp3|wav|m4a|webm|ogg|mp4a)$/i)) {
        setAudioFile(file);
        setRecordedAudio(null);
        toast.success('Audio file uploaded');
      } else {
        toast.error('Please upload a valid audio file (MP3, WAV, M4A, WebM, OGG)');
      }
    }
  };

  const handleProcess = async () => {
    const audio = audioFile || (recordedAudio ? new File([recordedAudio.blob], 'recording.webm', { type: 'audio/webm' }) : null);
    
    if (!audio) {
      toast.error('Please record or upload an audio file first');
      return;
    }

    setIsProcessing(true);
    setTranscript('');

    try {
      let result;
      
      if (mode === 'transcribe') {
        result = await contentService.transcribeAudio(audio, 'transcript');
        console.log('Transcribe result:', result);
        setTranscript(result.original_text || result.transcript || result.text || '');
      } else if (mode === 'conversation') {
        result = await contentService.transcribeAudio(audio, 'conversation');
        console.log('Conversation result:', result);
        const processed = result.processed || {};
        setTranscript(processed.formatted_text || processed.formatted_conversation || result.original_text || result.transcript || '');
      } else if (mode === 'command') {
        result = await contentService.transcribeAudio(audio, 'command');
        console.log('Command result:', result);
        const processed = result.processed || {};
        setTranscript(processed.result || processed.action || result.original_text || 'Command processed successfully');
      }

      // Add to history
      const historyItem: VoiceTranscript = {
        id: result.id || Date.now().toString(),
        transcript: result.original_text || result.transcript || result.text || 'Processing completed',
        format: mode,
        speakers: result.processed?.speakers_detected ? [`${result.processed.speakers_detected} speakers`] : result.speakers,
        created_at: result.timestamp || new Date().toISOString(),
      };

      setHistory(prev => [historyItem, ...prev.slice(0, 9)]);
      toast.success(`Audio ${mode} completed!`);

    } catch (error: any) {
      console.error('Voice processing error:', error);
      toast.error(error.userMessage || `Failed to ${mode} audio`);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const clearAudio = () => {
    setAudioFile(null);
    setRecordedAudio(null);
    setTranscript('');
    setRecordingTime(0);
  };

  const playRecording = () => {
    if (recordedAudio) {
      const audio = new Audio(recordedAudio.url);
      audio.play().catch(e => console.error('Error playing audio:', e));
    }
  };

  const downloadRecording = () => {
    if (recordedAudio) {
      const link = document.createElement('a');
      link.href = recordedAudio.url;
      link.download = `voice-recording-${Date.now()}.webm`;
      link.click();
      toast.success('Download started');
    }
  };

  const createContentFromTranscript = async (contentType: 'blog' | 'social' | 'ebook' | 'summary') => {
    if (!transcript) {
      toast.error('No transcript available');
      return;
    }

    setIsCreatingContent(true);
    
    try {
      let result;
      
      switch (contentType) {
        case 'blog':
          // Generate blog from transcript
          toast.loading('Creating blog post from transcript...', { id: 'voice-to-blog' });
          result = await contentService.generateBlog({
            topic: transcript, // Use full transcript
            tone: 'professional',
            length: 'medium',
            target_audience: 'general',
            include_outline: true,
            use_memory: true,
          });
          
          if (result.success) {
            toast.dismiss('voice-to-blog');
            toast.success('Blog post created from transcript!');
            // Navigate to content library with the blog tab selected
            navigate('/gallery', { state: { activeTab: 'blogs', newBlogId: result.blog_id } });
          } else {
            toast.dismiss('voice-to-blog');
          }
          break;
          
        case 'social':
          // Generate social posts from transcript
          toast.loading('Creating social posts from transcript...', { id: 'voice-to-social' });
          result = await contentService.generateSocialPosts({
            topic: transcript, // Use full transcript
            platforms: ['twitter', 'linkedin', 'instagram'],
            tone: 'casual',
            variations_per_platform: 2,
          });
          
          if (result.success) {
            toast.dismiss('voice-to-social');
            toast.success('Social posts created from transcript!');
            navigate('/gallery', { state: { activeTab: 'social', newSocialId: result.post_id } });
          } else {
            toast.dismiss('voice-to-social');
          }
          break;
          
        case 'ebook':
          // For eBook, we'll just save the transcript as a draft
          toast.info('eBook generation from voice coming soon! Your transcript has been saved.');
          // Save to memory for later use
          await contentService.transcribeAudio(
            new File([transcript], 'transcript.txt', { type: 'text/plain' }),
            'memory'
          );
          break;
          
        case 'summary':
          // Generate a summary of the transcript
          result = await contentService.transcribeAudio(
            new File([transcript], 'transcript.txt', { type: 'text/plain' }),
            'summary'
          );
          
          if (result.processed) {
            setTranscript(result.processed);
            toast.success('Summary generated from transcript!');
          }
          break;
      }
    } catch (error: any) {
      console.error('Error creating content from transcript:', error);
      // Dismiss any loading toasts
      toast.dismiss('voice-to-blog');
      toast.dismiss('voice-to-social');
      
      // Show appropriate error message
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        toast.error(`Creating ${contentType} is taking longer than expected. Please try with a shorter transcript or try again later.`);
      } else {
        toast.error(error.userMessage || `Failed to create ${contentType} from transcript`);
      }
    } finally {
      setIsCreatingContent(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Mode Selection */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-4">Voice Processing Mode</h3>
        <div className="grid grid-cols-3 gap-4">
          {modes.map((modeOption) => {
            const isSelected = mode === modeOption.id;
            return (
              <button
                key={modeOption.id}
                onClick={() => setMode(modeOption.id)}
                className={`p-4 rounded-lg border-2 transition-all duration-200 text-center ${
                  isSelected
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-dark-700 hover:border-dark-600 hover:bg-white/5'
                }`}
              >
                <modeOption.icon className={`h-6 w-6 mx-auto mb-2 ${
                  isSelected ? 'text-primary-400' : 'text-gray-400'
                }`} />
                <div className={`font-medium mb-1 ${
                  isSelected ? 'text-white' : 'text-gray-300'
                }`}>
                  {modeOption.name}
                </div>
                <div className="text-xs text-gray-500">
                  {modeOption.desc}
                </div>
              </button>
            );
          })}
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recording & Upload Panel */}
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Audio Input</h3>
            {(audioFile || recordedAudio) && (
              <Button
                onClick={clearAudio}
                variant="secondary"
                size="sm"
              >
                <XMarkIcon className="h-4 w-4" />
                Clear
              </Button>
            )}
          </div>

          {/* Device Selection */}
          {devices.length > 1 && (
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">Microphone</label>
              <select 
                className="input text-sm"
                value={selectedDeviceId}
                onChange={(e) => setSelectedDeviceId(e.target.value)}
                disabled={isRecording}
              >
                {devices.map(device => (
                  <option key={device.deviceId} value={device.deviceId}>
                    {device.label || `Microphone ${device.deviceId.slice(0, 8)}`}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Recording Section */}
          <div className="text-center py-6 border-b border-dark-700 mb-6">
            <div className="relative inline-block">
              <button
                onClick={toggleRecording}
                disabled={isProcessing}
                className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200 ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                    : 'bg-primary-500 hover:bg-primary-600 disabled:opacity-50'
                }`}
              >
                {isRecording ? (
                  <StopIcon className="h-8 w-8 text-white" />
                ) : (
                  <MicrophoneIcon className="h-8 w-8 text-white" />
                )}
              </button>
              
              {/* Audio level indicator */}
              {isRecording && (
                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-16 h-1 bg-dark-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary-500 transition-all duration-75"
                    style={{ width: `${audioLevel}%` }}
                  />
                </div>
              )}
            </div>
            
            <p className="text-gray-400 mt-3">
              {isRecording 
                ? `Recording... ${formatTime(recordingTime)}` 
                : 'Click to start recording'
              }
            </p>
          </div>

          {/* File Upload */}
          <div className="text-center py-6">
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*,.m4a,.webm,.ogg,.mp4a"
              onChange={handleFileUpload}
              className="hidden"
            />
            <label 
              onClick={() => fileInputRef.current?.click()}
              className="cursor-pointer inline-flex items-center gap-2 px-6 py-3 bg-dark-800 hover:bg-dark-700 rounded-lg border border-dark-700 transition-colors"
            >
              <CloudArrowUpIcon className="h-5 w-5" />
              Upload Audio File
            </label>
            
            {audioFile && (
              <div className="mt-3 text-center">
                <p className="text-sm text-gray-400">{audioFile.name}</p>
                <p className="text-xs text-gray-500">
                  {(audioFile.size / 1024 / 1024).toFixed(1)} MB
                </p>
              </div>
            )}

            {recordedAudio && (
              <div className="mt-3 space-y-2">
                <p className="text-sm text-gray-400">
                  Recorded: {formatTime(recordedAudio.duration)}
                </p>
                <div className="flex justify-center gap-2">
                  <Button onClick={playRecording} size="sm" variant="secondary">
                    <PlayIcon className="h-4 w-4" />
                    Play
                  </Button>
                  <Button onClick={downloadRecording} size="sm" variant="secondary">
                    <ArrowDownTrayIcon className="h-4 w-4" />
                    Download
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Process Button */}
          <Button 
            onClick={handleProcess}
            loading={isProcessing}
            disabled={!audioFile && !recordedAudio}
            className="w-full"
          >
            <SpeakerWaveIcon className="h-4 w-4" />
            {isProcessing ? 'Processing...' : `${mode === 'transcribe' ? 'Transcribe' : mode === 'conversation' ? 'Format Conversation' : 'Process Command'}`}
          </Button>
        </Card>

        {/* Results Panel */}
        <Card>
          <h3 className="text-lg font-semibold text-white mb-4">
            {mode === 'transcribe' ? 'Transcription' : 
             mode === 'conversation' ? 'Conversation' : 
             'Command Result'}
          </h3>
          
          {isProcessing ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
              <span className="ml-3 text-gray-400">Processing audio...</span>
            </div>
          ) : transcript ? (
            <div className="space-y-4">
              <div className="bg-dark-900/50 rounded-lg p-4 border border-dark-700">
                <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono max-h-64 overflow-y-auto">
                  {transcript}
                </pre>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <Button
                  onClick={() => {
                    navigator.clipboard.writeText(transcript);
                    toast.success('Copied to clipboard');
                  }}
                  variant="secondary"
                  size="sm"
                >
                  Copy Text
                </Button>
                <Button
                  onClick={() => toast.info('Save functionality coming soon!')}
                  variant="secondary"
                  size="sm"
                >
                  Save to Memory
                </Button>
              </div>
              
              {/* Content Creation Actions */}
              <div className="mt-4 pt-4 border-t border-dark-700">
                <h4 className="text-sm font-medium text-white mb-3">Create Content From This Transcript</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <Button
                    onClick={() => createContentFromTranscript('blog')}
                    variant="secondary"
                    size="sm"
                    className="flex items-center gap-1"
                    disabled={isCreatingContent}
                  >
                    <NewspaperIcon className="h-4 w-4" />
                    Blog Post
                  </Button>
                  <Button
                    onClick={() => createContentFromTranscript('social')}
                    variant="secondary"
                    size="sm"
                    className="flex items-center gap-1"
                    disabled={isCreatingContent}
                  >
                    <HashtagIcon className="h-4 w-4" />
                    Social Posts
                  </Button>
                  <Button
                    onClick={() => createContentFromTranscript('ebook')}
                    variant="secondary"
                    size="sm"
                    className="flex items-center gap-1"
                    disabled={isCreatingContent}
                  >
                    <BookOpenIcon className="h-4 w-4" />
                    eBook
                  </Button>
                  <Button
                    onClick={() => createContentFromTranscript('summary')}
                    variant="secondary"
                    size="sm"
                    className="flex items-center gap-1"
                    disabled={isCreatingContent}
                  >
                    <SparklesIcon className="h-4 w-4" />
                    Summary
                  </Button>
                </div>
              </div>
            </div>
          ) : history.length > 0 ? (
            <div className="space-y-3">
              <h4 className="font-medium text-white flex items-center gap-2">
                <ClockIcon className="h-4 w-4" />
                Recent Processing
              </h4>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {history.map((item) => (
                  <div key={item.id} className="bg-dark-900/30 rounded p-3 border border-dark-700">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-xs text-gray-400 capitalize">
                        {item.format} • {new Date(item.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300 truncate">
                      {item.transcript.length > 100 
                        ? `${item.transcript.slice(0, 100)}...` 
                        : item.transcript}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <ChatBubbleLeftRightIcon className="h-16 w-16 mx-auto mb-4 text-gray-600" />
              <p>
                {mode === 'transcribe' ? 'Transcription will appear here' :
                 mode === 'conversation' ? 'Formatted conversation will appear here' :
                 'Command results will appear here'}
              </p>
              <p className="text-sm mt-2">
                Record or upload audio to get started
              </p>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}