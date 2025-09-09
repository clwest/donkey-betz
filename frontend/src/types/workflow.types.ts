// Workflow Types - The core of our application

export type NodeCategory = 'input' | 'process' | 'output';

export type InputNodeType = 
  | 'research-input'
  | 'voice-input'
  | 'text-input'
  | 'image-input'
  | 'data-input';

export type ProcessNodeType =
  | 'content-generation'
  | 'image-generation'
  | 'video-generation'
  | 'content-enhancement'
  | 'format-conversion'
  | 'content-optimization'
  | 'summarization'
  | 'tagging';

export type OutputNodeType =
  | 'social-media'
  | 'blog-publishing'
  | 'ebook-creation'
  | 'email-campaigns'
  | 'presentations'
  | 'podcast-scripts'
  | 'reports'
  | 'storage'
  | 'webhooks';

export type NodeType = InputNodeType | ProcessNodeType | OutputNodeType;

export interface WorkflowNodeConfig {
  // Input node configs
  researchUrls?: string[];
  voiceFile?: File;
  textContent?: string;
  imageFile?: File;
  dataSource?: string;
  
  // Process node configs
  prompt?: string;
  model?: string;
  style?: string;
  tone?: string;
  length?: number;
  keywords?: string[];
  enhancementLevel?: 'basic' | 'advanced' | 'expert';
  
  // Output node configs
  platforms?: string[];
  publishSettings?: Record<string, any>;
  webhookUrl?: string;
  storageLocation?: string;
}

export interface WorkflowNode {
  id: string;
  type: NodeType;
  category: NodeCategory;
  name: string;
  description?: string;
  config: WorkflowNodeConfig;
  position: {
    x: number;
    y: number;
  };
  data?: any;
}

export interface WorkflowConnection {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface WorkflowSchedule {
  enabled: boolean;
  cron?: string;
  timezone?: string;
  nextRun?: Date;
}

export interface WorkflowTrigger {
  type: 'webhook' | 'event' | 'manual';
  config: Record<string, any>;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startedAt: Date;
  completedAt?: Date;
  logs: WorkflowExecutionLog[];
  results?: any;
  error?: string;
}

export interface WorkflowExecutionLog {
  nodeId: string;
  timestamp: Date;
  level: 'info' | 'warning' | 'error';
  message: string;
  data?: any;
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  schedule?: WorkflowSchedule;
  triggers?: WorkflowTrigger[];
  isTemplate?: boolean;
  templateCategory?: string;
  createdAt: Date;
  updatedAt: Date;
  lastExecutedAt?: Date;
  executionCount?: number;
  tags?: string[];
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  workflow: Partial<Workflow>;
  preview?: string;
}