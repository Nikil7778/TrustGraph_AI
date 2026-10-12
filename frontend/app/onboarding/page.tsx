'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api, ApiRole } from '../../services/api';
import { useLearner } from '../../context/LearnerContext';
import { Compass, Target, Clock, ArrowRight, Loader2, AlertCircle, CheckCircle2, User, Sparkles } from 'lucide-react';

export default function OnboardingPage() {
  const router = useRouter();
  const { setActiveUserId, refreshUser } = useLearner();

  const [roles, setRoles] = useState<ApiRole[]>([]);
  const [rolesLoading, setRolesLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Form states
  const [name, setName] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [experienceLevel, setExperienceLevel] = useState<string>('Intermediate');
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [weeklyHours, setWeeklyHours] = useState<number>(8);
  const [learningGoal, setLearningGoal] = useState<string>('Get my first Data/AI job');

  useEffect(() => {
    async function loadRoles() {
      try {
        setRolesLoading(true);
        const rolesData = await api.getRoles();
        setRoles(rolesData);
        if (rolesData.length > 0) {
          setSelectedRoleId(rolesData[0].id);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Could not fetch target roles from backend.';
        setFormError(msg);
      } finally {
        setRolesLoading(false);
      }
    }
    loadRoles();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    // Client-side validations
    if (!name.trim()) {
      setFormError('Please enter your full name.');
      return;
    }
    if (!email.trim() || !email.includes('@')) {
      setFormError('Please enter a valid email address.');
      return;
    }
    if (!selectedRoleId) {
      setFormError('Please select a target career role.');
      return;
    }

    try {
      setSubmitting(true);
      const newUser = await api.createUser({
        name: name.trim(),
        email: email.trim(),
        experience_level: experienceLevel,
        target_role_id: selectedRoleId,
        weekly_learning_hours: weeklyHours,
        learning_goal: learningGoal,
      });

      // Update active user context and redirect to dashboard
      setActiveUserId(newUser.id);
      await refreshUser();
      router.push('/');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Onboarding failed. Please try again.';
      setFormError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const experienceOptions = ['Beginner', 'Intermediate', 'Advanced'];
  const availabilityOptions = [
    { label: '2–4 hours / week', value: 3 },
    { label: '5–7 hours / week', value: 6 },
    { label: '8–10 hours / week', value: 9 },
    { label: '10+ hours / week', value: 12 },
  ];
  const goalOptions = [
    'Get my first Data/AI job',
    'Switch careers',
    'Improve current skills',
    'Prepare for interviews',
    'Build a portfolio',
    'Become industry-ready',
  ];

  return (
    <div className="min-h-screen bg-slate-50/80 flex flex-col justify-between p-4 sm:p-6 lg:p-8 antialiased">
      {/* Brand Header */}
      <header className="max-w-3xl w-full mx-auto flex items-center justify-between pb-4 border-b border-slate-200">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded bg-blue-600 flex items-center justify-center text-white font-black text-sm shadow-sm">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-slate-900 text-base tracking-tight block leading-none">
              SkillPath AI
            </span>
            <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
              Evidence-Driven Career Intelligence
            </span>
          </div>
        </div>

        <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-3 py-1 rounded border border-slate-200">
          Learner Setup
        </span>
      </header>

      {/* Form Container */}
      <main className="max-w-2xl w-full mx-auto my-8 bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
        <div className="bg-white border-b border-slate-200 p-6 sm:p-8">
          <div className="flex items-center gap-2 text-xs font-semibold text-blue-700 uppercase tracking-widest mb-1.5">
            <Sparkles className="w-4 h-4 text-blue-600" /> Learner Profile Setup
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">Set Your Career Target</h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 leading-relaxed">
            &quot;The learner does not follow the roadmap. The roadmap follows the learner.&quot;
            <br />
            Configure your initial benchmark role and availability to build your Skill DNA.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-6">
          {formError && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-md flex items-start gap-3 text-xs text-rose-800">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <strong className="block font-bold">Onboarding Error:</strong>
                <span>{formError}</span>
              </div>
            </div>
          )}

          {/* Section 1: Basic Info */}
          <div className="space-y-4 border-b border-slate-100 pb-5">
            <h3 className="font-bold text-slate-900 text-sm sm:text-base flex items-center gap-2">
              <User className="w-4 h-4 text-blue-600" /> Basic Information
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Jordan Lee"
                  className="w-full bg-slate-50 border border-slate-300 rounded-md px-3.5 py-2.5 text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Email Address <span className="text-rose-500">*</span>
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="e.g. jordan.lee@example.com"
                  className="w-full bg-slate-50 border border-slate-300 rounded-md px-3.5 py-2.5 text-sm font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Target Career Role */}
          <div className="space-y-3 border-b border-slate-100 pb-5">
            <h3 className="font-bold text-slate-900 text-sm sm:text-base flex items-center gap-2">
              <Target className="w-4 h-4 text-blue-600" /> Target Career Role <span className="text-rose-500">*</span>
            </h3>

            {rolesLoading ? (
              <div className="p-4 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-500 flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                Loading target career benchmarks from backend...
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {roles.map((role) => {
                  const isSelected = selectedRoleId === role.id;
                  return (
                    <div
                      key={role.id}
                      onClick={() => setSelectedRoleId(role.id)}
                      className={`p-3.5 rounded-lg border cursor-pointer transition-all flex flex-col justify-between min-h-[44px] ${
                        isSelected
                          ? 'border-2 border-blue-600 bg-blue-50/50 shadow-sm'
                          : 'border-slate-200 bg-slate-50 hover:bg-slate-100'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-slate-900 text-sm">{role.name}</span>
                          {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />}
                        </div>
                        <p className="text-[11px] text-slate-500 leading-snug line-clamp-2">
                          {role.description}
                        </p>
                      </div>
                      <span className="text-[10px] font-semibold text-slate-400 mt-2 block">
                        {role.role_skills.length} Benchmark Skills
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Section 3: Experience Level */}
          <div className="space-y-3 border-b border-slate-100 pb-5">
            <label className="block text-xs font-semibold text-slate-700">
              Technical Experience Level
            </label>
            <div className="grid grid-cols-3 gap-3">
              {experienceOptions.map((level) => {
                const isSelected = experienceLevel === level;
                return (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setExperienceLevel(level)}
                    className={`py-2.5 px-3 rounded-md border text-xs font-semibold transition-all min-h-[44px] ${
                      isSelected
                        ? 'border-blue-600 bg-blue-600 text-white shadow-sm'
                        : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    {level}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section 4: Weekly Learning Hours & Learning Goal */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-b border-slate-100 pb-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" /> Weekly Availability
              </label>
              <select
                value={weeklyHours}
                onChange={(e) => setWeeklyHours(parseInt(e.target.value, 10))}
                className="w-full bg-slate-50 border border-slate-300 rounded-md px-3.5 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
              >
                {availabilityOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Primary Learning Goal
              </label>
              <select
                value={learningGoal}
                onChange={(e) => setLearningGoal(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-md px-3.5 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[44px]"
              >
                {goalOptions.map((goal) => (
                  <option key={goal} value={goal}>
                    {goal}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={submitting}
              className="w-full inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-md shadow-sm transition-colors disabled:opacity-50 min-h-[48px]"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating Learner Profile & Skill DNA...
                </>
              ) : (
                <>
                  Initialize Learner DNA & Proceed to Dashboard
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </main>

      {/* Footer */}
      <footer className="max-w-3xl w-full mx-auto text-center text-xs text-slate-400 py-2">
        SkillPath AI • Hackathon Prototype • Evidence-Driven Career Intelligence Engine
      </footer>
    </div>
  );
}
