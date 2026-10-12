'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AppShell } from '../../../components/AppShell';
import {
  api,
  ApiAssessmentDetail,
  ApiAssessmentResult,
  ApiSingleQuestionAnswer,
  ApiQuestionReviewResult,
  ApiAIExplainMistakeResponse,
} from '../../../services/api';
import {
  FileCheck2,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  XCircle,
  AlertCircle,
  HelpCircle,
  RotateCcw,
  BarChart3,
  ListTodo,
  Sparkles,
  X,
  Loader2,
} from 'lucide-react';

function TakeAssessmentContent() {
  const params = useParams();
  const router = useRouter();
  const assessmentId = Number(params?.id);

  const [assessment, setAssessment] = useState<ApiAssessmentDetail | null>(null);
  const [answersMap, setAnswersMap] = useState<Record<number, string>>({});
  const [currentQIndex, setCurrentQIndex] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ApiAssessmentResult | null>(null);

  // Phase 11 — Gemini AI Mistake Explanation
  const [selectedMistakeQ, setSelectedMistakeQ] = useState<ApiQuestionReviewResult | null>(null);
  const [mistakeExplanation, setMistakeExplanation] = useState<ApiAIExplainMistakeResponse | null>(null);
  const [isLoadingMistake, setIsLoadingMistake] = useState<boolean>(false);

  const handleExplainAssessmentMistake = async (q: ApiQuestionReviewResult) => {
    setSelectedMistakeQ(q);
    setMistakeExplanation(null);
    setIsLoadingMistake(true);
    try {
      const res = await api.explainMistake({
        skill_name: result?.skill_name || assessment?.skill_name || 'Core Skill',
        task_or_question: q.question_text,
        learner_answer: q.user_answer,
        correct_answer_or_result: q.correct_answer,
        deterministic_evaluation: 'INCORRECT',
        target_role: 'Data Analyst',
      });
      setMistakeExplanation(res);
    } catch (err) {
      console.error('Failed to get mistake explanation:', err);
    } finally {
      setIsLoadingMistake(false);
    }
  };

  useEffect(() => {
    if (assessmentId) {
      loadAssessment();
    }
  }, [assessmentId]);

  const loadAssessment = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getAssessmentDetail(assessmentId);
      setAssessment(data);
    } catch (err: any) {
      console.error('Failed to load assessment detail:', err);
      setError(err?.message || 'Failed to load assessment details from server.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectOption = (questionId: number, optionText: string) => {
    if (result || isSubmitting) return; // Read-only if already submitted
    setAnswersMap((prev) => ({
      ...prev,
      [questionId]: optionText,
    }));
  };

  const handleSubmit = async () => {
    if (!assessment || isSubmitting) return;

    setIsSubmitting(true);
    setError(null);

    const answersPayload: ApiSingleQuestionAnswer[] = assessment.questions.map((q) => ({
      question_id: q.id,
      answer: answersMap[q.id] || '',
    }));

    try {
      const resultData = await api.submitAssessment({
        user_id: 1, // Alex Mercer demo learner
        assessment_id: assessment.id,
        answers: answersPayload,
      });

      setResult(resultData);
    } catch (err: any) {
      console.error('Failed to submit assessment attempt:', err);
      setError(err?.message || 'Failed to calculate score server-side.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setResult(null);
    setAnswersMap({});
    setCurrentQIndex(0);
  };

  if (isLoading) {
    return (
      <AppShell>
        <div className="bg-white border border-slate-200 rounded-lg p-16 text-center shadow-sm my-8">
          <div className="inline-block w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
          <h2 className="text-lg font-bold text-slate-800">Loading Diagnostic Questions...</h2>
          <p className="text-xs text-slate-500 mt-1">Preparing deterministic assessment environment.</p>
        </div>
      </AppShell>
    );
  }

  if (error && !assessment) {
    return (
      <AppShell>
        <div className="bg-white border border-slate-200 rounded-lg p-8 shadow-sm text-center my-8">
          <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto mb-3">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 mb-2">Unable to Load Assessment</h2>
          <p className="text-xs text-slate-500 mb-6">{error}</p>
          <button
            onClick={() => router.push('/assessments')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded hover:bg-slate-800"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Assessments
          </button>
        </div>
      </AppShell>
    );
  }

  if (!assessment) return null;

  const currentQ = assessment.questions[currentQIndex];
  const totalQuestions = assessment.questions.length;
  const answeredCount = Object.keys(answersMap).length;
  const progressPercent = Math.round(((currentQIndex + 1) / totalQuestions) * 100);

  // Interpretation colors
  const getInterpretationStyle = (interp: string) => {
    switch (interp) {
      case 'Strong':
        return 'bg-emerald-50 border-emerald-200 text-emerald-800';
      case 'Healthy':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'Developing':
        return 'bg-amber-50 border-amber-200 text-amber-800';
      case 'Critical Gap':
      default:
        return 'bg-rose-50 border-rose-200 text-rose-800';
    }
  };

  return (
    <AppShell>
      {/* Top Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => router.push('/assessments')}
            className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-slate-900 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Assessments
          </button>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">{assessment.title}</h1>
          <p className="text-xs text-slate-500 mt-1">
            Skill Assessed: <strong className="text-slate-700">{assessment.skill_name || 'Technical Skill'}</strong> • Difficulty: {assessment.difficulty}
          </p>
        </div>

        {!result && (
          <div className="flex items-center gap-3 bg-slate-50 px-4 py-3 rounded border border-slate-200 shrink-0">
            <div className="text-right">
              <div className="text-xs font-semibold text-slate-500">Progress</div>
              <div className="text-sm font-bold text-slate-900">
                {answeredCount} / {totalQuestions} Answered
              </div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 rounded-lg p-4 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* ========================================================= */}
      {/* RESULT SCREEN VIEW (After submission)                     */}
      {/* ========================================================= */}
      {result ? (
        <div className="space-y-6">
          {/* Main Score Banner */}
          <div className={`border rounded-lg p-6 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6 ${getInterpretationStyle(result.interpretation)}`}>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-white border border-slate-200 flex items-center justify-center shrink-0 shadow-xs">
                <span className="text-2xl font-extrabold text-slate-900">{Math.round(result.percentage)}%</span>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold uppercase tracking-wide px-2.5 py-0.5 rounded bg-white/80 border border-current">
                    {result.interpretation}
                  </span>
                  <span className="text-xs text-slate-600">Deterministic Score</span>
                </div>
                <h2 className="text-lg font-bold text-slate-900 mt-1">
                  {result.raw_score} of {result.total_questions} Questions Correct
                </h2>
                <p className="text-xs text-slate-600 mt-0.5">
                  Demonstrated Accuracy: {result.accuracy.toFixed(1)}% • Completed {new Date(result.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 w-full md:w-auto">
              <button
                onClick={handleRetake}
                className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white text-slate-800 font-semibold text-xs rounded border border-slate-300 hover:bg-slate-50 min-h-[44px]"
              >
                <RotateCcw className="w-4 h-4" /> Retake Assessment
              </button>
              <button
                onClick={() => router.push('/skill-dna')}
                className="flex-1 md:flex-initial inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-900 text-white font-semibold text-xs rounded hover:bg-slate-800 min-h-[44px]"
              >
                <BarChart3 className="w-4 h-4" /> View Skill DNA
              </button>
            </div>
          </div>

          {/* Detailed Question Review Breakdown */}
          <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100">
              <ListTodo className="w-5 h-5 text-blue-600" />
              <h3 className="text-base font-bold text-slate-900">Question Review & Explanations</h3>
            </div>

            <div className="space-y-4">
              {result.question_breakdown.map((q, idx) => (
                <div
                  key={q.question_id}
                  className={`p-4 rounded-lg border text-xs transition-colors ${
                    q.is_correct
                      ? 'bg-emerald-50/50 border-emerald-200'
                      : 'bg-rose-50/50 border-rose-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex items-start gap-2">
                      <span className="font-bold text-slate-700">Q{idx + 1}.</span>
                      <p className="font-semibold text-slate-900 text-sm">{q.question_text}</p>
                    </div>
                    {q.is_correct ? (
                      <span className="inline-flex items-center gap-1 text-emerald-700 font-bold bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300 shrink-0">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Correct
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-rose-700 font-bold bg-rose-100 px-2 py-0.5 rounded border border-rose-300 shrink-0">
                        <XCircle className="w-3.5 h-3.5" /> Incorrect
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-3 pt-3 border-t border-slate-200/60">
                    <div>
                      <span className="text-slate-500 font-medium">Your Answer:</span>
                      <p className={`font-semibold mt-0.5 ${q.is_correct ? 'text-emerald-800' : 'text-rose-800'}`}>
                        {q.user_answer}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-500 font-medium">Correct Answer:</span>
                      <p className="font-semibold text-slate-900 mt-0.5">{q.correct_answer}</p>
                    </div>
                  </div>

                  {q.explanation && (
                    <div className="mt-3 pt-2 text-slate-600 bg-white/80 p-2.5 rounded border border-slate-200/60 flex items-start gap-2">
                      <HelpCircle className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-slate-800 font-semibold">Explanation:</strong> {q.explanation}
                      </div>
                    </div>
                  )}

                  {!q.is_correct && (
                    <div className="mt-3 pt-2 flex items-center justify-end">
                      <button
                        onClick={() => handleExplainAssessmentMistake(q)}
                        className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded border border-indigo-200 transition-colors cursor-pointer"
                      >
                        <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
                        <span>Explain My Mistake (AI Coach)</span>
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* ========================================================= */
        /* ASSESSMENT TAKING INTERFACE                               */
        /* ========================================================= */
        <div className="space-y-6">
          {/* Progress Bar & Question Navigator */}
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-600">
              <span>Question {currentQIndex + 1} of {totalQuestions}</span>
              <span>{progressPercent}% Complete</span>
            </div>

            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className="bg-blue-600 h-2 transition-all duration-300 rounded-full"
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>

            {/* Question Quick-Jump Grid */}
            <div className="flex flex-wrap items-center gap-1.5 pt-2">
              {assessment.questions.map((q, idx) => {
                const isAnswered = !!answersMap[q.id];
                const isCurrent = idx === currentQIndex;

                let btnStyle = 'bg-slate-100 text-slate-600 hover:bg-slate-200';
                if (isCurrent) {
                  btnStyle = 'bg-blue-600 text-white ring-2 ring-blue-300 font-bold';
                } else if (isAnswered) {
                  btnStyle = 'bg-emerald-100 text-emerald-800 font-semibold border border-emerald-300';
                }

                return (
                  <button
                    key={q.id}
                    onClick={() => setCurrentQIndex(idx)}
                    className={`w-8 h-8 rounded text-xs transition-all flex items-center justify-center ${btnStyle}`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Current Question Card */}
          <div className="bg-white border border-slate-200 rounded-lg p-5 sm:p-8 shadow-sm space-y-6">
            <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Question {currentQIndex + 1}
              </span>
              <span className="text-xs font-semibold bg-slate-100 px-2.5 py-1 rounded text-slate-600 border border-slate-200">
                Difficulty: {currentQ.difficulty}
              </span>
            </div>

            <h3 className="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
              {currentQ.question_text}
            </h3>

            {/* Answer Choice Buttons */}
            <div className="space-y-3 pt-2">
              {currentQ.options.map((optionText, optIdx) => {
                const letter = String.fromCharCode(65 + optIdx); // A, B, C, D
                const isSelected = answersMap[currentQ.id] === optionText || answersMap[currentQ.id] === letter;

                return (
                  <button
                    key={optIdx}
                    onClick={() => handleSelectOption(currentQ.id, optionText)}
                    className={`w-full text-left p-4 rounded-lg border text-sm font-medium transition-all flex items-center gap-3.5 min-h-[52px] cursor-pointer ${
                      isSelected
                        ? 'bg-blue-50 border-blue-600 text-blue-950 ring-2 ring-blue-500/20 shadow-xs'
                        : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-800'
                    }`}
                  >
                    <span
                      className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs shrink-0 transition-colors ${
                        isSelected
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-100 text-slate-600 border border-slate-200'
                      }`}
                    >
                      {letter}
                    </span>
                    <span className="flex-1">{optionText}</span>
                  </button>
                );
              })}
            </div>

            {/* Navigation & Submit Bar */}
            <div className="flex items-center justify-between border-t border-slate-100 pt-6 gap-3 flex-wrap">
              <button
                onClick={() => setCurrentQIndex((prev) => Math.max(0, prev - 1))}
                disabled={currentQIndex === 0}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded text-xs font-semibold border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed min-h-[44px]"
              >
                <ArrowLeft className="w-4 h-4" /> Previous
              </button>

              <div className="flex items-center gap-3">
                {currentQIndex < totalQuestions - 1 ? (
                  <button
                    onClick={() => setCurrentQIndex((prev) => Math.min(totalQuestions - 1, prev + 1))}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 shadow-sm min-h-[44px]"
                  >
                    Next Question <ArrowRight className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className="inline-flex items-center gap-2 px-6 py-2.5 rounded text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-sm disabled:opacity-50 min-h-[44px]"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Calculating Score...
                      </>
                    ) : (
                      <>
                        <FileCheck2 className="w-4 h-4" /> Submit Assessment
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Phase 11 AI Mistake Explanation Modal */}
      {selectedMistakeQ && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden animate-in fade-in duration-150">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-indigo-50/70">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">
                    AI Mistake Analysis
                  </h3>
                  <p className="text-[11px] text-indigo-700">
                    Deterministic evaluation verified • Non-overriding AI diagnostic
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedMistakeQ(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-5 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
              <div className="p-3 rounded bg-slate-50 border border-slate-200 space-y-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Question</span>
                <p className="text-slate-800 font-semibold">{selectedMistakeQ.question_text}</p>
                <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200 mt-2">
                  <div>
                    <span className="text-[10px] text-rose-600 font-bold uppercase block">Your Answer</span>
                    <p className="font-medium text-rose-800">{selectedMistakeQ.user_answer}</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-emerald-600 font-bold uppercase block">Correct Answer</span>
                    <p className="font-medium text-emerald-800">{selectedMistakeQ.correct_answer}</p>
                  </div>
                </div>
              </div>

              {isLoadingMistake && (
                <div className="py-8 flex flex-col items-center justify-center text-center space-y-2">
                  <Loader2 className="w-6 h-6 text-indigo-600 animate-spin" />
                  <p className="text-xs font-semibold text-slate-700">
                    AI Coach is analyzing what went wrong...
                  </p>
                </div>
              )}

              {mistakeExplanation && (
                <div className="space-y-3">
                  <div className="p-3 rounded bg-rose-50 border border-rose-200 text-rose-950 space-y-1">
                    <span className="font-bold block text-rose-800">What went wrong:</span>
                    <p>{mistakeExplanation.what_went_wrong}</p>
                  </div>

                  <div className="p-3 rounded bg-amber-50 border border-amber-200 text-amber-950 space-y-1">
                    <span className="font-bold block text-amber-800">Why it happened:</span>
                    <p>{mistakeExplanation.why_it_happened}</p>
                  </div>

                  <div className="p-3 rounded bg-blue-50 border border-blue-200 text-blue-950 space-y-1">
                    <span className="font-bold block text-blue-800">How to recognize next time:</span>
                    <p>{mistakeExplanation.how_to_recognize_next_time}</p>
                  </div>

                  {mistakeExplanation.small_example && (
                    <div className="space-y-1">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                        Correct Pattern Example
                      </span>
                      <pre className="p-2.5 rounded bg-slate-900 text-emerald-400 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">
                        {mistakeExplanation.small_example}
                      </pre>
                    </div>
                  )}

                  {mistakeExplanation.short_practice_question && (
                    <div className="p-3 rounded bg-purple-50 border border-purple-200 text-purple-950 space-y-1">
                      <span className="font-bold block text-purple-800">Quick Practice Check (Unscored):</span>
                      <p className="italic">{mistakeExplanation.short_practice_question}</p>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="p-3.5 border-t border-slate-200 bg-slate-50 flex justify-end">
              <button
                onClick={() => setSelectedMistakeQ(null)}
                className="px-4 py-1.5 rounded-md bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold cursor-pointer shadow-xs"
              >
                Got It
              </button>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}

export default function TakeAssessmentPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 text-center">
          <div className="bg-white border border-slate-200 rounded-lg p-12 shadow-sm max-w-sm w-full">
            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-sm font-semibold text-slate-800">Loading Assessment Environment...</p>
          </div>
        </div>
      }
    >
      <TakeAssessmentContent />
    </Suspense>
  );
}


