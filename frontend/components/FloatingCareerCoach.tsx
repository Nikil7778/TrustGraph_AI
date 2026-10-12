'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useCoach } from '../context/CoachContext';
import { useLearner } from '../context/LearnerContext';
import { ApiChatAction } from '../services/api';
import {
  Sparkles,
  X,
  Send,
  RotateCcw,
  User,
  ArrowRight,
  Loader2,
  AlertTriangle,
  Minus,
} from 'lucide-react';

export const FloatingCareerCoach: React.FC = () => {
  const router = useRouter();
  const pathname = usePathname();
  const { activeUser } = useLearner();
  const {
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
  } = useCoach();

  const [inputMessage, setInputMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom on message changes
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading, isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isLoading) return;
    setInputMessage('');
    await sendMessage(text);
  };

  const handleActionClick = (action: ApiChatAction) => {
    if (action.target_route) {
      router.push(action.target_route);
    }
  };

  // Helper formatting for bolding, bullet points, and inline code
  const renderFormattedText = (text: string) => {
    return text.split('\n\n').map((paragraph, pIdx) => {
      // Bullet list handling
      if (paragraph.includes('\n- ') || paragraph.startsWith('- ')) {
        const lines = paragraph.split('\n');
        return (
          <ul key={pIdx} className="space-y-1.5 my-1.5 list-disc list-inside">
            {lines.map((line, lIdx) => {
              const clean = line.replace(/^[-\*]\s+/, '');
              return (
                <li key={lIdx} className="text-slate-800 leading-relaxed text-xs">
                  <span dangerouslySetInnerHTML={{ __html: formatInline(clean) }} />
                </li>
              );
            })}
          </ul>
        );
      }

      // Standard paragraph
      return (
        <p
          key={pIdx}
          className="my-1 leading-relaxed text-xs text-slate-800"
          dangerouslySetInnerHTML={{ __html: formatInline(paragraph) }}
        />
      );
    });
  };

  const formatInline = (str: string): string => {
    return str
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-slate-900">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic text-slate-700">$1</em>')
      .replace(/`(.*?)`/g, '<code class="bg-slate-200/60 text-slate-800 px-1 py-0.5 rounded text-[11px] font-mono">$1</code>');
  };

  // Context page label for contextual awareness
  const getPageContextLabel = () => {
    if (pathname === '/') return 'Dashboard';
    if (pathname === '/skill-dna') return 'Skill DNA';
    if (pathname === '/skill-debt') return 'Skill Debt';
    if (pathname === '/roadmap') return 'Roadmap';
    if (pathname === '/career-gap') return 'Career Gap';
    if (pathname === '/assessments') return 'Assessments';
    if (pathname === '/practice-lab') return 'Practice Lab';
    if (pathname === '/projects') return 'Projects';
    if (pathname === '/skill-passport') return 'Skill Passport';
    if (pathname === '/profile') return 'Profile';
    if (pathname === '/settings') return 'Settings';
    return pathname;
  };

  return (
    <>
      {/* Chat Panel (Anchored to bottom-right above the floating button) */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="SkillPath Career Coach"
          className="fixed bottom-24 right-4 sm:right-6 z-50 w-[calc(100vw-32px)] sm:w-[400px] h-[580px] max-h-[calc(100vh-110px)] bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-200"
        >
          {/* Panel Header */}
          <div className="bg-white border-b border-slate-200 p-3.5 sm:p-4 flex items-center justify-between gap-2 shrink-0">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-lg bg-blue-800 text-white flex items-center justify-center shrink-0 shadow-2xs">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <h3 className="text-sm font-bold text-slate-900 truncate">SkillPath Career Coach</h3>
                </div>
                <p className="text-[11px] text-slate-500 truncate">
                  Your personalized learning and career guide
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1 shrink-0">
              {/* Reset Conversation */}
              <button
                type="button"
                onClick={resetConversation}
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors cursor-pointer"
                title="Reset conversation"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>

              {/* Close / Minimize */}
              <button
                type="button"
                onClick={closeCoach}
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-md transition-colors cursor-pointer"
                title="Close chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Context Banner */}
          <div className="px-3.5 py-1.5 bg-slate-50 border-b border-slate-100 flex items-center justify-between text-[11px] text-slate-500 shrink-0">
            <span className="flex items-center gap-1.5 truncate">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
              <span className="truncate">Active Page: <strong>{getPageContextLabel()}</strong></span>
            </span>
            <span className="text-slate-400 font-mono text-[10px] shrink-0">
              {activeUser?.target_role?.name || 'Data Analyst'}
            </span>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 p-3.5 sm:p-4 overflow-y-auto space-y-3.5 bg-slate-50/50">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-6 h-6 rounded bg-blue-100 text-blue-700 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="w-3 h-3 text-blue-700" />
                  </div>
                )}

                <div
                  className={`max-w-[85%] rounded-xl px-3.5 py-2.5 text-xs shadow-2xs ${
                    msg.role === 'user'
                      ? 'bg-blue-800 text-white rounded-br-none'
                      : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none'
                  }`}
                >
                  {/* Content */}
                  <div>
                    {msg.role === 'assistant' ? (
                      renderFormattedText(msg.content)
                    ) : (
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    )}
                  </div>


                  {/* Secondary Action Buttons */}
                  {msg.actions && msg.actions.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap gap-1.5">
                      {msg.actions.map((action, aIdx) => (
                        <button
                          key={aIdx}
                          onClick={() => handleActionClick(action)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-white text-[11px] font-semibold rounded shadow-xs transition-colors cursor-pointer"
                        >
                          <span>{action.label}</span>
                          <ArrowRight className="w-2.5 h-2.5 text-blue-300" />
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Timestamp */}
                  <div
                    className={`text-[9px] mt-1 text-right ${
                      msg.role === 'user' ? 'text-blue-200' : 'text-slate-400'
                    }`}
                  >
                    {msg.timestamp}
                  </div>
                </div>

                {msg.role === 'user' && (
                  <div className="w-6 h-6 rounded bg-slate-800 text-white flex items-center justify-center shrink-0 mt-0.5 text-[10px] font-bold">
                    <User className="w-3 h-3 text-white" />
                  </div>
                )}
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex gap-2 justify-start items-center">
                <div className="w-6 h-6 rounded bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
                  <Sparkles className="w-3 h-3 text-blue-700" />
                </div>
                <div className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-600 flex items-center gap-1.5 shadow-2xs">
                  <Loader2 className="w-3 h-3 text-blue-600 animate-spin" />
                  <span>Analyzing your learning progress...</span>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-lg p-2.5 text-xs flex items-center gap-2">
                <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Suggestions Chips (Initial state / ongoing) */}
          <div className="px-3 py-2 bg-white border-t border-slate-100 overflow-x-auto whitespace-nowrap shrink-0">
            <div className="flex items-center gap-1.5 text-xs">
              {suggestedPrompts.map((prompt, pIdx) => (
                <button
                  key={pIdx}
                  type="button"
                  onClick={() => handleSend(prompt)}
                  disabled={isLoading}
                  className="px-2.5 py-1 bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 text-[11px] rounded-full font-medium transition-colors shrink-0 disabled:opacity-50 cursor-pointer shadow-2xs"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
          <div className="p-3 bg-white border-t border-slate-200 shrink-0">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend();
              }}
              className="flex items-center gap-1.5"
            >
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask about your Skill DNA, Debt, or Roadmap..."
                disabled={isLoading}
                className="flex-1 bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none transition-all disabled:opacity-60"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="inline-flex items-center justify-center p-2 bg-blue-800 hover:bg-blue-900 text-white rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer shrink-0"
                title="Send message"
              >
                {isLoading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Send className="w-3.5 h-3.5" />
                )}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Floating Chat Button (Bottom-Right corner) */}
      <div className="fixed bottom-6 right-6 z-50">
        <div className="relative group flex items-center justify-end">
          {/* Tooltip on Hover */}
          <span
            className="absolute right-full mr-3 px-2.5 py-1 bg-slate-900 text-white text-xs font-semibold rounded-md shadow-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
            role="tooltip"
          >
            SkillPath Career Coach
          </span>

          {/* Circular Button */}
          <button
            type="button"
            onClick={toggleCoach}
            aria-label="SkillPath Career Coach"
            className="w-14 h-14 rounded-full bg-blue-800 hover:bg-blue-900 text-white shadow-lg hover:shadow-xl transition-all cursor-pointer flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {isOpen ? (
              <X className="w-6 h-6 text-white" />
            ) : (
              <Sparkles className="w-6 h-6 text-white" />
            )}
          </button>
        </div>
      </div>
    </>
  );
};
