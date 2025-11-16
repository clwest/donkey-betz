/// Project Detail Screen - View project and its sessions
///
/// Session 101: Project Browser - Mobile Flutter App
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../core/app_theme.dart';
import '../../models/project.dart';
import '../../models/session.dart';
import '../../providers/projects_provider.dart';
import 'session_assets_screen.dart';

class ProjectDetailScreen extends ConsumerWidget {
  final String projectId;

  const ProjectDetailScreen({
    super.key,
    required this.projectId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final projectAsync = ref.watch(projectProvider(projectId));
    final sessionsAsync = ref.watch(projectSessionsProvider(projectId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Project Details'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await ref.refresh(projectProvider(projectId).future);
          await ref.refresh(projectSessionsProvider(projectId).future);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Project header
              projectAsync.when(
                loading: () => const LinearProgressIndicator(),
                error: (error, stack) => _buildErrorCard(
                  context,
                  'Error loading project: $error',
                ),
                data: (project) => _buildProjectHeader(context, project),
              ),

              const SizedBox(height: 8),

              // Sessions section
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Text(
                  'Sessions',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),

              sessionsAsync.when(
                loading: () => const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32),
                    child: CircularProgressIndicator(),
                  ),
                ),
                error: (error, stack) => _buildErrorCard(
                  context,
                  'Error loading sessions: $error',
                ),
                data: (sessions) {
                  if (sessions.isEmpty) {
                    return _buildEmptySessionsState(context);
                  }
                  return _buildSessionsList(context, sessions);
                },
              ),

              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProjectHeader(BuildContext context, Project project) {
    final dateFormat = DateFormat('MMM dd, yyyy');

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    _getProjectIcon(project.category),
                    size: 32,
                    color: AppTheme.primaryColor,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        project.name,
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      if (project.category != null)
                        Text(
                          project.category!,
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (project.description != null) ...[
              Text(
                project.description!,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 16),
            ],
            if (project.goal != null) ...[
              Row(
                children: [
                  Icon(Icons.flag, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Goal: ${project.goal}',
                      style: TextStyle(
                        color: Colors.grey[700],
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
            ],
            const Divider(),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStat(
                  Icons.image,
                  '${project.imageCount}',
                  'Images',
                ),
                _buildStat(
                  Icons.video_library,
                  '${project.videoCount}',
                  'Videos',
                ),
                _buildStat(
                  Icons.calendar_today,
                  dateFormat.format(project.createdAt),
                  'Created',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStat(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, size: 20, color: AppTheme.primaryColor),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildEmptySessionsState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            Icon(
              Icons.history,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'No Sessions Yet',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              'Start creating content to see sessions here',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSessionsList(BuildContext context, List<AISession> sessions) {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: sessions.length,
      itemBuilder: (context, index) {
        final session = sessions[index];
        return _buildSessionCard(context, session);
      },
    );
  }

  Widget _buildSessionCard(BuildContext context, AISession session) {
    final dateFormat = DateFormat('MMM dd, yyyy h:mm a');

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
          child: Text(
            '${session.imageCount + session.videoCount}',
            style: const TextStyle(
              color: AppTheme.primaryColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(
          session.title ?? 'Untitled Session',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(
              dateFormat.format(session.createdAt),
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                if (session.imageCount > 0) ...[
                  Icon(Icons.image, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    '${session.imageCount}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                  const SizedBox(width: 12),
                ],
                if (session.videoCount > 0) ...[
                  Icon(Icons.videocam, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    '${session.videoCount}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ],
            ),
          ],
        ),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => SessionAssetsScreen(
                sessionId: session.sessionId,
                sessionTitle: session.title ?? 'Untitled Session',
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildErrorCard(BuildContext context, String message) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.error_outline, color: AppTheme.errorColor),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: AppTheme.errorColor),
              ),
            ),
          ],
        ),
      ),
    );
  }

  IconData _getProjectIcon(String? category) {
    switch (category?.toLowerCase()) {
      case 'art':
      case 'artwork':
        return Icons.palette;
      case 'video':
      case 'videos':
        return Icons.video_library;
      case 'photo':
      case 'photography':
        return Icons.photo_camera;
      case 'design':
        return Icons.design_services;
      case 'music':
      case 'audio':
        return Icons.music_note;
      default:
        return Icons.folder;
    }
  }
}
