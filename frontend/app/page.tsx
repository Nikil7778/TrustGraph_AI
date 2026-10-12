'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AppShell } from '../components/AppShell';
import { useLearner } from '../context/LearnerContext';
import { useCoach } from '../context/CoachContext';
import { api, ApiDashboardResponse } from '../services/api';
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
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { activeUserId } = useLearner();
  const { openCoach } = useCoach();

  const [dashboardData, setDashboardData] = useState<ApiDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

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
          {/* 1. WELCOME HEADER (Matches Stitch Screenshot 1)                           */}
          {/* ========================================================================= */}
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
              Welcome back, {dashboardData.learner_name.split(' ')[0]}
            </h1>
            <p className="text-sm text-slate-500 mt-0.5">
              What should you work on next to reach job-readiness?
            </p>
          </div>

          {/* ========================================================================= */}
          {/* 2. TARGET ROLE & CAREER READINESS HERO CARD (Matches Stitch Screenshot 1) */}
          {/* ========================================================================= */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  TARGET ROLE
                </span>
                <span className="text-sm font-bold text-slate-900">
                  {dashboardData.target_role_name}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <span>Aggregate Career Readiness</span>
                <span className="text-sm font-black text-blue-800">
                  {Math.round(dashboardData.metrics.career_readiness.score)}%
                </span>
              </div>
            </div>

            {/* Deep Navy/Blue Progress Bar */}
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-900 h-full rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(
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
                <span className="text-sm font-bold text-rose-600 mt-0.5 block">
                  {dashboardData.metrics.high_debt_count > 0
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
          {/* 3. NEXT-BEST-PROOF CARD (Matches Stitch Screenshot 1)                     */}
          {/* ========================================================================= */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200/60 inline-flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
                  NEXT-BEST-PROOF • RECOMMENDED
                </span>
              </div>
              <span className="text-xs font-semibold text-emerald-600">
                +8% Readiness Boost
              </span>
            </div>

            <div>
              <h3 className="text-lg font-bold text-slate-900 tracking-tight">
                {dashboardData.next_best_proof?.title || 'SQL JOIN Rescue Practice'}
              </h3>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed max-w-4xl">
                Your SQL foundation is strong (76%), but multi-table query performance is currently limiting your readiness. Resolving this unlocks downstream Exploratory Data Analysis.
              </p>
            </div>

            {/* Metric Strip */}
            <div className="flex items-center gap-3 text-xs text-slate-500 pt-1 flex-wrap">
              <span>
                Current:{' '}
                <strong className="text-rose-600">
                  {Math.round(dashboardData.next_best_proof?.current_skill_level || 42)}%
                </strong>
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
                Career Impact: <strong className="text-slate-800">High</strong>
              </span>
              <span>•</span>
              <span>
                Est. Time:{' '}
                <strong className="text-slate-800">
                  {dashboardData.next_best_proof?.estimated_minutes || 35} min
                </strong>
              </span>
            </div>

            {/* Action Row */}
            <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    if (dashboardData.next_best_proof?.action_type === 'PRACTICE') {
                      router.push('/practice-lab');
                    } else if (dashboardData.next_best_proof?.action_type === 'REASSESS') {
                      router.push('/assessments');
                    } else {
                      router.push('/practice-lab');
                    }
                  }}
                  className="px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <span>Start Practice</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>

                <button
                  type="button"
                  onClick={() => openCoach('Why is SQL JOINs my priority?')}
                  className="text-xs text-slate-500 hover:text-slate-800 font-medium inline-flex items-center gap-1 cursor-pointer"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                  <span>Why this recommendation?</span>
                </button>
              </div>

              <span className="text-xs text-slate-400 font-medium">
                Pre-requisite: Database Fundamentals (Passed)
              </span>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* 4. TWO-COLUMN SPLIT: BIGGEST GAPS & IMMEDIATE ROADMAP (Matches Screenshot) */}
          {/* ========================================================================= */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Left Card: Biggest Career Gaps */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">Biggest Career Gaps</h3>
                    <p className="text-xs text-slate-500">
                      Top 4 competencies to reach job qualification
                    </p>
                  </div>
                  <span className="text-xs font-mono text-slate-400">4 Tracked</span>
                </div>

                <div className="space-y-4 pt-3">
                  {/* Row 1: SQL JOINs & Aggregations (Critical Gap) */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-900">
                        SQL JOINs & Aggregations
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-slate-500 text-[11px]">42% / 85%</span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200">
                          Critical Gap
                        </span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-rose-600 h-full rounded-full" style={{ width: '42%' }} />
                    </div>
                  </div>

                  {/* Row 2: Power BI & DAX */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-900">
                        Power BI & DAX
                      </span>
                      <span className="font-mono text-slate-500 text-[11px]">38% / 75%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-blue-600 h-full rounded-full" style={{ width: '38%' }} />
                    </div>
                  </div>

                  {/* Row 3: Exploratory Data Analysis (EDA) */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-900">
                        Exploratory Data Analysis (EDA)
                      </span>
                      <span className="font-mono text-slate-500 text-[11px]">65% / 80%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-blue-600 h-full rounded-full" style={{ width: '65%' }} />
                    </div>
                  </div>

                  {/* Row 4: SQL Query Foundations */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-900">
                        SQL Query Foundations
                      </span>
                      <span className="font-mono text-slate-500 text-[11px]">76% / 85%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div className="bg-blue-600 h-full rounded-full" style={{ width: '76%' }} />
                    </div>
                  </div>
                </div>
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
                      Adaptive sequence prioritized by ROI
                    </p>
                  </div>
                  <GitFork className="w-4 h-4 text-slate-400" />
                </div>

                <div className="space-y-3 pt-3 text-xs">
                  {/* Step 1: Python Core - Passed */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span className="text-slate-500 line-through">Python Core</span>
                    </div>
                    <span className="text-emerald-700 font-semibold text-[11px]">Passed (85%)</span>
                  </div>

                  {/* Step 2: SQL Basics - Passed */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span className="text-slate-500 line-through">SQL Basics</span>
                    </div>
                    <span className="text-emerald-700 font-semibold text-[11px]">Passed (76%)</span>
                  </div>

                  {/* Step 3: SQL JOIN Rescue - Current Focus */}
                  <div className="flex items-center justify-between bg-blue-50/60 -mx-2 px-2 py-1.5 rounded-md border border-blue-100">
                    <div className="flex items-center gap-2.5">
                      <div className="w-4 h-4 rounded-full bg-blue-800 flex items-center justify-center text-white shrink-0">
                        <span className="w-1.5 h-1.5 rounded-full bg-white" />
                      </div>
                      <span className="font-bold text-slate-900">SQL JOIN Rescue</span>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-800 text-white">
                      Current Focus
                    </span>
                  </div>

                  {/* Step 4: Exploratory Data Analysis - Upcoming */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                      <span className="text-slate-600">Exploratory Data Analysis</span>
                    </div>
                    <span className="text-slate-400 text-[11px]">Upcoming</span>
                  </div>

                  {/* Step 5: Data Visualization - Queued */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="w-4 h-4 rounded-full border border-slate-300 shrink-0" />
                      <span className="text-slate-600">Data Visualization</span>
                    </div>
                    <span className="text-slate-400 text-[11px]">Queued</span>
                  </div>
                </div>
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
          {/* 5. RECENT PROOF CARD (Matches Stitch Screenshot 1)                        */}
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
                <span>View all {dashboardData.metrics.evidence_records_count || 14}</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

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
          </div>
        </div>
      )}
    </AppShell>
  );
}
