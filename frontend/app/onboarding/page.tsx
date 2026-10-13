'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api, ApiRole, ApiRoleSkillMapResponse } from '../../services/api';
import { useLearner } from '../../context/LearnerContext';
import {
  Compass,
  Target,
  Clock,
  ArrowRight,
  Loader2,
  AlertCircle,
  CheckCircle2,
  User,
  Sparkles,
  Layers,
  PlusCircle,
  BookOpen,
  Zap,
  Check,
} from 'lucide-react';

export default function OnboardingPage() {
  const router = useRouter();
  const { registerLearner, activeUser, isAuthenticated, refreshUser } = useLearner();

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
  const [learningGoal, setLearningGoal] = useState<string>('Achieve career goal with adaptive skill path');

  // Goal & Skill Map states
  const [activeSkillMap, setActiveSkillMap] = useState<ApiRoleSkillMapResponse | null>(null);
  const [skillMapLoading, setSkillMapLoading] = useState<boolean>(false);
  const [isCustomGoalMode, setIsCustomGoalMode] = useState<boolean>(false);
  const [customGoalName, setCustomGoalName] = useState<string>('');
  const [customGoalDesc, setCustomGoalDesc] = useState<string>('');
  const [customGoalSkills, setCustomGoalSkills] = useState<string>('');
  const [isCreatingCustomGoal, setIsCreatingCustomGoal] = useState<boolean>(false);

  // Pre-fill user details if logged in via Google
  useEffect(() => {
    if (activeUser) {
      if (activeUser.name && !name) setName(activeUser.name);
      if (activeUser.email && !email) setEmail(activeUser.email);
    }
  }, [activeUser, name, email]);

  // Load available roles from backend DB
  useEffect(() => {
    async function loadRoles() {
      try {
        setRolesLoading(true);
        const rolesData = await api.getRoles();
        setRoles(rolesData);
        if (rolesData.length > 0) {
          // Default to Java Backend Developer or first role
          const javaRole = rolesData.find((r) => r.name.toLowerCase().includes('java'));
          const initial = javaRole || rolesData[0];
          setSelectedRoleId(initial.id);
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

  // Fetch structured Skill Map whenever selectedRoleId changes
  useEffect(() => {
    if (!selectedRoleId) return;
    async function fetchSkillMap() {
      try {
        setSkillMapLoading(true);
        const sm = await api.getRoleSkillMap(selectedRoleId!);
        setActiveSkillMap(sm);
      } catch (err) {
        console.error('Failed to load role skill map:', err);
      } finally {
        setSkillMapLoading(false);
      }
    }
    fetchSkillMap();
  }, [selectedRoleId]);

  const handleCreateCustomGoal = async () => {
    if (!customGoalName.trim()) {
      setFormError('Please provide a name for your custom career goal.');
      return;
    }
    setIsCreatingCustomGoal(true);
    setFormError(null);
    try {
      const skillsArray = customGoalSkills
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      const newRole = await api.createCustomRole({
        name: customGoalName.trim(),
        description: customGoalDesc.trim() || undefined,
        skills: skillsArray.length > 0 ? skillsArray : undefined,
      });

      // Update role list and select this new role
      setRoles((prev) => [...prev, newRole]);
      setSelectedRoleId(newRole.id);
      setIsCustomGoalMode(false);
      setCustomGoalName('');
      setCustomGoalDesc('');
      setCustomGoalSkills('');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to create custom goal.';
      setFormError(msg);
    } finally {
      setIsCreatingCustomGoal(false);
    }
  };

  const handleSaveAndProceed = async (targetPath: 'dashboard' | 'assessment') => {
    setFormError(null);

    if (!name.trim()) {
      setFormError('Please enter your full name.');
      return;
    }
    if (!email.trim() || !email.includes('@')) {
      setFormError('Please enter a valid email address.');
      return;
    }
    if (!selectedRoleId) {
      setFormError('Please select a target career goal.');
      return;
    }

    try {
      setSubmitting(true);
      let targetUserId = activeUser?.id;

      if (isAuthenticated && activeUser && activeUser.id > 0) {
        await api.updateUser(activeUser.id, {
          name: name.trim(),
          experience_level: experienceLevel,
          target_role_id: selectedRoleId,
          weekly_learning_hours: weeklyHours,
          learning_goal: learningGoal,
        });
        await refreshUser();
      } else {
        const newUser = await registerLearner({
          name: name.trim(),
          email: email.trim(),
          experience_level: experienceLevel,
          target_role_id: selectedRoleId,
          weekly_learning_hours: weeklyHours,
          learning_goal: learningGoal,
        });
        if (newUser) {
          targetUserId = newUser.id;
        }
      }

      if (targetPath === 'assessment') {
        router.push(`/assessments/goal/${selectedRoleId}`);
      } else {
        router.push('/');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Onboarding failed. Please try again.';
      if (msg.toLowerCase().includes('already exists')) {
        setFormError('An account with this email already exists. Please sign in.');
      } else {
        setFormError(msg);
      }
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

  return (
    <div className="min-h-screen bg-slate-50/80 flex flex-col justify-between p-4 sm:p-6 lg:p-8 antialiased">
      {/* Brand Header */}
      <header className="max-w-4xl w-full mx-auto flex items-center justify-between pb-4 border-b border-slate-200">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-black text-sm shadow-sm">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-slate-900 text-base tracking-tight block leading-none">
              SkillPath AI
            </span>
            <span className="text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
              Goal &rarr; Skill Map &rarr; Adaptive Path
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 transition-colors"
          >
            Sign In &rarr;
          </Link>
          <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-3 py-1 rounded border border-slate-200 hidden sm:inline">
            Goal Setup
          </span>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-4xl w-full mx-auto my-8 bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden">
        {/* Banner */}
        <div className="bg-white border-b border-slate-200 p-6 sm:p-8">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-700 uppercase tracking-widest mb-1.5">
            <Sparkles className="w-4 h-4 text-blue-600" /> Step 1: User Target Goal
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-900">
            What do you want to achieve?
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 leading-relaxed max-w-2xl">
            SkillPath AI does not simply give you courses. We identify the exact skills required for your target goal,
            diagnose your current gaps, and continuously determine what you need to learn next.
          </p>
        </div>

        <div className="p-6 sm:p-8 space-y-8">
          {formError && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg flex items-start gap-3 text-xs text-rose-800">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div className="flex-1">
                <strong className="block font-bold">Goal Setup:</strong>
                <span>{formError}</span>
              </div>
            </div>
          )}

          {/* SECTION 1: GOAL SELECTION (Predefined vs Custom) */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-sm sm:text-base flex items-center gap-2">
                <Target className="w-4 h-4 text-blue-600" /> Select Target Career Goal
              </h3>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setIsCustomGoalMode(false)}
                  className={`px-3 py-1.5 text-xs font-bold rounded-md transition-colors ${
                    !isCustomGoalMode
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  Predefined Goals
                </button>
                <button
                  type="button"
                  onClick={() => setIsCustomGoalMode(true)}
                  className={`px-3 py-1.5 text-xs font-bold rounded-md transition-colors flex items-center gap-1 ${
                    isCustomGoalMode
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <PlusCircle className="w-3.5 h-3.5" /> Custom Goal
                </button>
              </div>
            </div>

            {/* View A: Predefined Goals Grid */}
            {!isCustomGoalMode ? (
              rolesLoading ? (
                <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-500 flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                  Loading predefined goals from database...
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {roles.map((role) => {
                    const isSelected = selectedRoleId === role.id;
                    return (
                      <div
                        key={role.id}
                        onClick={() => setSelectedRoleId(role.id)}
                        className={`p-4 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                          isSelected
                            ? 'border-2 border-blue-600 bg-blue-50/50 shadow-sm ring-1 ring-blue-600/20'
                            : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50/60'
                        }`}
                      >
                        <div>
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="font-bold text-slate-900 text-sm">{role.name}</span>
                            {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0" />}
                          </div>
                          <p className="text-[11px] text-slate-500 leading-snug line-clamp-2">
                            {role.description || 'Target career milestone benchmark'}
                          </p>
                        </div>
                        <div className="mt-3 pt-2 border-t border-slate-100/80 flex items-center justify-between">
                          <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                            {role.role_skills?.length || 0} Competencies
                          </span>
                          <span className="text-[10px] font-semibold text-slate-400">
                            DB Stored
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )
            ) : (
              /* View B: Custom Goal Form */
              <div className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-4">
                <div className="space-y-1">
                  <h4 className="font-bold text-slate-900 text-sm">Create a Custom Target Goal</h4>
                  <p className="text-xs text-slate-500">
                    Define any specialized career role. We will dynamically register the goal and required skills in the database.
                  </p>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Goal Title <span className="text-rose-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={customGoalName}
                      onChange={(e) => setCustomGoalName(e.target.value)}
                      placeholder="e.g. Cloud Security Architect, Blockchain Engineer"
                      className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Description (Optional)
                    </label>
                    <input
                      type="text"
                      value={customGoalDesc}
                      onChange={(e) => setCustomGoalDesc(e.target.value)}
                      placeholder="e.g. Focus on AWS cloud infrastructure, IAM policies, and threat detection."
                      className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Required Skills (Comma separated)
                    </label>
                    <input
                      type="text"
                      value={customGoalSkills}
                      onChange={(e) => setCustomGoalSkills(e.target.value)}
                      placeholder="e.g. Cloud Security, IAM Policies, Terraform, Docker, Python"
                      className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <button
                    type="button"
                    disabled={isCreatingCustomGoal || !customGoalName.trim()}
                    onClick={handleCreateCustomGoal}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    {isCreatingCustomGoal ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" /> Registering Goal in DB...
                      </>
                    ) : (
                      <>
                        <Check className="w-3.5 h-3.5" /> Save Custom Goal & Preview Skill Map
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* SECTION 2: GOAL -> SKILL MAP LIVE PREVIEW (SECTION 2 MANDATE) */}
          <div className="bg-slate-50/70 border border-slate-200 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-100 text-blue-800">
                    Step 2: Goal &rarr; Skill Map
                  </span>
                  <span className="text-xs font-bold text-slate-900">
                    {activeSkillMap?.role_name || 'Competency Map'}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1">
                  Structured database skill map organized by domain categories.
                </p>
              </div>

              {skillMapLoading && <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />}
            </div>

            {activeSkillMap && activeSkillMap.categories && activeSkillMap.categories.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {activeSkillMap.categories.map((cat, catIdx) => (
                  <div key={catIdx} className="bg-white border border-slate-200 rounded-lg p-3.5 space-y-2">
                    <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-blue-600" />
                      {cat.category_name}
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {cat.skills.map((s, sIdx) => (
                        <span
                          key={sIdx}
                          className="px-2 py-1 bg-slate-50 border border-slate-200 rounded text-[11px] font-medium text-slate-700 flex items-center gap-1"
                        >
                          {s.name}
                          <span className="text-[9px] font-bold text-slate-400">
                            ({s.required_level}%)
                          </span>
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-slate-400">
                Loading categorized competencies...
              </div>
            )}
          </div>

          {/* SECTION 3: LEARNER BASIC INFO & AVAILABILITY */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-t border-slate-100 pt-6">
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
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-xs font-medium text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Technical Experience Level
              </label>
              <div className="grid grid-cols-3 gap-2">
                {experienceOptions.map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setExperienceLevel(level)}
                    className={`py-2 px-2 rounded-lg border text-xs font-semibold transition-all ${
                      experienceLevel === level
                        ? 'border-blue-600 bg-blue-600 text-white shadow-xs'
                        : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" /> Weekly Availability
              </label>
              <select
                value={weeklyHours}
                onChange={(e) => setWeeklyHours(parseInt(e.target.value, 10))}
                className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {availabilityOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* SECTION 4: CALLS TO ACTION */}
          <div className="pt-4 border-t border-slate-100 space-y-3">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Option 1: Direct Initial Diagnostic Assessment (Recommended) */}
              <button
                type="button"
                disabled={submitting}
                onClick={() => handleSaveAndProceed('assessment')}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs sm:text-sm rounded-xl shadow-sm transition-all disabled:opacity-50"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Preparing Assessment...
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" /> Start Initial Skill Assessment &rarr;
                  </>
                )}
              </button>

              {/* Option 2: Go directly to Workspace Dashboard */}
              <button
                type="button"
                disabled={submitting}
                onClick={() => handleSaveAndProceed('dashboard')}
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-4 bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-xs sm:text-sm rounded-xl transition-all disabled:opacity-50"
              >
                Save Goal &amp; Go to Dashboard &rarr;
              </button>
            </div>
            <p className="text-center text-[11px] text-slate-500">
              The initial diagnostic assessment tests 10–20 questions across your goal&apos;s skill map to calculate your baseline Skill DNA.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-4xl w-full mx-auto text-center text-xs text-slate-400 py-2">
        SkillPath AI • Goal &rarr; Skill Map &rarr; Assessment &rarr; Skill Gap &rarr; Personalized Path
      </footer>
    </div>
  );
}
