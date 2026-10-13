'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import { api, ApiRoadmapChange, ApiRoadmapHistory } from '../../services/api';
import {
  CheckCircle2,
  Play,
  RotateCw,
  Clock,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  AlertTriangle,
  Zap,
  ChevronDown,
  ChevronUp,
  History,
  FileCheck2,
} from 'lucide-react';

export default function RoadmapPage() {
  const router = useRouter();
  const {
    activeUserId,
    activeUser,
    roadmap,
    userEvidence,
    skillDebts,
    rebuildRoadmap,
    isDemoMode,
  } = useLearner();

  const [isRebuilding, setIsRebuilding] = useState<boolean>(false);
  const [showDetails, setShowDetails] = useState<boolean>(true);
  const [history, setHistory] = useState<ApiRoadmapHistory[]>([]);

  const targetRoleName =
    activeUser?.target_role?.name || roadmap?.target_role_name || 'Data Analyst';

  const isUnassessed = userEvidence.length === 0;
  const activeStep =
    roadmap?.steps.find(
      (s) => s.status === 'IN_PROGRESS' || s.status === 'RECOMMENDED'
    ) || roadmap?.steps[0];
  const completedCount =
    roadmap?.steps.filter((s) => s.status === 'COMPLETED').length || 0;
  const totalSteps = roadmap?.steps.length || 0;
  const hasSkillDebt = skillDebts.some((d) => d.debt_status === 'SKILL_DEBT');

  useEffect(() => {
    if (!activeUserId) return;
    api.getRoadmapHistory(activeUserId).then(setHistory).catch(() => []);
  }, [activeUserId]);

  const handleRebuild = async () => {
    setIsRebuilding(true);
    try {
      await rebuildRoadmap();
    } catch (err) {
      console.error('Failed to rebuild roadmap:', err);
    } finally {
      setIsRebuilding(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-5 max-w-6xl mx-auto">
        {/* ========================================================================= */}
        {/* 1. HEADER (Matches Stitch Screenshot 4)                                   */}
        {/* ========================================================================= */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Roadmap</h1>
              <span className="text-[11px] font-mono text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                v{roadmap?.version || (isUnassessed ? 1 : '3.2')} Adaptive Graph
              </span>
            </div>
            <p className="text-xs text-slate-500 italic mt-0.5">
              &ldquo;The learner doesn&apos;t follow the roadmap. The roadmap follows the learner.&rdquo;
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs font-semibold text-blue-900 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-full shadow-2xs inline-flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
              <span>Target: {targetRoleName} • {isUnassessed ? 'Not assessed' : '68% Career Readiness'}</span>
            </span>

            <button
              onClick={handleRebuild}
              disabled={isRebuilding}
              className="p-1.5 text-slate-500 hover:text-slate-800 bg-white hover:bg-slate-50 border border-slate-200 rounded-md transition-colors cursor-pointer"
              title="Force Rebuild Adaptive Graph"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isRebuilding ? 'animate-spin text-blue-600' : ''}`} />
            </button>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 2. ADAPTIVE RE-ROUTE BANNER                                               */}
        {/* ========================================================================= */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
              <h3 className="text-sm font-bold text-slate-900">
                {isUnassessed ? 'Onboarding & Diagnostic Sequence' : 'Why did my roadmap change?'}
              </h3>
              <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {isUnassessed ? '• Baseline Setup' : '• Adaptive Re-route - Yesterday at 16:42'}
              </span>
            </div>

            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-xs text-slate-500 hover:text-slate-800 font-medium inline-flex items-center gap-1 cursor-pointer"
            >
              <span>{showDetails ? 'Hide Details' : 'Details'}</span>
              {showDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>

          {showDetails && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1 text-xs text-slate-600 border-t border-slate-100">
              <p className="max-w-2xl leading-relaxed">
                {isUnassessed
                  ? 'Complete your baseline diagnostic assessment to evaluate your competencies, build your Skill DNA, and generate your personalized learning path.'
                  : 'Based on recent query execution in the Retail Analytics Lab, the adaptive engine inserted a targeted remediation (SQL JOIN Rescue Practice) before unlocking downstream Exploratory Data Analysis.'}
              </p>

              <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 inline-flex items-center gap-1 shrink-0 self-start sm:self-auto">
                <Zap className="w-3 h-3 text-emerald-600" />
                <span>{isUnassessed ? 'Est. 20 min diagnostic' : 'Saved ~6.2 hrs downstream rework'}</span>
              </span>
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* 3. 3-CARD METRIC STRIP                                                    */}
        {/* ========================================================================= */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          {/* Card 1: Verified Evidence */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                VERIFIED EVIDENCE
              </span>
              <span className="text-lg font-black text-slate-900 mt-0.5 block">
                {completedCount}{' '}
                <span className="text-slate-400 font-normal text-xs">
                  / {totalSteps} Milestones
                </span>
              </span>
            </div>
            <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>

          {/* Card 2: Current Focus */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                CURRENT FOCUS
              </span>
              <span className="text-sm font-bold text-blue-900 mt-0.5 block truncate max-w-[150px]">
                {activeStep?.title || 'Diagnostic Assessment'}
              </span>
            </div>
            <div className="w-8 h-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
              <Play className="w-4 h-4 fill-blue-600" />
            </div>
          </div>

          {/* Card 3: Intervention State */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                INTERVENTION STATE
              </span>
              <span className={`text-sm font-bold mt-0.5 block ${hasSkillDebt ? 'text-rose-700' : 'text-slate-800'}`}>
                {isUnassessed ? 'Onboarding' : hasSkillDebt ? 'Active Drill' : 'Standard Path'}
              </span>
            </div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${hasSkillDebt ? 'bg-rose-50 text-rose-600' : 'bg-blue-50 text-blue-600'}`}>
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 4. VERTICAL TIMELINE / ROADMAP FLOW (Matches Stitch Screenshot 4)         */}
        {/* ========================================================================= */}
        <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-200">
          {roadmap?.steps && roadmap.steps.length > 0 ? (
            roadmap.steps.map((step) => {
              const isCompleted = step.status === 'COMPLETED';
              const isCurrent =
                step.status === 'IN_PROGRESS' || step.status === 'RECOMMENDED';

              if (isCompleted) {
                return (
                  <div key={step.id} className="relative">
                    <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0 ring-4 ring-slate-50">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2">
                      <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                          STEP {step.order_index < 10 ? `0${step.order_index}` : step.order_index} • {step.step_type} • COMPLETED
                        </span>
                        <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                          • Verified
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-slate-900">{step.title}</h3>
                      {step.reason && (
                        <p className="text-xs text-slate-500 leading-relaxed">{step.reason}</p>
                      )}
                      <div className="flex items-center gap-4 pt-2 text-[11px] text-slate-400">
                        <span>{step.skill_name || 'Core Competency'}</span>
                        <span>•</span>
                        <span>Mastery Verified</span>
                      </div>
                    </div>
                  </div>
                );
              }

              if (isCurrent) {
                return (
                  <div key={step.id} className="relative">
                    <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-md bg-blue-800 text-white flex items-center justify-center shrink-0 ring-4 ring-slate-50 shadow-xs">
                      <Play className="w-3.5 h-3.5 fill-white" />
                    </div>
                    <div className="bg-white border-2 border-blue-600/80 rounded-xl p-5 shadow-xs space-y-3">
                      <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                            • STEP {step.order_index < 10 ? `0${step.order_index}` : step.order_index} • {step.step_type}
                          </span>
                          <span className="text-[10px] font-bold text-white bg-blue-800 px-2 py-0.5 rounded">
                            CURRENT FOCUS
                          </span>
                        </div>
                        <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <span>Est. {step.estimated_minutes} min</span>
                        </span>
                      </div>

                      <div>
                        <h3 className="text-lg font-bold text-slate-900">{step.title}</h3>
                        <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                          {step.reason ||
                            (isUnassessed
                              ? 'Baseline diagnostic assessment to baseline your skills and build your personalized skill graph.'
                              : 'Targeted learning milestone to reach job qualification.')}
                        </p>
                      </div>

                      <div className="pt-2 flex items-center gap-3">
                        <button
                          onClick={() => {
                            if (step.module_slug) {
                              router.push(`/learn/${step.module_slug}`);
                            } else if (
                              step.step_type === 'ASSESSMENT' ||
                              step.title.toLowerCase().includes('assessment')
                            ) {
                              router.push('/assessments');
                            } else if (step.step_type === 'PROJECT') {
                              router.push('/projects');
                            } else {
                              router.push('/practice-lab');
                            }
                          }}
                          className="px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                        >
                          <span>
                            {step.module_slug
                              ? 'Enter Learning Module'
                              : step.step_type === 'ASSESSMENT' || step.title.toLowerCase().includes('assessment')
                              ? 'Start Assessment'
                              : 'Start Practice'}
                          </span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              }

              return (
                <div key={step.id} className="relative">
                  <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-full bg-white border border-slate-300 text-slate-500 font-mono text-[10px] font-bold flex items-center justify-center shrink-0 ring-4 ring-slate-50">
                    {step.order_index < 10 ? `0${step.order_index}` : step.order_index}
                  </div>
                  <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2 opacity-85">
                    <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                        STEP {step.order_index < 10 ? `0${step.order_index}` : step.order_index} • {step.step_type} • {step.status === 'BLOCKED' ? 'LOCKED' : 'UPCOMING'}
                      </span>
                      <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-400" />
                        <span>Est. {step.estimated_minutes} min</span>
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <h3 className="text-base font-bold text-slate-800">{step.title}</h3>
                      {step.module_slug && (
                        <button
                          onClick={() => router.push(`/learn/${step.module_slug}`)}
                          className="text-xs font-semibold text-blue-700 hover:text-blue-900 inline-flex items-center gap-1 cursor-pointer"
                        >
                          <span>View Module</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed">
                      {step.reason || 'Upcoming competency block in career path.'}
                    </p>
                  </div>
                </div>
              );
            })
          ) : null}
        </div>
      </div>
    </AppShell>
  );
}
