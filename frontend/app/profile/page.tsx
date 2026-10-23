'use client';

import React, { useState, useEffect } from 'react';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import { api, ApiRole } from '../../services/api';
import {
  Target,
  CheckCircle2,
  Save,
  User,
  Mail,
  Clock,
  Briefcase,
  Sparkles,
  BookOpen,
  Edit3,
  Check,
  Loader2,
  Globe,
} from 'lucide-react';

export default function ProfilePage() {
  const { activeUser, updateTargetRole } = useLearner();

  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [experienceLevel, setExperienceLevel] = useState<string>('Intermediate');
  const [targetRoleId, setTargetRoleId] = useState<number>(1);
  const [availableRoles, setAvailableRoles] = useState<{ id: number; name: string }[]>([
    { id: 2, name: 'Data Scientist' },
    { id: 5, name: 'Python Developer' },
    { id: 1, name: 'Data Analyst' },
  ]);
  const [weeklyHours, setWeeklyHours] = useState<number>(8);
  const [learningGoal, setLearningGoal] = useState<string>('Get my first Data/AI job');
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);

  // Learning Platform Preferences (Phase 21)
  const [prefPrimary, setPrefPrimary] = useState<string>('no_preference');
  const [prefSecondaries, setPrefSecondaries] = useState<string[]>([]);
  const [isEditingPref, setIsEditingPref] = useState<boolean>(false);
  const [isSavingPref, setIsSavingPref] = useState<boolean>(false);
  const [prefSavedSuccess, setPrefSavedSuccess] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    api.getRoles().then((roles: ApiRole[]) => {
      if (mounted && roles && roles.length > 0) {
        const supported = [
          roles.find((r) => r.id === 2 || r.name === 'Data Scientist') || { id: 2, name: 'Data Scientist' },
          roles.find((r) => r.id === 5 || r.name === 'Python Developer') || { id: 5, name: 'Python Developer' },
          roles.find((r) => r.id === 1 || r.name === 'Data Analyst') || { id: 1, name: 'Data Analyst' },
        ];
        if (activeUser?.target_role_id === 9) {
          supported.push({ id: 9, name: 'Analytics Engineer (Preserved)' });
        }
        setAvailableRoles(supported);
      }
    }).catch(() => null);
    return () => {
      mounted = false;
    };
  }, [activeUser?.target_role_id]);

  useEffect(() => {
    if (activeUser) {
      setName(activeUser.name || '');
      setEmail(activeUser.email || '');
      setExperienceLevel(activeUser.experience_level || 'Intermediate');
      setWeeklyHours(activeUser.weekly_learning_hours || 8);
      setLearningGoal(activeUser.learning_goal || 'Get my first Data/AI job');
      if (activeUser.target_role_id) {
        setTargetRoleId(activeUser.target_role_id);
      }
    }
  }, [activeUser]);

  useEffect(() => {
    let mounted = true;
    api.getPreferencesResources()
      .then((res) => {
        if (mounted && res) {
          setPrefPrimary(res.primary_platform || 'no_preference');
          setPrefSecondaries(res.preferred_platforms || res.secondary_platforms || []);
        }
      })
      .catch(() => {
        if (activeUser?.id) {
          api.getResourcePreferences(activeUser.id).then((res) => {
            if (mounted && res) {
              setPrefPrimary(res.primary_platform || 'no_preference');
              setPrefSecondaries(res.secondary_platforms || []);
            }
          }).catch(() => null);
        }
      });
    return () => {
      mounted = false;
    };
  }, [activeUser?.id]);

  const handleSavePref = async () => {
    setIsSavingPref(true);
    setPrefSavedSuccess(null);
    try {
      const cleaned = prefSecondaries.filter((p) => p !== prefPrimary && p !== 'no_preference');
      await api.updatePreferencesResources({
        primary_platform: prefPrimary,
        preferred_platforms: cleaned,
      });
      setPrefSavedSuccess('Preferences updated successfully!');
      setIsEditingPref(false);
      setTimeout(() => setPrefSavedSuccess(null), 3500);
    } catch {
      if (activeUser?.id) {
        const cleaned = prefSecondaries.filter((p) => p !== prefPrimary && p !== 'no_preference');
        await api.updateResourcePreferences(activeUser.id, {
          primary_platform: prefPrimary,
          secondary_platforms: cleaned,
        }).catch(() => null);
        setPrefSavedSuccess('Preferences updated successfully!');
        setIsEditingPref(false);
        setTimeout(() => setPrefSavedSuccess(null), 3500);
      }
    } finally {
      setIsSavingPref(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setIsSaved(false);
    try {
      if (activeUser?.id) {
        await api.updateUser(activeUser.id, {
          name,
          experience_level: experienceLevel,
          weekly_learning_hours: weeklyHours,
          learning_goal: learningGoal,
          target_role_id: targetRoleId,
        });
      }
      if (targetRoleId && updateTargetRole) {
        await updateTargetRole(targetRoleId);
      }
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 3000);
    } catch (err) {
      console.error('Failed to update profile:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-5 max-w-4xl mx-auto">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Learner Profile</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Manage your personal learning identity, target competency vector, and availability.
          </p>
        </div>

        {/* Profile Card Form */}
        <form onSubmit={handleSave} className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-5">
          {/* Top user summary strip */}
          <div className="flex items-center gap-4 pb-4 border-b border-slate-100">
            <div className="w-14 h-14 rounded-full bg-slate-900 text-white font-bold text-lg flex items-center justify-center shrink-0 shadow-xs">
              {name ? name.split(' ').map((n) => n[0]).join('').slice(0, 2) : 'NA'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900">{name || 'Learner'}</h3>
              </div>
              <p className="text-xs text-slate-500">
                {email} • {activeUser?.target_role?.name || 'Analytics Engineer'} • {experienceLevel}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            {/* Full Name */}
            <div className="space-y-1.5">
              <label htmlFor="learner-name" className="font-semibold text-slate-700 block">
                Full Name
              </label>
              <input
                id="learner-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-xs"
                placeholder="Learner Name"
              />
            </div>

            {/* Email Address */}
            <div className="space-y-1.5">
              <label htmlFor="learner-email" className="font-semibold text-slate-700 block">
                Email Address
              </label>
              <input
                id="learner-email"
                type="email"
                value={email}
                disabled
                className="w-full px-3 py-2 bg-slate-100 border border-slate-200 rounded-md text-slate-600 text-xs cursor-not-allowed"
                placeholder="learner@example.com"
              />
            </div>

            {/* Experience Level */}
            <div className="space-y-1.5">
              <label htmlFor="exp-level" className="font-semibold text-slate-700 block">
                Experience Level
              </label>
              <select
                id="exp-level"
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-xs cursor-pointer"
              >
                <option value="Beginner">Beginner (0-1 years)</option>
                <option value="Intermediate">Intermediate (1-3 years)</option>
                <option value="Advanced">Advanced (3+ years)</option>
              </select>
            </div>

            {/* Target Role */}
            <div className="space-y-1.5">
              <label htmlFor="target-role" className="font-semibold text-slate-700 block">
                Target Role
              </label>
              <select
                id="target-role"
                value={targetRoleId}
                onChange={(e) => setTargetRoleId(parseInt(e.target.value, 10))}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-xs cursor-pointer font-medium"
              >
                {availableRoles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Weekly Availability */}
            <div className="space-y-1.5">
              <label htmlFor="weekly-hours" className="font-semibold text-slate-700 block">
                Weekly Learning Availability (Hours)
              </label>
              <input
                id="weekly-hours"
                type="number"
                min="2"
                max="40"
                value={weeklyHours}
                onChange={(e) => setWeeklyHours(parseInt(e.target.value, 10) || 10)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-xs"
              />
            </div>

            {/* Primary Learning Goal */}
            <div className="space-y-1.5 sm:col-span-2">
              <label htmlFor="learning-goal" className="font-semibold text-slate-700 block">
                Primary Career Goal
              </label>
              <input
                id="learning-goal"
                type="text"
                value={learningGoal}
                onChange={(e) => setLearningGoal(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-xs"
                placeholder="e.g. Master SQL & Power BI to secure a Data Analyst offer"
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
            {isSaved ? (
              <span className="text-xs font-semibold text-emerald-700 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Profile changes saved successfully!
              </span>
            ) : (
              <span className="text-xs text-slate-400">
                Changes adapt your Dynamic Roadmap calibration.
              </span>
            )}

            <button
              type="submit"
              disabled={isSaving}
              className="px-5 py-2.5 bg-blue-800 hover:bg-blue-900 text-white font-semibold text-xs rounded-md shadow-xs transition-colors flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
            >
              <Save className="w-3.5 h-3.5" />
              <span>{isSaving ? 'Saving...' : 'Save changes'}</span>
            </button>
          </div>
        </form>

        {/* Learning Preferences Section (Phase 7) */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <BookOpen className="w-5 h-5 text-blue-700 shrink-0" />
              <div>
                <h2 className="text-base font-bold text-slate-900">Learning preferences</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Your preferences influence which external resources are recommended. They do not change your skill priorities or learning roadmap.
                </p>
              </div>
            </div>

            {!isEditingPref && (
              <button
                type="button"
                onClick={() => setIsEditingPref(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold transition-colors cursor-pointer self-start sm:self-auto"
              >
                <Edit3 className="w-3.5 h-3.5 text-slate-500" />
                <span>Edit preferences</span>
              </button>
            )}
          </div>

          {prefSavedSuccess && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-xs font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              {prefSavedSuccess}
            </div>
          )}

          {!isEditingPref ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                  Primary platform
                </span>
                <span className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-blue-600" />
                  {prefPrimary === 'no_preference' ? 'Let SkillPath choose (Default)' : prefPrimary.toUpperCase()}
                </span>
                <p className="text-[11px] text-slate-500">
                  {prefPrimary === 'no_preference'
                    ? 'SkillPath automatically evaluates curriculum quality and verified coverage.'
                    : 'External recommendations prioritize tutorials from this platform.'}
                </p>
              </div>

              <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                  Also consider
                </span>
                <span className="text-sm font-bold text-slate-900 block">
                  {prefSecondaries.length > 0
                    ? prefSecondaries.map((p) => p.toUpperCase()).join(', ')
                    : 'None selected'}
                </span>
                <p className="text-[11px] text-slate-500">
                  Alternative platforms referenced if your primary platform lacks aligned coverage.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-4 pt-1">
              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-700 uppercase">
                  Primary platform
                </label>
                <select
                  value={prefPrimary}
                  onChange={(e) => {
                    const val = e.target.value;
                    setPrefPrimary(val);
                    setPrefSecondaries((prev) => prev.filter((p) => p !== val));
                  }}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="no_preference">Let SkillPath choose (No preference)</option>
                  <option value="geeksforgeeks">GeeksforGeeks</option>
                  <option value="w3schools">W3Schools</option>
                  <option value="khanacademy">Khan Academy</option>
                  <option value="coursera">Coursera</option>
                  <option value="datacamp">DataCamp</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-700 uppercase">
                  Also consider (Secondary Platforms)
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {[
                    { id: 'geeksforgeeks', label: 'GeeksforGeeks' },
                    { id: 'w3schools', label: 'W3Schools' },
                    { id: 'khanacademy', label: 'Khan Academy' },
                    { id: 'coursera', label: 'Coursera' },
                    { id: 'datacamp', label: 'DataCamp' },
                  ].map((platform) => {
                    const isPrimary = prefPrimary === platform.id;
                    const isSecondary = prefSecondaries.includes(platform.id);

                    return (
                      <button
                        type="button"
                        key={platform.id}
                        disabled={isPrimary}
                        onClick={() => {
                          if (isSecondary) {
                            setPrefSecondaries((prev) => prev.filter((p) => p !== platform.id));
                          } else {
                            setPrefSecondaries((prev) => [...prev, platform.id]);
                          }
                        }}
                        className={`p-2.5 rounded-lg border text-xs font-semibold text-left flex items-center justify-between transition-all ${
                          isPrimary
                            ? 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                            : isSecondary
                            ? 'bg-blue-50 border-blue-600 text-blue-900'
                            : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300'
                        }`}
                      >
                        <span>{platform.label}</span>
                        {isPrimary ? (
                          <span className="text-[10px] text-blue-700 font-bold">Primary</span>
                        ) : isSecondary ? (
                          <Check className="w-3.5 h-3.5 text-blue-600 stroke-[3]" />
                        ) : null}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <button
                  type="button"
                  disabled={isSavingPref}
                  onClick={handleSavePref}
                  className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-bold shadow-xs transition-colors cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
                >
                  {isSavingPref ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                  <span>{isSavingPref ? 'Saving...' : 'Save preferences'}</span>
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditingPref(false)}
                  className="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
