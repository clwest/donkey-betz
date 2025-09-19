import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  TrashIcon,
  PlayIcon,
  ChevronDownIcon,
  ChevronUpIcon,
} from '@heroicons/react/24/outline';
import { characterService } from '../../../services/character.service';
import type { CharacterProfile, SceneConfig } from '../../../types/character.types';
import { toast } from 'sonner';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';

export function BatchGenerator() {
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [selectedCharacter, setSelectedCharacter] = useState<string>('');
  const [batchName, setBatchName] = useState('');
  const [scenes, setScenes] = useState<SceneConfig[]>([
    { description: '', action: '', mood: '' },
  ]);
  const [variationStrength, setVariationStrength] = useState(1.0);
  const [preserveOutfit, setPreserveOutfit] = useState(true);
  const [preserveStyle, setPreserveStyle] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [expandedResults, setExpandedResults] = useState(false);

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    try {
      const data = await characterService.getLibrary();
      setCharacters(data.characters);
    } catch (error) {
      console.error('Failed to load characters:', error);
      toast.error('Failed to load characters');
    }
  };

  const handleAddScene = () => {
    setScenes([...scenes, { description: '', action: '', mood: '' }]);
  };

  const handleRemoveScene = (index: number) => {
    setScenes(scenes.filter((_, i) => i !== index));
  };

  const handleSceneChange = (index: number, field: keyof SceneConfig, value: string) => {
    const updatedScenes = [...scenes];
    updatedScenes[index] = { ...updatedScenes[index], [field]: value };
    setScenes(updatedScenes);
  };

  const handleGenerate = async () => {
    if (!selectedCharacter) {
      toast.error('Please select a character');
      return;
    }

    const validScenes = scenes.filter(
      (s) => s.description || s.action || s.mood
    );

    if (validScenes.length === 0) {
      toast.error('Please add at least one scene');
      return;
    }

    setGenerating(true);
    setResults([]);

    try {
      const response = await characterService.batchGenerate({
        character_id: selectedCharacter,
        scenes: validScenes,
        batch_name: batchName || `Batch ${new Date().toLocaleString()}`,
        variation_strength: variationStrength,
        preserve_outfit: preserveOutfit,
        preserve_style: preserveStyle,
      });

      setResults(response.results);
      setExpandedResults(true);
      toast.success(
        `Generated ${response.successful} scenes successfully${
          response.failed > 0 ? ` (${response.failed} failed)` : ''
        }`
      );
    } catch (error) {
      console.error('Batch generation failed:', error);
      toast.error('Failed to generate batch');
    } finally {
      setGenerating(false);
    }
  };

  const selectedCharacterData = characters.find((c) => c.id === selectedCharacter);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Batch Scene Generation</h2>
        <p className="text-muted-foreground">Generate multiple scenes with the same character</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration Panel */}
        <Card>
          <div className="p-6 space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Configuration</h3>

            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">
                Character
              </label>
              <select
                value={selectedCharacter}
                onChange={(e) => setSelectedCharacter(e.target.value)}
                className="w-full px-4 py-2 bg-card border border-border rounded-xl text-foreground focus:border-primary-500 focus:outline-none"
              >
                <option value="">Select a character...</option>
                {characters.map((char) => (
                  <option key={char.id} value={char.id}>
                    {char.name} ({char.usage_count} uses)
                  </option>
                ))}
              </select>
            </div>

            {selectedCharacterData && (
              <Card className="bg-primary-500/10 border-primary-500/30">
                <div className="p-4">
                  <p className="text-sm text-foreground font-medium mb-1">
                    Selected: {selectedCharacterData.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {selectedCharacterData.description}
                  </p>
                </div>
              </Card>
            )}

            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">
                Batch Name
              </label>
              <input
                type="text"
                value={batchName}
                onChange={(e) => setBatchName(e.target.value)}
                className="w-full px-4 py-2 bg-card border border-border rounded-xl text-foreground placeholder-gray-400 focus:border-primary-500 focus:outline-none"
                placeholder="My Scene Collection"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-muted-foreground mb-2">
                Variation Strength: {variationStrength.toFixed(1)}
              </label>
              <input
                type="range"
                value={variationStrength}
                onChange={(e) => setVariationStrength(parseFloat(e.target.value))}
                min="0.5"
                max="2.0"
                step="0.1"
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>Subtle</span>
                <span>Normal</span>
                <span>Strong</span>
              </div>
            </div>

            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preserveOutfit}
                  onChange={(e) => setPreserveOutfit(e.target.checked)}
                  className="rounded border-gray-600 text-primary-500 focus:ring-primary-500"
                />
                <span className="text-sm text-muted-foreground">Preserve Outfit</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preserveStyle}
                  onChange={(e) => setPreserveStyle(e.target.checked)}
                  className="rounded border-gray-600 text-primary-500 focus:ring-primary-500"
                />
                <span className="text-sm text-muted-foreground">Preserve Style</span>
              </label>
            </div>
          </div>
        </Card>

        {/* Scenes Panel */}
        <Card>
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-foreground">
                Scenes ({scenes.length})
              </h3>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleAddScene}
              >
                <PlusIcon className="h-4 w-4" />
                Add Scene
              </Button>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {scenes.map((scene, index) => (
                <Card key={index} className="bg-card/50">
                  <div className="p-4 space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-foreground">
                        Scene {index + 1}
                      </span>
                      <button
                        onClick={() => handleRemoveScene(index)}
                        className="text-muted-foreground hover:text-red-500 transition-colors"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>

                    <input
                      type="text"
                      value={scene.description}
                      onChange={(e) => handleSceneChange(index, 'description', e.target.value)}
                      className="w-full px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder-gray-500 focus:border-primary-500 focus:outline-none text-sm"
                      placeholder="Scene description (e.g., standing in snow)"
                    />

                    <div className="grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        value={scene.action || ''}
                        onChange={(e) => handleSceneChange(index, 'action', e.target.value)}
                        className="px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder-gray-500 focus:border-primary-500 focus:outline-none text-sm"
                        placeholder="Action (optional)"
                      />
                      <input
                        type="text"
                        value={scene.mood || ''}
                        onChange={(e) => handleSceneChange(index, 'mood', e.target.value)}
                        className="px-3 py-2 bg-background border border-border rounded-lg text-foreground placeholder-gray-500 focus:border-primary-500 focus:outline-none text-sm"
                        placeholder="Mood (optional)"
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Generate Button */}
      <div className="text-center">
        <Button
          variant="primary"
          size="lg"
          onClick={handleGenerate}
          disabled={generating || !selectedCharacter}
          className="min-w-[200px]"
        >
          {generating ? (
            <>
              <span className="animate-spin mr-2">⚡</span>
              Generating...
            </>
          ) : (
            <>
              <PlayIcon className="h-5 w-5" />
              Generate All Scenes
            </>
          )}
        </Button>
      </div>

      {/* Progress */}
      {generating && (
        <Card>
          <div className="p-4">
            <div className="w-full bg-card rounded-full h-2">
              <div className="bg-gradient-primary h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
            <p className="text-sm text-muted-foreground text-center mt-2">
              Generating scenes... This may take a few moments
            </p>
          </div>
        </Card>
      )}

      {/* Results */}
      {results.length > 0 && (
        <Card>
          <div className="p-6">
            <button
              onClick={() => setExpandedResults(!expandedResults)}
              className="flex items-center justify-between w-full mb-4"
            >
              <h3 className="text-lg font-semibold text-foreground">
                Generated Results ({results.length})
              </h3>
              {expandedResults ? (
                <ChevronUpIcon className="h-5 w-5 text-muted-foreground" />
              ) : (
                <ChevronDownIcon className="h-5 w-5 text-muted-foreground" />
              )}
            </button>

            {expandedResults && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {results.map((result, index) => (
                  <Card key={index} className="overflow-hidden">
                    <img
                      src={result.image_url}
                      alt={`Scene ${index + 1}`}
                      className="w-full h-48 object-cover"
                    />
                    <div className="p-4">
                      <p className="text-sm font-medium text-foreground mb-1">
                        Scene {index + 1}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {result.scene.description}
                        {result.scene.action && ` - ${result.scene.action}`}
                        {result.scene.mood && ` (${result.scene.mood})`}
                      </p>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}