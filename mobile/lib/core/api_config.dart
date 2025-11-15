/// API Configuration for DonkeyOS Backend
///
/// Session 100 Part 13 - Flutter Cockpit Integration
/// Session 102 - Mobile Auth & Connection Settings (Dynamic config support)
library;

import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  /// Default base URL for development (used as fallback)
  static const String defaultBaseUrl = 'http://localhost:8000';

  /// Base URL from environment (deprecated - use settings provider instead)
  @Deprecated('Use settings provider for dynamic configuration')
  static String get baseUrl =>
      dotenv.env['API_BASE_URL'] ?? defaultBaseUrl;

  /// API Endpoints
  static const String projectsEndpoint = '/api/creative-projects/';
  static const String sessionsEndpoint = '/api/v1/sessions/';
  static const String boardroomEndpoint = '/api/v1/coleadership/boardroom/';
  static const String coleadershipEndpoint = '/api/v1/coleadership/';
  static const String leadershipEndpoint = '/api/leadership/';

  /// Timeout durations
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 60);

  /// Executive agent names (matches backend)
  static const List<String> executiveAgents = [
    'CTOAgent',
    'COOAgent',
    'ProductManagerAgent',
    'LegalAgent',
    'MarketingAgent',
    'StrategyAgent',
    'HRAgent',
    'CFOAgent',
  ];

  /// Executive agent display names
  static const Map<String, String> agentDisplayNames = {
    'CTOAgent': 'CTO',
    'COOAgent': 'COO',
    'ProductManagerAgent': 'Product Manager',
    'LegalAgent': 'Legal Counsel',
    'MarketingAgent': 'Marketing Director',
    'StrategyAgent': 'Strategy Officer',
    'HRAgent': 'HR Director',
    'CFOAgent': 'CFO',
  };

  /// Get display name for an agent
  static String getAgentDisplayName(String agentName) {
    return agentDisplayNames[agentName] ?? agentName;
  }

  /// Priority colors
  static const Map<String, String> priorityColors = {
    'high': '#EF4444',
    'medium': '#F97316',
    'low': '#10B981',
  };
}
