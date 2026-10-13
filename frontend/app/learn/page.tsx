'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import {
  api,
  ApiLearningModuleSummary,
} from '../../services/api';
import {
  BookOpen,
  Lock,
  Unlock,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  Sparkles,
  RotateCw,
  Search,
  Filter,
  GraduationCap,
  Layers,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';

export default function LearningHubPage() {
  const router = useRouter();
  const { activeUserId, activeUser, isDemoMode, refreshUser } = useLearner();

  const [modules, setModules] = useState<ApiLearningModuleSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const targetRoleName =
    activeUser?.target_role?.name || 'Data Analyst';

  const loadModules = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getLearningModules(
        activeUserId || 1,
        activeUser?.target_role_id
      );
      setModules(data);
    } catch (err: any) {
      console.error('Failed to load learning modules:', err);
      setError(err?.message || 'Failed to load adaptive learning modules');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadModules();
  }, [activeUserId, activeUser?.target_role_id]);

  // Compute metrics
  const stats = useMemo(() => {
    const total = modules.length;
    const mastered = modules.filter((m) => m.status === 'MASTERED').length;
    const remediation = modules.filter((m) => m.status === 'REMEDIATION').length;
    const inProgress = modules.filter((m) =>
      ['LEARNING', 'PRACTICING', 'CHECK_PENDING', 'DEVELOPING'].includes(m.status)
    ).length;
    const available = modules.filter((m) => m.status === 'AVAILABLE').length;
    const locked = modules.filter((m) => m.is_locked || m.status === 'LOCKED').length;

    return { total, mastered, remediation, inProgress, available, locked };
  }, [modules]);

  // Next recommended action
  const nextRecommended = useMemo(() => {
    // 1. Prioritize remediation
    const rem = modules.find((m) => m.status === 'REMEDIATION');
    if (rem) return rem;
    // 2. Active in-progress
    const act = modules.find((m) =>
      ['PRACTICING', 'LEARNING', 'DEVELOPING', 'CHECK_PENDING'].includes(m.status)
    );
    if (act) return act;
    // 3. First available
    const avail = modules.find((m) => m.status === 'AVAILABLE');
    if (avail) return avail;
    // 4. First unlocked
    return modules.find((m) => !m.is_locked);
  }, [modules]);

  // Filtered modules
  const filteredModules = useMemo(() => {
    return modules.filter((m) => {
      // Filter by status
      if (statusFilter === 'REMEDIATION' && m.status !== 'REMEDIATION') return false;
      if (statusFilter === 'ACTIVE' && !['LEARNING', 'PRACTICING', 'CHECK_PENDING', 'DEVELOPING', 'AVAILABLE'].includes(m.status)) return false;
      if (statusFilter === 'MASTERED' && m.status !== 'MASTERED') return false;
      if (statusFilter === 'LOCKED' && !m.is_locked && m.status !== 'LOCKED') return false;

      // Filter by search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchTitle = m.title.toLowerCase().includes(q);
        const matchSkill = m.skill_name.toLowerCase().includes(q);
        const matchConcept = m.concept_name.toLowerCase().includes(q);
        if (!matchTitle && !matchSkill && !matchConcept) return false;
      }

      return true;
    });
  }, [modules, statusFilter, searchQuery]);

  const getStatusBadge = (module: ApiLearningModuleSummary) => {
    if (module.is_locked || module.status === 'LOCKED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
          <Lock className="w-3 h-3 text-slate-500" />
          Locked
        </span>
      );
    }
    if (module.status === 'REMEDIATION') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200 animate-pulse">
          <AlertTriangle className="w-3 h-3 text-rose-600" />
          Skill Debt Drill
        </span>
      );
    }
    if (module.status === 'MASTERED') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          Mastered
        </span>
      );
    }
    if (['LEARNING', 'PRACTICING', 'CHECK_PENDING', 'DEVELOPING'].includes(module.status)) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <TrendingUp className="w-3 h-3 text-blue-600" />
          In Progress
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold bg-sky-50 text-sky-700 border border-sky-200">
        <Unlock className="w-3 h-3 text-sky-600" />
        Available
      </span>
    );
  };

  return (
    <AppShell>
      <div className="max-w-6xl mx-auto space-y-6 pb-12">
        {/* Top Header */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-blue-700 mb-1">
                <GraduationCap className="w-4 h-4" />
                <span>Role-Correct Learning Path</span>
                <span className="text-slate-300">•</span>
                <span className="text-slate-600">{targetRoleName}</span>
              </div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                Adaptive Career Curriculum
              </h1>
              <p className="text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
                The learning path follows your demonstrated ability toward your target role. 
                Complete guided lessons, verify concepts through deterministic checks, and prove skills with real-world tasks to unlock downstream milestones.
              </p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
              <button
                onClick={loadModules}
                disabled={isLoading}
                className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg shadow-2xs flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <RotateCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Refresh Path</span>
              </button>
              <Link
                href="/roadmap"
                className="px-3.5 py-2 text-xs font-semibold text-white bg-blue-700 hover:bg-blue-800 rounded-lg shadow-2xs flex items-center gap-1.5 transition-colors"
              >
                <span>View Roadmap</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Metric Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-6 pt-6 border-t border-slate-100 text-xs">
            <div className="bg-slate-50/80 rounded-lg p-3 border border-slate-200/60">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Total Modules</span>
              <span className="text-xl font-black text-slate-900 mt-0.5 block">{stats.total}</span>
            </div>
            <div className="bg-emerald-50/70 rounded-lg p-3 border border-emerald-100">
              <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider block">Mastered</span>
              <span className="text-xl font-black text-emerald-800 mt-0.5 block">{stats.mastered}</span>
            </div>
            <div className="bg-rose-50/70 rounded-lg p-3 border border-rose-100">
              <span className="text-[10px] font-bold text-rose-700 uppercase tracking-wider block">Skill Debt Drills</span>
              <span className="text-xl font-black text-rose-800 mt-0.5 block">{stats.remediation}</span>
            </div>
            <div className="bg-blue-50/70 rounded-lg p-3 border border-blue-100">
              <span className="text-[10px] font-bold text-blue-700 uppercase tracking-wider block">Available</span>
              <span className="text-xl font-black text-blue-800 mt-0.5 block">{stats.available + stats.inProgress}</span>
            </div>
            <div className="bg-slate-50/80 rounded-lg p-3 border border-slate-200/60">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Locked</span>
              <span className="text-xl font-black text-slate-700 mt-0.5 block">{stats.locked}</span>
            </div>
          </div>
        </div>

        {/* Priority Next Action Banner */}
        {nextRecommended && (
          <div className={`rounded-xl p-5 border shadow-xs ${
            nextRecommended.status === 'REMEDIATION'
              ? 'bg-rose-50/80 border-rose-200'
              : 'bg-blue-50/70 border-blue-200'
          }`}>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                    nextRecommended.status === 'REMEDIATION'
                      ? 'bg-rose-700 text-white'
                      : 'bg-blue-800 text-white'
                  }`}>
                    {nextRecommended.status === 'REMEDIATION' ? 'URGENT RESCUE DRILL' : 'NEXT RECOMMENDED STEP'}
                  </span>
                  <span className="text-xs font-semibold text-slate-600">
                    {nextRecommended.skill_name}
                  </span>
                </div>
                <h2 className="text-lg font-bold text-slate-900">
                  {nextRecommended.title}
                </h2>
                <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
                  {nextRecommended.status === 'REMEDIATION'
                    ? 'Targeted remediation inserted to eliminate verified skill debt before progressing to downstream modeling and profiling.'
                    : `Core ${targetRoleName} benchmark milestone. Complete lessons, practice exercises, and formative checks to unlock dependent skills.`}
                </p>
              </div>

              <div className="shrink-0 flex items-center gap-3">
                <button
                  onClick={() => router.push(`/learn/${nextRecommended.slug}`)}
                  className={`px-4 py-2.5 text-xs font-bold rounded-lg shadow-2xs flex items-center gap-2 cursor-pointer transition-colors ${
                    nextRecommended.status === 'REMEDIATION'
                      ? 'bg-rose-700 hover:bg-rose-800 text-white'
                      : 'bg-blue-800 hover:bg-blue-900 text-white'
                  }`}
                >
                  <span>{nextRecommended.status === 'REMEDIATION' ? 'Start Rescue Learning' : 'Continue Learning'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          {/* Status Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
            {[
              { id: 'ALL', label: 'All Modules' },
              { id: 'REMEDIATION', label: 'Skill Debt' },
              { id: 'ACTIVE', label: 'Ready & In Progress' },
              { id: 'MASTERED', label: 'Mastered' },
              { id: 'LOCKED', label: 'Locked' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg whitespace-nowrap transition-colors cursor-pointer ${
                  statusFilter === tab.id
                    ? 'bg-blue-800 text-white shadow-2xs'
                    : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search concepts or skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>
        </div>

        {/* Module Cards Grid */}
        {isLoading ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-500">
            <RotateCw className="w-6 h-6 animate-spin mx-auto text-blue-600 mb-3" />
            <p className="text-sm font-medium">Evaluating prerequisites and building role-correct learning graph...</p>
          </div>
        ) : error ? (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-6 text-center text-rose-700">
            <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-rose-600" />
            <p className="text-sm font-bold">{error}</p>
            <button
              onClick={loadModules}
              className="mt-3 px-3 py-1.5 text-xs font-semibold bg-rose-700 text-white rounded-md hover:bg-rose-800"
            >
              Retry
            </button>
          </div>
        ) : filteredModules.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-xl p-12 text-center text-slate-500">
            <Layers className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <p className="text-sm font-bold text-slate-700">No learning modules found</p>
            <p className="text-xs text-slate-500 mt-1">Try adjusting your filter or search query.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredModules.map((module) => {
              const isLocked = module.is_locked || module.status === 'LOCKED';

              return (
                <div
                  key={module.id}
                  className={`bg-white border rounded-xl p-5 shadow-xs transition-all flex flex-col justify-between ${
                    module.status === 'REMEDIATION'
                      ? 'border-rose-200 ring-1 ring-rose-200'
                      : isLocked
                      ? 'border-slate-200 opacity-80'
                      : 'border-slate-200 hover:border-blue-400 hover:shadow-sm'
                  }`}
                >
                  <div className="space-y-3">
                    {/* Header line: Skill & Status */}
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {module.skill_name}
                      </span>
                      {getStatusBadge(module)}
                    </div>

                    {/* Title & Concept */}
                    <div>
                      <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-700">
                        {module.title}
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {module.concept_name}
                      </p>
                    </div>

                    {/* Meta info: Duration & Difficulty */}
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span className="inline-flex items-center gap-1 font-mono">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {module.estimated_minutes} min
                      </span>
                      <span>•</span>
                      <span className="text-[11px] font-semibold uppercase text-slate-600">
                        {module.difficulty}
                      </span>
                      {module.concept_check_score !== undefined && module.concept_check_score > 0 && (
                        <>
                          <span>•</span>
                          <span className="text-emerald-700 font-semibold">
                            Check: {module.concept_check_score}%
                          </span>
                        </>
                      )}
                    </div>

                    {/* Prerequisites */}
                    {(() => {
                      const prereqs = Array.isArray(module.prerequisite_concept_slugs)
                        ? module.prerequisite_concept_slugs
                        : typeof module.prerequisite_concept_slugs === 'string'
                        ? module.prerequisite_concept_slugs.split(',').map((s) => s.trim()).filter(Boolean)
                        : [];
                      if (prereqs.length === 0) return null;
                      return (
                        <div className="pt-2 border-t border-slate-100">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                            Prerequisites
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {prereqs.map((req) => (
                              <span
                                key={req}
                                className="text-[10px] font-medium bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded"
                              >
                                {req.replace(/-/g, ' ')}
                              </span>
                            ))}
                          </div>
                        </div>
                      );
                    })()}

                    {/* Lock reason message if locked */}
                    {isLocked && module.lock_reason && (
                      <div className="bg-slate-50 p-2.5 rounded-lg border border-slate-200 text-xs text-slate-600 flex items-start gap-2">
                        <Lock className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                        <span className="leading-relaxed">{module.lock_reason}</span>
                      </div>
                    )}
                  </div>

                  {/* Card Action footer */}
                  <div className="pt-4 mt-3 border-t border-slate-100 flex items-center justify-between">
                    {isLocked ? (
                      <button
                        disabled
                        className="w-full py-2 px-3 text-xs font-semibold text-slate-400 bg-slate-100 rounded-lg flex items-center justify-center gap-1.5 cursor-not-allowed"
                      >
                        <Lock className="w-3.5 h-3.5" />
                        <span>Prerequisites Required</span>
                      </button>
                    ) : (
                      <button
                        onClick={() => router.push(`/learn/${module.slug}`)}
                        className={`w-full py-2 px-3 text-xs font-bold rounded-lg shadow-2xs flex items-center justify-center gap-1.5 cursor-pointer transition-colors ${
                          module.status === 'REMEDIATION'
                            ? 'bg-rose-700 hover:bg-rose-800 text-white'
                            : module.status === 'MASTERED'
                            ? 'bg-slate-100 hover:bg-slate-200 text-slate-800'
                            : 'bg-blue-800 hover:bg-blue-900 text-white'
                        }`}
                      >
                        <span>
                          {module.status === 'REMEDIATION'
                            ? 'Start Rescue Practice'
                            : module.status === 'MASTERED'
                            ? 'Review Learning & Proof'
                            : 'Enter Learning Experience'}
                        </span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppShell>
  );
}
