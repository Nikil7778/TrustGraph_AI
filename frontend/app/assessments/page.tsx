'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import { AssessmentCard } from '../../components/AssessmentCard';
import { api, ApiAssessment, ApiAssessmentAttempt } from '../../services/api';
import { MOCK_ASSESSMENTS } from '../../lib/mockData';
import { AssessmentData } from '../../types';
import { FileCheck2, Filter, Award, History, AlertCircle, RefreshCw, Target, ArrowRight, Sparkles } from 'lucide-react';

export default function AssessmentsPage() {
  const router = useRouter();
  const { activeUserId, isDemoMode, activeUser } = useLearner();
  const [assessments, setAssessments] = useState<AssessmentData[]>([]);
  const [attempts, setAttempts] = useState<ApiAssessmentAttempt[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<string>('All');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadAssessmentData = useCallback(async () => {
    if (!activeUserId) return;
    setIsLoading(true);
    setError(null);
    try {
      // Fetch assessments and user's previous attempts for active user
      const [apiAssessments, apiAttempts] = await Promise.all([
        api.getAssessments().catch(() => []),
        api.getUserAssessmentAttempts(activeUserId).catch(() => []),
      ]);

      setAttempts(apiAttempts);

      if (apiAssessments && apiAssessments.length > 0) {
        // Map backend assessments to AssessmentData
        const mapped: AssessmentData[] = apiAssessments.map((a: ApiAssessment) => {
          // Find latest attempt for this assessment
          const userAttempts = apiAttempts.filter((att) => att.assessment_id === a.id);
          const latestAttempt = userAttempts[0]; // ordered desc by completed_at

          return {
            id: a.id.toString(),
            title: a.title,
            skillCategory: a.skill_name || 'Data Science',
            targetSkill: a.skill_name || 'Technical Skill',
            durationMinutes: 15,
            questionCount: a.question_count || 10,
            latestScore: latestAttempt ? Math.round(latestAttempt.score) : undefined,
            status: latestAttempt ? 'completed' : 'available',
            lastTaken: latestAttempt
              ? new Date(latestAttempt.completed_at).toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                })
              : undefined,
          };
        });
        setAssessments(mapped);
      } else {
        // Fallback to mock data only if explicitly in demo mode
        setAssessments(isDemoMode ? MOCK_ASSESSMENTS : []);
      }
    } catch (err: any) {
      console.error('Failed to load assessments from API:', err);
      setError(err?.message || 'Failed to load diagnostic assessments.');
      setAssessments(isDemoMode ? MOCK_ASSESSMENTS : []);
    } finally {
      setIsLoading(false);
    }
  }, [activeUserId, isDemoMode]);

  useEffect(() => {
    loadAssessmentData();
  }, [loadAssessmentData]);

  const handleStart = (assessmentId: string) => {
    router.push(`/assessments/${assessmentId}`);
  };

  // Skill filter options
  const filterOptions = ['All', 'SQL JOINs', 'Python', 'SQL', 'Statistics', 'EDA', 'Data Visualization', 'Power BI'];

  const filteredAssessments = assessments.filter((a) => {
    if (selectedFilter === 'All') return true;
    return a.targetSkill.toLowerCase() === selectedFilter.toLowerCase() ||
      a.skillCategory.toLowerCase() === selectedFilter.toLowerCase();
  });

  const completedCount = assessments.filter((a) => a.status === 'completed').length;

  return (
    <AppShell>
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 shrink-0">
            <FileCheck2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Diagnostic Assessments</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Strict quantitative evaluations measuring technical skill baseline and accuracy.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 bg-slate-100 px-3 py-2 rounded border border-slate-200 self-start md:self-auto shrink-0">
          <Award className="w-4 h-4 text-blue-600" />
          <span>{completedCount} / {assessments.length} Completed</span>
        </div>
      </div>

      {/* Target Goal Diagnostic Banner (Phase 1 Mandate) */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200/60 flex items-center gap-1">
              <Target className="w-3 h-3 text-blue-600" />
              Target Goal Assessment
            </span>
            <span className="text-xs font-semibold text-slate-500">
              {activeUser?.target_role?.name || 'Selected Target Goal'}
            </span>
          </div>
          <h2 className="text-base sm:text-lg font-bold text-slate-900">
            Comprehensive Goal Diagnostic: {activeUser?.target_role?.name || 'Your Target Track'}
          </h2>
          <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
            Evaluates every required competency for your target goal simultaneously. Produces your granular
            Skill DNA profile, calculates skill gaps, and unlocks your personalized learning roadmap.
          </p>
        </div>

        <button
          onClick={() => router.push(`/assessments/goal/${activeUser?.target_role_id || 1}`)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-blue-800 hover:bg-blue-900 text-white text-xs font-semibold shadow-xs transition-colors shrink-0 cursor-pointer"
        >
          <Sparkles className="w-4 h-4 text-blue-200" />
          <span>Launch Goal Assessment</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Error state alert if API had issues */}
      {error && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 rounded-lg p-4 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{error} Showing cached diagnostic assessments.</span>
          </div>
          <button
            onClick={loadAssessmentData}
            className="flex items-center gap-1 font-semibold text-amber-700 hover:text-amber-900 underline ml-2"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Retry
          </button>
        </div>
      )}

      {/* Responsive Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between bg-white p-3 sm:px-4 sm:py-3 border border-slate-200 rounded-lg shadow-2xs gap-3">
        <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-500">
          <div className="flex items-center gap-1.5 shrink-0">
            <Filter className="w-4 h-4 text-slate-400" />
            <span>Filter:</span>
          </div>
          {filterOptions.map((opt) => (
            <button
              key={opt}
              onClick={() => setSelectedFilter(opt)}
              className={`min-h-[36px] px-3 py-1 rounded font-medium focus:ring-2 focus:ring-blue-500 transition-colors ${
                selectedFilter === opt
                  ? 'bg-slate-900 text-white'
                  : 'hover:bg-slate-100 text-slate-700'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-400 shrink-0">
          Showing {filteredAssessments.length} Assessments
        </span>
      </div>

      {/* Loading state */}
      {isLoading ? (
        <div className="bg-white border border-slate-200 rounded-lg p-12 text-center shadow-xs">
          <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
          <p className="text-sm font-semibold text-slate-700">Loading Diagnostic Assessments...</p>
        </div>
      ) : filteredAssessments.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-lg p-8 text-center text-slate-500 text-xs">
          No diagnostic assessments found matching filter &quot;{selectedFilter}&quot;.
        </div>
      ) : (
        /* Grid of Assessment Cards */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          {filteredAssessments.map((assessment) => (
            <AssessmentCard
              key={assessment.id}
              assessment={assessment}
              onStart={() => handleStart(assessment.id)}
            />
          ))}
        </div>
      )}

      {/* Assessment History Section */}
      {attempts.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-6 shadow-sm mt-6">
          <div className="flex items-center gap-2 mb-4">
            <History className="w-5 h-5 text-blue-600" />
            <h2 className="text-base font-bold text-slate-900">Assessment History</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold">
                  <th className="py-2.5 px-3">Assessment Title</th>
                  <th className="py-2.5 px-3">Skill Assessed</th>
                  <th className="py-2.5 px-3">Score</th>
                  <th className="py-2.5 px-3">Accuracy</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Date Completed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {attempts.map((att) => {
                  const score = Math.round(att.score);
                  let interpretation = 'Developing';
                  let statusColor = 'bg-amber-50 text-amber-700 border-amber-200';
                  if (score >= 90) {
                    interpretation = 'Strong';
                    statusColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
                  } else if (score >= 75) {
                    interpretation = 'Healthy';
                    statusColor = 'bg-blue-50 text-blue-700 border-blue-200';
                  } else if (score < 50) {
                    interpretation = 'Critical Gap';
                    statusColor = 'bg-rose-50 text-rose-700 border-rose-200';
                  }

                  return (
                    <tr key={att.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-2.5 px-3 font-semibold text-slate-900">{att.assessment_title || 'Diagnostic Assessment'}</td>
                      <td className="py-2.5 px-3 text-slate-600">{att.skill_name || 'Skill'}</td>
                      <td className="py-2.5 px-3 font-bold text-slate-900">{score}%</td>
                      <td className="py-2.5 px-3 text-slate-600">{att.accuracy.toFixed(1)}%</td>
                      <td className="py-2.5 px-3">
                        <span className={`inline-block px-2 py-0.5 rounded border text-[11px] font-semibold ${statusColor}`}>
                          {interpretation}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-slate-500">
                        {new Date(att.completed_at).toLocaleString(undefined, {
                          dateStyle: 'medium',
                          timeStyle: 'short',
                        })}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </AppShell>
  );
}
