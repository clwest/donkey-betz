import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  TextInput,
  ActivityIndicator,
  FlatList,
  Modal,
  Platform,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../styles/theme';
import { PremiumButton } from '../components/common/PremiumButton';
import api from '../services/api';

interface CharacterProfile {
  id: string;
  name: string;
  description: string;
  seed: number;
  thumbnail_url?: string;
  usage_count: number;
  is_favorite: boolean;
  tags: string[];
  category: string;
}

interface SceneConfig {
  description: string;
  action?: string;
  mood?: string;
}

export default function CharacterScreen() {
  const [activeTab, setActiveTab] = useState<'library' | 'batch' | 'create'>('library');
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCharacter, setSelectedCharacter] = useState<CharacterProfile | null>(null);
  const [scenes, setScenes] = useState<SceneConfig[]>([{ description: '', action: '', mood: '' }]);
  const [batchName, setBatchName] = useState('');
  const [generating, setGenerating] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [newCharacter, setNewCharacter] = useState({
    name: '',
    description: '',
    category: 'default',
    tags: '',
  });

  useEffect(() => {
    loadCharacters();
  }, []);

  const loadCharacters = async () => {
    setLoading(true);
    try {
      const response = await api.get('/character/library/');
      // Axios returns the data directly in response.data
      const data = response.data || response;
      setCharacters(data.characters || []);
    } catch (error) {
      console.error('Failed to load characters:', error);
      Alert.alert('Error', 'Failed to load characters');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (character: CharacterProfile) => {
    try {
      await api.post(`/character/library/${character.id}/toggle-favorite/`);
      if (Platform.OS !== 'web') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
      loadCharacters();
    } catch (error) {
      Alert.alert('Error', 'Failed to update favorite status');
    }
  };

  const handleCreateCharacter = async () => {
    if (!newCharacter.name || !newCharacter.description) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    try {
      await api.post('/character/library/create/', {
        ...newCharacter,
        tags: newCharacter.tags.split(',').map(t => t.trim()).filter(t => t),
      });
      setCreateModalVisible(false);
      setNewCharacter({ name: '', description: '', category: 'default', tags: '' });
      loadCharacters();
      Alert.alert('Success', 'Character created successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to create character');
    }
  };

  const handleBatchGenerate = async () => {
    if (!selectedCharacter) {
      Alert.alert('Error', 'Please select a character');
      return;
    }

    const validScenes = scenes.filter(s => s.description);
    if (validScenes.length === 0) {
      Alert.alert('Error', 'Please add at least one scene');
      return;
    }

    setGenerating(true);
    try {
      const response = await api.post('/character/batch-generate/', {
        character_id: selectedCharacter.id,
        scenes: validScenes,
        batch_name: batchName || `Batch ${new Date().toLocaleString()}`,
        variation_strength: 1.0,
        preserve_outfit: true,
        preserve_style: true,
      });

      Alert.alert(
        'Success',
        `Generated ${response.data.successful} scenes successfully!`
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to generate batch');
    } finally {
      setGenerating(false);
    }
  };

  const renderCharacterCard = ({ item }: { item: CharacterProfile }) => (
    <TouchableOpacity
      style={styles.characterCard}
      onPress={() => setSelectedCharacter(item)}
      activeOpacity={0.7}
    >
      <BlurView intensity={20} tint="dark" style={styles.cardBlur}>
        {item.thumbnail_url ? (
          <Image source={{ uri: item.thumbnail_url }} style={styles.characterImage} />
        ) : (
          <LinearGradient
            colors={theme.colors.primary.gradient}
            style={styles.characterImagePlaceholder}
          >
            <Text style={styles.placeholderText}>{item.name[0]}</Text>
          </LinearGradient>
        )}
        
        <View style={styles.cardContent}>
          <Text style={styles.characterName}>{item.name}</Text>
          <Text style={styles.characterDescription} numberOfLines={2}>
            {item.description}
          </Text>
          
          <View style={styles.cardFooter}>
            <Text style={styles.seedText}>Seed: {item.seed}</Text>
            <TouchableOpacity
              onPress={() => handleToggleFavorite(item)}
              style={styles.favoriteButton}
            >
              <Text style={styles.favoriteIcon}>
                {item.is_favorite ? '❤️' : '🤍'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </BlurView>
    </TouchableOpacity>
  );

  const renderTabButton = (tab: 'library' | 'batch' | 'create', label: string, icon: string) => (
    <TouchableOpacity
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
      onPress={() => {
        setActiveTab(tab);
        if (Platform.OS !== 'web') {
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        }
      }}
    >
      <Text style={styles.tabIcon}>{icon}</Text>
      <Text style={[styles.tabLabel, activeTab === tab && styles.tabLabelActive]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#0f0f1e']}
        style={styles.gradient}
      />

      <View style={styles.header}>
        <Text style={styles.title}>Character Studio</Text>
        <Text style={styles.subtitle}>
          Create and manage consistent characters
        </Text>
      </View>

      <View style={styles.tabs}>
        {renderTabButton('library', 'Library', '📚')}
        {renderTabButton('batch', 'Batch', '🎬')}
        {renderTabButton('create', 'Create', '✨')}
      </View>

      {activeTab === 'library' && (
        <View style={styles.content}>
          {loading ? (
            <ActivityIndicator size="large" color={theme.colors.primary.main} />
          ) : (
            <FlatList
              data={characters}
              renderItem={renderCharacterCard}
              keyExtractor={(item) => item.id}
              numColumns={2}
              columnWrapperStyle={styles.row}
              contentContainerStyle={styles.listContent}
              showsVerticalScrollIndicator={false}
            />
          )}
        </View>
      )}

      {activeTab === 'batch' && (
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <BlurView intensity={30} tint="dark" style={styles.section}>
            <Text style={styles.sectionTitle}>Select Character</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {characters.map((char) => (
                <TouchableOpacity
                  key={char.id}
                  style={[
                    styles.characterChip,
                    selectedCharacter?.id === char.id && styles.characterChipActive,
                  ]}
                  onPress={() => setSelectedCharacter(char)}
                >
                  <Text style={styles.chipText}>{char.name}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </BlurView>

          <BlurView intensity={30} tint="dark" style={styles.section}>
            <Text style={styles.sectionTitle}>Batch Settings</Text>
            <TextInput
              style={styles.input}
              placeholder="Batch Name (optional)"
              placeholderTextColor={theme.colors.text.tertiary}
              value={batchName}
              onChangeText={setBatchName}
            />
          </BlurView>

          <BlurView intensity={30} tint="dark" style={styles.section}>
            <Text style={styles.sectionTitle}>Scenes</Text>
            {scenes.map((scene, index) => (
              <View key={index} style={styles.sceneCard}>
                <Text style={styles.sceneNumber}>Scene {index + 1}</Text>
                <TextInput
                  style={styles.input}
                  placeholder="Scene description"
                  placeholderTextColor={theme.colors.text.tertiary}
                  value={scene.description}
                  onChangeText={(text) => {
                    const newScenes = [...scenes];
                    newScenes[index].description = text;
                    setScenes(newScenes);
                  }}
                />
                <View style={styles.sceneRow}>
                  <TextInput
                    style={[styles.input, styles.halfInput]}
                    placeholder="Action"
                    placeholderTextColor={theme.colors.text.tertiary}
                    value={scene.action || ''}
                    onChangeText={(text) => {
                      const newScenes = [...scenes];
                      newScenes[index].action = text;
                      setScenes(newScenes);
                    }}
                  />
                  <TextInput
                    style={[styles.input, styles.halfInput]}
                    placeholder="Mood"
                    placeholderTextColor={theme.colors.text.tertiary}
                    value={scene.mood || ''}
                    onChangeText={(text) => {
                      const newScenes = [...scenes];
                      newScenes[index].mood = text;
                      setScenes(newScenes);
                    }}
                  />
                </View>
              </View>
            ))}

            <TouchableOpacity
              style={styles.addSceneButton}
              onPress={() => setScenes([...scenes, { description: '', action: '', mood: '' }])}
            >
              <Text style={styles.addSceneText}>+ Add Scene</Text>
            </TouchableOpacity>
          </BlurView>

          <PremiumButton
            title={generating ? 'Generating...' : 'Generate All Scenes'}
            onPress={handleBatchGenerate}
            disabled={generating || !selectedCharacter}
            style={styles.generateButton}
          />
        </ScrollView>
      )}

      {activeTab === 'create' && (
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <BlurView intensity={30} tint="dark" style={styles.section}>
            <Text style={styles.sectionTitle}>Character Details</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Character Name"
              placeholderTextColor={theme.colors.text.tertiary}
              value={newCharacter.name}
              onChangeText={(text) => setNewCharacter({ ...newCharacter, name: text })}
            />

            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Description (e.g., little girl with curly hair)"
              placeholderTextColor={theme.colors.text.tertiary}
              value={newCharacter.description}
              onChangeText={(text) => setNewCharacter({ ...newCharacter, description: text })}
              multiline
              numberOfLines={4}
            />

            <TextInput
              style={styles.input}
              placeholder="Tags (comma separated)"
              placeholderTextColor={theme.colors.text.tertiary}
              value={newCharacter.tags}
              onChangeText={(text) => setNewCharacter({ ...newCharacter, tags: text })}
            />

            <View style={styles.categoryContainer}>
              <Text style={styles.labelText}>Category:</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {['default', 'fantasy', 'realistic', 'cartoon', 'anime'].map((cat) => (
                  <TouchableOpacity
                    key={cat}
                    style={[
                      styles.categoryChip,
                      newCharacter.category === cat && styles.categoryChipActive,
                    ]}
                    onPress={() => setNewCharacter({ ...newCharacter, category: cat })}
                  >
                    <Text style={styles.chipText}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>

            <PremiumButton
              title="Create Character"
              onPress={handleCreateCharacter}
              disabled={!newCharacter.name || !newCharacter.description}
              style={styles.createButton}
            />
          </BlurView>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background.primary,
  },
  gradient: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    height: '100%',
  },
  header: {
    paddingTop: Platform.OS === 'ios' ? 60 : 40,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.text.secondary,
  },
  tabs: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  tabButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    marginHorizontal: 5,
    borderRadius: 12,
    backgroundColor: theme.colors.background.secondary,
  },
  tabButtonActive: {
    backgroundColor: theme.colors.primary.main + '20',
    borderWidth: 1,
    borderColor: theme.colors.primary.main,
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 12,
    color: theme.colors.text.secondary,
    fontWeight: '600',
  },
  tabLabelActive: {
    color: theme.colors.primary.main,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  listContent: {
    paddingBottom: 100,
  },
  row: {
    justifyContent: 'space-between',
  },
  characterCard: {
    flex: 0.48,
    marginBottom: 15,
    borderRadius: 16,
    overflow: 'hidden',
  },
  cardBlur: {
    padding: 12,
    backgroundColor: theme.colors.background.secondary + '80',
  },
  characterImage: {
    width: '100%',
    height: 120,
    borderRadius: 12,
    marginBottom: 12,
  },
  characterImagePlaceholder: {
    width: '100%',
    height: 120,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderText: {
    fontSize: 36,
    color: 'white',
    fontWeight: 'bold',
  },
  cardContent: {
    flex: 1,
  },
  characterName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  characterDescription: {
    fontSize: 12,
    color: theme.colors.text.secondary,
    marginBottom: 8,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  seedText: {
    fontSize: 10,
    color: theme.colors.text.tertiary,
  },
  favoriteButton: {
    padding: 4,
  },
  favoriteIcon: {
    fontSize: 16,
  },
  section: {
    padding: 16,
    borderRadius: 16,
    marginBottom: 20,
    backgroundColor: theme.colors.background.secondary + '40',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 12,
  },
  input: {
    backgroundColor: theme.colors.background.primary + '60',
    borderRadius: 12,
    padding: 12,
    color: theme.colors.text.primary,
    fontSize: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  textArea: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
  halfInput: {
    flex: 1,
    marginHorizontal: 4,
  },
  characterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: theme.colors.background.secondary,
    marginRight: 8,
  },
  characterChipActive: {
    backgroundColor: theme.colors.primary.main + '30',
    borderWidth: 1,
    borderColor: theme.colors.primary.main,
  },
  chipText: {
    color: theme.colors.text.primary,
    fontSize: 14,
    fontWeight: '600',
  },
  sceneCard: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
    backgroundColor: theme.colors.background.primary + '40',
  },
  sceneNumber: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.text.secondary,
    marginBottom: 8,
  },
  sceneRow: {
    flexDirection: 'row',
  },
  addSceneButton: {
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: theme.colors.primary.main,
    borderStyle: 'dashed',
  },
  addSceneText: {
    color: theme.colors.primary.main,
    fontSize: 14,
    fontWeight: '600',
  },
  generateButton: {
    marginBottom: 40,
  },
  categoryContainer: {
    marginBottom: 16,
  },
  labelText: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginBottom: 8,
  },
  categoryChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: theme.colors.background.secondary,
    marginRight: 8,
  },
  categoryChipActive: {
    backgroundColor: theme.colors.primary.main + '30',
    borderWidth: 1,
    borderColor: theme.colors.primary.main,
  },
  createButton: {
    marginTop: 8,
  },
});