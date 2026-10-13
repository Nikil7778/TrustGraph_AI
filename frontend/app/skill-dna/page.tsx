'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import { useCoach } from '../../context/CoachContext';
import { api, ApiSkillDNA, ApiAILearningExplanationResponse } from '../../services/api';
import { NextProofReadiness } from '../../components/NextProofReadiness';
import {
  Code2,
  Table,
  Database,
  BarChart3,
  Compass,
  AlertTriangle,
  LayoutGrid,
  Brain,
  ShieldCheck,
  RotateCw,
  X,
  BookOpen,
  Sparkles,
  ArrowRight,
  Loader2,
  AlertCircle,
} from 'lucide-react';

export default function SkillDNAPage() {
  const { activeUserId } = useLearner();
  const { openCoach } = useCoach();
  const [skillDnaList, setSkillDnaList] = useState<ApiSkillDNA[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRecalculating, setIsRecalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Inspector modal for deeper diagnostics & AI explanation
  const [inspectedSkill, setInspectedSkill] = useState<ApiSkillDNA | null>(null);
  const [aiExplanation, setAiExplanation] = useState<ApiAILearningExplanationResponse | null>(null);
  const [isLoadingAi, setIsLoadingAi] = useState<boolean>(false);

  const loadSkillDna = useCallback(async () => {
    if (!activeUserId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getSkillDna(activeUserId);
      setSkillDnaList(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load Skill DNA vector.';
      console.error('Failed to fetch Skill DNA:', err);
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [activeUserId]);

  useEffect(() => {
    loadSkillDna();
  }, [loadSkillDna]);

  const handleRecalculate = async () => {
    if (!activeUserId) return;
    setIsRecalculating(true);
    try {
      const updated = await api.recalculateSkillDna(activeUserId);
      if (updated && updated.length > 0) {
        setSkillDnaList(updated);
      }
    } catch (err: unknown) {
      console.error('Failed to recalculate Skill DNA:', err);
      setError('Failed to recalculate Skill DNA.');
    } finally {
      setIsRecalculating(false);
    }
  };

  const handleInspectSkill = async (skill: ApiSkillDNA) => {
    setInspectedSkill(skill);
    setAiExplanation(null);
    setIsLoadingAi(true);
    try {
      const res = await api.getLearningExplanation({
        skill_name: skill.skill_name,
        target_role: 'Data Analyst',
      });
      setAiExplanation(res);
    } catch (err) {
      console.error('Failed to load explanation:', err);
    } finally {
      setIsLoadingAi(false);
    }
  };

  // Helper to map skill name to Stitch domain & icon
  const getSkillMeta = (name: string, category: string) => {
    const lower = name.toLowerCase();
    if (lower.includes('python')) {
      return { domain: 'Core Analytics', icon: Code2 };
    }
    if (lower.includes('stat') || lower.includes('probability')) {
      return { domain: 'Statistical Analysis', icon: Table };
    }
    if (lower.includes('join') || lower.includes('relational')) {
      return { domain: 'Relational Algebra', icon: AlertTriangle };
    }
    if (lower.includes('query') || lower.includes('sql')) {
      return { domain: 'Core Querying', icon: Database };
    }
    if (lower.includes('visual') || lower.includes('tableau')) {
      return { domain: 'Presentation & Dashboards', icon: BarChart3 };
    }
    if (lower.includes('eda') || lower.includes('exploratory')) {
      return { domain: 'Data Wrangling', icon: Compass };
    }
    if (lower.includes('bi') || lower.includes('dax')) {
      return { domain: 'Business Intelligence', icon: LayoutGrid };
    }
    if (lower.includes('machine') || lower.includes('ml')) {
      return { domain: 'Predictive Modeling', icon: Brain };
    }
    return { domain: category || 'Domain Competency', icon: Database };
  };

  return (
    <AppShell>
      <div className="space-y-5 max-w-6xl mx-auto">
        {/* ========================================================================= */}
        {/* 1. HEADER (Matches Stitch Screenshot 3)                                   */}
        {/* ========================================================================= */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Skill DNA</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Your current ability based on demonstrated evidence.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs font-semibold text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-full shadow-2xs inline-flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
              <span>{skillDnaList.length || 8} Core Competencies Tracked</span>
            </span>

            <button
              onClick={handleRecalculate}
              disabled={isRecalculating}
              className="p-1.5 text-slate-500 hover:text-slate-800 bg-white hover:bg-slate-50 border border-slate-200 rounded-md transition-colors cursor-pointer"
              title="Recalculate Skill DNA Vector"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isRecalculating ? 'animate-spin text-blue-600' : ''}`} />
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
        {/* 2. COMPETENCY MATRIX TABLE (Matches Stitch Screenshot 3)                  */}
        {/* ========================================================================= */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/50 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-5">SKILL &amp; DOMAIN</th>
                  <th className="py-3 px-5">DEMONSTRATED LEVEL</th>
                  <th className="py-3 px-5">CONFIDENCE</th>
                  <th className="py-3 px-5">EVIDENCE</th>
                  <th className="py-3 px-5 text-right">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {skillDnaList.map((skill) => {
                  const isUnassessedSkill = skill.evidence_count === 0 || skill.status === 'UNKNOWN';
                  const isDebt = !isUnassessedSkill && skill.status === 'CRITICAL';
                  const { domain, icon: Icon } = getSkillMeta(
                    skill.skill_name,
                    skill.skill_category
                  );

                  // Confidence dot styling
                  const confidenceLabel = isUnassessedSkill
                    ? 'Not assessed'
                    : skill.confidence >= 75
                    ? 'High'
                    : skill.confidence >= 50
                    ? 'Medium'
                    : 'Low';

                  const confidenceDotClass = isUnassessedSkill
                    ? 'bg-slate-300'
                    : isDebt
                    ? 'bg-rose-600'
                    : confidenceLabel === 'High'
                    ? 'bg-emerald-600'
                    : confidenceLabel === 'Medium'
                    ? 'bg-blue-600'
                    : 'bg-slate-400';

                  // Status badge styling matching Stitch
                  let statusLabel = 'Developing';
                  let statusBadgeClass =
                    'bg-indigo-50 text-indigo-700 border border-indigo-200/60';

                  if (isUnassessedSkill) {
                    statusLabel = 'Not assessed';
                    statusBadgeClass = 'bg-slate-100 text-slate-600 border border-slate-200';
                  } else if (isDebt) {
                    statusLabel = 'Skill Debt';
                    statusBadgeClass = 'bg-rose-700 text-white font-semibold';
                  } else if (skill.skill_level >= 75) {
                    statusLabel = 'Verified';
                    statusBadgeClass =
                      'bg-emerald-50 text-emerald-700 border border-emerald-200/60 font-semibold';
                  } else if (skill.skill_level < 40) {
                    statusLabel = 'Elective';
                    statusBadgeClass = 'bg-slate-100 text-slate-600';
                  }

                  return (
                    <tr
                      key={skill.skill_id}
                      onClick={() => handleInspectSkill(skill)}
                      className={`transition-colors cursor-pointer ${
                        isDebt
                          ? 'bg-rose-50/40 hover:bg-rose-50/70'
                          : 'hover:bg-slate-50/70'
                      }`}
                    >
                      {/* 1. Skill & Domain with Icon */}
                      <td className="py-3.5 px-5">
                        <div className="flex items-center gap-3">
                          <div
                            className={`w-7 h-7 rounded-md flex items-center justify-center shrink-0 ${
                              isDebt
                                ? 'bg-rose-100 text-rose-700'
                                : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            <Icon className="w-3.5 h-3.5" />
                          </div>
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="font-bold text-slate-900 text-xs">
                                {skill.skill_name}
                              </span>
                              {isDebt && (
                                <span className="text-[9px] font-bold px-1.5 py-0.2 rounded bg-rose-600 text-white uppercase tracking-wider">
                                  INSPECT
                                </span>
                              )}
                            </div>
                            <span className="text-[11px] text-slate-500 block">
                              {domain}
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* 2. Demonstrated Level Progress Bar */}
                      <td className="py-3.5 px-5 min-w-[180px]">
                        <div className="flex items-center gap-3">
                          <div className="flex-1 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                isDebt
                                  ? 'bg-rose-600'
                                  : skill.skill_level >= 75
                                  ? 'bg-blue-900'
                                  : 'bg-blue-600'
                              }`}
                              style={{ width: isUnassessedSkill ? '0%' : `${Math.round(skill.skill_level)}%` }}
                            />
                          </div>
                          <span
                            className={`font-bold font-mono text-[11px] shrink-0 ${
                              isUnassessedSkill
                                ? 'text-slate-500 font-normal'
                                : isDebt
                                ? 'text-rose-600'
                                : 'text-slate-900'
                            }`}
                          >
                            {isUnassessedSkill ? 'Not assessed' : `${Math.round(skill.skill_level)}%`}
                          </span>
                        </div>
                      </td>

                      {/* 3. Confidence with Dot */}
                      <td className="py-3.5 px-5">
                        <div className="flex items-center gap-1.5 text-xs text-slate-700 font-medium">
                          <span
                            className={`w-1.5 h-1.5 rounded-full shrink-0 ${confidenceDotClass}`}
                          />
                          <span className={isDebt ? 'text-rose-700 font-semibold' : ''}>
                            {confidenceLabel}
                          </span>
                        </div>
                      </td>

                      {/* 4. Evidence Count */}
                      <td className="py-3.5 px-5">
                        <span
                          className={`text-xs ${
                            isDebt
                              ? 'text-rose-600 font-semibold'
                              : 'text-slate-500'
                          }`}
                        >
                          {skill.evidence_count} proof
                          {skill.evidence_count === 1 ? '' : 's'}
                        </span>
                      </td>

                      {/* 5. Status Badge */}
                      <td className="py-3.5 px-5 text-right">
                        <span
                          className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] tracking-tight ${statusBadgeClass}`}
                        >
                          {statusLabel}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Table Footer matching Stitch reference */}
          <div className="p-4 border-t border-slate-100 bg-slate-50/40 text-xs text-slate-500 flex items-center justify-between flex-wrap gap-2">
            <span>Click any item for detailed sub-competency diagnostics and evidence trail.</span>
            <span className="font-mono text-slate-400">{skillDnaList.length} skills total</span>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 3. DIAGNOSTICS & CONCEPT INSPECTOR MODAL                                  */}
        {/* ========================================================================= */}
        {inspectedSkill && (
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden animate-in fade-in duration-150">
              <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-blue-700" />
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">
                      {inspectedSkill.skill_name} Diagnostic Inspection
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Deterministic Vector Verification &amp; Evidence Ledger
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setInspectedSkill(null)}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-5 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
                {/* Metrics Breakdown */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">
                      Skill Level
                    </span>
                    <span className="text-base font-bold text-slate-900 font-mono">
                      {inspectedSkill.evidence_count === 0 || inspectedSkill.status === 'UNKNOWN'
                        ? 'Not assessed'
                        : `${Math.round(inspectedSkill.skill_level)}%`}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">
                      Confidence
                    </span>
                    <span className="text-base font-bold text-slate-900 font-mono">
                      {inspectedSkill.evidence_count === 0 || inspectedSkill.status === 'UNKNOWN'
                        ? 'Not assessed'
                        : `${Math.round(inspectedSkill.confidence)}%`}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">
                      Skill Debt
                    </span>
                    <span className={`text-base font-bold ${inspectedSkill.status === 'CRITICAL' ? 'text-rose-600' : 'text-slate-800'}`}>
                      {inspectedSkill.evidence_count === 0 || inspectedSkill.status === 'UNKNOWN'
                        ? 'None'
                        : inspectedSkill.status === 'CRITICAL'
                        ? 'HIGH'
                        : 'HEALTHY'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">
                      Career Priority
                    </span>
                    <span className="text-base font-bold text-slate-800">
                      {inspectedSkill.skill_name.toLowerCase().includes('sql') || inspectedSkill.skill_name.toLowerCase().includes('python') ? 'HIGH' : 'MEDIUM'}
                    </span>
                  </div>
                </div>

                {/* Section 3: Next-Proof Readiness (Supporting ML Predictive Advisory) */}
                <NextProofReadiness
                  userId={inspectedSkill.user_id || activeUserId || 1}
                  skillId={inspectedSkill.skill_id}
                  skillName={inspectedSkill.skill_name}
                  showExplainable={true}
                />

                {/* AI Concept Explanation / Guidance */}
                {isLoadingAi ? (
                  <div className="py-6 flex flex-col items-center justify-center text-center space-y-2">
                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                    <p className="text-slate-500 text-xs">Loading concept overview...</p>
                  </div>
                ) : aiExplanation ? (
                  <div className="space-y-3 pt-2">
                    <div>
                      <h4 className="font-bold text-slate-900 text-xs">Core Concept Overview</h4>
                      <p className="text-slate-600 text-xs mt-1 leading-relaxed">
                        {aiExplanation.concept_summary}
                      </p>
                    </div>

                    {aiExplanation.concise_example && (
                      <div className="p-2.5 bg-slate-50 border border-slate-200 rounded font-mono text-[11px] text-slate-800">
                        {aiExplanation.concise_example}
                      </div>
                    )}

                    {aiExplanation.common_pitfall && (
                      <div className="p-2 bg-rose-50 border border-rose-200 rounded text-rose-900 text-[11px]">
                        <strong>Common Pitfall:</strong> {aiExplanation.common_pitfall}
                      </div>
                    )}
                  </div>
                ) : null}

                {/* Action CTA */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      const prompt = `How can I improve ${inspectedSkill.skill_name}?`;
                      setInspectedSkill(null);
                      openCoach(prompt);
                    }}
                    className="inline-flex items-center gap-1.5 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold rounded-md border border-blue-200 transition-colors cursor-pointer"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    <span>Ask Career Coach</span>
                  </button>

                  <Link
                    href="/practice-lab"
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold rounded-md shadow-xs transition-colors"
                  >
                    <span>Practice Skill</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
