import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  FolderIcon,
  UsersIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon,
  StarIcon,
  TagIcon,
} from '@heroicons/react/24/outline';
import {
  StarIcon as StarIconSolid,
} from '@heroicons/react/24/solid';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { characterService } from '../../../services/character.service';
import type { CharacterCollection, CharacterProfile } from '../../../types/character.types';
import { toast } from 'sonner';

interface CreateCollectionData {
  name: string;
  description: string;
  color_theme: string;
  is_public: boolean;
  character_ids: string[];
}

const colorThemes = [
  { value: 'blue', label: 'Ocean Blue', color: 'from-blue-500 to-blue-600' },
  { value: 'purple', label: 'Royal Purple', color: 'from-purple-500 to-purple-600' },
  { value: 'green', label: 'Forest Green', color: 'from-green-500 to-green-600' },
  { value: 'red', label: 'Crimson Red', color: 'from-red-500 to-red-600' },
  { value: 'orange', label: 'Sunset Orange', color: 'from-orange-500 to-orange-600' },
  { value: 'pink', label: 'Blossom Pink', color: 'from-pink-500 to-pink-600' },
  { value: 'teal', label: 'Mystic Teal', color: 'from-teal-500 to-teal-600' },
  { value: 'indigo', label: 'Deep Indigo', color: 'from-indigo-500 to-indigo-600' },
];

const collectionTemplates = [
  {
    name: 'Fantasy Heroes',
    description: 'Epic fantasy characters for adventures',
    color_theme: 'purple',
    tags: ['fantasy', 'heroes', 'adventure']
  },
  {
    name: 'Modern Characters',
    description: 'Contemporary realistic characters',
    color_theme: 'blue',
    tags: ['modern', 'realistic', 'contemporary']
  },
  {
    name: 'Anime Style',
    description: 'Anime and manga inspired characters',
    color_theme: 'pink',
    tags: ['anime', 'manga', 'japanese']
  },
  {
    name: 'Sci-Fi Collection',
    description: 'Futuristic and cyberpunk characters',
    color_theme: 'teal',
    tags: ['sci-fi', 'futuristic', 'cyberpunk']
  }
];

export function CharacterCollections() {
  const [collections, setCollections] = useState<CharacterCollection[]>([]);
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingCollection, setEditingCollection] = useState<CharacterCollection | null>(null);
  const [selectedCharacterIds, setSelectedCharacterIds] = useState<string[]>([]);
  const [showCharacterSelector, setShowCharacterSelector] = useState(false);
  const [activeCollectionId, setActiveCollectionId] = useState<string | null>(null);

  const [createData, setCreateData] = useState<CreateCollectionData>({
    name: '',
    description: '',
    color_theme: 'blue',
    is_public: false,
    character_ids: []
  });

  useEffect(() => {
    loadCollections();
    loadCharacters();
  }, []);

  const loadCollections = async () => {
    setLoading(true);
    try {
      const data = await characterService.getCollections();
      setCollections(data.collections);
    } catch (error) {
      console.error('Failed to load collections:', error);
      toast.error('Failed to load character collections');
    } finally {
      setLoading(false);
    }
  };

  const loadCharacters = async () => {
    try {
      const data = await characterService.getLibrary({});
      setCharacters(data.characters);
    } catch (error) {
      console.error('Failed to load characters:', error);
    }
  };

  const openCreateModal = (template?: typeof collectionTemplates[0]) => {
    if (template) {
      setCreateData({
        name: template.name,
        description: template.description,
        color_theme: template.color_theme,
        is_public: false,
        character_ids: []
      });
    } else {
      setCreateData({
        name: '',
        description: '',
        color_theme: 'blue',
        is_public: false,
        character_ids: []
      });
    }
    setSelectedCharacterIds([]);
    setEditingCollection(null);
    setShowCreateModal(true);
  };

  const openEditModal = (collection: CharacterCollection) => {
    setCreateData({
      name: collection.name,
      description: collection.description,
      color_theme: collection.color_theme,
      is_public: collection.is_public,
      character_ids: collection.characters.map(c => c.id)
    });
    setSelectedCharacterIds(collection.characters.map(c => c.id));
    setEditingCollection(collection);
    setShowCreateModal(true);
  };

  const closeModal = () => {
    setShowCreateModal(false);
    setEditingCollection(null);
    setSelectedCharacterIds([]);
    setShowCharacterSelector(false);
    setActiveCollectionId(null);
  };

  const handleCreateOrUpdate = async () => {
    if (!createData.name.trim()) {
      toast.error('Collection name is required');
      return;
    }

    try {
      const collectionData = {
        ...createData,
        character_ids: selectedCharacterIds
      };

      if (editingCollection) {
        await characterService.updateCollection(editingCollection.id, collectionData);
        toast.success('Collection updated successfully!');
      } else {
        await characterService.createCollection(collectionData);
        toast.success('Collection created successfully!');
      }

      closeModal();
      loadCollections();
    } catch (error) {
      console.error('Failed to save collection:', error);
      toast.error(`Failed to ${editingCollection ? 'update' : 'create'} collection`);
    }
  };

  const handleDeleteCollection = async (collection: CharacterCollection) => {
    if (!confirm(`Are you sure you want to delete "${collection.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await characterService.deleteCollection(collection.id);
      toast.success('Collection deleted successfully');
      loadCollections();
    } catch (error) {
      console.error('Failed to delete collection:', error);
      toast.error('Failed to delete collection');
    }
  };

  const toggleCharacterInCollection = async (collectionId: string, characterId: string, isAdding: boolean) => {
    try {
      if (isAdding) {
        await characterService.addToCollection(collectionId, [characterId]);
        toast.success('Character added to collection');
      } else {
        await characterService.removeFromCollection(collectionId, [characterId]);
        toast.success('Character removed from collection');
      }
      loadCollections();
    } catch (error) {
      console.error('Failed to modify collection:', error);
      toast.error('Failed to modify collection');
    }
  };

  const openCharacterSelector = (collectionId: string) => {
    setActiveCollectionId(collectionId);
    setShowCharacterSelector(true);
  };

  const getThemeColors = (theme: string) => {
    const themeData = colorThemes.find(t => t.value === theme);
    return themeData?.color || 'from-blue-500 to-blue-600';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Character Collections</h2>
          <p className="text-muted-foreground mt-1">Organize your characters into themed collections</p>
        </div>
        <Button onClick={() => openCreateModal()}>
          <PlusIcon className="h-4 w-4" />
          New Collection
        </Button>
      </div>

      {/* Collection Templates */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Quick Start Templates</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {collectionTemplates.map((template, index) => (
              <button
                key={index}
                onClick={() => openCreateModal(template)}
                className="p-4 border border-gray-700 rounded-lg hover:border-primary-500/50 transition-all text-left group"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${getThemeColors(template.color_theme)} flex items-center justify-center mb-3 group-hover:scale-105 transition-transform`}>
                  <FolderIcon className="h-6 w-6 text-foreground" />
                </div>
                <div className="font-medium text-foreground mb-1">{template.name}</div>
                <div className="text-sm text-muted-foreground mb-2">{template.description}</div>
                <div className="flex flex-wrap gap-1">
                  {template.tags.map((tag, tagIndex) => (
                    <span key={tagIndex} className="px-2 py-1 bg-card text-xs text-muted-foreground rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Collections Grid */}
      {loading ? (
        <Card>
          <div className="p-8 text-center">
            <div className="animate-spin w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <div className="text-muted-foreground">Loading collections...</div>
          </div>
        </Card>
      ) : collections.length === 0 ? (
        <Card>
          <div className="p-8 text-center">
            <FolderIcon className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-foreground mb-2">No Collections Yet</h3>
            <p className="text-muted-foreground max-w-md mx-auto mb-6">
              Create your first character collection to organize your characters by theme, project, or any criteria you like.
            </p>
            <Button onClick={() => openCreateModal()}>
              <PlusIcon className="h-4 w-4" />
              Create First Collection
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {collections.map((collection) => (
            <Card key={collection.id}>
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${getThemeColors(collection.color_theme)} flex items-center justify-center`}>
                    <FolderIcon className="h-6 w-6 text-foreground" />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => openEditModal(collection)}
                      className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteCollection(collection)}
                      className="p-2 text-muted-foreground hover:text-red-500 transition-colors"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-foreground truncate">{collection.name}</h3>
                    {collection.is_public && (
                      <StarIcon className="h-4 w-4 text-yellow-500 flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">{collection.description}</p>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <UsersIcon className="h-4 w-4" />
                    <span>{collection.character_count} characters</span>
                  </div>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => openCharacterSelector(collection.id)}
                  >
                    <PlusIcon className="h-3 w-3" />
                    Add
                  </Button>
                </div>

                {/* Character Avatars */}
                {collection.characters.length > 0 && (
                  <div className="flex -space-x-2">
                    {collection.characters.slice(0, 4).map((character) => (
                      <div
                        key={character.id}
                        className="relative group"
                        title={character.name}
                      >
                        {character.thumbnail_url && character.thumbnail_url.trim() !== '' ? (
                          <img
                            src={character.thumbnail_url}
                            alt={character.name}
                            className="w-8 h-8 rounded-full object-cover border-2 border-gray-900"
                            onError={(e) => {
                              e.currentTarget.style.display = 'none';
                              const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                              if (fallback) fallback.style.display = 'flex';
                            }}
                          />
                        ) : null}
                        <div 
                          className="w-8 h-8 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-xs font-bold text-foreground border-2 border-gray-900"
                          style={{ display: character.thumbnail_url && character.thumbnail_url.trim() !== '' ? 'none' : 'flex' }}
                        >
                          {character.name.slice(0, 2).toUpperCase()}
                        </div>
                        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-card text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                          {character.name}
                        </div>
                      </div>
                    ))}
                    {collection.character_count > 4 && (
                      <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-bold text-muted-foreground border-2 border-gray-900">
                        +{collection.character_count - 4}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create/Edit Collection Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-foreground">
                {editingCollection ? 'Edit Collection' : 'Create New Collection'}
              </h3>
              <button onClick={closeModal} className="text-muted-foreground hover:text-foreground">
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-2">
                    Collection Name *
                  </label>
                  <input
                    type="text"
                    value={createData.name}
                    onChange={(e) => setCreateData({ ...createData, name: e.target.value })}
                    placeholder="Enter collection name..."
                    className="w-full px-3 py-2 bg-card border border-gray-700 rounded-lg text-foreground placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-muted-foreground mb-2">
                    Color Theme
                  </label>
                  <select
                    value={createData.color_theme}
                    onChange={(e) => setCreateData({ ...createData, color_theme: e.target.value })}
                    className="w-full px-3 py-2 bg-card border border-gray-700 rounded-lg text-foreground focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    {colorThemes.map((theme) => (
                      <option key={theme.value} value={theme.value}>
                        {theme.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-2">
                  Description
                </label>
                <textarea
                  value={createData.description}
                  onChange={(e) => setCreateData({ ...createData, description: e.target.value })}
                  placeholder="Describe this collection..."
                  rows={3}
                  className="w-full px-3 py-2 bg-card border border-gray-700 rounded-lg text-foreground placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={createData.is_public}
                  onChange={(e) => setCreateData({ ...createData, is_public: e.target.checked })}
                  className="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="text-sm font-medium text-muted-foreground">
                  Make this collection public (others can view)
                </label>
              </div>

              {/* Character Selection */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <label className="text-sm font-medium text-muted-foreground">
                    Characters ({selectedCharacterIds.length} selected)
                  </label>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-64 overflow-y-auto border border-gray-700 rounded-lg p-4">
                  {characters.map((character) => (
                    <label key={character.id} className="flex items-center gap-2 p-2 hover:bg-card rounded cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedCharacterIds.includes(character.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCharacterIds([...selectedCharacterIds, character.id]);
                          } else {
                            setSelectedCharacterIds(selectedCharacterIds.filter(id => id !== character.id));
                          }
                        }}
                        className="w-4 h-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div className="w-6 h-6 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-xs font-bold text-foreground">
                        {character.name.slice(0, 1).toUpperCase()}
                      </div>
                      <span className="text-sm text-foreground truncate">{character.name}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="secondary" onClick={closeModal}>
                Cancel
              </Button>
              <Button onClick={handleCreateOrUpdate}>
                {editingCollection ? 'Update Collection' : 'Create Collection'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Character Selector Modal */}
      {showCharacterSelector && activeCollectionId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-foreground">Add Characters to Collection</h3>
              <button
                onClick={() => setShowCharacterSelector(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {characters.map((character) => {
                const collection = collections.find(c => c.id === activeCollectionId);
                const isInCollection = collection?.characters.some(c => c.id === character.id);
                
                return (
                  <div key={character.id} className="border border-gray-700 rounded-lg p-4">
                    <div className="flex items-center gap-3 mb-3">
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
                        className="w-10 h-10 rounded-full bg-gradient-to-r from-primary-500 to-secondary-500 flex items-center justify-center text-sm font-bold text-foreground"
                        style={{ display: character.thumbnail_url && character.thumbnail_url.trim() !== '' ? 'none' : 'flex' }}
                      >
                        {character.name.slice(0, 2).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-foreground truncate">{character.name}</div>
                        <div className="text-sm text-muted-foreground truncate">{character.category}</div>
                      </div>
                    </div>
                    
                    <Button
                      size="sm"
                      variant={isInCollection ? "secondary" : "primary"}
                      onClick={() => toggleCharacterInCollection(activeCollectionId, character.id, !isInCollection)}
                      className="w-full"
                    >
                      {isInCollection ? (
                        <>
                          <CheckIcon className="h-3 w-3" />
                          In Collection
                        </>
                      ) : (
                        <>
                          <PlusIcon className="h-3 w-3" />
                          Add to Collection
                        </>
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}