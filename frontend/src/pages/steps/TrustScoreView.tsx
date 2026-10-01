import React from 'react';
import { ArrowRight } from 'lucide-react';
import type { TrustScoreBreakdown } from '../../types';

export const TrustScoreView: React.FC<{ data: TrustScoreBreakdown; onNext: () => void }> = ({ data, onNext }) => {
  const trustScore = data || {
    overallScore: 18,
    riskLevel: 'CRITICAL_SCAM',
    subScores: {
      officialRegistryAlignment: 5,
      suspiciousSimilarityPenalty: 3,
      riskAnomalyPenalty: 10
    },
    recommendation: 'DO NOT proceed with this recruitment offer. High risk of financial and data fraud.'
  };

  const isGenuine = trustScore.riskLevel === 'VERIFIED_GENUINE' || trustScore.overallScore >= 80;
  const isLowRisk = trustScore.riskLevel === 'LOW_RISK' || trustScore.overallScore >= 60;
  const isMediumRisk = trustScore.riskLevel === 'MEDIUM_RISK' || trustScore.overallScore >= 40;

  const circleBorderClass = isGenuine
    ? 'border-emerald-500 bg-emerald-50/50'
    : isLowRisk
    ? 'border-blue-500 bg-blue-50/50'
    : isMediumRisk
    ? 'border-amber-500 bg-amber-50/50'
    : 'border-red-500 bg-red-50/50';

  const badgeClass = isGenuine
    ? 'bg-emerald-100 text-emerald-800 font-black'
    : isLowRisk
    ? 'bg-blue-100 text-blue-800 font-black'
    : isMediumRisk
    ? 'bg-amber-100 text-amber-800 font-black'
    : 'bg-red-100 text-red-800 font-black';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900">Trust Score Calculated</h2>
          <p className="text-sm text-slate-500 font-medium mt-1">
            Multi-factor weighted trust score calculated from official data, suspicious similarity, and AI anomalies.
          </p>
        </div>
        <button
          onClick={onNext}
          className="px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md shadow-blue-600/20 transition-all flex items-center gap-2"
        >
          <span>View Final Explainable Result</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200/80 p-8 shadow-sm text-center space-y-6">
        <div className={`inline-flex flex-col items-center justify-center w-44 h-44 rounded-full border-8 shadow-inner ${circleBorderClass}`}>
          <span className="text-5xl font-black text-slate-900">{trustScore.overallScore}</span>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-widest mt-1">out of 100</span>
        </div>

        <div>
          <span className={`px-4 py-1.5 rounded-full text-sm uppercase tracking-wide ${badgeClass}`}>
            {trustScore.riskLevel.replace('_', ' ')}
          </span>
          <p className="text-sm font-semibold text-slate-700 max-w-xl mx-auto mt-3">
            {trustScore.recommendation}
          </p>
        </div>

        <div className="max-w-xl mx-auto space-y-4 pt-4 border-t border-slate-100 text-left">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wide">Score Component Breakdown</h4>

          <div>
            <div className="flex justify-between text-xs font-bold mb-1">
              <span>Official Registry Alignment</span>
              <span>{trustScore.subScores?.officialRegistryAlignment} / 40 pts</span>
            </div>
            <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full transition-all"
                style={{ width: `${(trustScore.subScores?.officialRegistryAlignment / 40) * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold mb-1">
              <span>Suspicious Fingerprint Penalty</span>
              <span>{trustScore.subScores?.suspiciousSimilarityPenalty} / 35 pts</span>
            </div>
            <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-purple-600 rounded-full transition-all"
                style={{ width: `${(trustScore.subScores?.suspiciousSimilarityPenalty / 35) * 100}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs font-bold mb-1">
              <span>Evidence Consistency & Risk Factors</span>
              <span>{trustScore.subScores?.riskAnomalyPenalty} / 25 pts</span>
            </div>
            <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full bg-emerald-600 rounded-full transition-all"
                style={{ width: `${(trustScore.subScores?.riskAnomalyPenalty / 25) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
