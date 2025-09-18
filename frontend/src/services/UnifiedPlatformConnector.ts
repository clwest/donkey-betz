/**
 * Unified Platform Connector
 * Connects all platform components with real data flows and WebSocket integration
 */

interface WebSocketMessage {
  type: string;
  data?: any;
  source?: string;
  target?: string;
  timestamp?: string;
}

interface ComponentContext {
  component: string;
  connected: boolean;
  lastMessage?: WebSocketMessage;
  dataCache?: any;
}

class UnifiedPlatformConnector {
  private ws: WebSocket | null = null;
  private components: Map<string, ComponentContext> = new Map();
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private connectionCallbacks: (() => void)[] = [];

  constructor() {
    this.initializeComponents();
  }

  private initializeComponents() {
    // Register all platform components
    const componentList = [
      'personal_assistant',
      'income_builder',
      'revenue_dashboard',
      'neural_orchestra',
      'decision_command',
      'job_tracker',
      'spider_network'
    ];

    componentList.forEach(component => {
      this.components.set(component, {
        component,
        connected: false
      });
    });
  }

  /**
   * Connect to the unified WebSocket hub
   */
  public async connect(component: string): Promise<boolean> {
    try {
      const wsUrl = this.getWebSocketUrl(component);
      console.log(`🔌 Connecting ${component} to Unified Hub at ${wsUrl}`);

      this.ws = new WebSocket(wsUrl);

      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Connection timeout'));
        }, 10000);

        this.ws!.onopen = () => {
          clearTimeout(timeout);
          console.log(`✅ ${component} connected to Unified Hub`);

          // Update component status
          this.updateComponentStatus(component, true);

          // Send initial connection message
          this.send({
            type: 'connection',
            source: component,
            data: { component, timestamp: new Date().toISOString() }
          });

          // Activate platform pipeline
          this.activatePlatformPipeline(component);

          this.reconnectAttempts = 0;
          resolve(true);
        };

        this.ws!.onmessage = (event) => {
          this.handleMessage(event.data);
        };

        this.ws!.onclose = () => {
          console.log(`🔌 ${component} disconnected from Unified Hub`);
          this.updateComponentStatus(component, false);
          this.handleReconnection(component);
        };

        this.ws!.onerror = (error) => {
          console.error(`❌ WebSocket error for ${component}:`, error);
          clearTimeout(timeout);
          reject(error);
        };
      });

    } catch (error) {
      console.error(`Failed to connect ${component}:`, error);
      return false;
    }
  }

  private getWebSocketUrl(component: string): string {
    const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

    // Map component names to actual WebSocket endpoints
    const endpointMap: { [key: string]: string } = {
      'opportunities_hub': '/ws/income-builder/', // Unified hub uses income-builder endpoint
      'income_builder': '/ws/income-builder/',
      'revenue_dashboard': '/ws/revenue-dashboard/',
      'decision_command': '/ws/decision-command/',
      'neural_orchestra': '/ws/neural-orchestra/',
      'control_center': '/ws/control-center/',
      'revenue_opportunities': '/ws/revenue-opportunities/',
      'monetization_hub': '/ws/monetization-hub/',
      'personal_assistant': '/ws/assistant/',
      'job_tracker': '/ws/agent-progress/',
      'spider_network': '/ws/agent-updates/'
    };

    const endpoint = endpointMap[component] || `/ws/${component.replace('_', '-')}/`;
    return `${baseUrl}${endpoint}`;
  }

  private updateComponentStatus(component: string, connected: boolean) {
    const context = this.components.get(component);
    if (context) {
      context.connected = connected;
      this.components.set(component, context);
    }
  }

  private handleMessage(data: string) {
    try {
      const message: WebSocketMessage = JSON.parse(data);
      console.log(`📨 Unified Hub message:`, message.type, message);

      // Store message in component context
      if (message.source) {
        const context = this.components.get(message.source);
        if (context) {
          context.lastMessage = message;
          context.dataCache = message.data;
          this.components.set(message.source, context);
        }
      }

      // Route message to handlers
      this.routeMessage(message);

    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private routeMessage(message: WebSocketMessage) {
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach(handler => {
      try {
        // Pass the entire message if data is undefined, otherwise pass data
        handler(message.data || message);
      } catch (error) {
        console.error(`Error in message handler for ${message.type}:`, error);
      }
    });

    // Component-specific routing
    switch (message.type) {
      case 'opportunities_analysis':
      case 'opportunities_update':
        this.forwardToComponent('income_builder', message);
        this.forwardToComponent('personal_assistant', message);
        break;

      case 'profile_updated':
        this.syncProfileUpdate(message.data);
        break;

      case 'spider_results':
        this.forwardToComponent('job_tracker', message);
        this.forwardToComponent('income_builder', message);
        break;

      case 'decision_ready':
        this.forwardToComponent('decision_command', message);
        break;

      case 'revenue_generated':
        this.forwardToComponent('revenue_dashboard', message);
        break;

      case 'pipeline_response':
        this.handlePipelineResponse(message.data);
        break;
    }
  }

  private forwardToComponent(targetComponent: string, message: WebSocketMessage) {
    // This would forward to component-specific handlers
    console.log(`🔄 Forwarding ${message.type} to ${targetComponent}`);
  }

  private async syncProfileUpdate(profileData: any) {
    console.log('🔄 Syncing profile update across components');

    // Notify Income Builder to refresh opportunities
    this.send({
      type: 'analyze_opportunities',
      source: 'platform_connector',
      target: 'income_builder',
      data: { profile: profileData }
    });

    // Update Neural Orchestra context
    this.send({
      type: 'context_update',
      source: 'platform_connector',
      target: 'neural_orchestra',
      data: { user_profile: profileData }
    });
  }

  private activatePlatformPipeline(component: string) {
    console.log(`🚀 Activating platform pipeline for ${component}`);

    this.send({
      type: 'activate_pipeline',
      source: component,
      data: {
        request: 'Platform integration activation',
        components: Array.from(this.components.keys()),
        timestamp: new Date().toISOString()
      }
    });
  }

  private handlePipelineResponse(data: any) {
    console.log('📊 Pipeline response received:', data);

    if (data.bridge_activated) {
      console.log('✅ Platform bridge is now active!');
      this.connectionCallbacks.forEach(callback => callback());
    }
  }

  private handleReconnection(component: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      console.log(`🔄 Attempting to reconnect ${component} in ${delay}ms (attempt ${this.reconnectAttempts})`);

      setTimeout(() => {
        this.connect(component);
      }, delay);
    } else {
      console.error(`❌ Failed to reconnect ${component} after ${this.maxReconnectAttempts} attempts`);
    }
  }

  /**
   * Register an event handler for specific message types
   */
  public on(eventType: string, handler: (data: any) => void): void {
    const handlers = this.messageHandlers.get(eventType) || [];
    handlers.push(handler);
    this.messageHandlers.set(eventType, handlers);
  }

  /**
   * Remove an event handler
   */
  public off(eventType: string, handler: (data: any) => void): void {
    const handlers = this.messageHandlers.get(eventType) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
      this.messageHandlers.set(eventType, handlers);
    }
  }

  /**
   * Send message through WebSocket
   */
  public send(message: WebSocketMessage): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        ...message,
        timestamp: new Date().toISOString()
      }));
      return true;
    }
    console.warn('WebSocket not connected, cannot send message:', message);
    return false;
  }

  /**
   * Register message handler
   */
  public onMessage(type: string, handler: (data: any) => void): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)!.push(handler);
  }

  /**
   * Remove message handler
   */
  public offMessage(type: string, handler: (data: any) => void): void {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Get component status
   */
  public getComponentStatus(component: string): ComponentContext | null {
    return this.components.get(component) || null;
  }

  /**
   * Get all component statuses
   */
  public getAllComponentStatuses(): Map<string, ComponentContext> {
    return new Map(this.components);
  }

  /**
   * Check if platform is fully connected
   */
  public isPlatformConnected(): boolean {
    const connectedCount = Array.from(this.components.values())
      .filter(component => component.connected).length;

    return connectedCount >= 3; // At least 3 components connected
  }

  /**
   * Personal Assistant Integration
   */
  public connectPersonalAssistant(onUpdate: (data: any) => void): void {
    this.onMessage('opportunities_analysis', onUpdate);
    this.onMessage('profile_suggestions', onUpdate);
    this.onMessage('assistant_context', onUpdate);

    // Request current context
    this.send({
      type: 'get_assistant_context',
      source: 'personal_assistant'
    });
  }

  /**
   * Income Builder Integration
   */
  public connectIncomeBuilder(onUpdate: (data: any) => void): void {
    this.onMessage('opportunities_analysis', onUpdate);
    this.onMessage('opportunities_update', onUpdate);
    this.onMessage('revenue_update', onUpdate);

    // Request current opportunities
    this.send({
      type: 'get_opportunities',
      source: 'income_builder'
    });
  }

  /**
   * Revenue Dashboard Integration
   */
  public connectRevenueDashboard(onUpdate: (data: any) => void): void {
    this.onMessage('metrics_update', onUpdate);
    this.onMessage('revenue_generated', onUpdate);
    this.onMessage('opportunities_data', onUpdate);
  }

  /**
   * Neural Orchestra Integration
   */
  public connectNeuralOrchestra(onUpdate: (data: any) => void): void {
    this.onMessage('orchestra_update', onUpdate);
    this.onMessage('agent_activity', onUpdate);
    this.onMessage('execution_update', onUpdate);
  }

  /**
   * Decision Command Integration
   */
  public connectDecisionCommand(onUpdate: (data: any) => void): void {
    this.onMessage('decision_update', onUpdate);
    this.onMessage('opportunities_analysis', onUpdate);
    this.onMessage('execution_started', onUpdate);
  }

  /**
   * Submit action for execution across platform
   */
  public executeAction(action: string, data: any, component: string): void {
    console.log(`🎯 Executing action: ${action} from ${component}`);

    this.send({
      type: 'execute_action',
      source: component,
      data: { action, payload: data }
    });
  }

  /**
   * Update user profile across all components
   */
  public updateProfile(profileData: any): void {
    this.send({
      type: 'profile_update',
      source: 'platform_connector',
      data: { profile: profileData }
    });
  }

  /**
   * Trigger job search across spider network
   */
  public triggerJobSearch(searchCriteria: any): void {
    this.send({
      type: 'trigger_spider_deployment',
      source: 'platform_connector',
      data: {
        request: 'Find job opportunities',
        domains: ['freelance', 'remote_work', 'ai_jobs'],
        criteria: searchCriteria
      }
    });
  }

  /**
   * Add connection callback
   */
  public onConnected(callback: () => void): void {
    this.connectionCallbacks.push(callback);
  }

  /**
   * Disconnect from WebSocket
   */
  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    // Reset component statuses
    this.components.forEach((context, component) => {
      context.connected = false;
      this.components.set(component, context);
    });
  }
}

// Export singleton instance
export const unifiedConnector = new UnifiedPlatformConnector();
export default unifiedConnector;