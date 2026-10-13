'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AppShell } from '../components/AppShell';
import { useLearner } from '../context/LearnerContext';
import { useCoach } from '../context/CoachContext';
import { api, ApiDashboardResponse } from '../services/api';
import { NextProofReadiness } from '../components/NextProofReadiness';
import {
  Target,
  ArrowRight,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  GitFork,
  Radio,
  FileCheck,
  Check,
  ExternalLink,
  Sparkles,
  TrendingUp,
  X,
  PlusCircle,
  Layers,
  Loader2,
  Zap,
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { activeUserId, refreshUser } = useLearner();
  const { openCoach } = useCoach();

  const [dashboardData, setDashboardData] = useState<ApiDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Phase 1 Goal Switcher & Custom Goal state
  const [isGoalModalOpen, setIsGoalModalOpen] = useState<boolean>(false);
  const [isSwitchingGoal, setIsSwitchingGoal] = useState<boolean>(false);
  const [isCustomMode, setIsCustomMode] = useState<boolean>(false);
  const [customGoalName, setCustomGoalName] = useState<string>('');
  const [customGoalDesc, setCustomGoalDesc] = useState<string>('');
  const [customGoalSkills, setCustomGoalSkills] = useState<string>('');
  const [goalModalError, setGoalModalError] = useState<string | null>(null);

  // Load live deterministic dashboard data
  const loadDashboard = useCallback(async () => {
    if (!activeUserId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getDashboard(activeUserId);
      setDashboardData(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load dashboard data.';
      console.error('Failed to fetch dashboard:', err);
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [activeUserId]);

  const handleSelectGoal = async (roleId: number) => {
    if (!activeUserId || isSwitchingGoal) return;
    setIsSwitchingGoal(true);
    setGoalModalError(null);
    try {
      await api.updateUser(activeUserId, { target_role_id: roleId });
      await refreshUser();
      await loadDashboard();
      setIsGoalModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to switch target goal.';
      setGoalModalError(msg);
    } finally {
      setIsSwitchingGoal(false);
    }
  };

  const handleCreateAndSelectCustomGoal = async () => {
    if (!activeUserId || isSwitchingGoal || !customGoalName.trim()) {
      setGoalModalError('Please enter a goal name.');
      return;
    }
    setIsSwitchingGoal(true);
    setGoalModalError(null);
    try {
      const skillsArray = customGoalSkills
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      const newRole = await api.createCustomRole({
        name: customGoalName.trim(),
        description: customGoalDesc.trim() || undefined,
        skills: skillsArray.length > 0 ? skillsArray : undefined,
      });

      await api.updateUser(activeUserId, { target_role_id: newRole.id });
      await refreshUser();
      await loadDashboard();
      setIsGoalModalOpen(false);
      setIsCustomMode(false);
      setCustomGoalName('');
      setCustomGoalDesc('');
      setCustomGoalSkills('');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create and assign custom goal.';
      setGoalModalError(msg);
    } finally {
      setIsSwitchingGoal(false);
    }
  };


  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const isUnassessed = Boolean(
    dashboardData && dashboardData.metrics.evidence_records_count === 0
  );

  return (
    <AppShell>
      {/* 1. LOADING & ERROR STATES */}
      {isLoading && !dashboardData && (
        <div className="space-y-5 animate-pulse">
          <div className="h-10 bg-slate-200 rounded-md w-72" />
          <div className="bg-white border border-slate-200 rounded-xl p-5 h-36" />
          <div className="bg-white border border-slate-200 rounded-xl p-5 h-48" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="bg-white border border-slate-200 rounded-xl p-5 h-64" />
            <div className="bg-white border border-slate-200 rounded-xl p-5 h-64" />
          </div>
        </div>
      )}

      {error && !dashboardData && (
        <div className="bg-rose-50 border border-rose-200 rounded-lg p-6 text-center space-y-3 my-6">
          <AlertTriangle className="w-8 h-8 text-rose-600 mx-auto" />
          <h3 className="font-bold text-slate-900 text-base">Unable to Load Dashboard</h3>
          <p className="text-xs text-slate-600 max-w-md mx-auto">{error}</p>
        </div>
      )}

      {dashboardData && (
        <div className="space-y-5">
          {/* ========================================================================= */}
          {/* 1. WELCOME HEADER                                                         */}
          {/* ========================================================================= */}
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Welcome back, {dashboardData.learner_name.split(' ')[0]}
            </h1>
            <p className="text-sm text-slate-500 mt-0.5">
              {isUnassessed
                ? 'Complete your baseline diagnostic to generate your personalized skill graph.'
                : 'What should you work on next to reach job-readiness?'}
            </p>
          </div>

          {/* ========================================================================= */}
          {/* 2. TARGET ROLE & CAREER READINESS HERO CARD                               */}
          {/* ========================================================================= */}
          {/* ========================================================================= */}
          {/* 2. TARGET ROLE & CAREER READINESS HERO CARD                               */}
          {/* ========================================================================= */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  TARGET GOAL
                </span>
                <span className="text-sm font-bold text-slate-900">
                  {dashboardData.target_role_name}
                </span>
                <button
                  type="button"
                  onClick={() => setIsGoalModalOpen(true)}
                  className="px-2.5 py-1 text-[11px] font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <GitFork className="w-3 h-3 text-blue-600" /> Switch Goal
                </button>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <span>Overall Goal Progress</span>
                {isUnassessed ? (
                  <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    Not assessed
                  </span>
                ) : (
                  <span className="text-sm font-black text-blue-800">
                    {Math.round(dashboardData.metrics.career_readiness.score)}%
                  </span>
                )}
              </div>
            </div>

            {/* Deep Navy/Blue Progress Bar */}
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-900 h-full rounded-full transition-all duration-500"
                style={{
                  width: isUnassessed
                    ? '0%'
                    : `${Math.min(
                        100,
                        Math.max(4, Math.round(dashboardData.metrics.career_readiness.score))
                      )}%`,
                }}
              />
            </div>

            {/* 3 Metric Columns */}
            <div className="grid grid-cols-3 gap-4 pt-2 border-t border-slate-100 text-xs">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  SKILLS VERIFIED
                </span>
                <span className="text-sm font-bold text-slate-900 mt-0.5 block">
                  {dashboardData.metrics.skills_verified}{' '}
                  <span className="text-slate-400 font-normal">
                    / {dashboardData.metrics.total_role_skills}
                  </span>
                </span>
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  SKILL DEBT
                </span>
                <span className={`text-sm font-bold mt-0.5 block ${dashboardData.metrics.high_debt_count > 0 ? 'text-rose-600' : 'text-slate-700'}`}>
                  {isUnassessed
                    ? 'None'
                    : dashboardData.metrics.high_debt_count > 0
                    ? `${dashboardData.metrics.high_debt_count} Critical`
                    : `${dashboardData.metrics.active_skill_debt_count} Monitored`}
                </span>
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                  EVIDENCE
                </span>
                <span className="text-sm font-bold text-slate-900 mt-0.5 block">
                  {dashboardData.metrics.evidence_records_count}{' '}
                  <span className="text-slate-500 font-normal">Verified</span>
                </span>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 3. "WHAT SHOULD I DO NEXT?" (SECTION 15 MANDATE — CENTRAL ACTION CARD)    */}
          {/* ========================================================================= */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200/60 inline-flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                  WHAT SHOULD I DO NEXT? • RECOMMENDED ACTION
                </span>
              </div>
              {!isUnassessed && (
                <span className="text-xs font-semibold text-emerald-600">
                  Highest Skill Gap Priority
                </span>
              )}
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 tracking-tight">
                {isUnassessed
                  ? `Take the "${dashboardData.target_role_name}" Initial Diagnostic Assessment`
                  : dashboardData.next_best_proof?.title || 'Target Competency Verification'}
              </h3>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed max-w-4xl">
                {isUnassessed
                  ? `We'll assess your skills across the ${dashboardData.target_role_name} skill map to calculate your baseline Skill DNA and detect your skill gaps.`
                  : dashboardData.next_best_proof?.reason ||
                    `Targeted practical proof to address your largest competency gap and accelerate qualification toward ${dashboardData.target_role_name}.`}
              </p>
            </div>

            {/* Metric Strip */}
            <div className="flex items-center gap-3 text-xs text-slate-500 pt-1 flex-wrap">
              <span>
                Current:{' '}
                {isUnassessed ? (
                  <strong className="text-slate-500 font-medium">Not assessed</strong>
                ) : (
                  <strong className="text-rose-600">
                    {Math.round(dashboardData.next_best_proof?.current_skill_level || 0)}%
                  </strong>
                )}
              </span>
              <span>•</span>
              <span>
                Target:{' '}
                <strong className="text-slate-800">
                  {Math.round(dashboardData.next_best_proof?.required_skill_level || 85)}%
                </strong>
              </span>
              <span>•</span>
              <span>
                Career Impact: <strong className="text-slate-800">Critical</strong>
              </span>
              <span>•</span>
              <span>
                Est. Time:{' '}
                <strong className="text-slate-800">
                  {dashboardData.next_best_proof?.estimated_minutes || (isUnassessed ? 20 : 35)} min
                </strong>
              </span>
              <span>•</span>
              <NextProofReadiness
                userId={dashboardData.user_id || activeUserId || 1}
                skillId={dashboardData.next_best_proof?.skill_id || 1}
                skillName={dashboardData.next_best_proof?.skill_name || 'Core Competency'}
                compact={true}
              />
            </div>

            {/* Action Row */}
            <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100">
              <div className="flex items-center gap-3">
                {isUnassessed ? (
                  <button
                    onClick={() => router.push(`/assessments/goal/${dashboardData.target_role_id}`)}
                    className="px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>Start Initial Diagnostic Assessment</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => {
                        if (
                          dashboardData.next_best_proof?.action_type === 'LEARN' ||
                          dashboardData.next_best_proof?.action_type === 'PRACTICE'
                        ) {
                          router.push('/learn');
                        } else if (dashboardData.next_best_proof?.action_type === 'REASSESS') {
                          router.push(`/assessments/goal/${dashboardData.target_role_id}`);
                        } else if (dashboardData.next_best_proof?.action_type === 'PROJECT') {
                          router.push('/projects');
                        } else {
                          router.push('/learn');
                        }
                      }}
                      className="px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                    >
                      <span>
                        {dashboardData.next_best_proof?.action_type === 'LEARN'
                          ? `Learn: ${dashboardData.next_best_proof?.skill_name}`
                          : dashboardData.next_best_proof?.action_type === 'PRACTICE'
                          ? `Practice: ${dashboardData.next_best_proof?.skill_name}`
                          : dashboardData.next_best_proof?.action_type === 'REASSESS'
                          ? 'Retake Assessment'
                          : 'Enter Practice Lab'}
                      </span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>

                    <button
                      onClick={() => router.push(`/assessments/goal/${dashboardData.target_role_id}`)}
                      className="px-3 py-2 text-xs font-medium text-slate-700 bg-slate-50 hover:bg-slate-100 rounded-md transition-colors cursor-pointer border border-slate-200"
                    >
                      Retake Goal Diagnostic
                    </button>
                  </>
                )}

                <button
                  type="button"
                  onClick={() =>
                    openCoach(
                      isUnassessed
                        ? 'Why should I start with the diagnostic assessment?'
                        : `Why is ${dashboardData.next_best_proof?.skill_name || 'this recommendation'} my priority?`
                    )
                  }
                  className="text-xs text-slate-500 hover:text-slate-800 font-medium inline-flex items-center gap-1 cursor-pointer"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                  <span>Why this recommendation?</span>
                </button>
              </div>

              <span className="text-xs text-slate-400 font-medium">
                {isUnassessed
                  ? 'Baseline diagnostic required to generate roadmap.'
                  : `Target: ${dashboardData.target_role_name}`}
              </span>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* GOAL ACHIEVEMENT PREDICTION CARD (SECTION 14 MANDATE)                     */}
          {/* ========================================================================= */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-emerald-600" /> Goal Prediction
                </span>
                <span className="text-xs font-bold text-slate-800">Target Completion Estimate</span>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                {isUnassessed ? 'Awaiting Baseline' : 'ON TRACK'}
              </span>
            </div>

            <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
              {isUnassessed
                ? 'Complete your baseline diagnostic assessment to enable the goal completion prediction system.'
                : `At your current pace of learning (~8–10 hours/week), you are estimated to achieve job qualification for ${dashboardData.target_role_name} in approximately 8–12 weeks.`}
            </p>

            <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-1 border-t border-slate-100">
              <span>Measurable factors: Competency gap velocity • Verified evidence consistency</span>
              <span className="text-slate-300">•</span>
              <span className="text-slate-500 font-medium italic">Estimated prediction</span>
            </div>
          </div>


          {/* ========================================================================= */}
          {/* 4. TWO-COLUMN SPLIT: BIGGEST GAPS & IMMEDIATE ROADMAP                     */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Left Card: Biggest Career Gaps */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">Biggest Career Gaps</h3>
                    <p className="text-xs text-slate-500">
                      {isUnassessed
                        ? 'Role benchmark competency targets'
                        : 'Top 4 competencies to reach job qualification'}
                    </p>
                  </div>
                  <span className="text-xs font-mono text-slate-400">
                    {Math.min(4, dashboardData.skill_gap_heatmap.length)} Tracked
                  </span>
                </div>

                {isUnassessed ? (
                  <div className="pt-3 space-y-3">
                    <div className="p-3 bg-blue-50/60 border border-blue-100 rounded-lg flex items-center justify-between gap-3 text-xs">
                      <p className="text-slate-700 leading-relaxed">
                        Complete your diagnostic assessment to identify your highest-impact skill gaps.
                      </p>
                      <button
                        onClick={() => router.push('/assessments')}
                        className="px-3 py-1.5 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs shrink-0 cursor-pointer"
                      >
                        Start Diagnostic Assessment
                      </button>
                    </div>

                    <div className="space-y-3 pt-1">
                      {dashboardData.skill_gap_heatmap.slice(0, 4).map((item) => (
                        <div key={item.skill_id} className="space-y-1.5">
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-semibold text-slate-900">
                              {item.skill_name}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-slate-500 text-[11px]">
                                Target {Math.round(item.required_level)}%
                              </span>
                              <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                                Not assessed
                              </span>
                            </div>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div className="bg-slate-300 h-full rounded-full" style={{ width: '0%' }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 pt-3">
                    {dashboardData.skill_gap_heatmap.slice(0, 4).map((item) => {
                      const isCritical =
                        item.skill_debt_status === 'SKILL_DEBT' || item.status === 'critical';
                      return (
                        <div key={item.skill_id} className="space-y-1.5">
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-semibold text-slate-900">
                              {item.skill_name}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-slate-500 text-[11px]">
                                {Math.round(item.current_level)}% / {Math.round(item.required_level)}%
                              </span>
                              {isCritical && (
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
                                  Critical Gap
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                isCritical ? 'bg-rose-600' : 'bg-blue-600'
                              }`}
                              style={{ width: `${Math.min(100, Math.round(item.current_level))}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-slate-100 flex justify-end">
                <Link
                  href="/career-gap"
                  className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1"
                >
                  <span>View Full Gap Matrix</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* Right Card: Immediate Roadmap */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">Immediate Roadmap</h3>
                    <p className="text-xs text-slate-500">
                      {isUnassessed
                        ? 'Onboarding sequence to unlock personalized path'
                        : 'Adaptive sequence prioritized by ROI'}
                    </p>
                  </div>
                  <GitFork className="w-4 h-4 text-slate-400" />
                </div>

                {isUnassessed ? (
                  <div className="space-y-3 pt-3 text-xs">
                    {/* Step 1: Complete Diagnostic Assessment — Current */}
                    <div className="flex items-center justify-between bg-blue-50/60 -mx-2 px-2 py-2 rounded-md border border-blue-100">
                      <div className="flex items-center gap-2.5">
                        <div className="w-4 h-4 rounded-full bg-blue-800 flex items-center justify-center text-white shrink-0">
                          <span className="w-1.5 h-1.5 rounded-full bg-white" />
                        </div>
                        <span className="font-bold text-slate-900">1. Complete Diagnostic Assessment</span>
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-800 text-white">
                        Current Focus
                      </span>
                    </div>

                    {/* Step 2: Build Skill DNA — Upcoming */}
                    <div className="flex items-center justify-between px-0.5">
                      <div className="flex items-center gap-2.5">
                        <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                        <span className="text-slate-600">2. Build Skill DNA</span>
                      </div>
                      <span className="text-slate-400 text-[11px]">Upcoming</span>
                    </div>

                    {/* Step 3: Generate Personalized Roadmap — Upcoming */}
                    <div className="flex items-center justify-between px-0.5">
                      <div className="flex items-center gap-2.5">
                        <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                        <span className="text-slate-600">3. Generate Personalized Roadmap</span>
                      </div>
                      <span className="text-slate-400 text-[11px]">Upcoming</span>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3 pt-3 text-xs">
                    {dashboardData.roadmap_preview.slice(0, 5).map((step) => {
                      const isCompleted = step.status === 'COMPLETED';
                      const isCurrent = step.status === 'IN_PROGRESS' || step.status === 'RECOMMENDED';

                      if (isCompleted) {
                        return (
                          <div key={step.id} className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                              <span className="text-slate-500 line-through">{step.title}</span>
                            </div>
                            <span className="text-emerald-700 font-semibold text-[11px]">Passed</span>
                          </div>
                        );
                      }

                      if (isCurrent) {
                        return (
                          <div
                            key={step.id}
                            className="flex items-center justify-between bg-blue-50/60 -mx-2 px-2 py-1.5 rounded-md border border-blue-100"
                          >
                            <div className="flex items-center gap-2.5">
                              <div className="w-4 h-4 rounded-full bg-blue-800 flex items-center justify-center text-white shrink-0">
                                <span className="w-1.5 h-1.5 rounded-full bg-white" />
                              </div>
                              <span className="font-bold text-slate-900">{step.title}</span>
                            </div>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-800 text-white">
                              Current Focus
                            </span>
                          </div>
                        );
                      }

                      return (
                        <div key={step.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2.5">
                            <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                            <span className="text-slate-600">{step.title}</span>
                          </div>
                          <span className="text-slate-400 text-[11px]">
                            {step.status === 'BLOCKED' ? 'Queued' : 'Upcoming'}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="pt-2 border-t border-slate-100 flex justify-end">
                <Link
                  href="/roadmap"
                  className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1"
                >
                  <span>View Full Adaptive Roadmap</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 5. RECENT PROOF CARD                                                      */}
          {/* ========================================================================= */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Recent Proof</h3>
                <p className="text-xs text-slate-500">
                  Empirical evidence validating your skill claims
                </p>
              </div>
              <Link
                href="/skill-passport"
                className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1"
              >
                <span>View all {dashboardData.metrics.evidence_records_count}</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {isUnassessed || dashboardData.recent_evidence.length === 0 ? (
              <div className="py-6 px-4 bg-slate-50/50 border border-slate-100 rounded-lg text-center space-y-2">
                <p className="text-xs text-slate-500">
                  No verified evidence recorded yet. Complete your diagnostic assessment to baseline your skills.
                </p>
                <button
                  onClick={() => router.push('/assessments')}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md transition-colors cursor-pointer"
                >
                  <span>Start Diagnostic Assessment</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                {dashboardData.recent_evidence.slice(0, 3).map((ev) => (
                  <div
                    key={ev.id}
                    className="p-3 rounded-lg border border-slate-200 bg-slate-50/60 flex items-start justify-between gap-3 text-xs"
                  >
                    <div className="space-y-0.5 min-w-0">
                      <span className="font-bold text-slate-900 block truncate">
                        {ev.skill_name}
                      </span>
                      <span className="text-[11px] text-slate-500 block truncate">
                        {ev.source} • {ev.evidence_type}
                      </span>
                      <span className="text-[10px] text-slate-400 block pt-1">
                        Verified {ev.verified_date}
                      </span>
                    </div>
                    <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 shrink-0">
                      {ev.score}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* GOAL SWITCHER & CUSTOM GOAL MODAL (SECTION 1 MANDATE)                     */}
      {/* ========================================================================= */}
      {isGoalModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-800 flex items-center justify-center">
                  <GitFork className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Switch or Create Target Goal</h3>
                  <p className="text-xs text-slate-500">
                    Your Skill Map, assessments, and roadmap adapt automatically to your goal.
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsGoalModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
                disabled={isSwitchingGoal}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Error Banner */}
            {goalModalError && (
              <div className="mx-6 mt-4 p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
                <span>{goalModalError}</span>
              </div>
            )}

            {/* Mode Switcher Tabs */}
            <div className="px-6 pt-4 flex gap-2">
              <button
                type="button"
                onClick={() => setIsCustomMode(false)}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2 border ${
                  !isCustomMode
                    ? 'bg-blue-50 text-blue-900 border-blue-200'
                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                }`}
              >
                <Layers className="w-4 h-4" />
                <span>Predefined Goals</span>
              </button>
              <button
                type="button"
                onClick={() => setIsCustomMode(true)}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2 border ${
                  isCustomMode
                    ? 'bg-blue-50 text-blue-900 border-blue-200'
                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                }`}
              >
                <PlusCircle className="w-4 h-4" />
                <span>Custom Target Goal</span>
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-3 flex-1">
              {!isCustomMode ? (
                <div className="space-y-2.5">
                  <p className="text-xs text-slate-500 font-medium pb-1">
                    Select one of our structured career tracks:
                  </p>
                  {(dashboardData?.all_roles || []).map((role) => {
                    const isSelected = dashboardData?.target_role_id === role.id;
                    return (
                      <button
                        key={role.id}
                        type="button"
                        onClick={() => handleSelectGoal(role.id)}
                        disabled={isSwitchingGoal}
                        className={`w-full p-4 rounded-xl border text-left transition-all flex items-center justify-between gap-3 ${
                          isSelected
                            ? 'bg-blue-900 text-white border-blue-900 shadow-md ring-2 ring-blue-900/20'
                            : 'bg-white border-slate-200 hover:border-blue-300 hover:bg-slate-50/80 text-slate-900'
                        }`}
                      >
                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm tracking-tight">{role.name}</span>
                            {isSelected && (
                              <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-800 text-white border border-blue-700">
                                Current Active
                              </span>
                            )}
                          </div>
                          {role.description && (
                            <p
                              className={`text-xs truncate ${
                                isSelected ? 'text-blue-100' : 'text-slate-500'
                              }`}
                            >
                              {role.description}
                            </p>
                          )}
                        </div>

                        <div className="shrink-0">
                          {isSelected ? (
                            <Check className="w-5 h-5 text-white" />
                          ) : (
                            <ArrowRight className="w-4 h-4 text-slate-400" />
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-xs text-slate-500 leading-relaxed">
                    Define any custom technical role. SkillPath AI will synthesize a dedicated skill
                    map and diagnostic assessment for it.
                  </p>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-700 block">
                      Target Goal Name <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., DevOps Engineer, Cloud Architect, Security Engineer"
                      value={customGoalName}
                      onChange={(e) => setCustomGoalName(e.target.value)}
                      className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-700 block">
                      Description (Optional)
                    </label>
                    <input
                      type="text"
                      placeholder="e.g., Specializing in AWS infrastructure, containerization, and automated deployments."
                      value={customGoalDesc}
                      onChange={(e) => setCustomGoalDesc(e.target.value)}
                      className="w-full text-xs px-3.5 py-2.5 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-700 block">
                      Core Competencies / Skills (Optional, comma-separated)
                    </label>
                    <textarea
                      rows={3}
                      placeholder="e.g., Docker, Kubernetes, Terraform, Linux, CI/CD, AWS Architecture"
                      value={customGoalSkills}
                      onChange={(e) => setCustomGoalSkills(e.target.value)}
                      className="w-full text-xs px-3.5 py-2 rounded-lg border border-slate-200 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                    />
                    <p className="text-[11px] text-slate-400">
                      Leave blank to let the system generate default competencies automatically.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={handleCreateAndSelectCustomGoal}
                    disabled={isSwitchingGoal || !customGoalName.trim()}
                    className="w-full py-2.5 px-4 bg-blue-900 hover:bg-blue-800 disabled:opacity-50 text-white rounded-lg text-xs font-bold flex items-center justify-center gap-2 shadow-xs transition-colors cursor-pointer"
                  >
                    {isSwitchingGoal ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Creating and Switching Goal...</span>
                      </>
                    ) : (
                      <>
                        <PlusCircle className="w-4 h-4" />
                        <span>Create and Set as Target Goal</span>
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
              <span>Skill maps are stored dynamically in the system database.</span>
              <button
                type="button"
                onClick={() => setIsGoalModalOpen(false)}
                className="font-semibold text-slate-600 hover:text-slate-900 cursor-pointer"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}

