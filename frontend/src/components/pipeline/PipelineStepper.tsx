import React from 'react';
import { Check, Loader2, PackageCheck, Sparkles } from 'lucide-react';
import { usePipeline } from '../../context/PipelineContext';

const STEPS = [
  { id: 1, label: 'Input', subtitle: 'Offer Data' },
  { id: 2, label: 'Extract', subtitle: 'Entities' },
  { id: 3, label: 'DNA', subtitle: 'Hashes' },
  { id: 4, label: 'Graph', subtitle: 'Relations' },
  { id: 5, label: 'Verify', subtitle: 'Registries' },
  { id: 6, label: 'Match', subtitle: 'Similarity' },
  { id: 7, label: 'Reason', subtitle: 'AI Risk' },
  { id: 8, label: 'Score', subtitle: 'Trust Rating' },
  { id: 9, label: 'Result', subtitle: 'Final Report' }
];

export const PipelineStepper: React.FC = () => {
  const { activeStep, setActiveStep, isAnalyzing } = usePipeline();

  const isComplete = activeStep === 9 && !isAnalyzing;
  const progressPercent = Math.round((activeStep / STEPS.length) * 100);

  return (
    <div className="bg-white border border-slate-200/90 rounded-3xl p-6 mb-6 shadow-sm overflow-x-auto select-none">
      {/* Tracking Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-bold transition-all duration-500 ${
            isComplete
              ? 'bg-emerald-50 text-emerald-600 border border-emerald-200 scale-105'
              : 'bg-blue-50 text-blue-600 border border-blue-100'
          }`}>
            {isComplete ? <PackageCheck className="w-5 h-5 text-emerald-600" /> : <Sparkles className="w-5 h-5 text-blue-600 animate-spin" style={{ animationDuration: '6s' }} />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-extrabold text-slate-900 tracking-tight">
                Verification Progress Tracking
              </h3>
              <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold transition-all duration-300 flex items-center gap-1.5 ${
                isComplete
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-sm'
                  : isAnalyzing
                  ? 'bg-blue-50 text-blue-700 border border-blue-200 animate-pulse'
                  : 'bg-slate-100 text-slate-600 border border-slate-200'
              }`}>
                {isComplete ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                    Verified Complete (100%)
                  </>
                ) : isAnalyzing ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping" />
                    Stage {activeStep} of 9 in progress...
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 rounded-full bg-slate-400" />
                    Stage {activeStep} Selected ({progressPercent}%)
                  </>
                )}
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium mt-0.5">
              Live animated tracking through 9-stage government recruitment fraud detection pipeline
            </p>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div className="w-52 space-y-1">
          <div className="flex justify-between text-[11px] font-bold text-slate-600">
            <span>Pipeline Progress</span>
            <span className="font-mono text-blue-600 font-extrabold transition-all duration-300">{progressPercent}%</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden border border-slate-200/60 p-0.5">
            <div
              className={`h-full rounded-full transition-all duration-700 ease-out shadow-sm ${
                isComplete
                  ? 'bg-emerald-500'
                  : 'bg-gradient-to-r from-blue-600 via-indigo-500 to-emerald-500 animate-flow-line'
              }`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Animated Timeline Stepper Track */}
      <div className="relative flex items-start justify-between min-w-[820px] px-6 pt-2 pb-1">
        {/* Base Inactive Track Line */}
        <div className="absolute top-[22px] left-[52px] right-[52px] h-[4px] bg-slate-100 rounded-full -z-0" />

        {/* Animated Active Progress Line */}
        <div
          className={`absolute top-[22px] left-[52px] h-[4px] rounded-full -z-0 transition-all duration-700 ease-in-out ${
            isComplete
              ? 'bg-emerald-500 shadow-sm shadow-emerald-500/40'
              : 'bg-gradient-to-r from-blue-600 via-indigo-500 to-emerald-500 animate-flow-line shadow-md shadow-blue-500/30'
          }`}
          style={{
            width: `calc(${((activeStep - 1) / (STEPS.length - 1)) * 100}% * (100% - 104px) / 100)`
          }}
        />

        {/* Traveling Pulsing Laser Orb along the animated progress line */}
        <div
          className="absolute top-[18px] w-3 h-3 bg-white border-2 border-blue-600 rounded-full shadow-[0_0_10px_#2563eb] -z-0 transition-all duration-700 ease-in-out animate-ping"
          style={{
            left: `calc(52px + (((activeStep - 1) / (STEPS.length - 1)) * 100% * (100% - 104px) / 100) - 6px)`,
            opacity: activeStep > 1 ? 1 : 0
          }}
        />

        {STEPS.map((step) => {
          const isCompleted = step.id < activeStep;
          const isActive = step.id === activeStep;
          const isClickable = isCompleted || step.id <= activeStep;

          return (
            <div
              key={step.id}
              onClick={() => isClickable && !isAnalyzing && setActiveStep(step.id)}
              className={`relative z-10 flex flex-col items-center gap-2 text-center transition-all duration-300 ${
                isClickable ? 'cursor-pointer opacity-100 hover:scale-105 active:scale-95' : 'cursor-not-allowed opacity-45'
              }`}
              style={{ width: '80px' }}
            >
              {/* Animated Status Circle Badge */}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-extrabold text-xs transition-all duration-500 relative ${
                  isCompleted
                    ? 'bg-gradient-to-tr from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-200 scale-100'
                    : isActive
                    ? 'bg-gradient-to-tr from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-500/40 ring-4 ring-blue-100 scale-110 animate-pulse-glow'
                    : 'bg-white text-slate-400 border-2 border-slate-200'
                }`}
              >
                {isCompleted ? (
                  <Check className="w-4 h-4 stroke-[3] animate-in zoom-in-50 duration-300" />
                ) : isActive && isAnalyzing ? (
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                ) : (
                  <span>{step.id}</span>
                )}
              </div>

              {/* Step Title & Subtitle */}
              <div className="flex flex-col items-center">
                <span
                  className={`text-xs tracking-tight transition-colors duration-300 ${
                    isActive
                      ? 'text-blue-600 font-extrabold scale-105'
                      : isCompleted
                      ? 'text-slate-900 font-bold'
                      : 'text-slate-400 font-medium'
                  }`}
                >
                  {step.label}
                </span>

                {/* E-Commerce Animated Status Tag */}
                <div className="mt-1">
                  {isCompleted ? (
                    <span className="inline-flex items-center gap-0.5 text-[9px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded-md border border-emerald-200/80 shadow-2xs">
                      <Check className="w-2.5 h-2.5 stroke-[3]" /> Done
                    </span>
                  ) : isActive ? (
                    <span className="inline-flex items-center gap-0.5 text-[9px] font-bold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded-md border border-blue-200/80 animate-pulse shadow-2xs">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-ping" /> Active
                    </span>
                  ) : (
                    <span className="text-[9px] font-semibold text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded-md border border-slate-200">
                      Pending
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};



