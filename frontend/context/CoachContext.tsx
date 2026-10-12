'use client';

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { useLearner } from './LearnerContext';
import {
  api,
  ApiChatMessage,
  ApiChatAction,
  ApiCoachChatResponse,
} from '../services/api';

export interface ExtendedChatMessage extends ApiChatMessage {
  actions?: ApiChatAction[];
  tools_used?: string[];
  timestamp?: string;
  fallback_used?: boolean;
}

export const INITIAL_SUGGESTED_PROMPTS = [
  'What should I work on next?',
  'Why is SQL JOINs my priority?',
  'How am I progressing?',
  'What skills need more proof?',
];

interface CoachContextType {
  isOpen: boolean;
  openCoach: (prompt?: string) => void;
  closeCoach: () => void;
  toggleCoach: () => void;
  messages: ExtendedChatMessage[];
  sendMessage: (textToSend?: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  suggestedPrompts: string[];
  resetConversation: () => void;
}

const CoachContext = createContext<CoachContextType | undefined>(undefined);

export const CoachProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { activeUserId, activeUser } = useLearner();

  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>(INITIAL_SUGGESTED_PROMPTS);

  // Initialize initial message when user is loaded or first mounted
  useEffect(() => {
    if (messages.length === 0) {
      const learnerName = activeUser?.name || 'Alex';
      setMessages([
        {
          role: 'assistant',
          content: `Hi ${learnerName}, what would you like to work on?`,
          timestamp: 'Just now',
        },
      ]);
    }
  }, [activeUser?.name, messages.length]);

  const openCoach = useCallback((prompt?: string) => {
    setIsOpen(true);
    if (prompt && prompt.trim()) {
      setTimeout(() => {
        sendMessage(prompt.trim());
      }, 50);
    }
  }, []);

  const closeCoach = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleCoach = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const resetConversation = useCallback(() => {
    const learnerName = activeUser?.name || 'Alex';
    setMessages([
      {
        role: 'assistant',
        content: `Hi ${learnerName}, what would you like to work on?`,
        timestamp: 'Just now',
      },
    ]);
    setSuggestedPrompts(INITIAL_SUGGESTED_PROMPTS);
    setError(null);
  }, [activeUser?.name]);

  const sendMessage = async (textToSend?: string) => {
    const messageText = (textToSend || '').trim();
    if (!messageText || isLoading) return;

    setError(null);

    const userTurn: ExtendedChatMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userTurn]);
    setIsLoading(true);

    try {
      // Build lightweight conversation history for multi-turn context
      const historyPayload: ApiChatMessage[] = [...messages, userTurn]
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.content }));

      const res: ApiCoachChatResponse = await api.coachChat({
        user_id: activeUserId || 1,
        message: messageText,
        history: historyPayload,
      });

      const assistantTurn: ExtendedChatMessage = {
        role: 'assistant',
        content: res.reply,
        actions: res.actions,
        tools_used: res.tools_used,
        fallback_used: res.fallback_used,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantTurn]);
      if (res.suggested_prompts && res.suggested_prompts.length > 0) {
        setSuggestedPrompts(res.suggested_prompts);
      }
    } catch (err: any) {
      console.error('Career Coach API call failed:', err);
      setError(err?.message || 'Career Coach is temporarily unable to connect to the backend.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <CoachContext.Provider
      value={{
        isOpen,
        openCoach,
        closeCoach,
        toggleCoach,
        messages,
        sendMessage,
        isLoading,
        error,
        suggestedPrompts,
        resetConversation,
      }}
    >
      {children}
    </CoachContext.Provider>
  );
};

export const useCoach = () => {
  const context = useContext(CoachContext);
  if (!context) {
    throw new Error('useCoach must be used within a CoachProvider');
  }
  return context;
};
