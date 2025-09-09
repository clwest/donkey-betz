import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Modal,
  TextInput,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { BlurView } from 'expo-blur';
import * as Haptics from 'expo-haptics';
import { theme } from '../../styles/theme';
import { styleMemoryService } from '../../services/api';

interface StyleRatingProps {
  contentId: string | number;
  imageUrl?: string;
  onRatingComplete?: (rating: number, feedback?: string) => void;
  onClose?: () => void;
}

export const StyleRating: React.FC<StyleRatingProps> = ({
  contentId,
  imageUrl,
  onRatingComplete,
  onClose,
}) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [animatedStars] = useState(() => 
    Array(5).fill(0).map(() => new Animated.Value(1))
  );

  const handleStarPress = (starRating: number) => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setRating(starRating);
    
    // Animate the selected star
    Animated.sequence([
      Animated.spring(animatedStars[starRating - 1], {
        toValue: 1.3,
        useNativeDriver: true,
      }),
      Animated.spring(animatedStars[starRating - 1], {
        toValue: 1,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const handleSubmit = async () => {
    if (rating === 0) return;

    setIsSubmitting(true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    try {
      // Map 1-5 stars to interaction types
      const interactionMap: Record<number, string> = {
        1: 'dislike',
        2: 'skip',
        3: 'view',
        4: 'like',
        5: 'love',
      };

      await styleMemoryService.captureInteraction(
        String(contentId),
        interactionMap[rating] as any,
        undefined,
        feedback || undefined
      );

      setShowSuccess(true);
      
      // Animate success
      setTimeout(() => {
        onRatingComplete?.(rating, feedback);
        onClose?.();
      }, 1500);
    } catch (error) {
      console.error('Failed to submit rating:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStar = (starNumber: number) => {
    const filled = starNumber <= (hoveredRating || rating);
    const scale = animatedStars[starNumber - 1];

    return (
      <TouchableOpacity
        key={starNumber}
        onPress={() => handleStarPress(starNumber)}
        onPressIn={() => setHoveredRating(starNumber)}
        onPressOut={() => setHoveredRating(0)}
        activeOpacity={0.7}
      >
        <Animated.View style={{ transform: [{ scale }] }}>
          <Text style={[styles.star, filled && styles.starFilled]}>
            {filled ? '⭐' : '☆'}
          </Text>
        </Animated.View>
      </TouchableOpacity>
    );
  };

  if (showSuccess) {
    return (
      <View style={styles.successContainer}>
        <Text style={styles.successIcon}>✨</Text>
        <Text style={styles.successText}>Style learned!</Text>
        <Text style={styles.successSubtext}>
          Your preference has been saved
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Rate This Style</Text>
      <Text style={styles.subtitle}>
        Help the AI learn your preferences
      </Text>

      <View style={styles.starsContainer}>
        {[1, 2, 3, 4, 5].map(renderStar)}
      </View>

      {rating > 0 && (
        <View style={styles.feedbackContainer}>
          <Text style={styles.feedbackLabel}>
            {rating >= 4 ? 'What did you love?' : 
             rating === 3 ? 'Any suggestions?' : 
             'What could be better?'}
          </Text>
          <TextInput
            style={styles.feedbackInput}
            placeholder="Optional feedback..."
            placeholderTextColor={theme.colors.text.secondary}
            value={feedback}
            onChangeText={setFeedback}
            multiline
            maxLength={200}
          />
        </View>
      )}

      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.cancelButton}
          onPress={onClose}
          disabled={isSubmitting}
        >
          <Text style={styles.cancelButtonText}>Skip</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            styles.submitButton,
            rating === 0 && styles.submitButtonDisabled,
          ]}
          onPress={handleSubmit}
          disabled={rating === 0 || isSubmitting}
        >
          <Text style={styles.submitButtonText}>
            {isSubmitting ? 'Saving...' : 'Submit'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Quick Actions Info */}
      <View style={styles.shortcutsInfo}>
        <Text style={styles.shortcutText}>
          Quick: L = Love (5⭐) | S = Save for Similar | R = Show Recipe
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 24,
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    marginBottom: 24,
  },
  starsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  star: {
    fontSize: 40,
    color: theme.colors.text.secondary,
  },
  starFilled: {
    color: '#FFD700',
  },
  feedbackContainer: {
    width: '100%',
    marginBottom: 24,
  },
  feedbackLabel: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    marginBottom: 8,
  },
  feedbackInput: {
    backgroundColor: theme.colors.background.secondary,
    borderRadius: 12,
    padding: 12,
    color: theme.colors.text.primary,
    fontSize: 14,
    minHeight: 60,
    textAlignVertical: 'top',
  },
  actions: {
    flexDirection: 'row',
    gap: 12,
    width: '100%',
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.colors.border.primary,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: theme.colors.text.secondary,
    fontSize: 16,
    fontWeight: '600',
  },
  submitButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    backgroundColor: theme.colors.primary.main,
    alignItems: 'center',
  },
  submitButtonDisabled: {
    opacity: 0.5,
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  shortcutsInfo: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border.secondary,
  },
  shortcutText: {
    fontSize: 12,
    color: theme.colors.text.secondary,
    textAlign: 'center',
  },
  successContainer: {
    padding: 48,
    alignItems: 'center',
  },
  successIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  successText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text.primary,
    marginBottom: 8,
  },
  successSubtext: {
    fontSize: 16,
    color: theme.colors.text.secondary,
  },
});