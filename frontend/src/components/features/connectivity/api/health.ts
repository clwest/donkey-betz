import { Logger } from '../../../../utils/logger';

export interface HealthProbeResult {
  success: boolean;
  status?: number;
  message: string;
  timestamp: number;
  responseTime?: number;
}

export interface CORSProbeResult extends HealthProbeResult {
  xOrchestratorAllowed: boolean;
  allowedHeaders?: string[];
}

/**
 * Probe API health endpoint
 * GET ${VITE_API_URL}/health/
 */
export async function probeAPIHealth(): Promise<HealthProbeResult> {
  const startTime = Date.now();
  const apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/v1$/, ''); // Root API for health/status endpoints
  
  try {
    Logger.api('PROBE', 'API Health Check', { url: `${apiUrl}/health/` });
    
    const response = await fetch(`${apiUrl}/health/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      // Don't include auth for health check
    });

    const responseTime = Date.now() - startTime;

    if (response.ok) {
      const data = await response.json();
      Logger.api('PROBE', 'API Health Success', { status: response.status, data, responseTime });
      
      return {
        success: true,
        status: response.status,
        message: data.status || 'API is healthy',
        timestamp: Date.now(),
        responseTime
      };
    } else {
      Logger.warn('PROBE', 'API Health Failed', { status: response.status, responseTime });
      
      return {
        success: false,
        status: response.status,
        message: `API returned ${response.status}: ${response.statusText}`,
        timestamp: Date.now(),
        responseTime
      };
    }
  } catch (error: any) {
    const responseTime = Date.now() - startTime;
    Logger.error('PROBE', 'API Health Error', { error: error.message, responseTime });
    
    return {
      success: false,
      message: `Connection failed: ${error.message}`,
      timestamp: Date.now(),
      responseTime
    };
  }
}

/**
 * Probe CORS preflight request
 * OPTIONS ${VITE_API_URL}/content/ 
 * Check that 'x-orchestrator' header is allowed
 */
export async function probeCORSPreflight(): Promise<CORSProbeResult> {
  const startTime = Date.now();
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'; // Use versioned API for app-specific endpoints
  
  try {
    Logger.api('PROBE', 'CORS Preflight Check', { url: `${apiUrl}/content/` });
    
    const response = await fetch(`${apiUrl}/content/`, {
      method: 'OPTIONS',
      headers: {
        'Origin': window.location.origin,
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'x-orchestrator,content-type,authorization'
      }
    });

    const responseTime = Date.now() - startTime;
    const allowedHeaders = response.headers.get('Access-Control-Allow-Headers')?.toLowerCase() || '';
    const xOrchestratorAllowed = allowedHeaders.includes('x-orchestrator');

    Logger.api('PROBE', 'CORS Preflight Response', {
      status: response.status,
      allowedHeaders,
      xOrchestratorAllowed,
      responseTime
    });

    if (response.ok || response.status === 200 || response.status === 204) {
      return {
        success: true,
        status: response.status,
        message: xOrchestratorAllowed 
          ? 'CORS configured correctly with x-orchestrator header'
          : 'CORS working but x-orchestrator header not allowed',
        timestamp: Date.now(),
        responseTime,
        xOrchestratorAllowed,
        allowedHeaders: allowedHeaders.split(',').map(h => h.trim()).filter(Boolean)
      };
    } else {
      return {
        success: false,
        status: response.status,
        message: `CORS preflight failed: ${response.status} ${response.statusText}`,
        timestamp: Date.now(),
        responseTime,
        xOrchestratorAllowed: false,
        allowedHeaders: []
      };
    }
  } catch (error: any) {
    const responseTime = Date.now() - startTime;
    Logger.error('PROBE', 'CORS Preflight Error', { error: error.message, responseTime });
    
    return {
      success: false,
      message: `CORS preflight failed: ${error.message}`,
      timestamp: Date.now(),
      responseTime,
      xOrchestratorAllowed: false,
      allowedHeaders: []
    };
  }
}

/**
 * Run all API probes at once
 */
export async function runAllAPIProbes() {
  const [healthResult, corsResult] = await Promise.all([
    probeAPIHealth(),
    probeCORSPreflight()
  ]);

  return {
    health: healthResult,
    cors: corsResult
  };
}