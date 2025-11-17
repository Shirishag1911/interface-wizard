/**
 * Zustand store for chat state management
 */
import { create } from 'zustand';
import { Message } from '../types';
import { v4 as uuidv4 } from 'uuid';

interface ChatState {
  messages: Message[];
  sessionId: string;
  isProcessing: boolean;
  addUserMessage: (content: string) => void;
  addSystemMessage: (content: string, operation?: any) => void;
  addErrorMessage: (content: string) => void;
  setProcessing: (processing: boolean) => void;
  clearMessages: () => void;
}

function generateId(): string {
  return Date.now().toString() + Math.random().toString(36).substr(2, 9);
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [
    {
      id: generateId(),
      type: 'system',
      content: 'Welcome to Interface Wizard! I can help you with HL7/FHIR data operations. Try commands like:\n\n• "Create 5 test patients with random demographics"\n• "Retrieve patient information for MRN 12345"\n• "Create lab results for patient 123"',
      timestamp: new Date(),
    },
  ],
  sessionId: uuidv4(),
  isProcessing: false,

  addUserMessage: (content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: generateId(),
          type: 'user',
          content,
          timestamp: new Date(),
        },
      ],
    })),

  addSystemMessage: (content, operation) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: generateId(),
          type: operation?.status === 'success' || operation?.status === 'partial_success' ? 'success' : 'system',
          content,
          timestamp: new Date(),
          operation,
        },
      ],
    })),

  addErrorMessage: (content) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: generateId(),
          type: 'error',
          content,
          timestamp: new Date(),
        },
      ],
    })),

  setProcessing: (processing) => set({ isProcessing: processing }),

  clearMessages: () =>
    set({
      messages: [
        {
          id: generateId(),
          type: 'system',
          content: 'Chat history cleared. How can I help you?',
          timestamp: new Date(),
        },
      ],
    }),
}));
