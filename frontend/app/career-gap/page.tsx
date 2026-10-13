'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import { useCoach } from '../../context/CoachContext';
import { api, ApiCareerValue, ApiAIExplainDecisionResponse } from '../../services/api';
import {
  Target,
  ArrowRight,
  RotateCw,
  Sparkles,
  X,
  AlertTriangle,
  Info,
  BookOpen,
} from 'lucide-react';

export default function CareerGapPage() {
  const router = useRouter();
  const { activeUserId, activeUser, careerValues, refreshUser, isDemoMode } = useLearner();
  const { openCoach } = useCoach();
  const [isRecalculating, setIsRecalculating] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState<ApiCareerValue | null>(null);

  // Phase 11 — Gemini AI Career Value Priority Explanation
  const [aiCareerExplanation, setAiCareerExplanation] = useState<ApiAIExplainDecisionResponse | null>(null);
  const [isLoadingAICareer, setIsLoadingAICareer] = useState<boolean>(false);

  const targetRoleName = activeUser?.target_role?.name || 'Data Analyst';

  const handleSelectSkill = async (skill: ApiCareerValue) => {
    setSelectedSkill(skill);
    setAiCareerExplanation(null);
    setIsLoadingAICareer(true);
    try {
      const res = await api.explainDecision({
        user_id: activeUserId || 1,
        target_role: targetRoleName,
        skill_name: skill.skill_name,
        context_type: 'CAREER_VALUE',
        structured_data: {
          priority: skill.priority,
          career_value_score: skill.career_value_score,
          gap_score: skill.gap_score,
          role_importance: skill.role_importance,
          industry_relevance: skill.industry_relevance,
          skill_debt_status: skill.skill_debt_status,
          current_skill_level: skill.current_skill_level,
          required_skill_level: skill.required_skill_level,
        },
      });
      setAiCareerExplanation(res);
    } catch (err) {
      console.error('Failed to get career priority explanation:', err);
    } finally {
      setIsLoadingAICareer(false);
    }
  };

  const handleRecalculate = async () => {
    setIsRecalculating(true);
    try {
      if (activeUserId) {
        await api.recalculateCareerValue(activeUserId);
        await refreshUser();
      }
    } catch (err) {
      console.error('Failed to recalculate Career Value priorities:', err);
    } finally {
      setIsRecalculating(false);
    }
  };

  const topPrioritySkill = careerValues[0] || null;
  const isUnassessed = careerValues.length === 0 || careerValues.every((cv) => cv.current_skill_level === 0);

  return (
    <AppShell>
      <div className="space-y-5 max-w-6xl mx-auto">
        {/* ========================================================================= */}
        {/* 1. HEADER (Matches Stitch Reference Visual Language)                      */}
        {/* ========================================================================= */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Career Gap</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Which skills matter most for your target role: <strong className="text-slate-800">{targetRoleName}</strong>
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs font-semibold text-slate-700 bg-white border border-slate-200 px-3 py-1.5 rounded-full shadow-2xs inline-flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5 text-blue-600" />
              <span>Target Vector: {targetRoleName}</span>
            </span>

            <button
              onClick={handleRecalculate}
              disabled={isRecalculating}
              className="p-1.5 text-slate-500 hover:text-slate-800 bg-white hover:bg-slate-50 border border-slate-200 rounded-md transition-colors cursor-pointer"
              title="Recalculate Career Value Priorities"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isRecalculating ? 'animate-spin text-blue-600' : ''}`} />
            </button>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 2. HIGHEST-PRIORITY GAP HERO CARD                                         */}
        {/* ========================================================================= */}
        {topPrioritySkill && (
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
              <div>
                <span className={`text-[10px] font-bold tracking-wider px-2.5 py-0.5 rounded-full inline-flex items-center gap-1.5 ${isUnassessed ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-rose-50 text-rose-700 border border-rose-200'}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${isUnassessed ? 'bg-blue-600' : 'bg-rose-600'}`} />
                  {isUnassessed ? 'PRIMARY BENCHMARK COMPETENCY' : 'HIGHEST PRIORITY GAP • RANK #1'}
                </span>
                <h2 className="text-xl font-bold text-slate-900 mt-2 tracking-tight">
                  {topPrioritySkill.skill_name}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5 max-w-3xl leading-relaxed">
                  {isUnassessed
                    ? 'Target competency required for job qualification. Complete your diagnostic assessment to identify your current skill standing.'
                    : topPrioritySkill.reason}
                </p>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 sm:text-right shrink-0">
                <span className={`text-2xl font-black ${isUnassessed ? 'text-slate-700' : 'text-rose-600'}`}>
                  {isUnassessed ? 'Not assessed' : `${Math.round(topPrioritySkill.gap_score)}%`}
                </span>
                <span className="text-xs text-slate-400 block font-medium">
                  {isUnassessed ? 'Demonstrated Standing' : 'Competency Deficit'}
                </span>
              </div>
            </div>

            {/* Current vs Target Comparison Bars */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs pt-2">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-slate-600">
                  <span>Demonstrated Level</span>
                  <span className="font-bold text-slate-900">
                    {isUnassessed ? 'Not assessed' : `${Math.round(topPrioritySkill.current_skill_level)}%`}
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-rose-600 h-full rounded-full"
                    style={{ width: isUnassessed ? '0%' : `${Math.round(topPrioritySkill.current_skill_level)}%` }}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-slate-600">
                  <span>Required Target Benchmark</span>
                  <span className="font-bold text-slate-900">{Math.round(topPrioritySkill.required_skill_level)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-blue-900 h-full rounded-full" style={{ width: `${Math.round(topPrioritySkill.required_skill_level)}%` }} />
                </div>
              </div>
            </div>

            {/* Action Row */}
            <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3 text-slate-500">
                <span>Role Importance: <strong className="text-slate-800">{Math.round(topPrioritySkill.role_importance)}%</strong></span>
                <span>•</span>
                <span>Target Benchmark: <strong className="text-slate-800">{Math.round(topPrioritySkill.required_skill_level)}%</strong></span>
              </div>

              <button
                onClick={() => router.push(isUnassessed ? '/assessments' : '/practice-lab')}
                className="px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer"
              >
                <span>{isUnassessed ? 'Start Diagnostic Assessment' : 'Prove Highest-Priority Gap'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* 3. RANKED SKILL GAPS TABLE                                                */}
        {/* ========================================================================= */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Ranked Role Competencies</h3>
              <p className="text-xs text-slate-500">
                Prioritized by Career Value Engine ROI (Gap + Role Importance + Skill Debt)
              </p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              {careerValues.length} tracked
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/50 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-4 text-center w-12">RANK</th>
                  <th className="py-3 px-4">COMPETENCY</th>
                  <th className="py-3 px-4 min-w-[200px]">CURRENT VS TARGET</th>
                  <th className="py-3 px-4 text-center">ROLE WEIGHT</th>
                  <th className="py-3 px-4 text-center">CAREER ROI</th>
                  <th className="py-3 px-4 text-right">PRIORITY</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {careerValues.map((item) => {
                  const isTopRank = item.rank === 1;

                  let priorityBadgeClass = 'bg-slate-100 text-slate-600';
                  if (item.priority === 'CRITICAL') {
                    priorityBadgeClass = 'bg-rose-50 text-rose-700 border border-rose-200 font-semibold';
                  } else if (item.priority === 'HIGH') {
                    priorityBadgeClass = 'bg-amber-50 text-amber-800 border border-amber-200 font-semibold';
                  } else if (item.priority === 'MEDIUM') {
                    priorityBadgeClass = 'bg-blue-50 text-blue-700 border border-blue-200';
                  }

                  return (
                    <tr
                      key={item.skill_id}
                      onClick={() => handleSelectSkill(item)}
                      className={`transition-colors cursor-pointer ${
                        isTopRank ? 'bg-rose-50/20 hover:bg-rose-50/40' : 'hover:bg-slate-50'
                      }`}
                    >
                      <td className="py-3 px-4 text-center font-bold text-slate-500">
                        {item.rank}
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-bold text-slate-900 block">{item.skill_name}</span>
                        <span className="text-[11px] text-slate-500 block">{item.skill_category}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                            <span>{isUnassessed ? 'Not assessed' : `${Math.round(item.current_skill_level)}%`}</span>
                            <span>Target {Math.round(item.required_skill_level)}%</span>
                          </div>
                          <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div
                              className={`h-full rounded-full ${
                                item.gap_score > 30 ? 'bg-rose-600' : 'bg-blue-700'
                              }`}
                              style={{ width: isUnassessed ? '0%' : `${Math.round(item.current_skill_level)}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-center font-semibold text-slate-700">
                        {Math.round(item.role_importance)}%
                      </td>
                      <td className="py-3 px-4 text-center font-mono font-bold text-slate-900">
                        {Math.round(item.career_value_score)}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] ${priorityBadgeClass}`}>
                          {item.priority}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* 4. DETAIL INSPECTOR MODAL                                                 */}
        {/* ========================================================================= */}
        {selectedSkill && (
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full border border-slate-200 overflow-hidden animate-in fade-in duration-150">
              <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-blue-700" />
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm">
                      {selectedSkill.skill_name} Priority Analysis
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Career Value Engine Diagnostics
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedSkill(null)}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded-md cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-5 space-y-4 max-h-[75vh] overflow-y-auto text-xs">
                <p className="text-slate-700 leading-relaxed font-normal">
                  {selectedSkill.reason}
                </p>

                <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Career ROI Score
                    </span>
                    <span className="text-base font-bold text-slate-900">
                      {Math.round(selectedSkill.career_value_score)} / 100
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Competency Deficit
                    </span>
                    <span className="text-base font-bold text-rose-600">
                      -{Math.round(selectedSkill.gap_score)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Role Importance
                    </span>
                    <span className="text-base font-bold text-slate-900">
                      {Math.round(selectedSkill.role_importance)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase font-bold block">
                      Skill Debt State
                    </span>
                    <span className="text-xs font-semibold text-slate-700 mt-1 block">
                      {selectedSkill.skill_debt_status}
                    </span>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      const prompt = `Why is ${selectedSkill.skill_name} important for my career?`;
                      setSelectedSkill(null);
                      openCoach(prompt);
                    }}
                    className="inline-flex items-center gap-1.5 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold rounded-md border border-blue-200 transition-colors cursor-pointer"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    <span>Ask Coach</span>
                  </button>

                  <button
                    onClick={() => router.push('/practice-lab')}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-800 hover:bg-blue-900 text-white font-semibold rounded-md shadow-xs transition-colors cursor-pointer"
                  >
                    <span>Practice Skill</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
