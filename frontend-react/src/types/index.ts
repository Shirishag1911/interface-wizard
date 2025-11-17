/**
 * TypeScript type definitions for Interface Wizard
 */

export interface CommandRequest {
  command: string;
  session_id?: string;
}

export interface OperationResponse {
  operation_id: string;
  status: 'pending' | 'processing' | 'success' | 'failed' | 'partial_success';
  message: string;
  data?: any;
  errors?: string[];
  warnings?: string[];
  protocol_used?: 'hl7v2' | 'fhir';
  records_affected: number;
  records_succeeded: number;
  records_failed: number;
  created_at: string;
  completed_at?: string;
}

export interface Message {
  id: string;
  type: 'user' | 'system' | 'error' | 'success';
  content: string;
  timestamp: Date;
  operation?: OperationResponse;
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  last_activity: string;
  command_count: number;
  operation_count: number;
}

export interface HealthStatus {
  status: string;
  version: string;
  timestamp: string;
}
