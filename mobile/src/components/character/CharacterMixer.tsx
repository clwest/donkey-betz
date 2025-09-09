import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  Alert,
  Modal,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../../styles/theme';
import { PremiumButton } from '../common/PremiumButton';
import api from '../../services/api';

interface CharacterProfile {
  id: string;
  name: string;
  description: string;
  features: Record<string, string>;
  seed: number;
  thumbnail_url?: string;
  category: string;
}

interface MixCharacter {
  character: CharacterProfile;
  weight: number;
  features: string[];
}

interface CharacterMix {
  id: string;
  name: string;
  mixed_features: Record<string, string>;
  mixed_seed: number;
  image_url?: string;
  created_at: string;
  source_characters: Array<{
    character_id: string;
    character_name: string;
    weight: number;
    features_used: string[];
  }>;
}

type MixMethod = 'weighted' | 'selective' | 'random';

const availableFeatures = [
  'hair', 'eyes', 'skin', 'clothing', 'accessories', 
  'age', 'gender', 'body', 'expression'
];

export default function CharacterMixer() {
  const [characters, setCharacters] = useState<CharacterProfile[]>([]);
  const [selectedCharacters, setSelectedCharacters] = useState<MixCharacter[]>([]);
  const [mixName, setMixName] = useState('');
  const [mixMethod, setMixMethod] = useState<MixMethod>('weighted');
  const [loading, setLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [mixHistory, setMixHistory] = useState<CharacterMix[]>([]);
  const [showPreview, setShowPreview] = useState(false);
  const [previewMix, setPreviewMix] = useState('');

  useEffect(() => {
    loadCharacters();
    loadMixHistory();
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
      Alert.alert('Error', 'Failed to load character library');
    } finally {
      setLoading(false);
    }
  };

  const loadMixHistory = async () => {
    try {
      const response = await api.get('/character/mix-history/');
      // Axios returns the data directly in response.data
      const data = response.data || response;
      setMixHistory(data.mixes || []);
    } catch (error) {
      if (error.response?.status === 404) {
        setMixHistory([]);
      } else {
        console.error('Failed to load mix history:', error);
      }
    }
  };

  const addCharacter = (character: CharacterProfile) => {
    if (selectedCharacters.find(sc => sc.character.id === character.id)) {
      Alert.alert('Error', 'Character already added to mix');
      return;
    }

    if (selectedCharacters.length >= 4) {
      Alert.alert('Error', 'Maximum 4 characters can be mixed');
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

    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
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
      Alert.alert('Error', 'At least 2 characters required for mixing');
      return;
    }

    if (!mixName.trim()) {
      Alert.alert('Error', 'Please enter a name for the mixed character');
      return;
    }

    setIsGenerating(true);
    try {
      const request = {
        name: mixName.trim(),
        method: mixMethod,
        characters: selectedCharacters.map(sc => ({
          character_id: sc.character.id,
          weight: sc.weight,
          features: sc.features
        }))
      };

      const response = await api.post('/character/mix/', request);
      
      Alert.alert(
        'Success',
        `Mixed character "${response.data.name}" created successfully!`
      );
      setMixName('');
      setSelectedCharacters([]);
      loadMixHistory();
      
    } catch (error) {
      console.error('Failed to mix characters:', error);
      Alert.alert('Error', 'Failed to create mixed character');
    } finally {
      setIsGenerating(false);
    }
  };

  const renderCharacterCard = (character: CharacterProfile) => (
    <TouchableOpacity
      key={character.id}
      style={[
        styles.characterCard,
        selectedCharacters.find(sc => sc.character.id === character.id) && styles.selectedCard
      ]}
      onPress={() => addCharacter(character)}
      disabled={selectedCharacters.find(sc => sc.character.id === character.id) !== undefined}
      activeOpacity={0.7}
    >
      <BlurView intensity={20} tint="dark" style={styles.cardBlur}>
        <LinearGradient
          colors={theme.colors.primary.gradient}
          style={styles.characterAvatar}
        >
          <Text style={styles.avatarText}>
            {character.name.slice(0, 2).toUpperCase()}
          </Text>
        </LinearGradient>
        
        <View style={styles.cardContent}>
          <Text style={styles.characterName} numberOfLines={1}>
            {character.name}
          </Text>
          <Text style={styles.characterCategory}>
            {character.category}
          </Text>
        </View>

        {selectedCharacters.find(sc => sc.character.id === character.id) && (
          <Text style={styles.checkIcon}>✓</Text>
        )}
      </BlurView>
    </TouchableOpacity>
  );

  const renderSelectedCharacter = (mixChar: MixCharacter) => (
    <View key={mixChar.character.id} style={styles.selectedCharacterCard}>
      <BlurView intensity={30} tint="dark" style={styles.selectedCardBlur}>
        <View style={styles.selectedHeader}>
          <LinearGradient
            colors={theme.colors.primary.gradient}
            style={styles.selectedAvatar}
          >
            <Text style={styles.avatarText}>
              {mixChar.character.name.slice(0, 2).toUpperCase()}
            </Text>
          </LinearGradient>
          
          <View style={styles.selectedInfo}>
            <Text style={styles.selectedName}>{mixChar.character.name}</Text>
            <Text style={styles.selectedCategory}>{mixChar.character.category}</Text>
          </View>
          
          <TouchableOpacity
            onPress={() => removeCharacter(mixChar.character.id)}
            style={styles.removeButton}
          >
            <Text style={styles.removeIcon}>×</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.weightSection}>
          <Text style={styles.weightLabel}>
            Weight: {Math.round(mixChar.weight * 100)}%
          </Text>
          {/* Note: Slider would need react-native-slider or similar package */}
          <View style={styles.weightBar}>
            <View
              style={[
                styles.weightFill,
                { width: `${mixChar.weight * 100}%` }
              ]}
            />
          </View>
        </View>

        {mixMethod === 'selective' && (
          <View style={styles.featuresSection}>
            <Text style={styles.featuresLabel}>Features to Use:</Text>
            <View style={styles.featuresGrid}>
              {availableFeatures.map((feature) => (
                <TouchableOpacity
                  key={feature}
                  style={[
                    styles.featureChip,
                    mixChar.features.includes(feature) && styles.featureChipActive
                  ]}
                  onPress={() => toggleFeature(mixChar.character.id, feature)}
                >
                  <Text style={[
                    styles.featureText,
                    mixChar.features.includes(feature) && styles.featureTextActive
                  ]}>
                    {feature}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
      </BlurView>
    </View>
  );

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#0f0f1e']}
        style={styles.gradient}
      />

      <View style={styles.header}>
        <Text style={styles.title}>Character Mixer</Text>
        <Text style={styles.subtitle}>
          Mix features from multiple characters to create unique hybrids
        </Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Character Selection */}
        <BlurView intensity={30} tint="dark" style={styles.section}>
          <Text style={styles.sectionTitle}>Select Characters to Mix</Text>
          <View style={styles.charactersGrid}>
            {loading ? (
              <ActivityIndicator size="large" color={theme.colors.primary.main} />
            ) : (
              characters.map(renderCharacterCard)
            )}
          </View>
        </BlurView>

        {/* Mix Settings */}
        <BlurView intensity={30} tint="dark" style={styles.section}>
          <Text style={styles.sectionTitle}>Mix Settings</Text>
          
          <TextInput
            style={styles.input}
            placeholder="Mixed Character Name"
            placeholderTextColor={theme.colors.text.tertiary}
            value={mixName}
            onChangeText={setMixName}
          />

          <View style={styles.methodSection}>
            <Text style={styles.methodLabel}>Mixing Method:</Text>
            {[
              { value: 'weighted', label: 'Weighted Average' },
              { value: 'selective', label: 'Selective Features' },
              { value: 'random', label: 'Random Mix' }
            ].map((method) => (
              <TouchableOpacity
                key={method.value}
                style={[
                  styles.methodOption,
                  mixMethod === method.value && styles.methodOptionActive
                ]}
                onPress={() => setMixMethod(method.value as MixMethod)}
              >
                <View style={[
                  styles.radio,
                  mixMethod === method.value && styles.radioActive
                ]} />
                <Text style={styles.methodText}>{method.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </BlurView>

        {/* Selected Characters */}
        {selectedCharacters.length > 0 && (
          <BlurView intensity={30} tint="dark" style={styles.section}>
            <Text style={styles.sectionTitle}>
              Selected Characters ({selectedCharacters.length}/4)
            </Text>
            {selectedCharacters.map(renderSelectedCharacter)}

            <View style={styles.actionButtons}>
              <TouchableOpacity
                style={styles.previewButton}
                onPress={generatePreview}
                disabled={selectedCharacters.length < 2}
              >
                <Text style={styles.previewButtonText}>👁 Preview Mix</Text>
              </TouchableOpacity>

              <PremiumButton
                title={isGenerating ? 'Creating Mix...' : 'Mix Characters'}
                onPress={mixCharacters}
                disabled={selectedCharacters.length < 2 || !mixName.trim() || isGenerating}
                style={styles.mixButton}
              />
            </View>
          </BlurView>
        )}

        {/* Mix History */}
        {mixHistory.length > 0 && (
          <BlurView intensity={30} tint="dark" style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Mixed Characters</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {mixHistory.slice(0, 6).map((mix) => (
                <View key={mix.id} style={styles.historyCard}>
                  <LinearGradient
                    colors={['#8B5CF6', '#EC4899']}
                    style={styles.historyAvatar}
                  >
                    <Text style={styles.avatarText}>
                      {mix.name.slice(0, 2).toUpperCase()}
                    </Text>
                  </LinearGradient>
                  
                  <Text style={styles.historyName} numberOfLines={1}>
                    {mix.name}
                  </Text>
                  <Text style={styles.historyInfo}>
                    {mix.source_characters.length} characters
                  </Text>
                </View>
              ))}
            </ScrollView>
          </BlurView>
        )}
      </ScrollView>

      {/* Preview Modal */}
      <Modal
        visible={showPreview}
        transparent
        animationType="fade"
        onRequestClose={() => setShowPreview(false)}
      >
        <View style={styles.modalOverlay}>
          <BlurView intensity={50} tint="dark" style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Mix Preview</Text>
              
              <ScrollView style={styles.previewScroll}>
                <Text style={styles.previewText}>{previewMix}</Text>
              </ScrollView>
              
              <PremiumButton
                title="Close"
                onPress={() => setShowPreview(false)}
                style={styles.closeButton}
              />
            </View>
          </BlurView>
        </View>
      </Modal>
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
  content: {
    flex: 1,
    paddingHorizontal: 20,
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
  charactersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  characterCard: {
    width: '48%',
    marginBottom: 12,
    borderRadius: 12,
    overflow: 'hidden',
  },
  selectedCard: {
    opacity: 0.6,
  },
  cardBlur: {
    padding: 12,
    backgroundColor: theme.colors.background.secondary + '80',
    flexDirection: 'row',
    alignItems: 'center',
  },
  characterAvatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  avatarText: {
    fontSize: 12,
    color: 'white',
    fontWeight: 'bold',
  },
  cardContent: {
    flex: 1,
  },
  characterName: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
  },
  characterCategory: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  checkIcon: {
    fontSize: 16,
    color: theme.colors.primary.main,
  },
  input: {
    backgroundColor: theme.colors.background.primary + '60',
    borderRadius: 12,
    padding: 12,
    color: theme.colors.text.primary,
    fontSize: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: theme.colors.border.secondary,
  },
  methodSection: {
    marginTop: 8,
  },
  methodLabel: {
    fontSize: 16,
    color: theme.colors.text.primary,
    marginBottom: 8,
    fontWeight: '600',
  },
  methodOption: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  methodOptionActive: {
    // Active styling handled by radio button
  },
  radio: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: theme.colors.border.secondary,
    marginRight: 12,
  },
  radioActive: {
    borderColor: theme.colors.primary.main,
    backgroundColor: theme.colors.primary.main,
  },
  methodText: {
    fontSize: 14,
    color: theme.colors.text.primary,
  },
  selectedCharacterCard: {
    marginBottom: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  selectedCardBlur: {
    padding: 16,
    backgroundColor: theme.colors.background.secondary + '60',
  },
  selectedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  selectedAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  selectedInfo: {
    flex: 1,
  },
  selectedName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
  },
  selectedCategory: {
    fontSize: 14,
    color: theme.colors.text.secondary,
  },
  removeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#EF4444',
    alignItems: 'center',
    justifyContent: 'center',
  },
  removeIcon: {
    fontSize: 20,
    color: 'white',
    fontWeight: 'bold',
  },
  weightSection: {
    marginBottom: 12,
  },
  weightLabel: {
    fontSize: 14,
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  weightBar: {
    height: 6,
    backgroundColor: theme.colors.background.primary,
    borderRadius: 3,
    overflow: 'hidden',
  },
  weightFill: {
    height: '100%',
    backgroundColor: theme.colors.primary.main,
  },
  featuresSection: {
    marginTop: 12,
  },
  featuresLabel: {
    fontSize: 14,
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  featureChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: theme.colors.background.primary,
    marginRight: 8,
    marginBottom: 8,
  },
  featureChipActive: {
    backgroundColor: theme.colors.primary.main + '30',
    borderWidth: 1,
    borderColor: theme.colors.primary.main,
  },
  featureText: {
    fontSize: 12,
    color: theme.colors.text.secondary,
  },
  featureTextActive: {
    color: theme.colors.primary.main,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 16,
  },
  previewButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: theme.colors.background.secondary,
    alignItems: 'center',
  },
  previewButtonText: {
    fontSize: 14,
    color: theme.colors.text.primary,
    fontWeight: '600',
  },
  mixButton: {
    flex: 1,
  },
  historyCard: {
    width: 100,
    alignItems: 'center',
    marginRight: 12,
    padding: 8,
    borderRadius: 12,
    backgroundColor: theme.colors.background.primary + '40',
  },
  historyAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  historyName: {
    fontSize: 12,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: 4,
  },
  historyInfo: {
    fontSize: 10,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalContainer: {
    width: '90%',
    maxHeight: '70%',
    borderRadius: 16,
    overflow: 'hidden',
  },
  modalContent: {
    padding: 20,
    backgroundColor: theme.colors.background.secondary + '90',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    textAlign: 'center',
    marginBottom: 16,
  },
  previewScroll: {
    maxHeight: 300,
    marginBottom: 16,
  },
  previewText: {
    fontSize: 14,
    color: theme.colors.text.primary,
    lineHeight: 20,
  },
  closeButton: {
    // PremiumButton handles its own styling
  },
});