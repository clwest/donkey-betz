/**
 * Enhanced Console Logger for Donkey Betz
 * Provides colored, categorized logging for better debugging
 */

export const Logger = {
  // Component lifecycle logging
  component: (name: string, action: string, data?: any) => {
    console.log(
      `%c[COMPONENT] %c${name} %c${action}`,
      'color: #4CAF50; font-weight: bold',
      'color: #2196F3; font-weight: bold',
      'color: #757575',
      data || ''
    );
  },

  // API call logging
  api: (method: string, endpoint: string, data?: any) => {
    console.log(
      `%c[API ${method}] %c${endpoint}`,
      'color: #FF9800; font-weight: bold',
      'color: #FFC107',
      data || ''
    );
  },

  // API response logging
  apiResponse: (endpoint: string, response: any, error: boolean = false) => {
    if (error) {
      console.error(
        `%c[API ERROR] %c${endpoint}`,
        'color: #F44336; font-weight: bold',
        'color: #FF5252',
        response
      );
    } else {
      console.log(
        `%c[API SUCCESS] %c${endpoint}`,
        'color: #4CAF50; font-weight: bold',
        'color: #66BB6A',
        response
      );
    }
  },

  // State/Store changes
  state: (store: string, action: string, data?: any) => {
    console.log(
      `%c[STATE] %c${store} %c${action}`,
      'color: #9C27B0; font-weight: bold',
      'color: #BA68C8; font-weight: bold',
      'color: #757575',
      data || ''
    );
  },

  // User actions/events
  event: (component: string, event: string, data?: any) => {
    console.log(
      `%c[EVENT] %c${component} %c${event}`,
      'color: #00BCD4; font-weight: bold',
      'color: #26C6DA; font-weight: bold',
      'color: #757575',
      data || ''
    );
  },

  // Workflow specific logging
  workflow: (action: string, nodeId?: string, data?: any) => {
    console.log(
      `%c[WORKFLOW] %c${action} ${nodeId ? `Node: ${nodeId}` : ''}`,
      'color: #E91E63; font-weight: bold',
      'color: #F06292',
      data || ''
    );
  },

  // Error logging with stack trace
  error: (context: string, error: any) => {
    console.error(
      `%c[ERROR] %c${context}`,
      'color: #F44336; font-weight: bold; font-size: 14px',
      'color: #FF5252; font-weight: bold',
      '\n',
      error,
      '\nStack trace:',
      error?.stack || 'No stack trace available'
    );
  },

  // Warning logging
  warn: (context: string, message: string, data?: any) => {
    console.warn(
      `%c[WARNING] %c${context} %c${message}`,
      'color: #FF9800; font-weight: bold',
      'color: #FFB74D; font-weight: bold',
      'color: #757575',
      data || ''
    );
  },

  // Debug logging (verbose)
  debug: (context: string, message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(
        `%c[DEBUG] %c${context} %c${message}`,
        'color: #607D8B; font-weight: bold',
        'color: #90A4AE',
        'color: #B0BEC5',
        data || ''
      );
    }
  },

  // Performance logging
  perf: (operation: string, duration: number) => {
    const color = duration < 100 ? '#4CAF50' : duration < 500 ? '#FF9800' : '#F44336';
    console.log(
      `%c[PERFORMANCE] %c${operation} %ctook ${duration}ms`,
      'color: #3F51B5; font-weight: bold',
      'color: #5C6BC0',
      `color: ${color}; font-weight: bold`
    );
  },

  // Group logging for related operations
  group: (title: string, collapsed: boolean = true) => {
    if (collapsed) {
      console.groupCollapsed(
        `%c${title}`,
        'color: #795548; font-weight: bold; font-size: 12px'
      );
    } else {
      console.group(
        `%c${title}`,
        'color: #795548; font-weight: bold; font-size: 12px'
      );
    }
  },

  groupEnd: () => {
    console.groupEnd();
  },

  // Table logging for structured data
  table: (data: any, columns?: string[]) => {
    console.table(data, columns);
  },

  // Clear console with a message
  clear: (message?: string) => {
    console.clear();
    if (message) {
      console.log(
        `%c${message}`,
        'color: #2196F3; font-weight: bold; font-size: 16px'
      );
    }
  },

  // ASCII art for important messages
  banner: (message: string) => {
    console.log(
      `%c
╔════════════════════════════════════════╗
║  ${message.padEnd(36)}  ║
╚════════════════════════════════════════╝`,
      'color: #4CAF50; font-weight: bold'
    );
  }
};

// Export a simpler version for quick logging
export const log = {
  info: (...args: any[]) => console.log('%c[INFO]', 'color: #2196F3; font-weight: bold', ...args),
  success: (...args: any[]) => console.log('%c[SUCCESS]', 'color: #4CAF50; font-weight: bold', ...args),
  warn: (...args: any[]) => console.warn('%c[WARN]', 'color: #FF9800; font-weight: bold', ...args),
  error: (...args: any[]) => console.error('%c[ERROR]', 'color: #F44336; font-weight: bold', ...args),
  debug: (...args: any[]) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('%c[DEBUG]', 'color: #9E9E9E; font-weight: bold', ...args);
    }
  }
};

// Initialize logger with welcome message
if (process.env.NODE_ENV === 'development') {
  Logger.banner('Donkey Betz Debug Mode Active');
  Logger.component('Logger', 'Initialized', { 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV 
  });
}