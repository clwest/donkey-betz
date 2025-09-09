import React, { useState, useEffect } from 'react';
import {
  HeartIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  Square3Stack3DIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartIconSolid } from '@heroicons/react/24/solid';
import { characterService } from '../../../services/character.service';
import type { CharacterProfile } from '../../../types/character.types';
import { toast } from 'sonner';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { getFullMediaURL } from '../../../services/api.config';

// Character Thumbnail Component with proper error handling
function CharacterThumbnail({ character }: { character: CharacterProfile }) {
  const [imageError, setImageError] = useState(false);
  const hasValidThumbnail = character.thumbnail_url && character.thumbnail_url.trim() !== '';
  const fullImageURL = getFullMediaURL(character.thumbnail_url || '');

  // Debug logging
  console.log('Character thumbnail debug:', {
    name: character.name,
    thumbnailUrl: character.thumbnail_url,
    fullImageURL,
    hasValidThumbnail,
    imageError
  });

  if (!hasValidThumbnail || imageError) {
    return (
      <div className="w-full h-48 bg-gradient-primary rounded-t-lg flex items-center justify-center">
        <span className="text-4xl font-bold text-white">
          {character.name[0]}
        </span>
      </div>
    );
  }

  return (
    <img
      src={fullImageURL}
      alt={character.name}
      className="w-full h-48 object-cover rounded-t-lg hover:scale-105 transition-transform duration-300"
      onError={(e) => {
        console.log('Image load error:', fullImageURL, e);
        setImageError(true);
      }}
      onLoad={() => console.log('Image loaded successfully:', fullImageURL)}
    />
  );
}

export function CharacterLibrary() {
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [selectedCharacter, setSelectedCharacter] = useState<CharacterProfile | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newCharacter, setNewCharacter] = useState({
    name: '',
    description: '',
    category: 'default',
    tags: [] as string[],
    is_favorite: false,
  });

  useEffect(() => {
    loadCharacters();
  }, [search, category, favoritesOnly]);

  const loadCharacters = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (search) params.search = search;
      if (category) params.category = category;
      if (favoritesOnly) params.is_favorite = true;

      const data = await characterService.getLibrary(params);
      setCharacters(data.characters);
    } catch (error) {
      console.error('Failed to load characters:', error);
      toast.error('Failed to load character library');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (character: CharacterProfile) => {
    try {
      await characterService.toggleFavorite(character.id);
      toast.success(
        character.is_favorite
          ? 'Removed from favorites'
          : 'Added to favorites'
      );
      loadCharacters();
    } catch (error) {
      toast.error('Failed to update favorite status');
    }
  };

  const handleCreateCharacter = async () => {
    try {
      await characterService.createCharacter(newCharacter);
      toast.success('Character created successfully!');
      setCreateModalOpen(false);
      setNewCharacter({
        name: '',
        description: '',
        category: 'default',
        tags: [],
        is_favorite: false,
      });
      loadCharacters();
    } catch (error) {
      toast.error('Failed to create character');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-white">Character Library</h2>
          <p className="text-gray-400 mt-1">Manage your consistent characters</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={() => setFavoritesOnly(!favoritesOnly)}
          >
            <HeartIcon className="h-4 w-4" />
            {favoritesOnly ? 'All' : 'Favorites'}
          </Button>
          <Button
            variant="primary"
            onClick={() => setCreateModalOpen(true)}
          >
            <PlusIcon className="h-4 w-4" />
            Create Character
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search characters..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-700 rounded-xl text-white placeholder-gray-400 focus:border-primary-500 focus:outline-none"
            />
          </div>
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="px-4 py-2 bg-dark-800 border border-dark-700 rounded-xl text-white focus:border-primary-500 focus:outline-none"
        >
          <option value="">All Categories</option>
          <option value="default">Default</option>
          <option value="fantasy">Fantasy</option>
          <option value="realistic">Realistic</option>
          <option value="cartoon">Cartoon</option>
          <option value="anime">Anime</option>
        </select>
      </div>

      {/* Character Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      ) : characters.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-gray-400 mb-4">
            {search || category || favoritesOnly
              ? 'No characters found. Try adjusting your filters.'
              : 'No characters yet. Create your first character to get started.'}
          </p>
          {!search && !category && !favoritesOnly && (
            <Button
              variant="primary"
              onClick={() => setCreateModalOpen(true)}
            >
              <PlusIcon className="h-4 w-4" />
              Create First Character
            </Button>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {characters.map((character) => (
            <Card
              key={character.id}
              className="group hover:border-primary-500/50 transition-all duration-200"
            >
              {/* Thumbnail */}
              <CharacterThumbnail character={character} />

              {/* Content */}
              <div className="p-4 space-y-3">
                <div className="flex justify-between items-start">
                  <h3 className="font-semibold text-white group-hover:text-primary-400 transition-colors">
                    {character.name}
                  </h3>
                  <button
                    onClick={() => handleToggleFavorite(character)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    {character.is_favorite ? (
                      <HeartIconSolid className="h-5 w-5 text-red-500" />
                    ) : (
                      <HeartIcon className="h-5 w-5" />
                    )}
                  </button>
                </div>

                <p className="text-sm text-gray-400 line-clamp-2">
                  {character.description}
                </p>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {character.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 text-xs bg-dark-700 text-gray-300 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                  {character.tags.length > 3 && (
                    <span className="px-2 py-1 text-xs bg-dark-700 text-gray-300 rounded-full">
                      +{character.tags.length - 3}
                    </span>
                  )}
                </div>

                {/* Footer */}
                <div className="flex justify-between items-center pt-3 border-t border-dark-700">
                  <span className="text-xs text-gray-500">
                    Used {character.usage_count} times
                  </span>
                  <span className="text-xs text-primary-400">
                    Seed: {character.seed}
                  </span>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    className="flex-1"
                    onClick={() => setSelectedCharacter(character)}
                  >
                    <Square3Stack3DIcon className="h-4 w-4" />
                    Batch
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="flex-1"
                    onClick={() => setSelectedCharacter(character)}
                  >
                    <SparklesIcon className="h-4 w-4" />
                    Vary
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Character Modal */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <Card className="w-full max-w-lg">
            <div className="p-6 space-y-4">
              <h3 className="text-xl font-bold text-white">Create New Character</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Character Name
                </label>
                <input
                  type="text"
                  value={newCharacter.name}
                  onChange={(e) => setNewCharacter({ ...newCharacter, name: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-xl text-white placeholder-gray-400 focus:border-primary-500 focus:outline-none"
                  placeholder="Enter character name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  value={newCharacter.description}
                  onChange={(e) => setNewCharacter({ ...newCharacter, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-xl text-white placeholder-gray-400 focus:border-primary-500 focus:outline-none resize-none"
                  placeholder="e.g., little girl with curly black hair, olive skin, wearing a silly dress"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Category
                </label>
                <select
                  value={newCharacter.category}
                  onChange={(e) => setNewCharacter({ ...newCharacter, category: e.target.value })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-xl text-white focus:border-primary-500 focus:outline-none"
                >
                  <option value="default">Default</option>
                  <option value="fantasy">Fantasy</option>
                  <option value="realistic">Realistic</option>
                  <option value="cartoon">Cartoon</option>
                  <option value="anime">Anime</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  value={newCharacter.tags.join(', ')}
                  onChange={(e) => setNewCharacter({
                    ...newCharacter,
                    tags: e.target.value.split(',').map(t => t.trim()).filter(t => t)
                  })}
                  className="w-full px-4 py-2 bg-dark-800 border border-dark-700 rounded-xl text-white placeholder-gray-400 focus:border-primary-500 focus:outline-none"
                  placeholder="girl, child, cute"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button
                  variant="secondary"
                  className="flex-1"
                  onClick={() => setCreateModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  className="flex-1"
                  onClick={handleCreateCharacter}
                  disabled={!newCharacter.name || !newCharacter.description}
                >
                  Create
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}