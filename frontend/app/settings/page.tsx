'use client';

import React, { useState, useEffect } from 'react';
import { AppShell } from '../../components/AppShell';
import { Settings, Target, Key, Database, CheckCircle2, Loader2, Save } from 'lucide-react';
import { useLearner } from '../../context/LearnerContext';
import { api, ApiRole } from '../../services/api';

export default function SettingsPage() {
  const { activeUser, updateTargetRole, isDemoMode } = useLearner();
  const [roles, setRoles] = useState<ApiRole[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number>(activeUser?.target_role_id || 1);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [savedSuccess, setSavedSuccess] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRoles() {
      try {
        const fetched = await api.getRoles();
        const supported = [
          fetched.find((r) => r.id === 2 || r.name === 'Data Scientist') || ({ id: 2, name: 'Data Scientist' } as ApiRole),
          fetched.find((r) => r.id === 5 || r.name === 'Python Developer') || ({ id: 5, name: 'Python Developer' } as ApiRole),
          fetched.find((r) => r.id === 1 || r.name === 'Data Analyst') || ({ id: 1, name: 'Data Analyst' } as ApiRole),
        ];
        if (activeUser?.target_role_id === 9) {
          supported.push({ id: 9, name: 'Analytics Engineer (Preserved)' } as ApiRole);
        }
        setRoles(supported);
        if (activeUser?.target_role_id) {
          setSelectedRoleId(activeUser.target_role_id);
        } else if (supported.length > 0) {
          setSelectedRoleId(supported[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch roles:', err);
      }
    }
    fetchRoles();
  }, [activeUser?.target_role_id]);

  const handleSaveRole = async () => {
    setIsSaving(true);
    setSavedSuccess(null);
    try {
      await updateTargetRole(selectedRoleId);
      setSavedSuccess('Career benchmark updated! Skill Debt and Roadmap recalculated.');
      setTimeout(() => setSavedSuccess(null), 3000);
    } catch (err) {
      console.error('Failed to update target role:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppShell>
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 sm:p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 shrink-0">
            <Settings className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Platform Settings</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Configure target career benchmarks, evidence thresholds, and notification preferences.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm divide-y divide-slate-100">
        {/* Section 1: Target Role Preference */}
        <div className="p-4 sm:p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-blue-600 shrink-0" />
            <h3 className="font-bold text-slate-900 text-base">Target Career Benchmark</h3>
          </div>

          <div className="w-full max-w-md space-y-3">
            <label htmlFor="target-role-select" className="block text-xs font-semibold text-slate-700 uppercase">
              Current Target Role
            </label>
            <select
              id="target-role-select"
              value={selectedRoleId}
              onChange={(e) => setSelectedRoleId(parseInt(e.target.value, 10))}
              className="w-full bg-slate-50 border border-slate-300 rounded-md px-3 py-2.5 text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
            >
              {roles.length > 0 ? (
                roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))
              ) : (
                <>
                  <option value={1}>Data Analyst</option>
                  <option value={9}>Analytics Engineer</option>
                  <option value={2}>Data Scientist</option>
                  <option value={3}>ML Engineer</option>
                </>
              )}
            </select>
            <span className="text-[11px] text-slate-500 block">
              Changing target role recalculates all Skill Debt thresholds and rebuilds the roadmap.
            </span>

            {savedSuccess && (
              <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                {savedSuccess}
              </div>
            )}

            <button
              onClick={handleSaveRole}
              disabled={isSaving}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded shadow-xs transition-colors cursor-pointer disabled:opacity-60"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {isSaving ? 'Updating Benchmark...' : 'Save Target Benchmark'}
            </button>
          </div>
        </div>

        {/* Section 2: AI Engine Explanations */}
        <div className="p-4 sm:p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Key className="w-5 h-5 text-amber-600 shrink-0" />
            <h3 className="font-bold text-slate-900 text-base">Optional Gemini AI Service</h3>
          </div>

          <div className="w-full max-w-md space-y-3">
            <label htmlFor="ai-rationale-toggle" className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-md cursor-pointer min-h-[44px]">
              <div>
                <span className="font-semibold text-xs text-slate-900 block">AI Rationale Explanations</span>
                <span className="text-[11px] text-slate-500 block">Generate natural language explanations for roadmap updates</span>
              </div>
              <input id="ai-rationale-toggle" type="checkbox" defaultChecked className="w-5 h-5 text-blue-600 rounded shrink-0 cursor-pointer" />
            </label>

            <div className="text-xs text-slate-500 bg-amber-50 p-3 rounded border border-amber-200">
              <strong>Architecture Note:</strong> Core roadmap decisions and scoring are 100% deterministic and remain processed by backend algorithms.
            </div>
          </div>
        </div>

        {/* Section 3: Data & Evidence Sync */}
        <div className="p-4 sm:p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-emerald-600 shrink-0" />
            <h3 className="font-bold text-slate-900 text-base">Evidence Retention</h3>
          </div>

          <div className="w-full max-w-md text-xs text-slate-600 space-y-2">
            <p>Skill DNA history retain interval: <strong>12 Months</strong></p>
            <p>Automatic Skill Debt Recalculation: <strong>Enabled after each assessment</strong></p>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
