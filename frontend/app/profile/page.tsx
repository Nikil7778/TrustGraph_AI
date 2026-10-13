'use client';

import React, { useState, useEffect } from 'react';
import { AppShell } from '../../components/AppShell';
import { useLearner } from '../../context/LearnerContext';
import { api, ApiRole } from '../../services/api';
import { Target, CheckCircle2, Save, User, Mail, Clock, Briefcase, Sparkles } from 'lucide-react';

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
      </div>
    </AppShell>
  );
}
