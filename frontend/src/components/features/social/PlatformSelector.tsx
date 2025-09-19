import React from 'react';
import type { Platform } from './types';

interface PlatformSelectorProps {
  platforms: Platform[];
  onPlatformToggle: (platformId: string) => void;
}

const PlatformSelector: React.FC<PlatformSelectorProps> = ({ platforms, onPlatformToggle }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
      {platforms.map((platform) => (
        <label
          key={platform.id}
          className={`
            relative flex items-center justify-center p-4 rounded-xl border-2 cursor-pointer 
            transition-all duration-300 transform hover:scale-105
            ${platform.selected 
              ? `${platform.color} shadow-lg` 
              : 'border-border bg-card/50 hover:bg-card hover:border-dark-600'
            }
          `}
        >
          <input
            type="checkbox"
            checked={platform.selected}
            onChange={() => onPlatformToggle(platform.id)}
            className="sr-only"
          />
          {platform.selected && (
            <div className="absolute top-2 right-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            </div>
          )}
          <div className="flex flex-col items-center gap-2">
            <span className="text-3xl">{platform.icon}</span>
            <span className={`text-xs font-medium ${platform.selected ? 'text-foreground' : 'text-muted-foreground'}`}>
              {platform.name}
            </span>
            <span className={`text-xs ${platform.selected ? 'text-foreground' : 'text-muted-foreground'}`}>
              {platform.charLimit.toLocaleString()} chars
            </span>
          </div>
        </label>
      ))}
    </div>
  );
};

export default PlatformSelector;