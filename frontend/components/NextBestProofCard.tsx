'use client';

import React, { useState } from 'react';
import { NextBestProofAction } from '../types';
import { api, ApiNextBestProof, ApiAIExplainDecisionResponse } from '../services/api';
import { useLearner } from '../context/LearnerContext';
import {
  ShieldAlert,
  Clock,
  ArrowRight,
  Target,
  AlertCircle,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Sparkles,
  CheckCircle2,
  Layers,
  Check,
  TrendingUp,
  X,
  Loader2,
} from 'lucide-react';
import { SkillStatusBadge } from './SkillStatusBadge';
import { NextProofReadiness } from './NextProofReadiness';

interface NextBestProofCardProps {
  proof?: ApiNextBestProof | null;
  action?: NextBestProofAction;
  onStartAction?: () => void;
}

export const NextBestProofCard: React.FC<NextBestProofCardProps> = ({
  proof,
  action,
  onStartAction,
}) => {
  const { completeProof, activeUserId } = useLearner();
  const [showWhyThis, setShowWhyThis] = useState<boolean>(false);
  const [showPracticeModal, setShowPracticeModal] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [simulationScore, setSimulationScore] = useState<number>(85);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Phase 11 — Gemini AI Coach Explanation State
  const [aiExplanation, setAiExplanation] = useState<ApiAIExplainDecisionResponse | null>(null);
  const [isLoadingAI, setIsLoadingAI] = useState<boolean>(false);
  const [showAICoachView, setShowAICoachView] = useState<boolean>(false);

  // Derive display values from live `proof` (API) or fallback `action` (mock)
  const skillName = proof?.skill_name || action?.skillName || 'SQL JOINs';
  const actionTypeLabel = proof?.action_type_label || 'Targeted Practice';
  const title = proof?.title || action?.challengeTitle || 'SQL JOIN Rescue Practice';
  const currentLevel = proof
    ? Math.round(proof.current_skill_level)
    : action?.currentEvidence || 42;
  const targetLevel = proof
    ? Math.round(proof.required_skill_level)
    : action?.targetRequirement || 75;
  const estimatedTime = proof
    ? `${proof.estimated_minutes} min`
    : action?.estimatedEffort || '25 min';
  const priority = proof?.priority || action?.priority || 'CRITICAL';
  const expectedProof =
    proof?.expected_proof ||
    'Solve 8/10 targeted SQL JOINs problems across core difficulty scenarios.';
  const skillDebtStatus = proof?.skill_debt_status || 'SKILL_DEBT';
  const skillDebtScore = proof ? Math.round(proof.skill_debt_score) : 65;
  const careerValueScore = proof ? Math.round(proof.career_value_score) : 70;
  const primaryButtonLabel =
    proof?.action_type === 'PRACTICE'
      ? 'Start Practice'
      : proof?.action_type === 'REASSESS'
      ? 'Take Assessment'
      : proof?.action_type === 'PRACTICAL_TASK'
      ? 'Start Practical Task'
      : proof?.action_type === 'PROJECT'
      ? 'Launch Project'
      : proof?.action_type === 'LEARN'
      ? 'Begin Learning'
      : action?.primaryActionText || 'Start Practice';

  const handleStartProof = () => {
    if (onStartAction) {
      onStartAction();
    } else {
      setShowPracticeModal(true);
    }
  };

  const handleCompleteProof = async () => {
    if (!proof) {
      setShowPracticeModal(false);
      return;
    }
    setIsSubmitting(true);
    setSuccessMessage(null);
    try {
      await completeProof(
        proof.skill_id,
        proof.action_type,
        simulationScore,
        `Demonstrated ${expectedProof} with score ${simulationScore}%`,
        'Interactive Lab Simulation'
      );
      setSuccessMessage(
        `Proof verified! Evidence stored in Skill DNA, Skill Debt recalculated, and Next-Best-Proof updated.`
      );
      setTimeout(() => {
        setShowPracticeModal(false);
        setSuccessMessage(null);
      }, 1600);
    } catch (err) {
      console.error('Failed to complete proof:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <div className="bg-white border-2 border-slate-900 rounded-lg shadow-sm overflow-hidden">
        {/* Header bar */}
        <div className="bg-slate-900 text-white px-4 py-3 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-amber-400 shrink-0" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
              NEXT BEST PROOF
            </span>
            <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-400/40">
              {actionTypeLabel}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`text-xs font-bold px-2.5 py-0.5 rounded border shrink-0 ${
                priority === 'CRITICAL'
                  ? 'text-rose-300 bg-rose-950/80 border-rose-800'
                  : priority === 'HIGH'
                  ? 'text-amber-300 bg-amber-950/80 border-amber-800'
                  : 'text-blue-300 bg-blue-950/80 border-blue-800'
              }`}
            >
              Priority: {priority}
            </span>
          </div>
        </div>

        <div className="p-4 sm:p-5">
          {/* Main Title & Challenge info */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-100 pb-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">
                  Skill:
                </span>
                <h3 className="text-lg sm:text-xl font-black text-slate-900">{skillName}</h3>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300">
                  {skillDebtStatus === 'SKILL_DEBT' ? 'Skill Debt' : skillDebtStatus}
                </span>
              </div>
              <div className="text-xs sm:text-sm font-semibold text-slate-700 leading-snug flex items-center gap-1.5 flex-wrap">
                <span>Action:</span>
                <span className="text-blue-700 font-extrabold">{title}</span>
              </div>
              <div className="pt-1">
                <NextProofReadiness
                  userId={proof?.user_id || activeUserId || 1}
                  skillId={proof?.skill_id || 3}
                  skillName={skillName}
                  compact={true}
                />
              </div>
            </div>

            {/* Metric grid */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 sm:gap-3 text-xs bg-slate-50 p-3 rounded-md border border-slate-200 shrink-0">
              <div className="text-left">
                <span className="text-[10px] text-slate-500 block uppercase font-medium">Current</span>
                <span className="text-sm font-black text-rose-600">{currentLevel}%</span>
              </div>
              <div className="text-left border-l border-slate-300 pl-2 sm:pl-3">
                <span className="text-[10px] text-slate-500 block uppercase font-medium">Target</span>
                <span className="text-sm font-black text-slate-800">{targetLevel}%</span>
              </div>
              <div className="text-left border-l border-slate-300 pl-2 sm:pl-3">
                <span className="text-[10px] text-slate-500 block uppercase font-medium">Career Val</span>
                <span className="text-sm font-bold text-indigo-700">
                  {careerValueScore > 50 ? 'High' : 'Med'} ({careerValueScore})
                </span>
              </div>
              <div className="text-left border-l border-slate-300 pl-2 sm:pl-3">
                <span className="text-[10px] text-slate-500 block uppercase font-medium">Skill Debt</span>
                <span className="text-sm font-bold text-amber-700">
                  {skillDebtScore > 40 ? 'High' : 'Med'} ({skillDebtScore})
                </span>
              </div>
              <div className="text-left border-l border-slate-300 pl-2 sm:pl-3 col-span-2 sm:col-span-1">
                <span className="text-[10px] text-slate-500 block uppercase font-medium">Estimated</span>
                <span className="text-xs sm:text-sm font-bold text-slate-800 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  {estimatedTime}
                </span>
              </div>
            </div>
          </div>

          {/* Expected Proof Banner */}
          <div className="mt-4 p-3 bg-blue-50/70 border border-blue-200 rounded-md text-xs sm:text-sm text-slate-900 flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <div className="flex-1">
              <span className="font-bold text-blue-950 uppercase tracking-wide text-[11px] block">
                Expected Proof:
              </span>
              <p className="text-slate-800 text-xs sm:text-sm font-medium mt-0.5">
                &quot;{expectedProof}&quot;
              </p>
            </div>
          </div>

          {/* Action Row: Primary CTA + Secondary 'Why this?' toggle */}
          <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
            <button
              onClick={() => setShowWhyThis(!showWhyThis)}
              aria-expanded={showWhyThis}
              className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-md transition-colors border border-slate-200 self-start sm:self-auto cursor-pointer"
            >
              <HelpCircle className="w-4 h-4 text-slate-500" />
              <span>Why this?</span>
              {showWhyThis ? (
                <ChevronUp className="w-3.5 h-3.5 text-slate-500" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
              )}
            </button>

            <button
              onClick={handleStartProof}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-md shadow-sm transition-colors cursor-pointer min-h-[44px]"
            >
              <span>{primaryButtonLabel}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* 'Why this?' Expandable Drawer */}
          {showWhyThis && (
            <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-3.5 animate-in fade-in duration-200">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <span className="font-bold uppercase tracking-wider text-slate-800 text-[11px] flex items-center gap-1.5">
                  <Target className="w-3.5 h-3.5 text-blue-600" />
                  Decision Engine Rationale Breakdown
                </span>
                <button
                  type="button"
                  onClick={() => {
                    const nextState = !showAICoachView;
                    setShowAICoachView(nextState);
                    if (nextState && !aiExplanation) {
                      setIsLoadingAI(true);
                      api.explainDecision({
                        user_id: proof?.user_id || activeUserId || 1,
                        target_role: proof?.role_name || 'Data Analyst',
                        skill_name: skillName,
                        context_type: 'NEXT_BEST_PROOF',
                        structured_data: {
                          current_skill_level: currentLevel,
                          required_skill_level: targetLevel,
                          priority: priority,
                          skill_debt_status: skillDebtStatus,
                          action_type_label: actionTypeLabel,
                          why_this_action: proof?.why_this_action,
                          why_now: proof?.why_now,
                        },
                      })
                        .then((res) => setAiExplanation(res))
                        .catch((err) => console.error(err))
                        .finally(() => setIsLoadingAI(false));
                    }
                  }}
                  className="text-[11px] font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 px-2.5 py-1 rounded-md transition-colors cursor-pointer flex items-center gap-1.5"
                >
                  <Sparkles className="w-3 h-3 text-blue-600" />
                  {showAICoachView ? 'View Engine Metrics' : 'Ask AI Learning Coach'}
                </button>
              </div>

              {showAICoachView ? (
                <div className="p-3.5 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 rounded-lg border border-blue-200 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-blue-900 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                      SkillPath AI Learning Coach
                    </span>
                    {aiExplanation && (
                      <span className="text-[10px] text-slate-500 font-mono">
                        {aiExplanation.fallback_used ? 'Deterministic Fallback' : aiExplanation.model_used}
                      </span>
                    )}
                  </div>

                  {isLoadingAI ? (
                    <div className="flex items-center gap-2 text-xs text-blue-700 py-3">
                      <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                      Synthesizing personalized coaching explanation...
                    </div>
                  ) : aiExplanation ? (
                    <div className="space-y-2.5 text-xs">
                      <p className="text-slate-800 leading-relaxed font-medium">
                        {aiExplanation.explanation}
                      </p>

                      {aiExplanation.key_takeaways?.length > 0 && (
                        <div className="space-y-1 pt-1 border-t border-blue-200/60">
                          <span className="text-[11px] font-bold text-blue-900 block">Key Takeaways:</span>
                          <ul className="list-disc pl-4 space-y-0.5 text-slate-700">
                            {aiExplanation.key_takeaways.map((t, i) => (
                              <li key={i}>{t}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {aiExplanation.actionable_next_step && (
                        <div className="bg-white/80 p-2.5 rounded border border-blue-200 text-blue-950 font-semibold text-[11px] flex items-center gap-1.5">
                          <ArrowRight className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                          Next Step: {aiExplanation.actionable_next_step}
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">Click to fetch AI coaching advice.</p>
                  )}
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-white p-3 rounded border border-slate-200 space-y-1">
                  <span className="font-bold text-slate-900 text-xs block">
                    1. Role Importance & Skill Gap
                  </span>
                  <p className="text-slate-600 leading-relaxed">
                    {proof?.role_name ? `Target role: ${proof.role_name}.` : 'Target role benchmark.'}{' '}
                    Current demonstrated proficiency is <strong>{currentLevel}%</strong> versus the required benchmark of <strong>{targetLevel}%</strong> (a {Math.max(0, targetLevel - currentLevel)}% gap).
                  </p>
                </div>

                <div className="bg-white p-3 rounded border border-slate-200 space-y-1">
                  <span className="font-bold text-slate-900 text-xs block">
                    2. Skill Debt & Evidence Weakness
                  </span>
                  <p className="text-slate-600 leading-relaxed">
                    Detected state: <strong>{skillDebtStatus}</strong> (Debt Score: {skillDebtScore}/100). Prior learning exists, but recent practical demonstration is inconsistent or unverified.
                  </p>
                </div>
              </div>

              <div className="bg-white p-3 rounded border border-slate-200 space-y-1">
                <span className="font-bold text-slate-900 text-xs block">
                  3. Why This Action ({actionTypeLabel})?
                </span>
                <p className="text-slate-700 leading-relaxed">
                  {proof?.why_this_action ||
                    'Learner has prior exposure but lacks reliable practical performance. Targeted problem practice directly repairs the demonstrated evidence vector without redundant lectures.'}
                </p>
                {proof?.why_now && (
                  <p className="text-indigo-900 font-semibold pt-1">
                    Why now: {proof.why_now}
                  </p>
                )}
              </div>

              {proof?.prerequisites && proof.prerequisites.length > 0 && (
                <div className="flex items-center gap-2 text-slate-600 pt-1 border-t border-slate-200">
                  <span className="font-semibold text-slate-800">Prerequisites Checked:</span>
                  <span className="text-slate-700">{proof.prerequisites.join(', ')}</span>
                  <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 ml-auto">
                    ✓ Verified Healthy
                  </span>
                </div>
              )}

              {/* Supporting Next-Proof Readiness Context */}
              <div className="pt-2 border-t border-slate-200 space-y-1">
                <NextProofReadiness
                  userId={proof?.user_id || activeUserId || 1}
                  skillId={proof?.skill_id || 3}
                  skillName={skillName}
                  showExplainable={true}
                />
                <p className="text-[10px] text-slate-500 italic">
                  The deterministic Next-Best-Proof recommendation remains authoritative. The ML readiness estimate is supporting advisory context only.
                </p>
              </div>
            </>
          )}
            </div>
          )}
        </div>
      </div>

      {/* Interactive Proof Action Completion Modal */}
      {showPracticeModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl border border-slate-200 max-w-lg w-full p-6 space-y-4 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 block">
                  {actionTypeLabel} Simulation
                </span>
                <h3 className="text-lg font-bold text-slate-900">{title}</h3>
              </div>
              <button
                onClick={() => setShowPracticeModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-md"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-700">
              <div className="bg-slate-50 p-3.5 rounded border border-slate-200 space-y-2">
                <span className="font-bold text-slate-900 block text-xs">
                  Expected Proof Verification:
                </span>
                <p className="text-slate-700 font-medium">{expectedProof}</p>
                <div className="text-[11px] text-slate-500 pt-1">
                  Estimated Completion Time: <strong>{estimatedTime}</strong>
                </div>
              </div>

              {/* Simulation score selector */}
              <div className="space-y-2 pt-1">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-slate-800">Demonstrated Performance Score:</span>
                  <span className="text-sm font-extrabold text-blue-600">{simulationScore}%</span>
                </div>
                <input
                  type="range"
                  min="60"
                  max="100"
                  step="5"
                  value={simulationScore}
                  onChange={(e) => setSimulationScore(parseInt(e.target.value, 10))}
                  className="w-full accent-blue-600"
                />
                <div className="flex justify-between text-[10px] text-slate-400">
                  <span>60% (Partial)</span>
                  <span>80% (Target Baseline)</span>
                  <span>100% (Flawless)</span>
                </div>
              </div>

              {successMessage && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-md text-xs font-medium flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{successMessage}</span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowPracticeModal(false)}
                disabled={isSubmitting}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCompleteProof}
                disabled={isSubmitting}
                className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold text-xs rounded-md shadow-sm transition-colors cursor-pointer"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Verifying Proof & Recalculating...</span>
                  </>
                ) : (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    <span>Submit Proof & Update DNA</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
