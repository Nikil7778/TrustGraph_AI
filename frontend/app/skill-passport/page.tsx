'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import {
  api,
  ApiSkillPassportResponse,
  ApiSkillProofMatrixItem,
  ApiSkillProofEvidenceItem,
  ApiEvidenceTimelineItem,
  ApiStrongestProofItem,
  ApiSkillNeedingProofItem,
  ApiPassportProjectItem,
  ApiPassportAssessmentItem,
  ApiCareerRelevanceItem,
  ApiAIExplainDecisionResponse,
} from '../../services/api';
import {
  Award,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  Share2,
  Copy,
  Check,
  Sparkles,
  Briefcase,
  Target,
  X,
  FileCheck2,
  FolderGit2,
  UserCheck,
  RefreshCw,
  Terminal,
  Activity,
  Layers,
  ChevronRight,
  Info,
} from 'lucide-react';

export default function SkillPassportPage() {
  const router = useRouter();
  const { activeUserId, activeUser, isDemoMode, refreshUser } = useLearner();

  // Primary Passport Data State
  const [passportData, setPassportData] = useState<ApiSkillPassportResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // View Mode: 'learner' | 'recruiter'
  const [viewMode, setViewMode] = useState<'learner' | 'recruiter'>('learner');

  // Modal / Detail States
  const [selectedSkill, setSelectedSkill] = useState<ApiSkillProofMatrixItem | null>(null);
  const [showShareModal, setShowShareModal] = useState<boolean>(false);
  const [copiedLink, setCopiedLink] = useState<boolean>(false);
  const [copiedSummary, setCopiedSummary] = useState<boolean>(false);

  // Gemini Explanation State for Selected Skill
  const [aiExplanation, setAiExplanation] = useState<string | null>(null);
  const [isAiLoading, setIsAiLoading] = useState<boolean>(false);
  const [aiExplainType, setAiExplainType] = useState<'why_verified' | 'how_to_strengthen' | null>(null);

  // Fetch Passport Data
  const loadPassport = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getSkillPassport(activeUserId || 1);
      setPassportData(data);
    } catch (err: any) {
      console.warn('Backend passport endpoint error, building fallback view:', err);
      setError(err?.message || 'Failed to load skill passport from backend.');
    } finally {
      setIsLoading(false);
    }
  }, [activeUserId]);

  useEffect(() => {
    loadPassport();
  }, [loadPassport]);

  // AI Explanation Handler
  const handleRequestAiExplanation = async (type: 'why_verified' | 'how_to_strengthen') => {
    if (!selectedSkill) return;
    setIsAiLoading(true);
    setAiExplainType(type);
    try {
      const contextType = type === 'why_verified' ? 'EVIDENCE_VERIFICATION' : 'STRENGTHEN_SKILL';
      const res: ApiAIExplainDecisionResponse = await api.explainDecision({
        user_id: activeUserId || 1,
        skill_name: selectedSkill.skill_name,
        target_role: passportData?.header.target_role_name || 'Data Analyst',
        context_type: contextType,
        structured_data: {
          skill_name: selectedSkill.skill_name,
          skill_level: selectedSkill.skill_level,
          confidence: selectedSkill.confidence,
          required_level: selectedSkill.required_level,
          status: selectedSkill.status,
          evidence_count: selectedSkill.evidence_count,
          evidence_strength_label: selectedSkill.evidence_strength_label,
          target_role: passportData?.header.target_role_name || 'Data Analyst',
        },
      });
      setAiExplanation(res.explanation);
    } catch (err: any) {
      // Deterministic client fallback if offline
      if (type === 'why_verified') {
        setAiExplanation(
          `${selectedSkill.skill_name} is marked as ${selectedSkill.status} based on ${selectedSkill.evidence_count} evaluated evidence item(s), demonstrating an assessed score of ${Math.round(selectedSkill.skill_level)}% against the role requirement of ${Math.round(selectedSkill.required_level)}% with ${Math.round(selectedSkill.confidence)}% deterministic confidence.`
        );
      } else {
        setAiExplanation(
          `To strengthen ${selectedSkill.skill_name}, complete an applied practical task or hands-on failure lab in the Practice Lab to reinforce real-world execution and eliminate edge-case errors.`
        );
      }
    } finally {
      setIsAiLoading(false);
    }
  };

  // Close skill modal & reset AI
  const handleCloseSkillModal = () => {
    setSelectedSkill(null);
    setAiExplanation(null);
    setAiExplainType(null);
  };

  // Copy shareable summary text to clipboard
  const handleCopySummaryText = () => {
    if (!passportData) return;
    const header = passportData.header;

    const summaryText = `SKILLPATH AI — PROOF-OF-SKILL PASSPORT
Learner: ${header.learner_name}
Target Role: ${header.target_role_name}
Passport ID: ${header.passport_id}
Career Readiness: ${Math.round(header.career_readiness)}%
Verified Skills: ${header.skills_verified_count} of ${header.total_role_skills_count}
Evidence Records: ${header.total_evidence_count} items
Last Verified: ${header.last_verified_date || 'Recent'}

VERIFIED COMPETENCIES:
${passportData.skill_proof_matrix
  .filter((s: ApiSkillProofMatrixItem) => s.is_verified)
  .map((s: ApiSkillProofMatrixItem) => `- ${s.skill_name}: Level ${Math.round(s.skill_level)}% (${s.evidence_count} proofs, ${s.evidence_strength_label})`)
  .join('\n') || '- In progress'}

ACTIVE SKILL DEBT / GAPS:
${passportData.skills_needing_proof
  .map((s: ApiSkillNeedingProofItem) => `- ${s.skill_name}: ${s.status} (Current ${Math.round(s.current_level)}% / Target ${Math.round(s.required_level)}%)`)
  .join('\n') || '- None'}

Verified through tamper-evident deterministic evaluations at SkillPath AI.`;

    if (typeof window !== 'undefined') {
      navigator.clipboard.writeText(summaryText);
      setCopiedSummary(true);
      setTimeout(() => setCopiedSummary(false), 2200);
    }
  };

  // Copy share link
  const handleCopyShareLink = () => {
    if (typeof window !== 'undefined') {
      navigator.clipboard.writeText(window.location.href);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2200);
    }
  };

  // Helper for status badge styling
  const getStatusBadge = (status: string) => {
    const s = (status || '').toUpperCase();
    if (s === 'VERIFIED' || s === 'HEALTHY' || s === 'STRONG') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          VERIFIED
        </span>
      );
    }
    if (s === 'DEVELOPING') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
          <Clock className="w-3 h-3 text-amber-600" />
          DEVELOPING
        </span>
      );
    }
    if (s === 'SKILL DEBT' || s === 'CRITICAL') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          <AlertTriangle className="w-3 h-3 text-rose-600" />
          SKILL DEBT
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
        <Clock className="w-3 h-3 text-slate-400" />
        NOT YET PROVEN
      </span>
    );
  };

  // Helper for evidence type badges
  const getEvidenceTypeBadge = (evType: string) => {
    const t = (evType || '').toUpperCase();
    if (t === 'REAL_WORLD_TASK' || t === 'INDUSTRY_LAB' || t === 'LAB') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
          <Terminal className="w-3 h-3 text-blue-600" />
          REAL-WORLD TASK
        </span>
      );
    }
    if (t === 'PROJECT') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-purple-50 text-purple-700 border border-purple-200">
          <FolderGit2 className="w-3 h-3 text-purple-600" />
          PROJECT
        </span>
      );
    }
    if (t === 'PRACTICE') {
      return (
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-cyan-50 text-cyan-700 border border-cyan-200">
          <Activity className="w-3 h-3 text-cyan-600" />
          PRACTICE
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
        <FileCheck2 className="w-3 h-3 text-slate-600" />
        ASSESSMENT
      </span>
    );
  };

  // Loading State
  if (isLoading && !passportData) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
          <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
          <div className="text-center">
            <h3 className="text-base font-semibold text-slate-800">Verifying Evidence Ledger</h3>
            <p className="text-sm text-slate-500">Compiling tamper-evident Proof-of-Skill transcript...</p>
          </div>
        </div>
      </AppShell>
    );
  }

  // Empty State: New learner without evidence or no data loaded (Requirement 21)
  if (!passportData || passportData.header.total_evidence_count === 0 || passportData.skill_proof_matrix.length === 0) {
    return (
      <AppShell>
        <div className="max-w-2xl mx-auto my-12 bg-white border border-slate-200 rounded-xl p-8 sm:p-12 text-center shadow-sm">
          <div className="w-16 h-16 rounded-full bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center mx-auto mb-6">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Your Skill Passport is being built</h2>
          <p className="text-slate-600 text-sm mt-3 max-w-md mx-auto leading-relaxed">
            A skill claim without evidence is not equivalent to a demonstrated skill. Complete your first diagnostic assessment or practical lab to establish verified proof.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/assessments"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-lg shadow-sm transition-colors"
            >
              <FileCheck2 className="w-4 h-4" />
              Start Assessment
            </Link>
            <Link
              href="/practice-lab"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm rounded-lg border border-slate-300 transition-colors"
            >
              <Terminal className="w-4 h-4" />
              Open Failure Lab
            </Link>
          </div>
        </div>
      </AppShell>
    );
  }

  const {
    header,
    summary,
    skill_proof_matrix,
    evidence_timeline,
    strongest_proof,
    skills_needing_proof,
    next_best_proof,
    projects,
    assessment_history,
    career_relevance,
  } = passportData;

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Top Control Bar: Mode Toggle & Share */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 sm:p-5 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold shrink-0 shadow-sm">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg sm:text-xl font-bold text-slate-900">Proof-of-Skill Passport</h1>
                <span className="text-[11px] font-mono font-medium px-2 py-0.5 bg-slate-100 text-slate-600 border border-slate-200 rounded">
                  {header.passport_id}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Deterministic evidence transcript verifying demonstrated competency for {header.target_role_name}.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5 flex-wrap">
            {/* Recruiter View Toggle (Requirement 17) */}
            <div className="inline-flex rounded-lg border border-slate-200 p-1 bg-slate-50">
              <button
                type="button"
                onClick={() => setViewMode('learner')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                  viewMode === 'learner'
                    ? 'bg-white text-blue-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Learner View
              </button>
              <button
                type="button"
                onClick={() => setViewMode('recruiter')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center gap-1.5 ${
                  viewMode === 'recruiter'
                    ? 'bg-white text-blue-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Briefcase className="w-3.5 h-3.5" />
                Recruiter View
              </button>
            </div>

            {/* Print / Export */}
            <button
              type="button"
              onClick={() => typeof window !== 'undefined' && window.print()}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-lg transition-colors cursor-pointer"
            >
              Export PDF
            </button>

            {/* Share / Copy (Requirement 16) */}
            <button
              type="button"
              onClick={() => setShowShareModal(true)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors cursor-pointer"
            >
              <Share2 className="w-3.5 h-3.5" />
              Share Passport
            </button>
          </div>
        </div>

        {/* 3. PASSPORT HEADER (Profile & Verified Statistics) */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
            {/* Candidate & Target Role */}
            <div className="md:col-span-1 border-b md:border-b-0 md:border-r border-slate-100 pb-4 md:pb-0 md:pr-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-base uppercase shrink-0">
                  {header.learner_name.slice(0, 2)}
                </div>
                <div>
                  <h2 className="text-base font-bold text-slate-900 leading-tight">{header.learner_name}</h2>
                  <div className="flex items-center gap-1.5 mt-1">
                    <Target className="w-3.5 h-3.5 text-blue-600" />
                    <span className="text-xs font-semibold text-slate-700">{header.target_role_name}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 block mt-0.5">
                    Verified: {header.last_verified_date || 'Today'}
                  </span>
                </div>
              </div>
            </div>

            {/* Career Readiness */}
            <div className="flex items-center gap-4">
              <div className="relative w-14 h-14 flex items-center justify-center rounded-full bg-slate-50 border-4 border-blue-500/30">
                <span className="text-base font-black text-slate-900">
                  {Math.round(header.career_readiness)}%
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 font-medium uppercase tracking-wider block">
                  Career Readiness
                </span>
                <span className="text-sm font-semibold text-slate-800">
                  {header.career_readiness_status}
                </span>
              </div>
            </div>

            {/* Skills Verified */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs text-slate-500 font-medium uppercase tracking-wider block">
                  Skills Verified
                </span>
                <span className="text-lg font-bold text-slate-900">
                  {header.skills_verified_count}{' '}
                  <span className="text-xs text-slate-400 font-normal">/ {header.total_role_skills_count} required</span>
                </span>
              </div>
            </div>

            {/* Evidence Records Count */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 flex items-center justify-center shrink-0">
                <FileCheck2 className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xs text-slate-500 font-medium uppercase tracking-wider block">
                  Evidence Items
                </span>
                <span className="text-lg font-bold text-slate-900">
                  {header.total_evidence_count}{' '}
                  <span className="text-xs text-slate-400 font-normal">verified submissions</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* RECRUITER VIEW SPECIAL MODE (Requirement 17) */}
        {viewMode === 'recruiter' && (
          <div className="bg-slate-900 text-white rounded-xl p-6 sm:p-8 space-y-6 shadow-md border border-slate-800">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
              <div>
                <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">
                  <UserCheck className="w-4 h-4" /> Recruiter Evaluation Summary
                </div>
                <h2 className="text-xl font-bold tracking-tight text-white">
                  Demonstrated Competency Audit — {header.learner_name}
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Target Role: <strong className="text-slate-200">{header.target_role_name}</strong> • Tamper-evident deterministic audit.
                </p>
              </div>
              <div className="text-right sm:text-right">
                <div className="text-2xl font-black text-emerald-400">{Math.round(header.career_readiness)}%</div>
                <span className="text-xs text-slate-400 font-medium">Deterministic Role Readiness</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Verified Capabilities */}
              <div className="bg-slate-800/80 rounded-lg p-4 border border-slate-700">
                <h3 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3">
                  Verified Technical Skills ({summary.verified_skills_count})
                </h3>
                <div className="space-y-2">
                  {skill_proof_matrix
                    .filter((s: ApiSkillProofMatrixItem) => s.is_verified)
                    .map((s: ApiSkillProofMatrixItem) => (
                      <div key={s.skill_id} className="flex items-center justify-between text-xs py-1 border-b border-slate-700/50">
                        <span className="font-semibold text-slate-200">{s.skill_name}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">{s.evidence_count} proofs</span>
                          <span className="font-mono text-emerald-400 font-bold">{Math.round(s.skill_level)}%</span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {/* Strongest Practical Evidence */}
              <div className="bg-slate-800/80 rounded-lg p-4 border border-slate-700">
                <h3 className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-3">
                  Hands-On Workplace Tasks
                </h3>
                {strongest_proof ? (
                  <div className="space-y-2 text-xs">
                    <div className="font-bold text-white text-sm">{strongest_proof.title}</div>
                    <div className="text-slate-400">{strongest_proof.evidence_strength}</div>
                    <div className="flex items-center justify-between pt-2 border-t border-slate-700">
                      <span className="text-slate-300">Demonstrated Score:</span>
                      <span className="font-mono font-bold text-blue-400">{Math.round(strongest_proof.score)}%</span>
                    </div>
                    <div className="flex flex-wrap gap-1 pt-1">
                      {strongest_proof.skills_demonstrated.map((sk: string) => (
                        <span key={sk} className="px-1.5 py-0.5 rounded bg-slate-700 text-slate-300 text-[10px]">
                          {sk}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">Practical tasks in progress.</p>
                )}
              </div>

              {/* Development Areas */}
              <div className="bg-slate-800/80 rounded-lg p-4 border border-slate-700">
                <h3 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-3">
                  Development Focus Areas ({skills_needing_proof.length})
                </h3>
                <div className="space-y-2">
                  {skills_needing_proof.map((snp: ApiSkillNeedingProofItem) => (
                    <div key={snp.skill_id} className="flex items-center justify-between text-xs py-1 border-b border-slate-700/50">
                      <span className="text-slate-200 font-medium">{snp.skill_name}</span>
                      <span className="text-[10px] uppercase font-bold text-amber-400 px-1.5 py-0.5 bg-amber-950/60 rounded">
                        {snp.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 bg-slate-950/60 p-3 rounded border border-slate-800 flex items-center gap-2">
              <Info className="w-4 h-4 text-slate-500 shrink-0" />
              <span>
                <strong>Methodology:</strong> Every metric is derived deterministically from timed diagnostic assessments and real PostgreSQL query execution in the Industry Failure Lab. SkillPath AI does not permit self-assessment claims.
              </span>
            </div>
          </div>
        )}

        {/* 4. PASSPORT SUMMARY (Proof of your current Data Analyst skills) */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
            <div>
              <h2 className="text-base font-bold text-slate-900">{summary.headline}</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Transparent breakdown of what has been demonstrably proven versus what requires additional evidence.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
            {/* Verified Skills */}
            <div className="p-4 rounded-lg bg-emerald-50/70 border border-emerald-200/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-emerald-800 uppercase tracking-wider">
                  Verified Skills
                </span>
                <span className="text-lg font-black text-emerald-700">{summary.verified_skills_count}</span>
              </div>
              <p className="text-xs text-emerald-700/90 mt-1.5">
                {summary.strongest_skills.length > 0
                  ? `Strongest: ${summary.strongest_skills.join(', ')}`
                  : 'Multi-source proof met target requirement'}
              </p>
            </div>

            {/* Developing Skills */}
            <div className="p-4 rounded-lg bg-amber-50/70 border border-amber-200/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-amber-800 uppercase tracking-wider">
                  Developing Skills
                </span>
                <span className="text-lg font-black text-amber-700">{summary.developing_skills_count}</span>
              </div>
              <p className="text-xs text-amber-700/90 mt-1.5">
                Demonstrated baseline performance; active growth toward role threshold.
              </p>
            </div>

            {/* Skill Debt */}
            <div className="p-4 rounded-lg bg-rose-50/70 border border-rose-200/80">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-rose-800 uppercase tracking-wider">
                  Active Skill Debt
                </span>
                <span className="text-lg font-black text-rose-700">{summary.skill_debt_count}</span>
              </div>
              <p className="text-xs text-rose-700/90 mt-1.5">
                {summary.skills_needing_proof.length > 0
                  ? `Immediate focus: ${summary.skills_needing_proof.join(', ')}`
                  : 'No active skill debt detected.'}
              </p>
            </div>
          </div>
        </div>

        {/* 5. SKILL PROOF MATRIX (Main Section) */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <div className="p-5 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-slate-900">Skill Proof Matrix</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Click any row to inspect individual supporting evidence items, scores, and deterministic audit trails.
              </p>
            </div>
            <div className="text-xs text-slate-500">
              Showing <strong className="text-slate-800">{skill_proof_matrix.length}</strong> role-competencies
            </div>
          </div>

          {/* Desktop Table View */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50/80 text-slate-600 font-semibold text-xs border-b border-slate-200 select-none">
                <tr>
                  <th className="py-3 px-5">Skill</th>
                  <th className="py-3 px-4 text-center">Demonstrated Level</th>
                  <th className="py-3 px-4 text-center">Confidence</th>
                  <th className="py-3 px-4">Supporting Evidence</th>
                  <th className="py-3 px-4">Last Verified</th>
                  <th className="py-3 px-4 text-center">Status</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {skill_proof_matrix.map((item: ApiSkillProofMatrixItem) => (
                  <tr
                    key={item.skill_id}
                    onClick={() => setSelectedSkill(item)}
                    className="hover:bg-blue-50/40 transition-colors cursor-pointer group"
                  >
                    <td className="py-3.5 px-5">
                      <div className="font-semibold text-slate-900 group-hover:text-blue-700 transition-colors">
                        {item.skill_name}
                      </div>
                      <span className="text-[11px] text-slate-400">{item.category}</span>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <div className="inline-flex flex-col items-center">
                        <span className="font-mono font-bold text-slate-800 text-sm">
                          {Math.round(item.skill_level)}
                        </span>
                        <span className="text-[10px] text-slate-400">
                          Target: {Math.round(item.required_level)}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span className="font-mono text-xs font-semibold text-slate-700">
                        {Math.round(item.confidence)}%
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex flex-col">
                        <span className="text-xs font-semibold text-slate-800">
                          {item.evidence_count} {item.evidence_count === 1 ? 'item' : 'items'}
                        </span>
                        <span className="text-[11px] text-slate-500">{item.evidence_strength_label}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600 font-medium">
                      {item.last_verified}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      {getStatusBadge(item.status)}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedSkill(item);
                        }}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
                      >
                        Inspect
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Card List View (Responsive Design - Requirement 22) */}
          <div className="md:hidden divide-y divide-slate-100">
            {skill_proof_matrix.map((item: ApiSkillProofMatrixItem) => (
              <div
                key={item.skill_id}
                onClick={() => setSelectedSkill(item)}
                className="p-4 hover:bg-blue-50/30 transition-colors cursor-pointer space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">{item.skill_name}</h3>
                    <span className="text-[11px] text-slate-400">{item.category}</span>
                  </div>
                  {getStatusBadge(item.status)}
                </div>

                <div className="grid grid-cols-3 gap-2 text-center text-xs bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block">Level</span>
                    <span className="font-mono font-bold text-slate-800">{Math.round(item.skill_level)}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block">Confidence</span>
                    <span className="font-mono font-bold text-slate-800">{Math.round(item.confidence)}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block">Evidence</span>
                    <span className="font-semibold text-slate-800">{item.evidence_count} items</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
                  <span>Verified: {item.last_verified}</span>
                  <span className="text-blue-600 font-semibold inline-flex items-center gap-1">
                    Inspect Proofs <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 10. STRONGEST PROOF & 11. SKILLS NEEDING MORE PROOF (Grid) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 10. Your Strongest Proof (Requirement 10) */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <h3 className="text-base font-bold text-slate-900">Your Strongest Proof</h3>
                </div>
                {strongest_proof && getEvidenceTypeBadge(strongest_proof.evidence_type)}
              </div>

              {strongest_proof ? (
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200/80 space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="text-sm font-bold text-slate-900">{strongest_proof.title}</h4>
                        <span className="text-xs text-slate-500">{strongest_proof.evidence_strength}</span>
                      </div>
                      <div className="text-right">
                        <span className="text-xl font-black font-mono text-blue-600">
                          {Math.round(strongest_proof.score)}%
                        </span>
                        <span className="text-[10px] text-slate-400 block">Evaluated Score</span>
                      </div>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed">{strongest_proof.description}</p>

                    <div className="pt-2 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap gap-1.5">
                        {strongest_proof.skills_demonstrated.map((sk: string) => (
                          <span
                            key={sk}
                            className="px-2 py-0.5 rounded text-[11px] font-semibold bg-white border border-slate-200 text-slate-700"
                          >
                            {sk}
                          </span>
                        ))}
                      </div>
                      <span className="text-xs text-slate-400">Verified {strongest_proof.verified_date}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400 text-xs">
                  No verified hands-on submissions yet.
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span>Deterministically ranked by practical proof weight</span>
              <Link href="/practice-lab" className="text-blue-600 font-semibold hover:underline">
                Generate More Proof &rarr;
              </Link>
            </div>
          </div>

          {/* 11. Skills That Need More Evidence (Requirement 11) */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center">
                  <AlertTriangle className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">Skills That Need More Evidence</h3>
                  <p className="text-xs text-slate-500">
                    Prioritized based on target role requirements and active skill debt.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {skills_needing_proof.length > 0 ? (
                  skills_needing_proof.slice(0, 3).map((item: ApiSkillNeedingProofItem) => (
                    <div
                      key={item.skill_id}
                      className="p-3.5 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-900 text-sm">{item.skill_name}</span>
                          <span
                            className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                              item.status === 'SKILL_DEBT'
                                ? 'bg-rose-50 text-rose-700 border border-rose-200'
                                : 'bg-amber-50 text-amber-700 border border-amber-200'
                            }`}
                          >
                            {item.status === 'SKILL_DEBT' ? 'HIGH Skill Debt' : 'Evidence Gap'}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 line-clamp-1">{item.evidence_gap_reason}</p>
                        <span className="text-[11px] text-slate-600 block">
                          Next proof: <strong>{item.recommended_proof_title}</strong>
                        </span>
                      </div>

                      <div className="shrink-0">
                        <Link
                          href={item.status === 'SKILL_DEBT' ? '/practice-lab' : '/assessments'}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-xs rounded-lg border border-blue-200 transition-colors"
                        >
                          Prove this
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6 text-slate-400 text-xs">
                    All core target skills currently possess verified proof!
                  </div>
                )}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 text-right">
              <Link href="/career-gap" className="text-xs text-blue-600 font-semibold hover:underline">
                View All Career Gaps &rarr;
              </Link>
            </div>
          </div>
        </div>

        {/* 12. NEXT-BEST-PROOF INTEGRATION (Requirement 12) */}
        {next_best_proof && (
          <div className="bg-gradient-to-r from-blue-900 to-slate-900 text-white rounded-xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-5 border border-blue-950">
            <div className="space-y-1.5 max-w-2xl">
              <div className="flex items-center gap-2 text-xs font-semibold text-blue-300 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                Recommended Next Proof
              </div>
              <h3 className="text-lg font-bold text-white tracking-tight">
                {next_best_proof.title || 'SQL JOIN Rescue & Validation Lab'}
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                {next_best_proof.why_now ||
                  'Your next strongest piece of evidence: establishes demonstrated mastery on multi-table queries to eliminate skill debt.'}
              </p>
              <div className="flex items-center gap-3 text-xs text-slate-400 pt-1">
                <span>Skill: <strong className="text-slate-200">{next_best_proof.skill_name || 'SQL JOINs'}</strong></span>
                <span>•</span>
                <span>Est. Time: <strong className="text-slate-200">{next_best_proof.estimated_minutes || 25} min</strong></span>
              </div>
            </div>

            <div className="shrink-0">
              <Link
                href="/practice-lab"
                className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-blue-500 hover:bg-blue-600 text-white font-bold text-xs uppercase tracking-wider rounded-lg shadow-sm transition-all"
              >
                Start Proof Activity
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        )}

        {/* 13. PROJECT EVIDENCE & 14. ASSESSMENT HISTORY (Dual Card Section) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 13. Project Evidence (Requirement 13) */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <FolderGit2 className="w-4 h-4 text-purple-600" />
                <h3 className="text-base font-bold text-slate-900">Project & Practical Evidence</h3>
              </div>
              <span className="text-xs text-slate-400">{projects.length} recorded</span>
            </div>

            <div className="space-y-3">
              {projects.length > 0 ? (
                projects.map((proj: ApiPassportProjectItem) => (
                  <div
                    key={proj.id}
                    className="p-3.5 rounded-lg bg-slate-50/70 border border-slate-200 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-slate-900">{proj.title}</h4>
                      <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                        {proj.status}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 pt-1">
                      <div className="flex flex-wrap gap-1">
                        {proj.skills_demonstrated.map((sk: string) => (
                          <span
                            key={sk}
                            className="px-1.5 py-0.5 rounded bg-white text-slate-700 border border-slate-200 text-[10px] font-medium"
                          >
                            {sk}
                          </span>
                        ))}
                      </div>
                      <div className="flex items-center gap-2">
                        {proj.score !== null && proj.score !== undefined && (
                          <span className="font-mono font-bold text-slate-800">
                            Score: {Math.round(proj.score)}%
                          </span>
                        )}
                        <span className="text-[11px] text-slate-400">{proj.verified_date}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-6 text-slate-400 text-xs">
                  No portfolio projects submitted yet.
                </div>
              )}
            </div>
          </div>

          {/* 14. Assessment History (Requirement 14) */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <FileCheck2 className="w-4 h-4 text-blue-600" />
                <h3 className="text-base font-bold text-slate-900">Diagnostic Assessment History</h3>
              </div>
              <span className="text-xs text-slate-400">{assessment_history.length} completed</span>
            </div>

            <div className="space-y-3">
              {assessment_history.map((ah: ApiPassportAssessmentItem) => (
                <div
                  key={ah.id}
                  className="p-3.5 rounded-lg bg-slate-50/70 border border-slate-200 flex items-center justify-between gap-3 text-xs"
                >
                  <div className="space-y-0.5">
                    <h4 className="font-bold text-slate-900">{ah.assessment_title}</h4>
                    <div className="flex items-center gap-2 text-slate-500 text-[11px]">
                      <span>Skill: <strong className="text-slate-700">{ah.skill_name}</strong></span>
                      <span>•</span>
                      <span>Difficulty: {ah.difficulty}</span>
                    </div>
                  </div>

                  <div className="text-right shrink-0">
                    <span className="font-mono font-bold text-sm text-slate-900 block">
                      {Math.round(ah.score)}%
                    </span>
                    <span className="text-[10px] text-slate-400">{ah.completed_at}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 9. EVIDENCE TIMELINE & 15. CAREER RELEVANCE */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 9. Evidence Timeline (Chronological - Requirement 9) */}
          <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-slate-900">Evidence Timeline</h3>
                <p className="text-xs text-slate-500">
                  Chronological log of verified diagnostic assessments, labs, and practical activities.
                </p>
              </div>
              <span className="text-xs text-slate-400 font-mono">Real Timestamps</span>
            </div>

            <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {evidence_timeline.slice(0, 6).map((ev: ApiEvidenceTimelineItem) => (
                <div key={ev.id} className="relative group">
                  <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-blue-600 border-2 border-white" />
                  <div className="bg-slate-50/70 p-3 rounded-lg border border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-slate-900 text-xs">{ev.source}</span>
                        {getEvidenceTypeBadge(ev.evidence_type)}
                      </div>
                      <span className="text-[11px] text-slate-500 mt-0.5 block">
                        Demonstrated Skill: <strong className="text-slate-700">{ev.skill_name}</strong>
                      </span>
                    </div>

                    <div className="flex items-center sm:flex-col sm:items-end justify-between gap-1 shrink-0">
                      <span className="font-mono font-bold text-xs text-slate-800">
                        Score: {Math.round(ev.score)}%
                      </span>
                      <span className="text-[10px] text-slate-400">{ev.relative_date}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 15. Career-Relevance for Target Role (Requirement 15) */}
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm space-y-4">
            <div className="border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-900">Proof for Target Role</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Core competencies required for <strong>{header.target_role_name}</strong>.
              </p>
            </div>

            <div className="space-y-2.5">
              {career_relevance.map((cr: ApiCareerRelevanceItem) => {
                const isStrong = cr.evidence_status_label.includes('Strong');
                const isDebt = cr.evidence_status_label.includes('Debt');
                return (
                  <div
                    key={cr.skill_name}
                    className="p-3 rounded-lg border border-slate-100 bg-slate-50/60 flex items-center justify-between text-xs"
                  >
                    <div>
                      <span className="font-bold text-slate-900 block">{cr.skill_name}</span>
                      <span
                        className={`text-[11px] font-medium ${
                          isStrong
                            ? 'text-emerald-700'
                            : isDebt
                            ? 'text-rose-700 font-bold'
                            : 'text-amber-700'
                        }`}
                      >
                        {cr.evidence_status_label}
                      </span>
                    </div>
                    <span className="text-[10px] uppercase font-bold text-slate-400">
                      {cr.career_priority}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* 6. CLICKABLE SKILL DETAIL MODAL (Requirements 6, 7 & 18) */}
        {selectedSkill && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-150">
            <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden">
              {/* Modal Header */}
              <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-slate-900">{selectedSkill.skill_name}</h3>
                    {getStatusBadge(selectedSkill.status)}
                  </div>
                  <span className="text-xs text-slate-500">{selectedSkill.category}</span>
                </div>
                <button
                  type="button"
                  onClick={handleCloseSkillModal}
                  className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6 overflow-y-auto space-y-6">
                {/* Metric Summary */}
                <div className="grid grid-cols-3 gap-3 p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-center text-xs">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block">Skill Level</span>
                    <span className="text-base font-black text-slate-900 font-mono">
                      {Math.round(selectedSkill.skill_level)}
                    </span>
                    <span className="text-[10px] text-slate-400 block">
                      Target: {Math.round(selectedSkill.required_level)}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block">Confidence</span>
                    <span className="text-base font-black text-slate-900 font-mono">
                      {Math.round(selectedSkill.confidence)}%
                    </span>
                    <span className="text-[10px] text-slate-400 block">Deterministic Engine</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase block">Evidence Strength</span>
                    <span className="text-xs font-bold text-blue-700 block mt-1">
                      {selectedSkill.evidence_strength_label}
                    </span>
                  </div>
                </div>

                {/* Supporting Evidence List (Requirement 6) */}
                <div>
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">
                    Evidence Supporting This Skill ({selectedSkill.supporting_evidences.length})
                  </h4>

                  <div className="space-y-2.5">
                    {selectedSkill.supporting_evidences.length > 0 ? (
                      selectedSkill.supporting_evidences.map((evItem: ApiSkillProofEvidenceItem) => (
                        <div
                          key={evItem.id}
                          className="p-3.5 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors space-y-2"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2">
                              {getEvidenceTypeBadge(evItem.evidence_type)}
                              <span className="text-xs font-bold text-slate-900">{evItem.title}</span>
                            </div>
                            <span className="font-mono font-bold text-xs text-blue-600">
                              Score: {Math.round(evItem.score)}%
                            </span>
                          </div>

                          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-100">
                            <span>Strength: <strong>{evItem.evidence_strength}</strong></span>
                            <span>Verified: {evItem.relative_date}</span>
                          </div>

                          {evItem.description && (
                            <p className="text-[11px] text-slate-600 italic">{evItem.description}</p>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-xs text-slate-400 text-center py-4 bg-slate-50 rounded-lg">
                        No direct evidence items found for this skill.
                      </div>
                    )}
                  </div>
                </div>

                {/* 18. Controlled Gemini AI Explainer (Requirement 18) */}
                <div className="p-4 bg-blue-50/60 rounded-lg border border-blue-200/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-blue-900">
                      <Sparkles className="w-4 h-4 text-blue-600" />
                      Gemini Evidence Assistant
                    </div>
                    <span className="text-[10px] text-slate-500">Strictly deterministic context</span>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      disabled={isAiLoading}
                      onClick={() => handleRequestAiExplanation('why_verified')}
                      className="px-3 py-1.5 bg-white hover:bg-slate-50 text-blue-700 text-xs font-semibold rounded border border-blue-200 transition-colors disabled:opacity-50"
                    >
                      Explain why this skill is verified
                    </button>
                    <button
                      type="button"
                      disabled={isAiLoading}
                      onClick={() => handleRequestAiExplanation('how_to_strengthen')}
                      className="px-3 py-1.5 bg-white hover:bg-slate-50 text-blue-700 text-xs font-semibold rounded border border-blue-200 transition-colors disabled:opacity-50"
                    >
                      How can I strengthen this skill?
                    </button>
                  </div>

                  {isAiLoading && (
                    <div className="flex items-center gap-2 text-xs text-slate-600 pt-1">
                      <RefreshCw className="w-3.5 h-3.5 text-blue-600 animate-spin" />
                      Analyzing deterministic evidence...
                    </div>
                  )}

                  {aiExplanation && !isAiLoading && (
                    <div className="p-3 bg-white rounded border border-blue-200 text-xs text-slate-700 leading-relaxed animate-in fade-in">
                      {aiExplanation}
                    </div>
                  )}
                </div>
              </div>

              {/* Modal Footer */}
              <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={handleCloseSkillModal}
                  className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-semibold rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 16. SHARE PASSPORT PREVIEW MODAL (Requirement 16) */}
        {showShareModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-150">
            <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-lg w-full p-6 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Share2 className="w-5 h-5 text-blue-600" />
                  <h3 className="text-base font-bold text-slate-900">Share Skill Passport</h3>
                </div>
                <button
                  type="button"
                  onClick={() => setShowShareModal(false)}
                  className="text-slate-400 hover:text-slate-700"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Passport Snapshot Card Preview */}
              <div className="p-4 bg-slate-900 text-white rounded-lg space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-emerald-400 font-bold uppercase tracking-wider">
                    {header.target_role_name}
                  </span>
                  <span className="text-slate-400 font-mono text-[10px]">{header.passport_id}</span>
                </div>
                <div>
                  <h4 className="text-base font-bold text-white">{header.learner_name}</h4>
                  <span className="text-xs text-slate-400">
                    Career Readiness: <strong className="text-emerald-400">{Math.round(header.career_readiness)}%</strong>
                  </span>
                </div>
                <div className="text-xs text-slate-300 pt-2 border-t border-slate-800 flex justify-between">
                  <span>Verified Skills: {header.skills_verified_count}</span>
                  <span>Evidence: {header.total_evidence_count} items</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2">
                <button
                  type="button"
                  onClick={handleCopySummaryText}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg shadow-sm transition-colors cursor-pointer"
                >
                  {copiedSummary ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copiedSummary ? 'Summary Copied to Clipboard!' : 'Copy Passport Summary for Resume/LinkedIn'}
                </button>

                <button
                  type="button"
                  onClick={handleCopyShareLink}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-lg border border-slate-300 transition-colors cursor-pointer"
                >
                  {copiedLink ? <Check className="w-4 h-4" /> : <Share2 className="w-4 h-4" />}
                  {copiedLink ? 'Link Copied!' : 'Copy Public Verification Link'}
                </button>
              </div>

              <p className="text-[11px] text-slate-400 text-center">
                Private personal contact details are never shared without learner authorization.
              </p>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
