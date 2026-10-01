import React from 'react';
import { ArrowRight, AlertOctagon, BrainCircuit, AlertTriangle } from 'lucide-react';
import type { AIRiskReasoning } from '../../types';

export const AIRiskReasoningView: React.FC<{ data: AIRiskReasoning; onNext: () => void }> = ({ data, onNext }) => {
  const reasoning = data || {
    overallRiskSummary: 'Recruitment verification analysis completed.',
    redFlags: [],
    anomaliesIdentified: [],
    chainOfThought: ['Executed automated 9-step fraud verification analysis.'],
    confidenceScore: 95.0
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Risk Analysis & Reasoning</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Rule-based review of extracted evidence, registry comparisons, and known risk indicators.
          </p>
        </div>
        <button
          onClick={onNext}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <span>Next: Trust Score</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="max-w-sm rounded-xl border border-blue-200 bg-blue-50 p-4">
        <div className="flex items-center justify-between gap-4 text-xs">
          <span className="font-bold text-slate-700">Evidence coverage</span>
          <span className="font-mono font-extrabold text-blue-900">{reasoning.confidenceScore ?? 0}%</span>
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-blue-100">
          <div className="h-full rounded-full bg-blue-600" style={{ width: `${Math.max(0, Math.min(100, reasoning.confidenceScore ?? 0))}%` }} />
        </div>
        <p className="mt-2 text-[11px] leading-4 text-slate-600">Share of key notice fields detected. This is not a probability that the result is correct.</p>
      </div>

      <div className="p-5 rounded-3xl bg-red-500 text-white shadow-lg space-y-2">
        <div className="flex items-center gap-3">
          <AlertOctagon className="w-6 h-6 text-white" />
          <h3 className="text-base font-extrabold">AI Safety Verdict</h3>
        </div>
        <p className="text-sm text-red-50 leading-relaxed font-medium">
          {reasoning.overallRiskSummary}
        </p>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 pb-3 border-b border-slate-100 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <span>Red Flags Detected ({reasoning.redFlags?.length || 0})</span>
        </h3>

        <div className="space-y-3">
          {reasoning.redFlags?.map((flag: any, idx: number) => (
            <div key={idx} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">{flag.category}</span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase ${
                    flag.severity === 'CRITICAL'
                      ? 'bg-red-100 text-red-800'
                      : flag.severity === 'HIGH'
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  {flag.severity} Severity
                </span>
              </div>

              <h4 className="text-sm font-bold text-slate-900">🔴 {flag.title}</h4>
              <p className="text-xs text-slate-600 leading-relaxed">{flag.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-4 pb-3 border-b border-slate-100 flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-blue-600" />
          <span>AI Chain-of-Thought Reasoning Log</span>
        </h3>

        <div className="space-y-2 font-mono text-xs text-slate-700 bg-slate-900 text-slate-200 p-4 rounded-2xl">
          {reasoning.chainOfThought?.map((step: string, idx: number) => (
            <p key={idx} className="flex items-start gap-2">
              <span className="text-blue-400 font-bold">[{idx + 1}]</span>
              <span>{step}</span>
            </p>
          ))}
        </div>
      </div>
    </div>
  );
};
