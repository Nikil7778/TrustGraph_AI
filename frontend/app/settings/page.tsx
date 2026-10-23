'use client';

import React, { useState, useEffect } from 'react';
import { AppShell } from '../../components/AppShell';
import {
  Settings,
  Target,
  Key,
  Database,
  CheckCircle2,
  Loader2,
  Save,
  BookOpen,
  Sparkles,
  Check,
  AlertCircle,
} from 'lucide-react';
import { useLearner } from '../../context/LearnerContext';
import { api, ApiRole } from '../../services/api';

const SUPPORTED_PLATFORMS = [
  { id: 'no_preference', label: 'No Preference', desc: 'Default ranking based on curriculum quality' },
  { id: 'geeksforgeeks', label: 'GeeksforGeeks', desc: 'Comprehensive explanations, syntax notes & code snippets' },
  { id: 'w3schools', label: 'W3Schools', desc: 'Clear documentation, beginner-friendly examples' },
  { id: 'khanacademy', label: 'Khan Academy', desc: 'Foundational concepts, intuitive step-by-step math/logic' },
  { id: 'coursera', label: 'Coursera', desc: 'Structured academic lessons and university-grade resources' },
  { id: 'datacamp', label: 'DataCamp', desc: 'Interactive hands-on data science & analytics tutorials' },
];

export default function SettingsPage() {
  const { activeUser, updateTargetRole, isDemoMode } = useLearner();
  const [roles, setRoles] = useState<ApiRole[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number>(activeUser?.target_role_id || 1);
  const [isSavingRole, setIsSavingRole] = useState<boolean>(false);
  const [roleSavedSuccess, setRoleSavedSuccess] = useState<string | null>(null);

  // Phase 21: Learning Platform Preferences
  const [primaryPlatform, setPrimaryPlatform] = useState<string>('no_preference');
  const [secondaryPlatforms, setSecondaryPlatforms] = useState<string[]>([]);
  const [isLoadingPref, setIsLoadingPref] = useState<boolean>(false);
  const [isSavingPref, setIsSavingPref] = useState<boolean>(false);
  const [prefSuccess, setPrefSuccess] = useState<string | null>(null);
  const [prefError, setPrefError] = useState<string | null>(null);

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

  useEffect(() => {
    const userId = activeUser?.id;
    if (!userId) return;
    let isMounted = true;
    async function fetchPreferences(uid: number) {
      setIsLoadingPref(true);
      try {
        const res = await api.getResourcePreferences(uid);
        if (isMounted && res) {
          setPrimaryPlatform(res.primary_platform || 'no_preference');
          setSecondaryPlatforms(res.secondary_platforms || []);
        }
      } catch (err) {
        console.error('Failed to fetch resource preferences:', err);
      } finally {
        if (isMounted) setIsLoadingPref(false);
      }
    }
    fetchPreferences(userId);
    return () => {
      isMounted = false;
    };
  }, [activeUser?.id]);

  const handleSaveRole = async () => {
    setIsSavingRole(true);
    setRoleSavedSuccess(null);
    try {
      await updateTargetRole(selectedRoleId);
      setRoleSavedSuccess('Career benchmark updated! Skill Debt and Roadmap recalculated.');
      setTimeout(() => setRoleSavedSuccess(null), 3500);
    } catch (err) {
      console.error('Failed to update target role:', err);
    } finally {
      setIsSavingRole(false);
    }
  };

  const handleToggleSecondary = (platformId: string) => {
    if (platformId === 'no_preference') return;
    setSecondaryPlatforms((prev) =>
      prev.includes(platformId)
        ? prev.filter((p) => p !== platformId)
        : [...prev, platformId]
    );
  };

  const handleSavePreferences = async () => {
    const uid = activeUser?.id;
    if (uid === undefined || uid === null) return;
    setIsSavingPref(true);
    setPrefSuccess(null);
    setPrefError(null);
    try {
      const cleanedSecondaries = secondaryPlatforms.filter(
        (p) => p !== primaryPlatform && p !== 'no_preference'
      );
      const res = await api.updateResourcePreferences(uid, {
        primary_platform: primaryPlatform,
        secondary_platforms: cleanedSecondaries,
      });
      setPrimaryPlatform(res.primary_platform);
      setSecondaryPlatforms(res.secondary_platforms);
      setPrefSuccess('Platform preferences updated! Learning modules will now highlight your preferred providers.');
      setTimeout(() => setPrefSuccess(null), 4000);
    } catch (err: any) {
      console.error('Failed to update platform preferences:', err);
      setPrefError(err?.message || 'Failed to update preferences');
    } finally {
      setIsSavingPref(false);
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
              Configure target career benchmarks, learning resource platforms, evidence thresholds, and AI guidance.
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

          <div className="w-full max-w-xl space-y-3">
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

            {roleSavedSuccess && (
              <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                {roleSavedSuccess}
              </div>
            )}

            <button
              onClick={handleSaveRole}
              disabled={isSavingRole}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded shadow-xs transition-colors cursor-pointer disabled:opacity-60"
            >
              {isSavingRole ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {isSavingRole ? 'Updating Benchmark...' : 'Save Target Benchmark'}
            </button>
          </div>
        </div>

        {/* Section 2: Learning Platform Preferences (Phase 21) */}
        <div className="p-4 sm:p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-indigo-600 shrink-0" />
              <div>
                <h3 className="font-bold text-slate-900 text-base">Learning Platform Preferences</h3>
                <p className="text-xs text-slate-500">
                  Choose your favorite providers to prioritize their verified tutorials and external resources in modules.
                </p>
              </div>
            </div>
            {isLoadingPref && (
              <span className="text-xs text-slate-400 flex items-center gap-1.5">
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Loading preferences...
              </span>
            )}
          </div>

          <div className="w-full max-w-2xl space-y-5">
            {/* Primary Platform */}
            <div className="space-y-2">
              <label htmlFor="primary-platform-select" className="block text-xs font-semibold text-slate-700 uppercase">
                Primary Platform <span className="text-indigo-600 font-medium">(Highest Recommendation Priority)</span>
              </label>
              <select
                id="primary-platform-select"
                value={primaryPlatform}
                onChange={(e) => {
                  const val = e.target.value;
                  setPrimaryPlatform(val);
                  // Remove from secondary if chosen as primary
                  setSecondaryPlatforms((prev) => prev.filter((p) => p !== val));
                }}
                className="w-full bg-slate-50 border border-slate-300 rounded-md px-3 py-2.5 text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[44px]"
              >
                {SUPPORTED_PLATFORMS.map((platform) => (
                  <option key={platform.id} value={platform.id}>
                    {platform.label} &mdash; {platform.desc}
                  </option>
                ))}
              </select>
              <span className="text-[11px] text-slate-500 block">
                Resources matching your primary platform receive a +30 ranking boost when learning modules are rendered.
              </span>
            </div>

            {/* Secondary Platforms */}
            <div className="space-y-2">
              <span className="block text-xs font-semibold text-slate-700 uppercase">
                Secondary Platforms <span className="text-slate-500 font-normal">(Additional +15 Ranking Boost)</span>
              </span>
              <p className="text-[11px] text-slate-500">
                Select additional platforms you enjoy for alternative perspectives:
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                {SUPPORTED_PLATFORMS.filter((p) => p.id !== 'no_preference').map((platform) => {
                  const isPrimary = primaryPlatform === platform.id;
                  const isSecondary = secondaryPlatforms.includes(platform.id);

                  return (
                    <div
                      key={platform.id}
                      onClick={() => !isPrimary && handleToggleSecondary(platform.id)}
                      className={`flex items-start gap-2.5 p-3 rounded-lg border text-left transition-all cursor-pointer select-none ${
                        isPrimary
                          ? 'bg-indigo-50/50 border-indigo-200 opacity-70 cursor-not-allowed'
                          : isSecondary
                          ? 'bg-indigo-50 border-indigo-300 shadow-xs'
                          : 'bg-white border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <div
                        className={`w-4 h-4 rounded mt-0.5 flex items-center justify-center shrink-0 border ${
                          isPrimary
                            ? 'bg-indigo-600 border-indigo-600 text-white'
                            : isSecondary
                            ? 'bg-indigo-600 border-indigo-600 text-white'
                            : 'border-slate-300 bg-white'
                        }`}
                      >
                        {(isPrimary || isSecondary) && <Check className="w-3 h-3 stroke-[3]" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs font-bold text-slate-900">{platform.label}</span>
                          {isPrimary && (
                            <span className="text-[10px] font-semibold text-indigo-700 bg-indigo-100 px-1.5 py-0.2 rounded">
                              Primary
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-500 leading-snug mt-0.5 line-clamp-2">
                          {platform.desc}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Architecture Invariant Callout */}
            <div className="text-xs text-indigo-900 bg-indigo-50/80 p-3.5 rounded-lg border border-indigo-200 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-indigo-950">
                <Sparkles className="w-4 h-4 text-indigo-600 shrink-0" />
                Strict Presentation-Only Guarantee
              </div>
              <p className="text-[11px] text-indigo-800 leading-relaxed">
                Platform preferences influence strictly the ordering of verified external tutorial links displayed for each learning module.
                Your <strong>Skill DNA mastery level</strong>, <strong>Skill Debt</strong>, <strong>Career Value calculations</strong>, and <strong>Deterministic Roadmap sequencing</strong> remain 100% objective and unchanged.
              </p>
            </div>

            {/* Success and Error messages */}
            {prefSuccess && (
              <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 text-xs font-semibold flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                {prefSuccess}
              </div>
            )}
            {prefError && (
              <div className="p-2.5 bg-rose-50 border border-rose-200 rounded text-rose-800 text-xs font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                {prefError}
              </div>
            )}

            <button
              onClick={handleSavePreferences}
              disabled={isSavingPref}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded shadow-xs transition-colors cursor-pointer disabled:opacity-60"
            >
              {isSavingPref ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              {isSavingPref ? 'Saving Preferences...' : 'Save Platform Preferences'}
            </button>
          </div>
        </div>

        {/* Section 3: AI Engine Explanations */}
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

        {/* Section 4: Data & Evidence Sync */}
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
