'use client';

import React, { useEffect, useState } from 'react';
import { api, ApiMLPredictionResponse } from '../services/api';
import { Loader2, HelpCircle, ChevronDown, ChevronUp, AlertCircle, Sparkles } from 'lucide-react';

interface NextProofReadinessProps {
  userId?: number;
  skillId: number;
  skillName: string;
  compact?: boolean;
  showExplainable?: boolean;
  className?: string;
}

export const NextProofReadiness: React.FC<NextProofReadinessProps> = ({
  userId = 1,
  skillId,
  skillName,
  compact = false,
  showExplainable = true,
  className = '',
}) => {
  const [prediction, setPrediction] = useState<ApiMLPredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isWhyOpen, setIsWhyOpen] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setError(null);

    api
      .getSkillMasteryPrediction(userId, skillId)
      .then((data) => {
        if (isMounted) {
          setPrediction(data);
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.warn(`[ML Service] Could not fetch prediction for skill ${skillId}:`, err);
          setError('Next-proof prediction is temporarily unavailable.');
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [userId, skillId]);

  // Status badge styling following existing SkillPath status system
  const getRiskBadge = (risk: 'LOW' | 'MEDIUM' | 'HIGH') => {
    switch (risk) {
      case 'LOW':
        return {
          bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
          dot: 'bg-emerald-600',
          label: 'LOW RISK',
          hint: 'Learner appears relatively ready for the next proof attempt.',
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-50 text-amber-800 border-amber-200',
          dot: 'bg-amber-600',
          label: 'MEDIUM RISK',
          hint: 'Learner is approaching readiness; reinforcement recommended.',
        };
      case 'HIGH':
      default:
        return {
          bg: 'bg-rose-50 text-rose-800 border-rose-200',
          dot: 'bg-rose-600',
          label: 'HIGH RISK',
          hint: 'Learner may benefit from preparation before attempting proof.',
        };
    }
  };

  // 1. Loading State
  if (isLoading) {
    if (compact) {
      return (
        <span className={`inline-flex items-center gap-1.5 text-[11px] text-slate-500 font-medium ${className}`}>
          <Loader2 className="w-3 h-3 animate-spin text-blue-600 shrink-0" />
          <span>Calculating next-proof readiness...</span>
        </span>
      );
    }
    return (
      <div className={`p-3.5 rounded-lg border border-slate-200 bg-slate-50/70 text-xs text-slate-600 flex items-center gap-2 ${className}`}>
        <Loader2 className="w-4 h-4 animate-spin text-blue-600 shrink-0" />
        <span>Calculating next-proof readiness...</span>
      </div>
    );
  }

  // 2. Error State
  if (error || !prediction) {
    if (compact) {
      return (
        <span className={`text-[11px] text-slate-400 font-medium ${className}`} title="Next-proof prediction is temporarily unavailable.">
          Next-proof prediction is temporarily unavailable.
        </span>
      );
    }
    return (
      <div className={`p-3 rounded-lg border border-slate-200 bg-slate-50 text-xs text-slate-500 flex items-center gap-2 ${className}`}>
        <AlertCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span>Next-proof prediction is temporarily unavailable.</span>
      </div>
    );
  }

  // 2b. Insufficient evidence state (Section 3: Not enough learning evidence yet)
  if (prediction.risk_level === 'UNKNOWN' || prediction.advisory_explanation?.includes('Not enough')) {
    if (compact) {
      return (
        <span className={`text-[11px] text-slate-400 font-medium ${className}`} title="Not enough learning evidence yet.">
          Not enough learning evidence yet
        </span>
      );
    }
    return (
      <div className={`p-3 rounded-lg border border-slate-200 bg-slate-50 text-xs text-slate-500 flex items-center gap-2 ${className}`}>
        <HelpCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />
        <span>Not enough learning evidence yet. Complete your diagnostic assessment to generate predictions.</span>
      </div>
    );
  }

  const pct = Math.round(prediction.mastery_probability * 100);
  const riskMeta = getRiskBadge(prediction.risk_level);

  // 3. Compact Mode (for Next-Best-Proof strip or table cell)
  if (compact) {
    return (
      <div className={`inline-flex items-center gap-2 flex-wrap ${className}`}>
        <span className="text-xs text-slate-600">
          Next-proof readiness: <strong className="font-bold text-slate-900">{pct}%</strong>
        </span>
        <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded border ${riskMeta.bg}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${riskMeta.dot}`} />
          {prediction.risk_level}
        </span>
      </div>
    );
  }

  // 4. Standard Section (for Skill DNA inspector / skill detail card)
  return (
    <div className={`rounded-lg border border-slate-200 bg-white p-3.5 space-y-3 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
            NEXT-PROOF READINESS
          </span>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Model estimate based on your current learning evidence.
          </p>
        </div>

        <span
          className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded border shrink-0 ${riskMeta.bg}`}
          title={riskMeta.hint}
        >
          <span className={`w-1.5 h-1.5 rounded-full ${riskMeta.dot}`} />
          {riskMeta.label}
        </span>
      </div>

      {/* Main Metric Display */}
      <div className="flex items-baseline gap-2.5 pt-1">
        <span className="text-2xl font-black text-slate-900 tracking-tight font-mono">
          {pct}%
        </span>
        <span className="text-xs font-semibold text-slate-700">
          Predicted success on next proof
        </span>
      </div>

      <p className="text-xs text-slate-600 leading-relaxed">
        Based on your recent accuracy, attempts, recency, and available evidence.
      </p>

      {/* Expandable 'Why this?' interaction */}
      {showExplainable && (
        <div className="border-t border-slate-100 pt-2.5">
          <button
            type="button"
            onClick={() => setIsWhyOpen(!isWhyOpen)}
            aria-expanded={isWhyOpen}
            className="inline-flex items-center gap-1.5 text-[11px] font-bold text-slate-700 hover:text-slate-900 transition-colors cursor-pointer"
          >
            <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
            <span>Why this next-proof readiness?</span>
            {isWhyOpen ? (
              <ChevronUp className="w-3 h-3 text-slate-400" />
            ) : (
              <ChevronDown className="w-3 h-3 text-slate-400" />
            )}
          </button>

          {isWhyOpen && (
            <div className="mt-2 p-3 bg-slate-50 rounded-md border border-slate-200 space-y-2 text-xs animate-in fade-in duration-150">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600 block">
                Strongest model signals:
              </span>

              {prediction.top_signals && prediction.top_signals.length > 0 ? (
                <ul className="space-y-1.5 text-[11px] text-slate-700">
                  {prediction.top_signals.map((signal, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-blue-600 font-bold shrink-0">•</span>
                      <span>{signal.description}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-[11px] text-slate-500">
                  Evaluated across prior proof attempts and evidence recency.
                </p>
              )}

              <div className="pt-2 border-t border-slate-200/80 text-[10px] text-slate-500 flex items-center justify-between gap-2">
                <span>Status: {riskMeta.hint}</span>
                <span className="font-mono text-slate-400">Model v{prediction.model_version}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
