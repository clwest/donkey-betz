/// API Configuration for DonkeyOS Backend
///
/// Session 100 Part 13 - Flutter Cockpit Integration
/// Session 102 - Mobile Auth & Connection Settings (Dynamic config support)
/// Session 115 - Platform-aware URL configuration (web vs mobile)
library;

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConfig {
  /// Default base URL for web (localhost works in browser)
  static const String defaultWebUrl = 'http://localhost:8000';

  /// Default base URL for mobile (127.0.0.1 for iOS/Android simulators)
  static const String defaultMobileUrl = 'http://127.0.0.1:8000';

  /// Default base URL - automatically selects based on platform
  static String get defaultBaseUrl => kIsWeb ? defaultWebUrl : defaultMobileUrl;

  /// Base URL from environment (deprecated - use settings provider instead)
  @Deprecated('Use settings provider for dynamic configuration')
  static String get baseUrl =>
      dotenv.env['API_BASE_URL'] ?? defaultBaseUrl;

  /// Default API key for mobile_test user (Session 115)
  static String get defaultApiKey =>
      dotenv.env['AUTH_TOKEN'] ?? '2e63ae5a6eb6e506f757351f2e2f2db9021d3498';

  /// API Endpoints
  static const String projectsEndpoint = '/api/creative-projects/';
  static const String sessionsEndpoint = '/api/v1/sessions/';
  static const String boardroomEndpoint = '/api/v1/coleadership/boardroom/';
  static const String coleadershipEndpoint = '/api/v1/coleadership/';
  static const String leadershipEndpoint = '/api/leadership/';
  static const String renderJobsEndpoint = '/api/v1/render-jobs/'; // Session 105
  static const String pipelinesEndpoint = '/api/v1/pipelines/'; // Session 109

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
