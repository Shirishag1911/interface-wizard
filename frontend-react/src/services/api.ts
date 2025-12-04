/**
 * API service for communicating with the backend
 */
import axios, { AxiosInstance } from 'axios';
import { CommandRequest, OperationResponse, SessionInfo, HealthStatus } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 seconds for long-running operations
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log('API Response:', response.status, response.config.url);
        return response;
      },
      (error) => {
        console.error('API Error:', error.response?.status, error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Send a command to the backend for processing with optional file upload
   */
  async processCommand(request: CommandRequest, file?: File): Promise<OperationResponse> {
    // If file is provided, use FormData for multipart/form-data
    if (file) {
      const formData = new FormData();
      formData.append('command', request.command);
      if (request.session_id) {
        formData.append('session_id', request.session_id);
      }
      formData.append('file', file, file.name);

      const response = await this.client.post<OperationResponse>('/command', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    }

    // Otherwise, use JSON
    const response = await this.client.post<OperationResponse>('/command', request);
    return response.data;
  }

  /**
   * Get session information
   */
  async getSession(sessionId: string): Promise<SessionInfo> {
    const response = await this.client.get<SessionInfo>(`/session/${sessionId}`);
    return response.data;
  }

  /**
   * Get operation details
   */
  async getOperation(operationId: string): Promise<OperationResponse> {
    const response = await this.client.get<OperationResponse>(`/operation/${operationId}`);
    return response.data;
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthStatus> {
    const response = await this.client.get<HealthStatus>('/health');
    return response.data;
  }

  /**
   * Get all chat sessions
   */
  async getSessions(): Promise<any[]> {
    const response = await this.client.get('/sessions');
    return response.data;
  }

  /**
   * Get messages for a session
   */
  async getMessages(sessionId: string): Promise<any[]> {
    const response = await this.client.get(`/sessions/${sessionId}/messages`);
    return response.data;
  }

  /**
   * Send a message
   */
  async sendMessage(sessionId: string, content: string, file?: File): Promise<any> {
    const formData = new FormData();
    formData.append('content', content);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }
    if (file) {
      formData.append('file', file);
    }

    const response = await this.client.post('/messages', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Create a new session
   */
  async createSession(): Promise<any> {
    const response = await this.client.post('/sessions');
    return response.data;
  }

  /**
   * Delete a session
   */
  async deleteSession(sessionId: string): Promise<void> {
    await this.client.delete(`/sessions/${sessionId}`);
  }

  /**
   * Preview operation before execution (URS FR-3)
   * Used for bulk CSV/Excel/PDF uploads to show confirmation dialog
   */
  async previewOperation(file: File, command?: string, sessionId?: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    if (command) {
      formData.append('command', command);
    }
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await this.client.post('/preview', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Confirm and execute previewed operation (URS FR-3)
   * Note: Current implementation requires re-upload due to missing cache
   */
  async confirmOperation(previewId: string, confirmed: boolean): Promise<OperationResponse> {
    const response = await this.client.post<OperationResponse>('/confirm', {
      preview_id: previewId,
      confirmed
    });
    return response.data;
  }

  /**
   * Get detailed health status (URS IR-1)
   */
  async getDetailedHealth(): Promise<any> {
    const response = await this.client.get('/health/detailed');
    return response.data;
  }
}

export const apiService = new ApiService();
