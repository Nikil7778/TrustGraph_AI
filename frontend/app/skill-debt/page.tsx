'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../components/AppShell';
import { useCoach } from '../../context/CoachContext';
import { api, ApiSkillDebt } from '../../services/api';
import {
  AlertTriangle,
  RotateCw,
  Sparkles,
  ArrowRight,
  Clock,
  Layers,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

export default function SkillDebtPage() {
  const router = useRouter();
  const { openCoach } = useCoach();
  const [skillDebts, setSkillDebts] = useState<ApiSkillDebt[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRecalculating, setIsRecalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSkillDebtData();
  }, []);

  const loadSkillDebtData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getSkillDebt(1);
      setSkillDebts(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load Skill Debt analysis from backend.';
      console.error('Failed to load skill debt:', err);
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRecalculate = async () => {
    setIsRecalculating(true);
    try {
      const updated = await api.recalculateSkillDebt(1);
      setSkillDebts(updated);
    } catch (err: unknown) {
      console.error('Failed to recalculate Skill Debt:', err);
      setError('Failed to trigger Skill Debt recalculation.');
    } finally {
      setIsRecalculating(false);
    }
  };

  // Identify the dominant primary high-priority debt item (SQL JOINs)
  const primaryDebt =
    skillDebts.find((d) => d.severity === 'HIGH' || d.debt_status === 'SKILL_DEBT') ||
    skillDebts[0] ||
    null;

  // Secondary items
  const otherDebts = skillDebts.filter(
    (d) => !primaryDebt || d.skill_id !== primaryDebt.skill_id
  );

  return (
    <AppShell>
      <div className="space-y-5 max-w-6xl mx-auto">
        {/* ========================================================================= */}
        {/* 1. HEADER (Matches Stitch Screenshot 2)                                   */}
        {/* ========================================================================= */}
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-rose-600 font-bold uppercase tracking-wider text-[11px]">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-600 animate-pulse" />
            <span>ACTIVE VERIFICATION GAP</span>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Skill Debt</h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Skills you&apos;ve encountered or completed, but cannot reliably demonstrate under production conditions.
              </p>
            </div>
            <button
              onClick={handleRecalculate}
              disabled={isRecalculating}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 bg-white hover:bg-slate-50 border border-slate-200 rounded-md transition-colors self-start sm:self-auto cursor-pointer"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isRecalculating ? 'animate-spin text-blue-600' : ''}`} />
              <span>{isRecalculating ? 'Re-evaluating...' : 'Recalculate'}</span>
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* ========================================================================= */}
        {/* 2. CLASSIFICATION BAR (Matches Stitch Screenshot 2)                       */}
        {/* ========================================================================= */}
        <div className="bg-white border border-slate-200 rounded-xl px-4 py-2.5 shadow-xs text-xs flex flex-wrap items-center gap-3 text-slate-600">
          <span className="font-bold text-slate-700 uppercase tracking-wider text-[10px]">
            CLASSIFICATION:
          </span>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-slate-400" />
            <span>Missing (never studied)</span>
          </div>
          <span className="text-slate-300">•</span>
          <div className="flex items-center gap-1.5 text-rose-700 font-medium">
            <span className="w-2 h-2 rounded-full bg-rose-600" />
            <span>Skill Debt (studied, but weak live proof)</span>
          </div>
          <span className="text-slate-300">•</span>
          <div className="flex items-center gap-1.5 text-emerald-700 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-600" />
            <span>Healthy (demonstrated &amp; verified)</span>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 3. DOMINANT PRIMARY SKILL DEBT CARD (Matches Stitch Screenshot 2)         */}
        {/* ========================================================================= */}
        {primaryDebt && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-5">
            {/* Top row with Title and Right Metric Callout Box */}
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
              <div>
                <span className="text-[10px] font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200 inline-flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-rose-600" />
                  HIGH PRIORITY DEBT
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-2 tracking-tight">
                  {primaryDebt.skill_name} &amp; Multi-Table Logic
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Core prerequisite for Target Vector: Data Analyst
                </p>
              </div>

              {/* Top-Right Metric Callout Box */}
              <div className="bg-slate-50/70 border border-slate-200 rounded-lg p-3 sm:text-right shrink-0 min-w-[150px]">
                <div className="flex items-baseline sm:justify-end gap-1">
                  <span className="text-2xl font-black text-rose-600">
                    {Math.round(primaryDebt.current_skill_level)}%
                  </span>
                  <span className="text-xs font-semibold text-slate-400">
                    / {Math.round(primaryDebt.role_requirement)}% target
                  </span>
                </div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mt-0.5">
                  CURRENT PRACTICAL PROOF
                </span>
              </div>
            </div>

            {/* Explanation box with red left accent border */}
            <div className="border-l-4 border-rose-500 bg-blue-50/40 p-3.5 rounded-r-lg text-xs text-slate-700 leading-relaxed font-normal">
              You have demonstrated SQL fundamentals (76%), but recent real-world scenario tests revealed query failures on complex JOINs.
            </div>

            {/* Transfer Gap Analysis Side-by-Side Cards */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-900">Transfer Gap Analysis</span>
                <span className="font-semibold text-rose-600 text-[11px]">
                  -42 pt execution divergence
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Academic Quiz Card */}
                <div className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-900">
                    <span>Academic Quiz</span>
                    <span>84%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-blue-900 h-full rounded-full" style={{ width: '84%' }} />
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Validated theoretical syntax recall
                  </p>
                </div>

                {/* Practical Code Execution Card */}
                <div className="p-3.5 rounded-lg border border-rose-200 bg-rose-50/20 space-y-2">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span className="text-rose-900">Practical Code Execution</span>
                    <span className="text-rose-600 font-extrabold">42%</span>
                  </div>
                  <div className="w-full bg-rose-100 rounded-full h-1.5 overflow-hidden">
                    <div className="bg-rose-600 h-full rounded-full" style={{ width: '42%' }} />
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Cartesian join timeout under messy data conditions
                  </p>
                </div>
              </div>
            </div>

            {/* Bottom Action Row */}
            <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-xs text-slate-600 font-medium">
                <Sparkles className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Recommended: SQL JOIN Rescue Practice (5 scenarios • 25 mins)</span>
              </div>

              <button
                onClick={() => router.push('/practice-lab')}
                className="px-5 py-2.5 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center justify-center gap-1.5 cursor-pointer self-start sm:self-auto"
              >
                <span>Prove This Skill Now</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* 4. OTHER SKILLS NEEDING REFRESH (Matches Stitch Screenshot 2)              */}
        {/* ========================================================================= */}
        <div className="space-y-3 pt-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">
              Other Skills Needing Refresh
            </h3>
            <span className="text-xs font-mono text-slate-400">
              {otherDebts.length} items monitored
            </span>
          </div>

          <div className="space-y-3">
            {otherDebts.slice(0, 3).map((item) => (
              <div
                key={item.skill_id}
                className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-slate-400 shrink-0" />
                    <span className="font-bold text-slate-900 text-sm">{item.skill_name}</span>
                    <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                      {Math.round(item.current_skill_level)}% Proof
                    </span>
                  </div>
                  <p className="text-slate-500 text-xs">
                    {item.reason || `Recency decay detected for ${item.skill_name}`}
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => openCoach(`How can I refresh ${item.skill_name}?`)}
                    className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 border border-slate-200 rounded-md transition-colors cursor-pointer"
                  >
                    Ask Coach
                  </button>
                  <Link
                    href="/assessments"
                    className="px-3 py-1.5 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md transition-colors flex items-center gap-1"
                  >
                    <span>Refresh Assessment</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
