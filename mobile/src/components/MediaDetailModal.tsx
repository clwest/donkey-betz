import React from 'react';
import {
  Dimensions,
  Image,
  Modal,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { Video, ResizeMode } from 'expo-av';
import type { MediaItem } from '../api/media';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

interface Props {
  item: MediaItem | null;
  onClose: () => void;
}

export default function MediaDetailModal({ item, onClose }: Props) {
  if (!item) return null;

  const dateStr = item.createdAt
    ? new Date(item.createdAt).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '';

  return (
    <Modal visible={!!item} animationType="slide" transparent>
      <View style={s.backdrop}>
        <View style={s.container}>
          {/* Header */}
          <View style={s.header}>
            <TouchableOpacity onPress={onClose}>
              <Text style={s.closeText}>✕</Text>
            </TouchableOpacity>
            <Text style={s.headerTitle}>
              {item.type === 'image' ? 'Image' : 'Video'}
            </Text>
            <View style={{ width: 30 }} />
          </View>

          {/* Media */}
          <View style={s.mediaContainer}>
            {item.type === 'image' && item.fullUrl ? (
              <ScrollView
                maximumZoomScale={3}
                minimumZoomScale={1}
                contentContainerStyle={s.scrollContent}
              >
                <Image
                  source={{ uri: item.fullUrl }}
                  style={s.fullImage}
                  resizeMode="contain"
                />
              </ScrollView>
            ) : item.type === 'video' && item.fullUrl ? (
              <Video
                source={{ uri: item.fullUrl }}
                style={s.fullVideo}
                useNativeControls
                resizeMode={ResizeMode.CONTAIN}
                shouldPlay
              />
            ) : (
              <View style={s.noMedia}>
                <Text style={s.noMediaText}>No preview available</Text>
              </View>
            )}
          </View>

          {/* Metadata */}
          <View style={s.meta}>
            {item.prompt ? (
              <View style={s.metaRow}>
                <Text style={s.metaLabel}>Prompt</Text>
                <Text style={s.metaValue} numberOfLines={3}>
                  {item.prompt}
                </Text>
              </View>
            ) : null}
            {item.model ? (
              <View style={s.metaRow}>
                <Text style={s.metaLabel}>Model</Text>
                <Text style={s.metaValue}>{item.model}</Text>
              </View>
            ) : null}
            {dateStr ? (
              <View style={s.metaRow}>
                <Text style={s.metaLabel}>Created</Text>
                <Text style={s.metaValue}>{dateStr}</Text>
              </View>
            ) : null}
            {item.width && item.height ? (
              <View style={s.metaRow}>
                <Text style={s.metaLabel}>Size</Text>
                <Text style={s.metaValue}>
                  {item.width} x {item.height}
                </Text>
              </View>
            ) : null}
            {item.duration != null ? (
              <View style={s.metaRow}>
                <Text style={s.metaLabel}>Duration</Text>
                <Text style={s.metaValue}>{item.duration}s</Text>
              </View>
            ) : null}
          </View>
        </View>
      </View>
    </Modal>
  );
}

const s = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.85)',
  },
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
    marginTop: 40,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
  closeText: { color: '#d1d5db', fontSize: 20 },
  headerTitle: { color: '#ffffff', fontSize: 16, fontWeight: '600' },
  mediaContainer: { flex: 1, backgroundColor: '#000000' },
  scrollContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  fullImage: { width: SCREEN_WIDTH, height: SCREEN_WIDTH },
  fullVideo: { width: SCREEN_WIDTH, height: SCREEN_WIDTH * 0.5625 },
  noMedia: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  noMediaText: { color: '#6b7280', fontSize: 14 },
  meta: {
    padding: 16,
    gap: 10,
    borderTopWidth: 1,
    borderTopColor: '#1a1a2e',
  },
  metaRow: { gap: 2 },
  metaLabel: { color: '#6b7280', fontSize: 12 },
  metaValue: { color: '#d1d5db', fontSize: 14 },
});
