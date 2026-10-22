'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import { useLearner } from '../../../context/LearnerContext';
import { useCoach } from '../../../context/CoachContext';
import { MarkdownMathRenderer } from '../../../components/MarkdownMathRenderer';
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
  Layers,
  Compass,
  Bookmark,
  TrendingUp,
  FileText,
  CheckSquare,
} from 'lucide-react';

type TabType = 'LEARN' | 'EXAMPLE' | 'PRACTICE' | 'CHECK' | 'APPLY';
type LevelType = 'Beginner' | 'Intermediate' | 'Advanced';

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
  const [selectedLevel, setSelectedLevel] = useState<LevelType>('Intermediate');

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

  const loadModuleDetail = async (overrideLevel?: LevelType) => {
    if (!slug) return;
    setIsLoading(true);
    setError(null);
    try {
      const targetLvl = overrideLevel || selectedLevel;
      const data = await api.getLearningModule(slug, activeUserId || 1, targetLvl);
      setModule(data);
      if (data.effective_level && (data.effective_level === 'Beginner' || data.effective_level === 'Intermediate' || data.effective_level === 'Advanced')) {
        setSelectedLevel(data.effective_level as LevelType);
      }
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

  const handleLevelChange = async (lvl: LevelType) => {
    setSelectedLevel(lvl);
    await loadModuleDetail(lvl);
  };

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

  // Submit Concept Check Quiz
  const handleSubmitQuiz = async () => {
    if (!module) return;
    setIsSubmittingQuiz(true);
    try {
      const res = await api.submitConceptCheck(slug, {
        user_id: activeUserId || 1,
        answers: quizAnswers,
      });
      setQuizResult(res);
      await refreshUser();
      // Reload module to update status & unlocked prerequisites
      await loadModuleDetail();
    } catch (err: any) {
      alert(err?.message || 'Failed to submit concept check.');
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
        code_or_query: appliedText,
        business_rationale: 'Submitted through applied learning workspace.',
      });
      setAppliedResult(res);
      await refreshUser();
      await loadModuleDetail();
    } catch (err: any) {
      alert(err?.message || 'Applied task submission failed.');
    } finally {
      setIsSubmittingApplied(false);
    }
  };

  // Determine user's active target role name
  const activeRoleName =
    (activeUser as any)?.target_role_name ||
    activeUser?.target_role?.name ||
    module?.target_role_name ||
    'Data Analyst';
  const roleWhyMatters =
    module?.why_it_matters_by_role?.[activeRoleName] ||
    module?.why_it_matters_by_role?.['Data Analyst'] ||
    module?.why_it_matters_by_role?.['Data Scientist'] ||
    module?.why_it_matters_by_role?.['Python Developer'] ||
    `Mastering ${module?.concept_name} provides the foundational precision required for ${activeRoleName} deliverables.`;

  const currentLevelVariation = module?.level_variations?.[selectedLevel];

  if (isLoading && !module) {
    return (
      <AppShell>
        <div className="min-h-[60vh] flex items-center justify-center p-6 text-center">
          <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-xs max-w-sm w-full space-y-3">
            <div className="inline-block w-8 h-8 border-3 border-blue-700 border-t-transparent rounded-full animate-spin" />
            <p className="text-xs font-semibold text-slate-800">
              Loading Adaptive Learning Module...
            </p>
            <p className="text-[11px] text-slate-500">
              Personalizing curriculum for {activeRoleName} ({selectedLevel} level)
            </p>
          </div>
        </div>
      </AppShell>
    );
  }

  if (error || !module) {
    return (
      <AppShell>
        <div className="max-w-xl mx-auto my-12 p-8 bg-white border border-rose-200 rounded-xl shadow-xs text-center space-y-4">
          <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center mx-auto">
            <Lock className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Module Access Restricted</h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            {error || 'This learning module is locked. Prerequisite concepts must be completed first.'}
          </p>
          <div className="pt-2">
            <Link
              href="/learn"
              className="px-4 py-2 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 rounded-lg inline-flex items-center gap-2"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to Learning Path</span>
            </Link>
          </div>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="max-w-6xl mx-auto space-y-6 pb-20">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between text-xs text-slate-500">
          <Link
            href="/learn"
            className="inline-flex items-center gap-1.5 hover:text-slate-800 font-semibold transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Role Curriculum</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-700">{module.skill_name}</span>
            <span>•</span>
            <span className="font-mono text-slate-500">{module.estimated_minutes} min lesson</span>
          </div>
        </div>

        {/* Top Header Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-xs space-y-5">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-5">
            <div className="space-y-2.5 max-w-3xl">
              {/* Badges & Meta */}
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-800 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
                  Target Role: {activeRoleName}
                </span>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-700 bg-slate-100 px-2.5 py-0.5 rounded-full border border-slate-200">
                  Skill: {module.skill_name}
                </span>
                <span
                  className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider border ${
                    module.status === 'MASTERED'
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                      : module.status === 'REMEDIATION'
                      ? 'bg-rose-50 text-rose-800 border-rose-300'
                      : 'bg-slate-50 text-slate-700 border-slate-200'
                  }`}
                >
                  Status: {module.status}
                </span>
                {module.concept_check_passed && (
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    Verified Mastery
                  </span>
                )}
              </div>

              {/* Title & Core Concept */}
              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight leading-tight">
                {module.title}
              </h1>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-medium">
                Core Competency: <span className="font-bold text-slate-900">{module.concept_name}</span>
              </p>
            </div>

            {/* Header Right Actions: Coach & Adaptive Level Selector */}
            <div className="flex flex-col items-start lg:items-end gap-3 shrink-0">
              <button
                onClick={() =>
                  openCoach(
                    `I am studying the ${module.concept_name} module for my ${activeRoleName} career path. Can you explain why this skill is critical and how to avoid common pitfalls?`
                  )
                }
                className="px-3.5 py-2 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl shadow-2xs flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                <span>Ask AI Career Coach</span>
              </button>

              {/* Adaptive Learner Level Switcher */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-2">
                  Level:
                </span>
                {(['Beginner', 'Intermediate', 'Advanced'] as LevelType[]).map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => handleLevelChange(lvl)}
                    className={`px-2.5 py-1 text-[11px] font-bold rounded-lg transition-all cursor-pointer ${
                      selectedLevel === lvl
                        ? 'bg-white text-blue-900 shadow-2xs border border-slate-200'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    title={`Adapt instructional depth for ${lvl} learners`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 5-Step Workflow Tab Bar */}
          <div className="flex items-center gap-2 pt-4 border-t border-slate-100 overflow-x-auto">
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
                  className={`px-3.5 py-2 text-xs font-bold rounded-xl flex items-center gap-2 transition-all whitespace-nowrap cursor-pointer ${
                    isActive
                      ? 'bg-blue-900 text-white shadow-xs'
                      : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200/80'
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
        {/* TAB 1: LEARN (Comprehensive Teaching, Objectives & Foundations)           */}
        {/* ========================================================================= */}
        {activeTab === 'LEARN' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
            {/* Left Sticky Table of Contents / Subtopics (Desktop) */}
            <div className="hidden lg:block lg:col-span-1 sticky top-6 space-y-4">
              <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-xs space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5 pb-2 border-b border-slate-100">
                  <Bookmark className="w-3.5 h-3.5 text-blue-700" />
                  Lesson Subtopics
                </h4>
                <nav className="space-y-1">
                  {(module.subtopics || [
                    { id: 'objectives', title: '1. Learning Objectives' },
                    { id: 'why-it-matters', title: '2. Why This Matters' },
                    { id: 'foundation', title: '3. Conceptual Foundation' },
                    { id: 'examples', title: '4. Practical Examples' },
                    { id: 'rules-mistakes', title: '5. Rules & Pitfalls' },
                    { id: 'quick-ref', title: '6. Quick Reference' },
                    { id: 'resources', title: '7. External References' },
                  ]).map((sub, idx) => (
                    <a
                      key={idx}
                      href={`#${sub.id}`}
                      className="block text-[11px] text-slate-600 hover:text-blue-800 hover:bg-blue-50/60 p-2 rounded-lg font-medium transition-colors"
                    >
                      {sub.title}
                    </a>
                  ))}
                </nav>

                <div className="pt-3 border-t border-slate-100">
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>Curriculum Level</span>
                    <span className="font-bold text-blue-800">{selectedLevel}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Main Learning Content */}
            <div className="lg:col-span-3 space-y-6">
              {/* 1. Learning Objectives */}
              <div id="objectives" className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-3.5">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-blue-700" />
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    What You Will Learn
                  </h3>
                </div>
                <ul className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs text-slate-700">
                  {parseStringList(module.learning_objectives).map((obj, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2.5 bg-slate-50 p-3 rounded-xl border border-slate-100 leading-relaxed font-medium"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 shrink-0" />
                      <span>{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* 2. Role-Specific "Why This Matters" */}
              <div id="why-it-matters" className="bg-gradient-to-r from-blue-50/90 via-indigo-50/50 to-slate-50 border border-blue-200 rounded-2xl p-6 shadow-xs space-y-2.5">
                <div className="flex items-center gap-2 text-blue-900">
                  <Briefcase className="w-4 h-4 text-blue-700" />
                  <h3 className="text-xs font-bold uppercase tracking-wider">
                    Why This Matters for a {activeRoleName}
                  </h3>
                </div>
                <div className="text-xs text-slate-800 leading-relaxed font-medium">
                  <MarkdownMathRenderer content={roleWhyMatters} />
                </div>
              </div>

              {/* 3. Level-Specific Focus & Prerequisite Callout */}
              {currentLevelVariation && (
                <div className="bg-amber-50/60 border border-amber-200 rounded-2xl p-5 shadow-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-900 bg-amber-100/80 px-2 py-0.5 rounded">
                      {selectedLevel} Learning Scope
                    </span>
                    <span className="text-xs font-bold text-amber-900">
                      Focus: {currentLevelVariation.focus}
                    </span>
                  </div>
                  {currentLevelVariation.prerequisite_recap && (
                    <p className="text-xs text-amber-950/90 leading-relaxed">
                      <span className="font-bold">Prerequisite Context: </span>
                      {currentLevelVariation.prerequisite_recap}
                    </p>
                  )}
                  {currentLevelVariation.explanation_supplement && (
                    <div className="pt-2 text-xs text-slate-800">
                      <MarkdownMathRenderer content={currentLevelVariation.explanation_supplement} />
                    </div>
                  )}
                </div>
              )}

              {/* 4. Conceptual Foundation & Intuition */}
              <div id="foundation" className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-xs space-y-4">
                <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                  <BookOpen className="w-4 h-4 text-blue-700" />
                  <h3 className="text-base font-extrabold text-slate-900">
                    Conceptual Foundation & Intuition
                  </h3>
                </div>
                <div className="text-slate-800 text-xs sm:text-sm leading-relaxed">
                  <MarkdownMathRenderer content={module.explanation} />
                </div>
              </div>

              {/* 5. Code Examples & Real-World Usage */}
              {module.code_examples && module.code_examples.length > 0 && (
                <div id="examples" className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
                  <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                    <Code className="w-4 h-4 text-blue-700" />
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Practical Code & Implementation Examples
                    </h3>
                  </div>
                  <div className="space-y-4">
                    {module.code_examples.map((ex, idx) => (
                      <div key={idx} className="space-y-1.5">
                        <h4 className="text-xs font-bold text-slate-800">{ex.title}</h4>
                        <MarkdownMathRenderer
                          content={`\`\`\`${ex.language || 'python'}\n${ex.code}\n\`\`\``}
                        />
                        {ex.explanation && (
                          <p className="text-xs text-slate-600 italic leading-relaxed">
                            {ex.explanation}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 6. Governing Rules & Common Mistakes */}
              <div id="rules-mistakes" className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Governing Rules */}
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-600" />
                    Governing Best Practices
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-700">
                    {parseStringList(module.key_rules).map((rule, idx) => (
                      <li key={idx} className="flex items-start gap-2 bg-emerald-50/50 p-2.5 rounded-xl border border-emerald-100">
                        <Check className="w-3.5 h-3.5 text-emerald-700 shrink-0 mt-0.5" />
                        <span>{rule}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Common Pitfalls */}
                <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs space-y-3">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                    <AlertTriangle className="w-4 h-4 text-rose-600" />
                    Common Industry Mistakes & Pitfalls
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-700">
                    {parseStringList(module.common_mistakes).map((mistake, idx) => (
                      <li key={idx} className="flex items-start gap-2 bg-rose-50/50 p-2.5 rounded-xl border border-rose-100">
                        <XCircle className="w-3.5 h-3.5 text-rose-700 shrink-0 mt-0.5" />
                        <span>{mistake}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* 7. Quick Reference Revision Sheet */}
              {module.quick_reference && (
                <div id="quick-ref" className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
                  <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
                    <FileText className="w-4 h-4 text-blue-700" />
                    <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Quick Reference Revision Sheet
                    </h3>
                  </div>

                  {module.quick_reference.key_terms && (
                    <div className="space-y-2">
                      <span className="text-[11px] font-bold text-slate-700 block uppercase tracking-wider">
                        Key Definitions
                      </span>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                        {module.quick_reference.key_terms.map((item, i) => (
                          <div key={i} className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                            <span className="font-bold text-blue-900 block">{item.term}</span>
                            <span className="text-slate-600 text-[11px] leading-relaxed block">{item.definition}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {module.quick_reference.takeaways && (
                    <div className="space-y-2 pt-2">
                      <span className="text-[11px] font-bold text-slate-700 block uppercase tracking-wider">
                        Core Takeaways
                      </span>
                      <ul className="space-y-1.5 text-xs text-slate-700">
                        {module.quick_reference.takeaways.map((takeaway, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0 mt-0.5" />
                            <span>{takeaway}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* 8. Verified Authoritative External Learning References */}
              <div id="resources" className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-blue-700" />
                    <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Verified External References for Deeper Learning
                    </h4>
                  </div>
                  <span className="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    Role Aligned
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
                        className="group flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 bg-slate-50 hover:bg-blue-50/50 border border-slate-200 hover:border-blue-300 rounded-xl transition-all"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
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
                          <h5 className="text-xs font-bold text-slate-900 group-hover:text-blue-800 flex items-center gap-1.5">
                            <span>{res.title}</span>
                          </h5>
                        </div>

                        <div className="flex items-center gap-3 shrink-0 self-start sm:self-auto text-xs text-slate-500">
                          <span className="inline-flex items-center gap-1 font-mono text-[11px]">
                            <Clock className="w-3 h-3 text-slate-400" />
                            {res.estimated_minutes} min
                          </span>
                          <span className="inline-flex items-center gap-1 text-blue-700 group-hover:translate-x-0.5 transition-transform font-bold text-xs">
                            <span>Read Resource</span>
                            <ExternalLink className="w-3.5 h-3.5" />
                          </span>
                        </div>
                      </a>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl text-center text-xs text-slate-500 italic">
                    Verified external references are being cataloged for this topic.
                  </div>
                )}
              </div>

              {/* 9. Adaptive Next Action Card */}
              {module.adaptive_next_action && (
                <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-6 shadow-md flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-blue-200 bg-blue-800/60 px-2 py-0.5 rounded">
                      Adaptive Recommendation
                    </span>
                    <h4 className="text-base font-bold">
                      {module.adaptive_next_action.label}
                    </h4>
                    <p className="text-xs text-blue-100/90 leading-relaxed max-w-xl">
                      {module.adaptive_next_action.description}
                    </p>
                  </div>

                  <button
                    onClick={() => {
                      const targetTab = module.adaptive_next_action?.target_tab as TabType;
                      if (targetTab) {
                        setActiveTab(targetTab);
                      } else {
                        router.push('/roadmap');
                      }
                    }}
                    className="px-5 py-2.5 rounded-xl font-bold text-xs bg-white text-blue-950 hover:bg-blue-50 transition-colors shadow-sm shrink-0 flex items-center gap-2 cursor-pointer"
                  >
                    <span>Proceed to Next Step</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: WORKED EXAMPLE (Realistic Scenario & Step Reasoning)              */}
        {/* ========================================================================= */}
        {activeTab === 'EXAMPLE' && module.worked_example && (
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-xs space-y-5">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded border border-blue-200">
                  Real-World Production Problem
                </span>
                <h3 className="text-lg font-bold text-slate-900 mt-1.5">
                  {module.worked_example.title || `${module.title} — Production Case Study`}
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {module.worked_example.scenario}
                </p>
              </div>

              {/* Code / Query Block */}
              <div>
                <div className="flex items-center justify-between text-xs font-mono text-slate-400 bg-slate-900 px-4 py-2.5 rounded-t-xl">
                  <span>PRODUCTION SOLUTION PATTERN</span>
                  <span>SQL / PYTHON</span>
                </div>
                <pre className="bg-slate-950 text-emerald-300/90 font-mono text-xs p-4 rounded-b-xl overflow-x-auto leading-relaxed border border-slate-800">
                  {module.worked_example.code_or_query || module.worked_example.code || '-- No code snippet provided'}
                </pre>
              </div>

              {/* Reasoning */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-1.5">
                <h4 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <Lightbulb className="w-4 h-4 text-amber-600" />
                  Step-by-Step Execution Rationale
                </h4>
                <div className="text-xs text-slate-700 leading-relaxed font-sans">
                  <MarkdownMathRenderer
                    content={module.worked_example.explanation || module.worked_example.reasoning || 'Follow the production pattern to ensure verified outcomes.'}
                  />
                </div>
              </div>

              {/* Expected Output */}
              <div className="bg-blue-50/50 border border-blue-200/60 rounded-xl p-4 space-y-1.5">
                <h4 className="text-xs font-bold text-blue-900">
                  Expected Output & Metric Verification
                </h4>
                <div className="text-xs font-mono text-slate-800 leading-relaxed bg-white p-3 rounded-lg border border-blue-100">
                  <MarkdownMathRenderer
                    content={module.worked_example.output || module.worked_example.expected_output || 'Output matches verified assertions.'}
                  />
                </div>
              </div>
            </div>

            {/* Advance Footer */}
            <div className="flex items-center justify-between pt-2">
              <button
                onClick={() => setActiveTab('LEARN')}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50"
              >
                Back to Explanation
              </button>
              <button
                onClick={() => setActiveTab('PRACTICE')}
                className="px-5 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 rounded-xl shadow-2xs flex items-center gap-2 cursor-pointer transition-colors"
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
            <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl w-fit border border-slate-200">
              <button
                onClick={() => handleSwitchPracticeType('GUIDED')}
                className={`px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  practiceType === 'GUIDED'
                    ? 'bg-white text-blue-900 shadow-2xs border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Guided Practice (With Scaffolding)
              </button>
              <button
                onClick={() => handleSwitchPracticeType('INDEPENDENT')}
                className={`px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all cursor-pointer ${
                  practiceType === 'INDEPENDENT'
                    ? 'bg-white text-blue-900 shadow-2xs border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Independent Practice (No Assistance)
              </button>
            </div>

            {/* Prompt & Instructions */}
            <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-xs space-y-4">
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
                  className="w-full font-mono text-xs p-4 bg-slate-950 text-slate-100 rounded-xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent leading-relaxed"
                />
              </div>

              {/* Hints Box (for guided) */}
              {practiceType === 'GUIDED' && (
                (() => {
                  const hintsList = parseStringList(module.guided_practice?.hints);
                  if (hintsList.length === 0) return null;
                  return (
                    <div className="bg-amber-50/50 border border-amber-200/70 rounded-xl p-4 space-y-2">
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
                            <p key={i} className="text-xs text-amber-900 bg-white/80 p-2.5 rounded-lg border border-amber-200">
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
                <div className={`p-4 rounded-xl border text-xs ${
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
                  className="px-3.5 py-2 text-xs font-semibold text-blue-700 hover:text-blue-900 inline-flex items-center gap-1"
                >
                  <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                  <span>Ask Coach for Debug Advice</span>
                </button>

                <div className="flex items-center gap-3">
                  <button
                    onClick={handleSubmitPractice}
                    disabled={isSubmittingPractice || !practiceCode.trim()}
                    className="px-5 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 disabled:bg-slate-300 rounded-xl shadow-2xs flex items-center gap-1.5 cursor-pointer transition-colors"
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
                    className="px-4 py-2.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl flex items-center gap-1.5 cursor-pointer"
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
            <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-xs space-y-6">
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
                      className="p-5 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-3"
                    >
                      <h4 className="text-xs font-bold text-slate-900 flex items-start gap-2">
                        <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center text-[10px] shrink-0 mt-0.5 font-bold">
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
                              className={`flex items-start gap-3 p-3 rounded-xl border text-xs cursor-pointer transition-all ${optionStyle}`}
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
                        <div className="mt-2 pl-7 text-xs text-slate-600 bg-white p-3 rounded-xl border border-slate-200">
                          <span className="font-bold text-slate-800">Explanation: </span>
                          <MarkdownMathRenderer content={qResult.explanation} />
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Quiz Result Banner */}
              {quizResult && (
                <div className={`p-5 rounded-2xl border text-xs space-y-2 ${
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
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50"
                >
                  Back to Practice
                </button>
                <div className="flex items-center gap-3">
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={isSubmittingQuiz || Object.keys(quizAnswers).length === 0}
                    className="px-5 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 disabled:bg-slate-300 rounded-xl shadow-2xs flex items-center gap-2 cursor-pointer transition-colors"
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
                    className="px-4 py-2.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl flex items-center gap-1.5 cursor-pointer"
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
            <div className="bg-white border border-slate-200 rounded-2xl p-6 md:p-8 shadow-xs space-y-6">
              <div>
                <div className="flex items-center gap-2 text-xs font-bold text-blue-700 uppercase tracking-wider mb-1">
                  <Briefcase className="w-4 h-4" />
                  <span>Target Role Deliverable</span>
                  <span className="text-slate-300">•</span>
                  <span className="text-slate-600">
                    {module.applied_task.role_relevance || module.applied_task.role_scenario || `Role Relevance: ${activeRoleName}`}
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
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Task Specification & Prompt
                </h4>
                <p className="text-xs text-slate-800 font-mono bg-white p-3 rounded-lg border border-slate-200 leading-relaxed whitespace-pre-wrap">
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
                        <div key={idx} className="flex items-start gap-2 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
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
                  className="w-full font-mono text-xs p-3.5 bg-slate-950 text-slate-100 rounded-xl border border-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent leading-relaxed"
                />
              </div>

              {/* Applied Feedback */}
              {appliedResult && (
                <div className={`p-4 rounded-xl border text-xs ${
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
                  className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:bg-slate-50"
                >
                  Back to Concept Check
                </button>
                <button
                  onClick={handleSubmitAppliedTask}
                  disabled={isSubmittingApplied || !appliedText.trim()}
                  className="px-5 py-2.5 text-xs font-bold text-white bg-blue-800 hover:bg-blue-900 disabled:bg-slate-300 rounded-xl shadow-2xs flex items-center gap-2 cursor-pointer transition-colors"
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
          <div className="bg-white border border-slate-200 rounded-xl p-12 shadow-sm max-w-sm w-full">
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
