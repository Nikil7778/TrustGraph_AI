'use client';

import React from 'react';
import { Inbox, Loader2, AlertCircle, RefreshCw } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Data Found',
  description = 'There are currently no items or evidence records available for this view.',
  actionText,
  onAction,
}) => {
  return (
    <div className="p-8 text-center bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col items-center justify-center my-4">
      <div className="w-12 h-12 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center mb-3 text-slate-400">
        <Inbox className="w-6 h-6 stroke-[1.5]" />
      </div>
      <h4 className="text-base font-bold text-slate-800 mb-1">{title}</h4>
      <p className="text-xs text-slate-500 max-w-sm mb-4">{description}</p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-md shadow-sm transition-colors"
        >
          {actionText}
        </button>
      )}
    </div>
  );
};

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Evaluating demonstrated skill evidence...',
}) => {
  return (
    <div className="p-8 text-center bg-white border border-slate-200 rounded-lg shadow-sm flex flex-col items-center justify-center my-4 min-h-[160px]">
      <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-2" />
      <span className="text-xs font-semibold text-slate-700">{message}</span>
      <span className="text-[11px] text-slate-400 mt-1">Rebuilding Skill DNA model...</span>
    </div>
  );
};

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Skill Engine Evaluation Error',
  message = 'Failed to retrieve assessment results or build roadmap. Please try again.',
  onRetry,
}) => {
  return (
    <div className="p-6 bg-rose-50/50 border border-rose-200 rounded-lg shadow-sm flex items-start gap-4 my-4">
      <div className="w-9 h-9 rounded-full bg-rose-100 border border-rose-300 flex items-center justify-center shrink-0 text-rose-700">
        <AlertCircle className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <h4 className="text-sm font-bold text-rose-900 mb-0.5">{title}</h4>
        <p className="text-xs text-rose-700 leading-relaxed mb-3">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-rose-700 hover:bg-rose-800 text-white font-semibold text-xs rounded shadow-sm transition-colors cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry Assessment Sync
          </button>
        )}
      </div>
    </div>
  );
};
