/// Personal Assistant Screen - Chat Interface
///
/// Session 112: Personal Assistant Mobile MVP
/// Session 113: Voice Input MVP
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/app_theme.dart';
import '../../models/personal_assistant.dart';
import '../../providers/personal_assistant_provider.dart';
import '../../providers/assistant_voice_provider.dart';

class PersonalAssistantScreen extends ConsumerStatefulWidget {
  const PersonalAssistantScreen({super.key});

  @override
  ConsumerState<PersonalAssistantScreen> createState() =>
      _PersonalAssistantScreenState();
}

class _PersonalAssistantScreenState
    extends ConsumerState<PersonalAssistantScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isSending = false;

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty || _isSending) return;

    setState(() {
      _isSending = true;
    });

    _messageController.clear();

    try {
      await ref
          .read(assistantConversationProvider.notifier)
          .sendMessage(text);

      // Scroll to bottom after sending
      Future.delayed(const Duration(milliseconds: 100), _scrollToBottom);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to send message: $e'),
            backgroundColor: AppTheme.errorColor,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSending = false;
        });
      }
    }
  }

  /// Handle microphone button tap - Session 113: Voice Input
  void _handleMicTap() async {
    final voiceState = ref.read(voiceRecordingProvider);

    if (voiceState.state == VoiceRecordingState.idle) {
      // Start recording
      await ref.read(voiceRecordingProvider.notifier).startRecording();
    } else if (voiceState.state == VoiceRecordingState.recording) {
      // Stop and send
      await ref.read(voiceRecordingProvider.notifier).stopAndSend();

      // Scroll to bottom after sending
      Future.delayed(const Duration(milliseconds: 500), _scrollToBottom);
    }
  }

  @override
  Widget build(BuildContext context) {
    final conversation = ref.watch(assistantConversationProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Personal Assistant'),
        backgroundColor: AppTheme.primaryColor,
        actions: [
          // Clear conversation
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () {
              ref.read(assistantConversationProvider.notifier).clearConversation();
            },
            tooltip: 'Clear conversation',
          ),

          // Refresh/Settings menu
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'clear') {
                ref.read(assistantConversationProvider.notifier).clearConversation();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'clear',
                child: Row(
                  children: [
                    Icon(Icons.delete_outline, size: 20),
                    SizedBox(width: 12),
                    Text('Clear Chat'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          // Chat messages
          Expanded(
            child: conversation.messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: conversation.messages.length,
                    itemBuilder: (context, index) {
                      final message = conversation.messages[index];
                      return _buildMessageBubble(message);
                    },
                  ),
          ),

          // Voice recording status banner (Session 113)
          Consumer(
            builder: (context, ref, child) {
              final voiceState = ref.watch(voiceRecordingProvider);

              // Show error if present
              if (voiceState.state == VoiceRecordingState.error) {
                WidgetsBinding.instance.addPostFrameCallback((_) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(voiceState.errorMessage ?? 'Voice input error'),
                        backgroundColor: AppTheme.errorColor,
                        action: SnackBarAction(
                          label: 'Dismiss',
                          textColor: Colors.white,
                          onPressed: () {
                            ref.read(voiceRecordingProvider.notifier).clearError();
                          },
                        ),
                      ),
                    );
                  }
                });
              }

              if (voiceState.state == VoiceRecordingState.recording) {
                return Container(
                  padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                  color: Colors.red[50],
                  child: Row(
                    children: [
                      Icon(Icons.fiber_manual_record, color: Colors.red, size: 12),
                      const SizedBox(width: 8),
                      const Text(
                        'Recording... Tap mic to stop and send',
                        style: TextStyle(
                          color: Colors.red,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                );
              }

              if (voiceState.state == VoiceRecordingState.uploading) {
                return Container(
                  padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                  color: AppTheme.primaryColor.withOpacity(0.1),
                  child: Row(
                    children: [
                      SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            AppTheme.primaryColor,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Transcribing and processing...',
                        style: TextStyle(
                          color: AppTheme.primaryColor,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                );
              }

              return const SizedBox.shrink();
            },
          ),

          // Loading indicator
          if (_isSending)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
              child: Row(
                children: [
                  const SizedBox(width: 40), // Align with assistant messages
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(
                          width: 12,
                          height: 12,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(
                              AppTheme.primaryColor,
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        const Text(
                          'Thinking...',
                          style: TextStyle(
                            fontSize: 14,
                            fontStyle: FontStyle.italic,
                            color: Colors.grey,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

          // Input bar
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.chat_bubble_outline,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'Hi! I\'m your Personal Assistant',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.grey[600],
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'I can help you with your projects, content creation, and more!',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            Text(
              'Try asking:',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[500],
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            ..._buildSuggestionChips(),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildSuggestionChips() {
    final suggestions = [
      'What projects am I working on?',
      'Tell me about my recent work',
      'What can you help me with?',
    ];

    return suggestions
        .map(
          (suggestion) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: ActionChip(
              label: Text(suggestion),
              onPressed: () {
                _messageController.text = suggestion;
                _sendMessage();
              },
              avatar: const Icon(Icons.lightbulb_outline, size: 18),
              backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
            ),
          ),
        )
        .toList();
  }

  Widget _buildMessageBubble(AssistantMessage message) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment:
            message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          // Avatar for assistant
          if (!message.isUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
              child: const Icon(
                Icons.smart_toy,
                size: 18,
                color: AppTheme.primaryColor,
              ),
            ),
            const SizedBox(width: 8),
          ],

          // Message bubble
          Flexible(
            child: Column(
              crossAxisAlignment: message.isUser
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: message.isUser
                        ? AppTheme.primaryColor
                        : Colors.grey[200],
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        message.text,
                        style: TextStyle(
                          color: message.isUser ? Colors.white : Colors.black87,
                          fontSize: 15,
                        ),
                      ),

                      // Confidence indicator for assistant
                      if (!message.isUser && message.confidence != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          'Confidence: ${(message.confidence! * 100).toInt()}%',
                          style: TextStyle(
                            fontSize: 11,
                            color: message.isUser
                                ? Colors.white70
                                : Colors.grey[600],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),

                // Suggested actions
                if (message.suggestedActions != null &&
                    message.suggestedActions!.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 4,
                    children: message.suggestedActions!
                        .map(
                          (action) => ActionChip(
                            label: Text(
                              action,
                              style: const TextStyle(fontSize: 12),
                            ),
                            onPressed: () {
                              _messageController.text = action;
                            },
                            visualDensity: VisualDensity.compact,
                          ),
                        )
                        .toList(),
                  ),
                ],

                // Timestamp
                const SizedBox(height: 4),
                Text(
                  _formatTime(message.timestamp),
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),

          // Avatar for user
          if (message.isUser) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              radius: 16,
              backgroundColor: AppTheme.primaryColor,
              child: const Icon(
                Icons.person,
                size: 18,
                color: Colors.white,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Text input
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: 'Type a message...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide(color: Colors.grey[300]!),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide(color: Colors.grey[300]!),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: const BorderSide(color: AppTheme.primaryColor),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
                filled: true,
                fillColor: Colors.grey[50],
              ),
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
              enabled: !_isSending,
            ),
          ),
          const SizedBox(width: 8),

          // Mic button (Session 113: Voice Input)
          Consumer(
            builder: (context, ref, child) {
              final voiceState = ref.watch(voiceRecordingProvider);
              final isRecording = voiceState.state == VoiceRecordingState.recording;
              final isUploading = voiceState.state == VoiceRecordingState.uploading;

              return IconButton(
                onPressed: isUploading ? null : _handleMicTap,
                icon: Icon(isRecording ? Icons.stop : Icons.mic),
                color: isRecording ? Colors.red : AppTheme.primaryColor,
                disabledColor: Colors.grey[400],
                tooltip: isRecording
                    ? 'Stop recording'
                    : isUploading
                        ? 'Processing...'
                        : 'Voice input',
              );
            },
          ),

          // Send button
          IconButton(
            onPressed: _isSending ? null : _sendMessage,
            icon: const Icon(Icons.send),
            color: AppTheme.primaryColor,
            disabledColor: Colors.grey[400],
            tooltip: 'Send message',
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final messageDate = DateTime(time.year, time.month, time.day);

    if (messageDate == today) {
      return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
    } else {
      return '${time.month}/${time.day} ${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
    }
  }
}
