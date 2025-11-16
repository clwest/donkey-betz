/// MiniFig Detail Screen - Session 111
///
/// Shows detailed information about a single mini-fig asset:
/// - Preview image and 3D file info
/// - Generation metadata (style, scale, parameters)
/// - User notes and tags
/// - Download button
/// - Source references (pipeline run, source image)

library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:donkey_os_cockpit/core/app_theme.dart';
import 'package:donkey_os_cockpit/models/minifig_asset.dart';
import 'package:donkey_os_cockpit/providers/minifigs_provider.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

class MiniFigDetailScreen extends ConsumerStatefulWidget {
  final String minifigId;

  const MiniFigDetailScreen({
    super.key,
    required this.minifigId,
  });

  @override
  ConsumerState<MiniFigDetailScreen> createState() =>
      _MiniFigDetailScreenState();
}

class _MiniFigDetailScreenState extends ConsumerState<MiniFigDetailScreen> {
  @override
  Widget build(BuildContext context) {
    final detailState = ref.watch(minifigDetailProvider(widget.minifigId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('MiniFig Details'),
        backgroundColor: AppTheme.primaryColor,
        actions: [
          if (detailState.minifig != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              tooltip: 'Refresh',
              onPressed: () {
                ref
                    .read(minifigDetailProvider(widget.minifigId).notifier)
                    .refresh();
              },
            ),
        ],
      ),
      body: detailState.isLoading && detailState.minifig == null
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Loading mini-fig details...'),
                ],
              ),
            )
          : detailState.error != null && detailState.minifig == null
              ? _buildErrorState(detailState.error!)
              : detailState.minifig != null
                  ? _buildMiniFigDetails(detailState.minifig!)
                  : const Center(child: Text('MiniFig not found')),
    );
  }

  Widget _buildMiniFigDetails(MiniFigAsset minifig) {
    return RefreshIndicator(
      onRefresh: () async {
        await ref
            .read(minifigDetailProvider(widget.minifigId).notifier)
            .refresh();
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildPreviewCard(minifig),
            const SizedBox(height: 16),
            _buildStatusCard(minifig),
            const SizedBox(height: 16),
            if (minifig.isReady) ...[
              _buildDownloadCard(minifig),
              const SizedBox(height: 16),
            ],
            _buildMetadataCard(minifig),
            const SizedBox(height: 16),
            if (minifig.userNotes.isNotEmpty || minifig.tags.isNotEmpty) ...[
              _buildNotesAndTagsCard(minifig),
              const SizedBox(height: 16),
            ],
            _buildInfoCard(minifig),
          ],
        ),
      ),
    );
  }

  Widget _buildPreviewCard(MiniFigAsset minifig) {
    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Preview image or placeholder
          Container(
            height: 300,
            decoration: BoxDecoration(
              color: minifig.hasPreview
                  ? Colors.black
                  : Color(minifig.statusColor).withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: minifig.hasPreview
                ? ClipRRect(
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(12),
                      topRight: Radius.circular(12),
                    ),
                    child: Image.network(
                      minifig.previewImageUrl!,
                      fit: BoxFit.contain,
                      errorBuilder: (context, error, stackTrace) {
                        return _buildPlaceholderIcon(minifig);
                      },
                    ),
                  )
                : _buildPlaceholderIcon(minifig),
          ),
          // Title and favorite button
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    minifig.title,
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Icon(
                  minifig.isFavorite ? Icons.favorite : Icons.favorite_border,
                  color: minifig.isFavorite ? Colors.pink : Colors.grey,
                  size: 28,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlaceholderIcon(MiniFigAsset minifig) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            minifig.isReady
                ? Icons.view_in_ar
                : minifig.isProcessing
                    ? Icons.hourglass_empty
                    : Icons.error_outline,
            size: 80,
            color: Color(minifig.statusColor),
          ),
          const SizedBox(height: 16),
          Text(
            minifig.hasPreview ? 'Failed to load preview' : 'No preview available',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusCard(MiniFigAsset minifig) {
    final dateFormatter = DateFormat('MMM d, y • h:mm a');

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Status',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Color(minifig.statusColor).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    minifig.isReady
                        ? Icons.check_circle
                        : minifig.isProcessing
                            ? Icons.sync
                            : minifig.isFailed
                                ? Icons.error
                                : Icons.schedule,
                    size: 32,
                    color: Color(minifig.statusColor),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        minifig.statusText,
                        style: TextStyle(
                          fontSize: 18,
                          color: Color(minifig.statusColor),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        minifig.providerName,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            if (minifig.errorMessage != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withOpacity(0.3)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        minifig.errorMessage!,
                        style: const TextStyle(
                          fontSize: 13,
                          color: Colors.red,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            const Divider(height: 24),
            _buildInfoRow(
              icon: Icons.calendar_today,
              label: 'Created',
              value: dateFormatter.format(minifig.createdAt),
            ),
            const SizedBox(height: 8),
            _buildInfoRow(
              icon: Icons.update,
              label: 'Updated',
              value: dateFormatter.format(minifig.updatedAt),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDownloadCard(MiniFigAsset minifig) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '3D File',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  Icons.insert_drive_file,
                  size: 32,
                  color: AppTheme.primaryColor,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        minifig.fileFormat,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Ready for 3D printing',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _downloadFile(minifig.threeDFile),
                icon: const Icon(Icons.download),
                label: const Text('Download 3D File'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryColor,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetadataCard(MiniFigAsset minifig) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Generation Details',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _buildInfoRow(
              icon: Icons.palette,
              label: 'Style',
              value: minifig.style,
            ),
            const SizedBox(height: 8),
            _buildInfoRow(
              icon: Icons.straighten,
              label: 'Scale',
              value: minifig.scale,
            ),
            if (minifig.metadata.isNotEmpty) ...[
              const Divider(height: 24),
              const Text(
                'Additional Metadata',
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              ...minifig.metadata.entries
                  .where((e) => e.key != 'style' && e.key != 'scale')
                  .map((e) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: _buildInfoRow(
                          icon: Icons.info_outline,
                          label: e.key,
                          value: e.value.toString(),
                        ),
                      )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildNotesAndTagsCard(MiniFigAsset minifig) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Notes & Tags',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (minifig.userNotes.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                minifig.userNotes,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[800],
                  height: 1.4,
                ),
              ),
            ],
            if (minifig.tags.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: minifig.tags.map((tag) {
                  return Chip(
                    label: Text(tag),
                    backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                    labelStyle: const TextStyle(
                      fontSize: 12,
                      color: AppTheme.primaryColor,
                    ),
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard(MiniFigAsset minifig) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Additional Information',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _buildInfoRow(
              icon: Icons.remove_red_eye,
              label: 'View Count',
              value: '${minifig.viewCount}',
            ),
            const SizedBox(height: 8),
            _buildInfoRow(
              icon: Icons.file_download,
              label: 'Downloads',
              value: '${minifig.downloadCount}',
            ),
            if (minifig.sourcePipelineRunId != null) ...[
              const SizedBox(height: 8),
              _buildCopyableRow(
                icon: Icons.account_tree,
                label: 'Pipeline Run',
                value: minifig.sourcePipelineRunId!,
              ),
            ],
            if (minifig.sourceImageAssetId != null) ...[
              const SizedBox(height: 8),
              _buildCopyableRow(
                icon: Icons.image,
                label: 'Source Image',
                value: minifig.sourceImageAssetId!,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Colors.grey[600]),
        const SizedBox(width: 8),
        Text(
          '$label:',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey[700],
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              color: AppTheme.textPrimary,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCopyableRow({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Row(
      children: [
        Icon(icon, size: 18, color: Colors.grey[600]),
        const SizedBox(width: 8),
        Text(
          '$label:',
          style: TextStyle(
            fontSize: 13,
            color: Colors.grey[700],
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value.substring(0, 8),
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
              fontFamily: 'monospace',
            ),
          ),
        ),
        IconButton(
          icon: const Icon(Icons.copy, size: 16),
          onPressed: () => _copyToClipboard(value),
          tooltip: 'Copy ID',
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(),
        ),
      ],
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red[300],
            ),
            const SizedBox(height: 16),
            const Text(
              'Failed to Load MiniFig',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                ref
                    .read(minifigDetailProvider(widget.minifigId).notifier)
                    .refresh();
              },
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _downloadFile(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Opening download...'),
            backgroundColor: AppTheme.successColor,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } else {
      // Show error message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Failed to open download URL'),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 3),
          ),
        );
      }
    }
  }

  Future<void> _copyToClipboard(String text) async {
    await Clipboard.setData(ClipboardData(text: text));
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('ID copied to clipboard'),
          backgroundColor: AppTheme.successColor,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }
}
