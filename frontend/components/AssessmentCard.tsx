'use client';

import React from 'react';
import { AssessmentData } from '../types';
import { Clock, HelpCircle, ArrowRight, CheckCircle2 } from 'lucide-react';

interface AssessmentCardProps {
  assessment: AssessmentData;
  onStart?: () => void;
}

export const AssessmentCard: React.FC<AssessmentCardProps> = ({
  assessment,
  onStart,
}) => {
  const isCompleted = assessment.status === 'completed';

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col justify-between min-w-0">
      <div>
        <div className="flex items-center justify-between text-xs font-semibold text-slate-500 mb-2 gap-2 flex-wrap">
          <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-600 border border-slate-200 truncate">
            {assessment.skillCategory}
          </span>
          {isCompleted ? (
            <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 flex items-center gap-1 shrink-0">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Score: {assessment.latestScore}%
            </span>
          ) : (
            <span className="text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 shrink-0">
              Ready to Take
            </span>
          )}
        </div>

        <h4 className="font-bold text-slate-900 text-base mb-1">{assessment.title}</h4>
        <p className="text-xs text-slate-500 mb-4">Target Skill: <strong className="text-slate-700">{assessment.targetSkill}</strong></p>

        <div className="flex items-center gap-3 sm:gap-4 text-xs text-slate-500 border-t border-slate-100 pt-3 flex-wrap">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            {assessment.durationMinutes} mins
          </span>
          <span className="flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
            {assessment.questionCount} Questions
          </span>
          {assessment.lastTaken && (
            <span className="text-slate-400">Taken {assessment.lastTaken}</span>
          )}
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100">
        <button
          onClick={onStart}
          className={`w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-md font-semibold text-xs transition-colors cursor-pointer min-h-[44px] ${
            isCompleted
              ? 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300'
              : 'bg-blue-800 hover:bg-blue-900 text-white shadow-xs'
          }`}
        >
          {isCompleted ? 'Retake Assessment' : 'Start Diagnostic Assessment'}
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
