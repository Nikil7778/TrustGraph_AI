'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  api,
  ApiDemoStateResponse,
  ApiDemoResetResponse,
} from '../services/api';
import { useLearner } from '../context/LearnerContext';
import {
  Sparkles,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Layers,
  ChevronDown,
  ChevronUp,
  Loader2,
  Check,
  ExternalLink,
} from 'lucide-react';

interface DemoPathComparisonProps {
  className?: string;
  defaultExpanded?: boolean;
}

export const DemoPathComparison: React.FC<DemoPathComparisonProps> = ({
  className = '',
  defaultExpanded = true,
}) => {
  const { activeUserId, refreshUser } = useLearner();
  const [demoState, setDemoState] = useState<ApiDemoStateResponse | null>(null);
  const [isExpanded, setIsExpanded] = useState<boolean>(defaultExpanded);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [resetSuccessMessage, setResetSuccessMessage] = useState<string | null>(null);

  const fetchState = async () => {
    try {
      const data = await api.getDemoState(activeUserId || 1);
      setDemoState(data);
    } catch (err) {
      console.warn('Could not load demo state from backend:', err);
    }
  };

  useEffect(() => {
    fetchState();
  }, [activeUserId]);

  const handleResetDemo = async () => {
    if (!confirm('Reset Alex Mercer to baseline state? This restores the initial SQL JOIN debt and roadmap remediation.')) {
      return;
    }
    setIsResetting(true);
    setResetSuccessMessage(null);
    try {
      const res: ApiDemoResetResponse = await api.resetDemo(activeUserId || 1);
      setResetSuccessMessage('Learner restored to initial state with active Skill Debt!');
      await refreshUser();
      await fetchState();
      setTimeout(() => setResetSuccessMessage(null), 3500);
    } catch (err: any) {
      alert('Failed to reset demo: ' + (err.message || 'Server error'));
    } finally {
      setIsResetting(false);
    }
  };

  const isImproved = demoState?.has_completed_proof || false;
  const currLevel = demoState?.sql_joins_snapshot.current_level || 55;
  const isHealthy = demoState?.sql_joins_snapshot.current_debt === 'HEALTHY' || isImproved;

  return (
    <div
      className={`bg-white border-2 ${
        isImproved ? 'border-emerald-300' : 'border-blue-200'
      } rounded-xl shadow-xs overflow-hidden transition-all ${className}`}
    >
      {/* Component Banner Header */}
      <div className="bg-slate-900 text-white p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 font-bold">
            <Sparkles className="w-5 h-5 text-amber-300" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm sm:text-base font-bold text-white">
                How Your Path Changed — Adaptive Learning Loop
              </h3>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                  isImproved
                    ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    : 'bg-amber-950 text-amber-300 border border-amber-800'
                }`}
              >
                {isImproved ? 'Evidence Verified' : 'Baseline State'}
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              The roadmap does not dictate the learner — the roadmap follows verified proof.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-auto">
          {/* Reset Demo Button */}
          <button
            type="button"
            disabled={isResetting}
            onClick={handleResetDemo}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-md border border-slate-700 transition-colors disabled:opacity-50 cursor-pointer"
            title="Reset Alex Mercer back to baseline"
          >
            {isResetting ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />
            ) : (
              <RotateCcw className="w-3.5 h-3.5 text-blue-400" />
            )}
            <span>{isResetting ? 'Resetting...' : 'Reset Demo'}</span>
          </button>

          {/* Toggle Accordion */}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-slate-400 hover:text-white rounded-md hover:bg-slate-800 transition-colors"
            aria-label="Toggle demo comparison view"
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Success Notification */}
      {resetSuccessMessage && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-2 text-xs font-semibold text-blue-800 flex items-center gap-2 animate-in fade-in">
          <Check className="w-4 h-4 text-blue-600" />
          <span>{resetSuccessMessage}</span>
        </div>
      )}

      {/* Expandable Comparison Content */}
      {isExpanded && (
        <div className="p-4 sm:p-6 space-y-5 bg-slate-50/50">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-stretch">
            {/* 1. BEFORE STATE */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Initial Baseline (Before)
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-50 text-rose-700 border border-rose-200 uppercase">
                  Skill Debt
                </span>
              </div>

              <div>
                <div className="flex items-baseline justify-between">
                  <span className="font-bold text-slate-900 text-sm">SQL JOINs</span>
                  <span className="font-mono text-base font-black text-rose-600">42%</span>
                </div>
                <span className="text-xs text-slate-500">Target Role Requirement: 80%</span>
              </div>

              <div className="p-2.5 rounded-lg bg-rose-50/60 border border-rose-200/80 text-xs text-rose-900 space-y-1">
                <div className="flex items-center gap-1 font-bold text-rose-800">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>HIGH Skill Debt Active</span>
                </div>
                <p className="text-[11px] text-rose-700/90 leading-tight">
                  Prior assessment exposure detected with low accuracy (42%). Requires targeted intervention.
                </p>
              </div>

              <div className="text-xs space-y-1 pt-1 border-t border-slate-100">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  Prescribed Dynamic Roadmap:
                </span>
                <p className="font-medium text-slate-700 text-[11px]">
                  SQL JOIN Rescue Practice ⚠ &rarr; Reassessment &rarr; Real-World Task &rarr;{' '}
                  <span className="text-slate-400">EDA (🔒 Blocked)</span>
                </p>
              </div>
            </div>

            {/* 2. THE TRANSFORMATION TRIGGER (Arrow / Action) */}
            <div className="bg-blue-50/60 p-4 rounded-xl border border-blue-200/80 flex flex-col justify-between space-y-3 text-center">
              <div>
                <span className="text-[11px] font-bold text-blue-800 uppercase tracking-wider block mb-1">
                  Verifiable Action Produced
                </span>
                <h4 className="text-sm font-bold text-slate-900">
                  {isImproved ? 'Workplace Query Completed!' : 'Awaiting Applied Proof'}
                </h4>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {isImproved
                    ? 'Learner submitted multi-table SQL query in the Industry Failure Lab, passing all 4 evaluation pillars.'
                    : 'Learner completes SQL JOIN Rescue Practice or E-Commerce Failure Lab sandbox query to produce real evidence.'}
                </p>
              </div>

              <div className="py-2 flex items-center justify-center gap-2">
                <div className="h-0.5 flex-1 bg-blue-300" />
                <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-xs">
                  <ArrowRight className="w-4 h-4" />
                </div>
                <div className="h-0.5 flex-1 bg-blue-300" />
              </div>

              <div>
                <Link
                  href="/practice-lab"
                  className="inline-flex items-center justify-center gap-1.5 w-full px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-xs transition-colors"
                >
                  <span>{isImproved ? 'Open Failure Lab' : 'Execute SQL Lab Task'}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>

            {/* 3. AFTER STATE */}
            <div
              className={`bg-white p-4 rounded-xl border ${
                isImproved ? 'border-emerald-300 ring-2 ring-emerald-400/20' : 'border-slate-200'
              } shadow-2xs space-y-3`}
            >
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Live Adaptive State (After)
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                    isImproved
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-slate-100 text-slate-600 border border-slate-200'
                  }`}
                >
                  {isImproved ? 'VERIFIED' : 'PENDING PROOF'}
                </span>
              </div>

              <div>
                <div className="flex items-baseline justify-between">
                  <span className="font-bold text-slate-900 text-sm">SQL JOINs</span>
                  <span
                    className={`font-mono text-base font-black ${
                      isImproved ? 'text-emerald-600' : 'text-slate-700'
                    }`}
                  >
                    {Math.round(currLevel)}%
                  </span>
                </div>
                <span className="text-xs text-slate-500">
                  {isImproved
                    ? 'Target Requirement (80%) Achieved'
                    : 'Currently below role requirement'}
                </span>
              </div>

              <div
                className={`p-2.5 rounded-lg text-xs space-y-1 ${
                  isImproved
                    ? 'bg-emerald-50/70 border border-emerald-200 text-emerald-900'
                    : 'bg-slate-100 text-slate-700'
                }`}
              >
                <div className="flex items-center gap-1 font-bold">
                  {isImproved ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span className="text-emerald-800">Skill Debt Cleared (HEALTHY)</span>
                    </>
                  ) : (
                    <span>Awaiting lab completion to clear debt</span>
                  )}
                </div>
                <p className="text-[11px] text-slate-600 leading-tight">
                  {isImproved
                    ? 'Evaluated across SQL correctness, data quality handling, and business KPI derivation.'
                    : 'Run and submit query in the Industry Failure Lab to observe live state shift.'}
                </p>
              </div>

              <div className="text-xs space-y-1 pt-1 border-t border-slate-100">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  Rebuilt Dynamic Pathway:
                </span>
                <p className="font-medium text-slate-700 text-[11px]">
                  {isImproved ? (
                    <>
                      SQL JOINs Verification ✓ &rarr;{' '}
                      <strong className="text-blue-700">EDA Core Lab (● Unlocked & Active)</strong> &rarr; Data Viz
                    </>
                  ) : (
                    'Waiting for proof to unblock downstream pathway'
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Quick Demo Step Navigation Links */}
          <div className="pt-3 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-2 text-xs">
            <span className="text-slate-500 font-medium">
              Demo Walkthrough Steps:
            </span>
            <div className="flex flex-wrap items-center gap-1.5">
              <Link
                href="/"
                className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 rounded border border-slate-200 font-semibold"
              >
                1. Dashboard
              </Link>
              <Link
                href="/career-gap"
                className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 rounded border border-slate-200 font-semibold"
              >
                2. Career Gap
              </Link>
              <Link
                href="/practice-lab"
                className="px-2.5 py-1 bg-white hover:bg-slate-100 text-blue-700 rounded border border-blue-200 font-bold"
              >
                3. Failure Lab
              </Link>
              <Link
                href="/roadmap"
                className="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 rounded border border-slate-200 font-semibold"
              >
                4. Dynamic Roadmap
              </Link>
              <Link
                href="/skill-passport"
                className="px-2.5 py-1 bg-white hover:bg-slate-100 text-emerald-700 rounded border border-emerald-200 font-semibold"
              >
                5. Skill Passport
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
