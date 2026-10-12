'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, Bell, Target, ChevronDown, UserPlus, Sparkles, RotateCcw, Search } from 'lucide-react';
import { useLearner } from '../context/LearnerContext';
import { useCoach } from '../context/CoachContext';
import { api } from '../services/api';
import { CURRENT_USER } from '../lib/mockData';

interface TopBarProps {
  onOpenMobileMenu?: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onOpenMobileMenu }) => {
  const pathname = usePathname();
  const { activeUserId, activeUser, allUsers, setActiveUserId, isDemoMode } = useLearner();
  const { openCoach } = useCoach();

  // Display user information
  const displayName = isDemoMode ? CURRENT_USER.name : (activeUser?.name || `Learner #${activeUserId}`);
  const targetRole = isDemoMode
    ? CURRENT_USER.targetRole
    : (activeUser?.target_role?.name || 'Data Analyst');

  // Breadcrumb logic matching Stitch reference
  const getBreadcrumb = () => {
    if (pathname === '/') return 'Target Role • ' + targetRole;
    if (pathname?.startsWith('/skill-debt')) return 'SkillPath AI / Skill Debt';
    if (pathname?.startsWith('/skill-dna')) return 'SkillPath AI / Competence Matrix';
    if (pathname?.startsWith('/roadmap')) return 'SkillPath AI / Analytics Console';
    if (pathname?.startsWith('/career-gap')) return 'SkillPath AI / Career Gap';
    if (pathname?.startsWith('/assessments')) return 'SkillPath AI / Assessments';
    if (pathname?.startsWith('/practice-lab')) return 'SkillPath AI / Practice Lab';
    if (pathname?.startsWith('/projects')) return 'SkillPath AI / Projects';
    if (pathname?.startsWith('/skill-passport')) return 'SkillPath AI / Skill Passport';
    if (pathname?.startsWith('/coach')) return 'SkillPath AI / Career Coach';
    if (pathname?.startsWith('/profile')) return 'SkillPath AI / Profile';
    if (pathname?.startsWith('/settings')) return 'SkillPath AI / Settings';
    return 'SkillPath AI / Overview';
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 fixed top-0 right-0 left-0 lg:left-64 z-20 px-3 sm:px-6 lg:px-8 flex items-center justify-between shadow-2xs">
      <div className="flex items-center gap-3 min-w-0">
        {/* Mobile menu trigger */}
        <button
          onClick={onOpenMobileMenu}
          className="lg:hidden min-h-[44px] min-w-[44px] flex items-center justify-center p-2 text-slate-600 hover:text-slate-900 rounded-md hover:bg-slate-100 transition-colors focus:ring-2 focus:ring-blue-500"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Breadcrumb Context from Stitch Reference */}
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 truncate">
          <span className="text-slate-800">{getBreadcrumb()}</span>
        </div>
      </div>

      {/* Right Action Icons & Active Learner Selector */}
      <div className="flex items-center gap-2 sm:gap-3 shrink-0">
        {/* Learner Switcher Dropdown */}
        <div className="relative flex items-center">
          <select
            value={activeUserId}
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              if (val === -1) {
                // Navigate to onboarding
                window.location.href = '/onboarding';
              } else {
                setActiveUserId(val);
              }
            }}
            className="bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 text-xs font-semibold text-slate-800 hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[40px] cursor-pointer"
          >
            <option value={1}>Alex Mercer (Demo Mode - Seeded Skill Debt)</option>
            {allUsers
              .filter((u) => u.id !== 1)
              .map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name} ({u.target_role?.name || 'Learner'})
                </option>
              ))}
            <option value={-1}>+ Onboard New Learner...</option>
          </select>
        </div>

        {/* Quick Demo Reset for Alex Mercer */}
        {activeUserId === 1 && (
          <button
            onClick={async () => {
              if (confirm('Reset Alex Mercer to initial baseline state with active Skill Debt?')) {
                try {
                  await api.resetDemo(1);
                  window.location.reload();
                } catch (err: any) {
                  alert('Reset failed: ' + (err.message || 'Server error'));
                }
              }
            }}
            className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-md border border-slate-300 transition-colors min-h-[40px] cursor-pointer"
            title="Reset Alex Mercer back to initial demo state"
          >
            <RotateCcw className="w-3.5 h-3.5 text-blue-600" />
            <span>Reset Demo</span>
          </button>
        )}

        {/* Career Coach Quick Trigger */}
        <button
          type="button"
          onClick={() => openCoach()}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-xs rounded-md border border-blue-200 transition-colors min-h-[40px] cursor-pointer"
          title="Ask your Career Coach"
        >
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span className="hidden sm:inline">Coach</span>
        </button>

        {/* Onboard New Learner Quick Link */}
        <Link
          href="/onboarding"
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-md shadow-2xs transition-colors min-h-[40px]"
        >
          <UserPlus className="w-3.5 h-3.5" /> Onboard
        </Link>

        {/* Notifications Button */}
        <button
          className="relative min-h-[44px] min-w-[44px] flex items-center justify-center p-2 text-slate-500 hover:text-slate-800 rounded-full hover:bg-slate-100 transition-colors focus:ring-2 focus:ring-blue-500"
          aria-label="View notifications"
        >
          <Bell className="w-4.5 h-4.5" />
          <span className="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white" />
        </button>

        <div className="h-5 w-px bg-slate-200" />

        {/* Profile Avatar Trigger */}
        <Link
          href="/profile"
          className="flex items-center gap-2 p-1.5 rounded-md hover:bg-slate-50 transition-colors focus:ring-2 focus:ring-blue-500 min-h-[44px]"
        >
          <div className="w-8 h-8 rounded-full bg-slate-900 text-white font-bold text-xs flex items-center justify-center border border-slate-700 shadow-2xs shrink-0">
            {displayName.split(' ').map((n) => n[0]).join('').slice(0, 2)}
          </div>
          <div className="hidden xl:block text-left">
            <span className="text-xs font-bold text-slate-900 block leading-tight truncate max-w-[120px]">
              {displayName}
            </span>
            <span className="text-[10px] text-slate-500 block leading-tight">
              {isDemoMode ? 'Alex Mercer' : 'Live Learner'}
            </span>
          </div>
        </Link>
      </div>
    </header>
  );
};
