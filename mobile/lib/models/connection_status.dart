/// Connection Status Enum
///
/// Session 102 - Mobile Auth & Connection Settings
library;

/// Connection test result status
enum ConnectionStatus {
  /// Successfully connected to the backend
  connected,

  /// Connection test failed
  failed,

  /// API endpoint or key not configured yet
  notConfigured;

  /// Display name for UI
  String get displayName {
    switch (this) {
      case ConnectionStatus.connected:
        return 'Connected';
      case ConnectionStatus.failed:
        return 'Connection Failed';
      case ConnectionStatus.notConfigured:
        return 'Not Configured';
    }
  }

  /// Whether this status represents a successful state
  bool get isSuccess => this == ConnectionStatus.connected;

  /// Whether this status represents an error state
  bool get isError => this == ConnectionStatus.failed;
}
