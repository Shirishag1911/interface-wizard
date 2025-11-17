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

    // Call the actual backend endpoint
    const payload = {
      command: request.content,
      session_id: request.session_id || `session-${Date.now()}`
    };

    return this.http.post<any>(`${environment.apiUrl}/command`, payload).pipe(
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
}
