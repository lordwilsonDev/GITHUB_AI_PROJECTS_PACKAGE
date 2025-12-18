// Core VY Task and Queue Types

export type TaskSource = 'user' | 'moie' | 'automation';
export type TaskStatus = 'intake' | 'planning' | 'running' | 'review' | 'done' | 'failed';

export interface VYTask {
  id: string;
  source: TaskSource;
  domain: string;
  goal: string;
  scope: string;
  priority: number;
  status: TaskStatus;
  artifacts: string[];
  created_at: string;
  updated_at: string;
  raw_input?: string;
  parsed_context?: Record<string, any>;
}

export interface QueueMessage<T = any> {
  id: string;
  task_id: string;
  payload: T;
  timestamp: string;
  retry_count: number;
}

export interface WorkerConfig {
  id: string;
  role: string;
  subscribes: string[];
  emits: string[];
  max_concurrent: number;
  timeout_ms: number;
}

export interface PanopticonLog {
  worker_id: string;
  task_id: string;
  action: string;
  status: 'start' | 'success' | 'error' | 'warning';
  message: string;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface MoIEInversion {
  type: 'architect' | 'referee' | 'critic';
  context: string;
  requirements: string[];
  constraints: string[];
}
