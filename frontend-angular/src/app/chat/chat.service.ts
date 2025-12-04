import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: Date;
  updated_at: Date;
  message_count?: number;
}

export interface SendMessageRequest {
  content: string;
  session_id?: string;
  file?: File;
}

export interface SendMessageResponse {
  message: Message;
  session_id: string;
}

export interface PatientPreview {
  name: string;
  mrn?: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  email?: string;
  address?: string;
}

export interface ConfirmationPreviewResponse {
  preview_id: string;
  operation_type: string;
  total_records: number;
  preview_records: PatientPreview[];
  validation_warnings: string[];
  estimated_time_seconds?: number;
  message: string;
}

export interface ConfirmationRequest {
  preview_id: string;
  confirmed: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private http = inject(HttpClient);

  private messagesSubject = new BehaviorSubject<Message[]>([]);
  public messages$ = this.messagesSubject.asObservable();

  private sessionsSubject = new BehaviorSubject<ChatSession[]>([]);
  public sessions$ = this.sessionsSubject.asObservable();

  private currentSessionSubject = new BehaviorSubject<ChatSession | null>(null);
  public currentSession$ = this.currentSessionSubject.asObservable();

  private isLoadingSubject = new BehaviorSubject<boolean>(false);
  public isLoading$ = this.isLoadingSubject.asObservable();

  constructor() {
    // Sessions will be managed in-memory for now
    // since backend doesn't have session endpoints yet
  }

  loadSessions(): Observable<ChatSession[]> {
    // Return empty sessions for now - backend doesn't have this endpoint
    const sessions: ChatSession[] = [];
    this.sessionsSubject.next(sessions);
    return new Observable(observer => {
      observer.next(sessions);
      observer.complete();
    });
  }

  loadSession(sessionId: string): Observable<Message[]> {
    // Sessions not persisted yet - just clear current messages
    this.messagesSubject.next([]);
    this.isLoadingSubject.next(false);
    return new Observable(observer => {
      observer.next([]);
      observer.complete();
    });
  }

  sendMessage(request: SendMessageRequest): Observable<any> {
    this.isLoadingSubject.next(true);

    // Optimistically add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: request.content,
      role: 'user',
      timestamp: new Date()
    };

    const currentMessages = this.messagesSubject.value;
    this.messagesSubject.next([...currentMessages, userMessage]);

    // Prepare form data for multipart/form-data upload
    const formData = new FormData();

    // If file is present but no content, provide default command
    const commandText = request.content || (request.file ? 'Process uploaded file' : '');
    formData.append('command', commandText);
    formData.append('session_id', request.session_id || `session-${Date.now()}`);

    // Add file if present
    if (request.file) {
      formData.append('file', request.file, request.file.name);
    }

    // Debug: Log what we're sending
    console.log('Sending FormData with:', {
      command: commandText,
      session_id: request.session_id || `session-${Date.now()}`,
      file: request.file ? request.file.name : null
    });

    return this.http.post<any>(`${environment.apiUrl}/command`, formData).pipe(
      tap((response: any) => {
        // Add assistant response - response.message is the string content
        const assistantMessage: Message = {
          id: response.operation_id || Date.now().toString(),
          content: response.message || 'No response',
          role: 'assistant',
          timestamp: response.created_at ? new Date(response.created_at) : new Date()
        };

        const messages = this.messagesSubject.value;
        this.messagesSubject.next([...messages, assistantMessage]);

        this.isLoadingSubject.next(false);
      }),
      catchError((error: any) => {
        console.error('Error sending message:', error);

        // Add error message to chat
        const errorMessage: Message = {
          id: Date.now().toString(),
          content: `Error: ${error.message || 'Failed to connect to backend. Please make sure the backend server is running on http://localhost:8000'}`,
          role: 'assistant',
          timestamp: new Date()
        };

        const messages = this.messagesSubject.value;
        this.messagesSubject.next([...messages, errorMessage]);

        this.isLoadingSubject.next(false);

        return of(error);
      })
    );
  }

  createNewSession(): void {
    this.messagesSubject.next([]);
    this.currentSessionSubject.next(null);
  }

  deleteSession(sessionId: string): Observable<void> {
    // Remove from in-memory sessions
    const sessions = this.sessionsSubject.value.filter(s => s.id !== sessionId);
    this.sessionsSubject.next(sessions);

    // Clear messages if current session was deleted
    if (this.currentSessionSubject.value?.id === sessionId) {
      this.messagesSubject.next([]);
      this.currentSessionSubject.next(null);
    }

    return new Observable(observer => {
      observer.next();
      observer.complete();
    });
  }

  clearMessages(): void {
    this.messagesSubject.next([]);
  }

  getMessages(): Message[] {
    return this.messagesSubject.value;
  }

  getCurrentSession(): ChatSession | null {
    return this.currentSessionSubject.value;
  }

  /**
   * Preview operation before execution (URS FR-3)
   * Used for bulk CSV/Excel uploads to show confirmation dialog
   */
  previewOperation(file: File, command?: string, sessionId?: string): Observable<ConfirmationPreviewResponse> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    if (command) {
      formData.append('command', command);
    }
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    return this.http.post<ConfirmationPreviewResponse>(`${environment.apiUrl}/preview`, formData);
  }

  /**
   * Confirm and execute previewed operation (URS FR-3)
   * Note: Current implementation requires re-upload due to missing cache
   */
  confirmOperation(request: ConfirmationRequest): Observable<any> {
    return this.http.post<any>(`${environment.apiUrl}/confirm`, request);
  }

  /**
   * Get detailed health status (URS IR-1)
   */
  getHealthStatus(): Observable<any> {
    return this.http.get<any>(`${environment.apiUrl}/health/detailed`);
  }
}
