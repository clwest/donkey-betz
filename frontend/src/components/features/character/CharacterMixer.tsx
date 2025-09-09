import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  TrashIcon,
  SparklesIcon,
  EyeIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { characterService } from '../../../services/character.service';
import type { CharacterProfile, CharacterMixRequest, CharacterMix, MixMethod } from '../../../types/character.types';
import { toast } from 'sonner';

interface MixCharacter {
  character: CharacterProfile;
  weight: number;
  features: string[];
}

export function CharacterMixer() {
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [selectedCharacters, setSelectedCharacters] = useState<MixCharacter[]>([]);
  const [mixName, setMixName] = useState('');
  const [mixMethod, setMixMethod] = useState<MixMethod>('weighted');
  const [loading, setLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [mixHistory, setMixHistory] = useState<CharacterMix[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [previewMix, setPreviewMix] = useState<string>('');

  const availableFeatures = [
    'hair', 'eyes', 'skin', 'clothing', 'accessories', 
    'age', 'gender', 'body', 'expression'
  ];

  useEffect(() => {
    loadCharacters();
    loadMixHistory();
  }, []);

  const loadCharacters = async () => {
    try {
      const data = await characterService.getLibrary({});
      setCharacters(data.characters);
    } catch (error) {
      console.error('Failed to load characters:', error);
      toast.error('Failed to load character library');
    }
  };

  const loadMixHistory = async () => {
    try {
      const data = await characterService.getMixHistory();
      setMixHistory(data.mixes);
    } catch (error) {
      // Silently handle missing mix history (expected when no mixes exist)
      if (error.response?.status === 404) {
        setMixHistory([]); // No mix history yet
      } else {
        console.error('Failed to load mix history:', error);
      }
    }
  };

  const addCharacter = (character: CharacterProfile) => {
    if (selectedCharacters.find(sc => sc.character.id === character.id)) {
      toast.error('Character already added to mix');
      return;
    }

    if (selectedCharacters.length >= 4) {
      toast.error('Maximum 4 characters can be mixed');
      return;
    }

    const mixCharacter: MixCharacter = {
      character,
      weight: 1.0 / (selectedCharacters.length + 1),
      features: [...availableFeatures]
    };

    // Rebalance weights
    const updatedCharacters = selectedCharacters.map(sc => ({
      ...sc,
      weight: sc.weight * selectedCharacters.length / (selectedCharacters.length + 1)
    }));

    setSelectedCharacters([...updatedCharacters, mixCharacter]);
  };

  const removeCharacter = (characterId: string) => {
    const updated = selectedCharacters.filter(sc => sc.character.id !== characterId);
    
    // Rebalance weights
    if (updated.length > 0) {
      const totalWeight = updated.reduce((sum, sc) => sum + sc.weight, 0);
      const rebalanced = updated.map(sc => ({
        ...sc,
        weight: sc.weight / totalWeight
      }));
      setSelectedCharacters(rebalanced);
    } else {
      setSelectedCharacters([]);
    }
  };

  const updateWeight = (characterId: string, weight: number) => {
    setSelectedCharacters(prev => 
      prev.map(sc => 
        sc.character.id === characterId 
          ? { ...sc, weight }
          : sc
      )
    );
  };

  const toggleFeature = (characterId: string, feature: string) => {
    setSelectedCharacters(prev =>
      prev.map(sc =>
        sc.character.id === characterId
          ? {
              ...sc,
              features: sc.features.includes(feature)
                ? sc.features.filter(f => f !== feature)
                : [...sc.features, feature]
            }
          : sc
      )
    );
  };

  const generatePreview = () => {
    if (selectedCharacters.length < 2) return;

    let preview = `Mixed character combining: `;
    
    selectedCharacters.forEach((sc, index) => {
      const percentage = Math.round(sc.weight * 100);
      preview += `${percentage}% ${sc.character.name}`;
      if (index < selectedCharacters.length - 1) {
        preview += ', ';
      }
    });

    preview += '\n\nFeatures from each character:\n';
    
    selectedCharacters.forEach(sc => {
      preview += `\n${sc.character.name} (${Math.round(sc.weight * 100)}%):\n`;
      sc.features.forEach(feature => {
        const featureValue = sc.character.features[feature];
        if (featureValue) {
          preview += `  ${feature}: ${featureValue}\n`;
        }
      });
    });

    setPreviewMix(preview);
    setShowPreview(true);
  };

  const mixCharacters = async () => {
    if (selectedCharacters.length < 2) {
      toast.error('At least 2 characters required for mixing');
      return;
    }

    if (!mixName.trim()) {
      toast.error('Please enter a name for the mixed character');
      return;
    }

    setIsGenerating(true);
    try {
      const request: CharacterMixRequest = {
        name: mixName.trim(),
        method: mixMethod,
        characters: selectedCharacters.map(sc => ({
          character_id: sc.character.id,
          weight: sc.weight,
          features: sc.features
        }))
      };

      const result = await characterService.mixCharacters(request);
      
      toast.success(`Mixed character "${result.name}" created successfully!`);
      setMixName('');
      setSelectedCharacters([]);
      loadMixHistory();
      
    } catch (error) {
      console.error('Failed to mix characters:', error);
      toast.error('Failed to create mixed character');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Character Mixer</h2>
          <p className="text-gray-400 mt-1">Mix features from multiple characters to create unique hybrids</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={generatePreview}
            disabled={selectedCharacters.length < 2}
          >
            <EyeIcon className="h-4 w-4" />
            Preview Mix
          </Button>
        </div>
      </div>

      {/* Mix Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Character Selection */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Select Characters to Mix</h3>
            
            <div className="grid grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {characters.map((character) => (
                <button
                  key={character.id}
                  onClick={() => addCharacter(character)}
                  disabled={selectedCharacters.find(sc => sc.character.id === character.id) !== undefined}
                  className={`
                    p-3 rounded-lg border text-left transition-all
                    ${selectedCharacters.find(sc => sc.character.id === character.id)
                      ? 'border-primary-500/50 bg-primary-500/10 text-gray-500'
                      : 'border-gray-700 hover:border-primary-500/50 bg-gray-800/50 text-white hover:bg-gray-700/50'
                    }
                  `}
                >
                  <div className="flex items-center gap-2">
                    {character.thumbnail_url && character.thumbnail_url.trim() !== '' ? (
                      <img
                        src={character.thumbnail_url}
                        alt={character.name}
                        className="w-8 h-8 rounded-full object-cover"
                        onError={(e) => {
                          // If image fails to load, hide it and show fallback
                          e.currentTarget.style.display = 'none';
                          const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                          if (fallback) fallback.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div 
                      className="w-8 h-8 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-xs font-bold"
                      style={{ display: character.thumbnail_url && character.thumbnail_url.trim() !== '' ? 'none' : 'flex' }}
                    >
                      {character.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{character.name}</div>
                      <div className="text-xs text-gray-400 truncate">{character.category}</div>
                    </div>
                    {selectedCharacters.find(sc => sc.character.id === character.id) && (
                      <CheckIcon className="h-4 w-4 text-primary-400" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </Card>

        {/* Mix Settings */}
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Mix Settings</h3>
            
            {/* Mix Name */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Mixed Character Name
              </label>
              <input
                type="text"
                value={mixName}
                onChange={(e) => setMixName(e.target.value)}
                placeholder="Enter name for mixed character..."
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Mix Method */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Mixing Method
              </label>
              <div className="space-y-2">
                {[
                  { value: 'weighted', label: 'Weighted Average', desc: 'Blend based on weights' },
                  { value: 'selective', label: 'Selective Features', desc: 'Pick specific features from each' },
                  { value: 'random', label: 'Random Mix', desc: 'Random combination' }
                ].map((method) => (
                  <label key={method.value} className="flex items-center gap-3">
                    <input
                      type="radio"
                      value={method.value}
                      checked={mixMethod === method.value}
                      onChange={(e) => setMixMethod(e.target.value as MixMethod)}
                      className="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                    />
                    <div>
                      <div className="text-sm font-medium text-white">{method.label}</div>
                      <div className="text-xs text-gray-400">{method.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Selected Characters */}
      {selectedCharacters.length > 0 && (
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Selected Characters ({selectedCharacters.length}/4)</h3>
              <Button
                onClick={mixCharacters}
                disabled={selectedCharacters.length < 2 || !mixName.trim() || isGenerating}
                loading={isGenerating}
              >
                <SparklesIcon className="h-4 w-4" />
                {isGenerating ? 'Creating Mix...' : 'Mix Characters'}
              </Button>
            </div>

            <div className="space-y-4">
              {selectedCharacters.map((sc) => (
                <div key={sc.character.id} className="border border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {sc.character.thumbnail_url && sc.character.thumbnail_url.trim() !== '' ? (
                        <img
                          src={sc.character.thumbnail_url}
                          alt={sc.character.name}
                          className="w-10 h-10 rounded-full object-cover"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                            if (fallback) fallback.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div 
                        className="w-10 h-10 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-sm font-bold"
                        style={{ display: sc.character.thumbnail_url && sc.character.thumbnail_url.trim() !== '' ? 'none' : 'flex' }}
                      >
                        {sc.character.name.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium text-white">{sc.character.name}</div>
                        <div className="text-sm text-gray-400">{sc.character.category}</div>
                      </div>
                    </div>
                    <button
                      onClick={() => removeCharacter(sc.character.id)}
                      className="text-red-400 hover:text-red-300 p-1"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Weight Slider */}
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium text-gray-300">Weight</label>
                      <span className="text-sm text-primary-400">{Math.round(sc.weight * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0.1"
                      max="1"
                      step="0.1"
                      value={sc.weight}
                      onChange={(e) => updateWeight(sc.character.id, parseFloat(e.target.value))}
                      className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  {/* Feature Selection */}
                  {mixMethod === 'selective' && (
                    <div>
                      <label className="text-sm font-medium text-gray-300 mb-2 block">Features to Use</label>
                      <div className="grid grid-cols-3 gap-2">
                        {availableFeatures.map((feature) => (
                          <label key={feature} className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={sc.features.includes(feature)}
                              onChange={() => toggleFeature(sc.character.id, feature)}
                              className="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                            />
                            <span className="text-sm text-gray-300 capitalize">{feature}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Mix History */}
      {mixHistory.length > 0 && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Mixed Characters</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {mixHistory.slice(0, 6).map((mix) => (
                <div key={mix.id} className="border border-gray-700 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-sm font-bold">
                      {mix.name.slice(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-white truncate">{mix.name}</div>
                      <div className="text-sm text-gray-400">
                        {mix.source_characters.length} characters mixed
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-400 space-y-1">
                    {mix.source_characters.map((source, index) => (
                      <div key={index}>
                        {Math.round(source.weight * 100)}% {source.character_name}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-lg p-6 max-w-2xl w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Mix Preview</h3>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-400 hover:text-white"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 max-h-96 overflow-y-auto">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap">{previewMix}</pre>
            </div>
            
            <div className="flex justify-end mt-4">
              <Button onClick={() => setShowPreview(false)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}