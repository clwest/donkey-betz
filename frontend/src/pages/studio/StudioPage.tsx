import { useState } from 'react';
import { 
  SparklesIcon, 
  PhotoIcon, 
  VideoCameraIcon,
  MicrophoneIcon,
  Cog6ToothIcon,
  PlusIcon,
  HashtagIcon,
} from '@heroicons/react/24/outline';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { TextGenerator } from '../../components/features/content-generation/TextGenerator';
import { ImageGenerator } from '../../components/features/content-generation/ImageGenerator';
import { VideoGenerator } from '../../components/features/content-generation/VideoGenerator';
import { ImageEditor } from '../../components/features/content-generation/ImageEditor';
import { VoiceStudio } from '../../components/features/voice-studio/VoiceStudio';
import { SocialMediaGenerator } from '../../components/features/social';

type StudioTab = 'text' | 'image' | 'video' | 'edit' | 'voice' | 'social';

export function StudioPage() {
  const [activeTab, setActiveTab] = useState<StudioTab>('text');

  const tabs = [
    { id: 'text' as const, label: 'Text', icon: SparklesIcon, description: 'Generate articles, blogs, and copy' },
    { id: 'social' as const, label: 'Social', icon: HashtagIcon, description: 'Multi-platform social posts' },
    { id: 'image' as const, label: 'Images', icon: PhotoIcon, description: 'Create stunning visuals with AI' },
    { id: 'video' as const, label: 'Videos', icon: VideoCameraIcon, description: 'Generate videos from text or images' },
    { id: 'edit' as const, label: 'Edit', icon: Cog6ToothIcon, description: 'Advanced image editing tools' },
    { id: 'voice' as const, label: 'Voice', icon: MicrophoneIcon, description: 'Voice recording and processing' },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'text':
        return <TextGenerator />;
      case 'social':
        return <SocialMediaGenerator />;
      case 'image':
        return <ImageGenerator />;
      case 'video':
        return <VideoGenerator />;
      case 'edit':
        return <ImageEditor />;
      case 'voice':
        return <VoiceStudio />;
      default:
        return <TextGenerator />;
    }
  };

  return (
    <div className="space-y-8" style={{ backgroundColor: 'hsl(var(--muted))', minHeight: '100vh' }}>
      {/* Header - Gaming Style */}
      <div className="bg-card p-6">
        <div className="bg-card"></div>
        <div className="relative z-10 flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-black font-mono uppercase tracking-wider" 
                style={{ 
                  color: 'hsl(var(--muted))',
                  textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
                }}>NEURAL CREATION STUDIO</h1>
            <p className="mt-3 font-mono" style={{ color: 'hsl(var(--muted))' }}>
              PROFESSIONAL AI-POWERED CONTENT FORGE
            </p>
          </div>
          <button
            className="bg-card px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider flex items-center gap-2 transition-all duration-300 hover:scale-105"
            style={{
              background: 'hsl(var(--muted))',
              border: '1px solid hsl(var(--muted))',
              color: 'hsl(var(--muted))'
            }}
          >
            <PlusIcon className="h-4 w-4" />
            SAVE PRESET
          </button>
        </div>
      </div>

      {/* Neural Tab Matrix */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <div
              key={tab.id}
              className={`bg-card p-6 cursor-pointer transition-all duration-300 hover:scale-105 ${
                isActive ? 'ring-2' : ''
              }`}
              style={{
                borderColor: isActive ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                boxShadow: isActive ? 'hsl(var(--muted))' : undefined,
                background: isActive ? 'hsl(var(--muted))' : undefined
              }}
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="bg-card"></div>
              <div className="relative z-10 text-center">
                <tab.icon className={`h-8 w-8 mx-auto mb-3`} 
                  style={{ 
                    color: isActive ? 'hsl(var(--muted))' : 'hsl(var(--muted))',
                    filter: isActive ? 'drop-shadow(0 0 8px rgba(0, 255, 255, 0.6))' : undefined
                  }} />
                <h3 className={`font-bold font-mono uppercase tracking-wider text-sm mb-2`}
                    style={{ 
                      color: isActive ? 'hsl(var(--muted))' : 'hsl(var(--muted))'
                    }}>
                  {tab.label}
                </h3>
                <p className={`text-xs font-mono`}
                   style={{ 
                     color: isActive ? 'hsl(var(--muted))' : 'hsl(var(--muted))'
                   }}>
                  {tab.description.toUpperCase()}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="animate-in">
        {renderTabContent()}
      </div>
    </div>
  );
}