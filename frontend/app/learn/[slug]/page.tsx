'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { useLearner } from '../../../context/LearnerContext';
import { useCoach } from '../../../context/CoachContext';
import {
  api,
  ApiLearningModuleDetail,
  ApiPracticeSubmissionResponse,
  ApiConceptCheckSubmissionResponse,
  ApiAppliedTaskSubmissionResponse,
} from '../../../services/api';
import {
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  HelpCircle,
  Lightbulb,
  Code,
  FileCheck2,
  Briefcase,
  ChevronRight,
  Lock,
  RotateCw,
  Award,
  Terminal,
  ShieldCheck,
  Check,
  XCircle,
  ExternalLink,
  Globe,
} from 'lucide-react';

type TabType = 'LEARN' | 'EXAMPLE' | 'PRACTICE' | 'CHECK' | 'APPLY';

function parseStringList(val: any): string[] {
  if (!val) return [];
  if (Array.isArray(val)) {
    return val.map((item) => (typeof item === 'string' ? item.trim() : String(item))).filter(Boolean);
  }
  if (typeof val === 'string') {
    const trimmed = val.trim();
    if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) return parseStringList(parsed);
      } catch (e) {
        // Fall through
      }
    }
    if (trimmed.includes('\n') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      return trimmed
        .split('\n')
        .map((line) => line.replace(/^[-*•]\s*/, '').trim())
        .filter(Boolean);
    }
    if (trimmed.includes(',')) {
      return trimmed
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
    }
    return [trimmed];
  }
  return [];
}

function LearningModuleDetailContent() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;

  const { activeUserId, activeUser, isDemoMode, refreshUser } = useLearner();
  const { openCoach } = useCoach();

  const [module, setModule] = useState<ApiLearningModuleDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>('LEARN');

  // Practice state
  const [practiceType, setPracticeType] = useState<'GUIDED' | 'INDEPENDENT'>('GUIDED');
  const [practiceCode, setPracticeCode] = useState<string>('');
  const [revealedHints, setRevealedHints] = useState<number>(0);
  const [isSubmittingPractice, setIsSubmittingPractice] = useState<boolean>(false);
  const [practiceResult, setPracticeResult] = useState<ApiPracticeSubmissionResponse | null>(null);

  // Concept Check state
  const [quizAnswers, setQuizAnswers] = useState<Record<string, number>>({});
  const [isSubmittingQuiz, setIsSubmittingQuiz] = useState<boolean>(false);
  const [quizResult, setQuizResult] = useState<ApiConceptCheckSubmissionResponse | null>(null);

  // Applied Task state
  const [appliedText, setAppliedText] = useState<string>('');
  const [isSubmittingApplied, setIsSubmittingApplied] = useState<boolean>(false);
  const [appliedResult, setAppliedResult] = useState<ApiAppliedTaskSubmissionResponse | null>(null);

  const loadModuleDetail = async () => {
    if (!slug) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getLearningModule(slug, activeUserId || 1);
      setModule(data);
      // Initialize practice code template
      const initial = data.guided_practice?.starter_code || data.guided_practice?.initial_code;
      if (initial) {
        setPracticeCode(initial);
      }
    } catch (err: any) {
      console.error('Failed to load module:', err);
      setError(err?.message || 'Access denied or module locked.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadModuleDetail();
  }, [slug, activeUserId]);

  // When switching between guided and independent practice, set initial template
  const handleSwitchPracticeType = (type: 'GUIDED' | 'INDEPENDENT') => {
    setPracticeType(type);
    setPracticeResult(null);
    if (type === 'GUIDED') {
      const code = module?.guided_practice?.starter_code || module?.guided_practice?.initial_code;
      if (code) setPracticeCode(code);
    } else if (type === 'INDEPENDENT') {
      const code = module?.independent_practice?.starter_code || module?.independent_practice?.initial_code;
      if (code) setPracticeCode(code);
    }
  };

  // Submit Practice
  const handleSubmitPractice = async () => {
    if (!module || !practiceCode.trim()) return;
    setIsSubmittingPractice(true);
    try {
      const res = await api.submitPractice(slug, {
        user_id: activeUserId || 1,
        practice_type: practiceType,
        code: practiceCode,
        hints_used: revealedHints,
      });
      setPracticeResult(res);
      await refreshUser();
    } catch (err: any) {
      alert(err?.message || 'Practice submission failed.');
    } finally {
      setIsSubmittingPractice(false);
    }
  };

  // Submit Concept Check
  const handleSubmitQuiz = async () => {
    if (!module) return;
    setIsSubmittingQuiz(true);
    try {
      const res = await api.submitConceptCheck(slug, {
        user_id: activeUserId || 1,
        answers: quizAnswers,
      });
      setQuizResult(res);
      // Reload current module state to reflect updated status and scores
      await loadModuleDetail();
      await refreshUser();
    } catch (err: any) {
      alert(err?.message || 'Concept check submission failed.');
    } finally {
      setIsSubmittingQuiz(false);
    }
  };

  // Submit Applied Task
  const handleSubmitAppliedTask = async () => {
    if (!module || !appliedText.trim()) return;
    setIsSubmittingApplied(true);
    try {
      const res = await api.submitAppliedTask(slug, {
        user_id: activeUserId || 1,
        submission_text: appliedText,
      });
      setAppliedResult(res);
      await loadModuleDetail();
      await refreshUser();
    } catch (err: any) {
      alert(err?.message || 'Applied task submission failed.');
    } finally {
      setIsSubmittingApplied(false);
    }
  };

  if (isLoading) {
    return (
      <AppShell>
        <div className="max-w-4xl mx-auto py-16 text-center text-slate-500">
          <RotateCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-3" />
          <p className="text-sm font-semibold">Verifying prerequisite mastery and loading concept...</p>
        </div>
      </AppShell>
    );
  }

  if (error || !module) {
    return (
      <AppShell>
        <div className="max-w-xl mx-auto py-16 px-4">
          <div className="bg-white border border-slate-200 rounded-xl p-8 text-center shadow-xs">
            <div className="w-12 h-12 rounded-full bg-rose-50 text-rose-600 flex items-center justify-center mx-auto mb-4">
              <Lock className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-slate-900">Concept Access Locked</h2>
            <p className="text-xs text-slate-600 mt-2 leading-relaxed">
              {error || 'This learning module is locked until all prerequisite competencies are demonstrated.'}
            </p>
            <div className="mt-6 flex items-center justify-center gap-3">
              <Link
                href="/learn"
                className="px-4 py-2 text-xs font-semibold bg-blue-800 text-white rounded-lg hover:bg-blue-900 shadow-2xs"
              >
                Return to Learning Curriculum
              </Link>
            </div>
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="max-w-5xl mx-auto space-y-6 pb-16">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between text-xs text-slate-500">
          <Link
            href="/learn"
            className="inline-flex items-center gap-1.5 hover:text-slate-800 font-medium transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Curriculum</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">{module.skill_name}</span>
            <span>•</span>
            <span className="font-mono">{module.estimated_minutes} min lesson</span>
          </div>
        </div>

        {/* Top Header Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  {module.difficulty}
                </span>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                  module.status === 'MASTERED'
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : module.status === 'REMEDIATION'
                    ? 'bg-rose-50 text-rose-700 border border-rose-200'
                    : 'bg-slate-100 text-slate-700'
                }`}>
                  {module.status}
                </span>
                {module.concept_check_passed && (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    Verified Mastery
                  </span>
                )}
              </div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                {module.title}
              </h1>
              <p className="text-xs text-slate-500">
                Core Concept: <span className="font-semibold text-slate-700">{module.concept_name}</span>
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() =>
                  openCoach(
                    `I am currently studying the ${module.concept_name} module for my ${module.target_role_name || 'target'} career path. Can you explain why this skill is critical and how to avoid common pitfalls?`
                  )
                }
                className="px-3 py-2 text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg shadow-2xs flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                <span>Ask AI Coach</span>
              </button>
            </div>
          </div>

          {/* 5-Step Workflow Tab Bar */}
          <div className="flex items-center gap-2 mt-6 pt-6 border-t border-slate-100 overflow-x-auto">
            {[
              { id: 'LEARN', label: '1. Learn Concept', icon: BookOpen },
              { id: 'EXAMPLE', label: '2. Worked Example', icon: Code },
              { id: 'PRACTICE', label: '3. Practice Lab', icon: Terminal },
              { id: 'CHECK', label: '4. Concept Check', icon: FileCheck2 },
              { id: 'APPLY', label: '5. Real-World Task', icon: Briefcase },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as TabType)}
                  className={`px-3.5 py-2 text-xs font-semibold rounded-lg flex items-center gap-2 transition-colors whitespace-nowrap cursor-pointer ${
                    isActive
                      ? 'bg-blue-800 text-white shadow-2xs'
                      : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200/60'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ========================================================================= */}
        {/* TAB 1: LEARN (Concise Teaching & Intuition)                              */}
        {/* ========================================================================= */}
        {activeTab === 'LEARN' && (
          <div className="space-y-6">
            {/* Learning Objectives */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-3">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-700" />
                Learning Objectives
              </h3>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-700">
                {parseStringList(module.learning_objectives).map((obj, i) => (
                  <li key={i} className="flex items-start gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
                    <span>{obj}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Core Explanation */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
              <h3 className="text-base font-bold text-slate-900">
                Conceptual Foundation & Intuition
              </h3>
              <div className="text-xs text-slate-700 leading-relaxed space-y-3 whitespace-pre-line font-sans">
                {module.explanation}
              </div>
            </div>

            {/* Two-Column: Key Rules & Common Mistakes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Key Rules */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  Governing Rules & Best Practices
                </h4>
                <ul className="space-y-2 text-xs text-slate-700">
                  {parseStringList(module.key_rules).map((rule, idx) => (
                    <li key={idx} className="flex items-start gap-2 bg-emerald-50/50 p-2.5 rounded-lg border border-emerald-100">
                      <Check className="w-3.5 h-3.5 text-emerald-700 shrink-0 mt-0.5" />
                      <span>{rule}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Common Pitfalls */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                  Common Industry Mistakes
                </h4>
                <ul className="space-y-2 text-xs text-slate-700">
                  {parseStringList(module.common_mistakes).map((mistake, idx) => (
                    <li key={idx} className="flex items-start gap-2 bg-rose-50/50 p-2.5 rounded-lg border border-rose-100">
                      <XCircle className="w-3.5 h-3.5 text-rose-700 shrink-0 mt-0.5" />
                      <span>{mistake}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Authoritative External Learning Resources (Sections 12-16) */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-blue-700" />
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Verified External Learning References
                  </h4>
                </div>
                <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                  Concept & Role Tailored
                </span>
              </div>

              {module.external_resources && module.external_resources.length > 0 ? (
                <div className="grid grid-cols-1 gap-2.5">
                  {module.external_resources.map((res) => (
                    <a
                      key={res.id}
                      href={res.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 bg-slate-50 hover:bg-blue-50/50 border border-slate-200 hover:border-blue-300 rounded-lg transition-all"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                              res.quality_rank === 1
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-blue-100 text-blue-800'
                            }`}
                          >
                            {res.quality_rank === 1 ? 'Tier 1 • Official Docs' : 'Tier 2 • Educational Platform'}
                          </span>
                          <span className="text-[11px] font-medium text-slate-500">
                            {res.provider}
                          </span>
                        </div>
                        <h5 className="text-xs font-bold text-slate-900 group-hover:text-blue-700 flex items-center gap-1.5">
                          <span>{res.title}</span>
                        </h5>
                      </div>

                      <div className="flex items-center gap-3 shrink-0 self-start sm:self-auto text-xs text-slate-500">
                        <span className="inline-flex items-center gap-1 font-mono text-[11px]">
                          <Clock className="w-3 h-3 text-slate-400" />
                          {res.estimated_minutes} min
                        </span>
                        <span className="inline-flex items-center gap-1 text-blue-700 group-hover:translate-x-0.5 transition-transform font-semibold text-xs">
                          <span>Read Source</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </span>
                      </div>
                    </a>
                  ))}
                </div>
              ) : (
                <div className="p-4 bg-slate-50 border border-slate-100 rounded-lg text-center text-xs text-slate-500 italic">
                  No verified external resource available yet
                </div>
              )}
            </div>

            {/* Advance Footer */}
            <div className="flex justify-end pt-2">
              <button
                onClick={() => setActiveTab('EXAMPLE')}
                className="px-4 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 rounded-lg shadow-2xs flex items-center gap-2 cursor-pointer transition-colors"
              >
                <span>Step 2: Study Worked Example</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: WORKED EXAMPLE (Realistic Scenario & Step Reasoning)              */}
        {/* ========================================================================= */}
        {activeTab === 'EXAMPLE' && module.worked_example && (
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-5">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                  Production Case Study
                </span>
                <h3 className="text-lg font-bold text-slate-900 mt-1">
                  {module.worked_example.title || `${module.title} — Production Case Study`}
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {module.worked_example.scenario}
                </p>
              </div>

              {/* Code / Query Block */}
              <div>
                <div className="flex items-center justify-between text-xs font-mono text-slate-400 bg-slate-900 px-4 py-2 rounded-t-lg">
                  <span>PRODUCTION SOLUTION PATTERN</span>
                  <span>SQL / PYTHON</span>
                </div>
                <pre className="bg-slate-950 text-slate-100 font-mono text-xs p-4 rounded-b-lg overflow-x-auto leading-relaxed border border-slate-800">
                  {module.worked_example.code_or_query || module.worked_example.code || '-- No code snippet provided'}
                </pre>
              </div>

              {/* Reasoning */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-1.5">
                <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <Lightbulb className="w-4 h-4 text-amber-600" />
                  Step-by-Step Execution Rationale
                </h4>
                <p className="text-xs text-slate-700 leading-relaxed whitespace-pre-line font-sans">
                  {module.worked_example.explanation || module.worked_example.reasoning || 'Follow the production pattern to ensure verified outcomes.'}
                </p>
              </div>

              {/* Expected Output */}
              <div className="bg-blue-50/50 border border-blue-200/60 rounded-lg p-4 space-y-1.5">
                <h4 className="text-xs font-bold text-blue-900">
                  Expected Output & Metric Verification
                </h4>
                <p className="text-xs font-mono text-slate-800 leading-relaxed bg-white p-2.5 rounded border border-blue-100">
                  {module.worked_example.output || module.worked_example.expected_output || 'Output matches verified assertions.'}
                </p>
              </div>
            </div>

            {/* Advance Footer */}
            <div className="flex items-center justify-between pt-2">
              <button
                onClick={() => setActiveTab('LEARN')}
                className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50"
              >
                Back to Explanation
              </button>
              <button
                onClick={() => setActiveTab('PRACTICE')}
                className="px-4 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 rounded-lg shadow-2xs flex items-center gap-2 cursor-pointer transition-colors"
              >
                <span>Step 3: Begin Practice Lab</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: PRACTICE LAB (Guided & Independent Adaptive Practice)             */}
        {/* ========================================================================= */}
        {activeTab === 'PRACTICE' && (
          <div className="space-y-6">
            {/* Practice Mode Switcher */}
            <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-lg w-fit">
              <button
                onClick={() => handleSwitchPracticeType('GUIDED')}
                className={`px-3 py-1.5 text-xs font-bold rounded-md transition-all cursor-pointer ${
                  practiceType === 'GUIDED'
                    ? 'bg-white text-blue-800 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Guided Practice (With Scaffolding)
              </button>
              <button
                onClick={() => handleSwitchPracticeType('INDEPENDENT')}
                className={`px-3 py-1.5 text-xs font-bold rounded-md transition-all cursor-pointer ${
                  practiceType === 'INDEPENDENT'
                    ? 'bg-white text-blue-800 shadow-2xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Independent Practice (No Assistance)
              </button>
            </div>

            {/* Prompt & Instructions */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  {practiceType === 'GUIDED'
                    ? module.guided_practice?.title || 'Guided Practice Drill'
                    : module.independent_practice?.title || 'Independent Application Drill'}
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {practiceType === 'GUIDED'
                    ? module.guided_practice?.instructions
                    : module.independent_practice?.instructions}
                </p>
              </div>

              {/* Code Editor */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
                  <span>ENTER YOUR SOLUTION CODE / QUERY</span>
                  <span>SQL / Python</span>
                </div>
                <textarea
                  rows={8}
                  value={practiceCode}
                  onChange={(e) => setPracticeCode(e.target.value)}
                  placeholder="Write your solution here..."
                  className="w-full font-mono text-xs p-4 bg-slate-950 text-slate-100 rounded-lg border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent leading-relaxed"
                />
              </div>

              {/* Hints Box (for guided) */}
              {practiceType === 'GUIDED' && (
                (() => {
                  const hintsList = parseStringList(module.guided_practice?.hints);
                  if (hintsList.length === 0) return null;
                  return (
                    <div className="bg-amber-50/50 border border-amber-200/70 rounded-lg p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                          <HelpCircle className="w-3.5 h-3.5 text-amber-700" />
                          Adaptive Progressive Hints
                        </span>
                        {revealedHints < hintsList.length && (
                          <button
                            onClick={() => setRevealedHints((prev) => prev + 1)}
                            className="text-xs font-semibold text-amber-800 hover:text-amber-950 underline cursor-pointer"
                          >
                            Reveal Hint {revealedHints + 1} of {hintsList.length}
                          </button>
                        )}
                      </div>
                      {revealedHints > 0 ? (
                        <div className="space-y-1.5 pt-1">
                          {hintsList.slice(0, revealedHints).map((hint, i) => (
                            <p key={i} className="text-xs text-amber-800 bg-white/80 p-2 rounded border border-amber-200">
                              <span className="font-bold">Hint {i + 1}:</span> {hint}
                            </p>
                          ))}
                        </div>
                      ) : (
                        <p className="text-[11px] text-amber-700">
                          Need guidance? Click reveal hint. Note: Using hints slightly reduces the practice score.
                        </p>
                      )}
                    </div>
                  );
                })()
              )}

              {/* Practice Submission Feedback */}
              {practiceResult && (
                <div className={`p-4 rounded-lg border text-xs ${
                  practiceResult.is_correct
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : 'bg-rose-50 border-rose-200 text-rose-900'
                }`}>
                  <div className="flex items-center justify-between font-bold">
                    <span className="flex items-center gap-1.5">
                      {practiceResult.is_correct ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-rose-600" />
                      )}
                      {practiceResult.is_correct ? 'Correct Solution!' : 'Solution Needs Revision'}
                    </span>
                    <span>Score: {practiceResult.score}%</span>
                  </div>
                  <p className="mt-1 leading-relaxed text-slate-700">{practiceResult.feedback}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-2">
                <button
                  onClick={() =>
                    openCoach(
                      `I am working on the practice exercise for ${module.concept_name}: "${practiceCode}". Can you review my approach without giving away the full answer?`
                    )
                  }
                  className="px-3 py-1.5 text-xs font-semibold text-blue-700 hover:text-blue-900 inline-flex items-center gap-1"
                >
                  <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                  <span>Ask Coach for Debug Advice</span>
                </button>

                <div className="flex items-center gap-3">
                  <button
                    onClick={handleSubmitPractice}
                    disabled={isSubmittingPractice || !practiceCode.trim()}
                    className="px-4 py-2 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 disabled:bg-slate-300 rounded-lg shadow-2xs flex items-center gap-1.5 cursor-pointer transition-colors"
                  >
                    {isSubmittingPractice ? (
                      <RotateCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Terminal className="w-3.5 h-3.5" />
                    )}
                    <span>Submit Solution</span>
                  </button>
                  <button
                    onClick={() => setActiveTab('CHECK')}
                    className="px-4 py-2 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>Step 4: Take Concept Check</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: CONCEPT CHECK (Deterministic Mastery Evaluation)                   */}
        {/* ========================================================================= */}
        {activeTab === 'CHECK' && (
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Formative Concept Check
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Demonstrate understanding to verify mastery and unlock dependent milestones. Minimum score: {module.passing_threshold}%.
                  </p>
                </div>

                {module.concept_check_score !== undefined && module.concept_check_score > 0 && (
                  <span className={`px-3 py-1 rounded-md text-xs font-bold shrink-0 ${
                    module.concept_check_passed
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-rose-50 text-rose-800 border border-rose-200'
                  }`}>
                    Best Score: {module.concept_check_score}%
                  </span>
                )}
              </div>

              {/* Questions List */}
              <div className="space-y-6">
                {(module.concept_check_questions || []).map((q, qIndex) => {
                  const qKey = q.id || q.question_id || `q_${qIndex}`;
                  const selected = quizAnswers[qKey];
                  const qResult = quizResult?.results?.find(
                    (r) => r.question_id === qKey || r.question_id === q.id || r.question_id === q.question_id
                  );
                  const qText = q.question || q.question_text || `Question ${qIndex + 1}`;
                  const optionsList = parseStringList(q.options);

                  return (
                    <div
                      key={qKey}
                      className="p-5 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3"
                    >
                      <h4 className="text-xs font-bold text-slate-900 flex items-start gap-2">
                        <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                          {qIndex + 1}
                        </span>
                        <span className="leading-relaxed">{qText}</span>
                      </h4>

                      <div className="space-y-2 pt-1 pl-7">
                        {optionsList.map((opt, optIndex) => {
                          const isOptionSelected = selected === optIndex;
                          let optionStyle = 'bg-white border-slate-200 text-slate-700 hover:border-slate-300';

                          if (qResult) {
                            if (optIndex === qResult.correct_option) {
                              optionStyle = 'bg-emerald-50 border-emerald-300 text-emerald-900 font-semibold';
                            } else if (isOptionSelected && !qResult.is_correct) {
                              optionStyle = 'bg-rose-50 border-rose-300 text-rose-900';
                            }
                          } else if (isOptionSelected) {
                            optionStyle = 'bg-blue-50 border-blue-400 text-blue-900 font-semibold';
                          }

                          return (
                            <label
                              key={optIndex}
                              className={`flex items-start gap-3 p-3 rounded-lg border text-xs cursor-pointer transition-all ${optionStyle}`}
                            >
                              <input
                                type="radio"
                                name={`q_${qKey}`}
                                checked={isOptionSelected}
                                onChange={() =>
                                  setQuizAnswers((prev) => ({ ...prev, [qKey]: optIndex }))
                                }
                                disabled={isSubmittingQuiz}
                                className="mt-0.5 text-blue-600 focus:ring-blue-500"
                              />
                              <span className="leading-relaxed">{opt}</span>
                            </label>
                          );
                        })}
                      </div>

                      {/* Post-submit explanation */}
                      {qResult && (
                        <div className="mt-2 pl-7 text-xs text-slate-600 bg-white p-3 rounded-lg border border-slate-200">
                          <span className="font-bold text-slate-800">Explanation: </span>
                          <span>{qResult.explanation}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Quiz Result Banner */}
              {quizResult && (
                <div className={`p-5 rounded-xl border text-xs space-y-2 ${
                  quizResult.passed
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : 'bg-rose-50 border-rose-200 text-rose-900'
                }`}>
                  <div className="flex items-center justify-between font-bold text-sm">
                    <span className="flex items-center gap-2">
                      {quizResult.passed ? (
                        <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-rose-600" />
                      )}
                      {quizResult.passed ? 'Concept Check Passed! Mastery Verified' : 'Passing Threshold Not Met'}
                    </span>
                    <span>{quizResult.score}% (Target: {quizResult.passing_threshold}%)</span>
                  </div>

                  {quizResult.passed && quizResult.unlocked_modules && quizResult.unlocked_modules.length > 0 && (
                    <div className="pt-2 border-t border-emerald-200/60">
                      <span className="font-bold block text-emerald-950 mb-1">
                        Unlocked Dependent Milestone(s):
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {quizResult.unlocked_modules.map((m) => (
                          <span key={m} className="px-2 py-0.5 bg-emerald-200/60 text-emerald-900 rounded font-mono text-[11px]">
                            {m}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Submit Quiz Button */}
              <div className="flex items-center justify-between pt-2">
                <button
                  onClick={() => setActiveTab('PRACTICE')}
                  className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50"
                >
                  Back to Practice
                </button>
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={isSubmittingQuiz || Object.keys(quizAnswers).length === 0}
                    className="px-5 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 disabled:bg-slate-300 rounded-lg shadow-2xs flex items-center gap-2 cursor-pointer transition-colors"
                  >
                    {isSubmittingQuiz ? (
                      <RotateCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <FileCheck2 className="w-3.5 h-3.5" />
                    )}
                    <span>Grade Concept Check</span>
                  </button>
                  <button
                    onClick={() => setActiveTab('APPLY')}
                    className="px-4 py-2.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>Step 5: Real-World Task</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 5: APPLIED TASK (Role-Specific Practical Proof)                       */}
        {/* ========================================================================= */}
        {activeTab === 'APPLY' && module.applied_task && (
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
              <div>
                <div className="flex items-center gap-2 text-xs font-bold text-blue-700 uppercase tracking-wider mb-1">
                  <Briefcase className="w-4 h-4" />
                  <span>Target Role Deliverable</span>
                  <span className="text-slate-300">•</span>
                  <span className="text-slate-600">
                    {module.applied_task.role_relevance || module.applied_task.role_scenario || `Role Relevance: ${module.target_role_name || 'Data Analyst'}`}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-900">
                  {module.applied_task.title || module.applied_task.role_scenario || `Applied Real-World Project: ${module.title}`}
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {module.applied_task.business_context || module.applied_task.task_description}
                </p>
              </div>

              {/* Prompt & Deliverable */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Task Specification & Prompt
                </h4>
                <p className="text-xs text-slate-800 font-mono bg-white p-3 rounded border border-slate-200 leading-relaxed whitespace-pre-wrap">
                  {module.applied_task.task_prompt || module.applied_task.starter_code || module.applied_task.task_description}
                </p>
                <div className="text-xs text-slate-600">
                  <span className="font-bold text-slate-800">Expected Deliverable: </span>
                  {module.applied_task.expected_deliverable || 'Production-grade SQL or Python deliverable with verification.'}
                </div>
              </div>

              {/* Rubric */}
              {(() => {
                const rubricList = parseStringList(
                  module.applied_task.evaluation_rubric || module.applied_task.rubrics
                );
                if (rubricList.length === 0) return null;
                return (
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Verification Rubric
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-700">
                      {rubricList.map((item, idx) => (
                        <div key={idx} className="flex items-start gap-2 bg-slate-50 p-2 rounded border border-slate-100">
                          <CheckCircle2 className="w-3.5 h-3.5 text-blue-700 shrink-0 mt-0.5" />
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })()}

              {/* Deliverable Editor */}
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Submit Applied Work / Query / Solution
                </label>
                <textarea
                  rows={6}
                  value={appliedText}
                  onChange={(e) => setAppliedText(e.target.value)}
                  placeholder="Paste your production query, analysis notes, or code deliverable..."
                  className="w-full font-mono text-xs p-3.5 bg-slate-950 text-slate-100 rounded-lg border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent leading-relaxed"
                />
              </div>

              {/* Applied Feedback */}
              {appliedResult && (
                <div className={`p-4 rounded-lg border text-xs ${
                  appliedResult.passed
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : 'bg-rose-50 border-rose-200 text-rose-900'
                }`}>
                  <div className="flex items-center justify-between font-bold">
                    <span className="flex items-center gap-1.5">
                      <Award className="w-4 h-4 text-emerald-600" />
                      Applied Evidence Recorded
                    </span>
                    <span>Evidence Score: {appliedResult.evidence_score}</span>
                  </div>
                  <p className="mt-1 leading-relaxed text-slate-700">{appliedResult.feedback}</p>
                </div>
              )}

              {/* Submit Button */}
              <div className="flex items-center justify-between pt-2">
                <button
                  onClick={() => setActiveTab('CHECK')}
                  className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50"
                >
                  Back to Concept Check
                </button>
                <button
                  onClick={handleSubmitAppliedTask}
                  disabled={isSubmittingApplied || !appliedText.trim()}
                  className="px-5 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 disabled:bg-slate-300 rounded-lg shadow-2xs flex items-center gap-2 cursor-pointer transition-colors"
                >
                  {isSubmittingApplied ? (
                    <RotateCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Award className="w-3.5 h-3.5" />
                  )}
                  <span>Record Applied Evidence</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

export default function LearningModuleDetailPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 text-center">
          <div className="bg-white border border-slate-200 rounded-lg p-12 shadow-sm max-w-sm w-full">
            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-sm font-semibold text-slate-800">Loading Adaptive Learning Module...</p>
          </div>
        </div>
      }
    >
      <LearningModuleDetailContent />
    </Suspense>
  );
}
