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
    <div className="space-y-8" style={{ backgroundColor: 'var(--gaming-bg-primary)', minHeight: '100vh' }}>
      {/* Header - Gaming Style */}
      <div className="gaming-neural-card p-6">
        <div className="gaming-border-glow"></div>
        <div className="relative z-10 flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-black font-mono uppercase tracking-wider" 
                style={{ 
                  color: 'var(--gaming-neon-cyan)',
                  textShadow: '0 0 20px rgba(0, 255, 255, 0.5)'
                }}>NEURAL CREATION STUDIO</h1>
            <p className="mt-3 font-mono" style={{ color: 'var(--gaming-text-secondary)' }}>
              PROFESSIONAL AI-POWERED CONTENT FORGE
            </p>
          </div>
          <button
            className="gaming-btn-secondary px-6 py-3 rounded-xl font-mono font-bold text-sm uppercase tracking-wider flex items-center gap-2 transition-all duration-300 hover:scale-105"
            style={{
              background: 'var(--gaming-bg-elevated)',
              border: '1px solid var(--gaming-neon-purple)',
              color: 'var(--gaming-neon-purple)'
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
              className={`gaming-neural-card p-6 cursor-pointer transition-all duration-300 hover:scale-105 ${
                isActive ? 'ring-2' : ''
              }`}
              style={{
                borderColor: isActive ? 'var(--gaming-neon-cyan)' : 'var(--gaming-border)',
                boxShadow: isActive ? 'var(--gaming-glow-primary)' : undefined,
                background: isActive ? 'var(--gaming-gradient-primary)' : undefined
              }}
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="gaming-border-glow"></div>
              <div className="relative z-10 text-center">
                <tab.icon className={`h-8 w-8 mx-auto mb-3`} 
                  style={{ 
                    color: isActive ? 'var(--gaming-text-primary)' : 'var(--gaming-text-secondary)',
                    filter: isActive ? 'drop-shadow(0 0 8px rgba(0, 255, 255, 0.6))' : undefined
                  }} />
                <h3 className={`font-bold font-mono uppercase tracking-wider text-sm mb-2`}
                    style={{ 
                      color: isActive ? 'var(--gaming-text-primary)' : 'var(--gaming-text-secondary)'
                    }}>
                  {tab.label}
                </h3>
                <p className={`text-xs font-mono`}
                   style={{ 
                     color: isActive ? 'var(--gaming-text-secondary)' : 'var(--gaming-text-muted)'
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