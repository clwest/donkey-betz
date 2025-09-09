import React, { useState } from 'react';
import {
  UserGroupIcon,
  Square3Stack3DIcon,
  SparklesIcon,
  AdjustmentsHorizontalIcon,
  FolderIcon,
} from '@heroicons/react/24/outline';
import { CharacterLibrary } from '../../components/features/character/CharacterLibrary';
import { BatchGenerator } from '../../components/features/character/BatchGenerator';
import { CharacterMixer } from '../../components/features/character/CharacterMixer';
import { FineTuneControls } from '../../components/features/character/FineTuneControls';
import { CharacterCollections } from '../../components/features/character/CharacterCollections';

interface TabItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  component: React.ComponentType;
}

const tabs: TabItem[] = [
  {
    id: 'library',
    label: 'Library',
    icon: UserGroupIcon,
    component: CharacterLibrary,
  },
  {
    id: 'batch',
    label: 'Batch Generate',
    icon: Square3Stack3DIcon,
    component: BatchGenerator,
  },
  {
    id: 'mixer',
    label: 'Character Mixer',
    icon: SparklesIcon,
    component: CharacterMixer,
  },
  {
    id: 'finetune',
    label: 'Fine-Tune',
    icon: AdjustmentsHorizontalIcon,
    component: FineTuneControls,
  },
  {
    id: 'collections',
    label: 'Collections',
    icon: FolderIcon,
    component: CharacterCollections,
  },
];

export function CharacterPage() {
  const [activeTab, setActiveTab] = useState('library');
  const ActiveComponent = tabs.find(t => t.id === activeTab)?.component || CharacterLibrary;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gradient mb-2">
          Character Studio
        </h1>
        <p className="text-gray-400">
          Create and manage consistent characters across all your content
        </p>
      </div>

      {/* Tabs */}
      <div className="glass-dark rounded-2xl overflow-hidden">
        <div className="border-b border-white/5">
          <nav className="flex overflow-x-auto scrollbar-hide" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center gap-2 px-6 py-4 text-sm font-medium
                    transition-all duration-200 whitespace-nowrap
                    border-b-2 hover:bg-white/5
                    ${isActive 
                      ? 'text-primary-400 border-primary-400 bg-primary-400/10' 
                      : 'text-gray-400 border-transparent hover:text-white'
                    }
                  `}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          <ActiveComponent />
        </div>
      </div>
    </div>
  );
}