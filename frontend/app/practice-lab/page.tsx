'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import { useCoach } from '../../context/CoachContext';
import {
  api,
  ApiIndustryLab,
  ApiIndustryLabTablePreview,
  ApiIndustryLabSubmitResponse,
  ApiIndustryLabAttempt,
  ApiAIHintResponse,
  ApiAIExplainMistakeResponse,
  ApiAIInterviewQuestionItem,
  ApiAILearningExplanationResponse,
} from '../../services/api';
import {
  Terminal,
  Play,
  CheckCircle2,
  AlertTriangle,
  Database,
  Table as TableIcon,
  ShieldAlert,
  Clock,
  Sparkles,
  ArrowRight,
  RotateCcw,
  Code2,
  FileCode,
  Layers,
  ChevronRight,
  TrendingUp,
  X,
  Loader2,
  Check,
} from 'lucide-react';

const CANONICAL_STARTER_SQL = `-- E-Commerce Customer Retention & Returns Analytics
-- Objective: Calculate segment-level gross revenue, refunds, net revenue, and return rate (%)
-- Critical: Use LEFT JOIN to retain orders with 0 returns & filter COMPLETED orders!

SELECT
    c.segment,
    COUNT(DISTINCT o.id) AS total_orders,
    ROUND(SUM(o.total_amount), 2) AS gross_revenue,
    ROUND(COALESCE(SUM(r.refund_amount), 0), 2) AS total_refunds,
    ROUND(SUM(o.total_amount) - COALESCE(SUM(r.refund_amount), 0), 2) AS net_revenue,
    ROUND((COUNT(DISTINCT r.id) * 100.0) / COUNT(DISTINCT o.id), 2) AS return_rate_pct
FROM lab_retail_customers c
JOIN lab_retail_orders o ON c.id = o.customer_id
LEFT JOIN lab_retail_returns r ON o.id = r.order_id
WHERE o.payment_status = 'COMPLETED'
GROUP BY c.segment
ORDER BY net_revenue DESC;`;

const CANONICAL_RATIONALE =
  'Enterprise segment generates the largest net revenue ($8,142) despite refunds. Mid-Market exhibits the highest return rate percentage (33.33%), which poses margin compression risk. SMB volume remains steady with low refund impact.';

export default function PracticeLabPage() {
  const { activeUserId, nextBestProof, refreshUser } = useLearner();
  const { openCoach } = useCoach();

  // Mode tab: 'lab' (Phase 10 Interactive Sandbox) vs 'challenges' (Scenario list)
  const [activeTab, setActiveTab] = useState<'lab' | 'challenges'>('lab');

  // Lab Data State
  const [lab, setLab] = useState<ApiIndustryLab | null>(null);
  const [previews, setPreviews] = useState<ApiIndustryLabTablePreview[]>([]);
  const [activeTableIndex, setActiveTableIndex] = useState<number>(0);
  const [attempts, setAttempts] = useState<ApiIndustryLabAttempt[]>([]);
  const [isLoadingLab, setIsLoadingLab] = useState<boolean>(true);

  // SQL Editor State
  const [queryCode, setQueryCode] = useState<string>(CANONICAL_STARTER_SQL);
  const [businessExplanation, setBusinessExplanation] = useState<string>(CANONICAL_RATIONALE);

  // Execution & Submission State
  const [isRunningQuery, setIsRunningQuery] = useState<boolean>(false);
  const [queryResult, setQueryResult] = useState<{
    success: boolean;
    columns: string[];
    rows: Record<string, any>[];
    row_count: number;
    execution_time_ms: number;
    error_message?: string | null;
  } | null>(null);

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [evalResult, setEvalResult] = useState<ApiIndustryLabSubmitResponse | null>(null);
  const [showResultModal, setShowResultModal] = useState<boolean>(false);

  // Phase 11 — AI Hint State
  const [hintLevel, setHintLevel] = useState<number>(1);
  const [currentHint, setCurrentHint] = useState<ApiAIHintResponse | null>(null);
  const [isFetchingHint, setIsFetchingHint] = useState<boolean>(false);

  // Phase 11 — AI Mistake Explanation State
  const [mistakeExplanation, setMistakeExplanation] = useState<ApiAIExplainMistakeResponse | null>(null);
  const [isExplainingMistake, setIsExplainingMistake] = useState<boolean>(false);

  // Phase 11 — AI Interview Prep & Concept Deep-Dive State
  const [interviewQuestions, setInterviewQuestions] = useState<ApiAIInterviewQuestionItem[]>([]);
  const [showInterviewModal, setShowInterviewModal] = useState<boolean>(false);
  const [isFetchingInterview, setIsFetchingInterview] = useState<boolean>(false);

  const [conceptExplanation, setConceptExplanation] = useState<ApiAILearningExplanationResponse | null>(null);
  const [showConceptModal, setShowConceptModal] = useState<boolean>(false);
  const [isFetchingConcept, setIsFetchingConcept] = useState<boolean>(false);

  // Handle Fetch AI Hint (Progressive Levels 1 -> 2 -> 3)
  const handleGetAIHint = async () => {
    setIsFetchingHint(true);
    try {
      const res = await api.getAIHint({
        task_title: lab?.title || 'E-Commerce Customer Retention & Returns Analytics',
        skill_name: 'SQL JOINs',
        context_description: 'Calculate segment-level gross revenue, refunds, net revenue, and return rate (%)',
        hint_level: hintLevel,
        learner_query: queryCode,
      });
      setCurrentHint(res);
      // Advance to next progressive level (up to 3)
      setHintLevel((prev) => (prev < 3 ? prev + 1 : 1));
    } catch (err) {
      console.error('Failed to fetch AI hint:', err);
    } finally {
      setIsFetchingHint(false);
    }
  };

  // Handle Explain Mistake with AI Coach
  const handleExplainMistake = async () => {
    if (!evalResult) return;
    setIsExplainingMistake(true);
    try {
      const res = await api.explainMistake({
        skill_name: 'SQL JOINs',
        task_or_question: lab?.title || 'E-Commerce Returns Analytics',
        learner_answer: queryCode,
        correct_answer_or_result: 'LEFT JOIN returns on orders with COALESCE and payment_status = COMPLETED',
        deterministic_evaluation: evalResult.diagnostic_failures?.join('; ') || evalResult.feedback,
        target_role: 'Data Analyst',
      });
      setMistakeExplanation(res);
    } catch (err) {
      console.error('Failed to explain mistake:', err);
    } finally {
      setIsExplainingMistake(false);
    }
  };

  // Handle Fetch Interview Prep Kit
  const handleFetchInterviewPrep = async () => {
    setShowInterviewModal(true);
    if (interviewQuestions.length > 0) return;
    setIsFetchingInterview(true);
    try {
      const res = await api.getInterviewQuestions({
        skill_name: 'SQL JOINs',
        target_role: 'Data Analyst',
      });
      setInterviewQuestions(res.questions);
    } catch (err) {
      console.error('Failed to fetch interview questions:', err);
    } finally {
      setIsFetchingInterview(false);
    }
  };

  // Handle Fetch Concept Deep-Dive
  const handleFetchConceptDeepDive = async () => {
    setShowConceptModal(true);
    if (conceptExplanation) return;
    setIsFetchingConcept(true);
    try {
      const res = await api.getLearningExplanation({
        skill_name: 'SQL JOINs',
        target_role: 'Data Analyst',
        specific_topic: 'LEFT JOIN vs INNER JOIN Pitfalls',
      });
      setConceptExplanation(res);
    } catch (err) {
      console.error('Failed to fetch concept deep-dive:', err);
    } finally {
      setIsFetchingConcept(false);
    }
  };

  // Load Lab, Previews, and Attempts on mount
  useEffect(() => {
    async function loadLabData() {
      setIsLoadingLab(true);
      try {
        const labData = await api.getIndustryLab('retail-returns-analytics');
        setLab(labData);

        const previewData = await api.getIndustryLabPreview('retail-returns-analytics');
        setPreviews(previewData);

        if (activeUserId) {
          const userAttempts = await api.getIndustryLabAttempts('retail-returns-analytics', activeUserId);
          setAttempts(userAttempts);
        }
      } catch (err) {
        console.warn('Could not load industry lab from backend API:', err);
      } finally {
        setIsLoadingLab(false);
      }
    }
    loadLabData();
  }, [activeUserId]);

  // Run Query in Sandbox
  const handleRunSandboxQuery = async () => {
    setIsRunningQuery(true);
    try {
      const res = await api.runIndustryLabQuery('retail-returns-analytics', queryCode);
      setQueryResult(res);
    } catch (err: any) {
      setQueryResult({
        success: false,
        columns: [],
        rows: [],
        row_count: 0,
        execution_time_ms: 0,
        error_message: err.message || 'Execution failed. Check backend connection.',
      });
    } finally {
      setIsRunningQuery(false);
    }
  };

  // Submit Final Solution for 4-Pillar Evaluation
  const handleSubmitEvaluation = async () => {
    setIsSubmitting(true);
    try {
      const res = await api.submitIndustryLabAttempt('retail-returns-analytics', {
        user_id: activeUserId || 1,
        query: queryCode,
        submitted_answer: businessExplanation,
        evidence_type: 'REAL_WORLD_TASK',
      });
      setEvalResult(res);
      setShowResultModal(true);

      // Refresh attempts & learner state (Skill DNA & Roadmap)
      if (activeUserId) {
        const updatedAttempts = await api.getIndustryLabAttempts('retail-returns-analytics', activeUserId);
        setAttempts(updatedAttempts);
        await refreshUser();
      }
    } catch (err: any) {
      console.error('Submission failed:', err);
      alert('Failed to submit evaluation: ' + (err.message || 'Server error'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const activePreview = previews[activeTableIndex] || null;

  return (
    <AppShell>
      <div className="space-y-6 pb-12">
        {/* Top Header Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs shrink-0">
              <Terminal className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-bold text-slate-900">
                  Industry Practical Lab & Sandbox
                </h1>
                <span className="text-[10px] font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Phase 10 Engine
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Live SQLite sandbox, real-world retail schemas, and automated 4-pillar evidence evaluation.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto flex-wrap">
            <button
              type="button"
              onClick={() => openCoach('Help me with SQL JOINs in the practice lab')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-xs rounded-lg border border-blue-200 transition-colors cursor-pointer"
              title="Ask Career Coach for help with this practice task"
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Ask Coach</span>
            </button>
            {nextBestProof && (
              <span className="text-xs font-semibold text-rose-700 bg-rose-50 px-3 py-1.5 rounded-lg border border-rose-200 flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-rose-600" />
                Active Focus: {nextBestProof.skill_name} ({nextBestProof.action_type_label})
              </span>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 gap-2 text-sm font-semibold">
          <button
            onClick={() => setActiveTab('lab')}
            className={`pb-3 px-4 flex items-center gap-2 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'lab'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            Interactive Industry Sandbox (Phase 10)
          </button>
          <button
            onClick={() => setActiveTab('challenges')}
            className={`pb-3 px-4 flex items-center gap-2 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'challenges'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <Layers className="w-4 h-4" />
            Skill Debt Rescue Tasks
          </button>
        </div>

        {activeTab === 'lab' ? (
          /* Interactive Industry Lab Sandbox (Phase 10) */
          <div className="space-y-6">
            {/* Lab Scenario Overview Card */}
            <div className="bg-white border border-slate-200 text-slate-900 rounded-xl p-5 shadow-xs space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                      Live Business Challenge
                    </span>
                    <span className="text-xs text-slate-300">•</span>
                    <span className="text-xs text-slate-500 font-medium">
                      Target Role: <strong className="text-slate-800">Data Analyst</strong>
                    </span>
                    <span className="text-xs text-slate-300">•</span>
                    <span className="text-xs text-slate-500 font-medium">
                      Primary Skill: <strong className="text-slate-800">SQL JOINs</strong>
                    </span>
                  </div>
                  <h2 className="text-lg font-bold text-slate-900">
                    {lab?.title || 'E-Commerce Customer Retention & Returns Analytics'}
                  </h2>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs bg-slate-100 border border-slate-200 text-slate-700 px-3 py-1 rounded-full flex items-center gap-1.5 font-medium">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    45 mins
                  </span>
                  <span className="text-xs bg-indigo-50 border border-indigo-200 text-indigo-700 px-3 py-1 rounded-full font-medium">
                    Intermediate
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed max-w-4xl">
                {lab?.business_context ||
                  'The Executive VP of E-Commerce has observed an escalation in customer refund requests and wants a segment-level breakdown of Gross Revenue, Total Refunds, Net Realized Revenue, and Return Rate (%). Because orders can have 0 returns, an INNER JOIN excludes non-returned orders, resulting in heavily biased metrics. Write clean queries using LEFT JOINs, NULL handling, and status filtering to produce verifiable executive KPIs.'}
              </p>

              {/* Data Quality Pitfall Warning */}
              <div className="bg-amber-50/70 border border-amber-200/80 rounded-lg p-3.5 flex items-start gap-3 text-xs text-amber-900">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <span className="font-bold text-amber-950">Data Engineering Quality Trap:</span>
                  <p className="text-amber-900/90 leading-normal">
                    1) Orders table contains <code className="bg-amber-100 px-1 py-0.5 rounded text-amber-900 font-mono text-[11px]">CANCELLED</code> and <code className="bg-amber-100 px-1 py-0.5 rounded text-amber-900 font-mono text-[11px]">PENDING</code> payments that must be filtered out.<br />
                    2) Non-returned orders do not exist in <code className="bg-amber-100 px-1 py-0.5 rounded text-amber-900 font-mono text-[11px]">lab_retail_returns</code>. Using an <code className="bg-rose-100 px-1 py-0.5 rounded text-rose-900 font-mono text-[11px]">INNER JOIN</code> discards ~80% of completed orders! A <code className="bg-emerald-100 px-1 py-0.5 rounded text-emerald-900 font-mono text-[11px]">LEFT JOIN</code> with <code className="bg-emerald-100 px-1 py-0.5 rounded text-emerald-900 font-mono text-[11px]">COALESCE(refund_amount, 0)</code> is strictly mandatory.
                  </p>
                </div>
              </div>
            </div>

            {/* Split Workspace: Schema Explorer & Live SQL Workbench */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Left Pane: Interactive Database Schema Explorer (4 cols) */}
              <div className="lg:col-span-5 space-y-4">
                <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4 text-blue-600" />
                      <h3 className="text-sm font-bold text-slate-900">Sandbox Schema Explorer</h3>
                    </div>
                    <span className="text-[11px] font-semibold text-slate-400">
                      SQLite Live DB
                    </span>
                  </div>

                  {/* Table Selection Tabs */}
                  <div className="flex flex-wrap gap-1.5">
                    {previews.map((prev, idx) => (
                      <button
                        key={prev.table_name}
                        onClick={() => setActiveTableIndex(idx)}
                        className={`text-xs px-2.5 py-1.5 rounded-md font-medium transition-colors cursor-pointer flex items-center gap-1.5 ${
                          activeTableIndex === idx
                            ? 'bg-blue-600 text-white font-semibold'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                        }`}
                      >
                        <TableIcon className="w-3 h-3" />
                        {prev.table_name.replace('lab_retail_', '')}
                        <span className={`text-[10px] px-1 rounded ${activeTableIndex === idx ? 'bg-blue-700 text-white' : 'bg-slate-200 text-slate-600'}`}>
                          {prev.row_count}
                        </span>
                      </button>
                    ))}
                  </div>

                  {/* Active Table Details */}
                  {activePreview && (
                    <div className="space-y-3 pt-2">
                      <div className="space-y-1">
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                          Table: <span className="text-slate-800 font-mono">{activePreview.table_name}</span>
                        </span>
                        {activePreview.quality_notes?.length > 0 && (
                          <div className="bg-blue-50 border border-blue-100 rounded-md p-2 space-y-0.5">
                            {activePreview.quality_notes.map((note, i) => (
                              <p key={i} className="text-[11px] text-blue-800 flex items-start gap-1">
                                <span className="text-blue-500 font-bold">•</span>
                                {note}
                              </p>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Columns List */}
                      <div className="border border-slate-200 rounded-lg overflow-hidden">
                        <div className="bg-slate-50 px-3 py-1.5 border-b border-slate-200 text-[11px] font-bold text-slate-600 grid grid-cols-2">
                          <span>Column Name</span>
                          <span>Data Type</span>
                        </div>
                        <div className="max-h-40 overflow-y-auto divide-y divide-slate-100 text-xs">
                          {activePreview.columns.map((col) => (
                            <div key={col.name} className="px-3 py-1.5 grid grid-cols-2 font-mono">
                              <span className="text-slate-800 font-medium">{col.name}</span>
                              <span className="text-slate-500">{col.type}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Sample Rows Preview */}
                      <div className="space-y-1.5">
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                          Sample Records (Top 5)
                        </span>
                        <div className="border border-slate-200 rounded-lg overflow-x-auto text-[11px]">
                          <table className="w-full text-left font-mono">
                            <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                              <tr>
                                {activePreview.columns.map((c) => (
                                  <th key={c.name} className="px-2.5 py-1.5 whitespace-nowrap">
                                    {c.name}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {activePreview.sample_rows.map((row, rIdx) => (
                                <tr key={rIdx} className="hover:bg-slate-50">
                                  {activePreview.columns.map((c) => (
                                    <td key={c.name} className="px-2.5 py-1 text-slate-700 whitespace-nowrap">
                                      {row[c.name] === null ? (
                                        <span className="text-rose-500 italic">NULL</span>
                                      ) : (
                                        String(row[c.name])
                                      )}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Attempt History Card */}
                <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Attempt History ({attempts.length})
                    </h3>
                  </div>
                  {attempts.length === 0 ? (
                    <p className="text-xs text-slate-400 italic">No previous attempts recorded yet.</p>
                  ) : (
                    <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                      {attempts.map((att) => (
                        <div
                          key={att.id}
                          className="p-2.5 rounded-lg border border-slate-100 bg-slate-50 flex items-center justify-between text-xs"
                        >
                          <div>
                            <span className="font-bold text-slate-800">
                              Attempt #{att.attempt_number}
                            </span>
                            <div className="text-[10px] text-slate-400 mt-0.5">
                              {new Date(att.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {att.execution_time_ms}ms
                            </div>
                          </div>
                          <div className="text-right">
                            <span
                              className={`text-xs font-bold px-2 py-0.5 rounded ${
                                att.status === 'PASSED'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : att.status === 'PARTIAL'
                                  ? 'bg-amber-100 text-amber-800'
                                  : 'bg-rose-100 text-rose-800'
                              }`}
                            >
                              {att.total_score}%
                            </span>
                            <span className="block text-[10px] text-slate-500 mt-0.5">
                              {att.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Right Pane: Live SQL Workbench & Submission (7 cols) */}
              <div className="lg:col-span-7 space-y-4">
                {/* SQL Code Editor Card */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col">
                  {/* Editor Header */}
                  <div className="bg-slate-950 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Code2 className="w-4 h-4 text-emerald-400" />
                      <span className="text-xs font-bold text-slate-200">
                        Interactive SQL Query Workbench
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        onClick={handleGetAIHint}
                        disabled={isFetchingHint}
                        className="text-[11px] font-bold text-amber-300 bg-amber-950/60 hover:bg-amber-900/80 border border-amber-600/50 px-2.5 py-1 rounded transition-colors cursor-pointer flex items-center gap-1.5"
                      >
                        {isFetchingHint ? (
                          <Loader2 className="w-3 h-3 animate-spin text-amber-300" />
                        ) : (
                          <Sparkles className="w-3 h-3 text-amber-300" />
                        )}
                        Ask Coach Hint (L{hintLevel}/3)
                      </button>

                      <button
                        onClick={handleFetchConceptDeepDive}
                        className="text-[11px] text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700 px-2 py-1 rounded transition-colors cursor-pointer"
                      >
                        Concept Guide
                      </button>

                      <button
                        onClick={handleFetchInterviewPrep}
                        className="text-[11px] text-blue-300 hover:text-blue-200 bg-blue-950/60 hover:bg-blue-900 px-2 py-1 rounded transition-colors cursor-pointer"
                      >
                        Interview Prep
                      </button>

                      <button
                        onClick={() => setQueryCode(CANONICAL_STARTER_SQL)}
                        className="text-[11px] text-slate-400 hover:text-slate-200 transition-colors cursor-pointer flex items-center gap-1 ml-1"
                      >
                        <RotateCcw className="w-3 h-3" />
                        Reset
                      </button>
                    </div>
                  </div>

                  {/* Progressive Hint Banner */}
                  {currentHint && (
                    <div className="bg-amber-950/80 border-b border-amber-600/40 p-3 flex items-start justify-between gap-3 text-xs text-amber-200">
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 bg-amber-900/80 px-1.5 py-0.5 rounded">
                            Hint Level {currentHint.hint_level} / 3: {currentHint.focus_concept}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {currentHint.fallback_used ? 'Deterministic Guide' : currentHint.model_used}
                          </span>
                        </div>
                        <p className="text-amber-100 font-medium leading-relaxed pt-1">
                          {currentHint.hint}
                        </p>
                      </div>
                      <button
                        onClick={() => setCurrentHint(null)}
                        className="text-amber-400 hover:text-amber-200 p-0.5 cursor-pointer"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  )}

                  {/* Code Textarea */}
                  <div className="p-3 bg-slate-900">
                    <textarea
                      value={queryCode}
                      onChange={(e) => setQueryCode(e.target.value)}
                      rows={14}
                      spellCheck={false}
                      className="w-full bg-slate-900 text-emerald-300 font-mono text-xs focus:outline-hidden resize-y leading-relaxed"
                      placeholder="Write your SQL SELECT query here..."
                    />
                  </div>

                  {/* Editor Action Bar */}
                  <div className="bg-slate-950 px-4 py-3 border-t border-slate-800 flex items-center justify-between">
                    <span className="text-[11px] text-slate-400 font-mono">
                      Safe Sandbox: SELECT &amp; WITH Only
                    </span>

                    <button
                      onClick={handleRunSandboxQuery}
                      disabled={isRunningQuery}
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-lg shadow-xs transition-colors cursor-pointer disabled:opacity-50"
                    >
                      {isRunningQuery ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                      Run Sandbox Query
                    </button>
                  </div>
                </div>

                {/* Sandbox Output Result Card */}
                {queryResult && (
                  <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-slate-700" />
                        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                          Query Execution Results
                        </h4>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono">
                        <span>{queryResult.row_count} rows</span>
                        <span>•</span>
                        <span>{queryResult.execution_time_ms} ms</span>
                      </div>
                    </div>

                    {queryResult.error_message ? (
                      <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-rose-800 text-xs font-mono">
                        {queryResult.error_message}
                      </div>
                    ) : (
                      <div className="border border-slate-200 rounded-lg overflow-x-auto text-xs">
                        <table className="w-full text-left font-mono">
                          <thead className="bg-slate-50 text-slate-700 border-b border-slate-200">
                            <tr>
                              {queryResult.columns.map((c) => (
                                <th key={c} className="px-3 py-2 whitespace-nowrap">
                                  {c}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {queryResult.rows.map((r, idx) => (
                              <tr key={idx} className="hover:bg-slate-50">
                                {queryResult.columns.map((c) => (
                                  <td key={c} className="px-3 py-1.5 whitespace-nowrap text-slate-800">
                                    {r[c] === null ? (
                                      <span className="text-rose-500 italic">NULL</span>
                                    ) : (
                                      String(r[c])
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}

                {/* Business Deduction & Final Submission Card */}
                <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
                  <div className="space-y-1">
                    <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider">
                      Executive Synthesis &amp; Business Deduction (Validation Pillar)
                    </label>
                    <p className="text-xs text-slate-500">
                      Explain your business findings based on the calculated net revenue and return rate % across segments.
                    </p>
                  </div>

                  <textarea
                    value={businessExplanation}
                    onChange={(e) => setBusinessExplanation(e.target.value)}
                    rows={3}
                    className="w-full border border-slate-300 rounded-lg p-3 text-xs text-slate-800 focus:border-blue-500 focus:outline-hidden leading-relaxed"
                    placeholder="Provide your executive analysis of segment return risk and net margins..."
                  />

                  <div className="flex items-center justify-between pt-2">
                    <div className="flex items-center gap-1.5 text-xs text-slate-500">
                      <Sparkles className="w-4 h-4 text-blue-600" />
                      Automated 4-pillar evaluation against ground truth
                    </div>

                    <button
                      onClick={handleSubmitEvaluation}
                      disabled={isSubmitting}
                      className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg shadow-sm transition-colors cursor-pointer disabled:opacity-50"
                    >
                      {isSubmitting ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Check className="w-4 h-4" />
                      )}
                      {isSubmitting ? 'Evaluating 4 Pillars...' : 'Submit Solution for Proof Verification'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Scenario Challenges List View */
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
              <h2 className="text-base font-bold text-slate-900">
                Active Skill Debt Intervention Tasks
              </h2>
              <p className="text-xs text-slate-500">
                Complete these targeted challenges to generate verifiable evidence and extinguish skill debt.
              </p>

              <div className="p-4 border-2 border-rose-300 bg-rose-50/20 rounded-xl flex items-start justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-rose-700 bg-rose-100 px-2 py-0.5 rounded">
                      Critical Priority
                    </span>
                    <span className="text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                      SQL JOINs
                    </span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-sm">
                    E-Commerce Customer Retention &amp; Returns Analytics Lab
                  </h3>
                  <p className="text-xs text-slate-600 max-w-2xl">
                    Multi-table relational schema analyzing customers, orders, and returns. Verifies LEFT JOIN usage, NULL handling, and status filtering.
                  </p>
                </div>

                <button
                  onClick={() => setActiveTab('lab')}
                  className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg transition-colors cursor-pointer shrink-0"
                >
                  Launch Interactive Sandbox
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 4-Pillar Evaluation Results Modal */}
        {showResultModal && evalResult && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs">
            <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 max-w-2xl w-full p-6 sm:p-7 space-y-6 animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
              {/* Header Status */}
              <div className="flex items-start justify-between gap-4 border-b border-slate-100 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-xs font-extrabold px-3 py-1 rounded-full uppercase tracking-wider ${
                        evalResult.status === 'PASSED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : evalResult.status === 'PARTIAL'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-rose-100 text-rose-800'
                      }`}
                    >
                      {evalResult.status} • {evalResult.total_score}% Score
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      Attempt #{evalResult.attempt_number}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-slate-900">
                    Automated 4-Pillar Verification Results
                  </h3>
                </div>

                <button
                  onClick={() => setShowResultModal(false)}
                  className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* 4 Pillars Breakdown Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 block">SQL Correctness</span>
                  <span className="text-lg font-extrabold text-slate-900">
                    {evalResult.section_scores.sql_correctness}
                    <span className="text-xs font-normal text-slate-400">/40</span>
                  </span>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden mt-1">
                    <div
                      className="bg-blue-600 h-full rounded-full"
                      style={{ width: `${(evalResult.section_scores.sql_correctness / 40) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 block">Data Quality</span>
                  <span className="text-lg font-extrabold text-slate-900">
                    {evalResult.section_scores.data_quality_handling}
                    <span className="text-xs font-normal text-slate-400">/20</span>
                  </span>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden mt-1">
                    <div
                      className="bg-emerald-600 h-full rounded-full"
                      style={{ width: `${(evalResult.section_scores.data_quality_handling / 20) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 block">Business Metrics</span>
                  <span className="text-lg font-extrabold text-slate-900">
                    {evalResult.section_scores.business_result}
                    <span className="text-xs font-normal text-slate-400">/25</span>
                  </span>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden mt-1">
                    <div
                      className="bg-amber-600 h-full rounded-full"
                      style={{ width: `${(evalResult.section_scores.business_result / 25) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-center space-y-1">
                  <span className="text-[11px] font-bold text-slate-500 block">Validation Reasoning</span>
                  <span className="text-lg font-extrabold text-slate-900">
                    {evalResult.section_scores.validation_reasoning}
                    <span className="text-xs font-normal text-slate-400">/15</span>
                  </span>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden mt-1">
                    <div
                      className="bg-purple-600 h-full rounded-full"
                      style={{ width: `${(evalResult.section_scores.validation_reasoning / 15) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Feedback Summary */}
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
                  Evaluation Feedback:
                </span>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {evalResult.feedback}
                </p>
              </div>

              {/* Diagnostic Failures List (if any) */}
              {evalResult.diagnostic_failures?.length > 0 && (
                <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl space-y-2">
                  <div className="flex items-center gap-2 text-rose-800 text-xs font-bold">
                    <AlertTriangle className="w-4 h-4 text-rose-600" />
                    Specific Diagnostic Flaws Identified:
                  </div>
                  <ul className="text-xs text-rose-700 space-y-1 list-disc pl-5">
                    {evalResult.diagnostic_failures.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Skill Evidence Generated Notice */}
              {evalResult.evidence_generated && (
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  <div className="space-y-1 text-xs">
                    <span className="font-bold text-emerald-900 block">
                      Verifiable Skill Evidence Recorded in Skill Passport!
                    </span>
                    <p className="text-emerald-800">
                      Score: <strong>{evalResult.evidence_generated.score}%</strong> • Type: {evalResult.evidence_generated.evidence_type}
                    </p>
                    <p className="text-emerald-700 text-[11px]">
                      Your Skill DNA and Dynamic Roadmap have been recalculated and updated automatically.
                    </p>
                  </div>
                </div>
              )}

              {/* AI Mistake Breakdown Button & Card */}
              {evalResult.status !== 'PASSED' && (
                <div className="space-y-3 pt-1">
                  {!mistakeExplanation ? (
                    <button
                      onClick={handleExplainMistake}
                      disabled={isExplainingMistake}
                      className="w-full py-2.5 px-4 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 border border-blue-200 rounded-xl text-blue-900 text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
                    >
                      {isExplainingMistake ? (
                        <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      ) : (
                        <Sparkles className="w-4 h-4 text-blue-600" />
                      )}
                      Explain My Mistake with AI Coach
                    </button>
                  ) : (
                    <div className="p-4 bg-blue-50/70 border border-blue-200 rounded-xl space-y-2.5 text-xs">
                      <div className="flex items-center justify-between border-b border-blue-200/60 pb-2">
                        <span className="font-bold text-blue-900 flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                          AI Learning Coach Mistake Breakdown
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {mistakeExplanation.fallback_used ? 'Deterministic Guide' : mistakeExplanation.model_used}
                        </span>
                      </div>

                      <div className="space-y-1">
                        <strong className="text-blue-950 block">What Went Wrong:</strong>
                        <p className="text-slate-800">{mistakeExplanation.what_went_wrong}</p>
                      </div>

                      <div className="space-y-1">
                        <strong className="text-blue-950 block">Why It Happened:</strong>
                        <p className="text-slate-800">{mistakeExplanation.why_it_happened}</p>
                      </div>

                      <div className="space-y-1">
                        <strong className="text-blue-950 block">How to Recognize Next Time:</strong>
                        <p className="text-emerald-900 font-medium">{mistakeExplanation.how_to_recognize_next_time}</p>
                      </div>

                      {mistakeExplanation.small_example && (
                        <div className="bg-slate-900 text-emerald-300 p-2.5 rounded font-mono text-[11px] overflow-x-auto">
                          {mistakeExplanation.small_example}
                        </div>
                      )}

                      {mistakeExplanation.short_practice_question && (
                        <div className="p-2.5 bg-white rounded border border-blue-200 text-slate-800">
                          <span className="font-bold text-blue-900 block text-[11px]">Quick Check Question:</span>
                          <p className="pt-0.5">{mistakeExplanation.short_practice_question}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  onClick={() => setShowResultModal(false)}
                  className="px-4 py-2.5 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
                >
                  Close
                </button>
                <Link
                  href="/roadmap"
                  className="inline-flex items-center gap-1.5 px-5 py-2.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors cursor-pointer"
                >
                  View Updated Roadmap
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Phase 11 — AI Concept Deep-Dive Modal */}
        {showConceptModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full border border-slate-200 p-6 space-y-4 animate-in fade-in duration-150">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                  <h3 className="text-base font-bold text-slate-900">
                    AI Concept Guide: SQL JOINs
                  </h3>
                </div>
                <button
                  onClick={() => setShowConceptModal(false)}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {isFetchingConcept ? (
                <div className="py-8 flex items-center justify-center gap-2 text-xs text-blue-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Synthesizing concept guide for Data Analyst...
                </div>
              ) : conceptExplanation ? (
                <div className="space-y-3 text-xs">
                  <div>
                    <span className="font-bold text-slate-900 block mb-0.5">Core Mechanism:</span>
                    <p className="text-slate-700 leading-relaxed">{conceptExplanation.concept_summary}</p>
                  </div>

                  <div className="bg-slate-900 text-emerald-300 p-3 rounded font-mono text-[11px] overflow-x-auto">
                    {conceptExplanation.concise_example}
                  </div>

                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-900 space-y-1">
                    <span className="font-bold block text-[11px]">Top Junior Analyst Pitfall:</span>
                    <p>{conceptExplanation.common_pitfall}</p>
                  </div>

                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-900 space-y-1">
                    <span className="font-bold block text-[11px]">Real-World Role Application:</span>
                    <p>{conceptExplanation.role_use_case}</p>
                  </div>

                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-slate-800 space-y-1">
                    <span className="font-bold block text-[11px]">Check Question:</span>
                    <p>{conceptExplanation.check_question}</p>
                  </div>
                </div>
              ) : null}

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setShowConceptModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
                >
                  Got It
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Phase 11 — AI Interview Prep Questions Modal */}
        {showInterviewModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
            <div className="bg-white rounded-xl shadow-xl max-w-xl w-full border border-slate-200 p-6 space-y-4 animate-in fade-in duration-150 max-h-[85vh] overflow-y-auto">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-600" />
                  <h3 className="text-base font-bold text-slate-900">
                    Role Interview Questions: SQL JOINs
                  </h3>
                </div>
                <button
                  onClick={() => setShowInterviewModal(false)}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {isFetchingInterview ? (
                <div className="py-8 flex items-center justify-center gap-2 text-xs text-indigo-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Generating technical interview questions for Data Analyst...
                </div>
              ) : (
                <div className="space-y-3">
                  {interviewQuestions.map((q, i) => (
                    <div key={i} className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5 text-xs">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded">
                          {q.category}
                        </span>
                        <span className="text-[11px] text-slate-400">Q{i + 1}</span>
                      </div>
                      <p className="font-semibold text-slate-900">{q.question}</p>
                      <div className="pt-1 text-slate-500 text-[11px]">
                        <strong>Interviewer Tip:</strong> {q.evaluation_tip}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setShowInterviewModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
