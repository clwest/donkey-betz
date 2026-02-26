import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  FlatList,
  Image,
  KeyboardAvoidingView,
  Modal,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  ActivityIndicator,
} from 'react-native';
import Markdown from 'react-native-markdown-display';
import { useAuthStore } from '../auth/authStore';
import * as assistantApi from '../api/assistant';
import MediaAttachments from '../components/MediaAttachments';
import {
  getActiveConversationId,
  setActiveConversationId,
  clearActiveConversationId,
} from '../storage/conversationStore';

// ── Types ────────────────────────────────────────────────────────────────────

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  toolRuns?: assistantApi.ToolRun[];
  audioUrl?: string | null;
  loading?: boolean;
}

// ── Polling helper ───────────────────────────────────────────────────────────

const POLL_INTERVAL = 2000;
const POLL_TIMEOUT = 300_000; // 5 minutes max

// ── Screen ───────────────────────────────────────────────────────────────────

export default function CommandCenterScreen() {
  const user = useAuthStore((s) => s.user);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [zoomImage, setZoomImage] = useState<string | null>(null);

  const flatListRef = useRef<FlatList>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Restore active conversation on mount
  useEffect(() => {
    getActiveConversationId().then((id) => {
      if (id) {
        setConversationId(id);
        loadConversation(id);
      }
    });
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const loadConversation = async (id: string) => {
    try {
      const detail = await assistantApi.getConversation(id);
      setMessages(
        detail.messages.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          toolRuns: m.tools_used?.map((t) => ({ tool: t, ok: true, latency_ms: 0 })),
        })),
      );
    } catch {
      // Conversation may have been deleted — start fresh
      await clearActiveConversationId();
      setConversationId(null);
    }
  };

  const scrollToBottom = useCallback(() => {
    setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
  }, []);

  // ── Send message ─────────────────────────────────────────────────────────

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    setInput('');
    setError(null);
    setSending(true);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
    };

    const loadingMsg: ChatMessage = {
      id: `loading-${Date.now()}`,
      role: 'assistant',
      content: '',
      loading: true,
    };

    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    scrollToBottom();

    try {
      const response = await assistantApi.paChat(text, {
        conversation_id: conversationId ?? undefined,
        context: { current_page: '/command-center', platform: 'mobile' },
        source: 'mobile',
        platform: 'mobile',
      });

      pollForResult(response.task_id, loadingMsg.id);
    } catch (err) {
      setMessages((prev) => prev.filter((m) => m.id !== loadingMsg.id));
      setError('Failed to send message. Tap to retry.');
      setSending(false);
    }
  };

  // ── Poll for async result ────────────────────────────────────────────────

  const pollForResult = (taskId: string, loadingMsgId: string) => {
    const startTime = Date.now();

    pollRef.current = setInterval(async () => {
      try {
        if (Date.now() - startTime > POLL_TIMEOUT) {
          clearInterval(pollRef.current!);
          pollRef.current = null;
          replaceLoading(loadingMsgId, 'Request timed out. Please try again.');
          setSending(false);
          return;
        }

        const status = await assistantApi.paChatStatus(taskId);

        if (status.status === 'completed') {
          clearInterval(pollRef.current!);
          pollRef.current = null;

          // Persist conversation_id
          if (status.conversation_id && !conversationId) {
            setConversationId(status.conversation_id);
            await setActiveConversationId(status.conversation_id);
          }

          setMessages((prev) =>
            prev.map((m) =>
              m.id === loadingMsgId
                ? {
                    ...m,
                    content: status.content ?? '',
                    toolRuns: status.tool_runs,
                    audioUrl: status.audio_url,
                    loading: false,
                  }
                : m,
            ),
          );
          scrollToBottom();
          setSending(false);
        } else if (status.status === 'failed') {
          clearInterval(pollRef.current!);
          pollRef.current = null;
          replaceLoading(loadingMsgId, status.error ?? 'Request failed.');
          setSending(false);
        }
        // 'processing' — keep polling
      } catch {
        // Network blip — keep polling, don't abort
      }
    }, POLL_INTERVAL);
  };

  const replaceLoading = (loadingMsgId: string, content: string) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.id === loadingMsgId ? { ...m, content, loading: false } : m,
      ),
    );
  };

  // ── New conversation ─────────────────────────────────────────────────────

  const handleNewConversation = async () => {
    await clearActiveConversationId();
    setConversationId(null);
    setMessages([]);
    setError(null);
  };

  // ── Render ───────────────────────────────────────────────────────────────

  const renderMessage = ({ item }: { item: ChatMessage }) => {
    const isUser = item.role === 'user';

    if (item.loading) {
      return (
        <View style={[styles.bubble, styles.assistantBubble]}>
          <ActivityIndicator size="small" color="#6366f1" />
          <Text style={styles.thinkingText}>Thinking...</Text>
        </View>
      );
    }

    const imageRules = {
      image: (
        node: { attributes: { src?: string; alt?: string } },
      ) => (
        <TouchableOpacity
          key={node.attributes.src}
          onPress={() => setZoomImage(node.attributes.src ?? null)}
          activeOpacity={0.8}
        >
          <Image
            source={{ uri: node.attributes.src }}
            style={styles.inlineImage}
            resizeMode="cover"
            accessibilityLabel={node.attributes.alt ?? 'image'}
          />
        </TouchableOpacity>
      ),
    };

    return (
      <View style={[styles.bubble, isUser ? styles.userBubble : styles.assistantBubble]}>
        {isUser ? (
          <Text style={styles.userText}>{item.content}</Text>
        ) : (
          <Markdown style={markdownStyles} rules={imageRules}>
            {item.content}
          </Markdown>
        )}
        <MediaAttachments toolRuns={item.toolRuns} audioUrl={item.audioUrl} />
        {item.toolRuns && item.toolRuns.length > 0 && (
          <View style={styles.toolBar}>
            {item.toolRuns.map((t, i) => (
              <Text key={i} style={[styles.toolChip, !t.ok && styles.toolChipError]}>
                {t.tool}
              </Text>
            ))}
          </View>
        )}
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}
    >
      {/* Header bar */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          {conversationId ? 'Conversation' : 'New Chat'}
        </Text>
        <TouchableOpacity onPress={handleNewConversation}>
          <Text style={styles.newChat}>New</Text>
        </TouchableOpacity>
      </View>

      {/* Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id}
        renderItem={renderMessage}
        contentContainerStyle={styles.messageList}
        onContentSizeChange={scrollToBottom}
      />

      {/* Error banner */}
      {error && (
        <TouchableOpacity style={styles.errorBanner} onPress={() => setError(null)}>
          <Text style={styles.errorBannerText}>{error}</Text>
        </TouchableOpacity>
      )}

      {/* Image zoom modal */}
      <Modal visible={!!zoomImage} transparent animationType="fade">
        <TouchableOpacity
          style={styles.zoomOverlay}
          activeOpacity={1}
          onPress={() => setZoomImage(null)}
        >
          {zoomImage && (
            <Image
              source={{ uri: zoomImage }}
              style={styles.zoomImage}
              resizeMode="contain"
            />
          )}
        </TouchableOpacity>
      </Modal>

      {/* Input */}
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder="Ask the PA anything..."
          placeholderTextColor="#6b7280"
          value={input}
          onChangeText={setInput}
          onSubmitEditing={handleSend}
          editable={!sending}
          multiline
          maxLength={4000}
        />
        <TouchableOpacity
          style={[styles.sendButton, (!input.trim() || sending) && styles.sendDisabled]}
          onPress={handleSend}
          disabled={!input.trim() || sending}
        >
          <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0f',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a2e',
  },
  headerTitle: {
    color: '#d1d5db',
    fontSize: 15,
    fontWeight: '600',
  },
  newChat: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600',
  },
  messageList: {
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  bubble: {
    maxWidth: '85%',
    borderRadius: 12,
    padding: 12,
    marginVertical: 4,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#6366f1',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#1a1a2e',
  },
  userText: {
    color: '#ffffff',
    fontSize: 15,
    lineHeight: 21,
  },
  thinkingText: {
    color: '#6b7280',
    fontSize: 13,
    marginLeft: 8,
  },
  toolBar: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
    gap: 4,
  },
  toolChip: {
    backgroundColor: 'rgba(99, 102, 241, 0.2)',
    color: '#818cf8',
    fontSize: 11,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    overflow: 'hidden',
  },
  toolChipError: {
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    color: '#ef4444',
  },
  errorBanner: {
    backgroundColor: 'rgba(239, 68, 68, 0.15)',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  errorBannerText: {
    color: '#ef4444',
    fontSize: 13,
    textAlign: 'center',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#1a1a2e',
  },
  input: {
    flex: 1,
    backgroundColor: '#1a1a2e',
    color: '#ffffff',
    fontSize: 15,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: '#6366f1',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginLeft: 8,
  },
  sendDisabled: {
    opacity: 0.4,
  },
  sendText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '600',
  },
  inlineImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginVertical: 8,
  },
  zoomOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.92)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  zoomImage: {
    width: '95%',
    height: '80%',
  },
});

const markdownStyles = {
  body: { color: '#d1d5db', fontSize: 15, lineHeight: 22 },
  image: { borderRadius: 8, marginVertical: 8 },
  heading1: { color: '#ffffff', fontSize: 20, fontWeight: '700' as const, marginBottom: 8 },
  heading2: { color: '#ffffff', fontSize: 18, fontWeight: '600' as const, marginBottom: 6 },
  heading3: { color: '#ffffff', fontSize: 16, fontWeight: '600' as const, marginBottom: 4 },
  strong: { color: '#ffffff', fontWeight: '600' as const },
  link: { color: '#818cf8' },
  code_inline: {
    backgroundColor: '#2a2a3e',
    color: '#a5b4fc',
    fontSize: 13,
    paddingHorizontal: 4,
    borderRadius: 3,
  },
  fence: {
    backgroundColor: '#1e1e30',
    color: '#d1d5db',
    fontSize: 13,
    padding: 12,
    borderRadius: 8,
  },
  bullet_list: { color: '#d1d5db' },
  ordered_list: { color: '#d1d5db' },
  table: { borderColor: '#2a2a3e' },
  tr: { borderBottomColor: '#2a2a3e' },
  th: { color: '#ffffff', fontWeight: '600' as const },
  td: { color: '#d1d5db' },
};
