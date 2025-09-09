import React, { useState, useEffect } from 'react';
import {
  AdjustmentsHorizontalIcon,
  SparklesIcon,
  ArrowPathIcon,
  EyeIcon,
  BookmarkIcon,
  ClockIcon,
  Cog6ToothIcon,
  PlusIcon,
} from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { characterService } from '../../../services/character.service';
import type { CharacterProfile, FineTuneRequest } from '../../../types/character.types';
import { toast } from 'sonner';
import { getFullMediaURL } from '../../../services/api.config';

interface FineTuneSettings {
  character_id: string;
  scene: string;
  variation_strength: number;
  seed_offset: number;
  cfg_scale_adjustment: number;
  style_mix: string;
  feature_overrides: {
    hair?: string;
    eyes?: string;
    skin?: string;
    clothing?: string;
    accessories?: string;
    age?: string;
    expression?: string;
  };
}

const presetScenes = [
  'standing confidently',
  'walking in a garden',
  'sitting at a cafe',
  'running through snow',
  'dancing gracefully',
  'reading a book',
  'looking at sunset',
  'in a magical forest',
  'on a city rooftop',
  'by the ocean waves'
];

const styleMixes = [
  { value: '', label: 'Original Style' },
  { value: 'photography', label: 'Photographic' },
  { value: 'oil_painting', label: 'Oil Painting' },
  { value: 'watercolor', label: 'Watercolor' },
  { value: 'anime', label: 'Anime Style' },
  { value: 'sketch', label: 'Pencil Sketch' },
  { value: 'digital_art', label: 'Digital Art' },
  { value: 'vintage', label: 'Vintage Film' },
  { value: 'cyberpunk', label: 'Cyberpunk' },
  { value: 'fantasy', label: 'Fantasy Art' }
];

export function FineTuneControls() {
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<CharacterProfile | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationHistory, setGenerationHistory] = useState<any[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState<string>('');

  const [settings, setSettings] = useState<FineTuneSettings>({
    character_id: '',
    scene: '',
    variation_strength: 1.0,
    seed_offset: 0,
    cfg_scale_adjustment: 0,
    style_mix: '',
    feature_overrides: {}
  });

  useEffect(() => {
    loadCharacters();
    loadVariationHistory();
  }, []);

  useEffect(() => {
    if (selectedCharacter) {
      loadVariationHistory(selectedCharacter.id);
    }
  }, [selectedCharacter]);

  const loadCharacters = async () => {
    try {
      const data = await characterService.getLibrary({});
      setCharacters(data.characters);
      if (data.characters.length > 0 && !selectedCharacter) {
        setSelectedCharacter(data.characters[0]);
        setSettings(prev => ({ ...prev, character_id: data.characters[0].id }));
      }
    } catch (error) {
      console.error('Failed to load characters:', error);
      toast.error('Failed to load character library');
    }
  };

  const loadVariationHistory = async (characterId?: string) => {
    try {
      const data = await characterService.getCharacterVariations(characterId);
      setGenerationHistory(data.variations || []);
    } catch (error) {
      console.error('Failed to load variation history:', error);
    }
  };

  const selectCharacter = (character: CharacterProfile) => {
    setSelectedCharacter(character);
    setSettings(prev => ({
      ...prev,
      character_id: character.id,
      feature_overrides: {} // Reset overrides when switching characters
    }));
  };

  const updateSetting = <K extends keyof FineTuneSettings>(
    key: K,
    value: FineTuneSettings[K]
  ) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const updateFeatureOverride = (feature: string, value: string) => {
    setSettings(prev => ({
      ...prev,
      feature_overrides: {
        ...prev.feature_overrides,
        [feature]: value || undefined
      }
    }));
  };

  const generatePreview = () => {
    if (!selectedCharacter) return;

    let preview = `Fine-tuned variation of "${selectedCharacter.name}":\n\n`;
    preview += `Base Character:\n`;
    preview += `- Description: ${selectedCharacter.description}\n`;
    preview += `- Category: ${selectedCharacter.category}\n`;
    preview += `- Base Seed: ${selectedCharacter.seed}\n\n`;

    preview += `Fine-Tune Adjustments:\n`;
    if (settings.scene) {
      preview += `- Scene: ${settings.scene}\n`;
    }
    preview += `- Variation Strength: ${settings.variation_strength}x\n`;
    preview += `- Seed Offset: ${settings.seed_offset > 0 ? '+' : ''}${settings.seed_offset}\n`;
    preview += `- CFG Scale: ${selectedCharacter.cfg_scale}${settings.cfg_scale_adjustment > 0 ? '+' : ''}${settings.cfg_scale_adjustment}\n`;
    
    if (settings.style_mix) {
      const style = styleMixes.find(s => s.value === settings.style_mix);
      preview += `- Style Mix: ${style?.label}\n`;
    }

    const overrides = Object.entries(settings.feature_overrides).filter(([_, value]) => value);
    if (overrides.length > 0) {
      preview += `\nFeature Overrides:\n`;
      overrides.forEach(([feature, value]) => {
        preview += `- ${feature}: ${value}\n`;
      });
    }

    preview += `\nExpected Result:\n`;
    preview += `- Adjusted Seed: ${selectedCharacter.seed + settings.seed_offset}\n`;
    preview += `- Final CFG: ${selectedCharacter.cfg_scale + settings.cfg_scale_adjustment}\n`;
    preview += `- Variation Level: ${settings.variation_strength === 0.5 ? 'Subtle' : settings.variation_strength === 1.0 ? 'Normal' : settings.variation_strength === 1.5 ? 'Strong' : 'Custom'}\n`;

    setPreviewData(preview);
    setShowPreview(true);
  };

  const generateFineTunedVariation = async () => {
    if (!selectedCharacter) {
      toast.error('Please select a character first');
      return;
    }

    setIsGenerating(true);
    try {
      const request: FineTuneRequest = {
        character_id: settings.character_id,
        scene: settings.scene || undefined,
        variation_strength: settings.variation_strength,
        feature_overrides: Object.keys(settings.feature_overrides).length > 0 
          ? settings.feature_overrides 
          : undefined,
        seed_offset: settings.seed_offset !== 0 ? settings.seed_offset : undefined,
        cfg_scale_adjustment: settings.cfg_scale_adjustment !== 0 ? settings.cfg_scale_adjustment : undefined,
        style_mix: settings.style_mix || undefined
      };

      const result = await characterService.fineTuneVariation(request);
      
      toast.success('Fine-tuned variation generated successfully!');
      
      // Refresh variation history to show the new generation
      await loadVariationHistory(selectedCharacter.id);
      
    } catch (error) {
      console.error('Failed to generate fine-tuned variation:', error);
      toast.error('Failed to generate variation');
    } finally {
      setIsGenerating(false);
    }
  };

  const resetSettings = () => {
    setSettings({
      character_id: selectedCharacter?.id || '',
      scene: '',
      variation_strength: 1.0,
      seed_offset: 0,
      cfg_scale_adjustment: 0,
      style_mix: '',
      feature_overrides: {}
    });
  };

  const saveAsPreset = () => {
    const presetName = prompt('Enter a name for this preset:');
    if (!presetName) return;

    const preset = {
      name: presetName,
      settings: { ...settings },
      created_at: new Date().toISOString()
    };

    // Save to localStorage for now (could be moved to backend)
    const savedPresets = JSON.parse(localStorage.getItem('fineTunePresets') || '[]');
    savedPresets.unshift(preset);
    localStorage.setItem('fineTunePresets', JSON.stringify(savedPresets.slice(0, 10)));
    
    toast.success(`Preset "${presetName}" saved successfully!`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Fine-Tune Controls</h2>
          <p className="text-gray-400 mt-1">Precise control over character variations and generation parameters</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={generatePreview} disabled={!selectedCharacter}>
            <EyeIcon className="h-4 w-4" />
            Preview Settings
          </Button>
          <Button variant="secondary" onClick={saveAsPreset} disabled={!selectedCharacter}>
            <BookmarkIcon className="h-4 w-4" />
            Save Preset
          </Button>
        </div>
      </div>

      {/* Character Selection */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Select Character</h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {characters.map((character) => (
              <button
                key={character.id}
                onClick={() => selectCharacter(character)}
                className={`
                  p-4 rounded-lg border text-left transition-all
                  ${selectedCharacter?.id === character.id
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-gray-700 hover:border-primary-500/50 bg-gray-800/50 hover:bg-gray-700/50'
                  }
                `}
              >
                <div className="flex items-center gap-3 mb-2">
                  {character.thumbnail_url && character.thumbnail_url.trim() !== '' ? (
                    <img
                      src={character.thumbnail_url}
                      alt={character.name}
                      className="w-10 h-10 rounded-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                        const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                        if (fallback) fallback.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div 
                    className="w-10 h-10 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-sm font-bold text-white"
                    style={{ display: character.thumbnail_url && character.thumbnail_url.trim() !== '' ? 'none' : 'flex' }}
                  >
                    {character.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-white truncate">{character.name}</div>
                    <div className="text-sm text-gray-400 truncate">{character.category}</div>
                  </div>
                </div>
                
                <div className="text-xs text-gray-500 space-y-1">
                  <div>Seed: {character.seed}</div>
                  <div>CFG: {character.cfg_scale}</div>
                  <div>Used: {character.usage_count} times</div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Fine-Tune Settings */}
      {selectedCharacter && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Scene & Basic Settings */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Scene & Variation</h3>
              
              <div className="space-y-4">
                {/* Scene Input */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Scene Description
                  </label>
                  <input
                    type="text"
                    value={settings.scene}
                    onChange={(e) => updateSetting('scene', e.target.value)}
                    placeholder="Enter scene description..."
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <div className="flex flex-wrap gap-2 mt-2">
                    {presetScenes.slice(0, 5).map((scene) => (
                      <button
                        key={scene}
                        onClick={() => updateSetting('scene', scene)}
                        className="px-2 py-1 bg-gray-700 text-xs text-gray-300 rounded hover:bg-gray-600 transition-colors"
                      >
                        {scene}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Variation Strength */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-300">Variation Strength</label>
                    <span className="text-sm text-primary-400">{settings.variation_strength}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.1"
                    max="2.0"
                    step="0.1"
                    value={settings.variation_strength}
                    onChange={(e) => updateSetting('variation_strength', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Subtle</span>
                    <span>Normal</span>
                    <span>Strong</span>
                  </div>
                </div>

                {/* Style Mix */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Style Mix
                  </label>
                  <select
                    value={settings.style_mix}
                    onChange={(e) => updateSetting('style_mix', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    {styleMixes.map((style) => (
                      <option key={style.value} value={style.value}>
                        {style.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </Card>

          {/* Advanced Parameters */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Advanced Parameters</h3>
              
              <div className="space-y-4">
                {/* Seed Offset */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-300">Seed Offset</label>
                    <span className="text-sm text-primary-400">
                      {selectedCharacter.seed} {settings.seed_offset > 0 ? '+' : ''}{settings.seed_offset !== 0 ? settings.seed_offset : ''}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="-1000"
                    max="1000"
                    step="10"
                    value={settings.seed_offset}
                    onChange={(e) => updateSetting('seed_offset', parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>-1000</span>
                    <span>0</span>
                    <span>+1000</span>
                  </div>
                </div>

                {/* CFG Scale Adjustment */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-300">CFG Scale Adjustment</label>
                    <span className="text-sm text-primary-400">
                      {selectedCharacter.cfg_scale} {settings.cfg_scale_adjustment > 0 ? '+' : ''}{settings.cfg_scale_adjustment !== 0 ? settings.cfg_scale_adjustment : ''}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="-5"
                    max="5"
                    step="0.5"
                    value={settings.cfg_scale_adjustment}
                    onChange={(e) => updateSetting('cfg_scale_adjustment', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>-5</span>
                    <span>0</span>
                    <span>+5</span>
                  </div>
                </div>

                {/* Quick Reset */}
                <div className="pt-2 border-t border-gray-700">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={resetSettings}
                    className="w-full"
                  >
                    <ArrowPathIcon className="h-4 w-4" />
                    Reset to Defaults
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Feature Overrides */}
      {selectedCharacter && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Feature Overrides</h3>
            <p className="text-gray-400 text-sm mb-4">
              Override specific character features. Leave blank to keep original.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries({
                hair: selectedCharacter.features.hair || 'No hair info',
                eyes: selectedCharacter.features.eyes || 'No eye info',
                skin: selectedCharacter.features.skin || 'No skin info',
                clothing: selectedCharacter.features.clothing || 'No clothing info',
                accessories: selectedCharacter.features.accessories || 'No accessories',
                age: selectedCharacter.features.age || 'No age info',
                expression: selectedCharacter.features.expression || 'Neutral'
              }).map(([feature, originalValue]) => (
                <div key={feature}>
                  <label className="block text-sm font-medium text-gray-300 mb-1 capitalize">
                    {feature}
                  </label>
                  <div className="text-xs text-gray-500 mb-2">Original: {originalValue}</div>
                  <input
                    type="text"
                    value={settings.feature_overrides[feature as keyof typeof settings.feature_overrides] || ''}
                    onChange={(e) => updateFeatureOverride(feature, e.target.value)}
                    placeholder={`Override ${feature}...`}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                  />
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Generate Section */}
      {selectedCharacter && (
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">Generate Fine-Tuned Variation</h3>
                <p className="text-gray-400 text-sm">Create a precisely controlled variation of your character</p>
              </div>
              <Button
                onClick={generateFineTunedVariation}
                disabled={isGenerating}
                loading={isGenerating}
                className="min-w-[140px]"
              >
                <SparklesIcon className="h-4 w-4" />
                {isGenerating ? 'Generating...' : 'Generate'}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Generation History */}
      {generationHistory.length > 0 && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Fine-Tuned Generations</h3>
            
            <div className="space-y-3">
              {generationHistory.map((item) => (
                <div key={item.id} className="border border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold text-white">
                        <Cog6ToothIcon className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="font-medium text-white">{item.character_name}</div>
                        <div className="text-sm text-gray-400">{item.scene_description || 'No scene specified'}</div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 flex items-center gap-2">
                      <ClockIcon className="h-3 w-3" />
                      {new Date(item.created_at).toLocaleString()}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-400 mb-3">
                    <div>Variation: {item.variation_strength}x</div>
                    <div>Seed Offset: {item.modifications?.seed_offset || 0}</div>
                    <div>CFG Adj: {item.modifications?.cfg_adjustment || 0}</div>
                    <div>Art Style: {item.modifications?.art_style || 'Default'}</div>
                  </div>
                  
                  {/* Generated Image */}
                  {item.image_url && (
                    <div className="mt-3">
                      <img
                        src={getFullMediaURL(item.image_url)}
                        alt={`Fine-tuned ${item.character_name}`}
                        className="w-full max-w-sm rounded-lg border border-gray-600 hover:border-primary-500 transition-colors"
                        onError={(e) => {
                          console.log('Image load error:', item.image_url);
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
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
              <h3 className="text-lg font-semibold text-white">Fine-Tune Preview</h3>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-400 hover:text-white"
              >
                <span className="sr-only">Close</span>
                ×
              </button>
            </div>
            
            <div className="bg-gray-800 rounded-lg p-4 max-h-96 overflow-y-auto">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap">{previewData}</pre>
            </div>
            
            <div className="flex justify-end gap-3 mt-4">
              <Button variant="secondary" onClick={() => setShowPreview(false)}>
                Close
              </Button>
              <Button onClick={generateFineTunedVariation} disabled={isGenerating} loading={isGenerating}>
                <SparklesIcon className="h-4 w-4" />
                Generate This Variation
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}