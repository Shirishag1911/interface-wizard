import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/Sidebar';
import MessageBubble from '../components/MessageBubble';
import ChatInputComponent from '../components/ChatInputComponent';
import { apiService } from '../services/api';
import './Chat.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface Session {
  id: string;
  title?: string;
  updated_at: string;
  messages?: Message[];
}

const Chat: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Show welcome message
    showWelcomeMessage();
    loadSessions();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const showWelcomeMessage = () => {
    const welcomeMessage: Message = {
      id: 'welcome',
      role: 'assistant',
      content: `# Welcome to Interface Wizard! 👋

I'm your AI assistant for healthcare data integration. I can help you with HL7/FHIR operations using natural language.

**Here are some things you can ask me:**

- "Create a test patient named John Doe"
- "Create 10 patients with random data"
- "Create a patient with diabetes diagnosis"
- "Generate ADT message for patient admission"
- "Retrieve patient with MRN 12345"
- "Send HL7 observation result for patient"

**Features:**
- Natural language patient record creation
- HL7 v2.x message generation (ADT, ORU, QRY)
- FHIR R4 resource management
- Mirth Connect integration
- OpenEMR database interaction

Just type your request below and I'll help you!`,
      created_at: new Date().toISOString()
    };

    setMessages([welcomeMessage]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessions = async () => {
    try {
      const sessionsData = await apiService.getSessions();
      setSessions(sessionsData);
      if (sessionsData.length > 0 && !currentSession) {
        await loadSession(sessionsData[0]);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const loadSession = async (session: Session) => {
    try {
      setCurrentSession(session);
      const messagesData = await apiService.getMessages(session.id);
      setMessages(messagesData);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const newChat = async () => {
    try {
      const newSession = await apiService.createSession();
      setSessions([newSession, ...sessions]);
      setCurrentSession(newSession);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await apiService.deleteSession(sessionId);
      setSessions(sessions.filter((s) => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
        if (sessions.length > 1) {
          const nextSession = sessions.find((s) => s.id !== sessionId);
          if (nextSession) {
            await loadSession(nextSession);
          }
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const sendMessage = async (content: string, file?: File) => {
    if (!content.trim() && !file) return;

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call the actual backend endpoint
      const response = await apiService.processCommand({
        command: content,
        session_id: currentSession?.id || `session-${Date.now()}`
      });

      // Add assistant response
      const assistantMessage: Message = {
        id: response.operation_id || Date.now().toString(),
        role: 'assistant',
        content: response.message || 'No response',
        created_at: response.created_at || new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Failed to send message:', error);
      // Add error message
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Error: ${error.message || 'Failed to connect to backend. Please make sure the backend server is running on http://localhost:8000'}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const getSessionTitle = (session: Session) => {
    if (session.title) {
      return session.title;
    }
    if (session.messages && session.messages.length > 0) {
      const firstUserMessage = session.messages.find((m) => m.role === 'user');
      if (firstUserMessage) {
        return firstUserMessage.content.substring(0, 50) + '...';
      }
    }
    return 'New Conversation';
  };

  return (
    <div className="chat-container-main">
      {isSidebarOpen && (
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSession?.id || null}
          onNewChat={newChat}
          onLoadSession={loadSession}
          onDeleteSession={deleteSession}
        />
      )}

      <div className="main-content-chat">
        <div className="chat-header">
          <button className="menu-button" onClick={toggleSidebar}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1>{currentSession ? getSessionTitle(currentSession) : 'New Conversation'}</h1>
        </div>

        <div className="messages-container-chat">
          <div className="messages-wrapper-chat">
            {messages.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">
                  <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="80" height="80" rx="16" fill="url(#emptyGradient)" />
                    <path d="M40 20L56 30V50L40 60L24 50V30L40 20Z" fill="white" opacity="0.9" />
                    <defs>
                      <linearGradient id="emptyGradient" x1="0" y1="0" x2="80" y2="80" gradientUnits="userSpaceOnUse">
                        <stop stopColor="#667eea" />
                        <stop offset="1" stopColor="#764ba2" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
                <h2>How can I help you today?</h2>
                <p>Start a conversation by typing a message below</p>

                <div className="suggestions">
                  <button className="suggestion-card" onClick={() => sendMessage('Create a test patient named John Doe')}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                    </svg>
                    <span>Create test patient</span>
                  </button>
                  <button className="suggestion-card" onClick={() => sendMessage('Create a patient with diabetes diagnosis')}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    <span>Create patient with diagnosis</span>
                  </button>
                  <button className="suggestion-card" onClick={() => sendMessage('Generate ADT message for patient admission')}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                    </svg>
                    <span>Generate HL7 ADT message</span>
                  </button>
                  <button className="suggestion-card" onClick={() => sendMessage('Create 10 patients with random data')}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <span>Create multiple patients</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="messages-list">
                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
              </div>
            )}

            {isLoading && (
              <div className="loading-indicator">
                <div className="typing-animation">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        <ChatInputComponent
          onSendMessage={sendMessage}
          disabled={false}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

export default Chat;
