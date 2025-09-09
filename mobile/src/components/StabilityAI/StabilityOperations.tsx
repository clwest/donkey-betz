import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import * as ImagePicker from 'expo-image-picker';
import * as Haptics from 'expo-haptics';
import { theme } from '../../styles/theme';
import { stabilityService } from '../../services/api';

interface StabilityOperation {
  id: string;
  name: string;
  icon: string;
  description: string;
  requiresMask?: boolean;
  requiresPrompt?: boolean;
  gradient: string[];
}

interface StabilityOperationsProps {
  imageUrl?: string;
  onOperationComplete?: (resultUrl: string, operation: string) => void;
}

export const StabilityOperations: React.FC<StabilityOperationsProps> = ({
  imageUrl,
  onOperationComplete,
}) => {
  const [selectedOperation, setSelectedOperation] = useState<StabilityOperation | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [maskImage, setMaskImage] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [resultImage, setResultImage] = useState<string | null>(null);

  const operations: StabilityOperation[] = [
    {
      id: 'upscale',
      name: 'Upscale',
      icon: '🔍',
      description: 'Enhance resolution 2x-4x',
      gradient: ['#10B981', '#34D399'],
    },
    {
      id: 'remove-background',
      name: 'Remove BG',
      icon: '✂️',
      description: 'Remove background',
      gradient: ['#6366F1', '#8B5CF6'],
    },
    {
      id: 'inpaint',
      name: 'Inpaint',
      icon: '🎨',
      description: 'Edit parts of image',
      requiresMask: true,
      requiresPrompt: true,
      gradient: ['#EC4899', '#F472B6'],
    },
    {
      id: 'outpaint',
      name: 'Outpaint',
      icon: '🖼️',
      description: 'Extend image borders',
      requiresPrompt: true,
      gradient: ['#F59E0B', '#FCD34D'],
    },
    {
      id: '3d',
      name: '3D Model',
      icon: '🎭',
      description: 'Convert to 3D',
      gradient: ['#8B5CF6', '#A78BFA'],
    },
    {
      id: 'reimagine',
      name: 'Reimagine',
      icon: '✨',
      description: 'Creative variations',
      requiresPrompt: true,
      gradient: ['#14B8A6', '#5EEAD4'],
    },
    {
      id: 'erase',
      name: 'Erase Object',
      icon: '🗑️',
      description: 'Remove objects',
      requiresMask: true,
      gradient: ['#EF4444', '#F87171'],
    },
    {
      id: 'sketch',
      name: 'Sketch to Image',
      icon: '✏️',
      description: 'From sketch to photo',
      requiresPrompt: true,
      gradient: ['#3B82F6', '#60A5FA'],
    },
    {
      id: 'control',
      name: 'Control Net',
      icon: '🎯',
      description: 'Pose/depth control',
      requiresPrompt: true,
      gradient: ['#A855F7', '#C084FC'],
    },
    {
      id: 'replace',
      name: 'Replace Object',
      icon: '🔄',
      description: 'Smart replacement',
      requiresMask: true,
      requiresPrompt: true,
      gradient: ['#06B6D4', '#22D3EE'],
    },
    {
      id: 'colorize',
      name: 'Colorize',
      icon: '🌈',
      description: 'Add colors to B&W',
      gradient: ['#F97316', '#FB923C'],
    },
    {
      id: 'enhance',
      name: 'Enhance',
      icon: '⚡',
      description: 'AI enhancement',
      gradient: ['#84CC16', '#A3E635'],
    },
  ];

  const pickMaskImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled) {
      setMaskImage(result.assets[0].uri);
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  };

  const handleOperation = async (operation: StabilityOperation) => {
    if (!imageUrl && operation.id !== 'sketch') {
      Alert.alert('Error', 'Please select or generate an image first');
      return;
    }

    if (operation.requiresMask && !maskImage) {
      Alert.alert('Mask Required', 'Please select a mask image for this operation');
      return;
    }

    if (operation.requiresPrompt && !prompt.trim()) {
      Alert.alert('Prompt Required', 'Please enter a prompt for this operation');
      return;
    }

    setIsProcessing(true);
    setSelectedOperation(operation);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    try {
      let result;
      
      // Create a mock file object for the image
      const imageFile = {
        uri: imageUrl,
        type: 'image/jpeg',
        name: 'image.jpg',
      };

      const maskFile = maskImage ? {
        uri: maskImage,
        type: 'image/jpeg',
        name: 'mask.jpg',
      } : null;

      switch (operation.id) {
        case 'upscale':
          result = await stabilityService.upscale(imageFile, 2);
          break;
        
        case 'remove-background':
          result = await stabilityService.removeBackground(imageFile);
          break;
        
        case 'inpaint':
          result = await stabilityService.inpaint(imageFile, maskFile!, prompt);
          break;
        
        case 'outpaint':
          result = await stabilityService.outpaint(imageFile, prompt, 'right');
          break;
        
        case '3d':
          result = await stabilityService.generate3D(imageFile);
          break;
        
        case 'reimagine':
          result = await stabilityService.reimagine(imageFile, prompt, 0.7);
          break;
        
        case 'erase':
          result = await stabilityService.eraseObject(imageFile, maskFile!);
          break;
        
        case 'sketch':
          result = await stabilityService.sketchToImage(imageFile, prompt);
          break;
        
        case 'control':
          result = await stabilityService.controlToImage(imageFile, prompt, 'pose');
          break;
        
        case 'replace':
          result = await stabilityService.replaceObject(
            imageFile,
            maskFile!,
            'object',
            prompt
          );
          break;
        
        default:
          throw new Error(`Operation ${operation.id} not implemented`);
      }

      if (result?.result_url) {
        setResultImage(result.result_url);
        onOperationComplete?.(result.result_url, operation.name);
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      }
    } catch (error) {
      console.error(`${operation.name} failed:`, error);
      Alert.alert('Error', `Failed to ${operation.name.toLowerCase()} image`);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🎨 Stability AI Tools</Text>
      <Text style={styles.subtitle}>Advanced image operations</Text>

      {/* Operations Grid */}
      <ScrollView 
        style={styles.operationsScroll}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.operationsGrid}>
          {operations.map((operation) => (
            <TouchableOpacity
              key={operation.id}
              style={styles.operationCard}
              onPress={() => handleOperation(operation)}
              disabled={isProcessing}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={operation.gradient}
                style={styles.operationGradient}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 1 }}
              >
                <Text style={styles.operationIcon}>{operation.icon}</Text>
                <Text style={styles.operationName}>{operation.name}</Text>
                <Text style={styles.operationDescription}>
                  {operation.description}
                </Text>
                {(operation.requiresMask || operation.requiresPrompt) && (
                  <View style={styles.requirementBadges}>
                    {operation.requiresMask && (
                      <View style={styles.badge}>
                        <Text style={styles.badgeText}>Mask</Text>
                      </View>
                    )}
                    {operation.requiresPrompt && (
                      <View style={styles.badge}>
                        <Text style={styles.badgeText}>Prompt</Text>
                      </View>
                    )}
                  </View>
                )}
              </LinearGradient>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      {/* Processing Overlay */}
      {isProcessing && selectedOperation && (
        <BlurView intensity={80} tint="dark" style={styles.processingOverlay}>
          <View style={styles.processingContent}>
            <ActivityIndicator size="large" color={theme.colors.primary.main} />
            <Text style={styles.processingText}>
              {selectedOperation.name} in progress...
            </Text>
            <Text style={styles.processingSubtext}>
              This may take a few moments
            </Text>
          </View>
        </BlurView>
      )}

      {/* Result Display */}
      {resultImage && !isProcessing && (
        <View style={styles.resultContainer}>
          <Text style={styles.resultTitle}>✨ Result</Text>
          <Image
            source={{ uri: resultImage }}
            style={styles.resultImage}
            resizeMode="contain"
          />
          <TouchableOpacity
            style={styles.saveButton}
            onPress={() => {
              Alert.alert('Success', 'Image saved to gallery!');
              setResultImage(null);
            }}
          >
            <Text style={styles.saveButtonText}>Save Result</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginBottom: 20,
  },
  operationsScroll: {
    flex: 1,
  },
  operationsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingBottom: 20,
  },
  operationCard: {
    width: '48%',
    height: 140,
    marginBottom: 12,
    borderRadius: 16,
    overflow: 'hidden',
  },
  operationGradient: {
    flex: 1,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  operationIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  operationName: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
    marginBottom: 4,
  },
  operationDescription: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
  },
  requirementBadges: {
    flexDirection: 'row',
    gap: 4,
    marginTop: 8,
  },
  badge: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  badgeText: {
    fontSize: 9,
    color: 'white',
    fontWeight: '600',
  },
  processingOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
  },
  processingContent: {
    backgroundColor: theme.colors.background.primary,
    padding: 32,
    borderRadius: 24,
    alignItems: 'center',
  },
  processingText: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginTop: 16,
  },
  processingSubtext: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginTop: 8,
  },
  resultContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: theme.colors.background.primary,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: '50%',
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: 12,
  },
  resultImage: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    marginBottom: 16,
  },
  saveButton: {
    backgroundColor: theme.colors.primary.main,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});