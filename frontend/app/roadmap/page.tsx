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
    rebuildRoadmap,
    isDemoMode,
  } = useLearner();

  const [isRebuilding, setIsRebuilding] = useState<boolean>(false);
  const [showDetails, setShowDetails] = useState<boolean>(true);
  const [history, setHistory] = useState<ApiRoadmapHistory[]>([]);

  const targetRoleName = isDemoMode
    ? 'Data Analyst'
    : activeUser?.target_role?.name || roadmap?.target_role_name || 'Data Analyst';

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
                v3.2 Adaptive Graph
              </span>
            </div>
            <p className="text-xs text-slate-500 italic mt-0.5">
              &ldquo;The learner doesn&apos;t follow the roadmap. The roadmap follows the learner.&rdquo;
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs font-semibold text-blue-900 bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-full shadow-2xs inline-flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />
              <span>Target: {targetRoleName} • 68% Career Readiness</span>
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
        {/* 2. ADAPTIVE RE-ROUTE BANNER (Matches Stitch Screenshot 4)                 */}
        {/* ========================================================================= */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
              <h3 className="text-sm font-bold text-slate-900">Why did my roadmap change?</h3>
              <span className="text-[10px] font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                • Adaptive Re-route - Yesterday at 16:42
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
                Based on recent query execution in the{' '}
                <strong className="text-slate-900">Retail Analytics Lab</strong>, the adaptive engine inserted a targeted remediation ({' '}
                <strong className="text-blue-700">SQL JOIN Rescue Practice</strong> ) before unlocking downstream Exploratory Data Analysis.
              </p>

              <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200 inline-flex items-center gap-1 shrink-0 self-start sm:self-auto">
                <Zap className="w-3 h-3 text-emerald-600" />
                <span>Saved ~6.2 hrs downstream rework</span>
              </span>
            </div>
          )}
        </div>

        {/* ========================================================================= */}
        {/* 3. 3-CARD METRIC STRIP (Matches Stitch Screenshot 4)                      */}
        {/* ========================================================================= */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
          {/* Card 1: Verified Evidence */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                VERIFIED EVIDENCE
              </span>
              <span className="text-lg font-black text-slate-900 mt-0.5 block">
                2 <span className="text-slate-400 font-normal text-xs">/ 10 Milestones</span>
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
                Relational Multi-Table
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
              <span className="text-sm font-bold text-rose-700 mt-0.5 block">
                Active Drill
              </span>
            </div>
            <div className="w-8 h-8 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 4. VERTICAL TIMELINE / ROADMAP FLOW (Matches Stitch Screenshot 4)         */}
        {/* ========================================================================= */}
        <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-3 sm:before:left-4 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-200">
          {/* STEP 01: Python Fundamentals (Completed) */}
          <div className="relative">
            <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0 ring-4 ring-slate-50">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  STEP 01 • FOUNDATION • COMPLETED MAY 12
                </span>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                  • Verified (Level 85)
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-900">Python Fundamentals</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Vectorized manipulation (Pandas &amp; NumPy), exploratory syntax, filtering algorithms, and deterministic data shaping routines.
              </p>
              <div className="flex items-center gap-4 pt-2 text-[11px] text-slate-400">
                <span>4 Projects Evaluated</span>
                <span>•</span>
                <span>100% Mastery Retention</span>
              </div>
            </div>
          </div>

          {/* STEP 02: SQL Query Foundations (Completed) */}
          <div className="relative">
            <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0 ring-4 ring-slate-50">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2">
              <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  STEP 02 • FOUNDATION • COMPLETED MAY 24
                </span>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                  • Verified (Level 76)
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-900">SQL Query Foundations</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Core SELECT queries, groupbys, filtering, CASE expressions, and aggregation logic across dimensional transactional schemata.
              </p>
              <div className="flex items-center gap-4 pt-2 text-[11px] text-slate-400">
                <span>28 Queries Executed</span>
                <span>•</span>
                <span>92% Execution Speed</span>
              </div>
            </div>
          </div>

          {/* STEP 03: SQL JOIN Rescue Practice (Active / Dynamically Inserted) */}
          <div className="relative">
            <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-md bg-blue-800 text-white flex items-center justify-center shrink-0 ring-4 ring-slate-50 shadow-xs">
              <Play className="w-3.5 h-3.5 fill-white" />
            </div>
            <div className="bg-white border-2 border-blue-600/80 rounded-xl p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                    • STEP 03 • DYNAMICALLY INSERTED
                  </span>
                  <span className="text-[10px] font-bold text-white bg-blue-800 px-2 py-0.5 rounded">
                    CURRENT FOCUS
                  </span>
                </div>
                <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <span>Est. 35 min</span>
                </span>
              </div>

              <div>
                <h3 className="text-lg font-bold text-slate-900">SQL JOIN Rescue Practice</h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  Targeted drill resolving relational multi-table JOIN gaps and Cartesian anomalies detected during live task execution. Re-calibrates self-joins, full outer joins, and complex NULL predicates.
                </p>
              </div>

              {/* Diagnostic Gap Progress Box */}
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-700">Diagnostic Gap Progress</span>
                  <span className="text-[11px] font-semibold text-slate-600">
                    Current: <strong className="text-rose-600">42%</strong> / Target: 75% accuracy
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-rose-600 h-full rounded-full" style={{ width: '42%' }} />
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-400 pt-0.5">
                  <span>Cartesian product mismatch in retail cohort queries</span>
                  <span>Threshold to unlock Step 04</span>
                </div>
              </div>

              <div className="pt-2 flex items-center gap-3">
                <button
                  onClick={() => router.push('/practice-lab')}
                  className="px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <span>Start Practice</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={() => router.push('/skill-debt')}
                  className="px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50 border border-slate-200 rounded-md transition-colors cursor-pointer"
                >
                  <span>View Diagnostic Gap</span>
                </button>
              </div>
            </div>
          </div>

          {/* STEP 04: Multi-Table Challenge Lab (Upcoming / Locked) */}
          <div className="relative">
            <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-full bg-white border border-slate-300 text-slate-500 font-mono text-[10px] font-bold flex items-center justify-center shrink-0 ring-4 ring-slate-50">
              04
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2 opacity-90">
              <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  STEP 04 • UPCOMING (UNLOCKS AFTER RESCUE)
                </span>
                <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <span>Est. 45 min</span>
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-800">Multi-Table Challenge Lab</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Complex relational datasets with missing foreign keys and dirty attributes. Exercises focus on resilient table coupling and windowed aggregate transforms.
              </p>
            </div>
          </div>

          {/* STEP 05: Retail Customer Analytics Lab (Upcoming) */}
          <div className="relative">
            <div className="absolute -left-6 sm:-left-8 top-3.5 w-6 h-6 rounded-full bg-white border border-slate-300 text-slate-500 font-mono text-[10px] font-bold flex items-center justify-center shrink-0 ring-4 ring-slate-50">
              05
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-2 opacity-80">
              <div className="flex items-center justify-between text-xs flex-wrap gap-2">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  STEP 05 • REAL-WORLD PROOF
                </span>
                <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                  <Clock className="w-3 h-3 text-slate-400" />
                  <span>Est. 1h 15m</span>
                </span>
              </div>
              <h3 className="text-base font-bold text-slate-800">Retail Customer Analytics Lab</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                End-to-end live transactions analysis and customer lifetime value pipeline under real-world schema conditions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
