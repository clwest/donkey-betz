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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white">Creation Studio</h1>
          <p className="text-gray-400 mt-1">Professional AI-powered content creation suite</p>
        </div>
        <Button variant="secondary">
          <PlusIcon className="h-4 w-4" />
          Save Preset
        </Button>
      </div>

      {/* Enhanced Tab Navigation */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <Card
              key={tab.id}
              className={`cursor-pointer transition-all duration-300 ${
                isActive 
                  ? 'bg-gradient-primary border-primary-500/50 shadow-lg shadow-primary-500/20' 
                  : 'hover:bg-white/5 hover:border-white/20'
              }`}
              onClick={() => setActiveTab(tab.id)}
            >
              <div className="text-center">
                <tab.icon className={`h-8 w-8 mx-auto mb-3 ${
                  isActive ? 'text-white' : 'text-gray-400'
                }`} />
                <h3 className={`font-semibold mb-1 ${
                  isActive ? 'text-white' : 'text-gray-300'
                }`}>
                  {tab.label}
                </h3>
                <p className={`text-xs ${
                  isActive ? 'text-gray-200' : 'text-gray-500'
                }`}>
                  {tab.description}
                </p>
              </div>
            </Card>
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