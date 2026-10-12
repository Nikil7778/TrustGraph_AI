'use client';

import React from 'react';
import { RoadmapStepData } from '../types';
import {
  CheckCircle2,
  Clock,
  Info,
  Lock,
  AlertTriangle,
  PlayCircle,
  FileCheck2,
  ShieldCheck,
} from 'lucide-react';

interface RoadmapStepProps {
  step: RoadmapStepData;
  isLast?: boolean;
  onStepClick?: (step: RoadmapStepData) => void;
}

export const RoadmapStep: React.FC<RoadmapStepProps> = ({
  step,
  isLast = false,
  onStepClick,
}) => {
  const normStatus = (step.status || 'upcoming').toLowerCase();

  let statusBadge = null;
  let icon = null;
  let cardBorder = 'border-slate-200 bg-white';
  let numberBg = 'bg-slate-100 text-slate-600 border-slate-300';
  let connectorColor = 'bg-slate-200';

  if (normStatus === 'completed' || normStatus === 'verified') {
    icon = <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />;
    statusBadge = (
      <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-300 flex items-center gap-1">
        ✓ Completed
      </span>
    );
    cardBorder = 'border-emerald-200 bg-emerald-50/10';
    numberBg = 'bg-emerald-100 text-emerald-800 border-emerald-400';
    connectorColor = 'bg-emerald-400';
  } else if (normStatus === 'recommended' || normStatus === 'current') {
    icon = <PlayCircle className="w-5 h-5 text-blue-600 shrink-0" />;
    statusBadge = (
      <span className="text-[11px] font-bold text-blue-800 bg-blue-100 px-2.5 py-0.5 rounded border border-blue-300 flex items-center gap-1">
        ● Recommended
      </span>
    );
    cardBorder = 'border-2 border-blue-500 bg-blue-50/30 shadow-sm';
    numberBg = 'bg-blue-600 text-white border-blue-600';
    connectorColor = 'bg-blue-300';
  } else if (normStatus === 'remediation') {
    icon = <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />;
    statusBadge = (
      <span className="text-[11px] font-bold text-amber-900 bg-amber-100 px-2 py-0.5 rounded border border-amber-300 flex items-center gap-1">
        ⚠ Remediation
      </span>
    );
    cardBorder = 'border-2 border-amber-400 bg-amber-50/30 shadow-sm';
    numberBg = 'bg-amber-600 text-white border-amber-600';
    connectorColor = 'bg-amber-300';
  } else if (normStatus === 'blocked') {
    icon = <Lock className="w-4.5 h-4.5 text-slate-400 shrink-0" />;
    statusBadge = (
      <span className="text-[11px] font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-300 flex items-center gap-1">
        🔒 Blocked
      </span>
    );
    cardBorder = 'border-slate-200 bg-slate-50/70 text-slate-600';
    numberBg = 'bg-slate-200 text-slate-500 border-slate-300';
    connectorColor = 'bg-slate-200';
  } else if (normStatus === 'in_progress' || normStatus === 'next') {
    icon = <PlayCircle className="w-5 h-5 text-indigo-600 shrink-0" />;
    statusBadge = (
      <span className="text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200">
        In Progress
      </span>
    );
    cardBorder = 'border-indigo-300 bg-indigo-50/15';
    numberBg = 'bg-indigo-600 text-white border-indigo-600';
    connectorColor = 'bg-indigo-300';
  } else {
    icon = <ShieldCheck className="w-4.5 h-4.5 text-slate-400 shrink-0" />;
    statusBadge = (
      <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
        Upcoming
      </span>
    );
  }

  const getTypeTag = (type: string) => {
    const t = (type || '').toLowerCase();
    switch (t) {
      case 'practice':
      case 'challenge':
        return 'bg-amber-100 text-amber-900 border-amber-200';
      case 'reassess':
      case 'reassessment':
        return 'bg-purple-100 text-purple-900 border-purple-200';
      case 'practical_task':
      case 'task':
        return 'bg-blue-100 text-blue-900 border-blue-200';
      case 'project':
      case 'capstone':
        return 'bg-slate-900 text-white border-slate-900';
      case 'foundation':
        return 'bg-emerald-100 text-emerald-900 border-emerald-200';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="relative flex items-start gap-3 sm:gap-4 group">
      {/* Step vertical connector */}
      {!isLast && (
        <div
          className={`absolute left-3.5 sm:left-4 top-10 bottom-0 w-0.5 ${connectorColor}`}
        />
      )}

      {/* Step node icon */}
      <div
        className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full border-2 flex items-center justify-center text-xs font-bold shrink-0 z-10 transition-transform ${numberBg}`}
      >
        {step.stepNumber}
      </div>

      {/* Card Content */}
      <div
        onClick={() => onStepClick && onStepClick(step)}
        className={`flex-1 p-4 rounded-lg border ${cardBorder} transition-all cursor-pointer hover:border-slate-400 mb-3 sm:mb-4 min-h-[44px] min-w-0 shadow-xs`}
      >
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 min-w-0">
            {icon}
            <h4 className="font-bold text-slate-900 text-sm sm:text-base truncate">
              {step.title}
            </h4>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            <span
              className={`text-[10px] sm:text-xs font-semibold px-2 py-0.5 rounded border uppercase tracking-wider ${getTypeTag(
                step.type
              )}`}
            >
              {step.type.replace('_', ' ')}
            </span>
            {statusBadge}
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-600 mt-2">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="font-medium text-slate-800">
              Target Skill: <strong className="text-slate-900">{step.skillName}</strong>
            </span>
            {step.estimatedTime && (
              <span className="flex items-center gap-1 text-slate-500">
                <Clock className="w-3.5 h-3.5" />
                {step.estimatedTime}
              </span>
            )}
          </div>
          {step.priority && (
            <span className="text-[11px] text-slate-500 font-medium">
              Priority: <span className="font-semibold text-slate-700">{step.priority}</span>
            </span>
          )}
        </div>

        {/* Rationale - Why it is here */}
        {step.rationale && (
          <div className="mt-2.5 pt-2 border-t border-slate-100 text-xs text-slate-600 flex items-start gap-1.5">
            <Info className="w-3.5 h-3.5 text-blue-500 shrink-0 mt-0.5" />
            <span className="leading-relaxed">
              <strong className="text-slate-700 font-semibold">Why in Roadmap:</strong>{' '}
              {step.rationale}
            </span>
          </div>
        )}

        {/* Expected Evidence Proof */}
        {step.evidenceRequired && (
          <div className="mt-1.5 text-xs text-emerald-800 bg-emerald-50/60 p-2 rounded border border-emerald-200/60 flex items-start gap-1.5">
            <FileCheck2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
            <span className="leading-relaxed">
              <strong className="text-emerald-900 font-semibold">Expected Proof:</strong>{' '}
              {step.evidenceRequired}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
