import React, { useCallback, useRef, useState } from 'react';
import {
  ActivityIndicator,
  Dimensions,
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Image,
} from 'react-native';
import { Video, ResizeMode, Audio } from 'expo-av';
import type { ToolRun } from '../api/assistant';

// ── Helpers ─────────────────────────────────────────────────────────────────

function extractVideoUrl(tr: ToolRun): string | null {
  const r = tr.result;
  if (!r) return null;
  return (
    r.video_url ??
    r.thumbnail_url ??
    r.data?.final_video_url ??
    r.data?.video_url ??
    null
  );
}

function extractThumbnail(tr: ToolRun): string | null {
  return tr.result?.thumbnail_url ?? tr.result?.data?.thumbnail_url ?? null;
}

function isProcessing(tr: ToolRun): boolean {
  return tr.result?.data?.status === 'processing';
}

const { width: SCREEN_WIDTH } = Dimensions.get('window');

// ── VideoThumbnail ──────────────────────────────────────────────────────────

function VideoThumbnail({
  videoUrl,
  thumbnailUrl,
  processing,
}: {
  videoUrl: string | null;
  thumbnailUrl: string | null;
  processing: boolean;
}) {
  const [showPlayer, setShowPlayer] = useState(false);

  if (processing) {
    return (
      <View style={s.videoCard}>
        <ActivityIndicator size="small" color="#6366f1" />
        <Text style={s.processingText}>Video generating...</Text>
      </View>
    );
  }

  if (!videoUrl) return null;

  return (
    <>
      <TouchableOpacity style={s.videoCard} onPress={() => setShowPlayer(true)}>
        {thumbnailUrl ? (
          <Image source={{ uri: thumbnailUrl }} style={s.thumbnail} />
        ) : (
          <View style={s.thumbnailPlaceholder} />
        )}
        <View style={s.playOverlay}>
          <Text style={s.playIcon}>▶</Text>
        </View>
      </TouchableOpacity>

      <Modal visible={showPlayer} animationType="fade" transparent>
        <View style={s.modalBg}>
          <TouchableOpacity style={s.closeBtn} onPress={() => setShowPlayer(false)}>
            <Text style={s.closeBtnText}>✕</Text>
          </TouchableOpacity>
          <Video
            source={{ uri: videoUrl }}
            style={s.fullVideo}
            useNativeControls
            resizeMode={ResizeMode.CONTAIN}
            shouldPlay
          />
        </View>
      </Modal>
    </>
  );
}

// ── AudioMiniPlayer ─────────────────────────────────────────────────────────

function AudioMiniPlayer({ uri }: { uri: string }) {
  const soundRef = useRef<Audio.Sound | null>(null);
  const [playing, setPlaying] = useState(false);

  const toggle = useCallback(async () => {
    if (playing && soundRef.current) {
      await soundRef.current.pauseAsync();
      setPlaying(false);
      return;
    }

    if (!soundRef.current) {
      const { sound } = await Audio.Sound.createAsync(
        { uri },
        { shouldPlay: true },
      );
      soundRef.current = sound;
      sound.setOnPlaybackStatusUpdate((status) => {
        if ('didJustFinish' in status && status.didJustFinish) {
          setPlaying(false);
          sound.unloadAsync();
          soundRef.current = null;
        }
      });
    } else {
      await soundRef.current.playAsync();
    }
    setPlaying(true);
  }, [playing, uri]);

  return (
    <TouchableOpacity style={s.audioRow} onPress={toggle}>
      <Text style={s.audioIcon}>{playing ? '⏸' : '▶'}</Text>
      <View style={s.audioBar}>
        <View style={[s.audioProgress, playing && s.audioProgressActive]} />
      </View>
      <Text style={s.audioLabel}>Audio</Text>
    </TouchableOpacity>
  );
}

// ── MediaAttachments ────────────────────────────────────────────────────────

interface Props {
  toolRuns?: ToolRun[];
  audioUrl?: string | null;
}

export default function MediaAttachments({ toolRuns, audioUrl }: Props) {
  const videos = (toolRuns ?? [])
    .filter(
      (tr) =>
        ['studio_tool', 'run_agent'].includes(tr.tool) &&
        (extractVideoUrl(tr) || isProcessing(tr)),
    )
    .map((tr) => ({
      url: extractVideoUrl(tr),
      thumb: extractThumbnail(tr),
      processing: isProcessing(tr),
    }));

  if (videos.length === 0 && !audioUrl) return null;

  return (
    <View style={s.container}>
      {videos.map((v, i) => (
        <VideoThumbnail
          key={i}
          videoUrl={v.url}
          thumbnailUrl={v.thumb}
          processing={v.processing}
        />
      ))}
      {audioUrl ? <AudioMiniPlayer uri={audioUrl} /> : null}
    </View>
  );
}

// ── Styles ──────────────────────────────────────────────────────────────────

const s = StyleSheet.create({
  container: { marginTop: 8, gap: 8 },
  videoCard: {
    backgroundColor: '#12121e',
    borderRadius: 8,
    height: 180,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  thumbnail: {
    width: '100%',
    height: '100%',
    borderRadius: 8,
  },
  thumbnailPlaceholder: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1a1a2e',
  },
  playOverlay: {
    ...StyleSheet.absoluteFillObject,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.35)',
  },
  playIcon: { fontSize: 36, color: '#ffffff' },
  processingText: { color: '#818cf8', fontSize: 13, marginTop: 6 },
  modalBg: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.95)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeBtn: { position: 'absolute', top: 50, right: 20, zIndex: 10 },
  closeBtnText: { color: '#ffffff', fontSize: 24 },
  fullVideo: { width: SCREEN_WIDTH, height: SCREEN_WIDTH * 0.5625 },
  audioRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#12121e',
    borderRadius: 8,
    padding: 10,
    gap: 8,
  },
  audioIcon: { fontSize: 18, color: '#818cf8' },
  audioBar: {
    flex: 1,
    height: 4,
    backgroundColor: '#2a2a3e',
    borderRadius: 2,
  },
  audioProgress: { width: '0%', height: '100%', backgroundColor: '#6366f1', borderRadius: 2 },
  audioProgressActive: { width: '50%' },
  audioLabel: { color: '#6b7280', fontSize: 12 },
});
