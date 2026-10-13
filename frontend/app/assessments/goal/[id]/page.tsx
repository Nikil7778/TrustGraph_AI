'use client';

import React, { useEffect, useState, Suspense } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { AppShell } from '../../../../components/AppShell';
import { useLearner } from '../../../../context/LearnerContext';
import {
  api,
  ApiAssessmentDetail,
  ApiGoalAssessmentResultResponse,
  ApiSingleQuestionAnswer,
  ApiQuestionReviewResult,
} from '../../../../services/api';
import {
  Compass,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Clock,
  Sparkles,
  BarChart3,
  Award,
  Zap,
  HelpCircle,
  Layers,
  Check,
  ChevronRight,
  Loader2,
  Target,
} from 'lucide-react';

function GoalAssessmentContent() {
  const params = useParams();
  const router = useRouter();
  const { activeUserId, refreshUser } = useLearner();
  const roleId = Number(params?.id);

  const [assessment, setAssessment] = useState<ApiAssessmentDetail | null>(null);
  const [answersMap, setAnswersMap] = useState<Record<number, string>>({});
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ApiGoalAssessmentResultResponse | null>(null);

  useEffect(() => {
    if (roleId) {
      loadAssessment();
    }
  }, [roleId]);

  const loadAssessment = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getGoalAssessment(roleId);
      setAssessment(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load goal assessment.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectOption = (questionId: number, optionText: string) => {
    if (result || isSubmitting) return;
    setAnswersMap((prev) => ({
      ...prev,
      [questionId]: optionText,
    }));
  };

  const handleSubmit = async () => {
    if (!assessment || isSubmitting || !activeUserId) return;

    const answers: ApiSingleQuestionAnswer[] = Object.entries(answersMap).map(([qId, ans]) => ({
      question_id: Number(qId),
      answer: ans,
    }));

    if (answers.length === 0) {
      setError('Please answer at least one question before submitting your assessment.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const res = await api.submitGoalAssessment({
        user_id: activeUserId,
        role_id: roleId,
        answers,
      });
      setResult(res);
      await refreshUser();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Submission failed. Please try again.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <AppShell>
        <div className="min-h-[500px] flex flex-col items-center justify-center p-8 text-center space-y-4">
          <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
          <h2 className="text-lg font-bold text-slate-800">Preparing Goal Diagnostic Assessment...</h2>
          <p className="text-xs text-slate-500 max-w-sm">
            Synthesizing benchmark questions for target competencies and skill map analysis.
          </p>
        </div>
      </AppShell>
    );
  }

  if (error && !assessment) {
    return (
      <AppShell>
        <div className="max-w-xl mx-auto my-12 p-8 bg-rose-50 border border-rose-200 rounded-xl text-center space-y-4">
          <AlertCircle className="w-10 h-10 text-rose-600 mx-auto" />
          <h2 className="text-lg font-bold text-rose-900">Assessment Error</h2>
          <p className="text-xs text-rose-700">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-slate-900 text-white rounded-md text-xs font-semibold hover:bg-slate-800"
          >
            Return to Dashboard
          </button>
        </div>
      </AppShell>
    );
  }

  // =========================================================================
  // VIEW: POST-SUBMISSION DETAILED SKILL-LEVEL ANALYSIS & GAP REPORT
  // =========================================================================
  if (result) {
    const nextAction = result.next_recommended_action;

    return (
      <AppShell>
        <div className="max-w-5xl mx-auto space-y-6 pb-12 antialiased">
          {/* Header Banner */}
          <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 text-white p-6 sm:p-8 rounded-2xl shadow-sm relative overflow-hidden">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
              <div className="space-y-2">
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-500/20 text-blue-300 text-xs font-semibold border border-blue-400/30">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" /> Goal Diagnostic Completed
                </div>
                <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
                  Skill-Level Analysis Report
                </h1>
                <p className="text-sm text-slate-300 max-w-xl">
                  Benchmark diagnostics for <strong className="text-white">{result.role_name}</strong>.
                  Your demonstrated skill levels have updated your live Skill DNA and identified your primary skill gaps.
                </p>
              </div>

              <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/10 flex items-center gap-6 shrink-0">
                <div className="text-center">
                  <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block">Overall Score</span>
                  <span className="text-3xl font-black text-white">{Math.round(result.overall_score)}%</span>
                </div>
                <div className="h-10 w-[1px] bg-white/20" />
                <div className="text-center">
                  <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block">Accuracy</span>
                  <span className="text-3xl font-black text-emerald-400">
                    {result.correct_questions}/{result.total_questions}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Central Highlight: "What should I do next?" (SECTION 15 MANDATE) */}
          {nextAction && (
            <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-2 border-amber-500/30 rounded-2xl p-6 sm:p-7 shadow-xs">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded bg-amber-600 text-white text-[11px] font-black uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" /> What Should I Do Next?
                    </span>
                    <span className="text-xs font-bold text-amber-700">Central Action Recommendation</span>
                  </div>
                  <h2 className="text-xl sm:text-2xl font-bold text-slate-900">
                    {nextAction.title}
                  </h2>
                  <p className="text-xs sm:text-sm text-slate-700 leading-relaxed max-w-2xl">
                    {nextAction.reason}
                  </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 shrink-0">
                  <button
                    onClick={() => router.push('/')}
                    className="inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition-all"
                  >
                    Proceed to Dashboard
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* SECTION 4: SKILL GAP VISUAL BREAKDOWN (Strong, Moderate, Weak, Missing) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Strong */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">Strong Skills</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                  {result.strong_skills.length}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Mastered or meets required benchmark level (≥75%)</p>
              <div className="space-y-1.5 pt-2">
                {result.strong_skills.length === 0 ? (
                  <span className="text-xs text-slate-400 italic">No skills at strong level yet</span>
                ) : (
                  result.strong_skills.map((s) => (
                    <div key={s} className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                      <span>{s}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Moderate */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-700">Moderate Skills</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                  {result.moderate_skills.length}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Developing competency with minor remaining gap (50–74%)</p>
              <div className="space-y-1.5 pt-2">
                {result.moderate_skills.length === 0 ? (
                  <span className="text-xs text-slate-400 italic">No moderate skills</span>
                ) : (
                  result.moderate_skills.map((s) => (
                    <div key={s} className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                      <div className="w-2 h-2 rounded-full bg-blue-500 shrink-0" />
                      <span>{s}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Weak */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-700">Weak Skills</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                  {result.weak_skills.length}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Requires targeted practice and remediation (&lt;50%)</p>
              <div className="space-y-1.5 pt-2">
                {result.weak_skills.length === 0 ? (
                  <span className="text-xs text-slate-400 italic">No weak skills</span>
                ) : (
                  result.weak_skills.map((s) => (
                    <div key={s} className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                      <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                      <span>{s}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Missing */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-rose-700">Missing Skills</span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-rose-100 text-rose-800">
                  {result.missing_skills.length}
                </span>
              </div>
              <p className="text-[11px] text-slate-500">Untested or unstarted goal prerequisites (0%)</p>
              <div className="space-y-1.5 pt-2">
                {result.missing_skills.length === 0 ? (
                  <span className="text-xs text-slate-400 italic">No missing skills</span>
                ) : (
                  result.missing_skills.map((s) => (
                    <div key={s} className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                      <div className="w-2 h-2 rounded-full bg-rose-400 shrink-0" />
                      <span>{s}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* SECTION 3: GRANULAR SKILL-LEVEL ANALYSIS LIST */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
            <div className="p-5 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" /> Granular Skill-Level Score Analysis
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Individual score calculated for every skill competency (Requirement: do not simply calculate one overall score).
                </p>
              </div>
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider hidden sm:inline">
                {result.skill_scores.length} Competencies Evaluated
              </span>
            </div>

            <div className="divide-y divide-slate-100">
              {result.skill_scores.map((s) => {
                const statusColors: Record<string, { badge: string; bar: string }> = {
                  Strong: { badge: 'bg-emerald-100 text-emerald-800 border-emerald-200', bar: 'bg-emerald-500' },
                  Moderate: { badge: 'bg-blue-100 text-blue-800 border-blue-200', bar: 'bg-blue-500' },
                  Weak: { badge: 'bg-amber-100 text-amber-800 border-amber-200', bar: 'bg-amber-500' },
                  Missing: { badge: 'bg-rose-100 text-rose-800 border-rose-200', bar: 'bg-rose-400' },
                };
                const color = statusColors[s.status] || statusColors.Missing;

                return (
                  <div key={s.skill_id} className="p-4 sm:p-5 hover:bg-slate-50/60 transition-colors">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-slate-900">{s.skill_name}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${color.badge}`}>
                            {s.status}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-500">{s.category}</span>
                      </div>

                      <div className="flex items-center gap-4 text-xs font-semibold">
                        <div>
                          <span className="text-slate-400">Current: </span>
                          <span className="font-bold text-slate-900">{Math.round(s.score)}%</span>
                        </div>
                        <div className="text-slate-300">/</div>
                        <div>
                          <span className="text-slate-400">Required: </span>
                          <span className="font-bold text-slate-700">{s.required_level}%</span>
                        </div>
                        <div className="text-slate-300">/</div>
                        <div>
                          <span className="text-slate-400">Gap: </span>
                          <span className={`font-bold ${s.gap > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                            {s.gap > 0 ? `-${Math.round(s.gap)}%` : 'Met'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar Stack */}
                    <div className="space-y-1">
                      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden flex">
                        <div
                          className={`h-full ${color.bar} transition-all duration-500`}
                          style={{ width: `${Math.min(100, Math.max(0, s.score))}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-[10px] text-slate-400 font-medium">
                        <span>
                          {s.questions_tested > 0
                            ? `${s.questions_correct}/${s.questions_tested} questions answered correctly`
                            : 'Untested in initial diagnostic'}
                        </span>
                        <span>Target: {s.required_level}%</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Question Breakdown with Explanations */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
            <div className="p-5 border-b border-slate-200 bg-slate-50/50">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-blue-600" /> Question Breakdown & Explanations
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Review your responses and learn from detailed explanations for each question.
              </p>
            </div>

            <div className="divide-y divide-slate-100 p-2 sm:p-4">
              {result.question_breakdown.map((q, idx) => (
                <div key={q.question_id} className="p-4 space-y-2.5">
                  <div className="flex items-start justify-between gap-3">
                    <span className="font-bold text-xs text-slate-500 shrink-0 mt-0.5">Q{idx + 1}.</span>
                    <p className="font-semibold text-xs sm:text-sm text-slate-900 flex-1">{q.question_text}</p>
                    {q.is_correct ? (
                      <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold flex items-center gap-1 shrink-0">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Correct
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-bold flex items-center gap-1 shrink-0">
                        <XCircle className="w-3 h-3 text-rose-600" /> Incorrect
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1">
                    <div className="p-2.5 rounded bg-slate-50 border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">Your Answer</span>
                      <span className={q.is_correct ? 'text-emerald-700 font-semibold' : 'text-rose-700 font-semibold'}>
                        {q.user_answer}
                      </span>
                    </div>
                    <div className="p-2.5 rounded bg-emerald-50/60 border border-emerald-200">
                      <span className="text-[10px] uppercase font-bold text-emerald-700 block mb-0.5">Correct Answer</span>
                      <span className="text-emerald-900 font-semibold">{q.correct_answer}</span>
                    </div>
                  </div>

                  {q.explanation && (
                    <div className="p-3 bg-blue-50/50 border border-blue-100 rounded-lg text-xs text-slate-700">
                      <strong className="text-blue-900 font-bold block mb-0.5">Explanation:</strong>
                      {q.explanation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Action Bar */}
          <div className="flex justify-end pt-4">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-lg shadow-sm transition-colors flex items-center gap-2"
            >
              Continue to Personalized Learning Workspace &rarr;
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  // =========================================================================
  // VIEW: TAKING DIAGNOSTIC ASSESSMENT
  // =========================================================================
  const questions = assessment?.questions || [];
  const currentQuestion = questions[currentIndex];
  const answeredCount = Object.keys(answersMap).length;
  const progressPercent = questions.length > 0 ? (answeredCount / questions.length) * 100 : 0;

  return (
    <AppShell>
      <div className="max-w-3xl mx-auto space-y-6 pb-12 antialiased">
        {/* Top Header Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-600 uppercase tracking-wider">
              <Compass className="w-4 h-4 text-blue-600" />
              <span>Initial Goal Diagnostic Assessment</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
              {assessment?.title || 'Goal Diagnostic'}
            </h1>
            <p className="text-xs text-slate-500">
              Evaluates core competencies across the target goal skill map to discover your skill gaps.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <div className="text-right">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Progress</span>
              <span className="text-sm font-black text-slate-900">
                {answeredCount} of {questions.length} Answered
              </span>
            </div>
          </div>
        </div>

        {/* Linear Progress Bar */}
        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
          <div
            className="bg-blue-600 h-full transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg flex items-start gap-3 text-xs text-rose-800">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Current Question Card */}
        {currentQuestion && (
          <div className="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
            <div className="p-6 sm:p-8 space-y-6">
              {/* Question Meta Badge */}
              <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                <span className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 text-xs font-bold border border-blue-200 flex items-center gap-1.5">
                  <Target className="w-3.5 h-3.5 text-blue-600" />
                  Testing Skill: {currentQuestion.skill_name || 'Core Skill'}
                </span>
                <span className="text-xs font-semibold text-slate-400">
                  Question {currentIndex + 1} of {questions.length}
                </span>
              </div>

              {/* Question Text */}
              <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                {currentQuestion.question_text}
              </h2>

              {/* Options List */}
              <div className="space-y-3 pt-2">
                {currentQuestion.options.map((opt, optIdx) => {
                  const isSelected = answersMap[currentQuestion.id] === opt;
                  const letter = String.fromCharCode(65 + optIdx);

                  return (
                    <div
                      key={optIdx}
                      onClick={() => handleSelectOption(currentQuestion.id, opt)}
                      className={`p-4 rounded-xl border cursor-pointer transition-all flex items-start gap-3 ${
                        isSelected
                          ? 'border-2 border-blue-600 bg-blue-50/50 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50/60'
                      }`}
                    >
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                          isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {isSelected ? <Check className="w-3.5 h-3.5" /> : letter}
                      </div>
                      <span className="text-xs sm:text-sm font-medium text-slate-800 leading-relaxed pt-0.5">
                        {opt}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Question Navigation Bar */}
            <div className="bg-slate-50/80 border-t border-slate-200 p-4 sm:p-6 flex items-center justify-between">
              <button
                type="button"
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
                className="inline-flex items-center gap-1.5 px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 disabled:opacity-40 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" /> Previous
              </button>

              <div className="flex items-center gap-3">
                {currentIndex < questions.length - 1 ? (
                  <button
                    type="button"
                    onClick={() => setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                    className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors"
                  >
                    Next Question <ArrowRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    type="button"
                    disabled={isSubmitting || answeredCount === 0}
                    onClick={handleSubmit}
                    className="inline-flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors disabled:opacity-50"
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Evaluating Skill DNA...
                      </>
                    ) : (
                      <>
                        Submit & Analyze Skill Gaps
                        <CheckCircle2 className="w-4 h-4" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Quick Question Jump Grid */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Question Palette
          </span>
          <div className="flex flex-wrap gap-2">
            {questions.map((q, qIdx) => {
              const isAnswered = Boolean(answersMap[q.id]);
              const isCurrent = qIdx === currentIndex;

              return (
                <button
                  key={q.id}
                  onClick={() => setCurrentIndex(qIdx)}
                  className={`w-8 h-8 rounded-lg text-xs font-bold transition-all ${
                    isCurrent
                      ? 'ring-2 ring-blue-600 ring-offset-1 bg-blue-600 text-white'
                      : isAnswered
                      ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {qIdx + 1}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

export default function GoalAssessmentPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 text-center">
          <div className="bg-white border border-slate-200 rounded-lg p-12 shadow-sm max-w-sm w-full">
            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-sm font-semibold text-slate-800">Loading Goal Assessment...</p>
          </div>
        </div>
      }
    >
      <GoalAssessmentContent />
    </Suspense>
  );
}
