'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import { Copy, Check, Info, Lightbulb, AlertTriangle, ShieldAlert } from 'lucide-react';

export interface MarkdownMathRendererProps {
  content: string;
  className?: string;
}

/**
 * Preprocesses markdown/LaTeX text to ensure:
 * 1. Double-escaped LaTeX commands (\\frac, \\text, \\sigma, etc.) become clean LaTeX (\frac, \text, \sigma)
 * 2. Unadorned standalone LaTeX equations without $$ delimiters are safely wrapped in $$ ... $$
 * 3. Does not alter code inside fenced code blocks ``` ... ```
 */
function preprocessMathContent(text: string): string {
  if (!text || typeof text !== 'string') return '';

  // Split by code blocks to avoid touching code snippets
  const parts = text.split(/(```[\s\S]*?```)/g);

  return parts
    .map((part, index) => {
      // Odd indices are fenced code blocks - return untouched
      if (index % 2 === 1) return part;

      let processed = part;

      // 1. Normalize double-escaped LaTeX commands in non-code text
      processed = processed.replace(
        /\\\\(frac|text|sqrt|alpha|beta|mu|sigma|theta|lambda|delta|Delta|pi|chi|bar|hat|sum|prod|int|approx|neq|leq?|geq?|times|pm|cdot|in|notin|subset|infty|rho|partial|left|right|begin|end|quad|qquad|mathbf|mathit|mathrm)/g,
        '\\$1'
      );

      // 2. Detect unadorned standalone LaTeX block equations
      // e.g. \text{Test Statistic} = \frac{...}{...} or t = \frac{...}{...} without $$
      const lines = processed.split('\n');
      const normalizedLines: string[] = [];
      let inBlockMath = false;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        if (trimmed.startsWith('$$')) {
          if (trimmed.endsWith('$$') && trimmed.length > 4) {
            const math = trimmed.slice(2, -2).trim();
            normalizedLines.push('$$');
            normalizedLines.push(math);
            normalizedLines.push('$$');
            continue;
          }
          inBlockMath = !inBlockMath || !trimmed.endsWith('$$') || trimmed === '$$';
          normalizedLines.push(line);
          continue;
        }

        if (inBlockMath) {
          normalizedLines.push(line);
          continue;
        }

        // Check if this standalone line is an unadorned LaTeX equation:
        // E.g. starts with \text{...} = \frac or \frac{...} or contains \frac{...}{...} with '='
        const isUnadornedEquation =
          !trimmed.startsWith('$') &&
          (
            /^\\text\{[^}]+\}\s*=\s*\\frac\{/.test(trimmed) ||
            /^[a-zA-Z\\][\w\s\\{}]*\s*=\s*\\frac\{/.test(trimmed) ||
            (/^\\frac\{/.test(trimmed) && trimmed.endsWith('}')) ||
            (trimmed.includes('\\frac{') && trimmed.includes('=') && !trimmed.includes('`'))
          );

        if (isUnadornedEquation) {
          normalizedLines.push('$$');
          normalizedLines.push(trimmed);
          normalizedLines.push('$$');
        } else {
          normalizedLines.push(line);
        }
      }

      return normalizedLines.join('\n');
    })
    .join('');
}

/**
 * Extracts plain text from React children to form a clean URL slug / HTML anchor ID.
 */
function extractTextFromChildren(children: React.ReactNode): string {
  if (!children) return '';
  if (typeof children === 'string') return children;
  if (typeof children === 'number') return children.toString();
  if (Array.isArray(children)) {
    return children.map(extractTextFromChildren).join('');
  }
  if (React.isValidElement(children)) {
    const props = children.props as { children?: React.ReactNode };
    return extractTextFromChildren(props.children);
  }
  return '';
}

function generateSlugId(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

/**
 * Syntax-highlighted code block with language pill and copy-to-clipboard button.
 */
function CodeBlock({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (typeof navigator !== 'undefined') {
      navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const displayLang = (language || 'code').toUpperCase();

  return (
    <div className="my-4 rounded-xl overflow-hidden border border-slate-800 bg-slate-950 text-slate-100 shadow-md">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-900/90 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
          <span className="ml-2 font-mono text-[11px] font-bold text-slate-400 tracking-wider">
            {displayLang}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors font-mono text-[11px] cursor-pointer"
          title="Copy code to clipboard"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-400 font-semibold">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code Area */}
      <pre className="p-4 text-xs font-mono leading-relaxed overflow-x-auto text-emerald-300/90">
        <code>{code}</code>
      </pre>
    </div>
  );
}

/**
 * Main Centralized Markdown + KaTeX Math Content Renderer Component.
 * Transforms raw markdown strings and LaTeX math expressions into rich, accessible UI.
 */
export const MarkdownMathRenderer: React.FC<MarkdownMathRendererProps> = ({
  content,
  className = '',
}) => {
  if (!content) return null;

  const preprocessed = preprocessMathContent(content);

  return (
    <div className={`prose-container text-slate-800 text-sm leading-relaxed ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkGfm]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Headers with auto-generated IDs for Table of Contents anchors
          h1({ children, ...props }) {
            const rawText = extractTextFromChildren(children);
            const id = generateSlugId(rawText);
            return (
              <h2
                id={id}
                className="text-xl sm:text-2xl font-black text-slate-900 mt-6 mb-4 pb-2 border-b border-slate-200 scroll-mt-20"
                {...props}
              >
                {children}
              </h2>
            );
          },
          h2({ children, ...props }) {
            const rawText = extractTextFromChildren(children);
            const id = generateSlugId(rawText);
            return (
              <h3
                id={id}
                className="text-base sm:text-lg font-extrabold text-slate-900 mt-6 mb-3 flex items-center gap-2 scroll-mt-20"
                {...props}
              >
                <span className="w-2 h-5 rounded-full bg-blue-700 inline-block shrink-0" />
                <span>{children}</span>
              </h3>
            );
          },
          h3({ children, ...props }) {
            const rawText = extractTextFromChildren(children);
            const id = generateSlugId(rawText);
            return (
              <h4
                id={id}
                className="text-sm sm:text-base font-bold text-slate-900 mt-5 mb-2.5 pb-1 border-b border-slate-100 flex items-center gap-2 scroll-mt-20"
                {...props}
              >
                <span className="w-1.5 h-4 rounded-full bg-blue-600 inline-block shrink-0" />
                <span>{children}</span>
              </h4>
            );
          },
          h4({ children, ...props }) {
            const rawText = extractTextFromChildren(children);
            const id = generateSlugId(rawText);
            return (
              <h5
                id={id}
                className="text-xs sm:text-sm font-bold text-slate-800 uppercase tracking-wider mt-4 mb-2 flex items-center gap-1.5 scroll-mt-20"
                {...props}
              >
                {children}
              </h5>
            );
          },

          // Paragraphs
          p({ children, ...props }) {
            return (
              <p className="text-slate-700 leading-relaxed text-sm my-2.5" {...props}>
                {children}
              </p>
            );
          },

          // Lists
          ul({ children, ...props }) {
            return (
              <ul className="list-disc pl-5 my-2.5 space-y-1.5 text-slate-700 text-sm" {...props}>
                {children}
              </ul>
            );
          },
          ol({ children, ...props }) {
            return (
              <ol className="list-decimal pl-5 my-2.5 space-y-1.5 text-slate-700 text-sm" {...props}>
                {children}
              </ol>
            );
          },
          li({ children, ...props }) {
            return (
              <li className="leading-relaxed text-slate-700 text-sm pl-1" {...props}>
                {children}
              </li>
            );
          },

          // Code blocks & inline code
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const isCodeBlock = match || String(children).includes('\n');

            if (isCodeBlock) {
              return (
                <CodeBlock
                  code={String(children).replace(/\n$/, '')}
                  language={match ? match[1] : 'code'}
                />
              );
            }

            return (
              <code
                className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[11px] border border-slate-200 font-semibold"
                {...props}
              >
                {children}
              </code>
            );
          },

          // Blockquotes and Callout alerts
          blockquote({ children, ...props }) {
            const rawText = extractTextFromChildren(children);
            let type: 'note' | 'tip' | 'warning' | 'important' | 'quote' = 'quote';
            let cleanChildren = children;

            if (rawText.includes('[!NOTE]')) {
              type = 'note';
            } else if (rawText.includes('[!TIP]')) {
              type = 'tip';
            } else if (rawText.includes('[!WARNING]') || rawText.includes('[!CAUTION]')) {
              type = 'warning';
            } else if (rawText.includes('[!IMPORTANT]')) {
              type = 'important';
            }

            if (type !== 'quote') {
              const styleConfig = {
                note: {
                  bg: 'bg-blue-50/70 border-blue-200 text-blue-900',
                  icon: <Info className="w-4 h-4 text-blue-700 shrink-0 mt-0.5" />,
                  title: 'Key Note',
                },
                tip: {
                  bg: 'bg-emerald-50/70 border-emerald-200 text-emerald-900',
                  icon: <Lightbulb className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />,
                  title: 'Professional Tip',
                },
                warning: {
                  bg: 'bg-amber-50/80 border-amber-200 text-amber-950',
                  icon: <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />,
                  title: 'Critical Warning',
                },
                important: {
                  bg: 'bg-rose-50/70 border-rose-200 text-rose-950',
                  icon: <ShieldAlert className="w-4 h-4 text-rose-700 shrink-0 mt-0.5" />,
                  title: 'Important Rule',
                },
              }[type];

              return (
                <div
                  className={`my-3 p-3.5 rounded-xl border ${styleConfig.bg} text-xs flex items-start gap-2.5 shadow-2xs`}
                >
                  {styleConfig.icon}
                  <div className="space-y-1">
                    <span className="font-bold uppercase tracking-wider text-[10px] block opacity-90">
                      {styleConfig.title}
                    </span>
                    <div className="leading-relaxed">{cleanChildren}</div>
                  </div>
                </div>
              );
            }

            return (
              <blockquote
                className="my-3 pl-4 py-1 border-l-4 border-blue-500 bg-blue-50/40 rounded-r text-slate-700 italic text-xs leading-relaxed"
                {...props}
              >
                {children}
              </blockquote>
            );
          },

          // Tables
          table({ children, ...props }) {
            return (
              <div className="my-4 overflow-x-auto rounded-lg border border-slate-200 shadow-2xs">
                <table className="min-w-full text-xs text-left divide-y divide-slate-200" {...props}>
                  {children}
                </table>
              </div>
            );
          },
          thead({ children, ...props }) {
            return (
              <thead className="bg-slate-100 text-slate-700 uppercase font-semibold" {...props}>
                {children}
              </thead>
            );
          },
          th({ children, ...props }) {
            return (
              <th className="px-3.5 py-2.5 text-slate-700 font-semibold" {...props}>
                {children}
              </th>
            );
          },
          td({ children, ...props }) {
            return (
              <td className="px-3.5 py-2 border-t border-slate-100 text-slate-600" {...props}>
                {children}
              </td>
            );
          },

          // Strong & Emphasis
          strong({ children, ...props }) {
            return (
              <strong className="font-bold text-slate-900" {...props}>
                {children}
              </strong>
            );
          },
          em({ children, ...props }) {
            return (
              <em className="italic text-slate-800" {...props}>
                {children}
              </em>
            );
          },

          // Links
          a({ href, children, ...props }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-700 hover:text-blue-900 underline font-semibold decoration-blue-300 hover:decoration-blue-700 transition-colors"
                {...props}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {preprocessed}
      </ReactMarkdown>
    </div>
  );
};

// Aliases for unified reusable access across the application
export const MarkdownRenderer = MarkdownMathRenderer;
export const LearningContentRenderer = MarkdownMathRenderer;

export default MarkdownMathRenderer;
