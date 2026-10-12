'use client';

import React from 'react';
import { RoadmapStepData } from '../types';
import { RoadmapStep } from './RoadmapStep';
import { RefreshCw, MapPin } from 'lucide-react';

interface RoadmapProps {
  steps: RoadmapStepData[];
  onSelectStep?: (step: RoadmapStepData) => void;
  compact?: boolean;
}

export const Roadmap: React.FC<RoadmapProps> = ({
  steps,
  onSelectStep,
  compact = false,
}) => {
  const displaySteps = compact ? steps.slice(0, 5) : steps;

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-5 shadow-sm min-w-0">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3 sm:pb-4 mb-4 sm:mb-5 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-600 shrink-0" />
            <h3 className="text-base font-bold text-slate-900">Dynamic Evidence-Driven Roadmap</h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            The roadmap follows the learner — rebuilt continuously after demonstrated proof.
          </p>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] sm:text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200 self-start sm:self-auto shrink-0">
          <RefreshCw className="w-3.5 h-3.5 text-emerald-600 animate-spin-slow" />
          <span>Roadmap updated live</span>
        </div>
      </div>

      <div className="space-y-1">
        {displaySteps.map((step, index) => (
          <RoadmapStep
            key={step.id}
            step={step}
            isLast={index === displaySteps.length - 1}
            onStepClick={onSelectStep}
          />
        ))}
      </div>
    </div>
  );
};
