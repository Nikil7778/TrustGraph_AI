import React, { useState } from 'react';
import { ArrowRight, ShieldAlert, Eye, ChevronDown, ChevronUp } from 'lucide-react';
import type { DetailedFingerprintMatch, FieldMatchResult } from '../../types';

export const SuspiciousMatchingView: React.FC<{ data: DetailedFingerprintMatch; onNext: () => void }> = ({ data, onNext }) => {
  const match = data || {
    matchedScamId: 'RF-NONE',
    matchedScamName: 'No Fraudulent Match Detected',
    scamCategory: 'Clean Verification',
    fieldMatches: [],
    matchedFieldsCount: 0,
    totalFieldsEvaluated: 9,
    overallSimilarityPercentage: 0.0,
    breakdownSummary: '0/9 characteristics matched'
  };

  const [showDetails, setShowDetails] = useState<boolean>(true);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Matching with Known Suspicious Fingerprints</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Compare this Recruitment DNA against previously identified suspicious recruitment fingerprints.
          </p>
        </div>
        <button
          onClick={onNext}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <span>Next: AI Risk Reasoning</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-red-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-red-50 text-red-600 border border-red-100 flex items-center justify-center font-bold text-sm">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-bold text-slate-400 uppercase font-mono">Fingerprint Match ID: {match.matchedScamId}</span>
              <h3 className="text-lg font-extrabold text-slate-900">{match.matchedScamName}</h3>
              <p className="text-xs text-slate-500 font-medium">{match.scamCategory}</p>
            </div>
          </div>

          <div className="text-right">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-100 text-red-800 font-black text-sm">
              <span>Similarity: {match.overallSimilarityPercentage}%</span>
            </div>
            <p className="text-xs font-bold text-slate-700 mt-1">{match.breakdownSummary}</p>
          </div>
        </div>

        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full py-2.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 text-xs font-bold transition-colors flex items-center justify-center gap-2"
        >
          <Eye className="w-4 h-4 text-blue-600" />
          <span>{showDetails ? 'Hide Field-by-Field Detailed Comparison' : 'View Field-by-Field Detailed Comparison'}</span>
          {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showDetails && (
          <div className="pt-2 space-y-4">
            <div className="bg-slate-50/80 rounded-2xl border border-slate-200/80 overflow-hidden">
              {/* Explicit Table Column Header Bar */}
              <div className="grid grid-cols-12 gap-2 bg-slate-100 px-4 py-3 border-b border-slate-200 text-[11px] font-extrabold text-slate-700 uppercase tracking-wider">
                <div className="col-span-3">Characteristic Field</div>
                <div className="col-span-5">Submitted Offer Parameter</div>
                <div className="col-span-2 text-center">Weight</div>
                <div className="col-span-2 text-right">Match Verdict</div>
              </div>

              {/* Data Rows */}
              <div className="divide-y divide-slate-100 p-2">
                {match.fieldMatches?.map((field: FieldMatchResult, idx: number) => (
                  <div key={idx} className="grid grid-cols-12 gap-2 items-center px-2 py-2.5 text-xs">
                    <div className="col-span-3 font-bold text-slate-900">{field.fieldName}</div>
                    <div className="col-span-5 text-slate-600 font-mono text-[11px] truncate">
                      {field.claimedValue}
                    </div>
                    <div className="col-span-2 text-center text-slate-400 font-mono text-[11px]">
                      {field.weight}%
                    </div>
                    <div className="col-span-2 text-right">
                      <span
                        className={`inline-block px-2.5 py-1 rounded-lg font-extrabold text-[11px] ${
                          field.matchType === 'EXACT'
                            ? 'bg-emerald-100 text-emerald-800'
                            : field.matchType === 'SIMILAR'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {field.matchType === 'EXACT' && '✓ EXACT'}
                        {field.matchType === 'SIMILAR' && '⚠ SIMILAR'}
                        {field.matchType === 'DIFFERENT' && '✕ DIFFERENT'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-blue-50 border border-blue-100 text-center space-y-1">
              <p className="text-sm font-extrabold text-blue-900">
                {match.matchedFieldsCount} of {match.totalFieldsEvaluated} characteristics matched
              </p>
              <p className="text-base font-black text-blue-600">
                Calculated Weighted Similarity: {match.overallSimilarityPercentage}%
              </p>
              <p className="text-[11px] text-slate-500">
                (Weighted sum of Exact & Similar fields vs threat database record {match.matchedScamId})
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
